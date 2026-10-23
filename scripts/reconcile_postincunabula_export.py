#!/usr/bin/env python3
"""Offline census of catalogue copy references, not verified physical items."""
import argparse, collections, json, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as E
N={'m':'http://www.loc.gov/MARC21/slim'}
ROOT=Path(__file__).resolve().parents[1]
ZB={'Z01','Z02','Z03','Z04','Z05','Z06'}
def vals(f,c): return [s.text or '' for s in f if s.get('code')==c]
def match(text,shelf):
 return bool(re.search(r'(?<![\w.,])'+re.escape(' '.join(shelf.casefold().split()))+r'(?![\w.,])',' '.join(text.casefold().split())))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('export_zip',type=Path);p.add_argument('--output',type=Path,default=ROOT/'data/research/zurich-postincunabula-export-20261023');a=p.parse_args()
 records={}
 with zipfile.ZipFile(a.export_zip) as z:
  for name in sorted(z.namelist()):
   if '/marcxml/metadata_' not in name or not name.endswith('.xml') or name.startswith('__MACOSX/'):continue
   for r in E.fromstring(z.read(name)).findall('.//m:record',N):
    rid=r.find('m:controlfield[@tag="001"]',N).text
    if rid in records:raise ValueError('Duplicate exported record '+rid)
    records[rid]=r
 out=[];fields=[];unresolved=[];record_index=[];stats=collections.Counter();libs=collections.Counter()
 for rid,r in records.items():
  fs=r.findall('m:datafield',N)
  def allv(tag,code):return [v for f in fs if f.get('tag')==tag for v in vals(f,code)]
  d008=r.find('m:controlfield[@tag="008"]',N);d008=d008.text if d008 is not None else ''
  d007=[f.text or '' for f in r.findall('m:controlfield[@tag="007"]',N)]
  reasons=[]
  if any(v.startswith('h') for v in d007) or d008[23:24] in ['a','b','c']:reasons.append('microform_encoding')
  if d008[6:7]=='r' and d008[7:11].isdigit() and int(d008[7:11])>1525:reasons.append('later_reproduction_date')
  holdings=[]
  for f in fs:
   if f.get('tag')!='852':continue
   bs=vals(f,'b'); js=vals(f,'j')
   if not set(bs)&ZB:continue
   if not js:unresolved.append({'record_id':rid,'reason':'ZB_852_without_j','subfields':[(s.get('code'),s.text) for s in f]})
   for b in bs:
    if b not in ZB:continue
    for j in js:
     key=(b,j)
     if key not in holdings:holdings.append(key)
  other=any(not set(vals(f,'b'))&ZB for f in fs if f.get('tag')=='852')
  localfields=[]
  for f in fs:
   tag=f.get('tag');sf=[(s.get('code'),s.text or '') for s in f]
   owner=tag in ['700','710','711'] and ('fmo' in vals(f,'4') or any(re.search(r'vorbesitzer|former owner|eigentümer',v,re.I) for v in vals(f,'e')))
   if not(tag in ['561','361'] or owner):continue
   if tag in ['561','361'] and f.get('ind1')=='0':continue
   scope=' '.join(vals(f,'3')+vals(f,'5'));targets=[list(h) for h in holdings if match(scope,h[1])]
   if len(targets)==1 and not re.search(r'Signaturen|\bund\b|\bbeide\b',scope,re.I):status='explicit_shelfmark_scope'
   elif targets:status='complex_or_multiple_scope'
   elif not scope and len(holdings)==1 and not other:status='single_reference_assumption';targets=[list(holdings[0])]
   else:status='unresolved_scope'
   x={'record_id':rid,'tag':tag,'subfields':sf,'status':status,'candidate_targets':targets};fields.append(x);localfields.append(x)
  record_index.append({'record_id':rid,'title':allv('245','a'),'ZB_reference_count':len(holdings),'review_flags':reasons,'core_provenance_field_count':len(localfields)})
  stats['records_with_core_provenance']+=bool(localfields)
  stats['records_without_ZB_852_j']+=not bool(holdings)
  stats['records_with_multiple_ZB_references']+=len(holdings)>1
  stats['records_flagged_reproduction']+=bool(reasons)
  for b,j in holdings:
   libs[b]+=1
   evidence=[x for x in localfields if [b,j] in x['candidate_targets']]
   out.append({'record_id':rid,'institution_code':b,'shelfmark':j,'title':allv('245','a'),'publication':[{ 'tag':f.get('tag'),'subfields':[(s.get('code'),s.text or '') for s in f]} for f in fs if f.get('tag') in ['260','264']], 'review_flags':reasons,'core_provenance_fields_in_record':len(localfields),'explicit_provenance_fields':sum(x['status']=='explicit_shelfmark_scope' for x in evidence),'assumed_provenance_fields':sum(x['status']=='single_reference_assumption' for x in evidence),'record_has_unresolved_provenance':any(x['status'] in ['unresolved_scope','complex_or_multiple_scope'] for x in localfields)})
 a.output.mkdir(parents=True,exist_ok=True)
 summary={'export_records':len(records),'catalogue_copy_references':len(out),'distinct_institution_shelfmark_pairs':len({(x['institution_code'],x['shelfmark']) for x in out}),'reference_counts_by_institution':dict(libs),**dict(stats),'references_flagged_reproduction':sum(bool(x['review_flags']) for x in out),'references_without_core_provenance_in_record':sum(x['core_provenance_fields_in_record']==0 for x in out),'field_scope_counts':dict(collections.Counter(x['status'] for x in fields)),'limitations':['A reference is record ID + institution + shelfmark, not a verified physical item. Shared shelfmarks across titles are not merged: they may identify bound-with prints.','All records retained; reproduction flags require review and are not deletions. Dates and hierarchy require further assessment.','Z01–Z06 included; UMWI not counted as ZB. Missing 852$j retained separately.','Core provenance indicator is not an exhaustive search of free-text notes. Single-reference attribution is an assumption; explicit scope matching is conservative.']}
 for name,obj in [('records',record_index),('copy-references',out),('provenance-fields',fields),('unresolved-holdings',unresolved),('summary',summary)]:
  (a.output/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
