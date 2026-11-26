"""Refs #452 / #453. Synthetic aligned bootstrap vocabulary, not a dialogue protocol.
Usage: python version-bridge.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np
PIN='aca863378e825b26921388cfaab890f9eac86279'
BLOBS={'control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
PINS={'grammar':PIN,'measurement':'8b9abd7ccc7b2d8c4bd278b1233c8d9183cdbc51','adversarial':'f4ecd30005c123d39452cac7937ca6266f791179','interaction':'3defc6747918bf17598f153742f7fd80530ec101','main':'495a98ca12bae467a507031f04931aa4254b1866'}
SEED=45230
VERBS=('PROPOSE','ACCEPT','COMMIT','RECEIPT','ABORT')
IDENTITIES=list(itertools.product(VERBS,('relocated-to-unified','unified-to-relocated'),range(16)))
def sha(b): return hashlib.sha256(b).hexdigest()
def build(root):
    for f,b in BLOBS.items():
        raw=(root/f).read_bytes()
        if hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()!=b: raise ValueError('source mismatch '+f)
    c=runpy.run_path(str(root/'control-namespace.py')); u,old,naive,fixed,names,_=c['build'](root)
    m=runpy.run_path(str(root/'migration-namespace.py')); _,free,modes,*_=m['construct'](u)
    books, *_=u['catalogue'](); books.update(modes); books['unified']=fixed
    assert np.array_equal(books['tag-pair'],old) and np.array_equal(books['free-cubic'],free)
    books['historical-eight']=naive[52000:,:8]
    x=np.arange(10); coeff=np.array(list(itertools.product(range(17),repeat=4)))
    allwords=coeff@x[None,:]**np.arange(4)[:,None]%17
    def key(w): return w[:,:8] @ 17**np.arange(8,dtype=np.int64)
    k=key(allwords); local=allwords[~np.isin(k,key(fixed))]
    global_spare=allwords[~np.isin(k,np.unique(np.concatenate([key(w) for w in books.values()])))]
    n=len(IDENTITIES); assert len(global_spare)>=n
    return u,books,local[:n],global_spare[:n],len(local),len(global_spare)
def candidates(book,obs,e):
    if len(obs)!=10 or type(e)!=int or not 0<=e<=3 or any(v is not None and (type(v)!=int or not 0<=v<17) for v in obs): raise ValueError('invalid observation')
    mask=[i for i,v in enumerate(obs) if v is not None]
    return np.flatnonzero(np.count_nonzero(book[:,mask]!=[obs[i] for i in mask],axis=1)<=e).tolist()
def decode(bridge,obs,e):
    hits=candidates(bridge,obs,e)
    return IDENTITIES[hits[0]] if len(hits)==1 else None
def census(bridge,books):
    result={}
    for name,w in books.items():
        hist=np.zeros(w.shape[1]+1,dtype=np.int64); best=w.shape[1]+1; witness=None
        for i,word in enumerate(bridge):
            d=np.count_nonzero(w!=word[:w.shape[1]],axis=1); hist+=np.bincount(d,minlength=len(hist)); j=int(d.argmin())
            if d[j]<best: best=int(d[j]); witness=[i,j,word.tolist(),w[j].tolist()]
        result[name]={'minimum':best,'distance_counts':hist.tolist(),'witness':witness,'pairs':int(hist.sum())}
    return result
def run(root,out):
    u,books,local,bridge,nlocal,nglobal=build(root); out.mkdir(parents=True,exist_ok=False)
    baseline=census(local,books); robust=census(bridge,books)
    assert all(v['minimum']>=5 for v in robust.values())
    for mask in itertools.combinations(range(10),4): assert len(np.unique(bridge[:,mask]@17**np.arange(4)))==len(bridge)
    rng=np.random.default_rng(SEED); trials={}
    for e,s in ((0,0),(1,2),(2,0),(3,0),(0,6)):
        ok=0
        for i,word in enumerate(bridge):
            obs=word.tolist(); p=rng.permutation(10)
            for j in p[:s]: obs[j]=None
            for j in p[s:s+e]: obs[j]=(obs[j]+int(rng.integers(1,17)))%17
            assert decode(bridge,obs,e)==IDENTITIES[i]; ok+=1
        trials[f'e{e}s{s}']=ok
    # At distance five, one origin can be transformed into the rival's radius-two ball by three substitutions.
    name=next(k for k,v in robust.items() if v['minimum']==5 and k!='historical-eight')
    i,j,a,b=robust[name]['witness']; obs=b.copy()
    diff=[k for k in range(10) if a[k]!=b[k]]
    for k in diff[:3]: obs[k]=a[k]
    assert decode(bridge,obs,2)==IDENTITIES[i]
    assert j in candidates(books[name],obs,3)
    examples=[]
    for label,word in [('bridge-propose',bridge[0].tolist()),('bridge-accept',bridge[32].tolist()),('bridge-commit',bridge[64].tolist()),('bridge-receipt',bridge[96].tolist()),('bridge-abort',bridge[128].tolist()),('boundary-payload',b),('boundary-bridge',a),('boundary-fault',obs)]:
        f=label+'.wav'; u['audio'](out/f,word)
        with wave.open(str(out/f),'rb') as wav:
            assert wav.getparams()[:4]==(1,2,16000,12800); pcm=wav.readframes(12800)
        assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2')))<=2048
        examples.append({'file':f,'symbols':word,'pcm_sha256':sha(pcm)})
    receipt={'schema':'mhac-version-bridge-v1','pins':PINS,'source_blobs':BLOBS,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'local_spares':nlocal,'all_menu_spares':nglobal,'identities':[{'identity':v,'symbols':w.tolist()} for v,w in zip(IDENTITIES,bridge)],'baseline':baseline,'bridge':robust,'roundtrips':trials,'boundary':{'format':name,'row':j,'bridge_identity':IDENTITIES[i],'observed':obs,'faults':3,'receiver_budget':2},'specimens':examples,'limits':'Aligned known length; eight-slot controls transcribed not original CJS. No authentication, version activation, replay safety, streaming or human evidence. Both designs use 10 slots, same alphabet and duration; compute/energy not measured.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    table=''.join(f'<tr><td>{k}</td><td>{baseline[k]["minimum"]}</td><td>{v["minimum"]}</td></tr>' for k,v in robust.items())
    gallery=''.join(f'<p>{v["file"]}<br><audio controls preload="none" src="{v["file"]}"></audio></p>' for v in examples)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Version bridge</title><h1>Version bridge</h1><p>Synthetic aligned codewords, not a negotiation state machine. Start at low volume.</p><table><tr><th>Payload format</th><th>Local spare distance</th><th>All-menu spare distance</th></tr>'+table+'</table>'+gallery+'<p><a href="receipt.json">Complete codebook and receipt</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'spares':[nlocal,nglobal],'baseline':{k:v['minimum'] for k,v in baseline.items()},'bridge':{k:v['minimum'] for k,v in robust.items()},'roundtrips':trials,'boundary':receipt['boundary']}))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
