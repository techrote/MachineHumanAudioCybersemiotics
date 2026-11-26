"""Refs #452 / Draft #453. Bounded ambiguity reports for list-valued observations.
Synthetic shared-frame alternatives, not authenticated senders or human evidence.
Usage: python ambiguity-admission.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='048b29a1608d0d2a72a3ad9c63e5f62978565226'
LIST_BLOB='ea61eb0f5534789eeff17c7eed07e96070eba9d0'
CAP=8; SEED=452400; S=1280

def classify(book, obs, cap=CAP):
    """Exact compatibility; None is erasure. Overflow never returns a partial list."""
    if len(obs)!=book.shape[1] or not 1<=cap<=CAP: raise ValueError('invalid shape or cap')
    hits=np.ones(len(book),dtype=bool)
    for i,values in enumerate(obs):
        if values is not None:
            if not isinstance(values,list) or not 1<=len(values)<=2 or any(type(x)!=int or not 0<=x<17 for x in values): raise ValueError('invalid observation')
            hits &= np.isin(book[:,i],values)
    ids=np.flatnonzero(hits); n=len(ids)
    return dict(status='none' if n==0 else 'unique' if n==1 else 'ambiguous' if n<=cap else 'overflow',count=n,ids=ids.tolist() if n<=cap else [])

def run(root,out):
    load=lambda f:runpy.run_path(str(root/f))
    m=load('interval-admission.py'); p=load('competing-starts.py'); s=load('discourse-sync.py'); w=load('window-admission.py'); l=load('list-window.py')
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':m['PARENT'],'interval-admission.py':w['BLOB'],'window-admission.py':l['WINDOW_BLOB'],'list-window.py':LIST_BLOB}
    for f,h in pins.items(): assert m['blob'](root/f)==h,f
    v=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']; _,raw,_=v['build'](root); old,new=raw
    long=np.concatenate([v['extend'](word,i,'polynomial') for i,word in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED); rows=[]; symbolic=[]; specimens=[]
    for source in (0,1):
        for n,book in books[source].items():
            for pair,i in enumerate(rng.choice(len(book),4,False)):
                i=int(i); a=book[i]; dist=np.count_nonzero(book!=a,axis=1); dist[i]=n+1; j=int(dist.argmin()); b=book[j]; ids=[i,j]
                union=[sorted({int(x),int(y)}) for x,y in zip(a,b)]
                for name,obs in [('clean',[[int(x)] for x in a]),('union',union),('all-erased',[None]*n),('invalid-prefix',[[1]]*3+union[3:])]:
                    rep=classify(book,obs); assert (rep['status']=='unique' and rep['ids']==[i]) if name=='clean' else (rep['count']>=2) if name=='union' else rep['status']==('overflow' if name=='all-erased' else 'none')
                    symbolic.append(dict(source=source,length=n,pair=pair,ids=ids,distance=int(dist[j]),case=name,observations=obs,report=rep))
                for gain in (0,.4,.7,1,1.4):
                    for noise in (0,150):
                        x=np.zeros(26*S,np.int32); y=x.copy(); lead=S+40
                        m['put'](x,s['preamble'](source)+a.tolist()+[18,18],lead); m['put'](y,b.tolist(),lead+2*S)
                        ns=SEED*10000+source*1000+n*10+pair*100+int(gain*10)+noise*10000
                        mix=x+gain*y+np.random.default_rng(ns).normal(0,noise,len(x)); assert abs(mix).max()<7000
                        pcm=np.rint(mix).astype('<i2'); digest=m['sha'](pcm.tobytes())
                        hard=m['acquire'](pcm,books,l['observer']('hard25'),joint,'multiplex')
                        exact=m['acquire'](pcm,books,l['observer']('list-exact'),lambda b,o,r:l['list_joint'](b,o,0),'multiplex')
                        reports=[]
                        for e in exact:
                            if e['kind'] not in ('candidate','reject'): continue
                            body=e['seen'][:-2]; sb=books[e['source']]
                            if len(body) not in sb or 18 in body: continue
                            rep=classify(sb[len(body)],body); assert (rep['status']=='unique')==(e['kind']=='candidate')
                            if e['kind']=='candidate': assert rep['ids']==[e['identity'][1]]
                            reports.append(dict(source=e['source'],length=len(body),sample=e['sample'],body_start=e['body_start'],**rep))
                        expected=[i] if gain==0 else ids
                        # Shared framing represents competing alternatives, not two complete frames.
                        matched=[r for r in reports if r['source']==source and r['length']==n and abs(r['body_start']-(lead+2*S))<=160]
                        assert len(matched)<=1
                        result=matched[0] if matched else dict(status='no-body',count=0,ids=[])
                        releases=lambda es:[e['identity'][1] for e in es if e['kind']=='release' and e['source']==source and e['identity'][0]==n]
                        row=dict(source=source,length=n,pair=pair,expected=expected,gain=gain,noise=noise,noise_seed=ns,pcm_sha256=digest,report=result,all_reports=reports,hard_releases=releases(hard),exact_releases=releases(exact),hard_events=hard,exact_events=exact)
                        rows.append(row)
                        if pair==0 and noise==0 and gain in (0,1):
                            name=f's{source}-n{n}-g{gain}.wav'
                            with wave.open(str(out/name),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
                            specimens.append(dict(file=name,pcm_sha256=digest,peak=int(abs(pcm).max()),report=result,expected=expected))
    stats={}
    for row in rows:
        k=f"{row['gain']}:{row['noise']}"; rep=row['report']; want=set(row['expected']); got=set(rep['ids'])
        stats.setdefault(k,Counter()).update([rep['status']]); stats[k].update(full_set=int(want==got),contains_all=int(want<=got),hard_release=int(bool(row['hard_releases'])),exact_release=int(bool(row['exact_releases'])),hard_unintended=sum(x not in want for x in row['hard_releases']),exact_unintended=sum(x not in want for x in row['exact_releases']))
    receipt=dict(schema='mhac-ambiguity-report-v1',pin=PIN,blobs=pins,source_sha256=m['sha'](pathlib.Path(__file__).read_bytes()),seed=SEED,numpy=np.__version__,cap=CAP,pcm_cases=len(rows),symbolic_cases=len(symbolic),stats=stats,specimens=specimens,limits='Shared source preamble and terminal, two superposed alternative bodies at identical slot timing; not two independently framed senders. Reports are sidecars to existing receiver events, not new live release policy. Exact list compatibility is not truth or authentication. Overflow reports count but no identities. Catalogue scanning and offline PCM/trace storage are not bounded streaming memory. Exploratory selected nearest neighbours; not a holdout or human evidence.')
    for name,data in [('receipt.json',receipt),('symbolic.json',symbolic)]: (out/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Ambiguity reports</title><h1>Shared-frame grammatical alternatives</h1><p>Synthetic only. Start at low volume; no automatic playback.</p><pre>'+json.dumps(stats,indent=2)+'</pre>'
    for g in specimens: html+=f'<h2>{g["file"]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(g['report'],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="symbolic.json">Symbolic cases</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:m['sha'](p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(stats))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
