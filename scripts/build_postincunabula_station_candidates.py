#!/usr/bin/env python3
"""Build auditable, unordered provenance-place candidates; no map import."""
import json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-export-20261023'
def main():
 fields=json.loads((D/'provenance-assignments.json').read_text());refs=json.loads((D/'working-copy-context.json').read_text());rules=json.loads((R/'data/authority/postincunabula-institution-localities.json').read_text());lookup={x['gnd_id']:x for x in rules};index={(x['record_id'],x['institution_code'],x['shelfmark']):x for x in refs};stations={};unlocated=[]
 def add(f,owner,place,basis,source,date=None,certainty='inferred',owner_id=None):
  for b,j in f['targets']:
   k=(f['record_id'],b,j);assert k in index
   sk=(*k,owner_id or owner,place,json.dumps(date,sort_keys=True))
   evidence={'tag':f['tag'],'occurrence':f['occurrence'],'subfields':f['subfields'],'copy_assignment':f['assignment']}
   if sk not in stations:stations[sk]={'record_id':k[0],'institution_code':b,'shelfmark':j,'title':index[k]['title'],'owner':owner,'owner_id':owner_id,'place':place,'place_basis':basis,'place_certainty':certainty,'enrichment_source':source,'date':date,'chronology':'not_ordered','evidence':[]}
   stations[sk]['evidence'].append(evidence)
 for f in fields:
  def vals(c):return [v for k,v in f['subfields'] if k==c]
  if not f['targets']:continue
  applied=False
  if f['tag']=='710':
   matches=[lookup[v.removeprefix('(DE-588)')] for v in vals('0') if v.startswith('(DE-588)') and v.removeprefix('(DE-588)') in lookup]
   if len(matches)==1:
    q=matches[0];add(f,q['institution'],q['locality'],q['basis'],q['source'],owner_id=q['gnd_id']);applied=True
  rid=f['record_id'];text=' '.join(vals('a')+vals('z'))
  if rid=='991019857919705501' and f['tag']=='561' and '1839' in text:
   add(f,'Stadtbibliothek Zürich','Zürich','catalogue_note','561 with explicit 4.305 scope',{'year':1839,'meaning':'donation_to_library'},'explicit', '17078-1')
   add(f,'Johann Kaspar von Orelli','Zürich','reviewed_biographical_inference','https://hls-dhs-dss.ch/de/articles/009051/2022-04-04/',{'relation':'immediately_before','year':1839,'meaning':'context_before_donation_not_acquisition_date'});applied=True
  if rid=='991001165399705501' and f['tag']=='500' and '1753' in text:
   add(f,'vermutlich Johann Caspar Hagenbuch','Zürich','reviewed_probable_identity_and_biography','https://hls-dhs-dss.ch/de/articles/043440/2007-11-20/',{'year':1753,'meaning':'ownership_inscription'},'probable');applied=True
  if rid=='991000419389705501' and f['tag']=='590' and 'Gosnay' in text:
   add(f,'Kartäuserinnen Gosnay','Gosnay','catalogue_note','590: Gosnay bei Béthune',certainty='explicit');applied=True
  if rid=='991002418219705501' and f['tag']=='949' and 'Rheinau' in text:
   q=lookup['4374885-5'];add(f,'Kloster Rheinau','Rheinau','reviewed_institution_locality',q['source'],owner_id='4374885-5');applied=True
  if not applied:unlocated.append(f)
 out=list(stations.values());covered={ (x['record_id'],x['institution_code'],x['shelfmark']) for x in out}
 s={'working_references':len(refs),'station_candidates':len(out),'references_with_place_candidates':len(covered),'candidates_without_dates':sum(x['date'] is None for x in out),'places':dict(collections.Counter(x['place'] for x in out)),'linked_fields_without_applied_place_rule':len(unlocated),'limitations':['Candidates are not ordered routes or proof of continuous residence.','Counts can include duplicate owner mentions across dated and undated evidence; do not count as distinct ownership events.','Only six existing institutional rules and four reviewed records are applied; no general person-to-place rules.','Source copy-assignment confidence is preserved separately from place confidence.','Uncertain reproduction references remain included; dates are never inferred from lifespans.']}
 for name,obj in [('station-candidates',out),('station-candidate-summary',s),('station-unlocated-evidence',unlocated)]:
  (D/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 assert not any(x['record_id']=='991001105039705501' for x in out)
 assert not any(x['record_id']=='991002418219705501' and x['shelfmark']=='Res 915' and x['place']=='Rheinau' for x in out)
 print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
