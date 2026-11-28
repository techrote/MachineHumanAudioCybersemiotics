"""#452 / #453. Relational motif grammar, synthetic PCM only. Known node boundaries.
Pinned polyphonic-depth.py: a012850105079a077848e29414ea8efef760c264,
Git blob 2715c38cf4d7dd2727d161a8020a46078d72b690.
"""
import hashlib, importlib.util, itertools, json, sys, wave, html
from collections import Counter
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('depth',Path(__file__).with_name('polyphonic-depth.py'))
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
RATE=16000; SLOT=3840; N=960; AMP=1600; SEED=452600
START=np.array([1280,1792,2304,2816]); T=np.arange(N)/RATE
ENV=np.minimum(1,np.minimum(np.arange(N),np.arange(N)[::-1])/96)
TARGET=600*2**(np.arange(13)/12); REF=500.; FFT=8192
MODES=('absolute','relational','relational_prefix','shared_anchor')
CONDITIONS=('clean','shift_minus2','shift_plus2','shift_plus5','random_local_shift','noise1000','noise3500','anchor_loss','target_loss','depth_shift','node_delete','anchor_detune','target_substitute','shift_anchor_loss','local_shift_anchor_loss','all_anchor_detune')

def render(rows, shifts=None, phase=0., erase=None, detune=None, depth_shift=None):
    """Generate independent node-local motifs, with optional constructed faults."""
    x=np.zeros((len(rows),SLOT)); shifts=[0.]*len(rows) if shifts is None else shifts
    for i,(k,dep) in enumerate(rows):
        for b,(start,f) in enumerate(((0,REF),(int(START[dep if depth_shift is None or i!=depth_shift[0] else depth_shift[1]]),TARGET[k]))):
            if erase==(i,b): continue
            s=shifts[i]+(detune[2] if detune is not None and detune[:2]==(i,b) else 0)
            x[i,start:start+N]=AMP*ENV*np.sin(2*np.pi*f*2**(s/12)*T+phase)
    return x.reshape(-1)

def peak(seg):
    """Peak interpolation, fixed amplitude threshold and known search band."""
    z=np.abs(np.fft.rfft(seg*np.hanning(N),n=FFT))*2/np.hanning(N).sum()
    lo,hi=int(250*FFT/RATE),int(2100*FFT/RATE)
    k=int(np.argmax(z[lo:hi])+lo); a,b,c=np.log(np.maximum(z[k-1:k+2],1e-10)); den=a-2*b+c
    off=.5*(a-c)/den if abs(den)>1e-12 else 0.
    return (k+off)*RATE/FFT, float(z[k])

def observe(pcm):
    if not len(pcm) or len(pcm)%SLOT: return []
    observations=[]
    for x in np.asarray(pcm,dtype=float).reshape(-1,SLOT):
        anchor,amp=peak(x[:N]); candidates=[peak(x[s:s+N]) for s in START]
        order=sorted(range(4),key=lambda i:candidates[i][1],reverse=True); best,second=order[:2]; target,level=candidates[best]
        dep=best if level>=600 and level-candidates[second][1]>=180 else None
        observations.append(dict(anchor=anchor if amp>=600 else None,target=target if level>=600 else None,depth=dep,anchor_level=amp,target_level=level,depth_margin=level-candidates[second][1]))
    return observations

def decode(obs,mode):
    rows=[]
    shared=None
    if mode=='shared_anchor':
        anchors=[o['anchor'] for o in obs if o['anchor'] is not None]
        if not anchors or (len(anchors)<len(obs) and len(anchors)<2): return None
        if 12*np.log2(max(anchors)/min(anchors))>.4: return None
        shared=float(np.median(anchors))
    for o in obs:
        target,anchor=o['target'],shared if mode=='shared_anchor' else o['anchor']; dep=o['depth']; k=None
        if target is not None and (mode=='absolute' or anchor is not None):
            f=target if mode=='absolute' else target*REF/anchor
            v=12*np.log2(f/600); j=round(v)
            if 0<=j<13 and abs(v-j)<=.40: k=int(j)
        rows.append((k,dep))
    return d.decode(rows,'prefix' if mode=='relational_prefix' else 'poly')

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    rng=np.random.default_rng(SEED); trees=d.catalogue(); seen=set(); census=Counter(); traces=[]; specimens=[]
    for tree in trees:
        rows=d.encode(tree); key=tuple(rows); assert key not in seen and d.decode(rows,'poly')==tree; seen.add(key)
        for j in range(len(rows)):
            for mode in ('prefix','poly'):
                got=d.decode(rows[:j]+rows[j+1:],mode); census[mode+'_'+d.classify(got,tree)]+=1
    # Explicit balanced size cohort; excludes Run 051's 96 tree indices.
    old=set(np.random.default_rng(452510).choice(len(trees),96,replace=False)); picks=[]
    for n in range(1,5):
        ids=[i for i,t in enumerate(trees) if len(d.encode(t))==n and i not in old]
        picks.extend(map(int,rng.choice(ids,min(32,len(ids)),replace=False)))
    for i,idx in enumerate(picks):
        tree=trees[idx]; orig=d.encode(tree); j=i%len(orig); k,dep=orig[j]; phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=len(orig)*SLOT)
        for condition in CONDITIONS:
            rows=orig.copy(); shifts=[0.]*len(rows); erase=detune=ds=None; sd=0
            if condition in ('shift_minus2','shift_plus2','shift_plus5'): shifts=[{'shift_minus2':-2,'shift_plus2':2,'shift_plus5':5}[condition]]*len(rows)
            if condition in ('random_local_shift','local_shift_anchor_loss'): shifts=list(rng.uniform(-3,3,len(rows)))
            if condition.startswith('noise'): sd=int(condition[5:])
            if condition in ('anchor_loss','shift_anchor_loss','local_shift_anchor_loss'): erase=(j,0)
            if condition=='shift_anchor_loss': shifts=[2.]*len(rows)
            if condition=='target_loss': erase=(j,1)
            if condition=='depth_shift': ds=(j,(dep+1)%4)
            if condition=='node_delete': rows.pop(j); shifts.pop(j)
            if condition=='anchor_detune': detune=(j,0,1)
            if condition=='target_substitute': detune=(j,1,1 if k<12 else -1)
            x=render(rows,shifts,phase,erase,detune,ds)
            if condition=='all_anchor_detune':
                for a in range(len(rows)): x[a*SLOT:a*SLOT+N]=AMP*ENV*np.sin(2*np.pi*REF*2**(1/12)*T+phase)
            pcm=np.clip(np.rint(x+sd*z[:len(x)]),-32768,32767).astype('<i2'); obs=observe(pcm)
            results={m:dict(decoded=decode(obs,m),status=d.classify(decode(obs,m),tree),inferred_anchor_indices=[a for a,o in enumerate(obs) if o['anchor'] is None] if m=='shared_anchor' and decode(obs,m) is not None else []) for m in MODES}
            traces.append(dict(index=idx,tree=tree,condition=condition,observations=obs,results=results,sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),samples=len(pcm),peak=int(np.max(np.abs(pcm.astype(int)))) if len(pcm) else 0))
            if i==len(picks)-1 and len(pcm):
                fn=condition+'.wav'; w=wave.open(str(out/fn),'wb'); w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(pcm.tobytes()); w.close(); specimens.append((fn,tree,results))
    # Explicit grammatical contrasts, identical timbre and no performed affect.
    contrasts=[('not',('quote',('fault',))),('quote',('not',('fault',))),('if',('fault',),('open',)),('if',('open',),('fault',))]
    contrast_results=[]
    for i,tree in enumerate(contrasts):
        pcm=np.rint(render(d.encode(tree))).astype('<i2'); obs=observe(pcm)
        results={m:dict(decoded=decode(obs,m),status=d.classify(decode(obs,m),tree)) for m in MODES}
        assert all(r['status']=='correct' for r in results.values())
        fn=f'contrast-{i+1}.wav'; w=wave.open(str(out/fn),'wb'); w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(pcm.tobytes()); w.close(); specimens.append((fn,tree,results))
        contrast_results.append(dict(file=fn,tree=tree,results=results))
    summary={c:{m:dict(Counter(t['results'][m]['status'] for t in traces if t['condition']==c)) for m in MODES} for c in CONDITIONS}
    receipt=dict(seed=SEED,python=sys.version.split()[0],numpy=np.__version__,catalogue=len(seen),deletion_census=census,cohort=picks,cohort_by_size=dict(Counter(len(d.encode(trees[i])) for i in picks)),signals=len(traces),decisions=len(traces)*len(MODES),summary=summary,contrasts=contrast_results,limitations=['known node alignment','fixed threshold','digital additive noise only','unvalidated arbitrary acoustic conventions','same PCM for all decoders','no physical or human tests'])
    for name,obj in [('receipt',receipt),('traces',traces)]: (out/(name+'.json')).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Relational motifs</title><h1>Relational motifs: original synthetic specimens</h1><p>Opt-in playback; begin at low volume. No human evidence.</p>'+''.join(f'<h2>{html.escape(fn)}</h2><pre>{html.escape(str(tree))}\n{html.escape(str({m:r["status"] for m,r in results.items()}))}</pre><audio controls preload="none" src="{fn}"></audio>' for fn,tree,results in specimens))
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(sys.argv[1])
