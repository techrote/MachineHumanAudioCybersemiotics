"""Refs #452 / Draft #453. Framed bidirectional clarification, synthetic only.
python acoustic-clarification.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Known slot clock, source/length and turn boundaries; no action authority.
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='60b7f27f7260d1a8ac00be5c3d13dc853a00a72c'
BLOB='32ffadda8146153ebbb90ebcd343129986512de8'
SEED=452420; F=16000; S=1280
sha=lambda b:hashlib.sha256(b).hexdigest()

def code(data):
    return list(data)+[sum(data)%17,sum((i+1)*v for i,v in enumerate(data))%17]

def recover(obs):
    holes=[i for i,v in enumerate(obs) if v is None]; found=[]
    if len(holes)>2: return None
    for values in itertools.product(range(17),repeat=len(holes)):
        x=list(obs)
        for i,v in zip(holes,values): x[i]=v
        if code(x[:-2])==x: found.append(x[:-2])
    if not holes and not found:
        for i,v in enumerate(obs):
            for a in range(17):
                if a==v: continue
                x=list(obs); x[i]=a
                if code(x[:-2])==x: found.append(x[:-2])
    return found[0] if len(found)==1 else None

T=np.arange(S//2); ENV=np.minimum(1,np.minimum(T/30,(len(T)-1-T)/30)); HZ=np.arange(400,2300,100)
TONES=np.rint(1500*ENV*np.sin(2*np.pi*HZ[:,None]*T/F+.137)).astype(np.int16)
BASIS=np.exp(-2j*np.pi*HZ[:,None]*np.arange(400)/F)

def exchange(payload,sd,seed,erase=None):
    tokens=[17,*payload,18]; x=np.zeros((len(tokens),S),float)
    if erase is not None: tokens[erase+1]=None
    for i,v in enumerate(tokens):
        if v is not None: x[i,:S//2]=TONES[v]
    x=np.clip(np.rint(x+np.random.default_rng(seed).normal(0,sd,x.shape)),-32768,32767).astype('<i2')
    scores=abs(x[:,80:480]@BASIS.T)*2/400
    obs=[int(a.argmax()) if a.max()>=600 else None for a in scores]
    data=obs[1:-1] if obs[0]==17 and obs[-1]==18 and all(v is None or v<17 for v in obs[1:-1]) else None
    return data,x,dict(sent=tokens,observed=obs,pcm_sha256=sha(x.tobytes()),slots=len(tokens),peak=int(abs(x).max()))

def run(root,out):
    raw=(root/'discriminating-reply.py').read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==BLOB
    p=runpy.run_path(str(root/'discriminating-reply.py'))
    for f,b in p['BLOBS'].items():
        raw=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    v=runpy.run_path(str(root/'version-bound-payload.py')); _,raw,_=v['build'](root); old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED); rows=[]; stats={}; specimens=[]; serial=0
    conditions=('clean','noise2500','query-erasure','reply-erasure','omitted-target','stale-nonce','wrapped-nonce','query-two-errors','reply-two-errors','query-frame-loss')
    for source,bylen in books.items():
        for length,book in bylen.items():
            for size in (2,4,8):
                for sample in range(2):
                    origin=int(rng.integers(len(book))); d=np.count_nonzero(book!=book[origin],axis=1); d[origin]=length+1
                    pool=np.argsort(d,kind='stable')[:32] if sample==0 else np.delete(np.arange(len(book)),origin)
                    ids=sorted([origin,*map(int,rng.choice(pool,size-1,False))]); pos=p['query'](book,ids,'balanced'); assert 3<=pos<length
                    omitted=int(next(i for i in np.flatnonzero(book[:,pos]==book[origin,pos]) if i not in ids)); serial+=1; nonce=[serial//17,serial%17]
                    for target in ids:
                        rival=next(i for i in ids if book[i,pos]!=book[target,pos])
                        for ci,condition in enumerate(conditions):
                            actual=omitted if condition=='omitted-target' else target; sd=2500 if condition=='noise2500' else 0; ns=SEED*10000+serial*1000+ids.index(target)*20+ci*2
                            for mode in ('compact','full'):
                                request=nonce+[pos-3 if mode=='compact' else 16]; wire=code(request)
                                if condition=='query-two-errors':
                                    other=code([(nonce[0]+1)%17,*request[1:]]); diff=[i for i in range(len(wire)) if wire[i]!=other[i]]; assert len(diff)==3
                                    for i in diff[:2]: wire[i]=other[i]
                                qo,qpcm,qt=exchange(wire,sd,ns,0 if condition=='query-erasure' else -1 if condition=='query-frame-loss' else None); q=recover(qo) if qo is not None else None
                                got=[]; rt=None; rpcm=None
                                if q is not None and (q[2]==16 or 0<=q[2]<length-3):
                                    sender=rival if condition in ('stale-nonce','wrapped-nonce') else actual
                                    echoed=[q[0],(q[1]+1)%17] if condition=='stale-nonce' else q[:2]
                                    payload=code(echoed+[q[2],int(book[sender,q[2]+3])]) if q[2]!=16 else code(echoed+[16])+book[sender].tolist()
                                    if condition=='reply-two-errors':
                                        other=code(echoed+[q[2],int(book[rival,q[2]+3])]) if q[2]!=16 else code(echoed+[16])+book[rival].tolist()
                                        diff=[i for i in range(len(payload)) if payload[i]!=other[i]]; assert len(diff)>=3
                                        for i in diff[:2]: payload[i]=other[i]
                                    ro,rpcm,rt=exchange(payload,sd,ns+1,len(payload)-1 if condition=='reply-erasure' else None)
                                    if ro is not None and mode=='compact' and len(ro)==6:
                                        h=recover(ro)
                                        if h is not None and h[:3]==request: got=[i for i in ids if book[i,pos]==h[3]]
                                    if ro is not None and mode=='full' and len(ro)==5+length:
                                        h=recover(ro[:5]); body=ro[5:]; keep=[i for i,x in enumerate(body) if x is not None]; e=length-len(keep)
                                        if h==request and e<=4:
                                            distances=np.count_nonzero(book[:,keep]!=np.array([body[i] for i in keep]),axis=1)
                                            found=np.flatnonzero(2*distances+e<=4); got=found.tolist() if len(found)==1 else []
                                status='withheld' if not got else 'wrong-set' if actual not in got else 'resolved' if len(got)==1 else 'retained'
                                slots=qt['slots']+(rt['slots'] if rt else 0); k=f'{mode}:{condition}'; stats.setdefault(k,Counter()).update([status]); stats[k]['slots']+=slots
                                row=dict(source=source,length=length,ids=ids,target=actual,nominal_target=target,mode=mode,condition=condition,request=request,decoded_query=q,returned=got,status=status,query=qt,reply=rt,noise_seed=ns,slots=slots); rows.append(row)
                                if serial==1 and target==origin and condition in ('clean','omitted-target','wrapped-nonce','query-two-errors','reply-two-errors','query-frame-loss'):
                                    for direction,pcm in [('query',qpcm),('reply',rpcm)]:
                                        if pcm is None: continue
                                        name=f'{mode}-{condition}-{direction}.wav'
                                        with wave.open(str(out/name),'wb') as w: w.setparams((1,2,F,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                                        specimens.append(dict(file=name,pcm_sha256=sha(pcm.tobytes()),peak=int(abs(pcm).max())))
    # Linear-code distance >=3: enumerate every weight-one and weight-two data delta.
    checks=0
    for n in (3,4):
        for w in (1,2):
            for indices in itertools.combinations(range(n),w):
                for vals in itertools.product(range(1,17),repeat=w):
                    x=[0]*n
                    for i,a in zip(indices,vals): x[i]=a
                    assert sum(v!=0 for v in code(x))>=3; checks+=1
    for row in rows:
        if row['condition'] in ('clean','noise2500','query-erasure','reply-erasure'): assert row['target'] in row['returned']
        if row['condition'] in ('stale-nonce','query-two-errors','query-frame-loss'): assert not row['returned']
        if row['condition']=='omitted-target': assert row['status']==('wrong-set' if row['mode']=='compact' else 'resolved')
        if row['condition']=='wrapped-nonce': assert row['status']=='wrong-set'
        if row['condition']=='reply-two-errors': assert row['status']==('wrong-set' if row['mode']=='compact' else 'resolved')
    receipt=dict(schema='mhac-acoustic-clarification-v1',pin=PIN,blobs={**p['BLOBS'],'discriminating-reply.py':BLOB},source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,sets=serial,evaluations=len(rows),distance_checks=checks,stats=stats,specimens=specimens,limits='Constructed candidate sets; known source, length, slot clock, frame and turn boundaries. Two distinct framing tones checked, not blind acquisition. 80ms slots, same tone amplitude; actual noise samples differ for unequal lengths. No propagation/turnaround delay, replay protection, authentication, action authority or human evidence. Omitted targets deliberately share a requested symbol; stale wrap is forced nonce reuse. Full comparator scans complete catalogue, not just candidates.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Acoustic clarification</title><h1>Framed query and reply</h1><p>Synthetic aligned trials. Start at low volume. No autoplay.</p><pre>'+json.dumps(stats,indent=2)+'</pre>'
    for z in specimens: html+=f'<p>{z["file"]}<br><audio controls preload="none" src="{z["file"]}"></audio></p>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(dict(sets=serial,evaluations=len(rows),checks=checks,stats=stats)))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
