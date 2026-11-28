"""Refs #442/#443. Exploratory synthetic PCM, fitted carrier subtraction.
Run: OPENBLAS_NUM_THREADS=1 python leakage-audit.py NEW_OUTPUT
"""
import hashlib, importlib.util, itertools, json, sys
from collections import Counter
from pathlib import Path
import numpy as np
PARENT='dbedec06ab77ff49a406b1438a74b2405ebdb39e'
SEED=4426001
N=512
base=Path(__file__).with_name('spectral-support.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='7510a7c4cfee78bdd35134b7a1721e5ee67db5273e427d534a46eb7b8c567f8f'
spec=importlib.util.spec_from_file_location('support',base)
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a); b=a.b
POL=('raw','residual')
CONDS={'clean':(0,0,0),'clean_offgrid':(27,0,0),'white':(25,1000,0),'offgrid':(27,1000,0),'mix25':(27,1000,.25),'mix75':(27,1000,.75),'colored':(25,1000,1),'absent':(27,1000,.75),'replace2':(27,1000,0)}

def measure(x,mode):
    s=b.spectra(x); slots=[next(i for i,g in enumerate(b.LAY[mode]) if k in g) for k in range(sum(map(len,b.LAY[mode])))]
    h=int(np.argmax(sum(s[j,b.FI[k]].max(axis=-1) for k,j in enumerate(slots))))
    winners=[]; joint=[]; raw=[]; residual=[]; fitted=x.copy()
    for j,g in enumerate(b.LAY[mode]):
        f=[]
        for k in g:
            v=s[j,b.FI[k][h]]; f.append(b.F[k][int(np.argmax(v))]+b.GRID[h])
        ang=2*np.pi*np.array(f)[:,None]*b.T
        design=np.concatenate((np.sin(ang),np.cos(ang))).T
        fitted[j]-=design@np.linalg.lstsq(design,x[j],rcond=None)[0]
    for k,j in enumerate(slots):
        v=s[j,b.FI[k][h]]; o=np.sort(v); winners.append(int(np.argmax(v))); joint.append(min(o[-1],3*(o[-1]-o[-2])))
        bank=a.BANK[a.RI[k][h]]
        raw.append(np.median(abs(bank@x[j])*2/640)); residual.append(np.median(abs(bank@fitted[j])*2/640))
    return winners,np.array(joint),np.array([raw,residual]).T,int(b.GRID[h])

def null(seed,weights,mode):
    rng=np.random.default_rng(seed); result={}
    for w in weights:
        v=[]
        for _ in range(N):
            _,j,d,_=measure(a.mix(rng.normal(size=(3,640)),w),mode)
            v.append(j[:,None]/np.maximum(d,1e-12))
        result[w]=np.array(v)
    return result

def run(out):
    out.mkdir(parents=True,exist_ok=False); audit=[]; thresholds={}; traces=[]; rng=np.random.default_rng(SEED)
    for mode in b.LAY:
        train=null(SEED+1,(0,.5,1),mode); hold=null(SEED+2,(0,.25,.75,1),mode)
        t=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0); thresholds[mode]=t.tolist()
        for w,v in hold.items():
            for k,p in itertools.product(range(len(t)),range(2)):
                audit.append(dict(mode=mode,mix=w,band=k,policy=POL[p],n=N,exceed=int((v[:,k,p]>=t[k,p]).sum())))
    for i,q in enumerate(b.Q*2):
        row=(int(rng.integers(4)),0,*q); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,b.d.SLOT))
        for mode,(cond,(shift,sd,w)) in itertools.product(b.LAY,CONDS.items()):
            expected=(*row[:2],*b.code(q,mode)); x=b.render(expected,mode,shift,phase); scale=b.d.AMP/np.max(abs(x)); changed=list(expected)
            if cond=='replace2': changed[2]=(changed[2]+1)%3; changed[3]=(changed[3]+2)%3
            signal=b.render(changed,mode,shift,phase)*scale
            if cond=='absent': signal[:]=0
            y=b.d.pcm(signal+sd*a.mix(z,w)); win,j,d,h=measure(y[:,160:800].astype(float),mode)
            for p,name in enumerate(POL):
                obs=[v if j[k]>=max(80,thresholds[mode][k][p]*d[k,p]) else None for k,v in enumerate(win)]
                got=b.repair(tuple(obs[2:]),mode) if obs[0] is not None and obs[0]<4 and obs[1]==0 else None
                status='withheld' if got is None else 'correct' if cond!='absent' and obs[:2]==list(row[:2]) and got[0][:3]==q else 'wrong'
                traces.append(dict(fixture=i,mode=mode,condition=cond,policy=name,expected=expected,observed=obs,decoded=got,status=status,offset=h,joint=j.tolist(),background=d[:,p].tolist(),pcm_sha256=b.sha(y.tobytes())))
    groups=[]
    for mode,cond,p in itertools.product(b.LAY,CONDS,POL):
        rows=[r for r in traces if (r['mode'],r['condition'],r['policy'])==(mode,cond,p)]; assert len(rows)==54
        groups.append(dict(mode=mode,condition=cond,policy=p,counts=dict(Counter(r['status'] for r in rows)),lexical_background=float(np.median([r['background'][0] for r in rows])),lexical_withheld=sum(r['observed'][0] is None for r in rows)))
    receipt=dict(parent=PARENT,grammar=b.PIN,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=b.sha(Path(__file__).read_bytes()),conditions=CONDS,thresholds=thresholds,null_audit=audit,groups=groups,pcm_trials=len(traces)//2,decisions=len(traces),limits='Known slots/layout, selected-offset null calibration on whole three-slot frames, not prior max per-band envelope. Same winner and joint score for both estimators; fit candidate sin/cos even under null. Strict repair, single leaf, matched pre-fault peak. Synthetic only; no human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces))
    html='<!doctype html><meta charset=utf-8><title>Carrier leakage</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto}td,th{padding:.4em;border-bottom:1px solid #aaa}</style><h1>Carrier subtraction audit</h1><p>Synthetic single-leaf PCM. Null exceedance is selected-offset field evidence, not message risk.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in CONDS)+'</select></label><table><thead><tr><th>Layout</th><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Lexical background (PCM counts)</th><th>Lexical withheld</th></tr></thead><tbody id="r"></tbody></table><h2>Noise-only holdout</h2><table><thead><tr><th>Layout</th><th>Mix</th><th>Band</th><th>Policy</th><th>Exceedances</th><th>N</th></tr></thead><tbody id="a"></tbody></table><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+',audit='+json.dumps(audit)+';function row(v){const t=document.createElement("tr");for(const x of v){const e=document.createElement("td");e.textContent=x;t.append(e)}return t}function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>row([x.mode,x.policy,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0,x.lexical_background.toFixed(2),x.lexical_withheld])))}a.replaceChildren(...audit.map(x=>row([x.mode,x.mix,x.band,x.policy,x.exceed,x.n])));c.onchange=draw;draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({p.name:b.sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(receipt['pcm_trials'],receipt['decisions'])

def verify(out):
    receipt=json.loads((out/'receipt.json').read_text()); rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]
    assert len(rows)==receipt['decisions']; pairs={}
    for r in rows:
        key=(r['fixture'],r['mode'],r['condition']); pairs.setdefault(key,[]).append(r)
        q=r['expected'][2:5]; obs=r['observed']; got=r['decoded']
        status='withheld' if got is None else 'correct' if r['condition']!='absent' and obs[:2]==r['expected'][:2] and got[0][:3]==q else 'wrong'
        assert r['status']==status
    assert all(len(v)==2 and v[0]['pcm_sha256']==v[1]['pcm_sha256'] and v[0]['joint']==v[1]['joint'] and v[0]['offset']==v[1]['offset'] for v in pairs.values())
    for g in receipt['groups']:
        rr=[r for r in rows if all(r[k]==g[k] for k in ('mode','condition','policy'))]
        assert dict(Counter(r['status'] for r in rr))==g['counts'] and len(rr)==54
    for p,h in json.loads((out/'manifest.json').read_text()).items(): assert b.sha((out/p).read_bytes())==h
    for mode in b.LAY:
        q=(0,1,2); x=b.render((0,0,*b.code(q,mode)),mode,0,0)[:,160:800]
        _,_,d,h=measure(x,mode); assert h==0 and np.max(d[:,1])<1e-8
    print('verified',len(rows),'decisions',len(pairs),'matched pairs',len(receipt['groups']),'groups')

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--verify': verify(Path(sys.argv[2]))
    else: run(Path(sys.argv[1]))
