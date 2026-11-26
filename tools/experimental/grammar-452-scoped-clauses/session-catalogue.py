"""Refs #452 / Draft #453. Session catalogue offers, revocation and replay witnesses.
Native synthetic aligned PCM only. Run: python session-catalogue.py PINNED_DIR NEW_OUTPUT.
Session ids are correlation, not authentication; no durable replay protection or action authority.
One GPT-6.2 agent; no human participants, independent review or scientific acceptance.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='755fa4849843a8226063465ce6426fca49fd8b86'
BLOB='8b0f4f6365e3c908a2f9c7a8a7e97fa245fe6580'
SEED=452450
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def run(root,out):
    path=root/'catalogue-agreement.py'; assert blob(path.read_bytes())==BLOB
    g=runpy.run_path(str(path)); c=runpy.run_path(str(root/'catalogue-reply.py'))
    pins={'catalogue-agreement.py':BLOB,'catalogue-reply.py':g['BLOB'],**c['BLOBS']}
    for f,b in pins.items():assert blob((root/f).read_bytes())==b,f
    a=runpy.run_path(str(root/'acoustic-clarification.py'));v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED);out.mkdir(parents=True,exist_ok=False);rows=[];stats={};spec=[];witness=[];sessions=0
    for source,bylen in books.items():
        for length,book in bylen.items():
            width=4 if length==13 else 5;identity=np.arange(len(book));shift=np.roll(identity,1);ca,cb,tries,ct=g['collision'](source,length,book)
            digest=lambda order:g['digest'](source,length,book[order]).digest()
            h=lambda d,n:int.from_bytes(d,'big')%17**n
            base,changed,da,db=map(digest,(identity,shift,ca,cb));assert h(da,4)==h(db,4)==ct and h(da,8)!=h(db,8) and h(base,4)!=h(changed,4)
            witness.append(dict(source=source,length=length,tries=tries,tag4=ct,tag8_sender=h(da,8),tag8_receiver=h(db,8),sender_sha256=da.hex(),receiver_sha256=db.hex(),sender_tail=ca[-10:].tolist(),receiver_tail=cb[-10:].tolist()))
            normal=rng.choice(len(book),8,False).tolist();special=np.resize(ca[np.flatnonzero(ca!=cb)],8).tolist()
            for condition in ('clean','noise2500','initial-shift','collision4','receiver-change','sender-change','stale-other-seq','stale-same-seq'):
                for mode in ('full','per-turn4','cached4','cached8','guarded8'):
                    sessions+=1;sid=[source*2+int(length==18),5];offer=None;accepted=None;frames=[];waves=[];events=[];allwaves=[]
                    so,ro=(ca,cb) if condition=='collision4' else (identity,shift if condition=='initial-shift' else identity)
                    sd,rd=(da,db) if condition=='collision4' else (base,changed if condition=='initial-shift' else base)
                    digits=4 if mode=='cached4' else 8;seed=SEED*10000+source*100000+length*1000+('clean','noise2500','initial-shift','collision4','receiver-change','sender-change','stale-other-seq','stale-same-seq').index(condition)*100
                    for t,target in enumerate(special if condition=='collision4' else normal):
                        frames=[];waves=[];events=[];result=None;reason='not-attempted';ns=seed+t*10
                        if t==4 and condition=='receiver-change':ro,rd=shift,changed;events.append('receiver-local-change')
                        if t==4 and condition=='sender-change':so,sd=shift,changed;events.append('sender-local-change')
                        def send(payload,role):
                            obs,pcm,trace=a['exchange'](payload,2500 if condition=='noise2500' else 0,ns+len(frames));frames.append(dict(role=role,**trace));waves.append(pcm);return obs
                        def read(obs,r,k):return c['decode'](obs,r) if obs is not None and len(obs)==k+r else None
                        def query(req,role):
                            obs=send(a['code'](req),role);return a['recover'](obs) if obs is not None and len(obs)==5 else None
                        def full():
                            req=[sid[0]+8,t,16];q=query(req,'full-query')
                            if q is None or q[2]!=16:return None,'full-query-rejected'
                            stale=t==2 and (condition=='stale-same-seq' or (condition=='stale-other-seq' and mode=='full'))
                            actual=(target+1)%len(book) if stale else target
                            if stale and condition=='stale-other-seq':q=[q[0],q[1]-1,q[2]]
                            obs=send(a['code'](q)+book[actual].tolist(),'stale-full' if stale else 'full-reply')
                            if obs is None or len(obs)!=5+length or a['recover'](obs[:5])!=req:return None,'full-correlation'
                            body=obs[5:];keep=[i for i,x in enumerate(body) if x is not None];e=length-len(keep)
                            if e>4:return None,'full-invalid'
                            hits=np.flatnonzero(2*np.count_nonzero(book[:,keep]!=[body[i] for i in keep],axis=1)+e<=4)
                            return (int(hits[0]),'full') if len(hits)==1 else (None,'full-invalid')
                        def address(req,tagged):
                            q=query(req,'address-query')
                            if q is None or (q[2]!=14 if tagged else q[:2]!=sid or not 0<=q[2]<8):return None,'address-query-rejected'
                            if not tagged and (offer is None or (mode=='guarded8' and sd!=offer)):
                                obs=send(c['encode'](q+[16],4),'revocation');z=read(obs,4,4)
                                return None,'sender-revoked' if z==req+[16] else 'revocation-invalid'
                            stale=t==2 and condition in ('stale-other-seq','stale-same-seq')
                            actual=(target+1)%len(book) if stale else target
                            if stale and condition=='stale-other-seq':q=[q[0],(q[1]-1)%17,q[2]] if tagged else [*q[:2],q[2]-1]
                            addr=int(np.flatnonzero(so==actual)[0]);obs=send(c['encode'](q+c['digits'](addr,width)+(c['digits'](h(sd,4),4) if tagged else []),4),'stale-address' if stale else 'address-reply')
                            z=read(obs,4,3+width+(4 if tagged else 0))
                            if z is None or z[:3]!=req:return None,'address-correlation'
                            if tagged and c['index'](z[3+width:])!=h(rd,4):return None,'tag-mismatch'
                            addr=c['index'](z[3:3+width]);return (int(ro[addr]),'address') if addr<len(ro) else (None,'range')
                        if t==0 and mode.startswith(('cached','guarded')):
                            req=sid+[13];q=query(req,'offer-query')
                            if q is not None and q[2]==13 and q[:2]==sid:
                                obs=send(c['encode'](q+c['digits'](h(sd,digits),digits),4),'offer-reply');offer=sd;z=read(obs,4,3+digits)
                                if z is not None and z[:3]==req and c['index'](z[3:])==h(rd,digits):accepted=rd;events.append('offer-accepted')
                                else:events.append('offer-rejected')
                        if mode=='guarded8' and accepted is not None and rd!=accepted:accepted=None;events.append('receiver-revoked')
                        if mode=='per-turn4':result,reason=address([sid[0],t,14],True)
                        elif accepted is not None:
                            result,reason=address(sid+[t],False)
                            if result is None:accepted=None;events.append('session-retired')
                        if result is None:events.append(reason);result,reason=full()
                        status='withheld' if result is None else 'correct' if result==target else 'wrong';slots=sum(f['slots'] for f in frames);k=mode+':'+condition;cnt=stats.setdefault(k,Counter());cnt[status]+=1;cnt['slots']+=slots;cnt['frames']+=len(frames)
                        rows.append(dict(source=source,length=length,session=sessions,sid=sid,turn=t,target=target,returned=result,status=status,mode=mode,condition=condition,reason=reason,events=events,slots=slots,seed=ns,frames=frames));allwaves.extend(waves)
                    if source==0 and length==13 and mode=='guarded8' and condition in ('clean','collision4','sender-change','stale-same-seq'):
                        name=condition+'.wav';pcm=np.concatenate([w.ravel() for w in allwaves]);b=pcm.tobytes()
                        with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b)
                        spec.append(dict(file=name,pcm_sha256=sha(b),peak=int(abs(pcm).max())))
    for row in rows:
        m,cnd,t,s=row['mode'],row['condition'],row['turn'],row['status']
        wrong=(cnd=='collision4' and m in ('cached4','per-turn4')) or (cnd in ('receiver-change','sender-change') and t>=4 and m in ('cached4','cached8')) or (cnd=='stale-same-seq' and t==2)
        withheld=cnd=='stale-other-seq' and m=='full' and t==2
        assert s==('wrong' if wrong else 'withheld' if withheld else 'correct'),row
        assert row['slots']==sum(x['slots'] for x in row['frames'])
    receipt=dict(schema='mhac-session-catalogue-v1',pin=PIN,blobs=pins,source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,sessions=sessions,turns=len(rows),stats=stats,collision_witnesses=witness,specimens=spec,limits='Exploratory aligned PCM with fixed source/length/turn and local immutable digest snapshots refreshed on scripted mapping changes. Eight-digit fingerprint is not authentication; only the four previous collision pairs tested, no 8-digit collision search. Stale frames are valid synthetic alternate content, not a recorded transport replay. Other-sequence injection affects first reply only; fallback is clean, full comparator has no retry. No elapsed processing, turnaround, timeout, persistent replay, blind acquisition or human evidence. Unequal airtime and energy.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Session catalogue</title><h1>Session catalogue</h1><p>Synthetic PCM. Start at low volume; no autoplay.</p>'+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>');(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(dict(sessions=sessions,turns=len(rows),stats=stats)))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
