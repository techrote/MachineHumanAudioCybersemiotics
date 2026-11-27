"""Refs #452 / Draft #453. Bounded epoch allocation and response-MAC witness.
python anchored-epoch.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Synthetic aligned PCM, public test key, no real authentication or action authority.
One GPT-6.2 worker; no participant evidence or independent review.
"""
import hashlib, hmac, json, pathlib, runpy, shutil, sys, tempfile, wave
from collections import Counter
import numpy as np
PIN='a9dfa879ea17c2adc33d40ebb0d41e6cae34addd'
SEED=452470
KEY=b'MHAC PUBLIC SYNTHETIC TEST KEY 047'
PINS={'epoch-replay.py':'6dcd5a75e0f67e16383f2421473e79b41610240a','catalogue-agreement.py':'8b0f4f6365e3c908a2f9c7a8a7e97fa245fe6580'}
sha=lambda b:hashlib.sha256(b).hexdigest()
blob=lambda b:hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def tag(context,body):
    return int.from_bytes(hmac.digest(KEY,b'MHAC-047-response\0'+context+bytes(body),'sha256'),'big')%17**8

class Session:
    # Allocator must be outside the rollback boundary for the anchored claim.
    def __init__(self,allocator):self.allocator=allocator;self.epoch=None;self.seq=289;self.pending=None
    def reserve(self):
        if self.pending is not None:raise ValueError('outstanding')
        if self.seq==289:
            self.epoch=self.allocator.reserve()
            if self.epoch is None:return None
            assert self.allocator.consume(self.epoch);self.seq=0
        self.pending=(self.epoch,self.seq);self.seq+=1;return self.pending
    def abandon(self):self.pending=None
    def consume(self,t):
        if self.pending!=t or t is None:return False
        self.pending=None;return True

def run(root,out):
    e=runpy.run_path(str(root/'epoch-replay.py'));c=runpy.run_path(str(root/'catalogue-reply.py'));a=runpy.run_path(str(root/'acoustic-clarification.py'));g=runpy.run_path(str(root/'catalogue-agreement.py'))
    pins={**PINS,**e['PINS'],**c['BLOBS']}
    for f,b in pins.items():assert blob((root/f).read_bytes())==b,f
    v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw;long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    out.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(SEED);rows=[];stats={};spec=[]
    cases=('clean','noise','duplicate','next-seq','restart','local-rollback','both-rollback','body-altered','signed-alternate','catalogue-shift','foreign-source','missing-tag','rollover')
    modes=('local','anchored','anchored-mac')
    for source,profiles in books.items():
        for length,book in profiles.items():
            width=4 if length==13 else 5;n=len(book);context=g['digest'](source,length,book).digest();foreign=g['digest'](1-source,length,books[1-source][length]).digest();shifted=g['digest'](source,length,np.roll(book,1,axis=0)).digest()
            for case in cases:
                previous,target=map(int,rng.choice(n,2,False))
                for mode in modes:
                    mac=mode=='anchored-mac';seed=SEED*1000+len(rows)*20;frames=[];replays=[];waves=[]
                    def transmit(data,role,sd=0):
                        assert len(data)+4<=17
                        _,pcm,t=a['exchange'](c['encode'](data,4),sd,seed+len(frames));frames.append(dict(role=role,**t));return pcm
                    def read(pcm,k):
                        if pcm is None or pcm.shape!=(k+6,a['S']):return None
                        scores=abs(pcm[:,80:480]@a['BASIS'].T)*2/400;obs=[int(z.argmax()) if z.max()>=600 else None for z in scores]
                        if obs[0]!=17 or obs[-1]!=18 or any(x is not None and x>=17 for x in obs[1:-1]):return None
                        return c['decode'](obs[1:-1],4)
                    def hdr(t):return c['digits'](t[0],2)+c['digits'](t[1],2)+[15]
                    def query(t,sd=0):
                        q=read(transmit(hdr(t),'query',sd),5);assert q==hdr(t);return q
                    def response(q,i,ctx,sd=0):
                        body=q+c['digits'](i,width);p=transmit(body,'body',sd);m=transmit(q+c['digits'](tag(ctx,body),8),'mac',sd) if mac else None;return p,m
                    def receive(sess,p,m):
                        body=read(p,5+width)
                        if body is None or body[4]!=15 or c['index'](body[5:])>=n:return None,'body'
                        token=(c['index'](body[:2]),c['index'](body[2:4]))
                        if token!=sess.pending:return None,'correlation'
                        if mac:
                            z=read(m,13)
                            if z is None or z[:5]!=body[:5] or not hmac.compare_digest(bytes(z[5:]),bytes(c['digits'](tag(context,body),8))):return None,'mac'
                        assert sess.consume(token);return c['index'](body[5:]),'admitted'
                    with tempfile.TemporaryDirectory() as tmp:
                        local=pathlib.Path(tmp)/'local.db';anchor=pathlib.Path(tmp)/'anchor.db';Ledger=e['Ledger']
                        for path in (local,anchor):
                            d=Ledger(path,289,False);d.close();shutil.copyfile(path,path.with_suffix('.snapshot'))
                        path=local if mode=='local' else anchor;db=Ledger(path,289,False);sess=Session(db)
                        t0=sess.reserve();assert t0==(0,0);capture=response(query(t0),previous,context);assert receive(sess,*capture)[0]==previous
                        if case in ('restart','local-rollback','both-rollback'):
                            db.close()
                            if case in ('local-rollback','both-rollback'):shutil.copyfile(local.with_suffix('.snapshot'),local)
                            if case=='both-rollback':shutil.copyfile(anchor.with_suffix('.snapshot'),anchor)
                            db=Ledger(path,289,False);sess=Session(db)
                        if case=='rollover':
                            for j in range(1,289):assert sess.reserve()==(0,j);sess.abandon()
                        t=None if case=='duplicate' else sess.reserve();start=len(frames)
                        if t is not None:q=query(t,2500 if case=='noise' else 0)
                        if case in ('duplicate','next-seq','restart','local-rollback','both-rollback','rollover'):
                            p,m=capture;replays=[sha(x.tobytes()) for x in capture if x is not None]
                        else:
                            ctx=shifted if case=='catalogue-shift' else foreign if case=='foreign-source' else context
                            i=(target+1)%n if case=='catalogue-shift' else previous if case in ('signed-alternate','foreign-source') else target
                            p,m=response(q,i,ctx,2500 if case=='noise' else 0)
                            if case=='body-altered':p=transmit(q+c['digits'](previous,width),'replacement-body')
                            if case=='missing-tag':m=None
                        got,reason=receive(sess,p,m);db.close()
                    status='withheld' if got is None else 'correct' if got==target else 'wrong'
                    expected='correct' if case in ('clean','noise') or case=='missing-tag' and not mac else 'wrong' if case=='both-rollback' or case=='local-rollback' and mode=='local' or case=='signed-alternate' or case in ('body-altered','catalogue-shift','foreign-source') and not mac else 'withheld'
                    assert status==expected,(source,length,case,mode,status,expected)
                    row=dict(source=source,length=length,case=case,mode=mode,target=target,previous=previous,token=t,returned=got,status=status,reason=reason,seed=seed,frames=frames,replay_hashes=replays,probe_generated_slots=sum(f['slots'] for f in frames[start:]),delivered_reply_hashes=[sha(x.tobytes()) for x in (p,m) if x is not None]);rows.append(row);stats.setdefault(mode+':'+case,Counter())[status]+=1
                    if source==0 and length==13 and mode=='anchored-mac' and case in ('clean','local-rollback','both-rollback','body-altered','signed-alternate'):
                        pcm=np.concatenate([x for x in (p,m) if x is not None]);name=case+'.wav'
                        with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
                        spec.append(dict(file=name,pcm_sha256=sha(pcm.tobytes()),peak=int(abs(pcm).max()),status=status))
    with tempfile.TemporaryDirectory() as tmp:
        db=e['Ledger'](pathlib.Path(tmp)/'exhaust.db',289,False)
        for i in range(289):assert db.reserve()==i;assert db.consume(i)
        db.close();db=e['Ledger'](pathlib.Path(tmp)/'exhaust.db',289,False);assert Session(db).reserve() is None;db.close()
    receipt=dict(schema='mhac-anchored-epoch-v1',pin=PIN,blobs=pins,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,trials=len(rows),generated_frames=sum(len(x['frames']) for x in rows),captured_frame_replays=sum(len(x['replay_hashes']) for x in rows),stats=stats,specimens=spec,limits='Known aligned frames, one serialized receiver, fixed catalogue context and public fixture key. Separate SQLite allocator models independent rollback boundary, not trusted hardware or remote attestation. Epoch echoed in query, no mutual negotiation. MAC response only, 8 base-17 digits (~32.7 bits), not production authentication; no key management, active forgery search or sender truth guarantee. No power loss, concurrent writers, actual transport, human evidence or action authority. Rollover/exhaustion advance reservations without audio. No retries; costs count generated frames, not transport latency.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Anchored epoch</title><h1>Anchored epoch and response binding</h1><p>Synthetic only. Start at low volume; no autoplay. Public test key, not real security.</p>'+''.join(f'<p>{s["file"]}: {s["status"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
