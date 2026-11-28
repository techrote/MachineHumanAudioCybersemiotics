"""Refs #452 / Draft #453: catalogue fingerprint replies, aligned synthetic PCM.
Run: python catalogue-agreement.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
No authentication, human evidence, blind acquisition or action authority.
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='6f97617400c4e2dc1d8d6a979edcba53c64e1f62'
BLOB='8b07a9dde7dd7250b490263c3044aeb798453019'
SEED=452440
sha=lambda b:hashlib.sha256(b).hexdigest()

def digest(source,length,book):
    return hashlib.sha256(b'MHAC-order-v1\0'+bytes([source,length])+len(book).to_bytes(4,'little')+book.astype('u1').tobytes())

def tag(h):
    return int.from_bytes(h.digest(),'big')%17**4

def collision(source,length,book):
    # Birthday search on permutations of the final ten actual catalogue rows.
    prefix=hashlib.sha256(b'MHAC-order-v1\0'+bytes([source,length])+len(book).to_bytes(4,'little')+book[:-10].astype('u1').tobytes())
    tail=book[-10:].astype('u1'); seen={}
    for count,p in enumerate(itertools.permutations(range(10)),1):
        if count>20000:break
        h=prefix.copy();h.update(tail[list(p)].tobytes());t=tag(h)
        if t in seen and sum(a!=b for a,b in zip(p,seen[t]))>=4:
            a=np.arange(len(book));b=a.copy();a[-10:]=len(book)-10+np.array(seen[t]);b[-10:]=len(book)-10+np.array(p)
            assert tag(digest(source,length,book[a]))==tag(digest(source,length,book[b]))==t
            assert digest(source,length,book[a]).digest()!=digest(source,length,book[b]).digest()
            return a,b,count,t
        seen[t]=p
    raise RuntimeError('no collision in bounded search')

def run(root,out):
    path=root/'catalogue-reply.py';raw=path.read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==BLOB
    c=runpy.run_path(str(path))
    for f,b in c['BLOBS'].items():
        raw=(root/f).read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    a=runpy.run_path(str(root/'acoustic-clarification.py'));v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED);out.mkdir(parents=True,exist_ok=False);rows=[];stats={};spec=[];witness=[]
    for source,bylen in books.items():
        for length,book in bylen.items():
            width=4 if length==13 else 5;identity=np.arange(len(book));shift=np.roll(identity,1);ca,cb,tries,ct=collision(source,length,book)
            changed=np.flatnonzero(ca!=cb);targets=ca[changed[:4]].tolist();normal=rng.choice(len(book),4,False).tolist()
            witness.append(dict(source=source,length=length,tries=tries,tag=ct,sender_tail=ca[-10:].tolist(),receiver_tail=cb[-10:].tolist(),sender_sha256=digest(source,length,book[ca]).hexdigest(),receiver_sha256=digest(source,length,book[cb]).hexdigest()))
            for condition in ('clean','noise2500','shift','collision','two-erasures','nonce-reuse','query-corruption'):
                so,ro=(ca,cb) if condition=='collision' else (identity,shift if condition=='shift' else identity)
                st,rt=tag(digest(source,length,book[so])),tag(digest(source,length,book[ro]));assert condition!='shift' or st!=rt
                for ti,target in enumerate(targets if condition=='collision' else normal):
                    nonce=[source*4+ti,length%17];seed=SEED*10000+len(rows)*10
                    for mode in ('index4','tagged','tagged-fallback','full'):
                        frames=[];waves=[];result=None;reason='no-reply';sender=(target+1)%len(book) if condition=='nonce-reuse' else target
                        def attempt(op,n,first):
                            request=n+[op];wire=a['code'](request)
                            if first and condition=='query-corruption':
                                rival=a['code']([(n[0]+1)%17,n[1],op]);diff=[i for i in range(len(wire)) if wire[i]!=rival[i]]
                                for i in diff[:2]:wire[i]=rival[i]
                            def send(payload):
                                obs,pcm,trace=a['exchange'](payload,2500 if condition=='noise2500' else 0,seed+len(frames));frames.append(trace);waves.append(pcm);return obs
                            obs=send(wire);q=a['recover'](obs) if obs is not None else None
                            if q is None or q[2] not in (14,15,16):return None,'query-rejected'
                            # Sender uses its decoded query, not the receiver's privileged request.
                            addr=int(np.flatnonzero(so==sender)[0]);payload=a['code'](q)+book[sender].tolist() if q[2]==16 else c['encode'](q+c['digits'](addr,width)+(c['digits'](st,4) if q[2]==14 else []),4)
                            if first and condition=='two-erasures':payload[-2:]=[None,None]
                            obs=send(payload)
                            if obs is None:return None,'framing'
                            if op==16:
                                if len(obs)!=5+length or a['recover'](obs[:5])!=request:return None,'correlation'
                                body=obs[5:];keep=[i for i,x in enumerate(body) if x is not None];e=length-len(keep)
                                if e>4:return None,'body-invalid'
                                hits=np.flatnonzero(2*np.count_nonzero(book[:,keep]!=[body[i] for i in keep],axis=1)+e<=4)
                                return (int(hits[0]),'full') if len(hits)==1 else (None,'body-invalid')
                            if len(obs)!=3+width+(4 if op==14 else 0)+4:return None,'format'
                            h=c['decode'](obs,4)
                            if h is None or h[:3]!=request:return None,'correlation'
                            if op==14 and c['index'](h[3+width:])!=rt:return None,'catalogue-mismatch'
                            addr=c['index'](h[3:3+width]);return (int(ro[addr]),'index') if addr<len(ro) else (None,'range')
                        result,reason=attempt(16 if mode=='full' else 15 if mode=='index4' else 14,nonce,True);initial=reason
                        if result is None and mode=='tagged-fallback':result,reason=attempt(16,[(nonce[0]+8)%17,nonce[1]],False)
                        status='withheld' if result is None else 'correct' if result==target else 'wrong';slots=sum(f['slots'] for f in frames);key=mode+':'+condition;counter=stats.setdefault(key,Counter());counter[status]+=1;counter['slots']+=slots;counter['frames']+=len(frames)
                        rows.append(dict(source=source,length=length,target=target,sender=sender,mode=mode,condition=condition,seed=seed,nonce=nonce,sender_tag=st,receiver_tag=rt,initial=initial,reason=reason,returned=result,status=status,slots=slots,frames=frames))
                        if source==0 and length==13 and ti==0 and mode=='tagged-fallback' and condition in ('clean','shift','collision','nonce-reuse'):
                            name=condition+'.wav';pcm=np.concatenate([w.ravel() for w in waves]);b=pcm.tobytes()
                            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b)
                            spec.append(dict(file=name,pcm_sha256=sha(b),peak=int(abs(pcm).max())))
    for row in rows:
        if row['condition'] in ('clean','noise2500','two-erasures'):assert row['status']=='correct',row
        if row['condition']=='shift':assert row['status']=={'index4':'wrong','tagged':'withheld','tagged-fallback':'correct','full':'correct'}[row['mode']]
        if row['condition']=='collision':assert row['status']==('correct' if row['mode']=='full' else 'wrong')
        if row['condition']=='nonce-reuse':assert row['status']=='wrong'
    receipt=dict(schema='mhac-catalogue-agreement-v1',pin=PIN,blob=BLOB,dependencies=c['BLOBS'],source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,evaluations=len(rows),stats=stats,collision_witnesses=witness,specimens=spec,limits='Four base-17 digits of SHA256 are a diagnostic fingerprint, not authentication. Actual catalogue order permutations, same codewords and semantic IDs. Known source/length/clock/turn boundaries. Full fallback adds a new query with different nonce; no durable replay protection. Faults exploratory, no holdout, no human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Catalogue agreement</title><h1>Catalogue agreement</h1><p>Synthetic aligned frames; start at low volume. No autoplay.</p>'+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<pre>'+json.dumps(stats,indent=2)+'</pre><p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>');(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(dict(evaluations=len(rows),stats=stats,witness=witness)))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
