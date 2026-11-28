"""Refs #442/#443. Synthetic five-band receiver calibration; no human evidence.
Run: OPENBLAS_NUM_THREADS=1 python depth-calibration.py OUTPUT
"""
import hashlib, importlib.util, itertools, json, sys, wave
from pathlib import Path
from collections import Counter
import numpy as np

PARENT='1be3c82fa74264121400c88de0679b85ba8350c4'
GRAMMAR='39421a0d705d5257cf8083e36a7739dc72123398'
GRAMMAR_BLOB='1d7075c4b569e1207c74e935beffaaef4927d70f'
SEED=4425501
BASE=Path(__file__).with_name('depth-level-audit.py')
def digest(b): return hashlib.sha256(b).hexdigest()
assert digest(BASE.read_bytes())=='e0e9206d581e40277ab9bfe8873bf2ca90642063a9b66da24f71bc2ea7a82a3c'
spec=importlib.util.spec_from_file_location('depth',BASE); d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
F=(*d.F,np.arange(3)*100+2800,np.arange(3)*100+3300,np.arange(3)*100+3800)
B=[np.exp(-2j*np.pi*f[:,None]*np.arange(160,800)/d.RATE) for f in F]
# Integer DFT bins halfway between nominal 100-Hz tones; orthogonal on 640 samples.
OFF=np.exp(-2j*np.pi*np.arange(425,4026,100)[:,None]*np.arange(160,800)/d.RATE)
MODES={'serial':((0,),(1,),(2,),(3,),(4,)), 'hybrid':((0,1),(2,3,4)), 'poly':((0,1,2,3,4),)}
POLICIES=('fixed','oracle','guard','offbin')
CONDS=('clean','white1000','white3500','active3500','guard3500','absent','replacement')

def render(rows,mode,phase):
    blocks=[]
    for row in rows:
        for group in MODES[mode]:
            x=np.zeros(d.SLOT)
            for b in group: x[:d.ACTIVE]+=d.AMP*d.W*np.sin(2*np.pi*F[b][row[b]]*d.T+phase)
            blocks.append(x)
    return np.array(blocks)

def scores(x,b): return abs(x@B[b].T)*2/640
def observe(y,mode):
    x=y[:,160:800].astype(float); n=len(MODES[mode]); bands=[]
    guard=np.sqrt(np.mean(y[:,960:].astype(float)**2,axis=1))
    off=np.median(abs(x@OFF.T)*2/640,axis=1)*np.sqrt(640/(4*np.log(2)))
    for b in range(5):
        j=next(j for j,g in enumerate(MODES[mode]) if b in g)
        s=scores(x[j::n],b); ix=np.argsort(s,axis=1); top=ix[:,-1]; a=s[np.arange(len(s)),top]; margin=a-s[np.arange(len(s)),ix[:,-2]]
        bands.append((top,a,margin,guard[j::n],off[j::n]))
    return bands
def decide(bands,policy,sd,k):
    cols=[]
    for b,(top,a,m,g,o) in enumerate(bands):
        t=720 if policy=='fixed' else np.maximum(80,k[b]*({'oracle':sd,'guard':g,'offbin':o}[policy]))
        cols.append([int(v) if ok else None for v,ok in zip(top,(a>=t)&(m>=(240 if policy=='fixed' else t/3)))])
    return list(zip(*cols))

def decode(rows):
    if any(any(v is None for v in row) for row in rows): return None
    tree=d.decode([r[:2] for r in rows]); return (tree,tuple(r[2:] for r in rows)) if tree is not None else None

def run(out):
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED)
    # Calibrate normalized band maxima from independent unit-variance Gaussian windows.
    cal=np.random.default_rng(SEED+1).normal(size=(8192,640)); k=[float(np.quantile(scores(cal,b).max(axis=1),.999)) for b in range(5)]
    trees=d.catalog(); upstream=set(np.random.default_rng(452510).choice(len(trees),96,replace=False)); audit=set(np.random.default_rng(4425401).choice(sorted(set(range(len(trees)))-upstream),192,replace=False)); grammar=set(np.random.default_rng(452520).choice(sorted(set(range(len(trees)))-upstream-audit),96,replace=False))
    picks=rng.choice(sorted(set(range(len(trees)))-upstream-audit-grammar),96,replace=False); traces=[]; gallery=[]
    for i,idx in enumerate(picks):
        tree=trees[int(idx)]; rows=[(*r,*map(int,rng.integers(0,3,3))) for r in d.encode(tree)]; target=decode(rows); phase=float(rng.uniform(0,2*np.pi)); assert target is not None
        ref=render(rows,'serial',phase); z=np.random.default_rng(SEED+100+i).normal(size=(len(rows),5,d.SLOT))
        for mode,norm,cond in itertools.product(MODES,('peak','energy'),CONDS):
            n=len(MODES[mode]); full=render(rows,mode,phase); scale=np.max(abs(ref))/np.max(abs(full)) if norm=='peak' else np.linalg.norm(ref)/np.linalg.norm(full)
            changed=list(rows); j=i%len(rows); changed[j]=(*rows[j][:2],(rows[j][2]+1)%3,*rows[j][3:])
            x=render(changed,mode,phase) if cond=='replacement' else full.copy(); sd=1000 if cond=='white1000' else 3500 if cond in ('white3500','active3500','guard3500','absent') else 0
            noise=z[:,:n,:].reshape(-1,d.SLOT).copy(); active_sd=sd
            if cond=='active3500': noise[:,960:]=0
            if cond=='guard3500': noise[:,:960]=0; active_sd=0
            if cond=='absent': x[:]=0
            clean=d.pcm(x*scale); y=d.pcm(clean.astype(float)+sd*noise); bands=observe(y,mode)
            for policy in POLICIES:
                obs=decide(bands,policy,active_sd,k); got=decode(obs); status='withheld' if got is None else 'correct' if cond!='absent' and got==target else 'wrong'
                traces.append(dict(fixture=int(idx),expected=rows,observed=obs,phase=phase,mode=mode,norm=norm,condition=cond,policy=policy,status=status,guard_sd=round(float(np.mean(bands[0][3])),3),offbin_sd=round(float(np.mean(bands[0][4])),3),samples=int(y.size),peak=int(np.max(abs(clean.astype(int)))),energy=int(np.sum(clean.astype(np.int64)**2)),pcm_sha256=digest(y.tobytes())))
            if i==0 and cond=='clean' and norm=='peak':
                p=out/f'{mode}.wav'
                with wave.open(str(p),'wb') as w: w.setparams((1,2,d.RATE,0,'NONE','not compressed')); w.writeframes(y.tobytes())
                gallery.append(p.name)
    groups=[]
    for key in itertools.product(MODES,('peak','energy'),CONDS,POLICIES):
        r=[t for t in traces if tuple(t[k] for k in ('mode','norm','condition','policy'))==key]; assert len(r)==96
        groups.append(dict(zip(('mode','norm','condition','policy'),key),counts=dict(Counter(t['status'] for t in r))))
    assert len(traces)==96*3*2*7*4 and not set(picks)&(upstream|audit|grammar)
    assert all(t['status']=='correct' for t in traces if t['condition']=='clean' and t['norm']=='energy')
    assert all(t['status']!='correct' for t in traces if t['condition']=='absent')
    assert all(t['status']=='wrong' for t in traces if t['condition']=='replacement' and t['norm']=='energy')
    receipt=dict(schema='mhac-depth-calibration-v1',parent=PARENT,grammar=GRAMMAR,grammar_blob=GRAMMAR_BLOB,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,source_sha256=digest(Path(__file__).read_bytes()),calibration_windows=8192,threshold_multipliers=k,fixtures=list(map(int,picks)),pcm_trials=len(traces)//4,decisions=len(traces),groups=groups,limits='Independent transcription; known slot alignment and mode; constructed white noise, active-only and guard-only noise; oracle knows active-window SD; guard/offbin estimate from same slot; no blind timing, real transport, human or loudness claims. Replacement is a valid alternate symbol, not random noise. Fixed uses 720/240 as Grammar morphology.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces))
    html='''<!doctype html><meta charset=utf-8><title>MHAC depth calibration</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto;padding:1em}td,th{padding:.5em;text-align:left;border-bottom:1px solid #aaa}table{border-collapse:collapse;width:100%}</style><h1>Five-band calibration and hybrid encoding</h1><p>Synthetic aligned PCM. 96 holdout trees; no human evidence.</p><label>Normalization <select id="norm"><option>peak</option><option>energy</option></select></label> <label>Condition <select id="cond">OPTIONS</select></label><table><thead><tr><th>Mode</th><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th></tr></thead><tbody id="rows"></tbody></table><h2>Matched-peak clean specimens</h2>GALLERY<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;function draw(){rows.replaceChildren(...data.filter(r=>r.norm===norm.value&&r.condition===cond.value).map(r=>{let t=document.createElement('tr');for(let v of [r.mode,r.policy,r.counts.correct||0,r.counts.wrong||0,r.counts.withheld||0]){let d=document.createElement('td');d.textContent=v;t.append(d)}return t}))}norm.onchange=cond.onchange=draw;document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>'''
    (out/'index.html').write_text(html.replace('OPTIONS',''.join(f'<option>{c}</option>' for c in CONDS)).replace('GALLERY',''.join(f'<p>{p}<br><audio controls preload="none" src="{p}"></audio></p>' for p in gallery)).replace('DATA',json.dumps(groups)))
    (out/'manifest.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('groups','fixtures')},indent=2))
if __name__=='__main__': run(Path(sys.argv[1]))
