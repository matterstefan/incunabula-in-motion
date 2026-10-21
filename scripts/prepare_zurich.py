"""Prepare source-linked edition and station tables without network access."""
import csv, json, re
from collections import defaultdict, Counter
from pathlib import Path
from transform_mei import transform
from build_itinerary_stations import build_rows, validate_rows, write_csv as write_stations
from fetch_library import summarise
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields=None):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def save(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 raw=json.loads((ROOT/'data/retrieved/zurich-full.json').read_text())
 records=raw['records']
 assert raw['complete'] and len(records)==raw['reported_hits']==len({r['id'] for r in records})
 assert all(r['holdingInstitutionId']=='ZurichZB' for r in records)
 links=[dict(mei_id=r['id'],host_istc_id=r['hostItemId'],requested_istc_id=r['hostItemId'],relation_type='direct',linked_copy_id=r.get('copyId'),holding_institution_id='ZurichZB',shelfmark=r.get('shelfmark')) for r in records]
 adapter=OUT/'mei-adapter.json'
 save(adapter,{'metadata':{'retrieved_at':raw['retrieved_at'],'source':raw['endpoint']},'records':records,'relationships':links})
 counts=transform(adapter,OUT)
 copies=read(OUT/'mei-copies.csv')
 for c in copies:
  c['copy_id']=c['mei_id'] # public identity follows MEI, retain source copyId in raw snapshot
 write(OUT/'mei-copies.csv',copies)
 gw=json.loads((ROOT/'data/sources/gw-zurich-editions.json').read_text())
 by_id=defaultdict(list)
 for r in gw['rows']:
  for identifier in re.findall(r'i[a-z]\d{8}',str(r['ISTC'] or '')):by_id[identifier].append(r)
 editions={};pilot=[];reviews=[]
 for identifier in sorted({r['hostItemId'] for r in records}):
  candidates=by_id[identifier];assert candidates
  # Never arbitrarily choose one of multiple GW records.
  single=candidates[0] if len(candidates)==1 else None
  date=str(single['Datum normiert'] or '') if single else ''
  years=re.findall(r'(?<!\d)(1[3456]\d{2})(?!\d)',date)
  start=min(years) if years else '';end=max(years) if years else ''
  editions[identifier]={'gw_candidates':candidates,'status':'single_gw_match' if single else 'multiple_gw_matches_review',
     'mei_host_items':[{'mei_id':r['id'],'hostItem':r.get('hostItem',{})} for r in records if r['hostItemId']==identifier]}
  if not single:
   for c in candidates:reviews.append({'istc_id':identifier,**c})
  pilot.append({'istc_id':identifier,'year_from':start,'year_to':end,'print_places_gw':str(single['Druckort'] or '') if single else '',
    'gw_ids':' | '.join(str(c['GW-Nr']) for c in candidates),'corpus_file':'gw-zurich-editions.json'})
 save(OUT/'editions.json',{'source':gw['source'],'editions':editions})
 write(OUT/'gw-multiple-matches.csv',reviews)
 stations=build_rows(pilot,copies,read(OUT/'mei-provenance.csv'),read(OUT/'mei-places.csv'),read(OUT/'mei-record-links.csv'))
 validate_rows(stations,{p['place_occurrence_id'] for p in read(OUT/'mei-places.csv')})
 for s in stations:
  if s['station_type']=='print_place':
   e=editions[s['host_istc_id']]
   s['source_snapshot']='data/sources/gw-zurich-editions.json'
   s['source_url']=' | '.join('https://www.gesamtkatalogderwiegendrucke.de/docs/'+str(c['GW-Nr'])+'.htm' for c in e['gw_candidates'])
   if e['status']=='multiple_gw_matches_review':
    s['location_resolution_status']='multiple_gw_matches_review';s['note']='Printing place and date withheld pending review of GW candidates.'
 write_stations(OUT/'stations-source.csv',stations)
 # Reuse only exact, context-free, unambiguous reviewed mappings.
 mappings=read(ROOT/'data/authority/place-authorities.csv')
 for s in stations:
  s['resolution_mapping_id']=''
  if s['latitude'] and s['longitude']:continue
  options=[m for m in mappings if m['station_type']==s['station_type'] and not m.get('match_context_key')
   and m.get('resolution_status')=='resolved' and m.get('source_key') and s.get(m['match_field'])==m['source_key']
   and m['latitude'] and m['longitude']]
  points={(m['latitude'],m['longitude']) for m in options}
  if len(points)==1:
   m=options[0];s.update(latitude=m['latitude'],longitude=m['longitude'],preferred_placename=m['resolved_name'],
    place_authority=m['place_authority'],place_authority_id=m['place_authority_id'],place_authority_url=m['place_authority_url'],
    location_resolution_status='reused_reviewed_mapping',resolution_mapping_id=m['mapping_id'])
 write(OUT/'stations-prepared.csv',stations)
 unresolved=defaultdict(list)
 for s in stations:
  if not s['latitude'] or not s['longitude']:
   unresolved[(s['station_type'],s['location_label'],s['place_authority_id'],s['location_resolution_status'])].append(s)
 review=[dict(station_type=k[0],location_label=k[1],authority_id=k[2],status=k[3],station_count=len(v),
   example_mei_id=v[0]['mei_id'],example_mei_url=v[0]['source_url'],suggested_place='',review_note='') for k,v in sorted(unresolved.items())]
 write(OUT/'locations-to-review.csv',review)
 vocabulary,coverage=summarise(records)
 write(OUT/'subjects.csv',[dict(term=k,source_fields=' | '.join(sorted(v['fields'])),copies=len(v['copies']),editions=len(v['editions'])) for k,v in sorted(vocabulary.items())])
 summary={**counts,**coverage,'gw_linked_editions':len(editions),'gw_multiple_match_editions':sum(e['status'].startswith('multiple') for e in editions.values()),
  'stations':len(stations),'station_types':dict(Counter(s['station_type'] for s in stations)),
  'stations_with_coordinates':sum(bool(s['latitude'] and s['longitude']) for s in stations),
  'unresolved_place_groups':len(review),'reused_mapping_stations':sum(bool(s['resolution_mapping_id']) for s in stations)}
 save(OUT/'preparation-summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
