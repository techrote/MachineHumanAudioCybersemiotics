"""Refs #452 / Draft #453. Synthetic candidate-set clarification reply.
Usage: python discriminating-reply.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Trusted out-of-band query and known PCM alignment; no action authority.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='b9c0af501b38ac516f194a362c8688c95657b32b'
BLOBS={'version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
SEED=452410; S=1280; F=16000
sha=lambda b:hashlib.sha256(b).hexdigest()

def query(book, ids, mode):
    if not 2<=len(ids)<=8 or len(set(ids))!=len(ids): raise ValueError('candidate set')
    if any(type(i)!=int or not 0<=i<len(book) for i in ids): raise ValueError('identity')
    scores=[]
    for p,col in enumerate(book[ids].T):
        counts=Counter(map(int,col)).values()
        if len(counts)>1: scores.append((max(counts),sum(n*n for n in counts),p))
    return (min(scores)[2] if mode=='balanced' else scores[0][2])

def tag(context):
    x=int(sha(json.dumps(context,separators=(',',':')).encode()),16)%289
    return [x//17,x%17]

def reply(context, book, target):
    return tag(context)+[int(book[target,context[4]])]*3

def narrow(context, book, observed):
    if len(observed)!=5 or observed[:2]!=tag(context): return []
    votes=Counter(v for v in observed[2:] if v is not None)
    if not votes: return []
    v,n=votes.most_common(1)[0]
    return [i for i in context[3] if book[i,context[4]]==v] if n>=2 else []

T=np.arange(S//2); ENV=np.minimum(1,np.minimum(T/30,(len(T)-1-T)/30))
TONES=np.rint(1500*ENV*np.sin(2*np.pi*np.arange(400,2001,100)[:,None]*T/F+.137)).astype(np.int16)
BASIS=np.exp(-2j*np.pi*np.arange(400,2001,100)[:,None]*np.arange(400)/F)
def render(tokens,noise):
    x=np.zeros((5,S),float)
    for k,v in enumerate(tokens):
        if v is not None: x[k,:S//2]=TONES[v]
    return np.clip(np.rint(x+noise),-32768,32767).astype('<i2')

def observe(pcm):
    scores=abs(pcm[:,80:480]@BASIS.T)*2/400
    return [int(a.argmax()) if a.max()>=600 else None for a in scores]

def run(root,out):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b,f
    v=runpy.run_path(str(root/'version-bound-payload.py')); _,raw,_=v['build'](root); old,new=raw
    long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED); stats={}; traces=[]; specimens=[]; sets=0; collision=None
    conditions=('clean','noise500','noise2500','erase1','erase2','substitute1','substitute2','wrong-tag')
    for source in (0,1):
        for length,book in books[source].items():
            for size in (2,4,8):
                for sample in range(8):
                    origin=int(rng.integers(len(book))); d=np.count_nonzero(book!=book[origin],axis=1); d[origin]=length+1
                    pool=np.argsort(d,kind="stable")[:32] if sample<4 else np.delete(np.arange(len(book)),origin)
                    ids=sorted([origin,*map(int,rng.choice(pool,size-1,False))]); sets+=1
                    for mode in ('first','balanced'):
                        pos=query(book,ids,mode); context=[PIN,source,length,ids,pos,sets]
                        assert max(Counter(map(int,book[ids,pos])).values())<size
                        if collision is None:
                            for nonce in range(sets+1,sets+10000):
                                stale=context[:-1]+[nonce]
                                if tag(stale)==tag(context):
                                    rival=next(i for i in ids if book[i,pos]!=book[origin,pos]); received=reply(stale,book,rival)
                                    got=narrow(context,book,received); assert origin not in got and rival in got
                                    collision=dict(current=context,stale=stale,origin=origin,stale_target=rival,tag=tag(context),returned=got); break
                        for target in ids:
                            rival=next(i for i in ids if book[i,pos]!=book[target,pos]); val=int(book[rival,pos])
                            clean=reply(context,book,target)
                            for ci,condition in enumerate(conditions):
                                tokens=clean.copy(); ns=SEED*100000+sets*1000+ids.index(target)*10+ci
                                if condition=='erase1': tokens[2]=None
                                if condition=='erase2': tokens[2:4]=[None,None]
                                if condition=='substitute1': tokens[2]=val
                                if condition=='substitute2': tokens[2:4]=[val,val]
                                if condition=='wrong-tag': tokens[0]=(tokens[0]+1)%17
                                sd={'noise500':500,'noise2500':2500}.get(condition,0)
                                pcm=render(tokens,np.random.default_rng(ns).normal(0,sd,(5,S)))
                                obs=observe(pcm); got=narrow(context,book,obs)
                                status='withheld' if not got else 'wrong-set' if target not in got else 'resolved' if len(got)==1 else 'retained'
                                if condition in ('clean','erase1','substitute1'): assert target in got
                                if condition in ('erase2','wrong-tag'): assert not got
                                if condition=='substitute2': assert got and target not in got
                                k=f'{mode}:{size}:{condition}'; stats.setdefault(k,Counter()).update([status]); stats[k]['remaining']+=len(got)
                                row=dict(context=context,mode=mode,cluster=sample<4,target=target,condition=condition,noise_seed=ns,tokens=tokens,observed=obs,returned=got,status=status,pcm_sha256=sha(pcm.tobytes())); traces.append(row)
                                if sets==1 and target==origin and mode=='balanced' and condition in ('clean','erase1','substitute2','wrong-tag'):
                                    name=condition+'.wav'
                                    with wave.open(str(out/name),'wb') as f: f.setparams((1,2,F,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
                                    specimens.append(dict(file=name,peak=int(abs(pcm).max()),**row))
    assert collision is not None
    # Exhaustive majority checks for all alphabet values and all one-symbol substitutions/erasures.
    checks=0
    for a in range(17):
        for p in range(3):
            for b in [None,*range(17)]:
                obs=[a]*3; obs[p]=b; assert Counter(v for v in obs if v is not None).most_common(1)[0][0]==a; checks+=1
    receipt=dict(schema='mhac-discriminating-reply-v1',pin=PIN,blobs=BLOBS,seed=SEED,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,sets=sets,evaluations=len(traces),majority_checks=checks,stats=stats,stale_collision=collision,specimens=specimens,limits='Trusted exact candidate-set query delivered out of band; known five-slot alignment, no acoustic query or framing, no authentication or replay protection. Conditional narrowing only, never action authorization. Candidate sets constructed, not outputs from a blind acoustic trial. Both policies use five slots and same amplitude; noise draws matched, targeted corruption chooses a rival symbol per query. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Discriminating reply</title><h1>Candidate-set clarification</h1><p>Synthetic only. Known alignment, trusted query. Start at low volume. No automatic playback.</p><pre>'+json.dumps(stats,indent=2)+'</pre>'
    for s in specimens: html+=f'<h2>{s["file"]}</h2><audio controls preload="none" src="{s["file"]}"></audio><pre>'+json.dumps(s,indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(sets=sets,evaluations=len(traces),checks=checks,stats=stats,collision=collision)))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
