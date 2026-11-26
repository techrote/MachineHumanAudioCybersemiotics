"""Refs #442 / Draft #443. Synthetic-only trace and PCM audit of Grammar #453.
Run: python admission-inspector.py PINNED_SOURCE_DIR FROZEN_OUTPUT NEW_OUTPUT
Requires NumPy. No human evidence, authentication, or device control.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter, defaultdict
import numpy as np

PIN='7053f813bf770c1ec195e0c4485d24f483505045'
BLOBS={'causal-frame.py':'fc5dd44fe87ebcabc2a1e0213726a3fd43cb2a60','competing-starts.py':'af3f673f28e65bb4fc241a22cc603a6cbb041dfb','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','discourse-sync.py':'cc6b996d6314fdcbb92edc85e12878d5d2077aa7','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','frame-length-commit.py':'1538e258e53b62fc62315ca11eb9ba34496c5919','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','prefix-disjoint.py':'f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942','version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401'}
CASES=('clean','cut','lost-end','false-start','cut-false-start','cut-two-false-starts','early-cut','noise')
POLICIES=('locked','restart','keep-two','replace-two')
SLOT=1280; RATE=16000; SEED=45236

def require(ok,msg):
    if not ok: raise ValueError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def write(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def synth(tokens):
    t=np.arange(960); env=np.minimum(1,np.minimum(t/80,(959-t)/80)); slots=[]
    for v in tokens:
        a=np.zeros(SLOT,dtype='<i2')
        if v is not None: a[:960]=np.rint(1500*env*np.sin(2*np.pi*(400+100*v)*t/RATE+.137)).astype('<i2')
        slots.append(a)
    return np.concatenate(slots)
def pre(s): return [20,22] if s==0 else [22,20]
def key(e): return e['source'],e['body_start']
def ident(e): return [e['source'],*e['identity']]

def scenarios(books):
    rng=np.random.default_rng(SEED)
    for j in range(8):
        s=j%2; n=13 if s else 18; n2=31-n
        i=int(rng.integers(len(books[s][n]))); i2=int(rng.integers(len(books[1-s][n2])))
        first=pre(s)+books[s][n][i].tolist()+[18,18]; second=pre(1-s)+books[1-s][n2][i2].tolist()+[18,18]
        for k,case in enumerate(CASES):
            seed=SEED+100*j+k; a=first[:]; complete=True
            if case.startswith('cut'):
                a=a[:8]; complete=False
                if case!='cut': a[4:6]=pre(1-s)
                if case=='cut-two-false-starts': a[6:8]=pre(s)
            if case=='early-cut': a=a[:3]; complete=False
            if case=='lost-end': a[-2:]=[None,None]; complete=False
            if case=='false-start': a[8:10]=pre(1-s)
            lead=int(rng.integers(321,2500)); gap=int(rng.integers(0,240))
            if case=='early-cut': gap=640
            bstart=lead+len(a)*SLOT+gap
            pcm=np.concatenate([np.zeros(lead,dtype='<i2'),synth(a),np.zeros(gap,dtype='<i2'),synth(second),np.zeros(24*SLOT,dtype='<i2')])
            if case=='noise': pcm=np.clip(np.rint(pcm.astype(float)+np.random.default_rng(seed).normal(0,100,len(pcm))),-2048,2048).astype('<i2')
            frames=[dict(identity=[s,n,i],start=lead,body=lead+2*SLOT,end=lead+len(a)*SLOT,expected=complete),dict(identity=[1-s,n2,i2],start=bstart,body=bstart+2*SLOT,end=bstart+len(second)*SLOT,expected=True)]
            yield case,j,seed,pcm,frames

def audit(trace,frames,books,pcm_len):
    active={}; detected={}; terminal={}; reasons=Counter(); peak=0; ready={}; releases=[]; prev=0
    for e in trace['events']:
        k=key(e); kind=e['kind']; t=e['sample']; require(prev<=t<=pcm_len and t%80==0,'event time'); prev=t
        if kind in ('start','ignore'):
            require(k not in detected and t<k[1],'duplicate or late start'); detected[k]=e; terminal[k]=kind
            if kind=='start': active[k]=e; peak=max(peak,len(active)); require(len(active)<= (1 if trace['policy'] in ('locked','restart') else 2),'capacity')
        else:
            require(k in active,'event without active hypothesis')
            if kind in ('candidate','reject'):
                seen=e['seen']; n=len(seen)-2; require(seen[-2:]==[18,18] and t>=k[1]+len(seen)*SLOT and len(seen)<=22,'terminal timing')
                hits=[]; reason='length'
                if n in books[k[0]] and 18 not in seen[:-2]:
                    keep=[i for i,v in enumerate(seen[:-2]) if v is not None]; values=[seen[i] for i in keep]; book=books[k[0]][n]
                    hits=np.flatnonzero(np.count_nonzero(book[:,keep]!=values,axis=1)<=2).tolist(); reason='unique' if len(hits)==1 else 'ambiguous' if hits else 'no-codeword'
                elif n in books[k[0]]: reason='interior-terminal'
                require((kind=='candidate')==(len(hits)==1),'candidate classification'); require(e['identity']==([n,hits[0]] if len(hits)==1 else None),'candidate identity'); reasons[reason]+=1
                if kind=='candidate': ready[k]=e
                terminal[k]=kind
            elif kind=='release':
                require(k in ready and e['identity']==ready[k]['identity'] and e['ready_sample']==ready[k]['sample'] and e['wait_samples']==t-ready[k]['sample'],'release readiness'); releases.append(e); terminal[k]=kind; del active[k]
            elif kind in ('timeout','evict','suppress-overlap'):
                if kind=='timeout': require(t>=k[1]+22*SLOT,'premature timeout')
                if kind=='suppress-overlap': require(releases and k[1]-2*SLOT<releases[-1]['body_start']+(releases[-1]['identity'][0]+2)*SLOT,'suppression interval')
                # Preserve a prior rejection: suppressing an already rejected hypothesis is not suppressing a valid one.
                if terminal[k]=='reject' and kind=='suppress-overlap': reasons['suppressed-after-reject']+=1
                if terminal[k]=='candidate' and kind in ('evict','suppress-overlap'): reasons['valid-'+kind]+=1
                terminal[k]=kind; del active[k]
            else: raise ValueError('unknown event '+kind)
        # Rejected/timeout older hypotheses may be silently popped before later events.
        # Rejections remain until the next event, where they can be explicitly suppressed.
        for old in list(active):
            if terminal[old]=='reject' and old!=k and kind=='start': del active[old]
        if kind=='reject' and next(iter(active),None)==k: del active[k]
    got=[ident(e) for e in releases]; want=[f['identity'] for f in frames if f['expected']]
    correct=sum((Counter(map(tuple,got))&Counter(map(tuple,want))).values())
    require(trace['decoded']==got and trace['expected']==want and (trace['correct'],trace['wrong'],trace['missing'])==(correct,len(got)-correct,len(want)-correct),'outcome accounting')
    rows=[]; matched=set()
    for f in frames:
        ks=[k for k in detected if k[0]==f['identity'][0] and abs(k[1]-f['body'])<=160]; require(len(ks)<=1,'ambiguous start association')
        k=ks[0] if ks else None; state=terminal[k] if k else 'not-detected'; rel=next((e for e in releases if key(e)==k),None)
        if k: matched.add(k)
        rows.append(dict(**f,state=state,estimated_body=k[1] if k else None,start_error_samples=k[1]-f['body'] if k else None,release_sample=rel['sample'] if rel else None,release_identity=ident(rel) if rel else None,end_delta_samples=rel['sample']-f['end'] if rel else None,wait_samples=rel['wait_samples'] if rel else None))
    require(all(r['state']!='release' or (r['expected'] and r['release_identity']==r['identity']) for r in rows),'matched wrong release')
    require(sum(r['state']=='release' for r in rows)==len(releases),'unmatched release')
    return dict(frames=rows,extraneous_starts=len(set(detected)-matched),peak_active=peak,reasons=dict(reasons),events=trace['events'])

def run(root,frozen,out):
    for f,b in BLOBS.items(): require(blob((root/f).read_bytes())==b,'source '+f)
    manifest=json.loads((frozen/'manifest.json').read_text()); require(set(manifest)=={p.name for p in frozen.iterdir()}-{'manifest.json'},'inventory')
    for f,h in manifest.items(): require(sha((frozen/f).read_bytes())==h,'manifest '+f)
    receipt=json.loads((frozen/'receipt.json').read_text()); require(receipt['source_sha256']==sha((root/'competing-starts.py').read_bytes()),'receipt source')
    traces=[json.loads(x) for x in (frozen/'traces.jsonl').read_text().splitlines()]; index={(r['case'],r['pair'],r['policy']):r for r in traces}; require(len(index)==len(traces)==256,'trace cardinality')
    m=runpy.run_path(str(root/'version-bound-payload.py')); _,raw,_=m['build'](root); old,new=raw
    long=np.concatenate([m['extend'](w,v,'polynomial') for v,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    upstream=runpy.run_path(str(root/'competing-starts.py')); observe=runpy.run_path(str(root/'causal-frame.py'))['observe']; joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']
    rows=[]; counts=defaultdict(Counter); reasons=defaultdict(Counter); stats=defaultdict(Counter); native=0; pcm_checks=0; wav_checks=0
    for case,j,seed,pcm,frames in scenarios(books):
        h=sha(pcm.tobytes()); pcm_checks+=1
        if j==0:
            with wave.open(str(frozen/(case+'.wav')),'rb') as w: require(w.getparams()[:3]==(1,2,RATE) and w.readframes(w.getnframes())==pcm.tobytes(),'WAV mismatch'); wav_checks+=1
        start_sets=[]
        for policy in POLICIES:
            r=index[case,j,policy]; require(r['seed']==seed and r['pcm_sha256']==h,'PCM hash')
            a=audit(r,frames,books,len(pcm)); start_sets.append({key(e) for e in r['events'] if e['kind'] in ('start','ignore')})
            require(upstream['acquire'](pcm,books,observe,joint,policy)==r['events'],'native trace mismatch'); native+=1
            counts[policy].update(x['state'] for x in a['frames'] if x['expected']); reasons[policy].update(a['reasons'])
            z=stats[case+':'+policy]; z.update(correct=r['correct'],wrong=r['wrong'],missing=r['missing'],wait_samples=sum(e['wait_samples'] for e in r['events'] if e['kind']=='release'),ignored=sum(e['kind']=='ignore' for e in r['events']),evicted=sum(e['kind']=='evict' for e in r['events'])); z['max_wait_samples']=max([z['max_wait_samples']]+[e['wait_samples'] for e in r['events'] if e['kind']=='release'])
            rows.append(dict(case=case,pair=j,policy=policy,seed=seed,pcm_sha256=h,**a))
        require(all(x==start_sets[0] for x in start_sets),'unmatched detected starts')
    require(stats==receipt['stats'],'summary mismatch')
    out.mkdir(parents=True,exist_ok=False)
    for case in CASES: (out/(case+'.wav')).write_bytes((frozen/(case+'.wav')).read_bytes())
    timings={}
    for policy in POLICIES:
        subset=[r for r in rows if r['policy']==policy]; f=[x for r in subset for x in r['frames']]; errors=[x['start_error_samples'] for x in f if x['expected'] and x['start_error_samples'] is not None]; delays=[x['end_delta_samples'] for x in f if x['end_delta_samples'] is not None]
        timings[policy]=dict(detected_true_starts=sum(x['estimated_body'] is not None for x in f),true_starts=len(f),extraneous_starts=sum(r['extraneous_starts'] for r in subset),expected_start_error_samples=[min(errors),max(errors)],release_end_delta_samples=[min(delays),max(delays)])
    result=dict(timings=timings,schema='mhac-admission-inspector-v1',source_pin=PIN,source_blobs=BLOBS,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frozen_receipt_sha256=sha((frozen/'receipt.json').read_bytes()),pcm_checks=pcm_checks,wav_checks=wav_checks,native_trace_checks=native,trace_checks=len(rows),matched_start_sets=pcm_checks,expected_frame_outcomes=counts,rejection_reasons=reasons,rows=rows,limits='Synthetic finite corpus, 160-sample start association, nominal slot end not perceived latency. Upstream catalogue, feature extractor and acquisition reused for native replay. Independent PCM rendering and dense candidate count only. No new holdout or human evidence.')
    write(out/'receipt.json',result)
    payload=json.dumps(rows,separators=(',',':')).replace('<','\\u003c')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Admission inspector</title><style>body{font:16px system-ui;max-width:1050px;margin:auto;padding:16px}table{border-collapse:collapse;width:100%}td,th{padding:6px;text-align:left;border-bottom:1px solid #aaa}select{margin:6px}pre{white-space:pre-wrap}svg{width:100%;height:110px}</style><h1>Competing-start admission inspector</h1><p>Synthetic PCM; identical sound across policies. No human evidence. Start with low device volume.</p><label>Condition <select id="c"></select></label><label>Pair <select id="j"></select></label><label>Policy <select id="p"></select></label><p id="summary"></p><audio id="a" controls preload="none"></audio><div id="view"></div><a href="receipt.json">Full machine-readable receipt</a><script>const rows='''+payload+''';const c=document.querySelector('#c'),j=document.querySelector('#j'),p=document.querySelector('#p'),a=document.querySelector('#a');for(const [e,k] of [[c,'case'],[j,'pair'],[p,'policy']])for(const v of new Set(rows.map(r=>r[k])))e.add(new Option(v,v));function render(){const r=rows.find(r=>r.case===c.value&&r.pair===+j.value&&r.policy===p.value);document.querySelector('#summary').textContent=`Seed ${r.seed} · ${r.extraneous_starts} extraneous starts · peak ${r.peak_active} active`;if(+j.value===0){a.hidden=false;if(a.getAttribute('src')!==r.case+'.wav'){a.pause();a.src=r.case+'.wav';a.volume=.2}}else{a.pause();a.hidden=true;a.removeAttribute('src')}let h='<h2>Ground truth and associated starts</h2><table><tr><th>Identity</th><th>Expected</th><th>State</th><th>Start error (ms)</th><th>Release minus nominal end (ms)</th></tr>';for(const f of r.frames)h+=`<tr><td>${f.identity.join('/')}</td><td>${f.expected}</td><td>${f.state}</td><td>${f.start_error_samples===null?'—':f.start_error_samples/16}</td><td>${f.end_delta_samples===null?'—':f.end_delta_samples/16}</td></tr>`;h+='</table><h2>Events (milliseconds from capture start)</h2><table><tr><th>Time</th><th>Event</th><th>Source</th><th>Body start</th><th>Identity</th></tr>';for(const e of r.events)h+=`<tr><td>${e.sample/16}</td><td>${e.kind}</td><td>${e.source}</td><td>${e.body_start/16}</td><td>${e.identity??'—'}</td></tr>`;document.querySelector('#view').innerHTML=h+'</table>'}for(const e of [c,j,p])e.onchange=render;render()</script>''',encoding='utf-8')
    write(out/'manifest.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())}); print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))

if __name__=='__main__': run(*map(pathlib.Path,sys.argv[1:]))
