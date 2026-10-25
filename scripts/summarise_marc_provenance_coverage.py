#!/usr/bin/env python3
"""Reproducible coverage census of the existing assigned MARC evidence.

No new catalogue queries or automatic geographical/chronological inference.
The unit is (record ID, institution, shelfmark), not a verified physical volume.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,html
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/research/zurich-postincunabula-export-20261023'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def key(r):return (r['record_id'],r['institution_code'],r['shelfmark'])
def dump(name,obj):
 (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def build():
 refs=read(DATA/'working-copy-references.json');bykey={key(r):r for r in refs}
 assert len(bykey)==len(refs)
 assignments=read(DATA/'provenance-assignments.json')
 old=read(DATA/'station-candidates.json');supp=read(DATA/'collection-place-supplement.json')
 pilot=read(ROOT/'data/map/marc-pilot.json');extra=read(DATA/'additional-dated-events.json')
 linked=defaultdict(list);open_by_record=defaultdict(list)
 for f in assignments:
  if f['assignment']=='open':open_by_record[f['record_id']].append(f)
  elif f['assignment'] in ['explicit','plausible']:
   for i,s in f['targets']:
    k=(f['record_id'],i,s)
    if k in bykey:linked[k].append(f)
 loc=defaultdict(list)
 for label,entries in [('station-candidates',old),('collection-place-supplement',supp)]:
  for r in entries:
   if key(r) in bykey:loc[key(r)].append({'layer':label,'place':r['place'],'basis':r.get('place_basis'), 'rule':r.get('rule'), 'owner':r.get('owner'),'date':r.get('date')})
 prior_keys=set(loc);pilot_keys={key(r) for r in pilot};extra_keys={key(r) for r in extra}
 dated=pilot_keys|extra_keys
 for r in pilot:
  s=r['stations'][1];loc[key(r)].append({'layer':'dated-pilot','place':s['place'],'basis':s['place_basis'],'date':{'year':s['year'],'certainty':s['date_certainty']}})
 for r in extra:loc[key(r)].append({'layer':'additional-events','place':r['place'],'basis':'named institution or explicit purchase locality','date':{'year':r['year']}})
 rows=[];coverage=Counter();tag_refs=defaultdict(set)
 for k,r in bykey.items():
  fs=linked[k];opens=open_by_record[k[0]]
  scope='explicit' if any(f['assignment']=='explicit' for f in fs) else 'plausible' if fs else 'open_only' if opens else 'no_detected_candidate'
  coverage[scope]+=1
  core=[f for f in fs if f['evidence_kind']=='catalogue_provenance_field_or_owner_role']
  lexical=[f for f in fs if f['evidence_kind']=='lexical_note_candidate']
  for f in fs:tag_refs[f['tag']].add(k)
  rows.append({'record_id':k[0],'institution_code':k[1],'shelfmark':k[2],'title':r['title'],
    'catalogue_url':'https://swisscollections.ch/Record/'+k[0], 'copy_assignment_category':scope,
    'linked_fields':len(fs),'linked_core_fields':len(core),'linked_lexical_candidates':len(lexical),
    'open_fields_in_record':len(opens),'linked_field_tags':sorted({f['tag'] for f in fs}),
    'linked_year_tokens':sorted({y for f in fs for y in f.get('year_tokens_not_events',[])}),
    'linked_place_tokens':sorted({v for f in fs for v in f.get('place_tokens_not_stations',[])}),
    'place_candidates':loc[k],'in_prior_409':k in prior_keys,'in_dated_pilot':k in pilot_keys,
    'in_additional_events':k in extra_keys,'dated_event_prepared':k in dated,
    'has_only_undated_prepared_places':bool(loc[k]) and not k in dated and not any(v.get('date') for v in loc[k])})
 groups={}
 for k,fs in linked.items():
  for f in fs:
   if f['tag'] not in ('700','710','711') or f['evidence_kind']!='catalogue_provenance_field_or_owner_role':continue
   vals=lambda c:[v for code,v in f['subfields'] if code==c]
   names=vals('a');ids=vals('0');label=' | '.join(names)
   if not label:continue
   gkey=(f['tag'],ids[0] if ids else label)
   g=groups.setdefault(gkey,{'tag':f['tag'],'authority_ids':set(),'names':set(),'refs':set()})
   g['names'].update(names);g['authority_ids'].update(ids);g['refs'].add(k)
 group_rows=[]
 for g in groups.values():
  keys=g['refs'];known=keys & {k for k,vs in loc.items() if vs}
  group_rows.append({'tag':g['tag'],'names':sorted(g['names']),'authority_ids':sorted(g['authority_ids']),
    'references':len(keys),'references_without_any_prepared_place':len(keys-known),
    'references_with_some_prepared_place':len(known),
    'references_without_prepared_dated_event':len(keys-dated),
    'reference_keys':[list(k) for k in sorted(keys)],
    'warning':'A prepared place may belong to another owner. Overlapping owner groups cannot be added as copy counts. Authority IDs identify catalogue entities, not places or ownership dates.'})
 group_rows.sort(key=lambda g:(-g['references_without_any_prepared_place'],-g['references'],g['names']))
 def count(pred):return sum(bool(pred(r)) for r in rows)
 layers=[]
 for name,entries in [('Earlier station candidates',old),('Collection/place supplement',supp)]:
  bases=defaultdict(set)
  for x in entries:bases[(x.get('place_basis'),x.get('rule'))].add(key(x))
  for (basis,rule),keys in bases.items():layers.append({'layer':name,'basis':basis,'rule':rule,'distinct_references':len(keys)})
 strictdatekeys={key(x) for x in old if x.get('date')}
 summary={'unit':'record_id + institution_code + shelfmark; not verified physical copies',
   'working_references':len(refs),'references_with_empty_852_shelfmark':sum(not r['shelfmark'] for r in refs),'bibliographic_records':len({r['record_id'] for r in refs}),
   'assignment_categories_exclusive':dict(coverage),
   'linked_any_candidate':count(lambda r:r['linked_fields']),
   'linked_core_indicator':count(lambda r:r['linked_core_fields']),
   'linked_lexical_only':count(lambda r:r['linked_lexical_candidates'] and not r['linked_core_fields']),
   'linked_year_tokens_not_events':count(lambda r:r['linked_year_tokens']),
   'linked_place_tokens_not_stations':count(lambda r:r['linked_place_tokens']),
   'prior_place_candidates_union':len(prior_keys),'pilot_references':len(pilot_keys),
   'additional_event_references':len(extra_keys),'pilot_and_additional_union':len(dated),
   'all_prepared_places_union':count(lambda r:r['place_candidates']),
   'references_with_places_but_no_pilot_or_extra_event':count(lambda r:r['place_candidates'] and not r['dated_event_prepared']),
   'old_dated_candidates_outside_new_pilot':len(strictdatekeys-dated),
   'strictly_undated_place_references':count(lambda r:r['has_only_undated_prepared_places']),
   'old_dated_candidate_keys_outside_new_pilot':[list(k) for k in sorted(strictdatekeys-dated)],
   'references_with_any_recognised_dated_candidate':len(dated|strictdatekeys),
   'references_with_GND_owner_id':len(set().union(*(g['refs'] for g in groups.values() if any(i.startswith('(DE-588)') for i in g['authority_ids'])))),
   'linked_references_without_prepared_places':count(lambda r:r['linked_fields'] and not r['place_candidates']),
   'prepared_place_without_linked_candidate':count(lambda r:r['place_candidates'] and not r['linked_fields']),
   'linked_references_by_field_tag':{tag:len(keys) for tag,keys in sorted(tag_refs.items())},
   'source_layers_nonexclusive':layers,
   'files_sha256':{n:hashlib.sha256((DATA/n).read_bytes()).hexdigest() for n in ['working-copy-references.json','provenance-assignments.json','station-candidates.json','collection-place-supplement.json','additional-dated-events.json']},
   'pilot_sha256':hashlib.sha256((ROOT/'data/map/marc-pilot.json').read_bytes()).hexdigest(),
   'limitations':['Census of current extraction results, not a full manual assessment of catalogue quality.','No detected candidate does not mean no provenance in the catalogue or artefact.','Exact copy linkage is independent of correctness of provenance or date.','Layer and field counts overlap; dates in lexical tokens may be citations or unrelated events.','Most named institution-to-place mappings and collection mappings are enrichment, even when the institution name itself is explicit.','45 reproduction-review references remain in the working baseline; this is not a final holdings census.']}
 return rows,group_rows,summary

def main():
 rows,groups,s=build()
 for name,obj in [('coverage-audit-references.json',rows),('coverage-audit-owner-groups.json',groups),('coverage-audit-summary.json',s)]:dump(name,obj)
 labels=[('Grundbestand: Katalognachweise',s['working_references']),('Zugehörige bibliographische Datensätze',s['bibliographic_records']),('Mit zugeordneten Provenienzfeldern oder Textkandidaten',s['linked_any_candidate']),('Davon: Kernfelder / Vorbesitzerrollen',s['linked_core_indicator']),('Davon: nur Textkandidaten',s['linked_lexical_only']),('Nur offene Zuordnung im Datensatz',s['assignment_categories_exclusive']['open_only']),('Kein erkannter Kandidat',s['assignment_categories_exclusive']['no_detected_candidate']),('Historische Ortszuordnung: bisherige Schichten',s['prior_place_candidates_union']),('Historische Ortszuordnung: alle vorbereiteten Schichten',s['all_prepared_places_union']),('Datierte Ereignisse im Pilot und Zusatzpaket',s['pilot_and_additional_union']),('Weitere ältere datierte Kandidaten ausserhalb des Piloten',s['old_dated_candidates_outside_new_pilot']),('Ortszuordnungen ausschliesslich ohne Datum',s['strictly_undated_place_references'])]
 md=['# Provenienzen der ZB-Postinkunabeln: Gesamtschau','', 'Stand: 25. Oktober 2026. Grundlage ist der vorhandene Export vom 23. Oktober; keine neuen Katalogabfragen.','', '**Die kleine Kartenmenge ist kein Mass für den Erschliessungsgrad.** Die bisherigen Ereignisregeln erschliessen nur einen engen Ausschnitt.','', '| Messgrösse | Anzahl |','|---|---:|']
 md += [f'| {label} | {n:,} |'.replace(',','’') for label,n in labels]
 md += ['', 'Die Zeilen sind nicht durchgehend ineinander geschachtelt. Gezählt wird die Kombination aus Datensatz-ID, Institutionscode und Signatur. Sie ist weder ein physischer Band noch notwendigerweise genau ein physisches Exemplar. Mehrere Drucke desselben Sammelbandes bleiben getrennte Nachweise.','', f"Technischer Sonderfall: {s['references_with_empty_852_shelfmark']} Nachweis hat im bisherigen Arbeitsschlüssel eine leere Signatur. Beim Datensatz 991093383479705501 ist 852$j im Originalexport leer; 949$h nennt jedoch II DD 381,27 und 949$z die Bestellsignatur II DD 381. Beide Felder tragen dieselbe lokale Kennung. Für diese Bestandsbilanz bleibt der bisherige Schlüssel erhalten; die technische Korrektur ist separat dokumentiert. Die Gesamtzahl wird dadurch nicht verändert.", '', '## 1. Was im Katalog erkannt wurde','', f"{s['linked_any_candidate']} Nachweise haben explizit oder plausibel zugeordnete Felder. Davon enthalten {s['linked_core_indicator']} ein Kernfeld (561 oder Vorbesitzerrolle in 700/710); bei {s['linked_lexical_only']} gibt es ausschliesslich sprachlich erkannte Textkandidaten. Auch Kernfelder sind keine unabhängig verifizierte Besitzgeschichte.", '', 'Die vier ausschliessenden Zuordnungskategorien lauten:']
 for label,n in s['assignment_categories_exclusive'].items():md.append(f'- `{label}`: {n}')
 md += ['', '`explicit` betrifft die Zuordnung des Feldes zur Signatur, nicht die historische Gewissheit. `plausible` beruht auf dokumentierten Kontextregeln. `open_only` enthält Kandidaten im gemeinsamen Datensatz, deren Exemplarzuordnung offen bleibt. `no_detected_candidate` bedeutet ausschliesslich: mit dem bisherigen Suchverfahren kein Kandidat erkannt. Daraus folgt nicht, dass das Artefakt keine Provenienzspuren hat oder der Katalog dazu schweigt.','',f"{s['linked_year_tokens_not_events']} Nachweise haben erkannte Jahreszahlen in zugeordneten Feldern; diese sind **noch keine {s['linked_year_tokens_not_events']} datierten Provenienzereignisse**. {s['linked_place_tokens_not_stations']} haben Ortswörter aus dem bisher verwendeten begrenzten Wortschatz; auch das ist keine vollständige Ortsauswertung.",'',f"Bei {s['references_with_GND_owner_id']} Nachweisen enthalten die zugeordneten Vorbesitzerfelder eine GND-ID. Normdaten sind hier also bereits eine wesentliche Ressource. Diese IDs können Identitäten bündeln, liefern aber nicht automatisch den Aufenthaltsort des Druckes oder ein Besitzdatum.",'', '## 2. Herkunft der Ortszuordnungen','','Die früher genannten 409 sind die Vereinigung zweier Ergänzungsschichten. Sie enthalten sowohl Katalogangaben als auch Handbuch- und biographische Ableitungen. Diese Tabelle zeigt ihre Herkunft, ohne die überlappenden Zahlen zu addieren:','','| Schicht | Grundlage / Regel | Nachweise |','|---|---|---:|']
 for row in s['source_layers_nonexclusive']:md.append(f"| {row['layer']} | {row['basis']} / {row['rule'] or '—'} | {row['distinct_references']} |")
 md += ['', f"Mit Pilot und jüngster Vorbereitung sind insgesamt {s['all_prepared_places_union']} Nachweise mit mindestens einer vorbereiteten historischen Ortszuordnung vorhanden. {s['prepared_place_without_linked_candidate']} davon haben keinen zugeordneten Feldkandidaten; hier greift insbesondere die separate Sammlungsschicht. Das ist kein Widerspruch, sondern eine andere Evidenzquelle.",'','## 3. Datierung ist ein zusätzlicher Engpass','',f"31 Pilotnachweise plus 19 weitere Stationskandidaten ergeben 42 verschiedene Nachweise. Die älteren Stationskandidaten enthalten darüber hinaus {s['old_dated_candidates_outside_new_pilot']} datierte Kandidaten, die nicht in diesen engen Pilotregeln vorkommen. Insgesamt sind somit {s['references_with_any_recognised_dated_candidate']} Nachweise mit irgendeinem vorbereiteten datierten Kandidaten vorhanden. Die zusätzlichen älteren Fälle sind noch keine vollständig vorbereiteten Kartenrouten.", '',f"Bei {s['strictly_undated_place_references']} Nachweisen liegen bislang ausschliesslich undatierte Ortszuordnungen vor. Sie sind für eine ortsbezogene Recherche nutzbar, aber nicht ohne Weiteres als Aufenthalt in einem bestimmten Slider-Jahr darstellbar.",'','Der ältere datierte Kandidat ausserhalb des neuen Piloten betrifft Signatur 4.221: den Besitzvermerk von 1753, dessen Zuordnung zu Johann Caspar Hagenbuch und Zürich bereits als wahrscheinlich diskutiert wurde. Er darf durch die engeren Rekonstruktionsregeln nicht aus dem Blick geraten.', '', '## 4. Nächste Schritte: Vorschlag zur Besprechung','','1. **Zuerst die vorhandene Menge nutzbar machen:** undatierte Ortsbezüge in der Exemplardetailansicht aufführen, separat von der datierten Reihenfolge. Keine Pfeile oder Linien zwischen undatierten Stationen, deren Reihenfolge unbekannt ist.','2. **Eine zeitunabhängige Ortsübersicht prüfen:** „Historical places, including undated evidence“ als klar getrennte Ansicht. Pro Druck und Ort nur einmal zählen; keine Aussage über gleichzeitige Bestände. Nicht mit der bestehenden Aufenthaltskarte für ein bestimmtes Jahr vermischen.','3. **Wiederkehrende Vorbesitzer bündeln:** die untenstehenden Namen einmal auf Normdaten, Identität und belegte Ortsbezüge prüfen. Eine Person kann mehrere Wirkungsorte haben; Lebensdaten ersetzen keine Besitzdaten. Deshalb zunächst Kandidaten, keine automatische Zuordnung sämtlicher Drucke zum bekanntesten Wohnort.','4. **Die 170 offenen Zuordnungen separat behandeln:** zuerst häufige Muster und Sammelbandsituationen prüfen, nicht tausende Einzelfälle durchgehen.','5. **Keine Erschliessungsquote behaupten:** vor einer Aussage zur ZB-Katalogisierung eine kleine, nach Feldtypen geschichtete Stichprobe der Treffer und Nichttreffer am Originalexport prüfen. Das misst auch die Grenzen unserer Erkennung.','','## 5. Vorbesitzergruppen als Arbeitspakete','','Priorisiert nach Nachweisen ohne irgendeine vorbereitete historische Ortszuordnung. Eine schon vorhandene Ortszuordnung kann einen anderen Vorbesitzer betreffen. Gruppen überschneiden sich.','','| Name(n) | Feld | Nachweise insgesamt | Ohne vorbereiteten Ort | Normdaten-ID vorhanden |','|---|---|---:|---:|---|']
 for g in groups[:20]:md.append(f"| {' / '.join(g['names']).replace('|','/')} | {g['tag']} | {g['references']} | {g['references_without_any_prepared_place']} | {'; '.join(g['authority_ids']) or '—'} |")
 md += ['', '## Wiederherstellung und Dateien','','`python3 scripts/summarise_marc_provenance_coverage.py` erstellt diese Übersicht, eine HTML-Lesefassung und drei JSON-Dateien. Die nachweisweise Tabelle dokumentiert alle Zählkriterien; die Gruppentabelle enthält die zugehörigen Schlüssel. Quell-Hashes stehen in `coverage-audit-summary.json`. Das Skript verändert keine Karten- oder Katalogdaten.','', 'Die HTML-Lesefassung enthält zusätzlich eine suchbare Nachweisliste. Alle Angaben sind Ergebnisse der derzeitigen Extraktion. Die 45 noch offenen Reproduktionsprüffälle verbleiben im Grundbestand.']
 report='\n'.join(md)+'\n';(ROOT/'docs/marc-provenance-coverage-overview.md').write_text(report,encoding='utf-8')
 # Plain HTML with table/filter: no dependencies and no fetched remote data.
 table=''.join('<tr><td><a href="'+html.escape(r['catalogue_url'])+'">'+html.escape(r['shelfmark'])+'</a></td><td>'+html.escape(' / '.join(r['title']))+'</td><td>'+r['copy_assignment_category']+'</td><td>'+str(r['linked_fields'])+'</td><td>'+html.escape(', '.join(sorted({v['place'] for v in r['place_candidates']})))+'</td><td>'+('ja' if r['dated_event_prepared'] else 'nein')+'</td></tr>' for r in rows)
 page='<!doctype html><html lang="de"><meta charset="utf-8"><title>Provenienz-Gesamtschau</title><style>body{font:16px/1.5 system-ui;margin:2rem;max-width:1400px}pre{white-space:pre-wrap;font:inherit}td,th{padding:.5rem;border:1px solid #ccc;vertical-align:top}table{border-collapse:collapse;width:100%;font-size:14px}input{padding:.7rem;width:90%;margin:1rem 0}th{background:#eee}</style><h1>Provenienz-Gesamtschau</h1><pre>'+html.escape(report)+'</pre><h2>Nachweise durchsuchen</h2><p>Die Datumsspalte bezieht sich nur auf den neuen Pilot plus Zusatzereignisse, nicht auf sämtliche älteren Kandidaten.</p><input id="q" aria-label="Nachweise durchsuchen" placeholder="Signatur, Titel, Ort oder Zuordnung"><table><thead><tr><th>Signatur</th><th>Titel</th><th>Zuordnung</th><th>Felder</th><th>Vorbereitete Orte</th><th>Pilot/Zusatz datiert</th></tr></thead><tbody>'+table+'</tbody></table><script>const rows=[...document.querySelectorAll("tbody tr")];document.getElementById("q").addEventListener("input",e=>{const q=e.target.value.toLocaleLowerCase();for(const r of rows)r.hidden=!r.textContent.toLocaleLowerCase().includes(q)});</script></html>'
 (DATA/'coverage-audit-overview.html').write_text(page,encoding='utf-8')
 print(json.dumps({k:v for k,v in s.items() if k not in ['files_sha256','source_layers_nonexclusive','limitations']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
