#!/usr/bin/env python3
"""Rebuild a conservative dated MARC route pilot offline; Python standard library only.

No target number is used. Narrow event rules deliberately leave most provenance
notes untouched. Run from any directory; optional --export-zip refreshes MARC 008.
"""
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/research/zurich-postincunabula-export-20261023'
N = {'m': 'http://www.loc.gov/MARC21/slim'}
CONFLICTS = {'991041866759705501', '991136341899705501'}
YEAR = r'(1[5-9]\d{2})'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def note(field):
    return ' '.join(v for k,v in field['subfields'] if k == 'a')

def key(row):
    return (row['record_id'], row['institution_code'], row['shelfmark'])

def dated_event(field):
    """Return one institution-event anchor, never an unrelated year or lifespan."""
    if field['assignment'] not in ('explicit','plausible') or field['tag'] not in ('500','561','590','361'):
        return None
    if field['record_id'] in CONFLICTS:
        return None
    t = note(field)
    institution = None
    match = None
    rule = None
    certainty = 'exact'
    if 'Stadtbibliothek' in t and 'Zürich' in t:
        institution = 'Stadtbibliothek Zürich'
        patterns = [
            ('arrival_donation', r'Gelangte (vermutlich )?'+YEAR+r'.*?als Donation.*?Stadtbibliothek Zürich'),
            ('dated_city_donation', r'(?:Donation|Geschenk|Schenkungsvermerk).*?an die Stadtbibliothek Zürich[ ,]*(?:\(\s*|dat\. )?'+YEAR),
            ('city_donation_after_name', r'Der Stadtbibliothek (?:in )?Zürich geschenkt.*?'+YEAR),
            ('city_donation_year_first', r'Der Stadtbibliothek Zürich '+YEAR+r' letztwillentlich geschenkt'),
            ('heidenheim_donation', r'Stadtbibliothek Zürich geschenkt von der Israelitischen Kultusgemeinde Zürich \('+YEAR+r'\)'),
        ]
        for rule,pattern in patterns:
            match = re.search(pattern,t)
            if match:
                if rule == 'arrival_donation' and match.group(1):certainty='probable'
                break
    elif 'Bibliothek des Grossmünsterstifts geschenkt' in t:
        institution='Bibliothek des Grossmünsterstifts Zürich'
        rule='pellikan_donation_circa'
        match=re.search(r'Von Konrad Pellikan um '+YEAR+r' der Bibliothek des Grossmünsterstifts geschenkt',t)
        certainty='circa'
    elif 'Naturforschende Gesellschaft (Zürich)' in t:
        institution='Naturforschende Gesellschaft Zürich'
        rule='dated_dedication'
        match=re.search(r'Widmung.*?Naturforschende Gesellschaft \(Zürich\), datiert: '+YEAR,t)
    if not match:return None
    years=[int(s) for s in match.groups() if s and re.fullmatch(YEAR,s)]
    if len(years)!=1:raise ValueError('Non-unique event year: '+t)
    return {'role':'historical_provenance','place':'Zürich','year':years[0],
            'date_certainty':certainty,'event_kind':'dedication_to_institution' if rule=='dated_dedication' else 'donation_to_institution',
            'owner_or_recipient':institution,'place_basis':'named recipient institution in Zürich',
            'rule_id':rule,'matched_text':match.group(0),
            'evidence':[field],
            'scope_note':'A catalogue copy reference is not necessarily a separate physical volume. Binding or bound-with evidence is retained as stated in the original note.'}

def extract_controls(export):
    controls={}
    with zipfile.ZipFile(export) as z:
        for name in sorted(z.namelist()):
            if name.startswith('__MACOSX/') or '/marcxml/metadata_' not in name or not name.endswith('.xml'):continue
            for r in ET.fromstring(z.read(name)).findall('.//m:record',N):
                rid=r.find('m:controlfield[@tag="001"]',N).text
                f=r.find('m:controlfield[@tag="008"]',N)
                if rid in controls:raise ValueError('Duplicate record '+rid)
                controls[rid]={'008':f.text or '' if f is not None else ''}
    return controls

def build(data=DATA, authority_path=ROOT/'data/authority/postincunabula-pilot-places.json'):
    refs=read(data/'working-copy-references.json')
    lookup={key(r):r for r in refs}
    if len(lookup)!=len(refs):raise ValueError('Duplicate catalogue reference')
    assignments=read(data/'provenance-assignments.json')
    controls=read(data/'route-pilot-controlfields.json')
    authority=read(authority_path)
    events={}; reviews=[]
    for field in assignments:
        e=dated_event(field)
        if not e:continue
        for inst,shelf in field['targets']:
            k=(field['record_id'],inst,shelf)
            if k not in lookup:continue
            if k in events:raise ValueError('Multiple event rules for reference '+repr(k))
            events[k]=e
    ready=[];pending=[]
    for k,event in sorted(events.items()):
        ref=lookup[k];rid,inst,shelf=k
        publication=ref['publication']
        labels=[v for f in publication for c,v in f['subfields'] if c=='a']
        dates=[v for f in publication for c,v in f['subfields'] if c=='c']
        d008=controls[rid]['008']
        year=int(d008[7:11]) if d008[6:7]=='s' and d008[7:11].isdigit() else None
        origin={'role':'publication','place_labels':labels,'date_labels':dates,'year':year,
                'date_basis':'MARC 008 single-year code; original 260/264 wording retained',
                'source_008':d008,'source_fields':publication,
                'date_certainty':'catalogue_year_not_independently_verified'}
        names={authority['publication_label_map'].get(label) for label in labels}
        issues=[]
        if len(names)!=1 or None in names:issues.append('Publication locality is unresolved or names more than one place; no single point inferred.')
        else:
            city=next(iter(names));geo=authority['places'][city]
            origin.update(normalised_place=city,coordinates={'latitude':geo['latitude'],'longitude':geo['longitude']},coordinate_source=geo)
        if year is None or not 1501<=year<=1525:issues.append('No single MARC 008 publication year in 1501–1525.')
        if year and year>event['year']:issues.append('Event precedes publication year.')
        geo=authority['places']['Zurich']
        for s in [event]:s.update(normalised_place='Zürich',coordinates={'latitude':geo['latitude'],'longitude':geo['longitude']},coordinate_source=geo)
        current={'role':'current_holding','place':'Zürich','institution':'Zentralbibliothek Zürich',
                 'observed_at':'2026-10-23','acquisition_date':None,'normalised_place':'Zürich',
                 'coordinates':{'latitude':geo['latitude'],'longitude':geo['longitude']},'coordinate_source':geo}
        route={'record_id':rid,'institution_code':inst,'shelfmark':shelf,'title':ref['title'],
               'catalogue_url':'https://swisscollections.ch/Record/'+rid,
               'reference_id':'marc:'+hashlib.sha256('\x1f'.join(k).encode()).hexdigest()[:20],
               'publication_source':publication,'source_008':d008,'review_flags':ref.get('review_flags',[]),
               'stations':[origin,event,current],'mapping_issues':issues,
               'limits':['Selected anchors only, not a complete ownership history. Other dated and undated evidence is not erased.',
                         'Catalogue copy assignment may be plausible rather than explicit; original MARC evidence retained.',
                         'Event year precision and certainty are distinct from copy assignment and location confidence.',
                         'Current holding observation is not an acquisition date. No continuous residence is established.',
                         'Publication statements may describe publication or distribution, not a separately established printing location.']}
        (pending if issues else ready).append(route)
    for f in assignments:
        if f['record_id'] in CONFLICTS and f['tag'] in ('561','590'):
            reviews.append({'reason':'Related bound-with references report a donation in 1836 and a donor-register entry in 1838. Retained for event interpretation, not silently collapsed to one year.','evidence':f})
    inputs=['working-copy-references.json','provenance-assignments.json','route-pilot-controlfields.json']
    summary={'reconstruction_date':'2026-10-24','working_catalogue_references':len(refs),
             'references_with_selected_dated_events':len(events),'map_ready_references':len(ready),
             'pending_publication_resolution':len(pending),'map_ready_station_count':sum(len(r['stations']) for r in ready),
             'event_date_certainty':{c:sum(r['stations'][1]['date_certainty']==c for r in ready) for c in ['exact','circa','probable']},
             'input_sha256':{n:hashlib.sha256((data/n).read_bytes()).hexdigest() for n in inputs},
             'authority_sha256':hashlib.sha256(authority_path.read_bytes()).hexdigest(),
             'limitations':['This is an independently reconstructed conservative selection, not a verified byte-for-byte recovery of the lost package.',
                            'There is no target count in the selection algorithm. This pilot is not a census of all usable provenance.',
                            'Institutional donation rules were reconstructed. Other event types, including reviewed personal ownership, remain outside these narrow rules.',
                            'The earlier station candidates and collection-place supplement remain unchanged.']}
    return ready,pending,reviews,summary

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--export-zip',type=Path,help='Optional original swisscollections export to regenerate MARC 008 snapshot')
    a=ap.parse_args()
    if a.export_zip:write(DATA/'route-pilot-controlfields.json',extract_controls(a.export_zip))
    ready,pending,reviews,summary=build()
    for name,obj in [('route-pilot-geocoded',ready),('route-pilot-pending',pending),('route-pilot-review',reviews),('route-pilot-summary',summary)]:write(DATA/(name+'.json'),obj)
    unparsed = [f for f in read(DATA/'provenance-assignments.json')
                if f['assignment'] in ('explicit','plausible') and f['tag'] in ('500','561','590','361')
                and re.search(YEAR, note(f)) and dated_event(f) is None]
    write(DATA/'route-pilot-unparsed-dated-notes.json', unparsed)
    # Human-readable review page, independent of the map application.
    import html
    rows=[]
    for r in ready+pending:
        origin,event,current=r['stations'];text=note(event['evidence'][0])
        rows.append('<tr><td><a href="'+html.escape(r['catalogue_url'])+'">'+html.escape(r['shelfmark'])+'</a><br>'+html.escape(' / '.join(r['title']))+'</td><td>'+html.escape(' / '.join(origin['place_labels']))+'<br>'+str(origin['year'])+'</td><td>'+html.escape(event['owner_or_recipient'])+'<br>'+str(event['year'])+' ('+event['date_certainty']+')</td><td>'+html.escape(text)+'</td><td>'+html.escape('; '.join(r['mapping_issues']) or 'Ready')+'</td></tr>')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><title>ZB MARC pilot review</title><style>body{font:16px/1.45 system-ui;margin:2rem}table{border-collapse:collapse}td,th{padding:.8rem;border:1px solid #bbb;vertical-align:top}th{background:#eee}a{color:#135c80}</style><h1>ZB postincunabula: reconstructed dated pilot</h1><p>'+str(len(ready))+' map-ready catalogue references; '+str(len(pending))+' pending publication-place resolution. Selected institutional events only; not a complete provenance census. Current holding: ZB Zürich, observed 23 October 2026, not an acquisition date.</p><p>Source assignment can be plausible rather than explicit. Original notes preserve evidence on bindings and other bound-with prints. Circa and probable years must remain qualified in the map.</p><table><thead><tr><th>Copy reference / title</th><th>Publication</th><th>Selected historical anchor</th><th>Original MARC note</th><th>Status</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></html>'
    (DATA/'route-pilot-review.html').write_text(page,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
