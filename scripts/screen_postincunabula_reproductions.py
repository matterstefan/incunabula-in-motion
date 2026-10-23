#!/usr/bin/env python3
"""Offline conservative reproduction screen. Original exports remain unchanged."""
import argparse,json,re,zipfile,collections
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];N={'m':'http://www.loc.gov/MARC21/slim'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('export_zip');a=p.parse_args();d=ROOT/'data/research/zurich-postincunabula-export-20261023'
 refs=json.loads((d/'copy-references.json').read_text());by=collections.defaultdict(list)
 for x in refs:by[x['record_id']].append(x)
 retained=[];excluded=[];review=[];digital=0
 with zipfile.ZipFile(a.export_zip) as z:
  for name in z.namelist():
   if '/marcxml/metadata_' not in name or not name.endswith('.xml') or name.startswith('__'):continue
   for r in E.fromstring(z.read(name)).findall('.//m:record',N):
    rid=r.find('m:controlfield[@tag="001"]',N).text
    def cf(tag):return [f.text or '' for f in r.findall(f'm:controlfield[@tag="{tag}"]',N)]
    fs=r.findall('m:datafield',N)
    def sub(f,c):return [s.text or '' for s in f if s.get('code')==c]
    v=(cf('008') or [''])[0];carriers=[x for f in fs if f.get('tag')=='338' for x in sub(f,'b')];physical=any(x in ['nc','nb'] for x in carriers)
    micro=any(x.startswith('h') for x in cf('007')) or v[23:24] in ['a','b','c'] or any(x.startswith('h') for x in carriers)
    later=v[6:7]=='r' and v[7:11].isdigit() and int(v[7:11])>1525
    digi=any(x.startswith('c') for x in cf('007')) or 'cr' in carriers
    notes=[{'tag':f.get('tag'),'subfields':[(s.get('code'),s.text or '') for s in f]} for f in fs if f.get('tag') in ['533','534']]
    for ref in by[rid]:
     reasons=[];warnings=[]
     if later:reasons.append({'rule':'008_reproduction_after_1525','evidence':v})
     elif micro:
      if re.match(r'^MF[A-Z]?\b',ref['shelfmark']) or not physical:reasons.append({'rule':'microform_encoding','evidence':{'007':cf('007'),'008':v,'338b':carriers}})
      else:warnings.append('Mixed physical/microform description: no automatic exclusion')
     if not reasons and notes:warnings.append('Reproduction/original-version note requires context')
     if not reasons and digi and not physical:warnings.append('Electronic encoding without explicit physical carrier: retain pending review')
     x={**ref,'reproduction_screen':{'status':'excluded_reproduction' if reasons else ('retained_for_review' if warnings else 'retained'),'reasons':reasons,'review_notes':warnings,'source_notes':notes}}
     (excluded if reasons else retained).append(x)
     if warnings and not reasons:review.append(x)
     if digi and not reasons:digital+=1
 assert len(retained)+len(excluded)==len(refs)
 s={'input_references':len(refs),'excluded_references':len(excluded),'excluded_records':len({x['record_id'] for x in excluded}),'retained_references':len(retained),'retained_records':len({x['record_id'] for x in retained}),'review_references':len(review),'retained_references_with_electronic_encoding':digital,'excluded_by_rule':dict(collections.Counter(r['rule'] for x in excluded for r in x['reproduction_screen']['reasons'])),'note':'Retained references are working candidates, not a verified census. Missing ZB references remain in the baseline records.json; no date/hierarchy exclusions in this step.'}
 for name,obj in [('working-copy-references',retained),('excluded-reproductions',excluded),('reproduction-review',review),('reproduction-summary',s)]:
  (d/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
