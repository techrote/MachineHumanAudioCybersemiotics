"""Measurement #442: strict profile identity and staged format coexistence.
Synthetic only. Python 3 + NumPy. python namespace-identity.py GRAMMAR_DIR OUTPUT
"""
import collections, hashlib, html, itertools, json, pathlib, runpy, sys, wave
import numpy as np

PINS = {'migration-namespace.py': ['b248075765aa1f47e2aaf7af86349a11b989c0f1','b3562781a974c47b41cbe066ceb755288a51b6b1'], 'distributed-profile.py': ['28d0433bd9f8a7ad96c616f0544caa9089c8e8e6','a780404e8c76820976ad6fb407429ec895a6313f']}

def digest(data): return hashlib.sha256(data).hexdigest()

def load(root):
    for name, (_, blob) in PINS.items():
        raw = (root/name).read_bytes()
        if hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() != blob: raise ValueError('source mismatch: '+name)
    m = runpy.run_path(str(root/'migration-namespace.py'))
    u = m['load'](root/'distributed-profile.py')
    old, free, modes, ids, profiles, labels, *_ = m['construct'](u)
    books = dict(u['catalogue']()[0], **modes)
    assert np.array_equal(old,books['tag-pair']) and np.array_equal(free,books['free-cubic'])
    return books, ids, profiles, labels, u['audio']

def near(a,b,ids):
    # Distinct degree <=4 bodies disagree in >=4 of 8 coordinates.
    assert not np.any(np.diff(a[:,:8],n=5,axis=1)%17)
    assert not np.any(np.diff(b[:,:8],n=5,axis=1)%17)
    groups=collections.defaultdict(list)
    for i,row in enumerate(a): groups[tuple(row[:8])].append(i)
    counts=np.zeros((3,3),dtype=np.int64); witnesses={}
    for j,row in enumerate(b):
        for i in groups.get(tuple(row[:8]),[]):
            d=int(np.count_nonzero(a[i]!=row)); c=0 if i==j else 1 if ids[i]==ids[j] else 2
            counts[d,c]+=1
            witnesses.setdefault((d,c),(i,j))
    return counts,witnesses

def projection(words,mask): return words[:,mask] @ (17**np.arange(len(mask),dtype=np.int64))

def consensus(books,ids,menu,mask):
    keys=np.concatenate([projection(books[n],mask) for n in menu]); n=len(ids)
    _, inv=np.unique(keys,return_inverse=True)
    def unique(values):
        values=np.tile(values,len(menu)); lo=np.full(int(inv.max())+1,n); hi=np.full_like(lo,-1)
        np.minimum.at(lo,inv,values); np.maximum.at(hi,inv,values)
        return (lo[inv]==hi[inv]).reshape(len(menu),n).sum(axis=1).tolist()
    return {'semantic':unique(ids),'strict':unique(np.arange(n)),'total_per_origin':n}

def decode(books,menu,obs,budget):
    mask=[i for i,v in enumerate(obs) if v is not None]; target=[obs[i] for i in mask]
    return sorted(set(int(i) for name in menu for i in np.flatnonzero(np.count_nonzero(books[name][:,mask]!=target,axis=1)<=budget)))

def run(root,out):
    books,ids,p,labels,audio=load(root); out.mkdir(parents=True,exist_ok=False)
    def identity(i): return {'row':int(i),'profile':int(p[i]),'meaning':labels[ids[i]]}
    counts={}; examples=[]; checked=0; rng=np.random.default_rng(44231)
    for a,b in itertools.combinations(books,2):
        c,w=near(books[a],books[b],ids); counts[a+' / '+b]=c.tolist()
        # Literal full-catalogue comparisons on 12 sampled origins and all retained witnesses.
        for i in sorted(set(rng.choice(len(ids),12,replace=False).tolist()+[i for i,j in w.values()])):
            ds=np.count_nonzero(books[b]!=books[a][i],axis=1)
            literal=set(np.flatnonzero(ds<=2)); join=set(j for j in np.flatnonzero(np.all(books[b][:,:8]==books[a][i,:8],axis=1)))
            assert literal==join; checked+=1
        for (d,k),(i,j) in w.items():
            if k==0: continue
            obs=books[a][i].tolist(); diff=np.flatnonzero(books[a][i]!=books[b][j]); budget=(d+1)//2
            for pos in diff[:d//2]: obs[pos]=int(books[b][j,pos])
            candidates=decode(books,[a,b],obs,budget); assert i in candidates and j in candidates
            name=f'witness-{len(examples):02d}.wav'; audio(out/name,obs)
            with wave.open(str(out/name),'rb') as f:
                assert f.getparams()[:4]==(1,2,16000,12800); pcm=f.readframes(12800)
            peak=int(np.max(np.abs(np.frombuffer(pcm,dtype='<i2')))); assert peak<=2048
            examples.append({'formats':[a,b],'distance':d,'identity_class':k,'origins':[identity(i),identity(j)],'observation':obs,'budget':budget,'candidates':[identity(x) for x in candidates],'wav':name,'pcm_sha256':digest(pcm),'peak_pcm16':peak})
    menus=[['tag-pair',x] for x in ('free-cubic','uniform-quartic','selective-quartic','relocated-cubic')]+[['tag-pair','free-cubic','relocated-cubic'],['tag-pair','reserved-cubic','relocated-cubic'],['free-cubic','relocated-cubic'],['reserved-cubic','relocated-cubic']]
    masks=[tuple(range(10)),tuple(range(8)),tuple(range(6)),tuple(range(4)),(0,2,4,6,8,9)]
    projections=[{'menu':menu,'mask':mask,**consensus(books,ids,menu,mask)} for menu in menus for mask in masks]
    receipt={'schema':'mhac-namespace-identity-v1','pins':PINS,'source_sha256':digest(pathlib.Path(__file__).read_bytes()),'seed':44231,'distance_axes':'distance 0,1,2 x same row, same meaning different profile, different meaning','pair_counts':counts,'literal_full_catalogue_checks':checked,'projection_results':projections,'witnesses':examples,'limits':'Closed aligned symbol catalogue. Clean projections on five selected masks only. Counts are not probabilities of physical errors. Strict identity is profile plus meaning, not outer format or authenticated source. Synthetic only; no human evidence.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    table=''.join('<tr><td>'+html.escape(name)+'</td><td>'+html.escape(str(c))+'</td></tr>' for name,c in counts.items())
    gallery=''.join('<details><summary>'+html.escape(str((s['formats'],s['distance'],s['identity_class'])))+'</summary><pre>'+html.escape(json.dumps(s,indent=2))+'</pre><audio controls preload="none" src="'+s['wav']+'"></audio></details>' for s in examples)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Namespace identity</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:1em}td{padding:.5em;border-bottom:1px solid #aaa}pre{white-space:pre-wrap}</style><h1>Namespace identity audit</h1><p>Synthetic only. Start at low volume; no autoplay. Counts: distance 0,1,2 × same row, same meaning different profile, different meaning.</p><table>'+table+'</table><h2>Auditionable ambiguity witnesses</h2>'+gallery+'<h2>Clean projection results</h2><select id="menu"></select><pre id="result"></pre><script>const rows='+json.dumps(projections)+';const menu=document.getElementById("menu"),result=document.getElementById("result");rows.forEach((r,i)=>menu.add(new Option(r.menu.join(" / ")+" | slots "+r.mask.join(","),i)));function show(){result.textContent=JSON.stringify(rows[Number(menu.value)],null,2)}menu.onchange=show;show()</script><p><a href="receipt.json">Full receipt</a></p>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({f.name:digest(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pairs':counts,'checks':checked,'witnesses':len(examples),'projection_rows':len(projections)},indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
