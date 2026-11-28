"""Refs #452 / Draft #453. Aligned prefix-disjoint frame experiment, synthetic only.
Usage: python prefix-disjoint.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np
PIN='7c40f0e533245d129881729722210ac6e9a65d9c'
BLOB='7ef6881cefa9c34355d024aeea671d021b674a55'
SEED=45233

def sha(b): return hashlib.sha256(b).hexdigest()
def joint(book, obs, radius=2):
    keep=[i for i,x in enumerate(obs) if x is not None]
    hits=np.flatnonzero(np.count_nonzero(book[:,keep]!=[obs[i] for i in keep],axis=1)<=radius)
    return int(hits[0]) if len(hits)==1 else None

def run(root,out):
    p=root/'version-bound-payload.py'; b=p.read_bytes()
    assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==BLOB
    m=runpy.run_path(str(p)); u,raw,names=m['build'](root)
    old,new=raw; offset=np.arange(15)**4%17
    short=np.column_stack((np.zeros((len(old),3),dtype=int),old))
    body=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    lookup={tuple(w):i for i,w in enumerate(old)}
    aliases=[(lookup[tuple(w)],j) for j,w in enumerate(new) if tuple(w) in lookup and lookup[tuple(w)]!=j]
    assert len(aliases)==2031
    rng=np.random.default_rng(SEED)
    origins=[(13,int(i)) for i in rng.choice(len(old),16,False)]+[(18,int(i)) for i in rng.choice(len(old),16,False)]+[(18,len(old)+aliases[int(i)][1]) for i in rng.choice(len(aliases),16,False)]
    out.mkdir(parents=True,exist_ok=False); stats={}; traces=[]; witnesses=[]; specimens=[]
    for mode in ('independent','quartic'):
        long=np.column_stack((np.full((len(body),3),16), (body+offset)%17 if mode=='quartic' else body))
        # Cubic bodies vs cubic + x^4: at most four equal positions of ten.
        prefix={tuple(w[3:13]) for w in long}; collision=len(prefix.intersection(lookup))
        assert collision==(0 if mode=="quartic" else len(old))
        books={13:short,18:long}; exact={n:{tuple(w[3:]):i for i,w in enumerate(book)} for n,book in books.items()}
        assert all(len(exact[n])==len(book) for n,book in books.items())
        for n,i in origins:
            word=books[n][i].tolist(); h=word[0]
            for pattern in itertools.product('CFE',repeat=3):
                header=[h if x=='C' else 16-h if x=='F' else None for x in pattern]
                a,b=header.count(0),header.count(16); declared=13 if a>b else 18 if b>a else None
                for cut in range(3,n+1):
                    got=exact[cut].get(tuple(word[3:cut])) if declared==cut and cut in exact else None
                    result='abstain' if got is None else 'correct' if (cut,got)==(n,i) else 'wrong'
                    key=f'{mode}:{"full" if cut==n else "cut"}:{result}'; stats[key]=stats.get(key,0)+1
                    traces.append([mode,n,i,''.join(pattern),cut,got,result])
                    if mode=='quartic' and cut<n: assert got is None
        # Identical extended origin across both schemes, closest short codeword chosen per scheme.
        a,j=aliases[0]; origin=len(old)+j; src=long[origin,:13].tolist()
        distances=np.count_nonzero(short!=src,axis=1); k=int(distances.argmin()); dst=short[k].tolist()
        diff=[i for i,(x,y) in enumerate(zip(src,dst)) if x!=y]; d=len(diff)
        assert d==(9 if mode=='quartic' else 3)
        path=[]
        for e in range(d+1):
            obs=src.copy()
            for pos in diff[:e]: obs[pos]=dst[pos]
            got=joint(short,obs); path.append(got)
            if e<d-2: assert got is None
        assert path[d-2]==k
        witnesses.append({'mode':mode,'long_row':j,'short_row':k,'long_meaning':names[j],'short_meaning':names[k],'distance':d,'radius2_path':path,'prefix_collisions':collision,'source_prefix':src,'target':dst})
        for label,obs in [('long',long[origin].tolist()),('cut',src),('false-short',[dst[t] if t in diff[:d-2] else x for t,x in enumerate(src)]),('short',dst)]:
            f=f'{mode}-{label}.wav'; u['audio'](out/f,obs)
            with wave.open(str(out/f),'rb') as w: pcm=w.readframes(w.getnframes()); assert w.getparams()[:4]==(1,2,16000,len(obs)*1280)
            assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2').astype(int)))<=2048
            specimens.append({'file':f,'symbols':obs,'pcm_sha256':sha(pcm)})
    receipt={'schema':'mhac-prefix-disjoint-v1','pin':PIN,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'seed':SEED,'origins':origins,'stats':stats,'observations':len(traces),'witnesses':witnesses,'specimens':specimens,'limits':'Aligned symbols, exact observed endpoint. Header-only faults exhaustive for sampled sources; joint radius-two paths targeted, not population rates. No streaming, insert/delete, noise, authentication, human evidence or legacy receiver compatibility. Same alphabet and duration; not compute or energy matched.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    gallery=''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Prefix disjoint frames</title><h1>Prefix disjoint frames</h1><p>Synthetic aligned frames. Start at low volume. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('observations','stats','witnesses')},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
