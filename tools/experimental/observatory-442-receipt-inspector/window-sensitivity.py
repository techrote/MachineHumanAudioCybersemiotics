"""Measurement lane, Refs #442/#443. Synthetic matched PCM, no human claims.
Run: python window-sensitivity.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
Original upstream observer and interval receiver reused; early/split reproduced
from window-admission.py at PIN (blob below), not a separate receiver design.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PIN='68232af33ab7b5666ab6a89d84a5e24d3532c973'
WINDOW_BLOB='83eafc7eae1fd9ff8961bb510af22afa4eb4a0fb'
INTERVAL_BLOB='32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3'
SEEDS=(4424101,4424102); MODES=('original','early20','split20'); S=1280
PHASES=(-30,-20,-10,0,10,20,30); GAINS=(.65,1.,1.5); NOISE=(0,150); DRIFT=(0,.005)
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def observer(mode):
    basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(320)/16000)
    def measure(w):
        scores=abs(basis@w)*2/320; k=int(scores.argmax()); top=float(scores[k]); second=float(np.partition(scores,-2)[-2]); return (18 if k==17 else k),top,(top-second)/max(top,1)
    def observe(slot):
        a=measure(slot[160:480])
        if mode=='early20': return a[0] if a[1]>=200 else None
        b=measure(slot[480:800]); best=max((a,b),key=lambda v:v[2] if v[1]>=200 else -1)
        return best[0] if best[1]>=200 and best[2]>=.35 else None
    return observe

def account(rows):
    groups={}; totals={}
    for r in rows:
        got=[(e['source'],*e['identity']) for e in r['events'] if e['kind']=='release']; want=list(map(tuple,r['expected']))
        hit=sum((Counter(got)&Counter(want)).values()); assert (hit,len(got)-hit,2-hit)==(r['correct'],r['wrong'],r['missing'])
        key=tuple(r[k] for k in ('seed','pair','phase_ms','gain','noise_sd','clock_stretch'))
        groups.setdefault(key,[]).append(r)
        for name in ('all',f"phase {r['phase_ms']}",f"gain {r['gain']}",f"noise {r['noise_sd']}",f"stretch {r['clock_stretch']}"):
            t=totals.setdefault(name,{}).setdefault(r['mode'],Counter()); t.update(expected=2,correct=hit,wrong=r['wrong'],missing=r['missing'],starts=sum(e['kind']=='start' for e in r['events']))
    for g in groups.values():
        assert len(g)==3 and {r['mode'] for r in g}==set(MODES) and len({r['pcm_sha256'] for r in g})==1
        assert len({tuple((e['source'],e['body_start'],e['sample']) for e in r['events'] if e['kind']=='start') for r in g})==1
    return totals,len(groups)

def run(root,out):
    assert blob(root/'interval-admission.py')==INTERVAL_BLOB
    m=runpy.run_path(str(root/'interval-admission.py')); p=runpy.run_path(str(root/'competing-starts.py')); s=runpy.run_path(str(root/'discourse-sync.py'))
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':m['PARENT'],'interval-admission.py':INTERVAL_BLOB}
    for f,b in pins.items(): assert blob(root/f)==b,f
    c=runpy.run_path(str(root/'causal-frame.py')); v=runpy.run_path(str(root/'version-bound-payload.py')); joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']
    _,raw,_=v['build'](root); old,new=raw; long=np.concatenate([v['extend'](w,k,'polynomial') for k,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs={'original':c['observe'],**{k:observer(k) for k in MODES[1:]}}; rows=[]; specimens=[]; out.mkdir(parents=True,exist_ok=False)
    # Fixed design, no tuning; same noise draw across gain/drift for each seed/pair/phase.
    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        for pair in range(2):
            a=pair%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); want=[[a,18,i],[b,13,k]]
            x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
            first=np.zeros(55*S,dtype=np.int32); m['put'](first,x,lead); second=np.zeros(len(y)*S,dtype=np.int32); m['put'](second,y,0)
            for phase in PHASES:
                start=lead+int(2.5*S)+16*phase; noise=rng.normal(0,1,len(first))
                for gain in GAINS:
                    for sd in NOISE:
                        for drift in DRIFT:
                            stretched=np.interp(np.arange(round(len(second)*(1+drift)))/(1+drift),np.arange(len(second)),second,left=0,right=0)
                            pcm=first.astype(float); pcm[start:start+len(stretched)]+=gain*stretched; pcm+=sd*noise; assert np.max(abs(pcm))<32767; pcm=np.rint(pcm).astype('<i2'); digest=sha(pcm.tobytes())
                            common=dict(seed=seed,pair=pair,phase_ms=phase,gain=gain,noise_sd=sd,clock_stretch=drift,expected=want,pcm_sha256=digest,peak=int(np.max(abs(pcm))))
                            for mode in MODES:
                                ev=m['acquire'](pcm,books,obs[mode],joint,'multiplex'); got=[(e['source'],*e['identity']) for e in ev if e['kind']=='release']; hit=sum((Counter(got)&Counter(map(tuple,want))).values()); rows.append(dict(common,mode=mode,correct=hit,wrong=len(got)-hit,missing=2-hit,events=ev))
                            if seed==SEEDS[0] and pair==0 and phase in (-20,20) and gain in (1.,1.5) and ((sd,drift) in ((0,0),(150,.005))):
                                f=f'phase{phase:+d}-gain{gain}-noise{sd}-stretch{drift}.wav'
                                with wave.open(str(out/f),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                                specimens.append(dict(common,file=f))
    totals,n=account(rows); assert n==len(SEEDS)*2*len(PHASES)*len(GAINS)*len(NOISE)*len(DRIFT)
    # Negative controls: false tally and unequal matched PCM must fail.
    for key,value in [('correct',99),('pcm_sha256','bad')]:
        bad=rows[:]; bad[0]=dict(bad[0],**{key:value})
        try: account(bad)
        except AssertionError: pass
        else: raise AssertionError('tamper accepted: '+key)
    receipt=dict(schema='mhac-window-sensitivity-v1',pin=PIN,window_reference_blob=WINDOW_BLOB,blobs=pins,source_sha256=sha(pathlib.Path(__file__).read_bytes()),seeds=SEEDS,conditions=n,decisions=len(rows),totals=totals,specimens=specimens,limits='Four new message pairs, fixed factorial, no tuning. Linear interpolation stretches B waveform including pitch; not pure clock correction. Noise SD in signed PCM counts; gain is linear B/A. No clipping, no human evidence or independent acoustic decoder. Marginals share message pairs; not independent trials.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    compact=[{k:v for k,v in r.items() if k!='events'} for r in rows]; gallery=''.join(f'<p>{z["file"]}<br><audio controls preload="none" src="{z["file"]}"></audio></p>' for z in specimens)
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Window sensitivity</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto;padding:1em}select{margin:8px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #aaa}pre{white-space:pre-wrap}</style><h1>Matched PCM window sensitivity</h1><p>Synthetic only. Select factors; all policies evaluated on identical PCM. Counts are not human performance. Audio opt-in; start low.</p><div id="controls"></div><table id="results"></table><h2>Original specimens</h2>'''+gallery+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Full event traces</a></p><script>const rows='''+json.dumps(compact)+''';const keys=['phase_ms','gain','noise_sd','clock_stretch'];for(const k of keys){let l=document.createElement('label');l.textContent=k;let s=document.createElement('select');s.id=k;s.add(new Option('All','all'));for(const v of [...new Set(rows.map(r=>r[k]))])s.add(new Option(v,v));s.onchange=render;l.append(s);controls.append(l)}function render(){let a=rows.filter(r=>keys.every(k=>document.getElementById(k).value==='all'||String(r[k])===document.getElementById(k).value));results.innerHTML='<tr><th>Mode</th><th>Expected</th><th>Correct</th><th>Wrong</th><th>Missing</th></tr>'+['original','early20','split20'].map(m=>{let b=a.filter(r=>r.mode===m);return '<tr><td>'+m+'</td><td>'+2*b.length+'</td>'+['correct','wrong','missing'].map(k=>'<td>'+b.reduce((n,r)=>n+r[k],0)+'</td>').join('')+'</tr>'}).join('')}render();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>''',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps({k:receipt[k] for k in ('conditions','decisions','totals')},indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
