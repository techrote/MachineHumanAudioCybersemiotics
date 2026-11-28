"""Refs #452 / Draft #453: aligned frame-length commitment, synthetic only.
Run: python frame-length-commit.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np
PIN='2515199a231bf95a9d20b74129af44008fc8233e'
BLOB='7ef6881cefa9c34355d024aeea671d021b674a55'
SEED=45232
POLICIES=('eager','first','majority','boundary')
def sha(b): return hashlib.sha256(b).hexdigest()
def length(header,policy):
    if policy=='eager': return 10
    if policy=='first': return {0:10,16:15}.get(header[0])
    a,b=header.count(0),header.count(16)
    return 10 if a>b else 15 if b>a else None

def receive(header,body,policy,short,long):
    n=length(header,policy)
    if n is None or len(body)<n or (policy=='boundary' and len(body)!=n): return None,None
    return (short if n==10 else long).get(tuple(body[:n])),n

def run(root,out):
    p=root/'version-bound-payload.py'; b=p.read_bytes()
    assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==BLOB
    m=runpy.run_path(str(p)); u,raw,names=m['build'](root)
    books=[m['extend'](w,v,'polynomial') for v,w in enumerate(raw)]
    short={tuple(w):(0,i) for i,w in enumerate(raw[0])}
    long={tuple(w):(v,i) for v,book in enumerate(books) for i,w in enumerate(book)}
    assert len(short)==len(raw[0]) and len(long)==sum(map(len,raw))
    aliases=[(short[tuple(w)][1],j) for j,w in enumerate(raw[1]) if tuple(w) in short and short[tuple(w)][1]!=j]
    assert len(aliases)==2031
    rng=np.random.default_rng(SEED)
    origins=[(0,int(i),10) for i in rng.choice(len(raw[0]),32,False)]+[(0,int(i),15) for i in rng.choice(len(raw[0]),32,False)]+[(1,aliases[int(i)][1],15) for i in rng.choice(len(aliases),32,False)]
    # All 27 aligned header corruption patterns, all payload-prefix lengths.
    stats={}; traces=[]
    for v,i,n in origins:
        body=(raw[0] if n==10 else books[v])[i].tolist(); h=0 if n==10 else 16
        for pattern in itertools.product('CFE',repeat=3):
            header=[h if x=='C' else 16-h if x=='F' else None for x in pattern]
            e=pattern.count('F'); s=pattern.count('E')
            if 2*e+s<3: assert length(header,'majority')==n
            for cut in range(n+1):
                row={'origin':[v,i,n],'header':header,'faults':''.join(pattern),'cut':cut,'results':{}}
                group='full' if cut==n else 'cut10' if cut==10 else 'other-cut'
                budget='protected' if 2*e+s<3 else 'outside'
                for policy in POLICIES:
                    got,k=receive(header,body[:cut],policy,short,long)
                    outcome='abstain' if got is None else 'correct' if got==(v,i) else 'wrong'
                    premature=got is not None and k<n
                    key=f'{policy}:{group}:{budget}'; count=stats.setdefault(key,[0,0,0,0])
                    count[('correct','wrong','abstain').index(outcome)]+=1; count[3]+=int(premature)
                    row['results'][policy]=[outcome,got,k,premature]
                    if policy in ('majority','boundary') and budget=='protected': assert (got==(v,i) if cut==n else got is None)
                traces.append(row)
    a,j=aliases[0]; body=books[1][j].tolist(); specimens=[]
    out.mkdir(parents=True,exist_ok=False)
    for label,header,cut in [('long-clean',[16]*3,15),('long-cut',[16]*3,10),('one-flip-cut',[0,16,16],10),('two-flip-cut',[0,0,16],10),('two-erased-cut',[16,None,None],10),('short-clean',[0]*3,10)]:
        symbols=header+body[:cut]; f=label+'.wav'; u['audio'](out/f,symbols)
        with wave.open(str(out/f),'rb') as w:
            assert w.getparams()[:4]==(1,2,16000,len(symbols)*1280); pcm=w.readframes(w.getnframes())
        assert np.max(np.abs(np.frombuffer(pcm,dtype='<i2').astype(int)))<=2048
        specimens.append({'file':f,'symbols':symbols,'pcm_sha256':sha(pcm),'results':{p:receive(header,body[:cut],p,short,long) for p in POLICIES}})
    assert receive([0,16,16],body[:10],'first',short,long)[0]==(0,a)
    assert receive([0,16,16],body[:10],'majority',short,long)[0] is None
    assert receive([0,0,16],body[:10],'boundary',short,long)[0]==(0,a)
    receipt={'schema':'mhac-frame-length-commit-v1','pin':PIN,'blob':BLOB,'seed':SEED,'source_sha256':sha(pathlib.Path(__file__).read_bytes()),'origins':origins,'axes':['correct','wrong','abstain','premature_subset'],'stats':stats,'observations':len(traces),'decisions':len(traces)*len(POLICIES),'alias_rows':[a,j],'alias_meanings':[names[a],names[j]],'specimens':specimens,'limits':'Aligned header and exact payload symbols; no acquisition, insertion/deletion, payload noise, streaming, authentication or human evidence. Boundary policy knows supplied prefix extent at end; no claim of observable physical boundary. Targeted new origins, not population rate. All policies same transmitted symbols.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in traces),encoding='utf-8')
    gallery=''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio><pre>{json.dumps(s["results"])}</pre></p>' for s in specimens)
    table=''.join(f'<tr><td>{k}</td>'+''.join(f'<td>{v}</td>' for v in vals)+'</tr>' for k,vals in sorted(stats.items()))
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Frame commitment</title><h1>Frame commitment</h1><p>Aligned synthetic header and payload. Start with low volume. No autoplay.</p><table><tr><th>Policy:cut:budget</th><th>Correct</th><th>Wrong</th><th>Abstain</th><th>Premature subset</th></tr>'+table+'</table>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('observations','decisions','stats','alias_rows','alias_meanings')},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
