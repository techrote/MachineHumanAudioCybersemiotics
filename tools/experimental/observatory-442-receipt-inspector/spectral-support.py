"""Refs #442/#443. Exploratory matched search calibration; synthetic aligned PCM only."""
import hashlib, importlib.util, itertools, json, sys
from collections import Counter
from pathlib import Path
import numpy as np

PARENT='ec34589b78a5b75e8aedb91ab16547a14c88e5fe'
SEED=4425901
N=1024
POLICIES=('global','local','wide')
base=Path(__file__).with_name('matched-calibration.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='b1fc7bd91941e10a70bb600b7558fb9b7a3c8bae59b96982ee2fac7c0057fce2'
spec=importlib.util.spec_from_file_location('matched',base)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); b=m.b
# Add orthogonal quarter-spacing reference bins around each band, at each offset.
REF=[np.array([f for f in range(int(v[0])-75,int(v[-1])+76,25) if f not in v]) for v in b.F]
HZ=sorted({int(f+h) for v in REF for f in v for h in b.GRID})
BANK=np.exp(-2j*np.pi*np.array(HZ)[:,None]*b.T)
IX={f:i for i,f in enumerate(HZ)}
RI=[np.array([[IX[int(f+h)] for f in v] for h in b.GRID]) for v in REF]

def features(x):
    s=b.spectra(x); w=abs(x@BANK.T)*2/640
    joint=[]; den=[]
    for band in range(7):
        j,g,l=m.scores(s,band)
        joint.append(j); den.append(np.stack((g,l,np.median(w[...,RI[band]],axis=-1)),axis=-1))
    return s,np.stack(joint,axis=-1),np.stack(den,axis=-2)

def mix(z,a):
    v=(1-a)**.5*z+a**.5*b.noise(z,'colored')
    return v/np.sqrt(np.mean(v*v,axis=-1,keepdims=True))

def null(seed,weights):
    rng=np.random.default_rng(seed); result={}
    for a in weights:
        _,j,d=features(mix(rng.normal(size=(N,640)),a))
        result[a]=(j[...,None]/np.maximum(d,1e-12)).max(axis=1)
    return result

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    train=null(SEED+1,(0,.5,1)); hold=null(SEED+2,(0,.25,.75,1))
    t=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0)
    audit=[dict(mix=a,band=k,policy=p,n=N,exceed=int((v[:,k,i]>=t[k,i]).sum())) for a,v in hold.items() for k in range(7) for i,p in enumerate(POLICIES)]
    rng=np.random.default_rng(SEED); traces=[]
    conds={'clean':(0,0,0),'white':(25,1000,0),'mix25':(27,1000,.25),'mix75':(27,1000,.75),'colored':(25,1000,1),'absent':(27,1000,.75),'replace2':(25,1000,0)}
    for i,q in enumerate(b.Q*2):
        row=(int(rng.integers(4)),0,*q); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,b.d.SLOT))
        for mode,(cond,(shift,sd,a)) in itertools.product(b.LAY,conds.items()):
            expected=(*row[:2],*b.code(q,mode)); x=b.render(expected,mode,shift,phase); scale=b.d.AMP/np.max(abs(x)); changed=list(expected)
            if cond=='replace2': changed[2]=(changed[2]+1)%3; changed[3]=(changed[3]+2)%3
            signal=b.render(changed,mode,shift,phase)*scale
            if cond=='absent': signal[:]=0
            y=b.d.pcm(signal+sd*mix(z,a)); s,j,d=features(y[:,160:800].astype(float))
            slots=[next(i for i,g in enumerate(b.LAY[mode]) if k in g) for k in range(len(expected))]
            h=int(np.argmax(sum(s[slot,b.FI[k]].max(axis=-1) for k,slot in enumerate(slots))))
            for pi,p in enumerate(POLICIES):
                obs=[int(np.argmax(s[slot,b.FI[k][h]])) if j[slot,h,k]>=max(80,t[k,pi]*d[slot,h,k,pi]) else None for k,slot in enumerate(slots)]
                got=b.repair(tuple(obs[2:]),mode) if obs[0] is not None and obs[0]<4 and obs[1]==0 else None
                status='withheld' if got is None else 'correct' if cond!='absent' and obs[:2]==list(row[:2]) and got[0][:3]==q else 'wrong'
                traces.append(dict(fixture=i,mode=mode,condition=cond,policy=p,expected=expected,observed=obs,decoded=got,status=status,offset=int(b.GRID[h]),joint=[float(j[slot,h,k]) for k,slot in enumerate(slots)],background=[float(d[slot,h,k,pi]) for k,slot in enumerate(slots)],pcm_sha256=b.sha(y.tobytes())))
    groups=[]
    for mode,cond,p in itertools.product(b.LAY,conds,POLICIES):
        rows=[r for r in traces if (r['mode'],r['condition'],r['policy'])==(mode,cond,p)]
        assert len(rows)==54
        groups.append(dict(mode=mode,condition=cond,policy=p,counts=dict(Counter(r['status'] for r in rows))))
    receipt=dict(parent=PARENT,grammar=b.PIN,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=b.sha(Path(__file__).read_bytes()),conditions=conds,reference_counts=[len(v) for v in REF],thresholds=t.tolist(),null_audit=audit,groups=groups,pcm_trials=len(traces)//3,decisions=len(traces),limits='Known slots and layout; strict qualifier repair; single leaf; matched pre-fault peak; mixture is correlated filtered/unfiltered same draw, normalized RMS, not independent power mixture. Null target is per-band search envelope, not message error. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces))
    html='<!doctype html><meta charset=utf-8><title>Spectral support</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto}td,th{padding:.4em;border-bottom:1px solid #aaa}</style><h1>Spectral reference support</h1><p>Synthetic single-leaf PCM. Null exceedances are per-band, not message risk.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in conds)+'</select></label><table><thead><tr><th>Layout</th><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th></tr></thead><tbody id="r"></tbody></table><h2>Noise-only holdout</h2><table><thead><tr><th>Mix</th><th>Band</th><th>Policy</th><th>Exceedances</th><th>N</th></tr></thead><tbody id="a"></tbody></table><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+',audit='+json.dumps(audit)+';function row(v){const t=document.createElement("tr");for(const x of v){const e=document.createElement("td");e.textContent=x;t.append(e)}return t}function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>row([x.mode,x.policy,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0])))}a.replaceChildren(...audit.map(x=>row([x.mix,x.band,x.policy,x.exceed,x.n])));c.onchange=draw;draw()</script>'
    (out/'index.html').write_text(html)
    (out/'manifest.json').write_text(json.dumps({p.name:b.sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(receipt['pcm_trials'],receipt['decisions'])

if __name__=='__main__': run(Path(sys.argv[1]))
