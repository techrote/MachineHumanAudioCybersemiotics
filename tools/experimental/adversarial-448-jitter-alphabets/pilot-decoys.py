"""Adversarial #448/#449: bounded pilot acquisition under matched continuous noise.
Run: python pilot-decoys.py acquisition-rank.py selective-transport.py OUTPUT
Synthetic known frame ID and capture length; no human or physical evidence.
"""
import hashlib, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

REF='2dab493e14107adb2fefce097aba59a13026d2a4'
PIN='dc27f1f5eaba943577ef85ebad9fd2d29c1307d82fa7f7dd27da50db9c1c69e3'
TRANSPORT_PIN='2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf'
SEED=4480681
CASES=('target','pilot_only','decoy_800','decoy_1600','decoy_2400','stale_only','target_and_stale','noise_only')
POLICIES=('pinned','bounded4','oracle')
def sha(b): return hashlib.sha256(b).hexdigest()
def run(ap,tp,out):
    assert sha(ap.read_bytes())==PIN and sha(tp.read_bytes())==TRANSPORT_PIN
    a=runpy.run_path(str(ap)); p=runpy.run_path(str(tp)); rng=np.random.default_rng(SEED)
    delays,shifts=a['DELAYS'],a['SHIFTS']; pad,slot,rate=a['PAD'],a['SLOT'],a['RATE']; n=6
    size=(n+3)*slot+2*pad; idx=pad+delays[:,None,None]+slot*np.arange(3)[None,:,None]+16+np.arange(160)
    env=np.minimum(1,np.minimum(np.arange(192),191-np.arange(192))/16); t=np.arange(192)/rate
    def signal(symbols,d,f,amp,ph):
        x=np.zeros(size)
        for i,v in enumerate(symbols):
            k=pad+d+i*slot; x[k:k+192]=amp*env*np.sin(2*np.pi*(1000+100*v+f)*t+ph[i])
        return x
    def valid(y,d,f,frame):
        v=a['decode'](y,n,d,f); q=p['unpack'](v)
        return q if q is not None and q[0]==frame and 0<=q[1]<108 else None
    rows=[]; gallery={}
    for frame in range(54):
        rank=int(rng.integers(108)); stale=(rank+1)%108
        d=int(rng.choice([-151,-73,9,41,103])); f=int(rng.choice([-67,-33,17,43,73])); dd=-d; ff=-f
        z=rng.normal(size=size); z*=1000/np.sqrt(np.mean(z*z)); ph=rng.uniform(0,2*np.pi,9); ph2=rng.uniform(0,2*np.pi,9)
        target=signal(a['PILOT']+p['packet']([frame,rank]),d,f,1600,ph)
        old=signal(a['PILOT']+p['packet']([frame,stale]),dd,ff,1600,ph2)
        pilot=signal(a['PILOT'],dd,ff,1,ph2)
        for case in CASES:
            present=case in ('target','decoy_800','decoy_1600','decoy_2400','target_and_stale')
            x=target.copy() if present else np.zeros(size)
            if case.startswith('decoy_'): x+=int(case.split('_')[1])*pilot
            if case=='pilot_only': x+=2400*pilot
            if case in ('stale_only','target_and_stale'): x+=old
            y=np.rint(x+z).clip(-32768,32767).astype('<i2'); digest=sha(y.tobytes())
            m=abs(np.einsum('dpt,fpt->dfp',y[idx].astype(float),a['PB']))*2/160
            score=np.mean(m*m,axis=2); work=score.copy(); candidates=[]
            for k in range(4):
                i,j=np.unravel_index(work.argmax(),work.shape); td,tf=int(delays[i]),int(shifts[j]); strength=float(m[i,j].min())
                candidates.append(dict(delay=td,shift=tf,pilot_min=strength,decoded=valid(y,td,tf,frame) if strength>=600 else None))
                work[(abs(delays[:,None]-td)<=32)&(abs(shifts[None,:]-tf)<=20)]=-1
            pd,pf,pa=a['acquire'](y); assert (pd,pf)==(candidates[0]['delay'],candidates[0]['shift']) and abs(pa-candidates[0]['pilot_min'])<1e-8
            values={tuple(c['decoded']) for c in candidates if c['decoded'] is not None}
            outputs=(candidates[0]['decoded'],list(next(iter(values))) if len(values)==1 else None,valid(y,d,f,frame) if present else None)
            for policy,q in zip(POLICIES,outputs):
                status='withheld' if q is None else 'correct' if present and q==[frame,rank] else 'wrong'
                rows.append(dict(frame=frame,case=case,policy=policy,present=present,rank=rank,stale_rank=stale,delay=d,shift=f,decoy_delay=dd,decoy_shift=ff,decoded=q,status=status,pcm_sha256=digest,noise_sha256=sha(z.astype('<f8').tobytes()),candidates=candidates))
            if frame==0 or (case=='decoy_2400' and outputs[0] is None and outputs[1]==[frame,rank] and 'rescued' not in gallery):
                name=case if frame==0 else 'rescued'; gallery[name]=y
    out.mkdir(); summary=[]
    for case in CASES:
        for policy in POLICIES:
            c=Counter(r['status'] for r in rows if r['case']==case and r['policy']==policy)
            summary.append(dict(case=case,policy=policy,**{k:c[k] for k in ('correct','wrong','withheld')}))
    receipt=dict(ref=REF,source_sha256=PIN,transport_sha256=TRANSPORT_PIN,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,sample_rate=rate,noise_rms_pcm=1000,summary=summary,limits='Exploratory held-out seed, continuous white noise including padding, arbitrary integer-sample arrival within search; fixed frame ID/capture length. Target and decoy superpose at matched target amplitude and noise, not matched total energy. Bounded4 uses same score plus four CRC candidates, 2 ms/20 Hz suppression; no CPU parity. Oracle knows target presence/timing/frequency. Stale same-ID header is deliberately valid, not a natural error rate. No body, streaming, authentication, physical or human qualification.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    for name,y in gallery.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w:
            w.setparams((1,2,rate,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Pilot decoys</title><h1>Pilot decoys: synthetic receivers</h1><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{k}<br><audio controls preload="none" src="{k}.wav"></audio></p>' for k in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.case)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.case===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n')
    verify(out)
def verify(out):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; rec=json.loads((out/'receipt.json').read_text()); assert len(rows)==1296
    groups={}; counts={}
    for r in rows:
        q=r['decoded']; expected='withheld' if q is None else 'correct' if r['present'] and q==[r['frame'],r['rank']] else 'wrong'; assert expected==r['status']
        v={tuple(c['decoded']) for c in r['candidates'] if c['decoded'] is not None}
        if r['policy']=='pinned': assert q==r['candidates'][0]['decoded']
        if r['policy']=='bounded4': assert q==(list(next(iter(v))) if len(v)==1 else None)
        groups.setdefault((r['frame'],r['case']),set()).add(r['pcm_sha256']); counts.setdefault((r['case'],r['policy']),Counter())[expected]+=1
    assert len(groups)==432 and all(len(v)==1 for v in groups.values())
    for g in rec['summary']:
        c=counts[g['case'],g['policy']]; assert sum(c.values())==54 and all(c[k]==g[k] for k in ('correct','wrong','withheld'))
    for name,h in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/name).read_bytes())==h
    print('verified',len(rows),'decisions',len(groups),'matched captures',len(counts),'groups')
if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
