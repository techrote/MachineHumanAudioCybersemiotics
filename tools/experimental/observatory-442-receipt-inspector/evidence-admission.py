"""Refs #442/#443. Synthetic Dual3 evidence-conditioned admission, no human evidence."""
import hashlib, importlib.util, itertools, json, sys
from collections import Counter
from pathlib import Path
import numpy as np

PARENT='fbae87f8d3b8d317dce12674034a229691403064'
MAIN='495a98ca12bae467a507031f04931aa4254b1866'
SEED=4426201
base=Path(__file__).with_name('lexical-power.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='5fc1521de804c96d90281e4daebaef75cdb93b912952e2e734cceb59edcf5cf2'
spec=importlib.util.spec_from_file_location('power',base)
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p); b=p.b; l=p.l
MODE='dual3'; WEIGHTS=(1.,2.,3.)
CONDS={'clean':(0,0,0),'white':(25,1000,0),'colored':(25,1000,1),'erase2':(27,1000,0),'replace2':(27,1000,0),'mixed':(27,1000,0),'absent':(27,1000,.75)}
POL=('strict','checks_observed','all_observed','all_observed_retry')

def admit(obs,policy):
    if obs[0] not in range(4) or obs[1]!=0: return None
    if policy=='checks_observed' and None in obs[5:]: return None
    if policy=='all_observed' and None in obs: return None
    got=b.repair(tuple(obs[2:]),MODE)
    return None if got is None else [*obs[:2],*got[0][:3]]

def status(got,expected,cond):
    return 'withheld' if got is None else 'correct' if cond!='absent' and got==list(expected[:5]) else 'wrong'

def decisions(obs):
    a={k:admit(obs[0],k) for k in POL[:3]}
    a[POL[3]]=a[POL[2]] if a[POL[2]] is not None else admit(obs[1],POL[2])
    return a

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    train=l.null(l.SEED+1,(0,.5,1),MODE)
    thresholds=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0)[:,0]
    rng=np.random.default_rng(SEED); rows=[]
    for i,q in enumerate(b.Q*2):
        expected=(int(rng.integers(4)),0,*b.code(q,MODE)); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(2,3,b.d.SLOT))
        for cond,(shift,sd,mix) in CONDS.items():
            changed=list(expected)
            if cond=='erase2': changed[2]=changed[3]=None
            if cond in ('replace2','mixed'): changed[2]=(changed[2]+1)%3; changed[3]=(changed[3]+2)%3
            if cond=='mixed': changed[6]=None
            noise=[sd*l.a.mix(v,mix) for v in z]
            for weight in WEIGHTS:
                x=p.render(expected,MODE,shift,phase,weight); scale=b.d.AMP/np.max(abs(x))
                signal=p.render(changed,MODE,shift,phase,weight)*scale
                if cond=='absent': signal[:]=0
                obs=[]; hashes=[]; evidence=[]
                for n in noise:
                    y=b.d.pcm(signal+n); win,j,d,h=l.measure(y[:,160:800].astype(float),MODE)
                    obs.append([v if j[k]>=max(80,thresholds[k]*d[k,0]) else None for k,v in enumerate(win)])
                    hashes.append(b.sha(y.astype('<i2').tobytes())); evidence.append(dict(offset=h,joint=j.tolist(),background=d[:,0].tolist()))
                got=decisions(obs)
                rows.append(dict(fixture=i,condition=cond,weight=weight,expected=expected,transmitted=changed,phase=phase,scale=float(scale),observed=obs,pcm_sha256=hashes,noise_sha256=[b.sha(n.astype('<f8').tobytes()) for n in noise],evidence=evidence,decoded=got,status={k:status(v,expected,cond) for k,v in got.items()},retry_used=got[POL[2]] is None))
    groups=aggregate(rows)
    receipt=dict(parent=PARENT,main=MAIN,grammar=b.PIN,seed=SEED,calibration_seed=l.SEED+1,thresholds=thresholds.tolist(),source_sha256=b.sha(Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,conditions=CONDS,weights=WEIGHTS,groups=groups,pcm_frames=2*len(rows),limits='Fresh noise and phase draws, balanced single leaves not new meanings. Known slots, fixed pre-fault peak 1600 counts, 240 ms per attempt. Retry repeats the same corruption with fresh noise, no feedback transport modeled. No human evidence or authentication.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset=utf-8><title>Evidence admission</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto}td,th{padding:.4em;border-bottom:1px solid #aaa}</style><h1>Evidence-conditioned admission</h1><p>Synthetic only. Retry repeats the same corruption with fresh noise. Cost includes a second 240 ms frame when requested; feedback cost excluded.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in CONDS)+'</select></label><table><thead><tr><th>Weight</th><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Frames</th></tr></thead><tbody id="r"></tbody></table><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+';function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>{const t=document.createElement("tr");for(const v of [x.weight,x.policy,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0,x.frames]){const e=document.createElement("td");e.textContent=v;t.append(e)}return t}))}c.onchange=draw;draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:b.sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); verify(out)

def aggregate(rows):
    groups=[]
    for cond,w,k in itertools.product(CONDS,WEIGHTS,POL):
        rr=[r for r in rows if r['condition']==cond and r['weight']==w]; assert len(rr)==54
        groups.append(dict(condition=cond,weight=w,policy=k,counts=dict(Counter(r['status'][k] for r in rr)),frames=len(rr)+sum(r['retry_used'] for r in rr if k==POL[3])))
    return groups

def verify(out):
    rec=json.loads((out/'receipt.json').read_text()); rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]
    assert len(rows)==54*len(CONDS)*len(WEIGHTS) and rec['pcm_frames']==2*len(rows)
    for r in rows:
        assert r['decoded']==decisions(r['observed']) and r['retry_used']==(r['decoded'][POL[2]] is None)
        for k,v in r['decoded'].items(): assert r['status'][k]==status(v,r['expected'],r['condition'])
        assert r['noise_sha256'][0]!=r['noise_sha256'][1] or r['condition']=='clean'
    assert aggregate(rows)==rec['groups']
    for f,h in json.loads((out/'manifest.json').read_text()).items(): assert b.sha((out/f).read_bytes())==h
    # Independent symbolic counterexample: both checks observed, 2 erasures + 1 substitution.
    w=(0,0,*b.code((0,0,0),MODE)); alternate=None
    for q in b.Q[1:]:
        a=(0,0,*b.code(q,MODE))
        if a[5:]==w[5:] and sum(x!=y for x,y in zip(w,a))==3:
            alternate=a; break
    assert alternate is not None
    x=[*alternate]; x[2]=x[3]=None
    assert admit(x,'checks_observed')==list(alternate[:5]) and admit(x,'all_observed') is None
    assert admit(list(alternate),'all_observed')==list(alternate[:5])!=list(w[:5])
    print('verified',len(rows),'paired attempts',len(rec['groups']),'aggregates')

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--verify': verify(Path(sys.argv[2]))
    else: run(Path(sys.argv[1]))
