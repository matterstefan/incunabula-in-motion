#!/usr/bin/env python3
"""Attach source 949 context without splitting, merging or counting physical items."""
import argparse,collections,json,zipfile,xml.etree.ElementTree as E
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-export-20261023';N={'m':'http://www.loc.gov/MARC21/slim'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('export_zip');a=p.parse_args()
 refs=json.loads((D/'working-copy-references.json').read_text());index=collections.defaultdict(list)
 for x in refs:index[x['record_id']].append(x)
 unmatched=[]
 with zipfile.ZipFile(a.export_zip) as z:
  for name in sorted(z.namelist()):
   if '/marcxml/metadata_' not in name or not name.endswith('.xml') or name.startswith('__'):continue
   for r in E.fromstring(z.read(name)).findall('.//m:record',N):
    rid=r.find('m:controlfield[@tag="001"]',N).text
    if rid not in index:continue
    fs=r.findall('m:datafield',N)
    def vals(f,c):return [s.text or '' for s in f if s.get('code')==c]
    context=[{'tag':f.get('tag'),'subfields':[(s.get('code'),s.text or '') for s in f]} for f in fs if f.get('tag') in ['019','300']]
    for x in index[rid]:x['record_description']=context;x['item_context_949']=[]
    for i,f in enumerate([f for f in fs if f.get('tag')=='949'],1):
     entry={'occurrence':i,'subfields':[(s.get('code'),s.text or '') for s in f],'additional_shelfmarks_h':vals(f,'h'),'part_labels_q':vals(f,'q'),'notes_z':vals(f,'z'),'association':'exact_same_record_institution_b_and_shelfmark_j'}
     targets=[x for x in index[rid] if x['institution_code'] in vals(f,'b') and x['shelfmark'] in vals(f,'j')]
     for x in targets:x['item_context_949'].append(entry)
     if not targets:unmatched.append({'record_id':rid,**entry})
 for x in refs:x.setdefault('item_context_949',[])
 s={'retained_references':len(refs),'references_with_949_context':sum(bool(x['item_context_949']) for x in refs),'references_with_multiple_949_fields':sum(len(x['item_context_949'])>1 for x in refs),'references_with_part_labels':sum(any(f['part_labels_q'] for f in x['item_context_949']) for x in refs),'references_with_949_notes':sum(any(f['notes_z'] for f in x['item_context_949']) for x in refs),'unmatched_949_occurrences':len(unmatched),'limitations':['949 occurrences are not counted as physical copies.','Matching is exact; unmatched fields can include excluded references, other institutions or differing shelfmark notation.','Notes are associated only with their own matched reference; no propagation to other MARC fields or owner entries.']}
 assert len(refs)==len({(x['record_id'],x['institution_code'],x['shelfmark']) for x in refs})
 for name,obj in [('working-copy-context',refs),('item-context-summary',s),('unmatched-item-context',unmatched)]:
  (D/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
