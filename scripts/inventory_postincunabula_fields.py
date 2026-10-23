import json,zipfile,re,collections,xml.etree.ElementTree as E
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/research/zurich-postincunabula-export-20261023';N={'m':'http://www.loc.gov/MARC21/slim'}
refs=json.loads((D/'working-copy-references.json').read_text());by=collections.defaultdict(list)
for x in refs:by[x['record_id']].append(x)
rows=[];counts=collections.Counter();records=collections.defaultdict(set);hits=[]
cue=re.compile(r'provenienz|vorbesitz|besitzvermerk|exlibris|ex libris|schenkung|schenkungsvermerk|donation|geschenkt|gekauft|erworben|aus dem besitz|aus der bibliothek|aus dem nachlass|eigentumsvermerk|legat\b|vermächtnis|stempel|supralibros|possessor|provenance|former owner',re.I)
import argparse
p=argparse.ArgumentParser(description='Offline field inventory; lexical matches are candidates, not proven ownership events.');p.add_argument('export_zip');args=p.parse_args()
with zipfile.ZipFile(args.export_zip) as z:
 for name in sorted(z.namelist()):
  if '/marcxml/metadata_' not in name or not name.endswith('.xml') or name.startswith('__'):continue
  for r in E.fromstring(z.read(name)).findall('.//m:record',N):
   rid=r.find('m:controlfield[@tag="001"]',N).text
   if rid not in by:continue
   occurrence=collections.Counter()
   for f in r.findall('m:datafield',N):
    tag=f.get('tag');occurrence[tag]+=1;counts[tag]+=1;records[tag].add(rid)
    sf=[(s.get('code'),s.text or '') for s in f];text=' '.join(v for k,v in sf if k not in ['0','1','2','9']);text=re.sub(r'https?://\S+', '',text);found=sorted(set(m.group(0).casefold() for m in cue.finditer(text)))
    owner=tag in ['700','710','711'] and any((k=='4' and v=='fmo') or (k=='e' and re.search('vorbesitzer|former owner',v,re.I)) for k,v in sf)
    core=tag in ['561','361'] or owner
    if tag in ['561','361'] and f.get('ind1')=='0':continue
    if core or found or tag in ['563','590','541','562'] or (tag=='949' and any(k=='z' for k,v in sf)):
     x={'record_id':rid,'tag':tag,'occurrence':occurrence[tag],'subfields':sf,'core_indicator':core,'matched_terms':found,'retained_shelfmarks':[v['shelfmark'] for v in by[rid]],'title':by[rid][0]['title']}
     rows.append(x)
     if core or found:hits.append(x)
summary={'working_references':len(refs),'working_records':len(by),'fields':{t:{'occurrences':counts[t],'records':len(records[t]),'records_with_lexical_cues':len({x['record_id'] for x in rows if x['tag']==t and x['matched_terms']}),'core_indicator_records':len({x['record_id'] for x in rows if x['tag']==t and x['core_indicator']})} for t in sorted(counts)},'records_with_core_indicators':len({x['record_id'] for x in hits if x['core_indicator']}),'records_with_any_lexical_cue':len({x['record_id'] for x in hits if x['matched_terms']}),'lexical_only_records':len({x['record_id'] for x in hits if x['matched_terms']}-{x['record_id'] for x in hits if x['core_indicator']})}
(D/'field-inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');(D/'field-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')

coreids={x['record_id'] for x in rows if x['core_indicator']}
notes=[x for x in rows if x['tag'] in ['500','541','561','563','590','596','949']]
strong=[x for x in notes if any(t!='stempel' for t in x['matched_terms'])]
summary['additional_records_with_strong_note_candidates']=len({x['record_id'] for x in strong}-coreids)
summary['note_candidate_records']=len({x['record_id'] for x in strong})
repeated=collections.defaultdict(list)
for x in strong:
 text=' '.join(v for k,v in x['subfields'] if k in ['a','z']);repeated[text].append({'record_id':x['record_id'],'tag':x['tag']})
groups=[{'text':t,'occurrences':len(v),'records':len({x['record_id'] for x in v}),'sources':v} for t,v in repeated.items()]
groups.sort(key=lambda x:(-x['records'],x['text']))
(D/'repeated-note-candidates.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n')
(D/'field-inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='fields'},indent=2))
