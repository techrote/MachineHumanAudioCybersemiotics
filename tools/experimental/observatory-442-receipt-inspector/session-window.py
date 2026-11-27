"""Measurement #442: synthetic session-window replay laboratory, not authentication.
Usage: python session-window.py acquisition-rank.py selective-transport.py OUT
"""
import hashlib, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

REF='cf8ed0b6dea0cfc4865ad10a57fbcebd3339fe36'
ADV='56272fdf8c81661a37b92cc1488baacf8f68e373'
PINS=('dc27f1f5eaba943577ef85ebad9fd2d29c1307d82fa7f7dd27da50db9c1c69e3','2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf')
SEED=4427101
POL=('session_only','monotonic','window8_volatile','window8_retained')
def sha(b): return hashlib.sha256(b).hexdigest()

def decide(state, candidates, session, policy, restart=False):
    # Trusted session selection is external; no modular sequence wrap is allowed.
    if state[0]!=session or (restart and policy=='window8_volatile'):
        state[:]=[session,-1,0]
    eligible={tuple(q) for q in candidates if q is not None and q[0]==session}
    if len(eligible)!=1: return None,'ambiguous_or_missing'
    _,seq,rank=next(iter(eligible)); hi,bits=state[1:]
    if policy=='session_only': return rank,'accepted'
    if seq<=hi:
        delta=hi-seq
        if policy=='monotonic' or delta>=8: return None,'expired_or_nonmonotonic'
        if bits&(1<<delta): return None,'duplicate'
        state[2]|=1<<delta
    else:
        state[2]=((bits<<min(seq-hi,8))|1)&255; state[1]=seq
    return rank,'accepted'

def run(ap,tp,out):
    assert (sha(ap.read_bytes()),sha(tp.read_bytes()))==PINS
    a=runpy.run_path(str(ap)); p=runpy.run_path(str(tp)); rng=np.random.default_rng(SEED)
    rate,slot,pad=a['RATE'],a['SLOT'],a['PAD']; size=13*slot+2*pad
    ds,fs=a['DELAYS'],a['SHIFTS']; idx=pad+ds[:,None,None]+slot*np.arange(3)[None,:,None]+16+np.arange(160)
    t=np.arange(192)/rate; env=np.minimum(1,np.minimum(np.arange(192),191-np.arange(192))/16)
    rows=[]; gallery={}
    for i in range(24):
        s=int(rng.integers(65535)); u=s+1; ranks=rng.permutation(108).tolist()
        # (label, expected session, wire session, sequence, rank, intended, restart, replay source)
        events=[('first',s,s,10,ranks[0],True,False,None),('advance',s,s,12,ranks[1],True,False,None),('reorder',s,s,11,ranks[2],True,False,None),('duplicate',s,s,10,ranks[0],False,False,'first'),('jump',s,s,25,ranks[3],True,False,None),('expired_unseen',s,s,13,ranks[4],False,False,None),('restart_replay',s,s,25,ranks[3],False,True,'jump'),('post_restart',s,s,26,ranks[5],True,False,None),('new_session',u,u,0,ranks[6],True,False,None),('old_session',u,s,26,ranks[5],False,False,'post_restart'),('new_advance',u,u,2,ranks[7],True,False,None),('same_session_stale_unseen',u,u,1,ranks[8],False,False,None),('legitimate_after_stale',u,u,1,ranks[9],True,False,None),('noise',u,u,3,ranks[10],False,False,None)]
        states={k:[None,-1,0] for k in POL}; captures={}
        for label,session,wire,seq,rank,intended,restart,replay in events:
            if replay is not None: y=captures[replay]
            else:
                d=int(rng.choice([-151,-73,9,41,103])); f=int(rng.choice([-67,-33,17,43,73])); z=rng.normal(size=size); z*=1000/np.sqrt(np.mean(z*z)); x=np.zeros(size)
                symbols=a['PILOT']+p['packet']([wire>>8,wire&255,seq,rank]) if label!='noise' else []
                for j,v in enumerate(symbols):
                    k=pad+d+j*slot; x[k:k+192]=1600*env*np.sin(2*np.pi*(1000+100*v+f)*t+rng.uniform(0,2*np.pi))
                y=np.rint(x+z).clip(-32768,32767).astype('<i2')
            captures[label]=y
            m=abs(np.einsum('dpt,fpt->dfp',y[idx].astype(float),a['PB']))*2/160; score=np.mean(m*m,axis=2); candidates=[]; symbols=[]
            for _ in range(4):
                j,k=np.unravel_index(score.argmax(),score.shape); d,f=int(ds[j]),int(fs[k]); v=a['decode'](y,10,d,f) if m[j,k].min()>=600 else [None]*10
                q=p['unpack'](v); candidates.append([q[0]*256+q[1],q[2],q[3]] if q is not None and len(q)==4 and q[3]<108 else None); symbols.append(v)
                score[(abs(ds[:,None]-d)<=32)&(abs(fs[None,:]-f)<=20)]=-1
            for policy in POL:
                before=states[policy].copy(); got,reason=decide(states[policy],candidates,session,policy,restart)
                status='withheld' if got is None else 'correct' if intended and got==rank else 'wrong'
                rows.append(dict(episode=i,event=label,policy=policy,session=session,wire_session=wire,seq=seq,rank=rank,intended=intended,restart=restart,replay=replay,pcm_sha256=sha(y.tobytes()),symbols=symbols,candidates=candidates,before=before,after=states[policy].copy(),decoded=got,reason=reason,status=status))
            if i==0: gallery[label]=y
    out.mkdir(); summary=[]
    for label in [e[0] for e in events]:
        for policy in POL:
            c=Counter(r['status'] for r in rows if r['event']==label and r['policy']==policy); summary.append(dict(event=label,policy=policy,**{k:c[k] for k in ('correct','wrong','withheld')}))
    receipt=dict(parent=REF,adversarial_ref=ADV,source_pins=PINS,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,packet_ms=260,summary=summary,limits='Synthetic known-length captures, externally trusted 16-bit session transitions. No negotiated session, authentication, real durable storage or streaming. Retained state models lossless atomic persistence; restart resets only volatile window. Same-session unseen stale packet intentionally indistinguishable from legitimate reorder. Sequence never wraps within session. Noise RMS 1000 counts; tone peak 1600 counts. Literal PCM replay includes original noise. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    for label in ('first','duplicate','restart_replay','old_session','same_session_stale_unseen','legitimate_after_stale'):
        with wave.open(str(out/(label+'.wav')),'wb') as w:
            w.setparams((1,2,rate,0,'NONE','not compressed')); w.writeframes(np.rint(gallery[label]*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Session replay laboratory</title><h1>Session replay laboratory</h1><p>Synthetic only; session supplied, retained state modeled.</p><select id="e"></select><pre id="r"></pre>'+''.join(f'<p>{f.stem}<br><audio controls preload="none" src="{f.name}"></audio></p>' for f in sorted(out.glob('*.wav')))+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';const e=document.getElementById("e"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.event)))e.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.event===e.value),null,2)}e.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); verify(out,p)

def verify(out,p):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; receipt=json.loads((out/'receipt.json').read_text()); assert len(rows)==1344
    seen={}; states={}; counts={}; captures={}
    for r in rows:
        key=(r['episode'],r['policy']); session=r['session']; old,hi,accepted=states.get(key,(None,-1,set())); policy=r['policy']
        assert r['before']==[old,hi,sum(1<<(hi-v) for v in accepted if 0<=hi-v<8)]
        if old!=session or (r['restart'] and policy=='window8_volatile'): hi,accepted=-1,set()
        qs=[]
        for v in r['symbols']:
            q=p['unpack'](v); qs.append([q[0]*256+q[1],q[2],q[3]] if q is not None and len(q)==4 and q[3]<108 else None)
        assert qs==r['candidates']; eligible={tuple(q) for q in qs if q is not None and q[0]==session}; got=None
        if len(eligible)==1:
            _,seq,rank=next(iter(eligible))
            if policy=='session_only': got=rank
            elif seq>hi or (policy!='monotonic' and seq>hi-8 and seq not in accepted): got=rank; hi=max(hi,seq); accepted={v for v in accepted|{seq} if v>hi-8}
        states[key]=(session,hi,accepted); assert r['after']==[session,hi,sum(1<<(hi-v) for v in accepted)]; assert got==r['decoded']
        status='withheld' if got is None else 'correct' if r['intended'] and got==r['rank'] else 'wrong'; assert status==r['status']
        k=(r['episode'],r['event']); captures.setdefault(k,set()).add(r['pcm_sha256']); counts.setdefault((r['event'],policy),Counter())[status]+=1
        if r['replay']: assert captures[(r['episode'],r['replay'])]=={r['pcm_sha256']}
    assert len(captures)==336 and all(len(v)==1 for v in captures.values())
    for g in receipt['summary']:
        c=counts[g['event'],g['policy']]; assert sum(c.values())==24 and all(c[k]==g[k] for k in ('correct','wrong','withheld'))
    for name,digest in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/name).read_bytes())==digest
    print('verified',len(rows),'decisions',len(captures),'matched event groups',len(counts),'summary groups')
if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
