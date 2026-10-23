#!/usr/bin/env python3
"""Resume a public swisscollections SRU snapshot and audit exposed provenance."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import json,time,collections
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research/zurich-postincunabula-20261023'
OUT.mkdir(parents=True,exist_ok=True)
NS={'s':'http://www.loc.gov/zing/srw/','m':'http://www.loc.gov/MARC21/slim'}
QUERY='sc.possessingInstitution = Z06 AND dc.date >= 1501 AND dc.date <= 1525'
records={}; pages=[]
from concurrent.futures import ThreadPoolExecutor
def fetch_year(year):
 path=OUT/f'year-{year}.xml'
 query=f'sc.possessingInstitution = Z06 AND dc.date = {year}'
 url='https://sru.swisscollections.ch/swisscollections?'+urlencode(dict(version='1.2',operation='searchRetrieve',query=query,recordSchema='marc21-xml',maximumRecords=500))
 if path.exists():raw=path.read_bytes()
 else:
  for attempt in range(3):
   try:raw=urlopen(url,timeout=90).read();break
   except Exception:
    if attempt==2:raise
    time.sleep(3*(attempt+1))
 tree=ET.fromstring(raw);n=tree.find('s:numberOfRecords',NS)
 if n is None:raise RuntimeError(raw.decode()[:1000])
 count=int(n.text);batch=tree.findall('.//m:record',NS)
 if len(batch)!=count:raise RuntimeError(f'Incomplete year {year}: {len(batch)}/{count}')
 if not path.exists():path.write_bytes(raw)
 print(f'{year}: {count}',flush=True)
 return year,url,batch
with ThreadPoolExecutor(max_workers=1) as pool:
 for year,url,batch in pool.map(fetch_year,range(1501,1526)):
  pages.append({'year':year,'count':len(batch),'url':url})
  for r in batch:
   rid=r.find("m:controlfield[@tag='001']",NS).text
   if rid in records and ET.tostring(records[rid])!=ET.tostring(r):raise RuntimeError('Record changed between year queries: '+rid)
   records[rid]=r
total=len(records)
summary=collections.Counter();rows=[]
for rid,r in records.items():
 fields=r.findall('m:datafield',NS)
 def fs(tag):return [f for f in fields if f.get('tag')==tag]
 def vals(f,c):return [s.text or '' for s in f if s.get('code')==c]
 notes={tag:[{'ind1':f.get('ind1'),'subfields':[(s.get('code'),s.text or '') for s in f]} for f in fs(tag) if f.get('ind1')!='0'] for tag in ['361','541','561']}
 for tag in ['563','590']:notes[tag]=[{'subfields':[(s.get('code'),s.text or '') for s in f]} for f in fs(tag)]
 owners=[f for f in fields if f.get('tag') in ['700','710','711'] and ('fmo' in vals(f,'4') or any('besitz' in x.lower() or 'former owner' in x.lower() for x in vals(f,'e')))]
 holdings=[f for f in fs('852') if 'Z06' in vals(f,'b')];shelves=sorted(set(v for f in holdings for v in vals(f,'j')))
 cf=r.find("m:controlfield[@tag='008']",NS);fixed=cf.text if cf is not None else ''
 row={'id':rid,'title':' '.join(v for f in fs('245') for v in vals(f,'a')),'shelfmarks':shelves,'date_008_type':fixed[6:7],'date_008_1':fixed[7:11],'date_008_2':fixed[11:15],'publication':[[(s.get('code'),s.text or '') for s in f] for f in fields if f.get('tag') in ['260','264']],'notes':notes,'former_owners':[{'tag':f.get('tag'),'subfields':[(s.get('code'),s.text or '') for s in f]} for f in owners]}
 rows.append(row);summary['bibliographic_records']+=1;summary['distinct_shelfmarks_per_record_sum']+=len(shelves)
 for tag in notes:
  if notes[tag]:summary['records_with_'+tag]+=1
 if owners:summary['records_with_former_owner']+=1
 if any(vals(f,'0') or vals(f,'1') for f in owners):summary['records_with_former_owner_authority']+=1
 if notes['361'] or notes['561'] or owners:summary['records_with_explicit_provenance_field_or_owner']+=1
 if len(shelves)>1:summary['records_with_multiple_Z06_shelfmarks']+=1
 if not shelves:summary['records_without_Z06_852_shelfmark']+=1
 if any(v.lower()=='online' for v in shelves):summary['records_with_online_shelfmark']+=1
 if not(row['date_008_1'].isdigit() and 1501<=int(row['date_008_1'])<=1525):summary['records_date1_outside_or_uncertain']+=1
(OUT/'records-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(OUT/'summary.json').write_text(json.dumps({'query':QUERY,'distinct_records_retrieved':total, 'selection_method':'Union of 25 complete single-year responses; original range query reported 3969' ,'pages':pages,'counts':dict(summary),'limitations':['Counts concern records and shelfmark candidates, not verified physical copies.','563 and 590 are retained as candidates, not automatically counted as provenance.','Private 361/541/561 excluded from derived audit; raw source retained.','Date index selection requires review against literal publication statements.']},ensure_ascii=False,indent=2))
print(json.dumps(dict(summary),indent=2))
