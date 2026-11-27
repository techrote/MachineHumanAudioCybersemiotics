"""Refs #452/#453; synthetic aligned PCM, no human evidence or action authority.
Parent 20986659fa9de8c9f63740a9b9d5704f432bc6b7. Run: python dual-morphology.py OUTPUT
Observatory drift audit 8dfade66fe75b63fc4967a36260a30328aff15f4 motivates future calibration; not a dependency.
"""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location('hybrid',Path(__file__).with_name('hybrid-morphology.py'))
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h); m=h.m; d=h.d
SEED=452540
LAYOUTS={'check3':((0,1),(2,3),(4,5)), 'dual3':((0,1,5),(2,3),(4,6)), 'dual2':((0,1,5,6),(2,3,4))}
F=(*m.F,np.arange(5)*100+4300,np.arange(5)*100+5000)
B=[np.exp(-2j*np.pi*f[:,None]*np.arange(160,800)/d.RATE) for f in F]
Q=list(itertools.product(range(3),repeat=3))

def code(q,mode):
    e,s,a=q
    return (*q,(e+s+a)%3) if mode=='check3' else (*q,(e+s+a)%5,(e+2*s+3*a)%5)

BOOK={k:[code(q,k) for q in Q] for k in LAYOUTS}

def repair(obs,mode,correct=False):
    """Return codeword plus evidence labels, or None; correction only with no erasures."""
    caps=(3,3,3,3) if mode=='check3' else (3,3,3,5,5)
    if len(obs)!=len(caps) or any(v is not None and v not in range(c) for v,c in zip(obs,caps)): return None
    missing=obs.count(None)
    if missing>(1 if mode=='check3' else 2): return None
    radius=int(correct and mode!='check3' and not missing)
    candidates=[w for w in BOOK[mode] if sum(v is not None and v!=u for v,u in zip(obs,w))<=radius]
    if len(candidates)!=1: return None
    w=candidates[0]; return w,tuple('inferred' if v is None else 'corrected' if v!=u else 'observed' for v,u in zip(obs,w))

def decode(rows,mode,correct=False):
    decoded=[]; evidence=[]
    for row in rows:
        if len(row)!=sum(map(len,LAYOUTS[mode])) or any(v is None or v not in range(len(F[b])) for b,v in enumerate(row[:2])): return None
        r=repair(tuple(row[2:]),mode,correct)
        if r is None: return None
        w,labels=r; decoded.append((*row[:2],*w[:3])); evidence.append(('observed','observed',*labels[:3]))
    meaning=m.decode(decoded)
    return (meaning,evidence) if meaning is not None else None

def render(rows,mode,phase):
    blocks=[]
    for row in rows:
        for group in LAYOUTS[mode]:
            x=np.zeros(d.SLOT)
            for b in group:
                if row[b] is not None: x[:d.ACTIVE]+=d.AMP*d.W*np.sin(2*np.pi*F[b][row[b]]*d.T+phase)
            blocks.append(x)
    return np.concatenate(blocks)

def receive(y,mode,t):
    groups=LAYOUTS[mode]; n=len(groups)
    if not len(y) or len(y)%(n*d.SLOT): return []
    x=np.asarray(y).reshape(-1,d.SLOT)[:,160:800].astype(float); cols={}
    for j,g in enumerate(groups):
        for b in g:
            bank=h.B[b] if mode=='check3' else B[b]; s=abs(x[j::n]@bank.T)*2/640; o=np.argsort(s,axis=1)
            cols[b]=[int(i[-1]) if v[i[-1]]>=t[b] and v[i[-1]]-v[i[-2]]>=t[b]/3 else None for v,i in zip(s,o)]
    return list(zip(*(cols[b] for b in sorted(cols))))

def census(mode,correct):
    book=BOOK[mode]; caps=(3,)*4 if mode=='check3' else (3,3,3,5,5); counts=Counter(); witnesses={}
    distance=min(sum(a!=b for a,b in zip(x,y)) for x,y in itertools.combinations(book,2))
    for w in book:
        for er,sub in ((0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,1),(2,1),(0,3)):
            for ee in itertools.combinations(range(len(w)),er):
                for ss in itertools.combinations([i for i in range(len(w)) if i not in ee],sub):
                    for vals in itertools.product(*[[v for v in range(caps[i]) if v!=w[i]] for i in ss]):
                        x=list(w)
                        for i in ee: x[i]=None
                        for i,v in zip(ss,vals): x[i]=v
                        got=repair(tuple(x),mode,correct); status='withheld' if got is None else 'correct' if got[0]==w else 'wrong'; key=f'{er}e-{sub}s-{status}'; counts[key]+=1
                        if status=='wrong': witnesses.setdefault(key,dict(sent=w,received=x,decoded=got[0],labels=got[1]))
    return dict(distance=distance,counts=dict(counts),wrong_witnesses=witnesses)

def run(out):
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED); symbolic={k:census('check3' if k=='single' else 'dual3',k=='correct') for k in ('single','strict','correct')}
    assert symbolic['strict']['distance']==3 and symbolic['single']['distance']==2
    assert symbolic['strict']['counts']['2e-0s-correct']==270 and symbolic['correct']['counts']['0e-1s-correct']==378
    thresholds={}; baseline_thresholds={}
    for sd in (0,1000,3500):
        z=np.random.default_rng(SEED+sd).normal(0,sd,(4096,640)); thresholds[sd]=[max(80.,float(np.quantile((abs(z@b.T)*2/640).max(axis=1),.999))) for b in B]; baseline_thresholds[sd]=[max(80.,float(np.quantile((abs(z@b.T)*2/640).max(axis=1),.999))) for b in h.B]
    trees=d.catalogue(); u=set(range(len(trees))); prev=set(np.random.default_rng(452510).choice(len(trees),96,replace=False)); audit=set(np.random.default_rng(4425401).choice(sorted(u-prev),192,replace=False)); prior=set(np.random.default_rng(452520).choice(sorted(u-prev-audit),96,replace=False)); hybrid=set(np.random.default_rng(452530).choice(sorted(u-prev-audit-prior),64,replace=False)); picks=rng.choice(sorted(u-prev-audit-prior-hybrid),64,replace=False)
    traces=[]; gallery=[]; conditions=('clean','noise1000','noise3500','two_erase','one_replace','two_replace','mixed','qualifier_slot','last_slot','lexical_slot','two_erase_noise1000')
    for i,idx in enumerate(picks):
        tree=trees[int(idx)]; quals=tuple(tuple(map(int,rng.integers(0,3,3))) for _ in d.encode(tree)); base=m.encode(tree,quals); phase=float(rng.uniform(0,2*np.pi)); j=i%len(base); ref=h.render(base,'serial',phase); noise=np.random.default_rng(SEED+10000+i).normal(size=(len(base),3,d.SLOT))
        for mode,cond in itertools.product(LAYOUTS,conditions):
            rows=[(*r[:2],*code(r[2:],mode)) for r in base]; clean0=render(rows,mode,phase); scale=np.max(abs(ref))/np.max(abs(clean0)); r=list(rows[j]); n=len(LAYOUTS[mode]); sd=3500 if cond=='noise3500' else 1000 if cond.endswith('1000') else 0
            if cond.startswith('two_erase'): r[2]=r[3]=None
            if cond in ('one_replace','two_replace','mixed'): r[2]=(r[2]+1)%3
            if cond=='two_replace': r[3]=(r[3]+2)%3
            if cond=='mixed': r[3]=None
            if cond.endswith('_slot'):
                group=LAYOUTS[mode][0 if cond=='lexical_slot' else 1 if cond=='qualifier_slot' else -1]
                for b in group: r[b]=None
            rows[j]=tuple(r); clean=m.pcm(render(rows,mode,phase)*scale); y=m.pcm(clean.astype(float)+sd*noise[:,:n,:].reshape(-1)); obs=receive(y,mode,(baseline_thresholds if mode=='check3' else thresholds)[sd]); policies=('strict',) if mode=='check3' else ('strict','correct')
            for policy in policies:
                got=decode(obs,mode,policy=='correct'); status='withheld' if got is None else 'correct' if got[0]==(tree,quals) else 'wrong'
                traces.append(dict(fixture=int(idx),tree=tree,qualifiers=quals,mode=mode,condition=cond,policy=policy,observed=obs,decoded=got,status=status,samples=len(y),peak=int(np.max(abs(clean.astype(int)))),energy=int(np.sum(clean.astype(np.int64)**2)),pcm_sha256=hashlib.sha256(y.tobytes()).hexdigest()))
            if i==0 and cond in ('clean','two_erase','two_replace','qualifier_slot','last_slot'):
                p=out/f'{mode}-{cond}.wav'
                with wave.open(str(p),'wb') as w: w.setparams((1,2,d.RATE,0,'NONE','not compressed')); w.writeframes(y.tobytes())
                gallery.append(dict(file=p.name,ms=len(y)*1000/d.RATE))
    groups=[]
    for mode,cond in itertools.product(LAYOUTS,conditions):
        for policy in ('strict',) if mode=='check3' else ('strict','correct'):
            r=[t for t in traces if (t['mode'],t['condition'],t['policy'])==(mode,cond,policy)]; assert len(r)==64
            groups.append(dict(mode=mode,condition=cond,policy=policy,counts=dict(Counter(t['status'] for t in r)),samples=sum(t['samples'] for t in r),energy=sum(t['energy'] for t in r),peak=max(t['peak'] for t in r)))
    assert all(t['status']=='correct' for t in traces if t['condition']=='clean')
    receipt=dict(schema='mhac-dual-morphology-v1',seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=m.sha(Path(__file__)),layouts=LAYOUTS,thresholds=thresholds,baseline_thresholds=baseline_thresholds,symbolic=symbolic,pcm_trials=64*len(LAYOUTS)*len(conditions),decisions=len(traces),groups=groups,gallery=gallery,limits='Known aligned slots and noise SD; peak matched before faults, not energy or loudness matched. Dual GF5 checks protect only qualifiers, not lexical/depth or truth. Strict refuses substitutions within distance two, correction can miscorrect two substitutions. Evidence labels describe decoder operations, not ground truth. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces))
    (out/'index.html').write_text('<!doctype html><meta charset=utf-8><title>Dual morphology</title><h1>Dual morphology</h1><p>Synthetic specimens; start at low volume. No human evidence.</p>'+''.join(f'<p>{g["file"]} / {g["ms"]} ms<br><audio controls preload="none" src="{g["file"]}"></audio></p>' for g in gallery)+'<p><a href="receipt.json">Results</a> | <a href="traces.jsonl">Evidence traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:m.sha(p) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(Path(sys.argv[1]))
