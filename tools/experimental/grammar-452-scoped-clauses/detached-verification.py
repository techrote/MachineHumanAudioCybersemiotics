"""Refs #452 / Draft #453. Synthetic aligned PCM; public fixture key only.
Run: python detached-verification.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Recipient IDs are provisioned out of band, not negotiated or authenticated.
One GPT-6.2 worker; no human evidence, action authority or independent review.
"""
import hashlib, hmac, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='ad0ec7c854459af609283602def017cf17e5c8f0'
SEED=452480
blob=lambda b:hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
sha=lambda b:hashlib.sha256(b).hexdigest()

def run(root,out):
    z=runpy.run_path(str(root/'anchored-epoch.py')); c=runpy.run_path(str(root/'catalogue-reply.py')); a=runpy.run_path(str(root/'acoustic-clarification.py')); g=runpy.run_path(str(root/'catalogue-agreement.py')); e=runpy.run_path(str(root/'epoch-replay.py'))
    pins={**z['PINS'],**e['PINS'],**c['BLOBS'],'anchored-epoch.py':'44c5766ffd3250fa230fee36208b8498dc24538d'}
    for f,b in pins.items():assert blob((root/f).read_bytes())==b,f
    v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw;long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    out.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(SEED);rows=[];spec=[];stats={};deadlines=(2080,2160,3200,3280,3600,3680)
    modes=('legacy','bound-header','bound-detached');cases=('clean','noise','two-tag-erasures','body-altered','foreign-recipient','other-transaction-tag','catalogue-shift','missing-tag','valid-alternate','foreign-recipient-alternate')
    for s,profiles in books.items():
        for length,book in profiles.items():
            width=4 if length==13 else 5;n=len(book);ctx=g['digest'](s,length,book).digest();shift=g['digest'](s,length,np.roll(book,1,axis=0)).digest()
            for sample in range(4):
                target,rival=map(int,rng.choice(n,2,False));hdr=c['digits'](sample,2)+c['digits'](11,2)+[15]
                for case in cases:
                    seed=SEED*10000+len(rows)*10
                    for mode in modes:
                        frames=[];pcm=[];sd=2500 if case=='noise' else 0
                        def wire(data,role,holes=0):
                            w=c['encode'](data,4)
                            if holes:w[-holes:]=[None]*holes
                            obs,x,t=a['exchange'](w,sd,seed+len(frames));frames.append(dict(role=role,**t));pcm.append(x)
                            return c['decode'](obs,4) if obs is not None else None
                        def digest(context,body,recipient):
                            if mode=='legacy':return z['tag'](context,body)
                            return int.from_bytes(hmac.digest(z['KEY'],b'MHAC-048-recipient\0'+bytes([recipient])+context+bytes(body),'sha256'),'big')%17**8
                        q=wire(hdr,'query');assert q==hdr
                        body=q+c['digits'](rival if case in ('valid-alternate','foreign-recipient-alternate') else target,width)
                        signed=body if case!='other-transaction-tag' else [(body[0]+1)%17,*body[1:]]
                        value=digest(shift if case=='catalogue-shift' else ctx,signed,2 if case in ('foreign-recipient','foreign-recipient-alternate') else 1)
                        sent=q+c['digits'](rival,width) if case=='body-altered' else body
                        got=wire(sent,'body');candidate=c['index'](got[5:]) if got is not None and got[:5]==hdr else None
                        assert candidate is not None and candidate<n
                        body_ms=sum(f['slots'] for f in frames)*80
                        tagdata=c['digits'](value,8) if mode=='bound-detached' else signed[:5]+c['digits'](value,8)
                        check=None if case=='missing-tag' else wire(tagdata,'tag',2 if case=='two-tag-erasures' else 0)
                        prefix=0 if mode=='bound-detached' else 5
                        verified=check is not None and (not prefix or check[:5]==hdr) and hmac.compare_digest(bytes(check[prefix:]),bytes(c['digits'](digest(ctx,got,1),8)))
                        returned=candidate if verified else None;status='withheld' if returned is None else 'correct' if returned==target else 'wrong'
                        expected='correct' if case in ('clean','noise','two-tag-erasures') or case=='foreign-recipient' and mode=='legacy' else 'wrong' if case=='valid-alternate' or case=='foreign-recipient-alternate' and mode=='legacy' else 'withheld'
                        assert status==expected,(case,mode,status)
                        total=sum(f['slots'] for f in frames)*80
                        # Deadline views are causal projections of the same single-attempt trace. Never promote provisional evidence.
                        views={str(d):dict(provisional=candidate if body_ms<=d else None,admitted=returned if total<=d else None) for d in deadlines}
                        row=dict(source=s,length=length,sample=sample,mode=mode,case=case,seed=seed,target=target,rival=rival,provisional=candidate,returned=returned,status=status,body_ms=body_ms,total_ms=total,frames=frames,deadline_views=views);rows.append(row);stats.setdefault(mode+':'+case,Counter())[status]+=1
                        if s==0 and length==13 and sample==0 and case in ('clean','foreign-recipient','body-altered'):
                            name=mode+'-'+case+'.wav';x=np.concatenate(pcm)
                            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(x.tobytes())
                            spec.append(dict(file=name,pcm_sha256=sha(x.tobytes()),peak=int(abs(x).max()),status=status))
    receipt=dict(schema='mhac-detached-verification-v1',pin=PIN,blobs=pins,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,trials=len(rows),frames=sum(len(r['frames']) for r in rows),stats=stats,specimens=spec,limits='Known aligned frame boundaries, fixed provisioned recipient, public test key, one transaction, no retry or allocator execution. Foreign-recipient-alternate conveys a rival meaning under the wrong recipient context. No captured replay or allocator tests here. Deadline views are transmission-only prefix projections, not measured wall-clock latency. Foreign recipient uses same target to isolate context admission. No blind acquisition, secret management, active forgery claim, semantic truth, human evidence or action authority.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Detached verification</title><h1>Detached verification</h1><p>Synthetic only. Start at low volume. No autoplay.</p>'+''.join(f'<p>{s["file"]}: {s["status"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
