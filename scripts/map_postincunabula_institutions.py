#!/usr/bin/env python3
"""Attach documented institutional localities to explicit owner access points, offline."""
import json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-20261023'
source='Handbuch der historischen Buchbestände in der Schweiz, vol. 3, Zentralbibliothek Zürich'
rules=[
 ('4374885-5','Kloster Rheinau','Rheinau',source+', §1.16–1.20, pp. 368–369','handbook'),
 ('17078-1','Stadtbibliothek Zürich','Zürich',source+', §1.21–1.22, p. 369','handbook'),
 ('4707527-2','Jesuitenkolleg Luzern','Luzern','Explicit locality in the catalogue corporate-owner name Jesuitenkolleg Luzern; authority identifier used for identity matching, not externally fetched','catalogue_name'),
 ('4372432-2','Großmünster','Zürich',source+', §1.2, p. 365','handbook'),
 ('2046336-4','Kantonsbibliothek Zürich','Zürich',source+', §1.87–1.88, p. 380','handbook'),
 ('38444-6','Naturforschende Gesellschaft in Zürich','Zürich',source+', §1.1, p. 365','handbook')]
rulemap={f'(DE-588){g}':{'gnd_id':g,'institution':n,'locality':p,'source':s,'basis':b,'scope':'Institutional locality; not direct evidence of physical residence of every copy; no dates inferred'} for g,n,p,s,b in rules}
(R/'data/authority').mkdir(exist_ok=True)
(R/'data/authority/postincunabula-institution-localities.json').write_text(json.dumps(list(rulemap.values()),ensure_ascii=False,indent=2)+'\n')
rows=json.loads((D/'records-audit.json').read_text());ex={x['id'] for x in json.loads((D/'provenance-assessment.json').read_text())['excluded']};out=[];counts=collections.Counter();amb=set();places=collections.defaultdict(set);covered=set();locsets=collections.defaultdict(set)
for r in rows:
 if r['id'] in ex:continue
 seen=set()
 for i,f in enumerate(r['former_owners'],1):
  ids=[v for c,v in f['subfields'] if c in ['0','1']];hit=next((rulemap[x] for x in ids if x in rulemap),None)
  if not hit:continue
  key=hit['gnd_id']
  out.append({'record_id':r['id'],'shelfmarks':r['shelfmarks'],'source_owner_occurrence':i,'source_field':f['tag'],'source_subfields':f['subfields'],'institution':hit['institution'],'gnd_id':key,'locality':hit['locality'],'locality_source':hit['source'],'locality_basis':hit['basis'],'date':None,'chronological_order':None,'status':'institution_locality_candidate_not_dated_station','copy_scope':'multiple_shelfmarks_unresolved' if len(r['shelfmarks'])>1 else 'single_shelfmark_candidate','notes':'No predecessor chain or ownership dates added. Owner access-point order is not chronological.'})
  if key not in seen:counts[hit['institution']]+=1;seen.add(key)
  covered.add(r['id']);places[hit['locality']].add(r['id']);locsets[r['id']].add(hit['locality'])
  if len(r['shelfmarks'])>1:amb.add(r['id'])
summary={'rules':len(rules),'records_with_institution_locality':len(covered),'records_multiple_shelfmarks':len(amb),'records_single_shelfmark':len(covered-amb),'institution_counts':dict(counts),'place_counts':{p:len(v) for p,v in places.items()},'records_with_multiple_distinct_institution_localities':sum(len(v)>1 for v in locsets.values()),'dated_stations_generated':0}
(D/'institution-locality-candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');(D/'institution-locality-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
assert len(covered)==len(set(x['record_id'] for x in out))
md=['# Institutional locality pilot — Zurich post-incunabula','', '23 October 2026. Offline reuse of explicit former-owner access points. No shelfmark-based provenance inference and no new catalogue requests.','',f"Six rules cover {len(covered)} distinct bibliographic records; {len(amb)} have multiple Z06 shelfmarks and unresolved allocation of notes to copies.",'','| Institution | Locality | Records | Source |','|---|---|---:|---|']
md += [f'| {n} | {p} | {counts[n]} | {s} |' for g,n,p,s,b in rules]
md+=['','## Interpretation','','Counts overlap between institutions. These are locality assignments to named institutional former owners, not dated copy movements. The catalogue supplies the ownership relationship; the handbook or explicit institutional name supplies the locality. No institutional founding date, dissolution date, transfer date or predecessor chain is automatically attached to a copy. A Zurich institution may add a meaningful institutional stage without a new city on the map.','',f"Locality-level record counts: {dict(summary['place_counts'])}. Records mentioning mapped institutions in more than one locality: {summary['records_with_multiple_distinct_institution_localities']}.",'','Other institutions and all individual people remain unresolved in this bounded pilot. Authority IDs are matched exactly; the Luzern locality comes from the catalogue label, not an independently retrieved GND record. Source subfields are retained for scope and uncertainty review. No coordinates or timeline stations are generated.','', '## Reproduce','','Run `python scripts/map_postincunabula_institutions.py` after the earlier collection and assessment steps. The live map is not modified.']
(R/'docs/postincunabula-institution-localities.md').write_text('\n'.join(md)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
