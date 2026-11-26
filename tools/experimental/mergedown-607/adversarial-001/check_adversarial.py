"""Refs #607. Independent bounded regression evidence audit, synthetic only.
Usage: python check_adversarial.py PACKAGE_ROOT
Reuses pinned upstream catalogue construction, not upstream decoder or metric functions.
"""
import hashlib, json, pathlib, runpy, sys, wave, struct
from collections import Counter, defaultdict
import numpy as np

COMMON = dict(zip('causal-frame control-namespace discourse-sync distributed-profile frame-length-commit migration-namespace prefix-disjoint version-bound-payload version-bridge'.split(), 'fc5dd44fe87ebcabc2a1e0213726a3fd43cb2a60 8e27fe89f2734a0b5fd666bb2018b0d379736493 cc6b996d6314fdcbb92edc85e12878d5d2077aa7 a780404e8c76820976ad6fb407429ec895a6313f 1538e258e53b62fc62315ca11eb9ba34496c5919 b3562781a974c47b41cbe066ceb755288a51b6b1 f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942 7ef6881cefa9c34355d024aeea671d021b674a55 6400cf4c1b42fbe958b0265da43ef657bb355401'.split()))
SPECS = {'binding': ('boundary1', 'source-binding-boundary', '7255d4d2a721f03174ea9550534bdbcb843c4364', '2a074c64797b310423824902d092ffb54eacf5e7'), 'overlap': ('overlap1', 'overlap-admission-audit', '826a7a3f3f969518e5079d926375356c575e80bb', '7053f813bf770c1ec195e0c4485d24f483505045')}
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def require(x, msg):
    if not x: raise ValueError(msg)
def load(root, kind):
    sub, script, h, pin = SPECS[kind]; root=root/kind; out=root/sub
    pins=COMMON | {script:h} | ({'competing-starts':'af3f673f28e65bb4fc241a22cc603a6cbb041dfb'} if kind=='overlap' else {})
    require({p.stem:blob(p.read_bytes()) for p in root.glob('*.py')}==pins, kind+' source inventory')
    m=json.loads((out/'manifest.json').read_text()); require(m=={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.name!='manifest.json'},kind+' manifest')
    rec=json.loads((out/'receipt.json').read_text()); require(rec.get('grammar_pin',rec.get('pin'))==pin and rec['source_sha256']==sha((root/(script+'.py')).read_bytes()),kind+' receipt pin')
    rows=[json.loads(l) for l in (out/'traces.jsonl').read_text().splitlines()]
    for s in rec['specimens']:
        with wave.open(str(out/s['file']),'rb') as f:
            require(f.getparams()[:3]==(1,2,16000),'WAV format'); pcm=f.readframes(f.getnframes())
        require(sha(pcm)==s['pcm_sha256'] and max(abs(x[0]) for x in struct.iter_unpack('<h',pcm))==s['peak'],'WAV payload/peak')
    return root, rec, rows, len(m)
def binding(root,rec,rows):
    # Dense exact distance over both complete short catalogues, independently of acquisition and decoder.
    _, (base,_), names = runpy.run_path(str(root/'version-bound-payload.py'))['build'](root)
    # Source translation expressed as modular powers, without reusing the candidate decoder.
    b=[np.column_stack((np.zeros((len(base),3),dtype=int),(base+s*np.array([pow(x,5,17) for x in range(10)]))%17)) for s in (0,1)]
    require(len(base)==52000,'catalogue size'); groups=defaultdict(list); stats=defaultdict(lambda:defaultdict(Counter))
    for r in rows: groups[tuple(r['origin'])].append(r)
    require(len(groups)==16 and len(rows)==128,'binding counts')
    for origin, group in groups.items():
        s,i=origin; a=b[s][i]; rival=b[1-s]; dist=np.sum(rival!=a,axis=1); k=int(np.argmin(dist)); delta=np.flatnonzero(rival[k]!=a).tolist()
        require(len(delta)==5 and len(group)==8 and len({r['case'] for r in group})==8,'distance/condition count')
        for r in group:
            require(r['target']==[1-s,k] and r['distance']==len(delta),'target')
            obs=a.tolist(); edits=r['substitutions']; erasures=r['erasures']
            require(edits==delta[:len(edits)] and erasures==delta[len(edits):len(edits)+len(erasures)],'edit positions')
            for x in edits: obs[x]=int(rival[k,x])
            for x in erasures: obs[x]=None
            require(obs==r['symbols'],'edited symbols')
            keep=[j for j,x in enumerate(obs) if x is not None]; candidates=[]
            for v in (0,1):
                hits=np.where(np.sum(b[v][:,keep]!=np.array([obs[j] for j in keep]),axis=1)<=2)[0].tolist()
                require(hits==r['hits'][str(v)],'candidate set'); candidates.extend((v,h) for h in hits)
            gate=[x for x in candidates if x[0]==r['label']]; g=gate[0] if len(gate)==1 else None; u=candidates[0] if len(candidates)==1 else None
            ev=[e for e in r['events'] if e['kind'] in ('release','reject')]; require(len(ev)==1 and ev[0]['source']==r['label'] and ev[0]['seen']==obs+[18,18],'acquisition record')
            require((tuple([ev[0]['source'],ev[0]['identity'][1]]) if ev[0]['kind']=='release' else None)==g,'native gated decision')
            for p,got in [('label-gated',g),('union',u),('union-agreement',u if u and u[0]==r['label'] else None)]:
                result='withheld' if got is None else 'correct' if got==origin else 'wrong'; expected={'decoded':list(got) if got else None,'outcome':result,'meaning_changed':bool(got and names[got[1]]!=names[i])}
                require(expected==r['outcomes'][p],'binding outcome'); stats[r['case']][p][result]+=1
    require(stats==rec['stats'],'binding aggregate')
    for x in rec['specimens']:
        r=next(r for r in rows if r['origin']==x['origin'] and r['case']==x['case']); require(x['pcm_sha256']==r['pcm_sha256'] and x['outcomes']==r['outcomes'],'binding specimen join')
    return {'origins':len(groups),'nearest_comparisons':len(groups)*len(base),'candidate_decisions':len(rows)*3,'stats':stats}
def overlap(rec,rows):
    groups=defaultdict(list); stats=defaultdict(lambda:defaultdict(Counter)); total=defaultdict(Counter)
    for r in rows:
        key=(r['pair'],r['offset_slots'],r['gain_b_over_a']); groups[key].append(r)
        ev=r['events']; require(all(a['sample']<=b['sample'] for a,b in zip(ev,ev[1:])),'noncausal event order')
        releases=[e for e in ev if e['kind']=='release']; got=[[e['source'],*e['identity']] for e in releases]
        for e in releases:
            require(e['sample']-e['ready_sample']==e['wait_samples']>=0,'release waiting')
            require(any(c['kind']=='candidate' and c['sample']==e['ready_sample'] and c['identity']==e['identity'] and c['source']==e['source'] and c['body_start']==e['body_start'] for c in ev),'release candidate provenance')
        want=Counter(map(tuple,r['expected'])); correct=sum((want&Counter(map(tuple,got))).values()); wrong=len(got)-correct; missing=sum(want.values())-correct
        require(got==r['decoded'] and (correct,wrong,missing)==(r['correct'],r['wrong'],r['missing']),'release outcome')
        counts=dict(correct=correct,wrong=wrong,missing=missing,suppressed=sum(e['kind']=='suppress-overlap' for e in ev),wait=sum(e['wait_samples'] for e in releases)); stats[f'{key[1]}:{key[2]}'][r['policy']].update(counts); total[r['policy']].update(counts)
    policies={'locked','restart','replace-two','body-only','no-suppression'}
    require(len(groups)==144 and len(rows)==720,'overlap counts')
    for g in groups.values(): require(len(g)==5 and {r['policy'] for r in g}==policies and len({r['pcm_sha256'] for r in g})==1 and all(r['expected']==g[0]['expected'] for r in g),'matched policies')
    require(stats==rec['summary'],'overlap aggregate')
    for x in rec['specimens']:
        g=groups[(0,x['offset_slots'],x['gain_b_over_a'])]; require(all(r['pcm_sha256']==x['pcm_sha256'] and r['expected']==x['expected'] and r['decoded']==x['decoded'][r['policy']] for r in g),'overlap specimen join')
    return {'observations':len(groups),'evaluations':len(rows),'total':total,'critical':stats['-2:1.35']}
def main(root):
    br,brec,brows,bm=load(root,'binding'); _,orec,orows,om=load(root,'overlap')
    return {'schema':'mhac-mergedown-adversarial-001','source_files':21,'manifest_entries':bm+om,'wav_files':len(brec['specimens'])+len(orec['specimens']),'binding':binding(br,brec,brows),'overlap':overlap(orec,orows),'limitations':'Pinned upstream catalogue reused; binding dense symbol audit and overlap event recount are not independent acoustic extraction or new holdout. Synthetic only.'}
if __name__=='__main__': print(json.dumps(main(pathlib.Path(sys.argv[1])),indent=2,sort_keys=True))
