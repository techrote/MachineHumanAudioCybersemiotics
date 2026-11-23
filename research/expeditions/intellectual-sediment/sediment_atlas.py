#!/usr/bin/env python3
"""Transparent lexical baseline for MHAC's narrative Markdown corpus."""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse, hashlib, json, math, os, re, subprocess

STOP=set('''a an and are as at be been being but by can could did do does for from had has have he her him his how i if in into is it its may might more most must my no nor not of on only or other our out over same she should so some such than that the their them then there these they this those through to too under up very was we were what when where which while who why will with would you your about after again against all any because before below between both each few further here once own per said says since still until use used using via within without research repo repository github branch branches commit commits file files path paths issue issues pull request requests pr prs main current existing actual exact accepted acceptance status scope scoped work working task tasks record records test tests tested testing check checks checked generated generation artifact artifacts document documents section sections read reading source sources evidence protocol protocols claim claims review reviews new independent access study studies frozen data result results explicit one paper papers publication publications search searches report reports article articles author authors doi full-text fulltext'''.split())
TOKEN=re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*')
FENCE=re.compile(r'\x60\x60\x60.*?\x60\x60\x60|~~~.*?~~~',re.S); INLINE=re.compile(r'\x60[^\x60\n]+\x60'); LINK=re.compile(r'\[([^\]]+)\]\([^)]+\)'); URL=re.compile(r'https?://\S+')
STYLE={
 'anti_collapse':[r'\bdistinguish\w*\b',r'\bseparat\w*\b',r'\bconflat\w*\b',r'\bcollaps\w*\b',r'\bkeep\b.{0,45}\bdistinct\b',r'\bnot the same\b'],
 'provisionality':[r'\bprovisional\w*\b',r'\bhypothes\w*\b',r'\bcandidate\b',r'\bunvalidated\b',r'\bspeculati\w*\b',r'\buncertain\w*\b',r'\binconclusive\b'],
 'adversariality':[r'\bfalsif\w*\b',r'\bcounterexample\w*\b',r'\bnegative control\w*\b',r'\breject\w*\b',r'\badversarial\w*\b'],
 'provenance':[r'\bprovenance\b',r'\bsource[- ](?:checked|bound|located|traceable)\b',r'\btraceab\w*\b',r'\blineage\b',r'\bidentity\b',r'\bversion\w*\b'],
 'boundary_disclaimer':[r'\bdoes not\b',r'\bdo not\b',r'\bcannot\b',r'\bnot evidence\b',r'\bnot a\b',r'\bnever\b'],
 'exaptation':[r'\bexapt\w*\b',r'\breus\w*\b',r'\btransfer\w*\b',r'\bcross[- ]domain\b',r'\binspir\w*\b']}
MOTIFS={
 'meaning_semiosis':[r'\bmeaning\b',r'\bsemantic\w*\b',r'\bsemiotic\w*\b',r'\bsemiosis\b',r'\binterpretant\w*\b',r'\bgrounding\b'],
 'observer_context_frame':[r'\bobserver\w*\b',r'\bcontext\w*\b',r'\bperspective\w*\b',r'\bframe\w*\b',r'\bviewpoint\w*\b'],
 'uncertainty_epistemics':[r'\buncertain\w*\b',r'\bcertainty\b',r'\bunknown\b',r'\bconfidence\b',r'\bepistemic\w*\b'],
 'repair_grounding':[r'\brepair\w*\b',r'\bclarif\w*\b',r'\brepeat\w*\b',r'\backnowledg\w*\b',r'\bgrounding\b'],
 'action_urgency_consequence':[r'\baction\w*\b',r'\burgenc\w*\b',r'\bdeadline\w*\b',r'\bconsequence\w*\b',r'\bhazard\w*\b'],
 'affect_anthropomorphism':[r'\baffect\w*\b',r'\bemotion\w*\b',r'\bwarmth\b',r'\bsycophan\w*\b',r'\banthropomorph\w*\b',r'\bfrustrat\w*\b'],
 'provenance_identity_authority':[r'\bprovenance\b',r'\bidentity\b',r'\bauthorit\w*\b',r'\bpermission\w*\b',r'\blineage\b',r'\bversion\w*\b'],
 'state_lifecycle_time':[r'\bstate\b',r'\blifecycle\b',r'\bpersist\w*\b',r'\bsupersed\w*\b',r'\bstale\b',r'\btemporal\w*\b'],
 'composition_binding_mapping':[r'\bcomposit\w*\b',r'\bbinding\b',r'\bmapping\w*\b',r'\bfield\w*\b',r'\bcodebook\w*\b'],
 'failure_ambiguity_conflict':[r'\bfail\w*\b',r'\bambigu\w*\b',r'\bconflict\w*\b',r'\bmisunderstand\w*\b',r'\berror\w*\b'],
 'exaptation_transfer':[r'\bexapt\w*\b',r'\breus\w*\b',r'\btransfer\w*\b',r'\bcross[- ]domain\b',r'\bsediment\b']}

def fine(p):
 if '/' not in p:return 'root'
 if p.startswith('docs/'):return 'docs'
 for pre,n in [('research/analysis/','analysis'),('research/expeditions/','expeditions'),('research/tangents/','tangents'),('research/protocol/','protocol'),('research/novelty/','novelty'),('research/sources/','sources'),('research/searches/','searches'),('research/screening/','screening'),('research/registry/','registry')]:
  if p.startswith(pre):return n
 return 'other'
def family(p):
 f=fine(p)
 if f in {'root','docs'}:return 'governance_foundations'
 if f=='analysis':return 'theory_analysis'
 if f in {'protocol','novelty'}:return 'method_novelty'
 if f in {'sources','searches','screening','registry'}:return 'evidence_retrieval'
 if f in {'expeditions','tangents'}:return 'exploratory_research'
 return 'other'
def clean(s):
 s=FENCE.sub(' ',s);s=INLINE.sub(' ',s);s=LINK.sub(r'\1',s);s=URL.sub(' ',s);return re.sub(r'[#>*_|=~<>]+',' ',s)
def tokens(s):return TOKEN.findall(clean(s).lower())
def phrases(ws):
 out=set();ws=list(ws)
 for n in (1,2,3):
  for i in range(len(ws)-n+1):
   g=ws[i:i+n]
   if all(len(x)>=3 and x not in STOP for x in g):out.add(' '.join(g))
 return out
def motif_hits(text):
 z=clean(text).lower();out={}
 for name,ps in MOTIFS.items():
  n=sum(len(re.findall(p,z,re.I)) for p in ps)
  if n:out[name]=n
 return out

def first_dates(root):
 try:o=subprocess.run(['git','-C',str(root),'log','--reverse','--all','--date=format-local:%Y-%m-%d','--format=@@%ad','--name-status','--diff-filter=A'],capture_output=True,text=True,check=True,env={**os.environ,'TZ':'UTC'}).stdout
 except Exception:return {}
 d={};day=None
 for line in o.splitlines():
  if line.startswith('@@'):day=line[2:].strip()
  elif day and line.startswith('A\t'):d.setdefault(line.split('\t',1)[1],day)
 return d
def head(root):
 try:return subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
 except Exception:return None
def eligible(rel):return rel.endswith('.md') and not rel.startswith(('.git/','.github/','build/','tests/fixtures/','research/registry/generated/','research/expeditions/intellectual-sediment/'))
def entropy(c):
 n=sum(c.values())
 if n==0 or len(c)<2:return 0.0
 return -sum((v/n)*math.log(v/n) for v in c.values())/math.log(len(c))
def score(df,c):return math.log2(1+df)*(1+entropy(c))*(1+math.sqrt(len(c)))
def build(root):
 root=root.resolve();dates=first_dates(root);docs=[]
 for p in sorted(root.rglob('*.md')):
  rel=p.relative_to(root).as_posix()
  if not eligible(rel):continue
  try:s=p.read_text(encoding='utf-8')
  except UnicodeDecodeError:continue
  ws=tokens(s);docs.append({'path':rel,'family':family(rel),'fine':fine(rel),'text':s,'words':ws,'phrases':phrases(ws),'date':dates.get(rel)})
 byphrase=defaultdict(list)
 for d in docs:
  for q in d['phrases']:byphrase[q].append(d)
 rows=[]
 for q,ds in byphrase.items():
  if len(ds)<2:continue
  fc=Counter(x['family'] for x in ds);rows.append({'phrase':q,'docs':len(ds),'families':dict(sorted(fc.items())),'family_count':len(fc),'entropy':round(entropy(fc),6),'score':round(score(len(ds),fc),6),'samples':[x['path'] for x in sorted(ds,key=lambda z:z['path'])[:5]]})
 rows.sort(key=lambda x:(-x['score'],-x['family_count'],-x['docs'],x['phrase']))
 famdocs=Counter(x['family'] for x in docs);famwords=Counter();finec=Counter(x['fine'] for x in docs)
 for d in docs:famwords[d['family']]+=len(d['words'])
 markers={};totalm=Counter()
 for fam in sorted(famdocs):
  ds=[d for d in docs if d['family']==fam];wc=sum(len(d['words']) for d in ds);c=Counter()
  for d in ds:
   z=clean(d['text']).lower()
   for name,ps in STYLE.items():c[name]+=sum(len(re.findall(p,z,re.I|re.S)) for p in ps)
  markers[fam]={k:{'count':c[k],'per_1000':round(1000*c[k]/max(1,wc),4)} for k in STYLE};totalm.update(c)
 motifout={}
 for name,ps in MOTIFS.items():
  match=[]
  for d in docs:
   z=clean(d['text']).lower();n=sum(len(re.findall(p,z,re.I)) for p in ps)
   if n:match.append((d,n))
  fc=Counter(d['family'] for d,n in match);early={}
  for fam in fc:
   a=sorted((d['date'],d['path']) for d,n in match if d['family']==fam and d['date'])
   if a:early[fam]={'date':a[0][0],'path':a[0][1]}
  motifout[name]={'documents':len(match),'families':dict(sorted(fc.items())),'family_count':len(fc),'hits':sum(n for d,n in match),'earliest_by_family':dict(sorted(early.items())),'samples':[{'path':d['path'],'hits':n,'date':d['date']} for d,n in sorted(match,key=lambda x:(-x[1],x[0]['path']))[:8]]}
 hist=defaultdict(Counter);undated=0
 for d in docs:
  if d['date']:hist[d['date']][d['family']]+=1
  else:undated+=1
 h=hashlib.sha256()
 for d in sorted(docs,key=lambda x:x['path']):h.update(d['path'].encode());h.update(b'\0');h.update(hashlib.sha256(d['text'].encode()).digest())
 return {'schema':'mhac-intellectual-sediment-atlas-v1','head_sha':head(root),'corpus':{'documents':len(docs),'words':sum(len(d['words']) for d in docs),'sha256':h.hexdigest(),'families':dict(sorted(famdocs.items())),'family_words':dict(sorted(famwords.items())),'fine_families':dict(sorted(finec.items()))},'style':{'totals':dict(totalm),'by_family':markers},'motifs':motifout,'top_bridges':[x for x in rows if x['family_count']>=3 and x['docs']>=4][:40],'sparse_bridges':[x for x in rows if 2<=x['docs']<=7 and x['family_count']>=2 and ' ' in x['phrase']][:40],'history':{'first_add_by_date':{k:dict(sorted(v.items())) for k,v in sorted(hist.items())},'undated':undated,'warning':'first-add dates are document lineage approximations, not first concept introduction'},'limits':['lexical recurrence is not semantic identity','shared instructions can induce repeated vocabulary and style','cross-family phrases may reflect citation or copying','motif lexicons are analyst-chosen','atlas does not identify consciousness, intent, authorship or originality']}
def ci(a):return {'head_sha':a['head_sha'],'corpus':a['corpus'],'style':a['style'],'motifs':{k:{'documents':v['documents'],'family_count':v['family_count'],'families':v['families'],'earliest_by_family':v['earliest_by_family']} for k,v in a['motifs'].items()},'top_bridges':[{k:x[k] for k in ('phrase','docs','family_count','entropy','score')} for x in a['top_bridges'][:20]],'sparse_bridges':[{'phrase':x['phrase'],'docs':x['docs'],'family_count':x['family_count'],'score':x['score'],'samples':x['samples'][:3]} for x in a['sparse_bridges'][:15]],'history':a['history']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--json',type=Path);p.add_argument('--print-ci-summary',action='store_true');a=p.parse_args();r=build(a.root)
 if a.json:a.json.parent.mkdir(parents=True,exist_ok=True);a.json.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 if a.print_ci_summary:print('MHAC_X004_SUMMARY='+json.dumps(ci(r),sort_keys=True))
 elif not a.json:print(json.dumps(ci(r),indent=2,sort_keys=True))
if __name__=='__main__':main()
