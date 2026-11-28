"""Refs #442/#443. Single-node synthetic PCM; independent transcription of #453 dual-morphology.
Run: OPENBLAS_NUM_THREADS=1 python band-local-audit.py NEW_OUTPUT
"""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

PIN='a012850105079a077848e29414ea8efef760c264'
BLOB='4b23f32d45fc4f389cbd09cc86e5667031f6b4a1'
PARENT='8dfade66fe75b63fc4967a36260a30328aff15f4'
SEED=4425701

def sha(b): return hashlib.sha256(b).hexdigest()
base=Path(__file__).with_name('depth-calibration.py')
assert sha(base.read_bytes())=='fb25fb572972bd5476c2f00acf3323e0a445496d589516bef92945936b917b7d'
spec=importlib.util.spec_from_file_location('cal',base); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c); d=c.d
F=(*c.F,np.arange(5)*100+4300,np.arange(5)*100+5000)
LAY={'check3':((0,1),(2,3),(4,5)), 'dual3':((0,1,5),(2,3),(4,6))}
GRID=np.arange(-40,41,5); T=np.arange(160,800)/d.RATE
# Local reference bins lie between carriers and outside the band edges.
LOCAL=[np.arange(f[0]-50,f[-1]+51,100) for f in F]
GLOBAL=np.arange(425,4026,100)
# One spectral transform for all candidate and reference bins.
HZ=sorted({int(v+h) for f in (*F,*LOCAL,GLOBAL) for v in f for h in GRID})
BANK=np.exp(-2j*np.pi*np.array(HZ)[:,None]*T)
IX={v:i for i,v in enumerate(HZ)}
def indices(f): return np.array([[IX[int(v+h)] for v in f] for h in GRID])
FI=[indices(f) for f in F]; LI=[indices(f) for f in LOCAL]; GI=indices(GLOBAL)
Q=list(itertools.product(range(3),repeat=3))
def code(q,mode):
    e,s,a=q
    return (*q,(e+s+a)%3) if mode=='check3' else (*q,(e+s+a)%5,(e+2*s+3*a)%5)
BOOK={m:[code(q,m) for q in Q] for m in LAY}
def repair(obs,mode,correct=False):
    missing=obs.count(None)
    if missing>(1 if mode=='check3' else 2): return None
    radius=int(correct and mode=='dual3' and not missing)
    candidates=[w for w in BOOK[mode] if sum(v is not None and v!=u for v,u in zip(obs,w))<=radius]
    if len(candidates)!=1:return None
    w=candidates[0];return w,tuple('inferred' if v is None else 'corrected' if v!=u else 'observed' for v,u in zip(obs,w))

def noise(z,kind):
    if kind=='white': return z
    a=np.apply_along_axis(lambda v:np.convolve(v,np.ones(12)/12,'same'),1,z)
    return a/np.sqrt(np.mean(a*a,axis=1,keepdims=True))
def spectra(x): return abs(x@BANK.T)*2/640

def calibrate():
    # Separate noise-only windows; calibrate the maximum over all 17 offsets,
    # not just the nominal bin. Worst of the two synthetic noise families.
    rng=np.random.default_rng(SEED+1); k=[]; local=[]
    z=rng.normal(size=(4096,640))
    white=spectra(z)
    colored=spectra(noise(z,'colored'))
    for b in range(7):
        k.append(float(np.quantile(white[:,FI[b][8]].max(axis=1),.999)))
        local.append(max(float(np.quantile((s[:,FI[b]].max(axis=2)/np.maximum(1e-12,np.median(s[:,LI[b]],axis=2))).max(axis=1),.99)) for s in (white,colored)))
    return k,local

def render(row,mode,shift,phase):
    x=np.zeros((3,d.SLOT))
    for j,g in enumerate(LAY[mode]):
        for b in g:
            if row[b] is not None:x[j,:d.ACTIVE]+=d.AMP*d.W*np.sin(2*np.pi*(F[b][row[b]]+shift)*d.T+phase)
    return x

def observe(y,mode,k,local):
    s=spectra(y[:,160:800].astype(float)); cols={b:s[j,FI[b]] for j,g in enumerate(LAY[mode]) for b in g}
    h=int(np.argmax(sum(v.max(axis=1) for v in cols.values())))
    result={p:[] for p in ('global','local')}; evidence=[]
    for b in sorted(cols):
        j=next(j for j,g in enumerate(LAY[mode]) if b in g); v=cols[b][h]; o=np.argsort(v); a=float(v[o[-1]]); margin=a-float(v[o[-2]])
        glob=float(np.median(s[j,GI[h]])*np.sqrt(640/(4*np.log(2))))
        loc=float(np.median(s[j,LI[b][h]]))
        ts=(max(80,k[b]*glob),max(80,local[b]*loc))
        for p,t in zip(result,ts):result[p].append(int(o[-1]) if a>=t and margin>=t/3 else None)
        evidence.append([a,margin,glob,loc,*ts])
    return result,int(GRID[h]),evidence

CONDS={'clean':(0,0,'white'),'white25':(25,1000,'white'),'offgrid':(27,1000,'white'),'colored25':(25,1000,'colored'),'absent_white':(25,1000,'white'),'absent_colored':(25,1000,'colored'),'erase2':(25,1000,'white'),'replace1':(25,1000,'white'),'replace2':(25,1000,'white')}
def run(out):
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED); k,local=calibrate(); traces=[]; gallery=[]
    for i,q in enumerate(Q*4):
        row=(int(rng.integers(4)),0,*q); phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,d.SLOT))
        for mode,(cond,(shift,sd,kind)) in itertools.product(LAY,CONDS.items()):
            expected=(*row[:2],*code(q,mode)); x=render(expected,mode,shift,phase); scale=d.AMP/np.max(abs(x)); changed=list(expected)
            if cond=='erase2':changed[2]=changed[3]=None
            if cond.startswith('replace'):changed[2]=(changed[2]+1)%3
            if cond=='replace2':changed[3]=(changed[3]+2)%3
            signal=render(changed,mode,shift,phase)*scale
            if cond.startswith('absent'):signal[:]=0
            y=d.pcm(signal+sd*noise(z,kind)); obs,h,evidence=observe(y,mode,k,local)
            for p,v in obs.items():
                for rule in (('strict',) if mode=='check3' else ('strict','correct')):
                    # Check lexical/depth validity, never use truth to admit a message.
                    if v[0] is not None and v[0]<4 and v[1]==0:
                        got=repair(tuple(v[2:]),mode,rule=='correct')
                    else:got=None
                    status='withheld' if got is None else 'correct' if not cond.startswith('absent') and v[:2]==list(row[:2]) and got[0][:3]==q else 'wrong'
                    traces.append(dict(fixture=i,mode=mode,condition=cond,receiver=p,rule=rule,expected=expected,observed=v,decoded=got,status=status,shift=shift,selected=h,phase=phase,metrics=evidence,pcm_sha256=sha(y.tobytes())))
            if i==0 and cond in ('clean','colored25','replace2'):
                name=f'{mode}-{cond}.wav'; safe=d.pcm(y.astype(float)*.25)
                with wave.open(str(out/name),'wb') as w:w.setparams((1,2,d.RATE,0,'NONE','not compressed'));w.writeframes(safe.tobytes())
                gallery.append(name)
    groups=[]
    for key in sorted({(t['mode'],t['condition'],t['receiver'],t['rule']) for t in traces}):
        a=[t for t in traces if tuple(t[k] for k in ('mode','condition','receiver','rule'))==key]; assert len(a)==108
        groups.append(dict(zip(('mode','condition','receiver','rule'),key),counts=dict(Counter(t['status'] for t in a)),inferred=sum(t['decoded'] is not None and 'inferred' in t['decoded'][1][:3] for t in a),corrected=sum(t['decoded'] is not None and 'corrected' in t['decoded'][1][:3] for t in a)))
    for m in LAY:
        assert len(set(BOOK[m]))==27
        assert min(sum(a!=b for a,b in zip(x,y)) for x,y in itertools.combinations(BOOK[m],2))==(2 if m=='check3' else 3)
    assert all(t['status']!='correct' for t in traces if t['condition'].startswith('absent'))
    receipt=dict(seed=SEED,source_sha256=sha(Path(__file__).read_bytes()),parent=PARENT,grammar=PIN,grammar_blob=BLOB,python=sys.version.split()[0],numpy=np.__version__,conditions=CONDS,calibration={'windows_per_family':4096,'global':k,'local':local},metric_order=['peak','margin','global_sd','local_median','global_threshold','local_threshold'],groups=groups,pcm_trials=108*2*len(CONDS),decisions=len(traces),limits='Single leaf node only, balanced qualifiers repeated four times; not tree holdout. Matched peak before faults; known slots/layout. Local ratio calibrated against noise-only search envelope, not guaranteed false acceptance. One shared noise draw per matched fixture across conditions and layouts. Synthetic, no human evidence or authentication.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces))
    html='<!doctype html><meta charset=utf-8><title>Band-local audit</title><style>body{font:16px system-ui;max-width:950px;margin:2em auto}td,th{padding:.5em;border-bottom:1px solid #aaa}</style><h1>Band-local qualifier audit</h1><p>Synthetic single-node PCM; 108 paired cases per condition. No human evidence.</p><label>Condition <select id="c">'+''.join(f'<option>{v}</option>' for v in CONDS)+'</select></label><table><thead><tr><th>Layout</th><th>Receiver</th><th>Rule</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Inferred</th><th>Corrected</th></tr></thead><tbody id="r"></tbody></table><h2>Common gain audition copies</h2>'+''.join(f'<p>{p}<br><audio controls preload="none" src="{p}"></audio></p>' for p in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const data='+json.dumps(groups)+';function draw(){r.replaceChildren(...data.filter(x=>x.condition===c.value).map(x=>{const t=document.createElement("tr");for(const v of [x.mode,x.receiver,x.rule,x.counts.correct||0,x.counts.wrong||0,x.counts.withheld||0,x.inferred,x.corrected]){const e=document.createElement("td");e.textContent=v;t.append(e)}return t}))}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html);(out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(receipt['pcm_trials'],receipt['decisions'])
if __name__=='__main__':run(Path(sys.argv[1]))
