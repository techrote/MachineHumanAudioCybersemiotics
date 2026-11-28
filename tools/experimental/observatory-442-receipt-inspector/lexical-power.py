"""Refs #442/#443. Synthetic matched-peak lexical allocation; no human evidence."""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np
PARENT='bdbef882c11b65e1d1bcbf9b9d8bf02c279b9257'
SEED=4426101
WEIGHTS=(1.,1.5,2.,3.)
CONDS={'clean':(0,0,0),'white':(25,1000,0),'offgrid':(27,1000,0),'mix25':(27,1000,.25),'mix75':(27,1000,.75),'colored':(25,1000,1),'absent':(27,1000,.75),'replace2':(27,1000,0)}
base=Path(__file__).with_name('leakage-audit.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='5da5770883bd43ff68a3901840b359de14681225ec295bc9ac29e4712e74c039'
spec=importlib.util.spec_from_file_location('leak',base)
l=importlib.util.module_from_spec(spec); spec.loader.exec_module(l); b=l.b

def render(row,mode,shift,phase,weight):
    return b.render(row,mode,shift,phase)+(weight-1)*b.render((row[0],*([None]*(len(row)-1))),mode,shift,phase)

def status(r):
    got=r['decoded']; obs=r['observed']; exp=r['expected']
    return 'withheld' if got is None else 'correct' if r['condition']!='absent' and list(obs[:2])==list(exp[:2]) and list(got[0][:3])==list(exp[2:5]) else 'wrong'

def run(out):
    out.mkdir(parents=True,exist_ok=False); thresholds={}; rng=np.random.default_rng(SEED); traces=[]; gallery=[]
    for mode in b.LAY:
        train=l.null(l.SEED+1,(0,.5,1),mode)
        thresholds[mode]=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0)[:,0].tolist()
    for i,q in enumerate(b.Q*2):
        row=(int(rng.integers(4)),0,*q); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,b.d.SLOT))
        for mode,(cond,(shift,sd,mix)) in itertools.product(b.LAY,CONDS.items()):
            expected=(*row[:2],*b.code(q,mode)); changed=list(expected)
            if cond=='replace2': changed[2]=(changed[2]+1)%3; changed[3]=(changed[3]+2)%3
            noise=sd*l.a.mix(z,mix)
            for weight in WEIGHTS:
                x=render(expected,mode,shift,phase,weight); scale=b.d.AMP/np.max(abs(x)); x=x*scale
                signal=render(changed,mode,shift,phase,weight)*scale
                if cond=='absent': signal[:]=0
                y=b.d.pcm(signal+noise); win,j,d,h=l.measure(y[:,160:800].astype(float),mode)
                obs=[v if j[k]>=max(80,thresholds[mode][k]*d[k,0]) else None for k,v in enumerate(win)]
                got=b.repair(tuple(obs[2:]),mode) if obs[0] is not None and obs[0]<4 and obs[1]==0 else None
                r=dict(fixture=i,mode=mode,condition=cond,weight=weight,expected=expected,observed=obs,decoded=got,offset=h,joint=j.tolist(),background=d[:,0].tolist(),peak=float(np.max(abs(x))),energy=float(np.sum(x*x)),scale=float(scale),phase=phase,pcm_sha256=b.sha(y.tobytes()),noise_sha256=b.sha(noise.astype('<f8').tobytes()))
                r['status']=status(r); traces.append(r)
                if i==0 and cond in ('clean','white') and weight in (1.,2.):
                    name=f'{mode}-{cond}-{weight}.wav'; safe=b.d.pcm(y.astype(float)*.25)
                    with wave.open(str(out/name),'wb') as w:
                        w.setparams((1,2,b.d.RATE,0,'NONE','not compressed')); w.writeframes(safe.astype('<i2').tobytes())
                    gallery.append(name)
    groups=[]
    for mode,cond,weight in itertools.product(b.LAY,CONDS,WEIGHTS):
        rr=[r for r in traces if (r['mode'],r['condition'],r['weight'])==(mode,cond,weight)]; assert len(rr)==54
        baseline=[r for r in traces if (r['mode'],r['condition'],r['weight'])==(mode,cond,1.)]
        groups.append(dict(mode=mode,condition=cond,weight=weight,counts=dict(Counter(r['status'] for r in rr)),withheld=[sum(r['observed'][k] is None for r in rr) for k in range(len(rr[0]['expected']))],energy_ratio=float(np.median([r['energy']/v['energy'] for r,v in zip(rr,baseline)]))))
    receipt=dict(parent=PARENT,grammar=b.PIN,seed=SEED,calibration_seed=l.SEED+1,python=sys.version.split()[0],numpy=np.__version__,source_sha256=b.sha(Path(__file__).read_bytes()),conditions=CONDS,weights=WEIGHTS,thresholds=thresholds,groups=groups,pcm_trials=len(traces),limits='Single leaf; known slots/layout; same noise/phase across weights; matched nominal pre-fault peak 1600 PCM counts and duration 240 ms, not matched energy. Strict repair, not authentication. Calibration identical to Run 060 raw, no threshold tuning. Repeated absent noise is not independent. Synthetic only.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces))
    html='<!doctype html><meta charset=utf-8><title>Lexical power</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto}td,th{padding:.4em;border-bottom:1px solid #aaa}</style><h1>Lexical power allocation</h1><p>Synthetic PCM, same pre-fault peak and duration, not equal energy. Common gain audition copies.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in CONDS)+'</select></label><table><thead><tr><th>Layout</th><th>Weight</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Per-field withheld</th><th>Energy ratio</th></tr></thead><tbody id="r"></tbody></table><h2>Audition (opt-in)</h2>'+''.join(f'<p>{p}<br><audio controls preload="none" src="{p}"></audio></p>' for p in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+';function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>{const t=document.createElement("tr");for(const v of [x.mode,x.weight,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0,x.withheld.join(" / "),x.energy_ratio.toFixed(3)]){const e=document.createElement("td");e.textContent=v;t.append(e)}return t}))}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({p.name:b.sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); verify(out)

def verify(out):
    rec=json.loads((out/'receipt.json').read_text()); rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; pairs={}
    assert len(rows)==rec['pcm_trials']==54*2*len(CONDS)*len(WEIGHTS)
    for r in rows:
        assert status(r)==r['status'] and abs(r['peak']-b.d.AMP)<1e-8
        pairs.setdefault((r['fixture'],r['mode'],r['condition']),[]).append(r)
    for key,rr in pairs.items():
        assert sorted(r['weight'] for r in rr)==list(WEIGHTS) and len({r['noise_sha256'] for r in rr})==1
        if key[2]=='absent': assert len({r['pcm_sha256'] for r in rr})==1
    for g in rec['groups']:
        rr=[r for r in rows if all(r[k]==g[k] for k in ('mode','condition','weight'))]; assert len(rr)==54 and dict(Counter(r['status'] for r in rr))==g['counts']
    for p,h in json.loads((out/'manifest.json').read_text()).items(): assert b.sha((out/p).read_bytes())==h
    print('verified',len(rows),'decisions',len(pairs),'matched groups',len(rec['groups']),'aggregates')

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--verify': verify(Path(sys.argv[2]))
    else: run(Path(sys.argv[1]))
