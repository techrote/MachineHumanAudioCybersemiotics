"""Measurement #442/#443. Direct finite-domain rank transport with epoch guard.
Usage: python epoch-rank.py acquisition-rank.py selective-transport.py OUTPUT
Synthetic only; epoch supplied by harness, not authenticated or negotiated.
"""
import hashlib, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

REF='2dab493e14107adb2fefce097aba59a13026d2a4'
ADV='9a8e4edc3c7607c37cda8381e57b707e70d66225'
PINS=('dc27f1f5eaba943577ef85ebad9fd2d29c1307d82fa7f7dd27da50db9c1c69e3','2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf')
SEED=4426901
CASES=('target','previous_only','wrap_only','target_previous','target_wrap','pilot_decoy','noise')
POLICIES=('rank','epoch_ignored','epoch_guard')
def sha(b): return hashlib.sha256(b).hexdigest()
def choose(candidates,epoch=None):
    ranks={q[-1] for q in candidates if q is not None and (epoch is None or q[1]==epoch)}
    return next(iter(ranks)) if len(ranks)==1 else None

def run(ap,tp,out):
    assert (sha(ap.read_bytes()),sha(tp.read_bytes()))==PINS
    a=runpy.run_path(str(ap)); p=runpy.run_path(str(tp)); rng=np.random.default_rng(SEED)
    ds,fs=a['DELAYS'],a['SHIFTS']; pad,slot,rate=a['PAD'],a['SLOT'],a['RATE']; size=11*slot+2*pad
    idx=pad+ds[:,None,None]+slot*np.arange(3)[None,:,None]+16+np.arange(160)
    t=np.arange(192)/rate; env=np.minimum(1,np.minimum(np.arange(192),191-np.arange(192))/16)
    def signal(symbols,d,f,amp,phase):
        x=np.zeros(size)
        for i,v in enumerate(symbols):
            k=pad+d+i*slot; x[k:k+192]=amp*env*np.sin(2*np.pi*(1000+100*v+f)*t+phase[i])
        return x
    rows=[]; gallery={}; order=rng.permutation(108)
    for i,rank in enumerate(order.tolist()):
        frame=i%54; epoch=int(rng.integers(256)); stale=(rank+int(rng.integers(1,108)))%108
        d=int(rng.choice([-151,-73,9,41,103])); f=int(rng.choice([-67,-33,17,43,73])); z=rng.normal(size=size); z*=1000/np.sqrt(np.mean(z*z))
        ph=rng.uniform(0,2*np.pi,11); ph2=rng.uniform(0,2*np.pi,11)
        for case in CASES:
            present=case in ('target','target_previous','target_wrap','pilot_decoy')
            for fmt in ('rank','epoch'):
                n=6 if fmt=='rank' else 8
                def header(r,e): return a['PILOT']+p['packet']([frame,r] if fmt=='rank' else [frame,e,r])
                x=signal(header(rank,epoch),d,f,1600,ph) if present else np.zeros(size)
                if case in ('previous_only','wrap_only','target_previous','target_wrap'):
                    old=epoch if 'wrap' in case else (epoch-1)%256
                    x+=signal(header(stale,old),-d,-f,1600,ph2)
                if case=='pilot_decoy': x+=signal(a['PILOT'],-d,-f,1600,ph2)
                y=np.rint(x+z).clip(-32768,32767).astype('<i2')
                m=abs(np.einsum('dpt,fpt->dfp',y[idx].astype(float),a['PB']))*2/160
                score=np.mean(m*m,axis=2); candidates=[]
                for _ in range(4):
                    j,k=np.unravel_index(score.argmax(),score.shape); dd,ff=int(ds[j]),int(fs[k]); strength=float(m[j,k].min())
                    v=a['decode'](y,n,dd,ff) if strength>=600 else [None]*n
                    q=p['unpack'](v); q=q if q is not None and q[0]==frame and 0<=q[-1]<108 else None
                    candidates.append(dict(delay=dd,shift=ff,pilot_min=strength,symbols=v,decoded=q))
                    score[(abs(ds[:,None]-dd)<=32)&(abs(fs[None,:]-ff)<=20)]=-1
                qs=[c['decoded'] for c in candidates]
                for policy in (('rank',) if fmt=='rank' else ('epoch_ignored','epoch_guard')):
                    got=choose(qs,epoch if policy=='epoch_guard' else None)
                    status='withheld' if got is None else 'correct' if present and got==rank else 'wrong'
                    rows.append(dict(i=i,frame=frame,epoch=epoch,case=case,policy=policy,rank=rank,stale=stale,present=present,delay=d,shift=f,decoded=got,status=status,candidates=candidates,pcm_sha256=sha(y.tobytes()),noise_sha256=sha(z.astype('<f8').tobytes()),signal_energy_pcm2=float(x@x),duration_ms=(n+3)*20))
                if i==0: gallery[case+'_'+fmt]=y
    out.mkdir(); summary=[]
    for case in CASES:
        for policy in POLICIES:
            g=[r for r in rows if r['case']==case and r['policy']==policy]; c=Counter(r['status'] for r in g)
            summary.append(dict(case=case,policy=policy,**{k:c[k] for k in ('correct','wrong','withheld')},duration_ms=g[0]['duration_ms']))
    receipt=dict(ref=REF,adversarial_ref=ADV,source_pins=PINS,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,summary=summary,limits='Known capture length, frame ID and expected epoch. Epoch byte is externally supplied, no authentication, negotiation or persistent replay state. Wrap control reuses epoch after 256 increments. Direct rank is complete only for 108 fixed-depth meanings. Continuous matched noise, same peak, not equal energy or duration. Four hypotheses, no streaming or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    for name,y in gallery.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w:
            w.setparams((1,2,rate,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Epoch rank laboratory</title><h1>Epoch rank laboratory</h1><p>Synthetic direct rank reception. Epoch supplied; wrap is not protected. Select a condition.</p><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{k}<br><audio controls preload="none" src="{k}.wav"></audio></p>' for k in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.case)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.case===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); verify(out,p)
def verify(out,p):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; rec=json.loads((out/'receipt.json').read_text()); assert len(rows)==2268
    groups={}; counts={}
    for r in rows:
        ranks=set()
        for c in r['candidates']:
            q=p['unpack'](c['symbols']); q=q if q is not None and q[0]==r['frame'] and 0<=q[-1]<108 else None
            assert q==c['decoded']
            if q is not None and (r['policy']!='epoch_guard' or q[1]==r['epoch']): ranks.add(q[-1])
        got=next(iter(ranks)) if len(ranks)==1 else None; assert got==r['decoded']
        status='withheld' if got is None else 'correct' if r['present'] and got==r['rank'] else 'wrong'; assert status==r['status']
        groups.setdefault((r['i'],r['case']),[]).append(r); counts.setdefault((r['case'],r['policy']),Counter())[status]+=1
    assert len(groups)==756
    for g in groups.values():
        assert len(g)==3 and len({r['noise_sha256'] for r in g})==1 and g[1]['pcm_sha256']==g[2]['pcm_sha256']
    for g in rec['summary']:
        c=counts[g['case'],g['policy']]; assert sum(c.values())==108 and all(c[k]==g[k] for k in ('correct','wrong','withheld'))
    for name,h in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/name).read_bytes())==h
    print('verified',len(rows),'decisions',len(groups),'matched noise groups',len(counts),'aggregate groups')
if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
