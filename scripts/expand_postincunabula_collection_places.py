#!/usr/bin/env python3
"""Narrow documented collection rules; retain source and no invented dates."""
import json,re,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-export-20261023'
def main():
 refs=json.loads((D/'working-copy-context.json').read_text());fields=json.loads((D/'provenance-assignments.json').read_text());old=json.loads((D/'station-candidates.json').read_text());idx={(x['record_id'],x['institution_code'],x['shelfmark']):x for x in refs};out={};frequent=collections.defaultdict(list)
 def add(key,owner,place,rule,source,evidence,assignment):
  k=(*key,owner,place)
  if k not in out:out[k]={'record_id':key[0],'institution_code':key[1],'shelfmark':key[2],'title':idx[key]['title'],'owner':owner,'place':place,'date':None,'chronology':'not_ordered','rule':rule,'source':source,'place_basis':'documented_collection_or_institution_inference','evidence':[]}
  out[k]['evidence'].append({'copy_assignment':assignment,'source':evidence})
 for key,x in idx.items():
  if re.match(r'^Gal\s+Tz\s+\d',x['shelfmark']):
   add(key,'Johann Jakob Simler','Zürich','handbook_Gal_Tz','Handbuch, Band 3, ZB, p. 375, shelfmark table; HLS Simmler https://hls-dhs-dss.ch/de/articles/010846/2011-03-31/',{'shelfmark':x['shelfmark'],'meaning':'Private library collection membership, not an acquisition date'},'shelfmark_collection_rule')
 for f in fields:
  if f['tag'] not in ['500','561','563','590','596','949']:continue
  text=' '.join(v for k,v in f['subfields'] if k in ['a','z'])
  frequent[text].append({'record_id':f['record_id'],'tag':f['tag'],'occurrence':f['occurrence'],'assignment':f['assignment']})
  if not f['targets'] or re.search(r'unsicher|vermutlich|wahrscheinlich|nicht aus|kein.{0,10}besitz',text,re.I):continue
  selections=[]
  if re.match(r'^Aus dem Vorbesitz des Klosters Rheinau\b',text):selections.append(('Kloster Rheinau','Rheinau','explicit_Rheinau_opening','Handbuch, ZB, §§1.16–1.20'))
  if re.search(r'(?:Supralibros|Exlibris|Vorbesitz) der Naturforschenden Gesellschaft in Zürich\b',text,re.I):selections.append(('Naturforschende Gesellschaft in Zürich','Zürich','NGZH_named_ownership_mark','Institution and city explicit in catalogue note'))
  for b,j in f['targets']:
   key=(f['record_id'],b,j);assert key in idx
   for owner,place,rule,source in selections:add(key,owner,place,rule,source,{'tag':f['tag'],'occurrence':f['occurrence'],'subfields':f['subfields']},f['assignment'])
 result=list(out.values());oldrefs={(x['record_id'],x['institution_code'],x['shelfmark']) for x in old};newrefs={(x['record_id'],x['institution_code'],x['shelfmark']) for x in result}
 grouped=[{'text':t,'field_occurrences':len(v),'records':len({x['record_id'] for x in v}),'sources':v} for t,v in frequent.items()];grouped.sort(key=lambda x:-x['records'])
 summary={'supplement_candidates':len(result),'references_in_supplement':len(newrefs),'previously_covered_references':len(oldrefs),'additional_references':len(newrefs-oldrefs),'combined_distinct_references':len(oldrefs|newrefs),'candidates_by_rule':dict(collections.Counter(x['rule'] for x in result)),'limits':['All added candidates undated. No chronology or automatic map update.','Supplement may repeat evidence already supporting a place; do not add candidate counts as movements.','Only Gal Tz shelfmarks and two narrowly defined positive note patterns used. General person names and Ms S signatures are not assigned places.','Underlying reproduction-review cases remain included.']}
 for name,obj in [('collection-place-supplement',result),('collection-place-summary',summary),('recurring-provenance-notes',grouped)]:
  (D/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
