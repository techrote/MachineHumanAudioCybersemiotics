"""Measurement #442/#443. Synthetic list ambiguity and privileged timing diagnostic.
Run: python list-evidence.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
Receiver reused; spectral rules transcribed from pinned list-window.py.
"""
import hashlib,json,pathlib,runpy,sys,wave
from collections import Counter
import numpy as np
PIN='048b29a1608d0d2a72a3ad9c63e5f62978565226'; LIST_BLOB='ea61eb0f5534789eeff17c7eed07e96070eba9d0'
S=1280; SEEDS=(4424201,4424202); MODES=('hard25','list-exact','list-radius2')
CASES=((0,1,0,0),(-30,1,0,0),(30,1,0,0),(-35,1,0,0),(35,1,0,0),(-30,.6,250,0),(30,1.7,250,0),(0,.6,400,0),(0,1.7,400,0),(-20,1,200,10000),(20,1,200,-10000),(-35,1,200,5000),(35,1,200,-5000),(-38,.5,400,15000),(38,2,400,-15000))
def sha(b): return hashlib.sha256(b).hexdigest()
def observer(mode):
    basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(400)/16000)
    def observe(slot):
        scores=abs(basis@slot[80:480])*2/400; k,j=map(int,np.argsort(-scores,kind='stable')[:2])
        if scores[k]<200: return None
        if k==17: return 18
        if mode=='hard25': return k
        return [k,j] if j!=17 and scores[j]>=max(200,.45*scores[k]) else [k]
    return observe
def distances(book,obs):
    masks=np.array([(1<<19)-1 if x is None else sum(1<<v for v in (x if isinstance(x,list) else [x])) for x in obs],dtype=np.int64)
    return np.count_nonzero(((masks[None,:]>>book)&1)==0,axis=1)
def diagnose(book,obs,idx,radius):
    d=distances(book,obs); hits=np.flatnonzero(d<=radius)
    return dict(count=len(hits),target_distance=int(d[idx]),minimum=int(d.min()),unique=int(hits[0]) if len(hits)==1 else None,erasures=obs.count(None),double=sum(isinstance(x,list) and len(x)==2 for x in obs))
def classify(d,idx):
    return 'none' if not d['count'] else 'ambiguous' if d['count']>1 else 'correct' if d['unique']==idx else 'wrong'
def run(root,out):
    load=lambda f:runpy.run_path(str(root/f))
    m=load('interval-admission.py'); p=load('competing-starts.py'); s=load('discourse-sync.py')
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':m['PARENT'],'interval-admission.py':'32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3'}
    for f,b in pins.items(): assert m['blob'](root/f)==b,f
    v=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']; _,raw,_=v['build'](root); old,new=raw
    long=np.concatenate([v['extend'](w,k,'polynomial') for k,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    def list_decode(book,obs,radius):
        d=np.zeros(len(book),np.int16)
        for i,x in enumerate(obs):
            if x is not None: d+=~np.isin(book[:,i],x)
        hits=np.flatnonzero(d<=radius); return int(hits[0]) if len(hits)==1 else None
    dec={'hard25':joint,'list-exact':lambda b,o,r:list_decode(b,o,0),'list-radius2':list_decode}
    obs={k:observer(k) for k in MODES}; rows=[]; specimens=[]; out.mkdir(parents=True,exist_ok=False)
    tiny=np.array([[0,1],[1,1],[2,2]])
    for x,n in (([[0,1],[1]],2),([[0],[1,2]],1),([[2],[1]],0),([None,None],3)): assert diagnose(tiny,x,0,0)['count']==n
    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        for pair in range(3):
            a=pair%2; b=1-a; i=int(rng.integers(len(long))); j=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); want=[[a,18,i],[b,13,j]]
            x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][j].tolist()+[18,18]
            for ci,(phase,gain,noise,ppm) in enumerate(CASES):
                aa=np.zeros(32*S,np.int32); bb=aa.copy(); m['put'](aa,x,lead); offset=lead+int(2.5*S)+phase*16
                for q,tok in enumerate(y): m['put'](bb,[tok],offset+round(q*S*(1+ppm/1e6)))
                ns=seed*10000+pair*100+ci; mix=aa+gain*bb+np.random.default_rng(ns).normal(0,noise,len(aa)); assert abs(mix).max()<10000
                pcm=np.rint(mix).astype('<i2'); digest=sha(pcm.tobytes()); groups=[]
                for mode in MODES:
                    ev=m['acquire'](pcm,books,obs[mode],dec[mode],'multiplex'); releases=[(e['source'],*e['identity']) for e in ev if e['kind']=='release']; hit=sum((Counter(releases)&Counter(map(tuple,want))).values()); radius=0 if mode=='list-exact' else 2
                    groups.append([(e['source'],e['body_start'],e['sample']) for e in ev if e['kind']=='start'])
                    for source,n,idx in want:
                        origin,drift=(lead,0) if source==a else (offset,ppm)
                        true=lambda q:origin+round(q*S*(1+drift/1e6))
                        oracle=[obs[mode](pcm[true(q):true(q)+S]) for q in range(2,n+4)]; od=diagnose(books[source][n],oracle[:-2],idx,radius)
                        st=[e for e in ev if e['kind']=='start' and e['source']==source]; term=[e for e in ev if e['kind'] in ('candidate','reject') and e['source']==source]; actual=None; error=None; body=None
                        if len(st)==1:
                            error=st[0]['body_start']-true(2); matches=[e for e in term if e['body_start']==st[0]['body_start']]
                            if len(matches)==1:
                                t=matches[0]; body=t['seen'][:-2]
                                if len(body)==n and 18 not in body:
                                    actual=diagnose(books[source][n],body,idx,radius); assert t['identity']==([n,actual['unique']] if actual['unique'] is not None else None)
                        outcome='released' if (source,n,idx) in releases else 'no-start' if not st else 'no-usable-terminal' if actual is None else classify(actual,idx)
                        rows.append(dict(seed=seed,pair=pair,condition=ci,mode=mode,source=source,length=n,target=idx,pcm_sha256=digest,start_count=len(st),start_error_samples=error,actual=actual,actual_observations=body,oracle=od,oracle_observations=oracle,oracle_terminals=oracle[-2:]==[18,18],oracle_class=classify(od,idx),outcome=outcome,releases=releases,events=ev))
                    assert sum(r['outcome']=='released' for r in rows[-2:])==hit
                assert groups[0]==groups[1]==groups[2]
                if seed==SEEDS[0] and pair==0 and ci in (0,1,2,3,4,13,14):
                    f=f'case-{ci:02d}.wav'
                    with wave.open(str(out/f),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                    specimens.append(dict(file=f,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    totals={k:dict(outcomes=Counter(r['outcome'] for r in rows if r['mode']==k),oracle=Counter(r['oracle_class'] for r in rows if r['mode']==k),oracle_with_terminal=sum(r['oracle_class']=='correct' and r['oracle_terminals'] for r in rows if r['mode']==k),wrong_releases=sum(len(r['releases'])-sum(z['outcome']=='released' for z in rows[t:t+2]) for t,r in enumerate(rows) if t%2==0 and r['mode']==k)) for k in MODES}
    receipt=dict(schema='mhac-list-evidence-v1',pin=PIN,list_reference_blob=LIST_BLOB,blobs=pins,seeds=SEEDS,conditions=CASES,condition_fields=['phase_ms','gain_B_over_A','noise_sd_counts','B_onset_drift_ppm'],physical_pcm=len(rows)//6,receiver_evaluations=len(rows)//2,identity_rows=len(rows),totals=totals,specimens=specimens,limits='Fresh six pairs; repeated conditions, not independent population samples. Oracle uses true source, length, slot onset and drift, same spectral rule, bypasses acquisition and admission; body-only candidates and terminal evidence counted separately. No authentication, human or physical evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    compact=[{k:v for k,v in r.items() if k!='events'} for r in rows]; gallery=''.join(f'<p>{g["file"]}<br><audio controls preload="none" src="{g["file"]}"></audio></p>' for g in specimens)
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>List evidence</title><style>body{font:16px system-ui;max-width:950px;margin:auto;padding:1em}pre{white-space:pre-wrap}td,th{border:1px solid #aaa;padding:5px}table{border-collapse:collapse}</style><h1>List evidence and privileged timing</h1><p>Synthetic only. Oracle knows exact source, frame length and timing; not a deployable receiver. No autoplay.</p><label>Condition <select id="condition"></select></label><table id="results"></table><label>Trace <select id="trace"></select></label><pre id="detail"></pre><h2>Original PCM specimens</h2>'''+gallery+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Complete traces</a></p><script>const rows='''+json.dumps(compact)+''';const c=document.getElementById('condition'),t=document.getElementById('trace'),d=document.getElementById('detail'),res=document.getElementById('results');c.add(new Option('All','all'));for(const v of [...new Set(rows.map(r=>r.condition))])c.add(new Option('Case '+v,v));let a=[];function render(){a=rows.filter(r=>c.value==='all'||String(r.condition)===c.value);res.innerHTML='<tr><th>Mode</th><th>Expected</th><th>Released</th><th>Oracle body correct</th><th>Oracle body + terminals</th><th>Oracle ambiguous</th></tr>'+['hard25','list-exact','list-radius2'].map(m=>{let b=a.filter(r=>r.mode===m);return '<tr><td>'+m+'</td><td>'+b.length+'</td>'+[b.filter(r=>r.outcome==='released').length,b.filter(r=>r.oracle_class==='correct').length,b.filter(r=>r.oracle_class==='correct'&&r.oracle_terminals).length,b.filter(r=>r.oracle_class==='ambiguous').length].map(v=>'<td>'+v+'</td>').join('')+'</tr>'}).join('');t.replaceChildren();a.forEach((r,i)=>t.add(new Option(r.seed+' / '+r.pair+' / '+r.condition+' / '+r.mode+' / source '+r.source,i)));show()}function show(){d.textContent=JSON.stringify(a[Number(t.value)],null,2)}c.onchange=render;t.onchange=show;render();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>''',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(totals,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
