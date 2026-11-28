"""#448 synthetic epoch-header acquisition: matched four-decode ceilings.
python bounded-reacquisition.py acquisition-rank.py selective-transport.py epoch-rank.py OUT
"""
import hashlib, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

PINS=('dc27f1f5eaba943577ef85ebad9fd2d29c1307d82fa7f7dd27da50db9c1c69e3','2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf','b2fe2e6468acd283c03d3766edc9036df1f7dd8b0933c9d6641fee6b61b8e13a')
REF='cf8ed0b6dea0cfc4865ad10a57fbcebd3339fe36'
SEED=4480701
CASES=('target','equal_pilot','strong_pilot','two_pilots','previous','reused','stale_only','noise')
MODES=('local4','diverse4','local8')
def sha(b): return hashlib.sha256(b).hexdigest()
def select(score,ds,fs,mode):
    work=score.copy(); result=[]
    for k in range(8 if mode=='local8' else 4):
        pool=work.copy()
        if mode=='diverse4' and k<3:
            for i,j in result: pool[abs(ds-ds[i])<=48,:]=-1
            if pool.max()<0: pool=work
        i,j=np.unravel_index(pool.argmax(),pool.shape)
        result.append((int(i),int(j)))
        work[(abs(ds[:,None]-ds[i])<=32)&(abs(fs[None,:]-fs[j])<=20)]=-1
    return result

def run(ap,tp,ep,out):
    assert tuple(sha(p.read_bytes()) for p in (ap,tp,ep))==PINS
    a,p,e=[runpy.run_path(str(x)) for x in (ap,tp,ep)]
    ds,fs=a['DELAYS'],a['SHIFTS']; rng=np.random.default_rng(SEED)
    pad,slot,rate=a['PAD'],a['SLOT'],a['RATE']; size=11*slot+2*pad
    idx=pad+ds[:,None,None]+slot*np.arange(3)[None,:,None]+16+np.arange(160)
    t=np.arange(192)/rate; env=np.minimum(1,np.minimum(np.arange(192),191-np.arange(192))/16)
    def signal(symbols,d,f,amp,phase):
        x=np.zeros(size)
        for i,v in enumerate(symbols):
            k=pad+d+i*slot; x[k:k+192]=amp*env*np.sin(2*np.pi*(1000+100*v+f)*t+phase[i])
        return x
    rows=[]; gallery={}
    for i,rank in enumerate(rng.permutation(108).tolist()):
        frame=i%54; epoch=int(rng.integers(256)); stale=(rank+1)%108
        d=int(rng.integers(-151,152)); f=int(rng.integers(-75,76)); dd=-d; ff=-f
        z=rng.normal(size=size); z*=1000/np.sqrt(np.mean(z*z)); ph=rng.uniform(0,2*np.pi,(3,11))
        target=signal(a['PILOT']+p['packet']([frame,epoch,rank]),d,f,1600,ph[0])
        pilot=signal(a['PILOT'],dd,ff,1,ph[1]); pilot2=signal(a['PILOT'],0,75,1,ph[2])
        for case in CASES:
            present=case not in ('stale_only','noise'); x=target.copy() if present else np.zeros(size)
            if case in ('equal_pilot','strong_pilot','two_pilots'): x+=(1600 if case=='equal_pilot' else 2400)*pilot
            if case=='two_pilots': x+=2400*pilot2
            if case in ('previous','reused','stale_only'):
                old=epoch if case!='previous' else (epoch-1)%256
                x+=signal(a['PILOT']+p['packet']([frame,old,stale]),dd,ff,1600,ph[1])
            y=np.rint(x+z).clip(-32768,32767).astype('<i2')
            m=abs(np.einsum('dpt,fpt->dfp',y[idx].astype(float),a['PB']))*2/160; score=np.mean(m*m,axis=2)
            for mode in MODES:
                candidates=[]
                for j,k in select(score,ds,fs,mode):
                    td,tf=int(ds[j]),int(fs[k]); strength=float(m[j,k].min()); v=a['decode'](y,8,td,tf) if strength>=600 else [None]*8
                    q=p['unpack'](v); q=q if q is not None and q[0]==frame and 0<=q[-1]<108 else None
                    candidates.append(dict(delay=td,shift=tf,pilot_min=strength,symbols=v,decoded=q))
                got=e['choose']([c['decoded'] for c in candidates],epoch)
                status='withheld' if got is None else 'correct' if present and got==rank else 'wrong'
                rows.append(dict(i=i,frame=frame,epoch=epoch,rank=rank,case=case,present=present,mode=mode,delay=d,shift=f,decoded=got,status=status,candidates=candidates,pcm_sha256=sha(y.tobytes())))
            if i==0: gallery[case]=y
    out.mkdir(); summary=[]
    for case in CASES:
        for mode in MODES:
            g=[r for r in rows if r['case']==case and r['mode']==mode]; c=Counter(r['status'] for r in g)
            summary.append(dict(case=case,mode=mode,**{k:c[k] for k in ('correct','wrong','withheld')},decodes=sum(v['pilot_min']>=600 for r in g for v in r['candidates'])))
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'receipt.json').write_text(json.dumps(dict(ref=REF,pins=PINS,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,summary=summary,limits='Known frame, epoch and capture; no streaming, authentication or human evidence. 357 pilot scores shared; 4 or 8 candidate checks. Equal ceiling not equal actual work. Matched PCM across policies, not equal energy across conditions. Exploratory.'),indent=2)+'\n')
    for name,y in gallery.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w:
            w.setparams((1,2,rate,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Bounded reacquisition</title><h1>Bounded reacquisition (synthetic)</h1><p>Four versus eight candidate checks. Select condition.</p><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{k}<br><audio controls preload="none" src="{k}.wav"></audio></p>' for k in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.case)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.case===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n')
    verify(out,p)

def verify(out,p):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; groups={}; counts={}
    assert len(rows)==108*len(CASES)*len(MODES)
    for r in rows:
        ranks=set(); key=(r['i'],r['case']); groups.setdefault(key,[]).append(r['pcm_sha256'])
        assert len(r['candidates'])==(8 if r['mode']=='local8' else 4)
        assert len({(v['delay'],v['shift']) for v in r['candidates']})==len(r['candidates'])
        for v in r['candidates']:
            q=p['unpack'](v['symbols']); q=q if q is not None and q[0]==r['frame'] and 0<=q[-1]<108 else None
            assert q==v['decoded']
            if q is not None and q[1]==r['epoch']: ranks.add(q[-1])
        got=next(iter(ranks)) if len(ranks)==1 else None; assert got==r['decoded']
        status='withheld' if got is None else 'correct' if r['present'] and got==r['rank'] else 'wrong'; assert status==r['status']
        counts.setdefault((r['case'],r['mode']),Counter())[status]+=1
    assert len(groups)==864 and all(len(h)==3 and len(set(h))==1 for h in groups.values())
    for g in json.loads((out/'receipt.json').read_text())['summary']:
        c=counts[g['case'],g['mode']]; assert sum(c.values())==108 and all(c[k]==g[k] for k in ('correct','wrong','withheld'))
    for name,h in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/name).read_bytes())==h
    print('verified',len(rows),'decisions',len(groups),'matched captures',len(counts),'groups')
if __name__=='__main__': run(*map(Path,sys.argv[1:]))
