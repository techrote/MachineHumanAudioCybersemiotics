"""Refs #452/#453. Synthetic aligned PCM; no human evidence or action authority.
Parent 39421a0d705d5257cf8083e36a7739dc72123398. Run: python hybrid-morphology.py OUTPUT
Observation motivation: #443 depth-level-audit at 1be3c82fa74264121400c88de0679b85ba8350c4.
"""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location('morph',Path(__file__).with_name('epistemic-morphology.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); d=m.d
SEED=452530
F=(*m.F,np.arange(3)*100+4300)
B=[np.exp(-2j*np.pi*f[:,None]*np.arange(160,800)/d.RATE) for f in F]
LAYOUTS={'serial':((0,),(1,),(2,),(3,),(4,)), 'poly':((0,1,2,3,4),), 'hybrid2':((0,1),(2,3,4)), 'hybrid3':((0,1),(2,3),(4,)), 'check2':((0,1,5),(2,3,4)), 'check3':((0,1),(2,3),(4,5))}

def protect(rows,mode):
    return [(*r,sum(r[2:])%3) for r in rows] if mode.startswith('check') else list(rows)

def decode(rows,mode):
    if mode.startswith('check'):
        repaired=[]
        for r in rows:
            if len(r)!=6 or any(v is not None and v not in range(len(F[b])) for b,v in enumerate(r)): return None
            if None in r[:2]: return None
            q=list(r[2:]); missing=[i for i,v in enumerate(q) if v is None]
            if len(missing)>1: return None
            if missing:
                i=missing[0]; q[i]=sum(q[:3])%3 if i==3 else (q[3]-sum(v for v in q[:3] if v is not None))%3
            if sum(q[:3])%3!=q[3]: return None
            repaired.append((*r[:2],*q[:3]))
        rows=repaired
    return m.decode(rows)

def render(rows,mode,phase):
    blocks=[]
    for r in rows:
        for group in LAYOUTS[mode]:
            x=np.zeros(d.SLOT)
            for b in group:
                if r[b] is not None: x[:d.ACTIVE]+=d.AMP*d.W*np.sin(2*np.pi*F[b][r[b]]*d.T+phase)
            blocks.append(x)
    return np.concatenate(blocks)

def receive(y,mode,t):
    groups=LAYOUTS[mode]; n=len(groups)
    if not len(y) or len(y)%(n*d.SLOT): return []
    x=np.asarray(y).reshape(-1,d.SLOT)[:,160:800].astype(float); cols={}
    for j,g in enumerate(groups):
        for b in g:
            s=abs(x[j::n]@B[b].T)*2/640; o=np.argsort(s,axis=1)
            cols[b]=[int(i[-1]) if v[i[-1]]>=t[b] and v[i[-1]]-v[i[-2]]>=t[b]/3 else None for v,i in zip(s,o)]
    return list(zip(*(cols[b] for b in sorted(cols))))

def run(out):
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED); census=Counter()
    for q in itertools.product(range(3),repeat=3):
        r=protect([(0,0,*q)],'check3')[0]; expected=decode([r],'check3'); assert expected is not None
        for b in range(2,6):
            x=list(r); x[b]=None; assert decode([x],'check3')==expected; census['single_erasure_recovered']+=1
            for delta in (1,2):
                x=list(r); x[b]=(x[b]+delta)%3; assert decode([x],'check3') is None; census['single_substitution_withheld']+=1
        for a,b in itertools.combinations(range(2,6),2):
            for u,v in itertools.product((1,2),repeat=2):
                x=list(r); x[a]=(x[a]+u)%3; x[b]=(x[b]+v)%3; got=decode([x],'check3'); assert got!=expected
                census['double_substitution_wrong' if got is not None else 'double_substitution_withheld']+=1
    thresholds={}
    for sd in (0,1000,3500):
        z=np.random.default_rng(SEED+sd).normal(0,sd,(4096,640))
        thresholds[sd]=[max(80.,float(np.quantile((abs(z@b.T)*2/640).max(axis=1),.999))) for b in B]
    trees=d.catalogue(); universe=set(range(len(trees))); prev=set(np.random.default_rng(452510).choice(len(trees),96,replace=False)); audit=set(np.random.default_rng(4425401).choice(sorted(universe-prev),192,replace=False)); prior=set(np.random.default_rng(452520).choice(sorted(universe-prev-audit),96,replace=False)); picks=rng.choice(sorted(universe-prev-audit-prior),64,replace=False)
    traces=[]; gallery=[]; conditions=('clean','noise1000','noise3500','erase','replace','cancel','erase_noise1000')
    for i,idx in enumerate(picks):
        tree=trees[int(idx)]; q=tuple(tuple(map(int,rng.integers(0,3,3))) for _ in d.encode(tree)); base=m.encode(tree,q); phase=float(rng.uniform(0,2*np.pi)); j=i%len(base); b=2+i%3
        ref=render(base,'serial',phase); noise=np.random.default_rng(SEED+10000+i).normal(size=(len(base),5,d.SLOT))
        for mode,condition in itertools.product(LAYOUTS,conditions):
            rows=protect(base,mode); original=render(rows,mode,phase); scale=np.max(abs(ref))/np.max(abs(original)); r=list(rows[j]); sd=3500 if condition=='noise3500' else 1000 if condition in ('noise1000','erase_noise1000') else 0
            if condition.startswith('erase'): r[b]=None
            if condition=='replace': r[b]=(r[b]+1)%3
            if condition=='cancel': r[2]=(r[2]+1)%3; r[3]=(r[3]+2)%3
            rows[j]=tuple(r); clean=m.pcm(render(rows,mode,phase)*scale); n=len(LAYOUTS[mode]); y=m.pcm(clean.astype(float)+sd*noise[:,:n,:].reshape(-1)); obs=receive(y,mode,thresholds[sd]); got=decode(obs,mode); status='withheld' if got is None else 'correct' if got==(tree,q) else 'wrong'
            traces.append(dict(fixture=int(idx),tree=tree,qualifiers=q,mode=mode,condition=condition,observed=obs,decoded=got,status=status,samples=len(y),peak=int(np.max(abs(clean.astype(int)))),energy=int(np.sum(clean.astype(np.int64)**2)),pcm_sha256=hashlib.sha256(y.tobytes()).hexdigest()))
            if i==0 and condition in ('clean','erase','replace','cancel'):
                p=out/f'{mode}-{condition}.wav'
                with wave.open(str(p),'wb') as w: w.setparams((1,2,d.RATE,0,'NONE','not compressed')); w.writeframes(y.tobytes())
                gallery.append(dict(file=p.name,status=status,ms=len(y)*1000/d.RATE))
    groups=[]
    for mode,condition in itertools.product(LAYOUTS,conditions):
        r=[t for t in traces if t['mode']==mode and t['condition']==condition]; assert len(r)==64
        groups.append(dict(mode=mode,condition=condition,counts=dict(Counter(t['status'] for t in r)),samples=sum(t['samples'] for t in r),energy=sum(t['energy'] for t in r),peak=max(t['peak'] for t in r)))
    assert all(t['status']=='correct' for t in traces if t['condition']=='clean')
    receipt=dict(schema='mhac-hybrid-morphology-v1',seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=m.sha(Path(__file__)),layouts=LAYOUTS,thresholds=thresholds,census=dict(census),trials=len(traces),groups=groups,gallery=gallery,limits='Known aligned timing, mode and Gaussian noise SD. Peak matched before fault; not energy/loudness matched. Check protects only qualifiers within a node; simultaneous compensating substitutions evade it. No participant or device evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces))
    (out/'index.html').write_text('<!doctype html><meta charset=utf-8><title>Hybrid morphology</title><h1>Hybrid morphology</h1><p>Synthetic specimens; start at low volume. Status is machine decoding only.</p>'+''.join(f'<p>{g["file"]} — {g["status"]} / {g["ms"]} ms<br><audio controls preload="none" src="{g["file"]}"></audio></p>' for g in gallery)+'<p><a href="receipt.json">Results</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:m.sha(p) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(Path(sys.argv[1]))
