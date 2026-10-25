#!/usr/bin/env python3
"""Prepare four owner decisions from existing MARC evidence; no map mutation."""
from pathlib import Path
from collections import defaultdict,Counter
import json,re,hashlib,html
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/research/zurich-postincunabula-export-20261023';OUT=ROOT/'data/research/owner-review-20261025'
IDS=['100408605','118637533','118694413','118517384']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def key(r):return(r['record_id'],r['institution_code'],r['shelfmark'])
def note(f):return ' '.join(v for c,v in f['subfields'] if c=='a')
def build():
 groups=read(DATA/'coverage-audit-owner-groups.json');refs={key(r):r for r in read(DATA/'coverage-audit-references.json')};fields=read(DATA/'provenance-assignments.json')
 decisions=[];details=[];allkeys=set();newkeys=set()
 patterns={
  '100408605':r'(?:unsicher|wahrscheinlich|vermutlich).{0,50}Sim[ml]+er',
  '118637533':r'(?:[Uu]nsicher|Unischer) ob aus dem Besitz Zwinglis|Vorbesitzer Zwingli, Huldrych: unsicher',
  '118694413':r'(?:[Uu]nsicher ob|[Ww]ahrscheinlich) aus dem Besitz (?:Conrad )?Gessners|vermutlich Gessners Handschrift',
  '118517384':r'[Ww]ahrscheinlich aus dem Vorbesitz Heinrich Bullingers'}
 for gid in IDS:
  authority='(DE-588)'+gid;g=next(g for g in groups if authority in g['authority_ids'] and g['tag']=='700');ks={tuple(k) for k in g['reference_keys']};allkeys|=ks;newkeys|={k for k in ks if not refs[k]['place_candidates']}
  norms=read(OUT/(gid+'.json'));assert norms['gndIdentifier']==gid
  owner_fields=[f for f in fields if any(c=='0' and v==authority for c,v in f['subfields'])]
  flagged=set();used=set();owneronly=set();examples=[]
  for k in sorted(ks):
   own=[f for f in owner_fields if [k[1],k[2]] in f['targets'] and f['record_id']==k[0] and f['assignment'] in ['explicit','plausible']]
   notes=[f for f in fields if f['tag'] not in ['700','710','711'] and f['record_id']==k[0] and [k[1],k[2]] in f['targets'] and f['assignment'] in ['explicit','plausible']]
   flags=[f for f in notes if re.search(patterns[gid],note(f))]
   use=[f for f in notes if gid=='118694413' and 'Von Gessner in der Stiftsbibliothek am Grossmünster benutzt' in note(f)]
   if flags:flagged.add(k)
   if use:used.add(k)
   if not notes:owneronly.add(k)
   details.append({'gnd_id':gid,'owner_name':g['names'][0],'record_id':k[0],'institution_code':k[1],'shelfmark':k[2],'title':refs[k]['title'],
    'catalogue_url':refs[k]['catalogue_url'],'owner_fields':own,'assigned_context_notes':notes,'ownership_caveat_pattern_hit':bool(flags),
    'explicit_gessner_use_at_grossmuenster':bool(use),'existing_place_candidates':refs[k]['place_candidates'],
    'decision_status':'pending_discussion','warning':'A context note can concern another owner. Review flags are narrow wording matches, not an exhaustive certainty assessment.'})
  decisions.append({'gnd_id':gid,'catalogue_names':g['names'],'gnd_preferred_name':norms.get('preferredName'),
   'references':len(ks),'without_any_prepared_place':sum(not refs[k]['place_candidates'] for k in ks),
   'without_assigned_context_note':len(owneronly),'ownership_caveat_pattern_hits':len(flagged),'explicit_gessner_use_at_grossmuenster':len(used),
   'owner_field_assignment_counts':dict(Counter(f['assignment'] for f in owner_fields)),
   'gnd_place_of_activity':norms.get('placeOfActivity',[]),'authority_source':'https://lobid.org/gnd/'+gid+'.json',
   'gnd_birth':norms.get('dateOfBirth'),'gnd_death':norms.get('dateOfDeath'),
   'decision_status':'pending_discussion','date_policy':'No owner lifespan or residence period is inserted as a copy event date.',
   'reference_keys':[list(k) for k in sorted(ks)]})
 return decisions,details,{'unique_references_in_four_groups':len(allkeys),'unique_references_without_any_prepared_place':len(newkeys),'source_snapshot':'2026-10-23','review_date':'2026-10-25','counts_overlap_between_owners':True,'no_map_changes':True}
def main():
 d,rows,s=build();OUT.mkdir(parents=True,exist_ok=True)
 for name,obj in [('owner-decisions',d),('owner-evidence',rows),('owner-review-summary',s)]:
  (OUT/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'coverage-audit-owner-groups.json',DATA/'coverage-audit-references.json',DATA/'provenance-assignments.json']+[OUT/(i+'.json') for i in IDS]}
 (OUT/'source-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
 table=[]
 for r in rows:
  notes='\n\n'.join('MARC '+f['tag']+': '+note(f) for f in r['assigned_context_notes']) or 'Only the linked owner field; no assigned context note in current extraction.'
  status=('Uncertainty wording flagged. ' if r['ownership_caveat_pattern_hit'] else '')+('Explicit use at Grossmünster. ' if r['explicit_gessner_use_at_grossmuenster'] else '')
  table.append('<tr><td>'+html.escape(r['owner_name'])+'</td><td><a href="'+html.escape(r['catalogue_url'])+'">'+html.escape(r['shelfmark'])+'</a></td><td>'+html.escape(' / '.join(r['title']))+'</td><td>'+html.escape(status)+'</td><td style="white-space:pre-wrap">'+html.escape(notes)+'</td></tr>')
 page='<!doctype html><html lang="de"><meta charset="utf-8"><title>Vorbesitzer: Belegliste</title><style>body{font:15px/1.45 system-ui;margin:2rem}table{border-collapse:collapse}th,td{padding:.7rem;border:1px solid #bbb;vertical-align:top}th{background:#eee}input{padding:.7rem;width:90%;margin:1rem 0}</style><h1>Vier Vorbesitzergruppen: Belegliste</h1><p>Entscheidungsvorbereitung, keine neuen Kartenstationen. Die Liste enthält '+str(len(rows))+' Person-Nachweis-Kombinationen für '+str(s['unique_references_in_four_groups'])+' verschiedene Katalognachweise. Kontextnotizen können andere Personen betreffen; Unsicherheitsmarker sind keine vollständige Prüfung.</p><input id="q" placeholder="Name, Signatur oder Text" aria-label="Belege filtern"><table><thead><tr><th>Person</th><th>Signatur</th><th>Titel</th><th>Hinweis</th><th>Zugeordnete Katalognotizen</th></tr></thead><tbody>'+''.join(table)+'</tbody></table><script>const rs=[...document.querySelectorAll("tbody tr")];document.getElementById("q").addEventListener("input",e=>{let q=e.target.value.toLocaleLowerCase();for(let r of rs)r.hidden=!r.textContent.toLocaleLowerCase().includes(q)});</script></html>'
 (OUT/'owner-evidence-review.html').write_text(page,encoding='utf-8');print(json.dumps(d,ensure_ascii=False,indent=2)[:0]);print(s)
 for x in d:print(x['catalogue_names'],x['references'],x['ownership_caveat_pattern_hits'],x['explicit_gessner_use_at_grossmuenster'],x['without_assigned_context_note'])
if __name__=='__main__':main()
