"""Measurement #442: conditional clarification on frozen acoustic reports.
Usage: python clarification-audit.py SOURCE_DIR COVERAGE_DIR NEW_OUTPUT_DIR
Synthetic target assignments, not observed intent; known reply alignment.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='60b7f27f7260d1a8ac00be5c3d13dc853a00a72c'; MEAS='185738e06eae9cd36a8bbbac533027e478c6c3a3'; TAG_PIN='b9c0af501b38ac516f194a362c8688c95657b32b'
BLOBS={'version-bound-payload.py':'7ef6881cefa9c34355d024aeea671d021b674a55','version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f','ambiguity-coverage.py':'7b5979d57908aafbea4d93337fd09d4ea76b96ba'}
SHA=lambda b:hashlib.sha256(b).hexdigest(); S=1280; F=16000; SEED=4424401
T=np.arange(640); ENV=np.minimum(1,np.minimum(T/30,(639-T)/30)); FREQ=np.arange(400,2001,100)
TONES=np.rint(1500*ENV*np.sin(2*np.pi*FREQ[:,None]*T/F+.137)).astype(np.int16); BASIS=np.exp(-2j*np.pi*FREQ[:,None]*np.arange(400)/F)
def render(tokens,seed,sd):
    a=np.zeros((len(tokens),S)); a[:,:640]=TONES[tokens]; return np.clip(np.rint(a+np.random.default_rng(seed).normal(0,sd,a.shape)),-32768,32767).astype('<i2')
def observe(a):
    scores=abs(a[:,80:480]@BASIS.T)/200; return [int(x.argmax()) if x.max()>=600 else -1 for x in scores]
def coordinate(book,ids):
    if len(ids)<2: raise ValueError('no partition')
    choices=[]
    for p in range(book.shape[1]):
        counts=list(Counter(map(int,book[ids,p])).values())
        if len(counts)>1: choices.append((max(counts),sum(x*x for x in counts),p))
    return min(choices)[2]
def tag(context):
    n=int(SHA(json.dumps(context,separators=(',',':')).encode()),16)%289; return [n//17,n%17]
def narrow(book,ids,p,t,obs):
    if obs[:2]!=t: return []
    v,n=Counter(obs[2:]).most_common(1)[0]; return [i for i in ids if book[i,p]==v] if n>=2 and v>=0 else []
def status(ids,target): return 'correct' if ids==[target] else 'wrong-singleton' if len(ids)==1 else 'retained' if target in ids else 'wrong-set' if ids else 'withheld'
def run(root,coverage,out):
    for name,h in BLOBS.items():
        b=(root/name).read_bytes(); assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==h,name
    assert SHA((coverage/'receipt.json').read_bytes())=='fa977026f70ad01096537da03213ba184095e76a11fc47c550254e72608611f6'
    rawtrace=(coverage/'traces.jsonl').read_bytes(); assert SHA(rawtrace)=='c7aa523e0b7ed351c1bb67531755a91af982e8c5165831049fdce346438dc054'
    v=runpy.run_path(str(root/'version-bound-payload.py')); _,raw,_=v['build'](root); old,new=raw; long=np.concatenate([v['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={s:{13:np.column_stack((np.zeros((len(old),3),int),(old+s*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+s*np.arange(15)**5)%17))} for s in (0,1)}
    out.mkdir(parents=True,exist_ok=False); traces=[]; stats={}; cache={}; specimens=[]
    for row in map(json.loads,rawtrace.splitlines()):
        if row['gain']==0: continue
        book=books[row['source']][row['length']]; ids=sorted(row['report']['ids']); assert len(ids)==row['report']['count']<=8
        for target in row['expected']:
            for ci,cond in enumerate(('clean','noise2500','two-substitutions')):
                seed=SEED*100000+row['noise_seed']*10+target*3+ci; sd=2500 if ci==1 else 0; key=(row['pcm_sha256'],target,cond)
                if key not in cache:
                    full=book[target].tolist(); rival=next(i for i in row['expected'] if i!=target)
                    if ci==2:
                        positions=np.flatnonzero(book[target]!=book[rival])[:2]; assert len(positions)==2
                        for p in positions: full[int(p)]=int(book[rival,p])
                    pcm=render(full,seed,sd); obs=observe(pcm); distance=np.count_nonzero((book!=obs)&(np.array(obs)>=0),axis=1); got=np.flatnonzero(distance<=2).tolist(); cache[key]=(got,SHA(pcm.tobytes()),obs)
                fullgot,fullhash,fullobs=cache[key]; q=[]; qhash=None; qobs=None; p=None; slots=0
                if len(ids)==1: q=ids.copy()
                elif len(ids)>1:
                    p=coordinate(book,ids); context=[TAG_PIN,row['source'],row['length'],ids,p,row['noise_seed']]; t=tag(context); value=int(book[target,p]); tokens=t+[value]*3
                    if ci==2:
                        other=next(i for i in ids if book[i,p]!=value); tokens[2:4]=[int(book[other,p])]*2
                    pcm=render(tokens,seed,sd); qobs=observe(pcm); qhash=SHA(pcm.tobytes()); q=narrow(book,ids,p,t,qobs); slots=5
                    assert set(q)<=set(ids)
                    if not any(s['condition']==cond for s in specimens):
                        name=cond+'.wav'
                        with wave.open(str(out/name),'wb') as w:w.setparams((1,2,F,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
                        specimens.append(dict(file=name,condition=cond,pcm_sha256=qhash,peak=int(np.max(np.abs(pcm.astype(int))))))
                fallback=q if q else fullgot; choices={'query-only':(q,slots),'fallback-on-empty':(fallback,slots+(0 if q else row['length'])),'full-always':(fullgot,row['length'])}
                for mode,(result,cost) in choices.items():
                    st=status(result,target); k=f"{row['mode']}:{cond}:{mode}"; stats.setdefault(k,Counter()).update([st]); stats[k]['slots']+=cost; stats[k]['target-omitted']+=int(target not in ids)
                    traces.append(dict(input_mode=row['mode'],condition=cond,policy=mode,source=row['source'],length=row['length'],gain=row['gain'],kind=row['kind'],input_pcm=row['pcm_sha256'],target=target,initial=ids,coordinate=p,query_observed=qobs,query_pcm=qhash,full_observed=fullobs,full_pcm=fullhash,returned=result,status=st,reply_slots=cost,seed=seed))
    assert len(traces)==6480 and len(cache)==720
    assert all(r['target'] in r['returned'] for r in traces if r['policy']=='full-always' and r['condition']=='clean')
    assert all(r['target'] not in r['returned'] for r in traces if r['policy']=='query-only' and r['target'] not in r['initial'])
    receipt=dict(schema='mhac.clarification-audit/1',grammar_pin=PIN,grammar_reference_blob='32ffadda8146153ebbb90ebcd343129986512de8',measurement_pin=MEAS,blobs=BLOBS,input_sha256=SHA(rawtrace),seed=SEED,source_sha256=SHA(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,trials=len(traces),unique_full_pcm=len(cache),stats=stats,specimens=specimens,limits='Hypothetical targets enumerate both constructed alternatives, not observed intent or probabilities. Known source/length and reply alignment, trusted out-of-band query, no framing/query cost, no authentication. Full body uses radius two, no source acquisition. Different slot counts/energy; targeted two substitutions per payload, not equal error rates. Not human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces),encoding='utf-8')
    gallery=''.join(f'<p>{s["condition"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in specimens)
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Clarification audit</title><style>body{font:16px system-ui;max-width:960px;margin:auto;padding:1em}td,th{padding:.5em;border-bottom:1px solid #aaa}pre{white-space:pre-wrap}</style><h1>Conditional clarification audit</h1><p>Synthetic target assignments only. Reply slots exclude queries/framing. No action authority. Start at low volume.</p><label>Input receiver <select id="m"></select></label> <label>Condition <select id="c"></select></label><table id="t"></table><label>Trace <select id="r"></select></label><pre id="d"></pre>'''+gallery+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps(traces)+''';const m=document.getElementById('m'),c=document.getElementById('c'),t=document.getElementById('t'),r=document.getElementById('r'),d=document.getElementById('d');for(const v of new Set(rows.map(x=>x.input_mode)))m.add(new Option(v,v));for(const v of new Set(rows.map(x=>x.condition)))c.add(new Option(v,v));let a=[];function detail(){d.textContent=JSON.stringify(a[+r.value],null,2)}function draw(){a=rows.filter(x=>x.input_mode===m.value&&x.condition===c.value);t.innerHTML='<tr><th>Policy</th><th>Correct</th><th>Wrong singleton</th><th>Other</th><th>Reply slots</th></tr>'+['query-only','fallback-on-empty','full-always'].map(p=>{const z=a.filter(x=>x.policy===p),n=z.filter(x=>x.status==='correct').length,w=z.filter(x=>x.status==='wrong-singleton').length;return '<tr>'+[p,n,w,z.length-n-w,z.reduce((s,x)=>s+x.reply_slots,0)].map(x=>'<td>'+x+'</td>').join('')+'</tr>'}).join('');r.replaceChildren();a.forEach((x,i)=>r.add(new Option(x.policy+' / '+x.kind+' / '+x.gain+' / '+x.target,i)));detail()}m.onchange=c.onchange=draw;r.onchange=detail;draw();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>''',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:SHA(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(stats))
if __name__=='__main__':run(*map(pathlib.Path,sys.argv[1:]))
