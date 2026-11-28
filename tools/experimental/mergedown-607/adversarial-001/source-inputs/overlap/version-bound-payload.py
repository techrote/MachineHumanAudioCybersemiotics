"""Refs #452 / Draft #453. Synthetic fixed-length version-bound payloads.
Run: python version-bound-payload.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
"""
import hashlib, json, pathlib, runpy, sys, wave, math
import numpy as np
PIN='e500334db2d6f03ff6e788084dc09e5e3cd2d85d'
BLOBS={'version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
SEED=45231

def sha(b): return hashlib.sha256(b).hexdigest()
def build(root):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes()
        if hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()!=b: raise ValueError(f)
    c=runpy.run_path(str(root/'control-namespace.py')); u,_,_,new,names,_=c['build'](root)
    m=runpy.run_path(str(root/'migration-namespace.py')); old=m['construct'](u)[2]['relocated-cubic']
    return u,(old,new),names

def extend(w,v,mode):
    if mode=='marker': tail=np.full((len(w),5),v)
    elif mode=='polynomial':
        dif=np.stack([np.diff(w[:,:4],n=k,axis=1)[:,0] for k in range(4)],axis=1)
        x=np.array([[math.comb(j,k) for j in range(15)] for k in range(4)])
        p=dif@x%17
        assert np.array_equal(p[:,:10],w)
        tail=(p[:,10:]+v)%17
    else: raise ValueError(mode)
    return np.concatenate((w,tail),axis=1)

def decode(books,obs,e,version=None):
    if len(obs)!=15 or type(e)!=int or not 0<=e<=5 or any(x is not None and (type(x)!=int or not 0<=x<17) for x in obs): raise ValueError('invalid observation')
    if version not in (None,0,1): raise ValueError('invalid version')
    keep=[i for i,x in enumerate(obs) if x is not None]; y=[obs[i] for i in keep]
    hits=[]
    for v,w in enumerate(books):
        if version is not None and v!=version: continue
        d=np.count_nonzero(w[:,keep]!=y,axis=1)
        hits.extend((v,int(i)) for i in np.flatnonzero(d<=e)[:2])
        if len(hits)>1: return None
    return hits[0] if len(hits)==1 else None

def run(root,out):
    u,raw,names=build(root); out.mkdir(parents=True,exist_ok=False)
    index={tuple(w):i for i,w in enumerate(raw[1])}
    aliases=[(i,index[tuple(w)]) for i,w in enumerate(raw[0]) if tuple(w) in index]
    wrong=[(i,j) for i,j in aliases if i!=j]; assert len(wrong)==2031 and len(aliases)==51999
    i,j=wrong[0]; assert names[i]!=names[j]
    rng=np.random.default_rng(SEED); cases=[]
    for e,s in ((0,0),(2,0),(1,2),(0,4),(3,0),(4,0),(5,0),(2,6),(0,11)):
        for v in (0,1):
            for row in rng.choice(len(raw[v]),24,False):
                p=rng.permutation(15); delta=rng.integers(1,17,size=e)
                cases.append((e,s,v,int(row),p,delta))
    results={}; specimens=[]
    for mode in ('marker','polynomial'):
        books=tuple(extend(w,v,mode) for v,w in enumerate(raw))
        # Distinct cubic prefix bodies differ in >=7 slots. Same bodies differ in all five tail slots.
        assert all(np.count_nonzero(books[0][a]!=books[1][b])==5 for a,b in aliases)
        intra=[]
        for v,w in enumerate(books):
            d=np.count_nonzero(w[1:]!=w[0],axis=1); k=int(d.argmin())+1
            assert int(d.min())==(7 if mode=='marker' else 12)
            intra.append([0,k,int(d.min())])
        stats={}
        for e,s,v,row,p,delta in cases:
            obs=books[v][row].tolist()
            for pos in p[:s]: obs[pos]=None
            for pos,d in zip(p[s:s+e],delta): obs[pos]=(obs[pos]+int(d))%17
            for known in (False,True):
                got=decode(books,obs,e,v if known else None)
                counts=stats.setdefault(f'e{e}s{s}:{"known" if known else "union"}',[0,0,0])
                counts[0 if got==(v,row) else 1 if got is None else 2]+=1
                limit=(7 if mode=='marker' else 12) if known else 5
                if 2*e+s<limit: assert got==(v,row)
        # Explicit boundary: full tail erasure or majority replacement of an aliased body.
        a=books[0][i].tolist(); b=books[1][j].tolist(); erased=a[:10]+[None]*5
        corrupt=a[:10]+b[10:13]+a[13:]
        assert decode(books,erased,0) is None and decode(books,corrupt,2)==(1,j)
        try: decode(books,a[:10],0); raise AssertionError('truncated frame accepted')
        except ValueError: pass
        results[mode]={'internal_distance_witnesses':intra,'stats':stats,'cross_distance':5,'tail_erasure':None,'three_substitution_radius_two': [1,j]}
        for label,obs in [('old',a),('new',b),('erased',erased),('wrong',corrupt)]:
            fn=f'{mode}-{label}.wav'; u['audio'](out/fn,obs)
            with wave.open(str(out/fn),'rb') as f:
                assert f.getparams()[:4]==(1,2,16000,19200); pcm=f.readframes(19200)
            assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2').astype(int)))<=2048
            specimens.append({'file':fn,'symbols':obs,'pcm_sha256':sha(pcm)})
    receipt={'schema':'mhac-version-bound-payload-v1','pin':PIN,'blobs':BLOBS,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'rows':list(map(len,raw)),'aliases':len(aliases),'incompatible_aliases':len(wrong),'witness_rows':[i,j],'witness_meanings':[names[i],names[j]],'trials_per_mode':len(cases)*2,'axes':['correct','abstain','incorrect'],'results':results,'specimens':specimens,'limits':'Fixed known 15-slot alignment, relocated/unified only; no streaming, authentication, replay resistance or human evidence. Known version is oracle side information. Equal duration and alphabet for extended variants, not compute matched. Original 10-slot prefix remains valid in old receivers. Historical CJS equivalence untested.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    gallery=''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Version-bound payload</title><h1>Version-bound payload</h1><p>Synthetic 15-slot frames. Old and new share their first ten tones. Start at low volume. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt and replay symbols</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('aliases','incompatible_aliases','witness_rows','witness_meanings','trials_per_mode','results')},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
