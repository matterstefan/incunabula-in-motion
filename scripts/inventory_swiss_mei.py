"""Inventory MEI copies by current Swiss holding institution, not provenance."""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
from mei_client import fetch_complete_query, request_page, hits_value, RateLimiter, atomic_write_json, now_iso
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/retrieved/swiss-inventory'
QUERY='data.holdingInstitution.country:CH'

def inventory(records):
    groups=defaultdict(list)
    ids=set()
    for r in records:
        identifier=r.get('id')
        if not identifier or identifier in ids:raise ValueError('Missing or duplicate MEI copy ID')
        ids.add(identifier)
        holding=r.get('holdingInstitution') or {}
        if holding.get('country')!='CH':raise ValueError('Result does not have current holding country CH; query needs review')
        institution=r.get('holdingInstitutionId')
        if not institution:raise ValueError('Swiss holding lacks institution ID; manual review needed')
        groups[institution].append(r)
    rows=[]
    for key,rs in sorted(groups.items()):
        names=sorted({r.get('holdingInstitution',{}).get('name','') for r in rs}- {''})
        rows.append(dict(institution_id=key,institution_names=' | '.join(names),mei_copies=len(rs),
          distinct_istc_editions=len({r['hostItemId'] for r in rs if r.get('hostItemId')}),
          copies_with_provenance_blocks=sum(bool(r.get('provenance')) for r in rs),
          provenance_blocks=sum(len(r.get('provenance') or []) for r in rs),
          example_mei_id=rs[0]['id'],example_mei_url='https://data.cerl.org/mei/'+rs[0]['id']))
    return sorted(rows,key=lambda r:(-r['mei_copies'],r['institution_id']))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,help='Offline check of an existing snapshot (no CERL request)')
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    if args.input:
        data=json.loads(args.input.read_text());records=data.get('records',data.get('rows',[]))
        complete=False;query=data.get('query','offline sample');stamp=data.get('retrieved_at','unknown')
    else:
        limiter=RateLimiter(2)
        # Fail early if the index does not recognise the holding-country field.
        sample=request_page(QUERY,0,5,limiter)
        if not hits_value(sample):raise ValueError('Country query returned zero hits; no empty inventory will be published')
        inventory(sample.get('rows',[]))
        data=fetch_complete_query(QUERY,limiter)
        records=data['rows'];complete=True;query=QUERY;stamp=data['retrieved_at']
    rows=inventory(records)
    args.output.mkdir(parents=True,exist_ok=True)
    atomic_write_json(args.output/'swiss-mei-snapshot.json',{'query':query,'retrieved_at':stamp,'complete':complete,'records':records})
    atomic_write_json(args.output/'inventory.json',{'query':query,'retrieved_at':stamp,'complete':complete,
        'scope':'Current institution country CH; not Swiss provenance. Missing or incorrect country codes may cause omissions.',
        'copies':len(records),'institutions':len(rows),'holdings':rows})
    if rows:
        with (args.output/'swiss-institutions.csv').open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({'complete':complete,'copies':len(records),'institutions':len(rows)},indent=2))
if __name__=='__main__':main()
