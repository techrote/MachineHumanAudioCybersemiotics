"""Refs #442/#443. Synthetic paired amplitude-diverse retry; no human evidence."""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

PARENT='f7e0f68c20f7b48cbb3cafc8ef58498bcb0e2a25'
MAIN='495a98ca12bae467a507031f04931aa4254b1866'
SEED=4426301
base=Path(__file__).with_name('evidence-admission.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='bb426d8e81a2fce162bf446b06c6dc305f54298acf876fd936cea073fb4b6fe2'
spec=importlib.util.spec_from_file_location('admit',base)
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a); b=a.b; l=a.l
CONDS={'clean':(0,0,0),'white':(25,1000,0),'colored':(25,1000,1),'offgrid':(27,1000,.25),'persistent_mixed':(27,1000,0),'transient_mixed':(27,1000,0),'persistent_valid_alternate':(25,1000,0),'absent':(25,1000,0)}
POL=('single','repeat','diverse','repeat_union','diverse_union')
WEIGHTS=(2.,2.,1.)

def union(x,y):
    if any(u is not None and v is not None and u!=v for u,v in zip(x,y)): return None
    return [v if u is None else u for u,v in zip(x,y)]

def decide(obs,policy):
    first=a.admit(obs[0],'all_observed')
    if first is not None or policy=='single': return first,1
    second=obs[2 if policy.startswith('diverse') else 1]
    combined=union(obs[0],second) if policy.endswith('union') else second
    return (None if combined is None else a.admit(combined,'all_observed')),2

def aggregate(rows):
    result=[]
    for cond,policy in itertools.product(CONDS,POL):
        rr=[r for r in rows if r['condition']==cond]; counts=Counter(r['status'][policy] for r in rr); frames=sum(r['frames'][policy] for r in rr)
        result.append(dict(condition=cond,policy=policy,n=len(rr),counts=dict(counts),frames=frames,seconds=frames*.24,correct_per_second=counts['correct']/(frames*.24)))
    return result

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    train=l.null(l.SEED+1,(0,.5,1),a.MODE)
    thresholds=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0)[:,0]
    rng=np.random.default_rng(SEED); rows=[]; gallery=[]
    for i,q in enumerate(b.Q*2):
        exp=(int(rng.integers(4)),0,*b.code(q,a.MODE)); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(2,3,b.d.SLOT))
        for cond,(shift,sd,mix) in CONDS.items():
            obs=[]; hashes=[]; evidence=[]; sent=[]; noises=[]; peaks=[]
            for j,weight in enumerate(WEIGHTS):
                changed=list(exp)
                if cond=='persistent_mixed' or (cond=='transient_mixed' and j==0):
                    changed[2]=(changed[2]+1)%3; changed[3]=(changed[3]+2)%3; changed[6]=None
                if cond=='persistent_valid_alternate': changed[2:]=b.code(((q[0]+1)%3,q[1],q[2]),a.MODE)
                x=a.p.render(exp,a.MODE,shift,phase,weight); scale=b.d.AMP/np.max(abs(x)); peaks.append(float(np.max(abs(x*scale))))
                sig=a.p.render(changed,a.MODE,shift,phase,weight)*scale
                if cond=='absent': sig[:]=0
                noise=sd*l.a.mix(z[int(j>0)],mix); y=b.d.pcm(sig+noise)
                win,joint,d,h=l.measure(y[:,160:800].astype(float),a.MODE)
                obs.append([v if joint[k]>=max(80,thresholds[k]*d[k,0]) else None for k,v in enumerate(win)])
                hashes.append(b.sha(y.astype('<i2').tobytes())); noises.append(b.sha(noise.astype('<f8').tobytes())); sent.append(changed)
                evidence.append(dict(offset=h,joint=joint.tolist(),background=d[:,0].tolist(),scale=float(scale)))
                if i==0 and cond=='white':
                    name=f'attempt-{j}.wav'; gallery.append(name)
                    with wave.open(str(out/name),'wb') as w:
                        w.setparams((1,2,b.d.RATE,0,'NONE','not compressed')); w.writeframes(b.d.pcm(y.astype(float)*.25).astype('<i2').tobytes())
            got={k:decide(obs,k) for k in POL}
            rows.append(dict(fixture=i,condition=cond,expected=exp,transmitted=sent,phase=phase,observed=obs,pcm_sha256=hashes,noise_sha256=noises,pre_fault_peak=peaks,evidence=evidence,decoded={k:v[0] for k,v in got.items()},frames={k:v[1] for k,v in got.items()},status={k:a.status(v[0],exp,cond) for k,v in got.items()}))
    groups=aggregate(rows)
    rec=dict(parent=PARENT,main=MAIN,grammar=b.PIN,seed=SEED,calibration_seed=l.SEED+1,thresholds=thresholds.tolist(),source_sha256=b.sha(Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,conditions=CONDS,weights=WEIGHTS,groups=groups,pcm_frames=3*len(rows),limits='Known slots; nominal peak 1600 PCM counts; 240 ms/frame; same second noise across policies; no feedback cost. Union rejects observed conflicts but cannot detect a consistent alternate valid codeword. Synthetic only.')
    (out/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset=utf-8><title>Diverse retry</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto}td,th{padding:.5em;border-bottom:1px solid #aaa}pre{white-space:pre-wrap}</style><h1>Amplitude-diverse retry</h1><p>Synthetic aligned PCM; union rejects conflicts. No feedback cost included. Alternate valid codeword is a deliberate integrity control.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in CONDS)+'</select></label><table><thead><tr><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Frames</th><th>Correct/s</th></tr></thead><tbody id="r"></tbody></table><h2>Audition: first / same-weight retry / diverse retry</h2>'+''.join(f'<p>{p}<br><audio controls preload="none" src="{p}"></audio></p>' for p in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+';const c=document.getElementById("c"),r=document.getElementById("r");function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>{const t=document.createElement("tr");for(const v of [x.policy,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0,x.frames,x.correct_per_second.toFixed(3)]){const e=document.createElement("td");e.textContent=v;t.append(e)}return t}))}c.onchange=draw;document.querySelectorAll("audio").forEach(x=>x.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:b.sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); verify(out)

def verify(out):
    rec=json.loads((out/'receipt.json').read_text()); rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]
    assert len(rows)==54*len(CONDS) and rec['pcm_frames']==3*len(rows)
    def direct(x):
        return x[:5] if x is not None and x[0] in range(4) and x[1]==0 and tuple(x[2:]) in b.BOOK[a.MODE] else None
    for r in rows:
        x,y,z=r['observed']; assert r['noise_sha256'][1]==r['noise_sha256'][2] and all(abs(v-1600)<1e-8 for v in r['pre_fault_peak'])
        for k in POL:
            g=direct(x); n=1
            if g is None and k!='single':
                n=2; other=z if k.startswith('diverse') else y
                if k.endswith('union'):
                    pairs=[set((u,v))-{None} for u,v in zip(x,other)]
                    other=[next(iter(s)) if len(s)==1 else None for s in pairs] if all(len(s)<=1 for s in pairs) else None
                g=direct(other)
            assert g==r['decoded'][k] and n==r['frames'][k] and a.status(g,r['expected'],r['condition'])==r['status'][k]
    assert aggregate(rows)==rec['groups']
    for f,h in json.loads((out/'manifest.json').read_text()).items(): assert b.sha((out/f).read_bytes())==h
    assert union([1,None],[None,2])==[1,2] and union([1],[2]) is None
    print('verified',len(rows),'paired fixtures',len(rows)*len(POL),'policy decisions')

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--verify': verify(Path(sys.argv[2]))
    else: run(Path(sys.argv[1]))
