"""Refs #452/#453. Synthetic scoped morphology, not human evidence.
Pinned polyphonic-depth.py at 93fcfcb9ae78e0a4686baff9bffe25e44f117c9a,
blob 2715c38cf4d7dd2727d161a8020a46078d72b690. Level-control motivation:
Observatory #443 depth-level-audit.py at 1be3c82fa74264121400c88de0679b85ba8350c4.
Run: OPENBLAS_NUM_THREADS=1 python epistemic-morphology.py OUTPUT
"""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

spec = importlib.util.spec_from_file_location('depth', Path(__file__).with_name('polyphonic-depth.py'))
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
SEED = 452520
FIELDS = (('unmarked','tentative','asserted'), ('unmarked','pump','relay'), ('unmarked','inspect','hold'))
F = (*d.FREQ, np.arange(3)*100+2800, np.arange(3)*100+3300, np.arange(3)*100+3800)
B = [np.exp(-2j*np.pi*f[:,None]*np.arange(160,800)/d.RATE) for f in F]
MODES = ('serial','poly')

def encode(tree, qualifiers):
    rows = d.encode(tree)
    if len(qualifiers)!=len(rows) or any(len(q)!=3 or any(v not in range(3) for v in q) for q in qualifiers): raise ValueError('qualifiers')
    return [(*r,*q) for r,q in zip(rows,qualifiers)]

def decode(rows):
    if any(len(r)!=5 or any(v is None or v not in range(len(F[b])) for b,v in enumerate(r)) for r in rows): return None
    tree=d.decode([r[:2] for r in rows],'poly')
    return (tree,tuple(tuple(r[2:]) for r in rows)) if tree is not None else None

def render(rows,mode,phase=0.,gain=1.):
    blocks=[]
    for row in rows:
        tones=np.zeros((5,d.SLOT))
        for b,k in enumerate(row):
            if k is not None: tones[b,:d.ACTIVE]=d.AMP*d.W*np.sin(2*np.pi*F[b][k]*d.T+phase)* (gain if b==2 else 1.)
        blocks.extend(tones if mode=='serial' else [tones.sum(axis=0)])
    return np.concatenate(blocks)

def scores(x,b): return abs(x @ B[b].T)*2/640

def receive(pcm,mode,thresholds):
    n=5 if mode=='serial' else 1
    if len(pcm)==0 or len(pcm)%(d.SLOT*n): return []
    x=np.asarray(pcm).reshape(-1,d.SLOT)[:,160:800].astype(float)
    cols=[]
    for b in range(5):
        s=scores(x[b::5] if mode=='serial' else x,b); o=np.argsort(s,axis=1)
        cols.append([int(i[-1]) if v[i[-1]]>=thresholds[b] and v[i[-1]]-v[i[-2]]>=thresholds[b]/3 else None for v,i in zip(s,o)])
    return list(zip(*cols))

def pcm(x): return np.clip(np.rint(x),-32768,32767).astype('<i2')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def flat(rows): return tuple(r[:2] for r in rows),tuple(rows[0][2:]),tuple(tuple(sorted(r[b] for r in rows[1:])) for b in range(2,5))

def run(out):
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED)
    # Exhaustive scope census: ordered binary root, two atomic leaves, neutral root qualifiers.
    q=list(itertools.product(range(3),repeat=3)); buckets=Counter(); scoped=set()
    for op,a,b,u,v in itertools.product(d.BINARY,d.ATOMS,d.ATOMS,q,q):
        tree=(op,(a,),(b,)); rows=encode(tree,[(0,0,0),u,v]); key=tuple(rows)
        assert decode(rows)==(tree,((0,0,0),u,v)) and key not in scoped
        scoped.add(key); buckets[flat(rows)]+=1
    # Noise-only calibration and independent holdout, declared noise SD (not blind estimation).
    thresholds={}; calibration=[]
    for sd in (0,1000,3500):
        z=np.random.default_rng(SEED+sd+1).normal(0,sd,(4096,640)); h=np.random.default_rng(SEED+sd+2).normal(0,sd,(4096,640))
        thresholds[sd]=[max(80.,float(np.quantile(scores(z,b).max(axis=1),.999))) for b in range(5)]
        for policy,t in [('fixed',[720.]*5),('calibrated',thresholds[sd])]:
            accepted=[]
            for b in range(5):
                s=np.sort(scores(h,b),axis=1); accepted.append(int(np.sum((s[:,-1]>=t[b]) & (s[:,-1]-s[:,-2]>=t[b]/3))))
            calibration.append(dict(sd=sd,policy=policy,thresholds=t,holdout_slots_per_band=len(h),false_accepts=accepted))
    upstream=set(np.random.default_rng(452510).choice(len(d.catalogue()),96,replace=False)); audit=set(np.random.default_rng(4425401).choice(sorted(set(range(len(d.catalogue())))-upstream),192,replace=False))
    trees=d.catalogue(); picks=rng.choice(sorted(set(range(len(trees)))-upstream-audit),96,replace=False); traces=[]; gallery=[]
    for i,idx in enumerate(picks):
        tree=trees[int(idx)]; quals=tuple(tuple(int(v) for v in rng.integers(0,3,3)) for _ in d.encode(tree)); rows=encode(tree,quals); phase=float(rng.uniform(0,2*np.pi)); j=i%len(rows)
        ref=render(rows,'serial',phase); z=np.random.default_rng(SEED+i+10000).normal(size=(len(rows),5,d.SLOT))
        for mode,norm,condition in itertools.product(MODES,('energy','peak'),('clean','noise1000','noise3500','cue_loss','cue_change','weak_cue')):
            r=rows.copy(); sd=int(condition[5:]) if condition.startswith('noise') else 0
            if condition=='cue_loss': r[j]=(*r[j][:2],None,*r[j][3:])
            if condition=='cue_change': r[j]=(*r[j][:2],(r[j][2]+1)%3,*r[j][3:])
            full=render(rows,mode,phase); scale=np.linalg.norm(ref)/np.linalg.norm(full) if norm=='energy' else np.max(abs(ref))/np.max(abs(full))
            clean=pcm(render(r,mode,phase,.25 if condition=='weak_cue' else 1.)*scale)
            y=pcm(clean.astype(float)+sd*(z.reshape(-1) if mode=='serial' else z[:,0,:].reshape(-1)))
            for policy,t in [('fixed',[720.]*5),('calibrated',thresholds[sd])]:
                obs=receive(y,mode,t); got=decode(obs); status='withheld' if got is None else 'correct' if got==(tree,quals) else 'wrong'
                traces.append(dict(fixture=int(idx),tree=tree,qualifiers=quals,observed=obs,decoded=got,status=status,mode=mode,norm=norm,condition=condition,policy=policy,samples=len(y),energy=int(np.sum(clean.astype(np.int64)**2)),peak=int(np.max(abs(clean.astype(int)))),pcm_sha256=hashlib.sha256(y.tobytes()).hexdigest()))
            if i==0 and condition in ('clean','cue_loss','cue_change'):
                p=out/f'{mode}-{norm}-{condition}.wav'
                with wave.open(str(p),'wb') as w: w.setparams((1,2,d.RATE,0,'NONE','not compressed')); w.writeframes(y.tobytes())
                gallery.append(dict(file=p.name,sha256=sha(p),tree=tree,qualifiers=quals,ms=len(y)*1000/d.RATE))
    # Minimal contrast: qualifiers attach to different ordered operands, not a global mood.
    tree=('and',('fault',),('open',))
    qa=((0,0,0),(1,1,1),(2,2,2)); qb=(qa[0],qa[2],qa[1])
    assert flat(encode(tree,qa))==flat(encode(tree,qb))
    for name,qs in [('scope-a',qa),('scope-b',qb)]:
        for mode in MODES:
            y=pcm(render(encode(tree,qs),mode)); assert decode(receive(y,mode,[720.]*5))==(tree,qs)
            p=out/f'{name}-{mode}.wav'
            with wave.open(str(p),'wb') as w: w.setparams((1,2,d.RATE,0,'NONE','not compressed')); w.writeframes(y.tobytes())
            gallery.append(dict(file=p.name,sha256=sha(p),tree=tree,qualifiers=qs,ms=len(y)*1000/d.RATE))
    groups=[]
    for key in itertools.product(MODES,('energy','peak'),('clean','noise1000','noise3500','cue_loss','cue_change','weak_cue'),('fixed','calibrated')):
        r=[t for t in traces if tuple(t[k] for k in ('mode','norm','condition','policy'))==key]; assert len(r)==96
        groups.append(dict(zip(('mode','norm','condition','policy'),key),counts=dict(Counter(t['status'] for t in r)),energy=sum(t['energy'] for t in r),peak=max(t['peak'] for t in r),samples=sum(t['samples'] for t in r)))
    receipt=dict(schema='mhac-epistemic-morphology-v1',seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=sha(Path(__file__)),fields=FIELDS,scoped=len(scoped),flat_distinct=len(buckets),flat_multiplicity=dict(Counter(buckets.values())),calibration=calibration,groups=groups,pcm_frames=len(traces)//2,decisions=len(traces),gallery=gallery,limits='Synthetic aligned slots; known mode and noise SD; ordered binary scope census only; qualifiers are arbitrary conventions, no human evidence or action authority. Equal digital energy or peak separately, not loudness or bandwidth. Noise-only slot false acceptance is not message false acceptance. Cue change is a valid replacement tone.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces))
    (out/'index.html').write_text('<!doctype html><meta charset=utf-8><title>Scoped acoustic morphology</title><h1>Scoped acoustic morphology</h1><p>Synthetic fixtures. Start at low volume. No human validation.</p>'+''.join(f'<p>{g["file"]} / {g["ms"]} ms<br><audio controls preload="none" src="{g["file"]}"></audio></p>' for g in gallery)+'<p><a href="receipt.json">Receipt and scope census</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(Path(sys.argv[1]))
