"""Measurement #442: cross-format ambiguity audit, synthetic only.
Usage: python format-overlap.py PINNED_DISTRIBUTED_PROFILE.py NEW_OUTPUT
Requires NumPy. The source argument must match the exact pinned blob.
"""
import hashlib, html, itertools, json, pathlib, runpy, sys, wave
import numpy as np

PIN='28d0433bd9f8a7ad96c616f0544caa9089c8e8e6'
BLOB='a780404e8c76820976ad6fb407429ec895a6313f'
MODES=('tag-pair','free-cubic','reserved-cubic')

def key(words, mask):
    return words[:,mask] @ (17**np.arange(len(mask),dtype=np.int64))

def groups(words, ids, mask):
    keys=key(words,mask)
    unique, inv=np.unique(keys,return_inverse=True)
    lo=np.full(len(unique),len(ids)*10); hi=np.full(len(unique),-1)
    np.minimum.at(lo,inv,ids); np.maximum.at(hi,inv,ids)
    return unique,lo,hi

def query(words, mask, group):
    keys,lo,hi=group; k=key(words,mask)
    idx=np.minimum(np.searchsorted(keys,k),len(keys)-1)
    present=keys[idx]==k
    return np.where(present,lo[idx],-1),np.where(present,hi[idx],-1)

def close_pairs(a,b):
    # Each first-eight body is a cubic or lower. Different polynomials
    # disagree at >=5 of those positions. Thus all distance <=4 pairs
    # must have identical bodies. Preserve duplicate body rows in joins.
    ka,kb=key(a,tuple(range(8))),key(b,tuple(range(8)))
    order=np.argsort(kb); sortedkeys=kb[order]
    left=np.searchsorted(sortedkeys,ka,'left'); right=np.searchsorted(sortedkeys,ka,'right')
    ia=np.repeat(np.arange(len(a)),right-left)
    offsets=np.concatenate([np.arange(x,y) for x,y in zip(left,right) if x<y]) if len(ia) else np.array([],int)
    ib=order[offsets]; dist=np.count_nonzero(a[ia]!=b[ib],axis=1)
    return ia,ib,dist

def candidates(books,ids,obs,budget):
    mask=[i for i,v in enumerate(obs) if v is not None]
    return {mode:np.unique(ids[np.count_nonzero(w[:,mask]!=np.array([obs[i] for i in mask]),axis=1)<=budget]).tolist() for mode,w in books.items()}

def render(path,obs):
    n=np.arange(1280); frame=[]
    for v in obs:
        x=np.zeros(1280,dtype='<i2')
        if v is not None:
            t=n[:960]; x[:960]=np.rint(2048*np.minimum(1,np.minimum(t/80,(959-t)/80))*np.sin(2*np.pi*(400+100*v)*t/16000+.137)).astype('<i2')
        frame.append(x)
    pcm=np.concatenate(frame)
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
    with wave.open(str(path),'rb') as f:
        assert f.getparams()[:4]==(1,2,16000,12800)
        got=np.frombuffer(f.readframes(12800),dtype='<i2').reshape(10,1280)
    basis=np.exp(-2j*np.pi*np.arange(400,2001,100)[:,None]*np.arange(640)/16000)
    assert [int(np.argmax(abs(basis@x[160:800]))) if np.any(x) else None for x in got]==obs
    return hashlib.sha256(pcm.tobytes()).hexdigest()

def run(source,out):
    raw=source.read_bytes(); blob=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    if blob!=BLOB: raise ValueError('pinned source blob mismatch')
    upstream=runpy.run_path(str(source)); books,ids,p,labels,_=upstream['catalogue']()
    assert tuple(books)==MODES and len(ids)==52000
    # Independently check degree <=3 on the first eight via fourth differences.
    for w in books.values(): assert not np.any(np.diff(w[:,:8],n=4,axis=1)%17)
    profile_ids=ids+48000*p.astype(int)
    near={}; witnesses=[]; checks=0
    for a,b in itertools.combinations(MODES,2):
        ia,ib,d=close_pairs(books[a],books[b]); different=ids[ia]!=ids[ib]
        near[a+' / '+b]=[{'distance':k,'pairs':int(np.sum(d==k)),'different_meaning':int(np.sum((d==k)&different)),'different_profile_or_meaning':int(np.sum((d==k)&(profile_ids[ia]!=profile_ids[ib])))} for k in range(3)]
        for k in range(3):
            pick=np.flatnonzero((d==k)&different)
            if not len(pick): continue
            j=pick[0]; i,h=int(ia[j]),int(ib[j]); x=books[a][i].tolist(); y=books[b][h].tolist()
            obs=x.copy(); differing=[t for t in range(10) if x[t]!=y[t]]
            if k==2: obs[differing[0]]=y[differing[0]]
            budget=int(k>0)
            c=candidates(books,ids,obs,budget)
            assert int(ids[i]) in c[a] and int(ids[h]) in c[b]
            witnesses.append({'formats':[a,b],'distance':k,'rows':[i,h],'meanings':[labels[ids[i]],labels[ids[h]]],'words':[x,y],'observation':obs,'budget':budget,'candidates':c,'one_error_candidates':candidates(books,ids,obs,1)})
        # Literal complete row distances for a deterministic subset, all other rows.
        for i in np.random.default_rng(442).choice(len(ids),24,replace=False):
            literal=np.flatnonzero(np.count_nonzero(books[a][i]!=books[b],axis=1)<=2)
            assert np.array_equal(np.sort(ib[(ia==i)&(d<=2)]),literal); checks+=1
    census={}; masks_used={}
    for n in (4,6,10):
        totals={m:dict(total=0,known_unique=0,union_unique=0,union_profile_unique=0,wrong_other_unique=0) for m in MODES}
        masks_used[str(n)]=sorted(set((tuple(range(n)),tuple(range(10-n,10)),tuple(range(0,10,2))[:n]))); masks_used[str(n)]=[m for m in masks_used[str(n)] if len(m)==n]
        for mask in masks_used[str(n)]:
            g={m:groups(w,ids,mask) for m,w in books.items()}
            pg={m:groups(w,profile_ids,mask) for m,w in books.items()}
            for m,w in books.items():
                rows=[query(w,mask,g[z]) for z in MODES]; prows=[query(w,mask,pg[z]) for z in MODES]
                known=rows[MODES.index(m)]; union=np.ones(len(ids),bool); pu=union.copy(); wrong=np.zeros(len(ids),bool)
                for z,(lo,hi),(pl,ph) in zip(MODES,rows,prows):
                    union&=(lo<0)|((lo==ids)&(hi==ids)); pu&=(pl<0)|((pl==profile_ids)&(ph==profile_ids))
                    if z!=m: wrong|=(lo>=0)&(lo==hi)&(lo!=ids)
                t=totals[m]; t['total']+=len(ids); t['known_unique']+=int(np.sum(known[0]==known[1])); t['union_unique']+=int(union.sum()); t['union_profile_unique']+=int(pu.sum()); t['wrong_other_unique']+=int(wrong.sum())
                assert np.all(~pu|union)
        census[str(n)]=totals
    out.mkdir(parents=True,exist_ok=False)
    for i,w in enumerate(witnesses):
        name=f'witness-{i}.wav'; w['file']=name; w['pcm_sha256']=render(out/name,w['observation'])
    report={'schema':'mhac-format-overlap-v1','pin':PIN,'blob':BLOB,'source_sha256':hashlib.sha256(raw).hexdigest(),'audit_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'near_pairs':near,'clean_census':census,'masks':masks_used,'literal_checks':checks,'seed':442,'witnesses':witnesses,'limits':'Selected clean masks only; full-frame near-pair census exact. Closed three-format catalogue, known alignment and erasures, symbolic counts not channel probabilities. Semantic IDs collapse the two profiles; stricter profile+meaning reported separately. Wrong-other-unique counts rows with at least one wrong unique other-format interpretation, not union failures. Not authentication or human evidence.'}
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    body='<!doctype html><meta charset="utf-8"><title>Format overlap</title><h1>Cross-format ambiguity</h1><p>Original synthetic examples, opt-in playback. Start at low volume.</p>'
    for k,v in census.items():
        body+=f'<details open><summary>{k} surviving symbols</summary><pre>'+html.escape(json.dumps(v,indent=2))+'</pre></details>'
    for w in witnesses:
        body+='<details><summary>'+html.escape(str(w['formats'])+' distance '+str(w['distance']))+'</summary><audio controls preload="none" src="'+w['file']+'"></audio><pre>'+html.escape(json.dumps(w,indent=2))+'</pre></details>'
    (out/'index.html').write_text(body+'<p><a href="receipt.json">Complete receipt</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'near_pairs':near,'clean_census':census,'literal_checks':checks,'witnesses':len(witnesses)},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
