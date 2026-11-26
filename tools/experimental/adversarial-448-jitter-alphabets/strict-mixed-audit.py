"""Adversarial #448, synthetic strict identity mixed-fault census.
python strict-mixed-audit.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
No modification to upstream catalogues; relocation is a local diagnostic control.
"""
import collections as C, hashlib, itertools as I, json, pathlib, runpy, sys, wave
import numpy as np

PINS={'grammar':'b248075765aa1f47e2aaf7af86349a11b989c0f1','measurement':'dfa83c9af0e4fc30703ee3e8523f51a97d2e3105','parent':'8f75cb3484fedab4017de56a3a7485a718507690','main':'495a98ca12bae467a507031f04931aa4254b1866'}
BLOBS={'distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1'}
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(root):
    for name,b in BLOBS.items():
        raw=(root/name).read_bytes()
        if hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()!=b: raise ValueError('pinned blob mismatch: '+name)
    m=runpy.run_path(str(root/'migration-namespace.py')); u=m['load'](root/'distributed-profile.py')
    return m,u

def near(a,b,key,same):
    # For cubic first-eight bodies, distinct bodies differ in >=5 positions.
    # Thus all pairs at distance <=4 must share a body. Preserve duplicates.
    groups=C.defaultdict(list)
    for j,k in enumerate(key(b)): groups[int(k)].append(j)
    return [(i,j,int(np.count_nonzero(a[i]!=b[j]))) for i,k in enumerate(key(a)) for j in groups[int(k)] if (not same or i<j)]

def faults(a,b,e,s):
    # Enumerate literal origin/fault descriptors, retaining duplicates only once.
    diff=set(np.flatnonzero(a!=b).tolist()); result=set()
    for mask in I.combinations(range(10),s):
        visible=diff-set(mask); d=len(visible)
        if not e:
            if d==0: result.add((mask,-1,-1))
        elif d<=2:
            for k in range(10):
                if k in mask: continue
                for v in range(17):
                    if v==a[k]: continue
                    if d-int(k in visible)+int(v!=b[k])<=1: result.add((mask,k,v))
    return result

def census(old,new,ids,key,e,s):
    books=[old,new]; pairs=[(0,i,0,j,d) for i,j,d in near(old,old,key,True)]+[(0,i,1,j,d) for i,j,d in near(old,new,key,False) if i!=j]
    counts=C.Counter(); events=C.defaultdict(set)
    for f,i,g,j,d in pairs:
        if d>2*e+s: continue
        kind='semantic' if ids[i]!=ids[j] else 'profile_only'
        counts[f'{"internal" if f==g else "cross"}:{kind}:d{d}']+=1
        for x,y,z,w in ((f,i,g,j),(g,j,f,i)):
            fs=faults(books[x][y],books[z][w],e,s)
            assert fs
            for scope in ('all','cross') if x!=z else ('all',):
                events[x,y,scope,'strict'].update(fs)
                if kind=='semantic': events[x,y,scope,'semantic'].update(fs)
    sums=C.Counter()
    for (f,i,scope,kind),v in events.items(): sums[f'{f}:{scope}:{kind}']+=len(v)
    return {'pairs':dict(sorted(counts.items())),'ambiguous_origin_faults':dict(sorted(sums.items())),'denominator_per_format':len(ids)*len(list(I.combinations(range(10),s)))*((10-s)*16 if e else 1)}

def run(root,out):
    m,u=load(root); old,free,modes,ids,p,labels,bad,g,sp=m['construct'](u); new=modes['relocated-cubic']; key=m['bodykey']
    assert all(not np.any(np.diff(w[:,:8],n=4,axis=1)%17) for w in (old,new))
    cross=[(i,j,d) for i,j,d in near(old,new,key,False) if i!=j]; assert cross==[(48000,0,2)]
    # Strict repair control: first unused cubic in lexicographic coefficient order.
    coeff=np.array(list(I.product(range(17),repeat=4)),dtype=np.int64); x=np.arange(10); words=(coeff@x[None,:]**np.arange(4)[:,None])%17
    spare=words[~np.isin(key(words),np.union1d(key(old),np.union1d(key(free),key(new))))]
    patched=new.copy(); patched[0]=spare[0]
    assert not np.any(np.diff(patched,n=4,axis=1)%17) and len(np.unique(patched,axis=0))==len(ids)
    assert not [(i,j,d) for i,j,d in near(old,patched,key,False) if i!=j]
    results={}
    for name,b in [('pinned',new),('one_row_control',patched)]:
        for e,s in ((1,0),(0,2),(1,2)):
            results[f'{name}:e{e}s{s}']=census(old,b,ids,key,e,s)
    # Literal full-catalogue validation: exhaustive masks on the strict witness
    # with a deterministic sample of substitutions, plus an internal semantic pair.
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(44830); checks=0; specimens=[]
    pairs=[(48000,0),next((i,j) for i,j,d in near(old,old,key,True) if ids[i]!=ids[j])]
    for a,b,tag in [(old[pairs[0][0]],new[0],'profile'),(old[pairs[1][0]],old[pairs[1][1]],'semantic')]:
        for e,s in ((1,0),(0,2),(1,2)):
            fs=faults(a,b,e,s)
            for mask in I.combinations(range(10),s):
                for _ in range(2):
                    k=int(rng.choice([j for j in range(10) if j not in mask])) if e else -1
                    v=(int(a[k])+int(rng.integers(1,17)))%17 if e else -1
                    obs=a.copy(); obs[k]=v if e else obs[k]; keep=[j for j in range(10) if j not in mask]
                    assert ((mask,k,v) in fs)==(np.count_nonzero(obs[keep]!=b[keep])<=e); checks+=1
            mask,k,v=min(fs); obs=[None if j in mask else int(a[j]) for j in range(10)]
            if e: obs[k]=v
            keep=[j for j in range(10) if obs[j] is not None]
            for name,w in [('tag',old),('relocated',new),('control',patched)]:
                got=np.flatnonzero(np.count_nonzero(w[:,keep]!=[obs[j] for j in keep],axis=1)<=e)
                if name=='tag': assert (pairs[0][0] if tag=='profile' else pairs[1][0]) in got
                if name=='relocated' and tag=='profile': assert 0 in got
                if name=='control' and tag=='profile': assert 0 not in got
                checks+=1
            fn=f'{tag}-e{e}s{s}.wav'; u['audio'](out/fn,obs)
            with wave.open(str(out/fn),'rb') as f:
                assert f.getparams()[:4]==(1,2,16000,12800); pcm=f.readframes(12800)
            specimens.append({'file':fn,'observation':obs,'pcm_sha256':sha(pcm),'peak':int(np.max(np.abs(np.frombuffer(pcm,dtype='<i2'))))})
    receipt={'schema':'mhac-strict-mixed-audit-v1','pins':PINS,'blobs':BLOBS,'seed':44830,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'results':results,'control_row0':patched[0].tolist(),'original_row0':new[0].tolist(),'checks':checks,'specimens':specimens,'limits':'Exact finite aligned-symbol census; one tag format plus one relocated replacement only. Exactly e substitutions and s known erasures; receiver radius e. Strict identity=row index, not outer format. Original tag internal conflicts persist. Local diagnostic control, not a proposed accepted protocol. No human data, authentication, streaming or noisy extraction; same duration/alphabet/nominal peak, not energy or compute matched.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
