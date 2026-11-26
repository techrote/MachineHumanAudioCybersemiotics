"""Grammar #452: migration namespaces, synthetic only. Python 3 + NumPy.
CLI: python migration-namespace.py PINNED_DISTRIBUTED_PROFILE.py NEW_OUTPUT
No changes to existing encoders. Semantic IDs deliberately collapse profiles.
"""
import hashlib, itertools as it, json, pathlib, runpy, sys, wave, html
import numpy as np

PINS={'grammar':'28d0433bd9f8a7ad96c616f0544caa9089c8e8e6','measurement':'beb414f2a501e5ca1df825c53d7cb5d0b81742c7','adversarial':'8f75cb3484fedab4017de56a3a7485a718507690'}
BLOB='a780404e8c76820976ad6fb407429ec895a6313f'
SEED=45228

def load(source):
    raw=source.read_bytes()
    if hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()!=BLOB: raise ValueError('pinned source mismatch')
    return runpy.run_path(str(source))

def bodykey(w): return w[:,:8] @ 17**np.arange(8,dtype=np.int64)

def construct(u):
    b,ids,p,labels,_=u['catalogue'](); old=b['tag-pair']; free=b['free-cubic']; x=np.arange(10,dtype=np.int64)
    groups={}
    for k,i in zip(bodykey(old),ids): groups.setdefault(int(k),set()).add(int(i))
    bad=np.array([bool(groups.get(int(k),set())-{int(i)}) for k,i in zip(bodykey(free),ids)])
    # Monic quartic vanishes at all four systematic coordinates.
    g=np.prod(x[None,:]-np.array(u['POS'])[:,None],axis=0)%17
    uniform=(free+g)%17; selective=free.copy(); selective[bad]=uniform[bad]
    # Alternative: relocate only incompatible rows to unused cubic bodies.
    coeff=np.array(list(it.product(range(17),repeat=4)),dtype=np.int64)
    allwords=(coeff @ x[None,:]**np.arange(4)[:,None])%17
    spare=allwords[~np.isin(bodykey(allwords),np.union1d(bodykey(old),bodykey(free)))]
    relocated=free.copy(); relocated[bad]=spare[:int(bad.sum())]
    modes={'uniform-quartic':uniform,'selective-quartic':selective,'relocated-cubic':relocated}
    for name,w in modes.items():
        assert len(np.unique(w,axis=0))==len(ids)
        assert not np.any(np.diff(w,n=5,axis=1)%17)
        if name=='relocated-cubic': assert not np.any(np.diff(w,n=4,axis=1)%17)
        else: assert np.array_equal(w[:,u['POS']],free[:,u['POS']])
        for k,i in zip(bodykey(w),ids): assert not (groups.get(int(k),set())-{int(i)})
    return old,free,modes,ids,p,labels,bad,g,len(spare)

def key(w,mask): return w[:,mask] @ 17**np.arange(len(mask),dtype=np.int64)

def cross(old,new,ids,n):
    # New projections with >=5 observations are injective (degree <=4).
    # Each old row can therefore match at most one new row per mask.
    pairs=0; witness=None
    for mask in it.combinations(range(10),n):
        a=key(old,mask); b=key(new,mask); order=np.argsort(b); sortedb=b[order]
        assert not np.any(sortedb[1:]==sortedb[:-1])
        j=np.minimum(np.searchsorted(sortedb,a),len(b)-1); h=order[j]
        hit=np.flatnonzero((a==b[h])&(ids!=ids[h])); pairs+=len(hit)
        if len(hit) and witness is None:
            i=int(hit[0]); k=int(h[i]); witness=(i,k,int(np.count_nonzero(old[i]!=new[k])))
    return int(pairs),witness

def candidates(w,ids,obs,budget):
    mask=[i for i,v in enumerate(obs) if v is not None]
    return set(map(int,ids[np.count_nonzero(w[:,mask]!=[obs[i] for i in mask],axis=1)<=budget]))

def run(source,out):
    u=load(source); old,free,modes,ids,p,labels,bad,g,spare=construct(u)
    out.mkdir(parents=True,exist_ok=False); results={}; rng=np.random.default_rng(SEED); specimens=[]
    # Same rows, masks and symbol deltas in all modes. No fitted parameters.
    trials=[(int(i),tuple(sorted(rng.choice(10,n,replace=False))),int(rng.integers(n)),int(rng.integers(1,17))) for n in (4,5,6,8,9,10) for i in rng.choice(len(ids),32,replace=False)]
    for name,w in {'free-cubic':free,**modes}.items():
        r={'unchanged_frames':[int(np.count_nonzero(np.all(w==free,axis=1)&(p==v))) for v in (0,1)],'unchanged_systematic_rows':int(np.count_nonzero(np.all(w[:,u['POS']]==free[:,u['POS']],axis=1))),'symbol_changes':int(np.count_nonzero(w!=free)),'samples':{}}
        if name!='free-cubic':
            count,wit=cross(old,w,ids,6)
            # Degree bound and body exclusion rule forbid semantic distance <4;
            # hence each six-coordinate hit represents exactly one distance-4 pair.
            assert wit is None or wit[2]==4
            r['distance4_pairs']=count
            if not count:
                count,wit=cross(old,w,ids,5); assert wit is None or wit[2]==5
                r['distance5_pairs']=count
            r['cross_witness']=wit
            if wit is not None:
                i,k,d=wit; assert ids[i]!=ids[k]
                # Outside guaranteed boundary: split differing symbols between the origins.
                diff=np.flatnonzero(old[i]!=w[k]); obs=old[i].tolist()
                for j in diff[:d//2]: obs[j]=int(w[k,j])
                budget=d-d//2; got=candidates(old,ids,obs,budget)|candidates(w,ids,obs,budget)
                assert {int(ids[i]),int(ids[k])}<=got
                for suffix,word in [('old',old[i].tolist()),('new',w[k].tolist()),('ambiguous',obs)]:
                    fn=f'{name}-{suffix}.wav'; u['audio'](out/fn,word)
                    with wave.open(str(out/fn),'rb') as f:
                        assert f.getparams()[:4]==(1,2,16000,12800); pcm=f.readframes(12800)
                    assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2')))==2048
                    specimens.append({'file':fn,'symbols':word,'pcm_sha256':hashlib.sha256(pcm).hexdigest(),'old_meaning':labels[ids[i]],'new_meaning':labels[ids[k]],'ambiguity_budget':budget})
        for i,mask,j,delta in trials:
            for origin,a,b in [('old',old,w),('new',w,old)]:
                obs=[int(a[i,k]) if k in mask else None for k in range(10)]
                obs[mask[j]]=(obs[mask[j]]+delta)%17
                local=candidates(a,ids,obs,1); other=candidates(b,ids,obs,1); union=local|other
                assert int(ids[i]) in local
                k=f'{origin}:{len(mask)}'; counts=r['samples'].setdefault(k,[0,0,0])
                counts[0]+=1; counts[1]+=len(local)==1; counts[2]+=len(union)==1
                if name!='free-cubic' and len(mask)>=9: assert not (other-{int(ids[i])})
                if name=='relocated-cubic' and len(mask)>=8: assert not (other-{int(ids[i])})
        results[name]=r
    receipt={'schema':'mhac-migration-namespace-v1','pins':PINS,'upstream_blob':BLOB,'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'seed':SEED,'unsafe_free_rows_by_profile':[int(np.count_nonzero(bad&(p==v))) for v in (0,1)],'unused_cubic_bodies':spare,'quartic_offset':g.tolist(),'results':results,'sample_counts':'total, known format unique, union unique; exactly one substitution, selected random masks; shared semantic IDs','specimens':specimens,'limits':'Only original tag-pair plus one chosen replacement. Old free/reserved not simultaneously enabled. Closed catalogue; aligned slots; no authentication, physical listening or human evidence. Equal duration 800ms and nominal amplitude, not exact energy/compute. Quartic cross distance >=4, relocated cross >=5; legacy tag internal ambiguities remain.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Migration namespace</title><h1>Migration namespace</h1><p>Original synthetic PCM; start at low volume. No autoplay.</p>'+''.join('<h2>'+s['file']+'</h2><p>'+html.escape(str((s['old_meaning'],s['new_meaning'])))+'</p><audio controls preload="none" src="'+s['file']+'"></audio>' for s in specimens)+'<p><a href="receipt.json">Receipt</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('unsafe_free_rows_by_profile','unused_cubic_bodies','quartic_offset','results')},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
