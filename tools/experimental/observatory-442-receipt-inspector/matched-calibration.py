"""Refs #442/#443. Matched search-envelope calibration, synthetic PCM only."""
import hashlib, importlib.util, itertools, json, sys
from collections import Counter
from pathlib import Path
import numpy as np

PARENT='bc72cd64f36441f2d806b579fd76ffdd02879173'
SEED=4425801
base=Path(__file__).with_name('band-local-audit.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='9f7d2bea4fe07c1092d42d3c126ef68b581ea381f73e8a8672ed3a595d4a969f'
spec=importlib.util.spec_from_file_location('band',base)
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
N=2048
Q=.99
POLICIES=('old-global','old-local','matched-global','matched-local')

def scores(s,band):
    v=s[...,b.FI[band]]
    a=np.sort(v,axis=-1)
    joint=np.minimum(a[...,-1],3*(a[...,-1]-a[...,-2]))
    g=np.median(s[...,b.GI],axis=-1)*np.sqrt(640/(4*np.log(2)))
    l=np.median(s[...,b.LI[band]],axis=-1)
    return joint, g, l

def envelope(seed):
    z=np.random.default_rng(seed).normal(size=(N,640))
    result={}
    for family in ('white','colored'):
        s=b.spectra(b.noise(z,family))
        for band in range(7):
            joint,g,l=scores(s,band)
            for name,den in [('global',g),('local',l)]:
                result[family,band,name]=(joint/np.maximum(den,1e-12)).max(axis=-1)
    return result

def calibrate():
    train=envelope(SEED+1); hold=envelope(SEED+2)
    thresholds={}; audit=[]
    for band,name in itertools.product(range(7),('global','local')):
        t=max(float(np.quantile(train[f,band,name],Q,method='higher')) for f in ('white','colored'))
        thresholds[band,name]=t
        for f in ('white','colored'):
            audit.append(dict(band=band,estimator=name,family=f,threshold=t,exceed=int(np.sum(hold[f,band,name]>=t)),n=N))
    return thresholds,audit

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    t,audit=calibrate(); k,l=b.calibrate(); rng=np.random.default_rng(SEED)
    traces=[]
    for i,q in enumerate(b.Q*4):
        row=(int(rng.integers(4)),0,*q); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,b.d.SLOT))
        for mode,(cond,(shift,sd,kind)) in itertools.product(b.LAY,b.CONDS.items()):
            expected=(*row[:2],*b.code(q,mode)); x=b.render(expected,mode,shift,phase); scale=b.d.AMP/np.max(abs(x)); changed=list(expected)
            if cond=='erase2': changed[2]=changed[3]=None
            if cond.startswith('replace'): changed[2]=(changed[2]+1)%3
            if cond=='replace2': changed[3]=(changed[3]+2)%3
            signal=b.render(changed,mode,shift,phase)*scale
            if cond.startswith('absent'): signal[:]=0
            y=b.d.pcm(signal+sd*b.noise(z,kind)); obs,h,e=b.observe(y,mode,k,l)
            # Same selected offset, bins, symbol winners, 80-count floor and margin rule.
            s=b.spectra(y[:,160:800].astype(float)); hi=list(b.GRID).index(h)
            for name,di in [('global',2),('local',3)]:
                values=[]
                for band,m in enumerate(e):
                    j=next(j for j,g in enumerate(b.LAY[mode]) if band in g)
                    limit=max(80,t[band,name]*m[di])
                    values.append(int(np.argmax(s[j,b.FI[band][hi]])) if min(m[0],3*m[1])>=limit else None)
                obs['matched-'+name]=values
            for p,v in obs.items():
                p='old-'+p if p in ('global','local') else p
                got=b.repair(tuple(v[2:]),mode) if v[0] is not None and v[0]<4 and v[1]==0 else None
                status='withheld' if got is None else 'correct' if not cond.startswith('absent') and v[:2]==list(row[:2]) and got[0][:3]==q else 'wrong'
                traces.append(dict(fixture=i,phase=phase,mode=mode,condition=cond,policy=p,expected=expected,observed=v,decoded=got,status=status,offset=h,metrics=e,pcm_sha256=b.sha(y.tobytes())))
    groups=[]
    for mode,cond,p in itertools.product(b.LAY,b.CONDS,POLICIES):
        rows=[r for r in traces if (r['mode'],r['condition'],r['policy'])==(mode,cond,p)]
        assert len(rows)==108
        groups.append(dict(mode=mode,condition=cond,policy=p,counts=dict(Counter(r['status'] for r in rows))))
    assert len(traces)==108*2*len(b.CONDS)*4
    receipt=dict(parent=PARENT,grammar=b.PIN,grammar_blob=b.BLOB,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=b.sha(Path(__file__).read_bytes()),conditions=b.CONDS,quantile=Q,windows_per_family_per_split=N,null_audit=audit,groups=groups,pcm_trials=len(traces)//4,decisions=len(traces),limits='Noise-only per-band search-envelope target, not message false acceptance or selected-offset probability. Shared draws across noise families and paired policies. Strict repair, known slots/layout, single leaf, pre-fault matched peak; no human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces))
    html='<!doctype html><meta charset=utf-8><title>Matched calibration</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto}td,th{padding:.5em;border-bottom:1px solid #aaa}</style><h1>Matched search-envelope calibration</h1><p>Single-node synthetic PCM; 108 cases per condition. Null exceedance is per band, not message risk.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in b.CONDS)+'</select></label><table><thead><tr><th>Layout</th><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th></tr></thead><tbody id="r"></tbody></table><h2>Independent noise-only holdout</h2><table><thead><tr><th>Band</th><th>Estimator</th><th>Family</th><th>Exceedances</th><th>Windows</th></tr></thead><tbody id="a"></tbody></table><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+',audit='+json.dumps(audit)+';function row(v){const t=document.createElement("tr");for(const x of v){const e=document.createElement("td");e.textContent=x;t.append(e)}return t}function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>row([x.mode,x.policy,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0])))}a.replaceChildren(...audit.map(x=>row([x.band,x.estimator,x.family,x.exceed,x.n])));c.onchange=draw;draw()</script>'
    (out/'index.html').write_text(html)
    (out/'manifest.json').write_text(json.dumps({p.name:b.sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(receipt['pcm_trials'],receipt['decisions'])

if __name__=='__main__': run(Path(sys.argv[1]))
