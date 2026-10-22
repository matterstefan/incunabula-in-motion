"""Prepare all current Swiss MEI holdings offline; source snapshot stays intact."""
import json,re,csv
from pathlib import Path
from collections import defaultdict
from transform_mei import transform
from build_itinerary_stations import build_rows,validate_rows
from prepare_zurich import read,write,save
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/derived/swiss'
def main():
 raw=json.loads((ROOT/'data/retrieved/swiss-inventory/swiss-mei-snapshot.json').read_text());records=raw['records']
 assert raw['complete'] and len(records)==len({r['id'] for r in records})
 assert all((r.get('holdingInstitution') or {}).get('country')=='CH' for r in records)
 links=[dict(mei_id=r['id'],host_istc_id=r.get('hostItemId',''),requested_istc_id=r.get('hostItemId',''),relation_type='direct',linked_copy_id=r.get('copyId'),holding_institution_id=r['holdingInstitutionId'],shelfmark=r.get('shelfmark')) for r in records]
 save(OUT/'mei-adapter.json',{'metadata':{'retrieved_at':raw['retrieved_at'],'source':'https://data.cerl.org/mei/_search'},'records':records,'relationships':links})
 transform(OUT/'mei-adapter.json',OUT);copies=read(OUT/'mei-copies.csv')
 for c in copies:c['copy_id']=c['mei_id']
 write(OUT/'mei-copies.csv',copies)
 gw=json.loads((ROOT/'data/sources/gw-swiss-editions.json').read_text());byid=defaultdict(list)
 for g in gw['rows']:
  for i in re.findall(r'i[a-z]\d{8}',str(g['ISTC'] or '')):byid[i].append(g)
 editions={};pilot=[]
 for i in sorted({r.get('hostItemId','') for r in records}):
  cs=byid[i];hs=[{'mei_id':r['id'],'hostItem':r.get('hostItem') or {}} for r in records if r.get('hostItemId','')==i]
  editions[i]={'gw_candidates':cs,'mei_host_items':hs,'status':'single_gw_match' if len(cs)==1 else 'multiple_gw_matches_review' if cs else 'no_gw_match'}
  places={str(c['Druckort'] or '') for c in cs};dates={str(c['Datum normiert'] or '') for c in cs}
  yrs=re.findall(r'(?<!\d)(1[3456]\d{2})(?!\d)',next(iter(dates))) if len(dates)==1 else []
  place=next(iter(places)) if len(places)==1 else ''
  # Entire imprint remains the source. Fallback does not mix GW place with MEI date.
  if not cs and i:
   imprint=hs[0]['hostItem'].get('imprint','');place=imprint.split(':',1)[0].strip(' []') if ':' in imprint else ''
   yrs=re.findall(r'(?<!\d)(1[3456]\d{2})(?!\d)',imprint)
  pilot.append(dict(istc_id=i,year_from=min(yrs) if yrs else '',year_to=max(yrs) if yrs else '',print_places_gw=place,gw_ids=' | '.join(str(c['GW-Nr']) for c in cs),corpus_file='gw-swiss-editions.json'))
 save(OUT/'editions.json',{'source':gw['source'],'editions':editions})
 stations=build_rows(pilot,copies,read(OUT/'mei-provenance.csv'),read(OUT/'mei-places.csv'),read(OUT/'mei-record-links.csv'))
 validate_rows(stations,{p['place_occurrence_id'] for p in read(OUT/'mei-places.csv')})
 old={s['station_id']:s for s in read(ROOT/'data/derived/stations-reviewed.csv')}
 mappings=read(ROOT/'data/authority/place-authorities.csv')
 for s in stations:
  s.update(resolution_mapping_id='',locality_review='',coordinate_source='',mapping_lookup_name=s['location_label'])
  if s['station_type']=='print_place':
   cs=editions[s['host_istc_id']]['gw_candidates']
   s['source_snapshot']='data/sources/gw-swiss-editions.json' if cs else 'data/retrieved/swiss-inventory/swiss-mei-snapshot.json'
   s['source_catalogue']='GW' if cs else 'MEI (embedded edition imprint)'
   s['source_url']=' | '.join('https://www.gesamtkatalogderwiegendrucke.de/docs/'+str(c['GW-Nr'])+'.htm' for c in cs) if cs else 'https://data.cerl.org/mei/'+s['mei_id']
  previous=old.get(s['station_id'])
  # Reuse previous display coordinates only when source identity and location agree.
  if previous and s['location_label']==previous['location_label'] and s['place_name']==previous['place_name']:
   for k in ['latitude','longitude','preferred_placename','place_authority','place_authority_id','place_authority_url','location_resolution_status','resolution_mapping_id','locality_review','coordinate_source','mapping_lookup_name']:s[k]=previous.get(k,'')
  if s['latitude'] and s['longitude']:continue
  options=[m for m in mappings if m['station_type']==s['station_type'] and not m.get('match_context_key') and m.get('resolution_status')=='resolved' and m.get('source_key') and s.get(m['match_field'])==m['source_key'] and m['latitude'] and m['longitude']]
  if len({(m['latitude'],m['longitude']) for m in options})==1:
   m=options[0];s.update(latitude=m['latitude'],longitude=m['longitude'],preferred_placename=m['resolved_name'],place_authority=m['place_authority'],place_authority_id=m['place_authority_id'],place_authority_url=m['place_authority_url'],resolution_mapping_id=m['mapping_id'])
  lookup=s['mapping_lookup_name'];correction=re.search(r'\[vielmehr:\s*(.*?)\]',lookup)
  if correction:lookup=correction.group(1).strip();s['mapping_lookup_name']=lookup
  if '?' in lookup:s['locality_review']='source_uncertainty_preserved'
  if ' oder ' in lookup or ' und ' in lookup:s['locality_review']='multiple_or_alternative_places'
 write(OUT/'stations-reviewed.csv',stations)
 groups=defaultdict(list)
 for s in stations:
  if not(s['latitude'] and s['longitude']):groups[(s['station_type'],s['mapping_lookup_name'])].append(s)
 rows=[dict(station_type=k[0],lookup_name=k[1],count=len(ss),mei_id=ss[0]['mei_id'],country=ss[0]['country']) for k,ss in sorted(groups.items())]
 write(OUT/'unlocated.csv',rows);print(len(copies),'copies;',len(stations),'stations;',len(rows),'unlocated groups')
if __name__=='__main__':main()
