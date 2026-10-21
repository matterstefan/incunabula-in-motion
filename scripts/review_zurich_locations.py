"""Classify unresolved localities and reuse exact city matches, offline.
Run after prepare_zurich.py. Never overwrite source station tables.
"""
import csv,json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 out=ROOT/'data/derived'; authority=ROOT/'data/authority'
 cities=json.loads((authority/'corpus-city-points.json').read_text())
 reviewed=json.loads((authority/'reviewed-city-points.json').read_text())
 index=defaultdict(list)
 for c in cities:
  for name in [c['name']]+c.get('aliases',[]):index[name].append(c)
 for name,c in reviewed.items():index[name].append(c)
 editions=json.loads((out/'editions.json').read_text())['editions']
 consensus=[]
 for identifier,e in editions.items():
  if len(e['gw_candidates'])<2:continue
  places={str(c['Druckort'] or '').strip() for c in e['gw_candidates']}
  assert len(places)==1 and '' not in places
  consensus.append(dict(istc_id=identifier,printing_place=next(iter(places)),gw_ids=' | '.join(c['GW-Nr'] for c in e['gw_candidates']),decision='Shared printing place; retain all titles and dates; no candidate selected.'))
 write(out/'gw-place-consensus.csv',consensus)
 shared={r['istc_id']:r['printing_place'] for r in consensus}
 rows=read(out/'stations-prepared.csv');groups=defaultdict(list)
 regions={'Deutschland(?)','Niederlande oder Niederrhein','Süddeutschland','Ort Süddeutschland','Westschweiz'}
 unknown={'','Unbekannt','Unbekannter Ort','unbekannt','unbekannter Ort'}
 for s in rows:
  s['locality_review']='';s['coordinate_source']='';s['mapping_lookup_name']=''
  if s['latitude'] and s['longitude']:continue
  label=s['location_label'].strip();lookup=label
  if s['station_type']=='print_place' and s['host_istc_id'] in shared:
   lookup=shared[s['host_istc_id']];s['locality_review']='GW candidates agree on place; date remains withheld'
  # Explicit corrections in GW are not our own historical attribution.
  correction=re.search(r'\[vielmehr:\s*(.*?)\]',lookup)
  if correction:lookup=correction.group(1).strip()
  if lookup in unknown:category='no_locality_in_source'
  elif lookup in regions:category='region_not_city'
  elif ' oder ' in lookup or ' und ' in lookup:category='multiple_or_alternative_places'
  elif '?' in lookup:category='source_uncertainty_preserved'
  elif lookup=='Seefeld':category='expert_identification_needed'
  else:category='technical_city_lookup_pending'
  # Ambiguous bare names need context, even if an old vocabulary has a match.
  options=[] if lookup in {'Freiburg','Burgdorf','Rougemont','Seefeld','Vienne'} else index.get(lookup,[])
  points={(float(c['lat']),float(c['lon'])) for c in options}
  if len(points)==1 and category=='technical_city_lookup_pending':
   c=options[0];s.update(latitude=c['lat'],longitude=c['lon'],preferred_placename=c['name'],
    location_resolution_status='exact_existing_city_vocabulary',coordinate_source=c.get('source',''),
    resolution_mapping_id='city:'+str(c.get('gid','')),mapping_lookup_name=lookup)
   category='resolved_existing_city_vocabulary'
  s['locality_review']='; '.join(filter(None,[s['locality_review'],category]))
  s['mapping_lookup_name']=lookup
  groups[(label,lookup,s['station_type'],category)].append(s)
 write(out/'stations-reviewed.csv',rows)
 report=[]
 for (label,lookup,typ,category),ss in sorted(groups.items()):
  note=''
  if lookup=='Seefeld':note='Ra 20: Sum parochiae Seefeldensis; later Rheinau. Which parish?'
  if lookup=='Vienne':note='Both MEI host items explicitly give imprint_country_code FR. French Vienne, not Vienna; coordinate lookup pending.'
  if category=='multiple_or_alternative_places':note='Keep source alternatives or multiple production places; do not invent a sequence.'
  report.append(dict(source_label=label,lookup_name=lookup,station_type=typ,classification=category,station_count=len(ss),example_mei_id=ss[0]['mei_id'],mei_url='https://data.cerl.org/mei/'+ss[0]['mei_id'],note=note))
 write(out/'locality-review-triage.csv',report)
 write(out/'locality-expert-questions.csv',[r for r in report if r['classification']=='expert_identification_needed'])
 print(json.dumps({'GW_consensus_groups':len(consensus),'newly_resolved_stations':sum(s['location_resolution_status']=='exact_existing_city_vocabulary' for s in rows),'remaining_unlocated_stations':sum(not(s['latitude'] and s['longitude']) for s in rows),'expert_questions':sum(r['classification']=='expert_identification_needed' for r in report)},indent=2))
if __name__=='__main__':main()
