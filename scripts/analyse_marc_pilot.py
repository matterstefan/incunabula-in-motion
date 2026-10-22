"""Offline comparison of a bounded, non-representative Zurich MARC sample.

No provenance events or map routes are generated. Holdings are not item IDs.
"""
import json,re,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/research/marc-pilot-20261022'
NS={'m':'http://www.loc.gov/MARC21/slim'}
def records(name):return ET.parse(BASE/name).findall('.//m:record',NS)
def fields(r,tag):
 return [{'tag':tag,'ind1':f.get('ind1'),'ind2':f.get('ind2'),'subfields':[{'code':s.get('code'),'value':s.text or ''} for s in f]} for f in r.findall('m:datafield[@tag="'+tag+'"]',NS)]
def values(f,code):return [s['value'] for s in f['subfields'] if s['code']==code]
def first(f,code):return next(iter(values(f,code)),'')
def rid(r):return r.findtext('m:controlfield[@tag="001"]',namespaces=NS)
def owners(r):return [f for t in ['700','710','711'] for f in fields(r,t) if 'fmo' in values(f,'4')]
def main():
 alma={rid(r):r for r in records('alma-comparison.xml')};sc={}
 for name in ['sc-inc-1.xml','sc-inc-sample.xml','sc-sixteenth-zb.xml']:
  for r in records(name):
   for f in fields(r,'986'):
    for v in values(f,'a'):
     if v.startswith('(41SLSP_UZB)'):sc[v.split(')')[1]]=r
 mei=json.loads((ROOT/'data/retrieved/zurich-full.json').read_text())['records']
 target={'990047941940205508':'02129563','990047733730205508':'02129360','990045665310205508':'02129912','990047317990205508':'00570263','990048649500205508':'02129976','990037626940205508':'02129744'}
 focused16={'990070507980205508','990036481340205508','990053546370205508','990060026240205508','990043572860205508','990037763520205508'}
 cases=[]
 for id,r in sorted(alma.items()):
  sr=sc[id];h=[]
  for f in fields(r,'AVA'):
   if first(f,'b')=='Z06':h.append({'holding_id':first(f,'8'),'shelfmark':first(f,'d'),'total_items':first(f,'f'),'location_code':first(f,'j')})
  # Presence of a record must not be mistaken for an individual copy.
  scope='manual_copy_assignment_required' if len(h)!=1 else 'single_holding_in_response_item_identity_unverified'
  if any(v['shelfmark']=='Online' for v in h):scope='online_placeholder_not_physical_copy'
  item={'alma_mms_id':id,'swisscollections_id':rid(sr),'title':first(fields(r,'245')[0],'a'),'publication':fields(r,'264')+fields(r,'260'),'holdings':h,'copy_scope_status':scope,'mei_id_checked':target.get(id),'focus_group':'incunabula_mei_comparison' if id in target else 'sixteenth_century' if id in focused16 else 'additional_search_result','fields':{t:fields(r,t) for t in ['361','541','561','562','563','510']},'former_owners':owners(r),'swisscollections_inventory':fields(sr,'852')+fields(sr,'949'),'comparison':{t:fields(r,t)==fields(sr,t) for t in ['361','561','563']}}
  if id in target:
   m=next(x for x in mei if x['id']==target[id]);assert any(x['shelfmark'].strip()==m['shelfmark'].strip() for x in h)
   item['mei_title']=m.get('hostItem',{}).get('title');item['mei_provenance_blocks']=len(m.get('provenance',[]))
  cases.append(item)
 summary={'retrieved_on':'2026-10-22','selection':'Convenience sample: known Zurich MEI shelfmarks and first ten Z06 hits dated 1531; related shelfmarks also returned. Not representative.','compared_bibliographic_records':len(cases),'focused_mei_comparisons':len(target),'focused_sixteenth_century_records':len(focused16),'records_with_fields':{t:sum(bool(c['fields'][t]) for c in cases) for t in ['361','561','563']},'records_with_former_owner_access_points':sum(bool(c['former_owners']) for c in cases),'copy_scope_status':dict(Counter(c['copy_scope_status'] for c in cases)),'same_361_561_563_in_both_responses':all(all(c['comparison'].values()) for c in cases),'cases':cases}
 (BASE/'comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k!='cases'},indent=2))
if __name__=='__main__':main()
