"""Refs #452 / Draft #453. Catalogue-address replies, synthetic aligned PCM only.
Usage: python catalogue-reply.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Shared exact catalogue ordering, source, length and slot clock are assumptions.
"""
import functools, hashlib, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='feba52809552355db1beb33a36dd7fdd619b2e0f'
BLOBS={'acoustic-clarification.py':'71e527852c278fb91088ed9fdcf5d7d6027426a3','discriminating-reply.py':'32ffadda8146153ebbb90ebcd343129986512de8','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401'}
SEED=452430; sha=lambda b:hashlib.sha256(b).hexdigest()
@functools.lru_cache(None)
def matrix(points,n):
    return np.array([[functools.reduce(lambda a,j:a*(x-j)*pow((i-j)%17,-1,17)%17,(j for j in points if j!=i),1) for x in range(n)] for i in points],dtype=np.int64)
def encode(data,r):
    return (np.array(data)@matrix(tuple(range(len(data))),len(data)+r)%17).tolist()
@functools.lru_cache(None)
def plans(k,n,keep):
    p=list(itertools.combinations(keep,k))
    return np.array(p),np.stack([matrix(z,n) for z in p])
def decode(obs,r):
    n=len(obs); k=n-r; keep=tuple(i for i,x in enumerate(obs) if x is not None); e=n-len(keep)
    if e>r:return None
    y=np.array([0 if x is None else x for x in obs]); p,m=plans(k,n,keep)
    words=np.einsum('bi,bij->bj',y[p],m)%17
    valid=words[2*np.count_nonzero(words[:,keep]!=y[list(keep)],axis=1)+e<=r]
    if not len(valid):return None
    assert np.all(valid==valid[0]);return valid[0,:k].tolist()
def digits(i,k):return [(i//17**j)%17 for j in range(k)]
def index(x):return sum(v*17**j for j,v in enumerate(x))
def run(root,out):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    a=runpy.run_path(str(root/'acoustic-clarification.py'));p=runpy.run_path(str(root/'discriminating-reply.py'));v=runpy.run_path(str(root/'version-bound-payload.py'));_,raw,_=v['build'](root);old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    rng=np.random.default_rng(SEED);out.mkdir(parents=True,exist_ok=False);rows=[];stats={};spec=[];checks=0
    # Exhaustive support patterns for one fixed nonzero codeword per profile, within 2t+e<=r.
    for k in (7,8):
        for r in (2,4):
            data=list(range(k));word=encode(data,r);n=len(word)
            for e in range(r+1):
                for t in range((r-e)//2+1):
                    for holes in itertools.combinations(range(n),e):
                        for errors in itertools.combinations([i for i in range(n) if i not in holes],t):
                            obs=word.copy()
                            for i in holes:obs[i]=None
                            for i in errors:obs[i]=(obs[i]+1)%17
                            assert decode(obs,r)==data;checks+=1
    conditions=('clean','noise2500','omitted','two-errors','three-errors','two-erasures','wrapped','catalogue-shift')
    serial=0
    for source,bylen in books.items():
        for length,book in bylen.items():
            width=4 if length==13 else 5;assert 17**(width-1)<len(book)<=17**width
            assert all(index(digits(i,width))==i for i in range(len(book)))
            for size in (2,4,8):
                for sample in range(2):
                    ids=sorted(map(int,rng.choice(len(book),size,False)));pos=p['query'](book,ids,'balanced');serial+=1;nonce=[serial//17,serial%17]
                    for target in ids:
                        rival=next(i for i in ids if book[i,pos]!=book[target,pos]);omitted=next(int(i) for i in np.flatnonzero(book[:,pos]==book[target,pos]) if i not in ids)
                        for ci,condition in enumerate(conditions):
                            actual=omitted if condition=='omitted' else target;sd=2500 if condition=='noise2500' else 0;seed=SEED*10000+serial*1000+ids.index(target)*20+ci*2
                            for mode in ('compact','index2','index4','full'):
                                r=4 if mode=='index4' else 2;request=nonce+[pos-3 if mode=='compact' else 16 if mode=='full' else 15]
                                qo,qpcm,qt=a['exchange'](a['code'](request),sd,seed);q=a['recover'](qo) if qo is not None else None;got=[];rt=None;rpcm=None
                                if q==request:
                                    def payload(i):
                                        if mode=='compact':return a['code'](q+[int(book[i,pos])])
                                        if mode=='full':return a['code'](q)+book[i].tolist()
                                        return encode(q+digits(i,width),r)
                                    sender=rival if condition=='wrapped' else actual;wire=payload(sender)
                                    if condition in ('two-errors','three-errors'):
                                        if mode.startswith('index'):
                                            # Change one base-17 digit; MDS minimum-distance rival.
                                            d=digits(actual,width);d[0]=(d[0]+1)%17;other_id=index(d)
                                            if other_id>=len(book):d[0]=(d[0]-2)%17;other_id=index(d)
                                            assert 0<=other_id<len(book) and other_id!=actual
                                        else:other_id=rival
                                        other=payload(other_id);diff=[i for i in range(len(wire)) if wire[i]!=other[i]];assert len(diff)>=3
                                        for i in diff[:2 if condition=='two-errors' else 3]:wire[i]=other[i]
                                    if condition=='two-erasures':wire[-2:]=[None,None]
                                    ro,rpcm,rt=a['exchange'](wire,sd,seed+1)
                                    if ro is not None:
                                        if mode=='compact':
                                            h=a['recover'](ro);got=[i for i in ids if book[i,pos]==h[3]] if h is not None and h[:3]==request else []
                                        elif mode=='full':
                                            h=a['recover'](ro[:5]);body=ro[5:];keep=[i for i,x in enumerate(body) if x is not None];e=length-len(keep)
                                            if h==request and e<=4:
                                                found=np.flatnonzero(2*np.count_nonzero(book[:,keep]!=[body[i] for i in keep],axis=1)+e<=4);got=found.tolist() if len(found)==1 else []
                                        else:
                                            h=decode(ro,r)
                                            if h is not None and h[:3]==request and index(h[3:])<len(book):got=[(index(h[3:])+int(condition=='catalogue-shift'))%len(book)]
                                status='withheld' if not got else 'wrong-set' if actual not in got else 'resolved' if len(got)==1 else 'retained';slots=qt['slots']+(rt['slots'] if rt else 0);c=stats.setdefault(mode+':'+condition,Counter());c[status]+=1;c['slots']+=slots
                                rows.append(dict(source=source,length=length,ids=ids,target=actual,mode=mode,condition=condition,request=request,decoded_query=q,returned=got,status=status,query=qt,reply=rt,slots=slots,seed=seed))
                                if serial==1 and target==ids[0] and condition in ('clean','omitted','two-errors','three-errors','catalogue-shift') and rpcm is not None:
                                    name=f'{mode}-{condition}-reply.wav';b=rpcm.tobytes()
                                    with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b)
                                    spec.append(dict(file=name,pcm_sha256=sha(b),peak=int(abs(rpcm).max())))
    for row in rows:
        m,c,s=row['mode'],row['condition'],row['status']
        if c in ('clean','noise2500','two-erasures'):assert s in ('resolved','retained')
        if m=='index4' and c in ('omitted','two-errors'):assert s=='resolved'
        if m.startswith('index') and c in ('wrapped','catalogue-shift','three-errors'):assert s=='wrong-set'
        if m=='index2' and c=='two-errors':assert s=='wrong-set'
    receipt=dict(schema='mhac-catalogue-reply-v1',pin=PIN,blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,checks=checks,sets=serial,evaluations=len(rows),stats=stats,specimens=spec,limits='Aligned PCM, known source/length and exact shared catalogue order except shifted receiver fixture. Index is a global dictionary address, not a semantic field or authentication. Two/four check symbols are systematic degree<k polynomial evaluation at distinct GF(17) points (distance r+1). Support tests use one fixed word and +1 deltas. Targeted substitutions are format-specific rivals; unequal airtime/energy. No human evidence or dialogue/action authority.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Catalogue reply</title><h1>Catalogue-address acoustic replies</h1><p>Synthetic aligned frames. Start at low volume; no autoplay.</p><pre>'+json.dumps(stats,indent=2)+'</pre>'+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>');(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(dict(checks=checks,sets=serial,evaluations=len(rows),stats=stats)))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
