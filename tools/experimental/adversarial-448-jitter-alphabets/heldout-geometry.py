"""#448 adversarial holdout: fixed Run070 policies, independent pilot geometry.
python heldout-geometry.py bounded-reacquisition.py acquisition-rank.py selective-transport.py epoch-rank.py OUT
"""
import hashlib, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

REF='56272fdf8c81661a37b92cc1488baacf8f68e373'
PIN='386a2e3b1e88369748e2a7641614d7c12616cf4f7bbd0ba9c29c8b09da33d43d'
SEEDS=(4480721,4480722)
CASES=('target','coincident','near','far','independent','two','previous','reused','noise')
MODES=('local4','diverse4','local8')
def sha(x): return hashlib.sha256(x).hexdigest()

def run(bp,ap,tp,ep,out):
    assert sha(bp.read_bytes())==PIN
    b=runpy.run_path(str(bp)); assert tuple(sha(x.read_bytes()) for x in (ap,tp,ep))==b['PINS']
    a,p,e=[runpy.run_path(str(x)) for x in (ap,tp,ep)]
    ds,fs=a['DELAYS'],a['SHIFTS']; pad,slot,rate=a['PAD'],a['SLOT'],a['RATE']; size=11*slot+2*pad
    idx=pad+ds[:,None,None]+slot*np.arange(3)[None,:,None]+16+np.arange(160)
    t=np.arange(192)/rate; env=np.minimum(1,np.minimum(np.arange(192),191-np.arange(192))/16)
    def signal(symbols,d,f,amp,phase):
        x=np.zeros(size)
        for j,v in enumerate(symbols):
            k=pad+d+j*slot; x[k:k+192]=amp*env*np.sin(2*np.pi*(1000+100*v+f)*t+phase[j])
        return x
    rows=[]; gallery={}; groups={}; pairs={}
    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        for i,rank in enumerate(rng.permutation(108).tolist()):
            frame=i%54; epoch=int(rng.integers(256)); stale=(rank+int(rng.integers(1,108)))%108
            d=int(rng.integers(-151,152)); f=int(rng.integers(-75,76))
            near=int(np.clip(d+int(rng.choice([-40,-24,24,40])),-151,151))
            far=int(rng.choice([x for x in range(-151,152) if abs(x-d)>=96]))
            independent=int(rng.integers(-151,152)); f1,f2=map(int,rng.integers(-75,76,2))
            z=rng.normal(size=size); z*=1000/np.sqrt(np.mean(z*z)); ph=rng.uniform(0,2*np.pi,(3,11))
            target=signal(a['PILOT']+p['packet']([frame,epoch,rank]),d,f,1600,ph[0])
            for case in CASES:
                present=case!='noise'; x=target.copy() if present else np.zeros(size); geom=[]
                if case in ('coincident','near','far','independent','two'):
                    dd={'coincident':d,'near':near,'far':far,'independent':independent,'two':near}[case]
                    geom=[(dd,f1,2400)]
                    if case=='two': geom.append((far,f2,2400))
                    for k,(dd,ff,amp) in enumerate(geom): x+=signal(a['PILOT'],dd,ff,amp,ph[k+1])
                if case in ('previous','reused'):
                    old=(epoch-1)%256 if case=='previous' else epoch
                    geom=[(independent,f1,1600)]; x+=signal(a['PILOT']+p['packet']([frame,old,stale]),independent,f1,1600,ph[1])
                y=np.rint(x+z).clip(-32768,32767).astype('<i2'); digest=sha(y.tobytes())
                m=abs(np.einsum('dpt,fpt->dfp',y[idx].astype(float),a['PB']))*2/160; score=np.mean(m*m,axis=2); statuses=[]
                for mode in MODES:
                    candidates=[]
                    for j,k in b['select'](score,ds,fs,mode):
                        td,tf=int(ds[j]),int(fs[k]); strength=float(m[j,k].min())
                        v=a['decode'](y,8,td,tf) if strength>=600 else [None]*8
                        q=p['unpack'](v); q=q if q is not None and q[0]==frame and 0<=q[-1]<108 else None
                        candidates.append(dict(delay=td,shift=tf,pilot_min=strength,symbols=v,decoded=q))
                    got=e['choose']([c['decoded'] for c in candidates],epoch)
                    status='withheld' if got is None else 'correct' if present and got==rank else 'wrong'; statuses.append(status)
                    calls=sum(c['pilot_min']>=600 for c in candidates)
                    rows.append(dict(seed=seed,i=i,case=case,mode=mode,frame=frame,epoch=epoch,rank=rank,stale=stale,delay=d,shift=f,decoys=geom,present=present,decoded=got,status=status,calls=calls,candidates=candidates,pcm_sha256=digest,noise_sha256=sha(z.astype('<f8').tobytes())))
                    g=groups.setdefault((seed,case,mode),Counter()); g[status]+=1; g['calls']+=calls
                pairs.setdefault((seed,case),Counter())['/'.join(statuses[:2])]+=1
                if i==0 and seed==SEEDS[0]: gallery[case]=y
    out.mkdir(); summary=[dict(seed=s,case=c,mode=m,**{k:v[k] for k in ('correct','wrong','withheld','calls')}) for (s,c,m),v in groups.items()]
    receipt=dict(ref=REF,pin=PIN,measurement_ref=b['REF'],measurement_pins=b['PINS'],seeds=SEEDS,python=sys.version.split()[0],numpy=np.__version__,summary=summary,paired=[dict(seed=s,case=c,transitions=dict(v)) for (s,c),v in pairs.items()],limits='Known capture, epoch and frame; no streaming, timing drift, authentication, human evidence, or longer-body suspension. Unchanged policies, fresh seeds and geometry; no tuning. Same PCM per policy, not equal energy across conditions or measured CPU parity.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    for name,y in gallery.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w:
            w.setparams((1,2,rate,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Held-out geometry</title><h1>Held-out competing pilot geometry</h1><p>Synthetic only. Same capture per policy. Select condition.</p><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{k}<br><audio controls preload="none" src="{k}.wav"></audio></p>' for k in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.case)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.case===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n')
    verify(out,p)

def verify(out,p):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; groups={}; counts={}
    assert len(rows)==len(SEEDS)*108*len(CASES)*len(MODES)
    for r in rows:
        ranks=set(); groups.setdefault((r['seed'],r['i'],r['case']),[]).append(r)
        assert len(r['candidates'])==(8 if r['mode']=='local8' else 4)
        assert len({(v['delay'],v['shift']) for v in r['candidates']})==len(r['candidates'])
        for v in r['candidates']:
            q=p['unpack'](v['symbols']); q=q if q is not None and q[0]==r['frame'] and 0<=q[-1]<108 else None
            assert q==v['decoded']
            if q is not None and q[1]==r['epoch']: ranks.add(q[-1])
        got=next(iter(ranks)) if len(ranks)==1 else None; assert got==r['decoded']
        status='withheld' if got is None else 'correct' if r['present'] and got==r['rank'] else 'wrong'; assert status==r['status']
        calls=sum(v['pilot_min']>=600 for v in r['candidates']); assert calls==r['calls']
        g=counts.setdefault((r['seed'],r['case'],r['mode']),Counter()); g[status]+=1; g['calls']+=calls
    assert len(groups)==len(SEEDS)*108*len(CASES)
    paired={}
    for (s,i,c),rs in groups.items():
        assert len(rs)==3 and len({r['pcm_sha256'] for r in rs})==1 and {r['mode'] for r in rs}==set(MODES)
        by={r['mode']:r['status'] for r in rs}; paired.setdefault((s,c),Counter())[by['local4']+'/'+by['diverse4']]+=1
    rec=json.loads((out/'receipt.json').read_text())
    for g in rec['summary']:
        c=counts[g['seed'],g['case'],g['mode']]; assert sum(c[k] for k in ('correct','wrong','withheld'))==108 and all(c[k]==g[k] for k in c)
    for g in rec['paired']: assert dict(paired[g['seed'],g['case']])==g['transitions']
    for name,h in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/name).read_bytes())==h
    print('verified',len(rows),'decisions',len(groups),'matched captures',len(counts),'groups')
if __name__=='__main__': run(*map(Path,sys.argv[1:]))
