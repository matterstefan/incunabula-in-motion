#!/usr/bin/env python3
"""Offline field-level copy-scope audit; explicit matches do not prove physical item identity."""
from pathlib import Path
import json,re,collections,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-20261023';N={'m':'http://www.loc.gov/MARC21/slim'}
ex={x['id'] for x in json.loads((D/'provenance-assessment.json').read_text())['excluded']};seen=set();out=[];codes=collections.Counter();records=collections.defaultdict(set)
def norm(s):return ' '.join(s.casefold().split())
def has(text,shelf):
 # Never let 4.330 match 4.330,2 or a short call number match a longer suffix.
 return bool(re.search(r'(?<![\w.,])'+re.escape(norm(shelf))+r'(?![\w.,])',norm(text)))
for p in sorted(D.glob('year*.xml')):
 for r in E.parse(p).findall('.//m:record',N):
  rid=r.find('m:controlfield[@tag="001"]',N).text
  if rid in seen or rid in ex:continue
  seen.add(rid);fs=r.findall('m:datafield',N)
  def vals(f,k):return [s.text or '' for s in f if s.get('code')==k]
  holds=[{'institution':vals(f,'b'),'shelfmarks':vals(f,'j')} for f in fs if f.get('tag')=='852']
  zb=sorted(set(s for h in holds if 'Z06' in h['institution'] for s in h['shelfmarks']));other=any('Z06' not in h['institution'] for h in holds)
  occurrence=collections.Counter()
  for f in fs:
   tag=f.get('tag');occurrence[tag]+=1
   if not(tag in ['361','561'] or (tag in ['700','710','711'] and ('fmo' in vals(f,'4') or any('eigentümer' in v.lower() or 'former owner' in v.lower() for v in vals(f,'e'))))):continue
   if tag in ['361','561'] and f.get('ind1')=='0':continue
   sf=[(s.get('code'),s.text or '') for s in f];scope=' '.join(vals(f,'3')+vals(f,'5'));note=' '.join(vals(f,'a')+vals(f,'z')) if tag in ['361','561'] else ''
   match=[s for s in zb if has(scope,s)];textmatch=[s for s in zb if has(note,s)]
   related=bool(re.search(r'vorgebunden|nachgebunden|ersten Druck|ander\w* Druck|Sammelband',note,re.I))
   zb_scope=bool(re.search(r'ZB\s*(?:Zürich)?|Zentralbibliothek\s+Zürich|CH-Zu',scope,re.I))
   explicit_other=bool(scope) and not zb_scope and not match
   if match and re.search(r'Signaturen|\bund\b|\bbeide\b',scope,re.I):status='complex_scope_expression';target=match
   elif len(match)==1:status='explicit_shelfmark_in_scope';target=match
   elif len(match)>1:status='multiple_shelfmarks_in_scope';target=match
   elif related:status='bound_volume_or_related_print_scope';target=[]
   elif textmatch:status='shelfmark_in_narrative_needs_context';target=textmatch
   elif len(zb)==1 and (not other or zb_scope) and not explicit_other:status='plausible_single_ZB_shelfmark';target=zb
   elif len(zb)>1:status='unresolved_multiple_ZB_shelfmarks';target=[]
   else:status='unresolved_institution_or_scope';target=[]
   codes[status]+=1;records[status].add(rid)
   out.append({'record_id':rid,'field':tag,'field_occurrence':occurrence[tag],'subfields':sf,'ZB_shelfmarks':zb,'other_institution_holdings_present':other,'status':status,'candidate_targets':target,'related_print_or_volume_mentioned':related})
summary={'records_checked':len(seen),'records_with_audited_fields':len(set(x['record_id'] for x in out)),'field_counts':dict(codes),'record_counts_overlapping':{k:len(v) for k,v in records.items()},'records_all_audited_fields_explicit':sum(all(x['status']=='explicit_shelfmark_in_scope' for x in out if x['record_id']==rid) for rid in set(x['record_id'] for x in out))}
(D/'copy-scope-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');(D/'copy-scope-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
md=['# Copy-scope audit of Zurich post-incunabula','', 'Offline audit, 23 October 2026. Bibliographic records with exposed holdings, not a census of physical items. Core scope: public 561/361 and former-owner 700/710/711. Binding and general copy notes are not exhaustively classified in this step.','', '| Classification | Field occurrences | Records (overlapping) |','|---|---:|---:|']
for k,v in codes.items():md.append(f'| {k} | {v} | {len(records[k])} |')
md+=['','## Interpretation','','Explicit means exactly one complete Z06 shelfmark string is found in subfield 3 or 5 of the same source field. It establishes a catalogue reference to that shelfmark, not a verified physical item ID. No scope is propagated to neighbouring fields or other owners. Single-shelfmark attribution remains an assumption; holdings from other libraries block it unless an explicit ZB institution scope is present. Narrative references and composite-volume mentions remain unresolved. Multiple statuses can occur in one record.','', 'Matching is case/whitespace-normalised but otherwise conservative: variants and differing punctuation may be missed. Numeric prefixes must not match longer shelfmarks. Other institutional labels and complex qualifiers need further rules; no automatic map import follows.','', '## Examples of explicit scope','','| Record | Field | Scope | Matched shelfmark |','|---|---|---|---|']
for x in [x for x in out if x['status']=='explicit_shelfmark_in_scope'][:10]:md.append(f"| {x['record_id']} | {x['field']} | {'; '.join(v for k,v in x['subfields'] if k in ['3','5'])} | {'; '.join(x['candidate_targets'])} |")
(R/'docs/postincunabula-copy-scope.md').write_text('\n'.join(md)+'\n');print(json.dumps(summary,indent=2))
