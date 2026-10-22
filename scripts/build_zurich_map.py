"""Build the Zurich map offline from reviewed tables and explicit decisions."""
import csv,html,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(p,data):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def write(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main(swiss=False):
 out=ROOT/'data/map';derived=ROOT/('data/derived/swiss' if swiss else 'data/derived')
 raw=json.loads((ROOT/('data/retrieved/swiss-inventory/swiss-mei-snapshot.json' if swiss else 'data/retrieved/zurich-full.json')).read_text());records={r['id']:r for r in raw['records']}
 editions=json.loads((derived/'editions.json').read_text())['editions']
 decisions=json.loads((ROOT/'data/authority/zurich-locality-decisions.json').read_text())
 mappings={m['source_label']:m for m in decisions['mappings']}
 extra=json.loads((ROOT/'data/authority/swiss-locality-decisions.json').read_text()) if swiss else {'mappings':[],'holdings':[],'regions':[]}
 for m in extra['mappings']:mappings.setdefault(m['source_label'],m)
 holdings={m['institution_id']:m for m in extra['holdings']}
 stations=read(derived/'stations-reviewed.csv');copies=read(derived/'mei-copies.csv');issues=[];langs={}
 for c in copies:
  h=records[c['mei_id']].get('hostItem',{});terms=[]
  for field in ['subject','keywords']:
   val=h.get(field,[]);val=[val] if isinstance(val,str) else val
   for item in val or []:terms.extend(t.strip() for t in html.unescape(str(item)).split(';') if t.strip())
  c['mei_terms']=' | '.join(sorted(set(terms)));c['collection_groups']='core'
  candidates=editions[c['host_istc_id']]['gw_candidates']
  codes=sorted({code for g in candidates for code in re.findall(r'\b[a-z]{3}\b',str(g.get('Sprache') or ''))})
  langs[c['host_istc_id']]={'codes':codes}
 for s in stations:
  s.update(spatial_precision='locality',map_point_policy='',display_uncertainty='',location_resolution_note='',date_warning='',source_date_label='',geolocation_certainty='')
  lookup=s['mapping_lookup_name'] or s['location_label'];category=s['locality_review']
  m=holdings.get(s['institution_id']) if s['station_type']=='current_holding' else mappings.get(lookup)
  if m and not (s['latitude'] and s['longitude']):
   s.update(latitude=m['latitude'],longitude=m['longitude'],preferred_placename=m['name'],place_authority='GeoNames',place_authority_id=m['gid'],place_authority_url=m['coordinate_source'],coordinate_source=m['coordinate_source'],location_resolution_status='reviewed_city_match',location_resolution_note=m['note'])
  if lookup in extra['regions'] or lookup=='OrtSüddeutschland' or 'region_not_city' in category:
   s.update(spatial_precision='region',map_point_policy='no_locality_point',display_uncertainty='Region only; no local map point')
  if lookup=='Seefeld':s.update(latitude='',longitude='',map_point_policy='no_locality_point',display_uncertainty='Unidentified parish of Seefeld; clarification with Zurich cataloguers pending')
  # Suppress conflicting source coordinates rather than turn them into false journeys.
  if (s['place_name']=='Zürich' or s['location_label']=='Zürich') and s['latitude'] and (abs(float(s['latitude'])-47.36667)>.15 or abs(float(s['longitude'])-8.55)>.15):
   s.update(map_point_policy='no_locality_point',display_uncertainty='Source place label and coordinates conflict; map point withheld')
   issues.append({'station_id':s['station_id'],'mei_id':s['mei_id'],'kind':'coordinate_conflict','detail':'Zürich label with '+s['latitude']+', '+s['longitude']+'; original retained, point suppressed'})
  if s['station_type']=='print_place':
   candidates=editions[s['host_istc_id']]['gw_candidates'];labels=list(dict.fromkeys(str(c['Datum'] or '') for c in candidates));s['source_date_label']=' | '.join(filter(None,labels))
   places=set(str(c['Druckort'] or '') for c in candidates)
   if not s['location_label'] and len(places)==1:s['location_label']=next(iter(places))
   norms=set(str(c['Datum normiert'] or '') for c in candidates)
   if len(norms)==1:
    yrs=re.findall(r'(?<!\d)(1[3456]\d{2})(?!\d)',next(iter(norms)))
    s['time_start']=min(yrs) if yrs else '';s['time_end']=max(yrs) if yrs else ''
   if len(candidates)>1 and len(norms)>1:
    s['time_start']=s['time_end']='';s['date_warning']='Multiple GW date statements; no single timeline date selected'
   if not candidates:
    s['source_date_label']=records[s['mei_id']].get('hostItem',{}).get('imprint','')
   if re.search(r'\b(um|vor|nach|zwischen|nicht|about|before|after)\b|\?|\[',s['source_date_label']):
    s['display_uncertainty']='Source dating is approximate or bounded; timeline uses a catalogue-derived year as a display anchor'
   if '?' in lookup or 'multiple_or_alternative_places' in category:
    s['display_uncertainty']='Printing locality uncertain or multiple; no single point inferred'
  if s['time_start'] and s['time_end'] and int(s['time_start'])>int(s['time_end']):s['date_warning']='Source date range is reversed; omitted from historical timeline'
  if s['date_warning']:issues.append({'station_id':s['station_id'],'mei_id':s['mei_id'],'kind':'date_review','detail':s['date_warning']})
  if not(s['latitude'] and s['longitude']) and not s['display_uncertainty']:s['display_uncertainty']='No identified local map point'
 # Flag events ending before printing without silently reordering the evidence.
 birth={s['copy_id']:int(s['time_start']) for s in stations if s['station_type']=='print_place' and s['time_start']}
 for s in stations:
  if s['station_type']=='provenance_place' and s['time_end'] and s['copy_id'] in birth and int(s['time_end'])<birth[s['copy_id']]:
   s['date_warning']='Source provenance date precedes the printing-date anchor; omitted from historical timeline'
   issues.append({'station_id':s['station_id'],'mei_id':s['mei_id'],'kind':'date_review','detail':s['date_warning']})
 assert len(copies)==len(records) and len({c['copy_id'] for c in copies})==len(records)
 assert len({s['station_id'] for s in stations})==len(stations)
 assert all(s['copy_id'] in records for s in stations)
 for c in copies:
  ss=[s for s in stations if s['copy_id']==c['copy_id']]
  assert sum(s['station_type']=='print_place' for s in ss)==1 and sum(s['station_type']=='current_holding' for s in ss)==1
 write(out/'copies.csv',copies);write(out/'stations.csv',stations);save(out/'edition-languages.json',{'editions':langs});save(out/'digital-links.json',{'copies':{},'editions':{}})
 write(derived/'map-review-issues.csv',issues)
 unresolved=[{'station_id':s['station_id'],'mei_id':s['mei_id'],'station_type':s['station_type'],'location_label':s['location_label'],'reason':s['display_uncertainty'] or s['map_point_policy']} for s in stations if not(s['latitude'] and s['longitude']) or s['map_point_policy']]
 if unresolved:write(derived/'unmapped-stations.csv',unresolved)
 summary={'institutions':len({c['holding_institution_id'] for c in copies}),'copies':len(copies),'stations':len(stations),'mapped_stations':sum(bool(s['latitude'] and s['longitude'] and not s['map_point_policy']) for s in stations),'issue_types':dict(Counter(i['kind'] for i in issues)),'retrieved_at':raw['retrieved_at'],'source_query':raw['query']}
 save(out/'summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
