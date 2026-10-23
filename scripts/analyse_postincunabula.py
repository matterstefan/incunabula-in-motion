"""Offline exploratory audit; record-level metrics, not copy-level provenance claims."""
import json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/research/zurich-postincunabula-20261023'
rows=json.loads((D/'records-audit.json').read_text());excluded=[];kept=[];review=[]
for r in rows:
 y=r['date_008_1'];pub=' '.join(v for f in r['publication'] for c,v in f if c=='c')
 reason=None
 if r['id']=='ZBC6ec2ab88e03945c1a32625dd44038f79':reason='Collection-level description, not an individual edition'
 elif r['date_008_type']=='r' and y.isdigit() and int(y)>1600:reason='Later reproduction; historical original date caused search hit'
 elif r['id']=='991097182939705501':reason='Publication statement 1543; outside 1501–1525'
 if reason:excluded.append({'id':r['id'],'title':r['title'],'publication_date':pub,'reason':reason});continue
 kept.append(r)
 if not(y.isdigit() and 1501<=int(y)<=1525):review.append({'id':r['id'],'title':r['title'],'publication_date':pub,'status':'retained_boundary_or_corrected_date'})
c=collections.Counter();owners={};hist=collections.Counter()
for r in kept:
 n=r['notes'];o=r['former_owners'];c['records']+=1
 for tag in ['361','541','561','563','590']:
  if n.get(tag):c['with_'+tag]+=1
 if o:c['with_former_owners']+=1
 if o or n.get('561') or n.get('361'):c['with_explicit_provenance_or_owner']+=1
 if n.get('561') and o:c['with_561_and_owner']+=1
 if o and not n.get('561') and not n.get('361'):c['owner_without_561_361']+=1
 authority=False;seen=set()
 for f in o:
  sub=f['subfields'];ids=[v for code,v in sub if code in ['0','1']];names=[v for code,v in sub if code=='a'];name='; '.join(names);key=ids[0] if ids else f['tag']+':'+name
  if ids:authority=True
  if key in seen:continue
  seen.add(key);x=owners.setdefault(key,{'name':name,'authority_ids':ids,'record_count':0});x['record_count']+=1
 if authority:c['with_owner_authority']+=1
 hist[len(seen)]+=1
 shelves=r['shelfmarks'];c['shelfmark_occurrences']+=len(shelves)
 if len(shelves)>1:c['multiple_shelfmarks']+=1
out={'counts':dict(c),'excluded':excluded,'retained_date_review':review,'former_owner_count_per_record':dict(sorted(hist.items())),'owners_by_frequency':sorted(owners.values(),key=lambda x:-x['record_count']),'scope':'Z06; record-level; dates based on catalogue, no item-level provenance allocation yet'}
(D/'provenance-assessment.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
lines=['# Zurich post-incunabula: first provenance assessment','', 'Source: public swisscollections SRU snapshot, 23 October 2026. Scope: Z06 (ZB Alte Drucke und Rara), year queries 1501–1525. This is an exploratory record-level audit; no new network requests.','',f"Retrieved {len(rows)} distinct records. Excluded {len(excluded)} clear out-of-scope records; retained {len(kept)} candidates, including {len(review)} explicitly flagged boundary/corrected-date cases.",'','## Record-level indicators','','| Indicator | Records | Share |','|---|---:|---:|']
for k in ['with_explicit_provenance_or_owner','with_561','with_former_owners','with_owner_authority','with_561_and_owner','owner_without_561_361','with_361','with_563','with_590','multiple_shelfmarks']:
 lines.append(f'| {k} | {c[k]} | {c[k]/len(kept):.1%} |')
lines+=['','## Interpretation','','The indicators overlap. 563 and 590 describe bindings and copy notes and must not automatically be counted as provenance. Former-owner access points provide identities, not necessarily places, dates or a chronological sequence. An absence of 561/361/fmo is not proof of absent provenance: other notes may contain evidence. Authority identifiers do not establish where a copy was owned. Multiple shelfmarks and field scope must be resolved before making copy-level claims. Counts are limited to exposed records from Z06 and are not a census of all ZB collections.','', 'The 26 initial date warnings were inspected against publication statements. Later reproductions and the collection-level description were excluded. Corrected dates and ranges overlapping 1501–1525 remain explicit candidates rather than being silently discarded. The additional 23 hits from the broad range query are retained separately in range-only.xml and are not added to this year-query cohort.','', '## Most frequent former-owner access points','','| Name | Records | Authority |','|---|---:|---|']
for o in out['owners_by_frequency'][:20]:lines.append(f"| {o['name']} | {o['record_count']} | {'; '.join(o['authority_ids'])} |")
lines+=['','## Date exclusions','','| Record | Date statement | Reason |','|---|---|---|']
for r in excluded:lines.append(f"| {r['id']} | {r['publication_date']} | {r['reason']} |")
lines+=['','## Retained date-review cases','','| Record | Date statement |','|---|---|']
for r in review:lines.append(f"| {r['id']} | {r['publication_date']} |")
lines+=['','## Next step','','Extract source-linked owner, place and date statements for the candidates with provenance. Measure explicitly dated and geolocatable events separately from identities. Apply documented institutional enrichment only as a distinct derivation. Do not invent chronology from field order or use personal life dates as ownership dates. No live-map changes were made.']
(ROOT/'docs/postincunabula-provenance-assessment.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2)[:7000])
