"""Refs #442/#443. Synthetic exploratory drift and interference measurement.
Run: OPENBLAS_NUM_THREADS=1 python drift-audit.py NEW_OUTPUT
No human evidence. All policies know nominal slot boundaries and layout.
"""
import hashlib, importlib.util, itertools, json, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

PARENT='6af3e93c9d82536f7f70177dbc9fe54b3934f58e'
GRAMMAR='20986659fa9de8c9f63740a9b9d5704f432bc6b7'
BASE=Path(__file__).with_name('depth-calibration.py')
def sha(x): return hashlib.sha256(x).hexdigest()
assert sha(BASE.read_bytes())=='fb25fb572972bd5476c2f00acf3323e0a445496d589516bef92945936b917b7d'
spec=importlib.util.spec_from_file_location('cal',BASE); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c); d=c.d
SEED=4425601
GRID=np.arange(-40,41,5); T=np.arange(160,800)/d.RATE
BANK=[[np.exp(-2j*np.pi*(f[:,None]+h)*T) for f in c.F] for h in GRID]
OFF=[np.exp(-2j*np.pi*(np.arange(425,4026,100)[:,None]+h)*T) for h in GRID]
# (carrier shift Hz, delay samples, noise SD PCM counts, noise kind)
CONDS={'clean':(0,0,0,'white'),'white':(0,0,1000,'white'),'drift25':(25,0,1000,'white'),'drift35':(-35,0,1000,'white'),'delay':(25,240,1000,'white'),'colored':(25,0,1000,'colored'),'competitor':(25,0,1000,'tone'),'absent_white':(0,0,1000,'absent'),'absent_colored':(0,0,1000,'absent_colored')}
POLICIES=('nominal','estimated','oracle')

def render(rows,mode,phase,h):
    blocks=[]
    for row in rows:
        for g in c.MODES[mode]:
            x=np.zeros(d.SLOT)
            for b in g: x[:d.ACTIVE]+=d.AMP*d.W*np.sin(2*np.pi*(c.F[b][row[b]]+h)*d.T+phase)
            blocks.append(x)
    return np.array(blocks)

def measure(y,mode,truth,k):
    x=y[:,160:800].astype(float); groups=c.MODES[mode]; n=len(groups)
    def score(b,j):
        s=np.abs(x[j::n]@BANK[h][b].T)*2/640
        return s
    all_scores=[]; objectives=[]
    for h in range(len(GRID)):
        ss=[score(b,next(j for j,g in enumerate(groups) if b in g)) for b in range(5)]
        all_scores.append(ss); objectives.append(sum(float(v.max(axis=1).sum()) for v in ss))
    selected=int(np.argmax(objectives)); oracle=int(np.where(GRID==truth)[0][0]); nominal=int(np.where(GRID==0)[0][0]); result={}
    for policy,h in zip(POLICIES,(nominal,selected,oracle)):
        off=np.median(abs(x@OFF[h].T)*2/640,axis=1)*np.sqrt(640/(4*np.log(2))); cols=[]
        for b,s in enumerate(all_scores[h]):
            j=next(j for j,g in enumerate(groups) if b in g); ix=np.argsort(s,axis=1); top=ix[:,-1]; a=s[np.arange(len(s)),top]; m=a-s[np.arange(len(s)),ix[:,-2]]; t=np.maximum(80,k[b]*off[j::n]); cols.append([int(v) if ok else None for v,ok in zip(top,(a>=t)&(m>=t/3))])
        result[policy]=(list(zip(*cols)),int(GRID[h]),float(np.mean(off)))
    return result

def run(out):
    out.mkdir(parents=True,exist_ok=False); rng=np.random.default_rng(SEED)
    cal=np.random.default_rng(c.SEED+1).normal(size=(8192,640)); k=[float(np.quantile(c.scores(cal,b).max(axis=1),.999)) for b in range(5)]
    trees=d.catalog(); u=set(range(len(trees))); prev=set(np.random.default_rng(452510).choice(len(trees),96,replace=False)); audit=set(np.random.default_rng(4425401).choice(sorted(u-prev),192,replace=False)); grammar=set(np.random.default_rng(452520).choice(sorted(u-prev-audit),96,replace=False)); last=set(np.random.default_rng(c.SEED).choice(sorted(u-prev-audit-grammar),96,replace=False)); hybrid=set(np.random.default_rng(452530).choice(sorted(u-prev-audit-grammar),64,replace=False)); picks=rng.choice(sorted(u-prev-audit-grammar-last-hybrid),48,replace=False); traces=[]; gallery=[]
    for i,idx in enumerate(picks):
        rows=[(*r,*map(int,rng.integers(0,3,3))) for r in d.encode(trees[int(idx)])]; target=c.decode(rows); phase=float(rng.uniform(0,2*np.pi)); z=np.random.default_rng(SEED+100+i).normal(size=(len(rows),5,d.SLOT))
        for mode,cond in itertools.product(c.MODES,CONDS):
            shift,delay,sd,kind=CONDS[cond]; n=len(c.MODES[mode]); ref=render(rows,'serial',phase,shift); x=render(rows,mode,phase,shift); x*=np.max(abs(ref))/np.max(abs(x)); noise=z[:,:n,:].reshape(-1,d.SLOT).copy()
            if 'colored' in kind:
                noise=np.apply_along_axis(lambda a:np.convolve(a,np.ones(12)/12,'same'),1,noise); noise/=np.sqrt(np.mean(noise**2,axis=1,keepdims=True))
            if kind.startswith('absent'): x[:]=0
            if kind=='tone':
                # One valid alternative epistemic carrier in the applicable slot, at 600 PCM counts.
                j=next(j for j,g in enumerate(c.MODES[mode]) if 2 in g); b=(rows[0][2]+1)%3; x[j,:d.ACTIVE]+=600*d.W*np.sin(2*np.pi*(c.F[2][b]+shift)*d.T+phase)
            if delay: x=np.pad(x.ravel(),(delay,0))[:x.size].reshape(x.shape)
            y=d.pcm(x+sd*noise); measurements=measure(y,mode,shift,k)
            for policy,(obs,h,off) in measurements.items():
                got=c.decode(obs); status='withheld' if got is None else 'correct' if not kind.startswith('absent') and got==target else 'wrong'
                traces.append(dict(fixture=int(idx),mode=mode,condition=cond,policy=policy,expected=rows,observed=obs,status=status,shift_hz=shift,selected_hz=h,offbin_sd=round(off,3),delay_samples=delay,pcm_sha256=sha(y.tobytes())))
            if i==0 and cond in ('clean','drift25','colored') and mode in ('hybrid','poly'):
                p=out/f'{mode}-{cond}.wav'; safe=d.pcm(y.astype(float)*min(1,3000/max(1,int(np.max(abs(y.astype(int)))))))
                with wave.open(str(p),'wb') as w: w.setparams((1,2,d.RATE,0,'NONE','not compressed')); w.writeframes(safe.tobytes())
                gallery.append(p.name)
    groups=[]
    for mode,cond,policy in itertools.product(c.MODES,CONDS,POLICIES):
        r=[t for t in traces if (t['mode'],t['condition'],t['policy'])==(mode,cond,policy)]; assert len(r)==48
        groups.append(dict(mode=mode,condition=cond,policy=policy,counts=dict(Counter(t['status'] for t in r)),shift_exact=sum(t['selected_hz']==t['shift_hz'] for t in r),mean_offbin_sd=round(float(np.mean([t['offbin_sd'] for t in r])),2)))
    assert len(traces)==48*3*len(CONDS)*3
    assert all(t['status']=='correct' for t in traces if t['condition']=='clean')
    assert all(t['status']!='correct' for t in traces if t['condition'].startswith('absent'))
    receipt=dict(schema='mhac-drift-audit-v1',parent=PARENT,grammar_context=GRAMMAR,seed=SEED,source_sha256=sha(Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,conditions=CONDS,grid_hz=GRID.tolist(),fixtures=list(map(int,picks)),groups=groups,pcm_trials=len(traces)//3,decisions=len(traces),limits='Exploratory aligned known-layout synthetic PCM. Equal nominal peak before interference; common additive carrier offset, not clock scaling. Shift search maximizes summed band maxima; inherited white-noise thresholds not calibrated for search or colored noise. Oracle knows injected offset, not noise. Audition copies peak limited independently, not analysis PCM or matched loudness. No human or physical transport evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in traces))
    html='''<!doctype html><meta charset=utf-8><title>MHAC drift audit</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto;padding:1em}td,th{padding:.5em;text-align:left;border-bottom:1px solid #aaa}</style><h1>Carrier drift and interference audit</h1><p>48 synthetic trees per condition; known slot timing. No human evidence.</p><label>Condition <select id="cond">OPTIONS</select></label><table><thead><tr><th>Mode</th><th>Policy</th><th>Correct</th><th>Wrong</th><th>Withheld</th><th>Offset exact</th><th>Off-bin SD</th></tr></thead><tbody id="rows"></tbody></table><h2>Peak-limited audition copies (not matched loudness)</h2>GALLERY<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;const cond=document.getElementById('cond'),rows=document.getElementById('rows');function draw(){rows.replaceChildren(...data.filter(r=>r.condition===cond.value).map(r=>{let t=document.createElement('tr');for(let v of [r.mode,r.policy,r.counts.correct||0,r.counts.wrong||0,r.counts.withheld||0,r.shift_exact,r.mean_offbin_sd]){let d=document.createElement('td');d.textContent=v;t.append(d)}return t}))}cond.onchange=draw;document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>'''
    (out/'index.html').write_text(html.replace('OPTIONS',''.join(f'<option>{x}</option>' for x in CONDS)).replace('GALLERY',''.join(f'<p>{p}<br><audio controls preload="none" src="{p}"></audio></p>' for p in gallery)).replace('DATA',json.dumps(groups)))
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(receipt['pcm_trials'],receipt['decisions'])
if __name__=='__main__': run(Path(sys.argv[1]))
