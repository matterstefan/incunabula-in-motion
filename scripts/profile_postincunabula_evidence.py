#!/usr/bin/env python3
"""Offline evidence profiling. Text matches are review candidates, never inferred events."""
from pathlib import Path
import json,re,collections,unicodedata
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-20261023'
rows=json.loads((D/'records-audit.json').read_text());assessment=json.loads((D/'provenance-assessment.json').read_text());exclude={x['id'] for x in assessment['excluded']};rows=[x for x in rows if x['id'] not in exclude]
# Deliberately limited lexical pilot: explicit literal mentions, including institution names.
# No person-to-city inference, no coordinates, no attribution to a particular owner.
places=['Zürich','Zuerich','Rheinau','Wettingen','Luzern','Basel','Bern','Wien','Paris','Venedig','Strassburg','Straßburg','Augsburg','Nürnberg','Nuremberg','Genf','Geneve','Genève','Winterthur','Schaffhausen','St. Gallen','St.Gallen','Konstanz','Rom','Mailand','Lyon','Lugduni','Turicensi','Turicensis','Tiguri','Rhenoviensis']
place_re=re.compile(r'(?<!\w)(?:'+ '|'.join(re.escape(x) for x in sorted(places,key=len,reverse=True))+r')(?!\w)',re.I)
year_re=re.compile(r'(?<!\w)(?:1[0-9]{3}|20[0-2][0-9])(?!\w)')
century_re=re.compile(r'\b\d{1,2}\.\s*(?:Jh\.?|Jahrhundert)',re.I)
prov_re=re.compile(r'vorbesitz|besitzvermerk|besitzereintrag|verbalexlibris|exlibris|ex libris|provenienz|schenkung|schenkungsvermerk|bibliothec|aus dem besitz',re.I)
norm=lambda x:' '.join(unicodedata.normalize('NFKC',x).casefold().split()).rstrip(' .;')
owners={};notes={};candidates=[];stats=collections.Counter();institutions=collections.Counter()
for r in rows:
 rid=r['id'];seen=set();flags=set()
 for f in r['former_owners']:
  sub=f['subfields'];ids=[v for k,v in sub if k in ['0','1']];names=[v for k,v in sub if k=='a'];name='; '.join(names);key=ids[0] if ids else f['tag']+':'+norm(name)
  o=owners.setdefault(key,{'names':set(),'authority_ids':set(),'record_ids':set(),'tag':f['tag']});o['names'].add(name);o['authority_ids'].update(ids);o['record_ids'].add(rid);seen.add(key)
  if f['tag']=='710':institutions[name]+=1
 for tag in ['361','541','561','563','590']:
  for index,f in enumerate(r['notes'].get(tag,[]),1):
   text=' '.join(v for k,v in f['subfields'] if k in ['a','z']);
   if not text:continue
   provenance=tag in ['361','541','561'] or bool(prov_re.search(text))
   if not provenance:continue
   key=norm(text);o=notes.setdefault(key,{'text':text,'fields':set(),'record_ids':set()});o['fields'].add(tag);o['record_ids'].add(rid)
   pm=[{'text':m.group(),'start':m.start(),'end':m.end()} for m in place_re.finditer(text)];ym=[{'text':m.group(),'start':m.start(),'end':m.end()} for m in year_re.finditer(text)];cm=[m.group() for m in century_re.finditer(text)]
   flags.add('provenance_note_candidate')
   if pm:flags.add('explicit_place_string')
   if ym or cm:flags.add('date_string')
   if pm and (ym or cm):flags.add('place_and_date_same_note')
   if tag in ['563','590']:flags.add('provenance_cue_outside_561_361')
   candidates.append({'record_id':rid,'shelfmarks':r['shelfmarks'],'field':tag,'occurrence':index,'source_text':text,'subfields':f['subfields'],'place_matches':pm,'year_matches':ym,'century_matches':cm,'copy_scope_status':'unresolved_multiple_shelfmarks' if len(r['shelfmarks'])>1 else 'single_shelfmark_candidate_not_verified','status':'lexical_candidate_not_station'})
 for flag in flags:stats[flag]+=1
 if 'provenance_cue_outside_561_361' in flags and not r['former_owners'] and not r['notes'].get('561') and not r['notes'].get('361'):stats['additional_records_from_other_note_cues']+=1
ownerlist=[]
for k,v in owners.items():ownerlist.append({'key':k,**{a:sorted(b) if isinstance(b,set) else b for a,b in v.items()},'record_count':len(v['record_ids'])})
ownerlist.sort(key=lambda x:-x['record_count']);coverage={}
for n in [5,10,20,50]:coverage[str(n)]=len(set().union(*(set(x['record_ids']) for x in ownerlist[:n])))
notelist=[{**{a:sorted(b) if isinstance(b,set) else b for a,b in v.items()},'record_count':len(v['record_ids'])} for v in notes.values()];notelist.sort(key=lambda x:-x['record_count'])
summary={'record_count':len(rows),'unique_owner_keys':len(ownerlist),'owner_grouping':'First authority identifier where present, otherwise tag and normalised name; not a complete identity reconciliation.','top_owner_union_coverage':coverage,'candidate_counts':dict(stats),'place_dictionary':places,'limitations':['Place dictionary is limited; missing matches do not imply missing places.','Years may be reference-publication dates or biographical dates, not ownership dates.','Co-occurrence does not connect a date to a place or owner.','Repeated text does not establish identical copy histories.','No event chronology, coordinates or new map stations generated.']}
for name,value in [('evidence-profile-summary.json',summary),('owner-groups.json',ownerlist),('repeated-provenance-notes.json',notelist),('provenance-text-candidates.json',candidates)]: (D/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2));print('COMMON NOTES',[(x['text'][:130],x['record_count']) for x in notelist[:8]])
md=['# Automated post-incunabula evidence profile','', 'Offline analysis of the saved swisscollections snapshot; 23 October 2026. Counts refer to bibliographic records, not uniquely identified copies. No network retrieval.','',f"Analysed {len(rows)} retained records; found {len(ownerlist)} distinct owner keys. Authority-based grouping remains provisional where identifiers or aliases differ.",'','## Reusable owner groups','','| Top owner groups | Distinct records covered (union) |','|---|---:|']
md += [f'| {n} | {v} |' for n,v in coverage.items()]
md += ['','## Candidate extraction','','These counts describe literal text matches, not verified events. The small place lexicon is recorded in the JSON output.','', '| Indicator | Records |','|---|---:|']+[f'| {k} | {v} |' for k,v in stats.items()]
md += ['','## Repeated notes','','| Note (abbreviated) | Records |','|---|---:|']+[f"| {x['text'][:180].replace('|','/')} | {x['record_count']} |" for x in notelist[:12]]
md += ['','## Boundaries and next step','','Each candidate retains record, source field occurrence, complete text, subfields, shelfmarks and matched text spans. Multiple-shelfmark records are marked for unresolved scope. Public note text only is analysed; personal life dates in name headings are not used. Numeric dates embedded in notes can still refer to literature or biography. No chronology is inferred from field order.','', 'Prioritise the most frequent institutional owner groups and repeated formulations. Check a small sample of each rule before interpreting candidate text as an event. Use the handbook as explicitly sourced enrichment only. Person-to-place assignments and inferred residence periods are not part of this run.']
(R/'docs/postincunabula-evidence-profile.md').write_text('\n'.join(md)+'\n')
