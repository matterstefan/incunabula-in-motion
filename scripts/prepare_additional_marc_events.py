#!/usr/bin/env python3
"""Prepare additional source-linked dated events; never modifies the live map."""
from pathlib import Path
import json,re,hashlib,html
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/research/zurich-postincunabula-export-20261023'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def key(r):return (r['record_id'],r['institution_code'],r['shelfmark'])
def text(f):return ' '.join(v for c,v in f['subfields'] if c=='a')
def extract(f,rules):
 if f['assignment'] not in ['explicit','plausible'] or f['tag'] not in ['500','561','590','361']:return []
 out=[]
 for rule in rules:
  for m in re.finditer(rule['pattern'],text(f)):
   out.append({**{k:v for k,v in rule.items() if k!='pattern'},'year':int(m['year']),'matched_text':m.group(0)})
 return out

def build():
 refs={key(r):r for r in read(DATA/'working-copy-references.json')}
 rulesfile=ROOT/'data/authority/postincunabula-additional-event-rules.json'
 rules=read(rulesfile)
 pilot=read(ROOT/'data/map/marc-pilot.json');existing={key(r) for r in pilot}
 events=[];seen=set()
 for f in read(DATA/'provenance-assignments.json'):
  for e in extract(f,rules['rules']):
   for institution,shelf in f['targets']:
    k=(f['record_id'],institution,shelf)
    if k not in refs:continue
    signature=(k,e['rule_id'],e['year'],f['tag'],f['occurrence'])
    if signature in seen:continue
    seen.add(signature)
    ref=refs[k];geo=rules['places'][e['place']]
    events.append({**e,'record_id':k[0],'institution_code':k[1],'shelfmark':k[2],
       'title':ref['title'],'publication_source':ref['publication'],
       'reference_id':'marc:'+hashlib.sha256('\x1f'.join(k).encode()).hexdigest()[:20],
       'catalogue_url':'https://swisscollections.ch/Record/'+k[0],
       'already_in_first_pilot':k in existing,'date_certainty':'year_stated_in_catalogue_note',
       'copy_assignment':f['assignment'],'evidence':f,'coordinates':geo,
       'status':'prepared_not_published','review_note':'Original scope retained. A shared binding or inscription on another print does not establish when each constituent joined the volume. This is not a new complete itinerary.'})
 events.sort(key=lambda e:(e['record_id'],e['shelfmark'],e['year'],e['rule_id']))
 summary={'working_references':len(refs),'additional_event_candidates':len(events),
   'distinct_references':len({key(e) for e in events}),
   'references_already_in_first_pilot':len({key(e) for e in events if e['already_in_first_pilot']}),
   'new_references':len({key(e) for e in events if not e['already_in_first_pilot']}),
   'places':{place:sum(e['place']==place for e in events) for place in sorted({e['place'] for e in events})},
   'status':'prepared_not_published','rules_sha256':hashlib.sha256(rulesfile.read_bytes()).hexdigest(),
   'input_sha256':{name:hashlib.sha256((DATA/name).read_bytes()).hexdigest() for name in ['working-copy-references.json','provenance-assignments.json']}}
 return events,summary

def main():
 events,summary=build()
 for name,obj in [('additional-dated-events',events),('additional-dated-events-summary',summary)]:
  (DATA/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows=[]
 for e in events:
  cells=[e['shelfmark']+' — '+' / '.join(e['title']),e['place']+' — '+str(e['year']),e['owner'], 'Additional station for existing pilot reference' if e['already_in_first_pilot'] else 'New reference outside the first pilot',text(e['evidence']),e['copy_assignment']]
  rows.append('<tr>'+''.join('<td>'+html.escape(c)+'</td>' for c in cells)+'<td><a href="'+html.escape(e['catalogue_url'])+'">Catalogue</a></td></tr>')
 page='<!doctype html><html lang="en"><meta charset="utf-8"><title>Additional MARC events</title><style>body{font:16px/1.5 system-ui;margin:2rem}td,th{padding:.7rem;border:1px solid #bbb;vertical-align:top}table{border-collapse:collapse}th{background:#eee}</style><h1>Additional dated MARC events — preparation</h1><p>Not yet published on the map. Source notes and copy assignment retained; bound-with evidence does not establish binding chronology.</p><p>'+str(summary['additional_event_candidates'])+' event candidates; '+str(summary['references_already_in_first_pilot'])+' existing pilot references; '+str(summary['new_references'])+' new references.</p><table><tr><th>Reference</th><th>Place / year</th><th>Owner / recipient</th><th>Relation to pilot</th><th>Original note</th><th>Copy assignment</th><th>Source</th></tr>'+''.join(rows)+'</table></html>'
 (DATA/'additional-dated-events-review.html').write_text(page,encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
