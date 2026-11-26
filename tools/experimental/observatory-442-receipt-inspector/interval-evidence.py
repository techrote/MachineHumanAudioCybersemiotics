"""Measurement #442: interval evidence accounting; synthetic trace audit, not human evidence.
Usage: python interval-evidence.py SOURCE_DIR INTERVAL_OUTPUT NEW_OUTPUT
Requires only the Python standard library. Upstream regeneration uses NumPy.
"""
import collections as C
import hashlib, json, pathlib, sys, wave, shutil

PIN = 'f215e18d8cbcbaa7c19fd5f199cd69bb510c1c22'
SOURCE_BLOB = '32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3'
POLICIES = ('keep-two','replace-two','exclusive','multiplex')
LIMITS = (0, 800, 1600, 3200, 3280, 5760)

def require(test, message):
    if not test: raise ValueError(message)

def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def key(e): return (e['source'],e['body_start'])
def identity(e): return (e['source'],*e['identity'])

def audit(row):
    active={}; candidates={}; reports={}; released={}; final={}; last=-1
    want=C.Counter(map(tuple,row['expected'])); got=C.Counter()
    for e in row['events']:
        t=e['sample']; k=key(e); kind=e['kind']
        require(t>=last and t%80==0,'event clock')
        if t>last:
            while active and next(iter(active.values())) in ('reject','timeout'):
                active.pop(next(iter(active)))
        last=t
        if kind=='start':
            require(k not in active and len(active)<2,'capacity/start'); active[k]='pending'
        elif kind in ('ignore','overflow-ready-protected'):
            require(len(active)==2 and k not in active,'overflow capacity')
            if kind=='overflow-ready-protected': require(list(active.values())[-1]!='pending','protected state')
        elif kind in ('candidate','reject','timeout'):
            require(active.get(k)=='pending','candidate lifecycle'); active[k]=kind
            if kind=='candidate':
                require(e['seen'][-2:]==[18,18] and len(e['seen'])==e['identity'][0]+2,'candidate length')
                require(t>=k[1]+len(e['seen'])*1280,'premature candidate'); candidates[k]=e
            if kind in ('reject','timeout'): final[k]=(kind,t)
        elif kind in ('overlap-conflict','overlap-coadmission'):
            require(len(e['candidates'])==2,'report arity'); pair=[]
            for c in e['candidates']:
                ck=(c['source'],c['start']+2560); q=candidates.get(ck)
                require(q is not None and active.get(ck)=='candidate' and ck not in reports,'report readiness')
                require(c['identity']==q['identity'] and c['ready']==q['sample'] and c['end']==ck[1]+len(q['seen'])*1280,'report provenance')
                require(t>=c['ready'],'report causality'); pair.append(c); reports[ck]=(kind,t)
            require(max(c['start'] for c in pair)<min(c['end'] for c in pair),'report interval')
            if kind=='overlap-conflict':
                for c in pair:
                    ck=(c['source'],c['start']+2560); final[ck]=(kind,t); active.pop(ck)
        elif kind=='release':
            q=candidates.get(k)
            require(q is not None and active.get(k)=='candidate' and k not in released,'release lifecycle')
            require(identity(e)==identity(q) and e['ready_sample']==q['sample'] and e['wait_samples']==t-q['sample'],'release readiness')
            got[identity(e)]+=1; released[k]=t; final[k]=(kind,t); active.pop(k)
        elif kind in ('evict','suppress-overlap'):
            require(k in active,'discard lifecycle'); final[k]=(kind,t); active.pop(k)
        else: raise ValueError('unknown event '+kind)
    require(got==C.Counter(map(tuple,row['decoded'])),'decoded accounting')
    correct=sum((want&got).values()); require((correct,sum(got.values())-correct,sum(want.values())-correct)==(row['correct'],row['wrong'],row['missing']),'outcome accounting')
    require(all(k in final for k in candidates),'unresolved completed candidate')
    require(all(v[0]!='overlap-coadmission' or k in released for k,v in reports.items()),'coadmission missing release')
    evidence=[]; remaining=want.copy()
    for k,q in candidates.items():
        ident=identity(q); expected=remaining[ident]>0
        if expected: remaining[ident]-=1
        end,t=final[k]; evidence.append(dict(identity=list(ident),expected=expected,ready=q['sample'],end=t,wait=t-q['sample'],disposition=end,reported=k in reports))
    for ident,n in remaining.items():
        for _ in range(n): evidence.append(dict(identity=list(ident),expected=True,disposition='no-valid-candidate',ready=None,end=None,wait=None,reported=False))
    return evidence

def run(root, inp, out):
    require(blob(root/'interval-admission.py')==SOURCE_BLOB,'source blob')
    manifest=json.loads((inp/'manifest.json').read_text()); require(set(manifest)=={p.name for p in inp.iterdir()}-{'manifest.json'},'manifest inventory')
    for f,h in manifest.items(): require(sha((inp/f).read_bytes())==h,'manifest '+f)
    receipt=json.loads((inp/'receipt.json').read_text())
    require(receipt['source_sha256']==sha((root/'interval-admission.py').read_bytes()),'receipt source')
    for f,h in receipt['blobs'].items(): require(blob(root/f)==h,'source '+f)
    rows=[json.loads(s) for s in (inp/'traces.jsonl').read_text().splitlines()]; groups=C.defaultdict(list)
    stats={p:C.Counter() for p in POLICIES}; deadlines={p:{str(d):0 for d in LIMITS} for p in POLICIES}; detail=[]
    for r in rows:
        groups[(r['case'],r['pair'])].append(r); ev=audit(r); p=r['policy']; s=stats[p]
        for e in ev:
            if not e['expected']: s['unexpected-candidate']+=1; continue
            s['expected']+=1; s[e['disposition']]+=1
            if e['ready'] is not None: s['candidate']+=1
            if e['reported']: s['reported']+=1
            if e['disposition']=='release':
                for d in LIMITS: deadlines[p][str(d)]+=int(e['wait']<=d)
        detail.append(dict(case=r['case'],pair=r['pair'],policy=p,evidence=ev,events=r['events']))
    require(len(rows)==receipt['observations'] and len(groups)==receipt['physical_pcm'],'inventory')
    for group in groups.values():
        require(len(group)==4 and {r['policy'] for r in group}==set(POLICIES) and len({r['pcm_sha256'] for r in group})==1 and len({json.dumps(r['expected']) for r in group})==1,'matched conditions')
    out.mkdir(parents=True,exist_ok=False)
    for v in receipt['specimens']:
        f=v['file']
        with wave.open(str(inp/f),'rb') as w:
            require((w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,16000),'WAV format'); require(sha(w.readframes(w.getnframes()))==v['pcm_sha256'],'WAV hash')
        shutil.copyfile(inp/f,out/f)
    result=dict(schema='mhac-interval-evidence-v1',source_ref=PIN,source_blob=SOURCE_BLOB,input_manifest_sha256=sha((inp/'manifest.json').read_bytes()),source_sha256=sha(pathlib.Path(__file__).read_bytes()),observations=len(rows),matched_groups=len(groups),sample_rate=16000,stats=stats,deadline_samples=LIMITS,release_within=deadlines,limits='Relative to candidate readiness, not arrival or full task deadline. Conflict reporting is not release. Finite constructed corpus; no human evidence.')
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8'); (out/'evidence.json').write_text(json.dumps(detail)+'\n',encoding='utf8')
    page='''<!doctype html><meta charset="utf-8"><title>Interval evidence</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto;padding:0 1em}pre{white-space:pre-wrap}table{border-collapse:collapse}td,th{padding:.5em;border:1px solid #888}</style><h1>Interval evidence inspector</h1><p>Synthetic trace audit. Candidate readiness is not semantic release. Deadline is measured from readiness, not frame onset. Conflict reports are not releases.</p><label>Policy <select id="p"></select></label> <label>Post-readiness budget <select id="d"></select></label><p id="summary"></p><label>Trace <select id="r"></select></label><p><audio id="audio" controls preload="none"></audio></p><pre id="trace"></pre><p><a href="receipt.json">Receipt</a> | <a href="evidence.json">All evidence</a></p><script>const data=DATA, rows=ROWS;const p=document.getElementById('p'),d=document.getElementById('d'),r=document.getElementById('r'),a=document.getElementById('audio');for(const x of Object.keys(data.stats))p.add(new Option(x,x));for(const x of data.deadline_samples)d.add(new Option(x/16+' ms',x));function show(){const s=data.stats[p.value];document.getElementById('summary').textContent='Released within budget: '+data.release_within[p.value][d.value]+'/'+s.expected+'; candidate evidence: '+s.candidate+'/'+s.expected;const x=rows[Number(r.value)];document.getElementById('trace').textContent=JSON.stringify(x,null,2);a.pause();if(x.pair===0){a.src=x.case+'.wav';a.volume=.2;a.hidden=false}else{a.removeAttribute('src');a.hidden=true}}function select(){r.replaceChildren();rows.forEach((x,i)=>{if(x.policy===p.value)r.add(new Option(x.case+' / pair '+x.pair,i))});show()}p.onchange=select;d.onchange=show;r.onchange=show;select();</script>'''.replace('DATA',json.dumps(result)).replace('ROWS',json.dumps(detail))
    (out/'index.html').write_text(page,encoding='utf8'); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf8'); print(json.dumps(result,indent=2))

if __name__=='__main__': run(*map(pathlib.Path,sys.argv[1:]))
