"""Refs #442 / #443. Synthetic aligned PCM measurement; no human evidence.
Independent transcription of polyphonic-depth.py at 93fcfcb9ae78e0a4686baff9bffe25e44f117c9a
(blob 2715c38cf4d7dd2727d161a8020a46078d72b690). Run: python depth-level-audit.py OUTPUT
"""
import hashlib, itertools, json, sys, wave
from pathlib import Path
from collections import Counter
import numpy as np

PIN = '93fcfcb9ae78e0a4686baff9bffe25e44f117c9a'
BLOB = '2715c38cf4d7dd2727d161a8020a46078d72b690'
SEED = 4425401
RATE, SLOT, ACTIVE, AMP = 16000, 1280, 960, 1600
V = ('fault','open','stopped','overload','not','quote','question','verify','pump-reports','relay-reports','uncertain','and','if')
A = (0,)*4+(1,)*7+(2,)*2
F = (np.arange(13)*100+400,np.arange(4)*100+2100)
T = np.arange(ACTIVE)/RATE
W = np.minimum(1,np.minimum(np.arange(ACTIVE),np.arange(ACTIVE)[::-1])/80)
B = [np.exp(-2j*np.pi*f[:,None]*np.arange(160,800)/RATE) for f in F]

def catalog():
    levels=[[],[(k,) for k in range(4)]]
    for n in range(2,5):
        levels.append([(k,c) for k in range(4,11) for c in levels[n-1]]+[(k,x,y) for i in range(1,n-1) for k in (11,12) for x in levels[i] for y in levels[n-1-i]])
    return sum(levels,[])

def encode(tree,d=0): return [(tree[0],d)]+[r for c in tree[1:] for r in encode(c,d+1)]
def decode(rows):
    i=0
    def read(d):
        nonlocal i
        if i>=len(rows): raise ValueError()
        k,h=rows[i]; i+=1
        if k is None or d!=h: raise ValueError()
        return (k,)+tuple(read(d+1) for _ in range(A[k]))
    try:
        t=read(0); return t if i==len(rows) else None
    except ValueError: return None

def render(rows,mode,phase,depth_gain=1):
    frames=[]
    for k,d in rows:
        a,b=np.zeros(SLOT),np.zeros(SLOT)
        a[:ACTIVE]=AMP*W*np.sin(2*np.pi*F[0][k]*T+phase)
        b[:ACTIVE]=depth_gain*AMP*W*np.sin(2*np.pi*F[1][d]*T+phase)
        frames.extend([a,b] if mode=='serial' else [a+b])
    return np.concatenate(frames)

def receive(pcm,mode):
    x=pcm.reshape(-1,SLOT)[:,160:800].astype(float)
    def band(b):
        s=np.abs(x@B[b].T)*2/640; order=np.argsort(s,axis=1)
        return [int(o[-1]) if v[o[-1]]>=AMP*.45 and v[o[-1]]-v[o[-2]]>=AMP*.25 else None for v,o in zip(s,order)]
    a,b=band(0),band(1)
    return list(zip(a[::2],b[1::2])) if mode=='serial' else list(zip(a,b))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pcm(x): return np.clip(np.rint(x),-32768,32767).astype('<i2')
def run(out):
    out.mkdir(parents=True,exist_ok=False)
    trees=catalog(); assert len(trees)==len(set(trees))==2304
    # Disjoint from the upstream 96-tree sample, whose exact selection is transcribed.
    upstream=set(np.random.default_rng(452510).choice(len(trees),96,replace=False).tolist())
    rng=np.random.default_rng(SEED); picks=rng.choice(sorted(set(range(len(trees)))-upstream),192,replace=False)
    traces=[]; gallery=[]
    for i,idx in enumerate(picks):
        tree=trees[int(idx)]; rows=encode(tree); phase=float(rng.uniform(0,2*np.pi))
        ref=render(rows,'serial',phase); target_energy=float(ref@ref); target_peak=float(np.max(np.abs(ref)))
        # Common per-node/per-band noise draws; poly uses lexical-slot noise only, not a sum.
        z=np.random.default_rng(SEED+i).normal(size=(len(rows),2,SLOT))
        for norm,depth,gain,sd in itertools.product(('energy','peak'),(1.,.5), (1.,.6), (0,1000,3500)):
            for mode in ('serial','poly'):
                x=render(rows,mode,phase,depth)
                scale=(target_energy/float(x@x))**.5 if norm=='energy' else target_peak/float(np.max(np.abs(x)))
                clean=pcm(x*scale*gain); noise=z.reshape(-1) if mode=='serial' else z[:,0,:].reshape(-1)
                y=pcm(clean.astype(float)+sd*noise); observed=receive(y,mode); got=decode(observed)
                status='withheld' if got is None else 'correct' if got==tree else 'wrong'
                traces.append(dict(tree=int(idx),nodes=len(rows),phase=phase,norm=norm,depth=depth,gain=gain,sd=sd,mode=mode,status=status,observed=observed,expected=rows,samples=len(y),energy=int(np.sum(clean.astype(np.int64)**2)),peak=int(np.max(np.abs(clean.astype(int)))),pcm_sha256=hashlib.sha256(y.tobytes()).hexdigest()))
                if i==0 and sd==0 and gain==1 and depth==1:
                    p=out/f'{norm}-{mode}.wav'
                    with wave.open(str(p),'wb') as w: w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(clean.tobytes())
                    gallery.append(dict(file=p.name,sha256=sha(p)))
    assert len(traces)==9216 and len(set(picks))==192 and not upstream.intersection(picks)
    groups=[]
    for norm,depth,gain,sd in itertools.product(('energy','peak'),(1.,.5),(1.,.6),(0,1000,3500)):
        pair={m:[r for r in traces if (r['norm'],r['depth'],r['gain'],r['sd'],r['mode'])==(norm,depth,gain,sd,m)] for m in ('serial','poly')}
        assert all(len(v)==192 for v in pair.values())
        s,p=pair['serial'],pair['poly']; assert [r['tree'] for r in s]==[r['tree'] for r in p]
        groups.append(dict(norm=norm,depth=depth,gain=gain,sd=sd,serial=dict(Counter(r['status'] for r in s)),poly=dict(Counter(r['status'] for r in p)),poly_only=sum(a['status']!='correct' and b['status']=='correct' for a,b in zip(s,p)),serial_only=sum(a['status']=='correct' and b['status']!='correct' for a,b in zip(s,p)),energy_ratio=sum(r['energy'] for r in p)/sum(r['energy'] for r in s),peak_ratio=sum(r['peak'] for r in p)/sum(r['peak'] for r in s)))
    assert all(r['status']=='correct' for r in traces if r['norm']=='energy' and r['depth']==r['gain']==1 and r['sd']==0)
    receipt=dict(schema='mhac-depth-level-audit-v1',source_ref=PIN,source_blob=BLOB,source_sha256=sha(Path(__file__)),seed=SEED,python=sys.version.split()[0],numpy=np.__version__,trials=len(traces),holdout=len(picks),groups=groups,gallery=gallery,limits='Independent transcription, not upstream execution. Aligned timing; fixed thresholds; common lexical-slot Gaussian draws, serial depth noise independent. Energy is summed squared digital PCM before noise, not loudness. Peak is pre-noise absolute digital count. No physical or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces))
    html='''<!doctype html><meta charset=utf-8><title>MHAC depth level audit</title><style>body{font:16px system-ui;max-width:950px;margin:2em auto;padding:1em}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #aaa;padding:.5em;text-align:left}</style><h1>Depth-channel level audit</h1><p>Synthetic aligned PCM; 192 held-out trees per condition. Fixed decoder thresholds. Digital energy is not loudness.</p><label>Normalization <select id="n"><option>energy</option><option>peak</option></select></label><table><thead><tr><th>Depth gain</th><th>Overall gain</th><th>Noise SD</th><th>Serial correct</th><th>Poly correct</th><th>Poly-only</th><th>Serial-only</th><th>Energy ratio</th></tr></thead><tbody id="rows"></tbody></table><h2>Matched-condition specimens</h2>GALLERY<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;function draw(){rows.replaceChildren(...data.filter(r=>r.norm===n.value).map(r=>{let t=document.createElement('tr');for(let x of [r.depth,r.gain,r.sd,r.serial.correct||0,r.poly.correct||0,r.poly_only,r.serial_only,r.energy_ratio.toFixed(3)]){let d=document.createElement('td');d.textContent=x;t.append(d)}return t}))}n.onchange=draw;document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(groups)).replace('GALLERY',''.join(f'<p>{g["file"]}<br><audio controls preload="none" src="{g["file"]}"></audio></p>' for g in gallery)))
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(Path(sys.argv[1]))
