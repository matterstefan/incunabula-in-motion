#!/usr/bin/env python3
"""Conservative offline assignment of provenance fields/candidates to references."""
import argparse,json,re,collections,zipfile,xml.etree.ElementTree as E
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-export-20261023';N={'m':'http://www.loc.gov/MARC21/slim'}
def norm(s):return ' '.join(s.casefold().split())
def has(t,s):return bool(re.search(r'(?<![\w.,])'+re.escape(norm(s))+r'(?![\w.,])',norm(t)))
def key(x):return [x['institution_code'],x['shelfmark']]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('export_zip');a=p.parse_args()
 refs=json.loads((D/'working-copy-context.json').read_text());by=collections.defaultdict(list)
 for x in refs:by[x['record_id']].append(x)
 candidates=json.loads((D/'field-candidates.json').read_text());candidate_index={(x['record_id'],x['tag'],x['occurrence']):x for x in candidates}
 notes={'500','541','563','590','596','949'};results=[]
 with zipfile.ZipFile(a.export_zip) as z:
  for name in sorted(z.namelist()):
   if '/marcxml/metadata_' not in name or not name.endswith('.xml') or name.startswith('__'):continue
   for r in E.fromstring(z.read(name)).findall('.//m:record',N):
    rid=r.find('m:controlfield[@tag="001"]',N).text
    if rid not in by:continue
    fs=r.findall('m:datafield',N)
    def vals(f,c):return [s.text or '' for s in f if s.get('code')==c]
    allholds={(b,j) for f in fs if f.get('tag')=='852' for b in vals(f,'b') for j in vals(f,'j')}
    incomplete=any(not vals(f,'b') or not vals(f,'j') for f in fs if f.get('tag')=='852')
    occ=collections.Counter()
    for f in fs:
     tag=f.get('tag');occ[tag]+=1;c=candidate_index.get((rid,tag,occ[tag]))
     if not c:continue
     lexical=tag in notes and any(t!='stempel' for t in c['matched_terms'])
     if not(c['core_indicator'] or lexical):continue
     scope=' '.join(vals(f,'3')+vals(f,'5'));text=' '.join(vals(f,'a')+vals(f,'z'))
     targets=[];status='open';reason='insufficient_copy_scope'
     matched=[x for x in by[rid] if has(scope,x['shelfmark'])]
     complex_scope=bool(re.search(r'Signaturen|\bund\b|\bbeide\b|nicht|ausser|außer',scope,re.I))
     if tag=='949':
      targets=[key(x) for x in by[rid] if x['institution_code'] in vals(f,'b') and x['shelfmark'] in vals(f,'j')]
      if len(targets)==1:status='explicit';reason='same_949_institution_and_shelfmark'
      else:targets=[]
     elif len(matched)==1 and not complex_scope and len({b for b,j in allholds if norm(j)==norm(matched[0]['shelfmark'])})==1:
      targets=[key(matched[0])];status='explicit';reason='complete_shelfmark_in_same_field_scope'
     elif not scope and len(allholds)==1 and not incomplete and len(by[rid])==1:
      targets=[key(by[rid][0])];status='plausible';reason='only_one_catalogue_reference_in_record'
     elif len(by[rid])==1 and re.fullmatch(r'(?:Exemplar\s+)?(?:ZB Zürich|Zentralbibliothek Zürich|CH-Zu)[., ]*',scope,re.I) and not incomplete:
      targets=[key(by[rid][0])];status='plausible';reason='ZB_scope_and_single_retained_reference'
     if rid=='991001105039705501' and tag!='949':status='open';targets=[];reason='reviewed_Biel_scope_unresolved'
     # These are text tokens, not resolved event dates/places. Owner lifespan dates are excluded.
     dates=re.findall(r'(?<!\d)(?:1[0-9]{3}|20[0-2][0-9])(?!\d)',text) if tag not in ['700','710','711'] else []
     places=sorted(set(re.findall(r'Zürich|Zuerich|Rheinau|Gosnay|Béthune|Luzern|Basel|Bern|Winterthur|Schaffhausen|St\. Gallen',text,re.I)))
     results.append({'record_id':rid,'tag':tag,'occurrence':occ[tag],'subfields':c['subfields'],'evidence_kind':'catalogue_provenance_field_or_owner_role' if c['core_indicator'] else 'lexical_note_candidate','assignment':status,'reason':reason,'targets':targets,'year_tokens_not_events':dates,'place_tokens_not_stations':places,'uncertainty_word_present':bool(re.search(r'unsicher|vermutlich|wahrscheinlich|\?',text,re.I))})
 coverage=[]
 for x in refs:
  rr=[f for f in results if f['record_id']==x['record_id']];linked=[f for f in rr if key(x) in f['targets']]
  status='explicit' if any(f['assignment']=='explicit' for f in linked) else ('plausible' if linked else ('open_only' if any(f['assignment']=='open' for f in rr) else 'no_assigned_candidate'))
  coverage.append({'record_id':x['record_id'],'institution_code':x['institution_code'],'shelfmark':x['shelfmark'],'coverage':status,'linked_field_count':len(linked),'open_fields_in_record':sum(f['assignment']=='open' for f in rr),'linked_fields_with_place_tokens':sum(bool(f['place_tokens_not_stations']) for f in linked),'linked_fields_with_year_tokens':sum(bool(f['year_tokens_not_events']) for f in linked)})
 summary={'references':len(refs),'records':len(by),'source_fields_or_candidates':len(results),'field_assignments':dict(collections.Counter(x['assignment'] for x in results)),'reference_coverage_mutually_exclusive':dict(collections.Counter(x['coverage'] for x in coverage)),'references_with_linked_place_tokens':sum(x['linked_fields_with_place_tokens']>0 for x in coverage),'references_with_linked_year_tokens':sum(x['linked_fields_with_year_tokens']>0 for x in coverage),'warning':'Explicit refers only to catalogue copy linkage, not certainty of ownership, physical identity or map readiness. Lexical notes remain candidates. Places use a small declared vocabulary; dates may be citations or other events. Reviewed biographical inferences remain separate in review-decisions.json.'}
 for name,obj in [('provenance-assignments',results),('provenance-coverage',coverage),('provenance-assignment-summary',summary)]:
  (D/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
