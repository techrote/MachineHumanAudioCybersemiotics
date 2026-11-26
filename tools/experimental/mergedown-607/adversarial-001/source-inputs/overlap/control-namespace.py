"""Refs #452 / Draft #453. Grammars lane, synthetic aligned symbols only.
Run: python control-namespace.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
Historical control rank rules transcribed from the pinned CJS sources; those
CJS programs are not executed here. The new lifted format is ten slots only.
"""
import hashlib, itertools as it, json, pathlib, runpy, sys, wave, html
import numpy as np
PARENT='b248075765aa1f47e2aaf7af86349a11b989c0f1'
PINS={'main':'495a98ca12bae467a507031f04931aa4254b1866','grammar':PARENT,'measurement':'dfa83c9af0e4fc30703ee3e8523f51a97d2e3105','adversarial':'09654d45a051960e8f7a27d51d82469f9d1e7b8e'}
BLOBS={'migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','systematic-mds.cjs':'3e74ca6f76b0e9fdb267c5b4e5734828ca27ddf3','algebraic-binding.cjs':'7415235429fd86aa96bde3f69bcfe10cf5eb8fa2','clarification-controls.cjs':'9434b7134f23c54e3870f78efcc84fa145a70d2d','transaction-clarification.cjs':'37bd277c96b08bff10465b17de246bb570c68d09','epoch-fence.cjs':'311aa5e8d621238eec47d238861e8bec1bb02a94','typed-negative.cjs':'9de937800542e9af3ea3ec3fe3c58e9a74b8e3b0','response-revisions.cjs':'9592ff3004db7763dceb3e3164b9455b102e1cef','terminal-responses.cjs':'4d79022bf88c07ad1dba8e7817b5e01d2c823a90','terminal-receipts.cjs':'96571cc8c24318e8f97e6bacdce033c1e7904f59','conflict-certificate.cjs':'dae13404d68c00bbe537d128802a1848aac2d952'}
SEED=45229
POS=(0,1,4,5); POW=np.array([4913,289,17,1]); X=np.arange(10)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def rank(w): return w[:,POS]@POW
def controls(u):
    # Earlier terminal, ACK, quote and certificate are already in the 52k data book.
    return {'clause':[k for k in range(17**4) if u['syntax'](u['digits'](k,4))],
      'clarification':[a*4913+b*289+c*17+d for b in range(2) for c in range(8) for a,ds in ((15,[0]),(16,range(17))) for d in ds],
      'transaction':[(15+k//4335)*4913+(2+k//289%15)*289+k%289 for k in range(4896)],
      'epoch':list(range(16*4913+4*289,16*4913+4*289+3504)),
      'negative':list(range(14*4913+15*289,14*4913+15*289+576)),
      'revision':list(range(13*4913,13*4913+3840))}
def build(root):
    for name in ('migration-namespace.py','distributed-profile.py'):
        raw=(root/name).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==BLOBS[name]
    m=runpy.run_path(str(root/'migration-namespace.py')); u=m['load'](root/'distributed-profile.py')
    old,free,modes,ids,p,labels,*_=m['construct'](u); relocated=modes['relocated-cubic']
    coeff=np.array(list(it.product(range(17),repeat=4))); allwords=coeff@X[None,:]**np.arange(4)[:,None]%17
    lookup=allwords[np.argsort(rank(allwords))]; assert np.array_equal(rank(lookup),np.arange(17**4))
    families=controls(u); cr=np.concatenate(list(families.values())); assert len(cr)==len(np.unique(cr))
    names=[(str(labels[int(i)]),int(v)) for i,v in zip(ids,p)]+[(kind,int(k)) for kind,ks in families.items() for k in ks]
    assert len(names)==len(set(names))
    naive=np.vstack((relocated,lookup[cr])); data_r=rank(relocated); old_r=rank(old)
    oldgroups={}
    for i,k in enumerate(old_r): oldgroups.setdefault(int(k),[]).append(i)
    strict_bad=np.array([any(j!=i for j in oldgroups.get(int(k),[])) for i,k in enumerate(data_r)])
    data_bad=strict_bad|np.isin(data_r,cr); control_bad=np.isin(cr,old_r)
    bad=np.concatenate((data_bad,control_bad))
    unused=np.setdiff1d(np.arange(17**4),np.unique(np.concatenate((old_r,rank(free),rank(naive)))))
    assert len(unused)>=bad.sum()
    fixed=naive.copy(); fixed[bad]=lookup[unused[:bad.sum()]]
    assert len(np.unique(rank(fixed)))==len(fixed)
    assert not np.any(np.diff(fixed,n=4,axis=1)%17)
    assert not np.any(np.diff(old[:,:8],n=4,axis=1)%17)
    assert not np.intersect1d(rank(fixed[:52000]),cr).size
    assert not [(i,j) for i,k in enumerate(rank(fixed)) for j in oldgroups.get(int(k),[]) if i!=j]
    info={'family_counts':{k:len(v) for k,v in families.items()},'strict_prior_rows':np.flatnonzero(strict_bad).tolist(),'data_relocated':int(data_bad.sum()),'control_relocated':int(control_bad.sum()),'naive_duplicate_words':len(naive)-len(np.unique(rank(naive))),'naive_incompatible_tag_pairs':sum(j!=i for i,k in enumerate(rank(naive)) for j in oldgroups.get(int(k),[])),'free_unchanged':int(np.all(fixed[:52000]==free,axis=1).sum()),'previous_relocated_unchanged':int((~data_bad).sum()),'control_prefix_unchanged':int((~control_bad).sum()),'unallocated_cubic_rows':17**4-len(fixed),'allocation_spares_before':len(unused),'retired_free_control_collisions':int(np.intersect1d(rank(free),rank(fixed[52000:])).size),'family_collisions':{k:{'prior_data':int(np.intersect1d(v,data_r).size),'old_tag':int(np.isin(old_r,v).sum())} for k,v in families.items()}}
    return u,old,naive,fixed,names,info

def decode(book,obs,e,old=None):
    """Return a unique strict identity row, else None. Optional original tag menu."""
    if len(obs)!=10 or type(e)!=int or not 0<=e<=3 or any(v is not None and (type(v)!=int or not 0<=v<17) for v in obs): raise ValueError('invalid observation')
    keep=[i for i,v in enumerate(obs) if v is not None]; y=[obs[i] for i in keep]
    got=set(np.flatnonzero(np.count_nonzero(book[:,keep]!=y,axis=1)<=e).tolist())
    if old is not None: got.update(np.flatnonzero(np.count_nonzero(old[:,keep]!=y,axis=1)<=e).tolist())
    return next(iter(got)) if len(got)==1 else None

def run(root,out):
    u,old,naive,fixed,names,info=build(root); out.mkdir(parents=True,exist_ok=False)
    # Exhaustive clean four-symbol projection injectivity; exact finite checks.
    for mask in it.combinations(range(10),4):
        assert len(np.unique(fixed[:,mask]@(17**np.arange(4))))==len(fixed)
    rng=np.random.default_rng(SEED); results={}; cases=[]
    for e,s in ((0,6),(1,4),(2,2),(3,0),(1,2)):
        trials=np.concatenate((rng.choice(52000,48,False),rng.choice(np.arange(52000,len(fixed)),48,False)))
        stats=[0,0,0,0]
        for i in trials:
            i=int(i); obs=fixed[i].tolist(); positions=rng.permutation(10)
            for j in positions[:s]: obs[j]=None
            for j in positions[s:s+e]: obs[j]=(obs[j]+int(rng.integers(1,17)))%17
            assert decode(fixed,obs,e)==i; stats[0]+=1
            if 2*e+s<5:
                assert decode(fixed,obs,e,old)==i; stats[1]+=1
            else:
                v=decode(fixed,obs,e,old); assert v in (i,None); stats[2]+=v==i; stats[3]+=v is None
        results[f'e{e}s{s}']=stats
    # Exact wrong-identity clean witness for naive lift, then matched repaired observations.
    _,inv,counts=np.unique(rank(naive),return_inverse=True,return_counts=True)
    i,j=map(int,np.flatnonzero(inv==np.flatnonzero(counts>1)[0])); assert i<52000<=j
    assert decode(naive,naive[i].tolist(),0) is None
    for title,word,expected in [('naive-alias',naive[i],None),('repaired-data',fixed[i],i),('repaired-control',fixed[j],j)]:
        obs=word.tolist(); got=decode(naive if title=='naive-alias' else fixed,obs,0); assert got==expected
        fn=title+'.wav'; u['audio'](out/fn,obs)
        with wave.open(str(out/fn),'rb') as f:
            assert f.getparams()[:4]==(1,2,16000,12800); pcm=f.readframes(12800)
        assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2')))<=2048
        cases.append({'file':fn,'observation':obs,'identity':None if got is None else names[got],'pcm_sha256':sha(pcm)})
    receipt={'schema':'mhac-control-namespace-v1','pins':PINS,'source_blobs':BLOBS,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'info':info,'unified_rows':len(fixed),'projection_masks':210,'projection_rows':210*len(fixed),'sample_results':results,'sample_axes':['unified correct','tag-union guaranteed correct','tag-union outside-bound correct','tag-union outside-bound abstain'],'witness_identities':[names[i],names[j]],'specimens':cases,'limits':'Known ten-slot alignment and bounded faults; control rank formulas transcribed, not original CJS execution. No eight-slot auto-detection, no retired free/reserved menu, no authentication, physical listening or human evidence. Same nominal duration, alphabet, peak within ten-slot comparison, not energy or compute matched. Tag internal distance-two failures persist.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Unified control namespace</title><h1>Unified control namespace</h1><p>Synthetic only. Start playback at low volume. No autoplay.</p><p>Naive alias: '+html.escape(str(receipt['witness_identities']))+'</p>'+''.join('<h2>'+s['file']+'</h2><p>'+html.escape(str(s['identity']))+'</p><audio controls preload="none" src="'+s['file']+'"></audio>' for s in cases)+'<p><a href="receipt.json">Receipt</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
