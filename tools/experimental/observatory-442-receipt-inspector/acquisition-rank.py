"""Measurement #442/#443: bounded pilot acquisition and finite-domain rank.
python acquisition-rank.py selective-transport.py OUTPUT
Synthetic known-length capture, known frame ID; no authentication or human evidence.
"""
import hashlib, itertools, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

REF='8656394a04100f9dd6d835397cd2831f58356b36'
PIN='2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf'
ADVERSARY='b1430d799ea2858f0b548705b4e2d3289e98711e'
SEED=4426701
PILOT=[0,15,5]; RATE=16000; SLOT=320; PAD=320
DELAYS=np.arange(-160,161,16); SHIFTS=np.arange(-80,81,10)
T=np.arange(160)/RATE; F=1000+100*np.arange(16)
PB=np.exp(-2j*np.pi*(1000+100*np.array(PILOT)[None,:,None]+SHIFTS[:,None,None])*T)
MEANINGS=[list(x) for x in itertools.product(range(4),[0],range(3),range(3),range(3))]

def sha(b): return hashlib.sha256(b).hexdigest()
def rank(m): return MEANINGS.index(list(m))
def acquire(y):
    idx=PAD+DELAYS[:,None,None]+SLOT*np.arange(3)[None,:,None]+16+np.arange(160)
    m=abs(np.einsum('dpt,fpt->dfp',y[idx].astype(float),PB))*2/160
    score=np.mean(m*m,axis=2); i,j=np.unravel_index(score.argmax(),score.shape)
    return int(DELAYS[i]),int(SHIFTS[j]),float(m[i,j].min())
def decode(y,n,delay,shift):
    idx=PAD+delay+SLOT*(3+np.arange(n))[:,None]+16+np.arange(160)
    bank=np.exp(-2j*np.pi*(F[:,None]+shift)*T)
    m=abs(y[idx].astype(float)@bank.T)*2/160
    order=np.argsort(m,axis=1); top=order[:,-1]; a=m[np.arange(n),top]; b=m[np.arange(n),order[:,-2]]
    return [int(v) if x>=350 and x-z>=200 else None for v,x,z in zip(top,a,b)]

def run(source,out):
    assert sha(source.read_bytes())==PIN
    p=runpy.run_path(str(source)); rng=np.random.default_rng(SEED); rows=[]; samples={}; groups={}
    collisions=[]
    for frame in range(54):
        buckets={}
        for m in MEANINGS: buckets.setdefault(tuple(p['fingerprint'](frame,m)),[]).append(m)
        for tag,ms in buckets.items():
            for a,b in itertools.combinations(ms,2): collisions.append(dict(frame=frame,tag=list(tag),a=a,b=b,rank_a=rank(a),rank_b=rank(b)))
    assert len({rank(m) for m in MEANINGS})==108 and len(collisions)==4
    for frame in range(54):
        m=MEANINGS[int(rng.integers(108))]; z=rng.normal(size=(11,SLOT))
        for mode in ('hash16','rank7'):
            data=[frame,*p['fingerprint'](frame,m)] if mode=='hash16' else [frame,rank(m)]
            sent=p['packet'](data); n=len(sent)
            for shift,delay,absent in [*itertools.product((0,27,50,75),(-160,-80,-32,0,32,80,160),(False,)),(0,0,True)]:
                _,pcm,_=p['channel']([None]*(n+3) if absent else PILOT+sent,z,shift,1000,0)
                y=np.zeros(pcm.size+2*PAD,dtype='<i2'); y[PAD+delay:PAD+delay+pcm.size]=pcm.ravel()
                d,f,a=acquire(y)
                for policy,dd,ff in [('fixed',0,0),('pilot',d,f),('oracle',delay,shift)]:
                    v=decode(y,n,dd,ff) if policy!='pilot' or a>=600 else [None]*n
                    q=p['unpack'](v); valid=q is not None and q[0]==frame and (mode!='rank7' or q[1]<108)
                    status='withheld' if not valid else 'correct' if not absent and q==data else 'wrong'
                    row=dict(frame=frame,mode=mode,policy=policy,shift=shift,delay=delay,absent=absent,estimated_delay=dd,estimated_shift=ff,pilot_min_pcm=a,sent=None if absent else data,observed=v,decoded=q,status=status,pcm_sha256=sha(y.tobytes()))
                    rows.append(row); groups.setdefault((mode,policy,shift,delay,absent),Counter())[status]+=1
                if frame==0 and mode=='rank7' and shift==75 and delay==80 and not absent: samples['rank-shift75-delay5']=y
                if frame==0 and mode=='hash16' and shift==75 and delay==80 and not absent: samples['hash-shift75-delay5']=y
    out.mkdir(); summary=[dict(mode=m,policy=p,shift=f,delay=d,absent=a,**{k:c[k] for k in ('correct','wrong','withheld')}) for (m,p,f,d,a),c in sorted(groups.items())]
    receipt=dict(ref=REF,adversarial_ref=ADVERSARY,source_sha256=PIN,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,pilot=PILOT,pilot_threshold_pcm=600,delay_grid=DELAYS.tolist(),shift_grid=SHIFTS.tolist(),header_ms={'hash16':220,'rank7':180},summary=summary,collisions=collisions,limits='Known capture length and expected frame ID; zero padding, fixed integer arrival offset, matched prefix noise, no clock drift. Pilot search is bounded, not continuous-stream acquisition. Rank injective only for fixed 108 meanings; unkeyed CRC is not authentication. Same peak, not energy or duration. No body or feedback transport tested.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    for name,y in samples.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w:
            w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Pilot and rank laboratory</title><h1>Pilot and rank laboratory</h1><p>Synthetic headers only; known frame ID and capture length. Arrival in samples at 16 kHz.</p><label>Offset <select id="s"></select></label><pre id="r"></pre>'+''.join(f'<p>{n}<br><audio controls preload="none" src="{n}.wav"></audio></p>' for n in samples)+'<p><a href="receipt.json">Receipt and collisions</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';const s=document.getElementById("s"),r=document.getElementById("r");for(const f of [0,27,50,75])s.add(new Option(f+" Hz",f));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.shift==s.value),null,2)}s.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html)
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n')
    verify(out,p)

def verify(out,p):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; rec=json.loads((out/'receipt.json').read_text()); assert len(rows)==9396
    counts={}; hashes={}
    for r in rows:
        q=p['unpack'](r['observed']); assert q==r['decoded']; valid=q is not None and q[0]==r['frame'] and (r['mode']!='rank7' or q[1]<108)
        status='withheld' if not valid else 'correct' if not r['absent'] and q==r['sent'] else 'wrong'; assert status==r['status']
        k=tuple(r[x] for x in ('mode','policy','shift','delay','absent')); counts.setdefault(k,Counter())[status]+=1
        key=(r['frame'],r['mode'],r['shift'],r['delay'],r['absent']); hashes.setdefault(key,set()).add(r['pcm_sha256'])
    assert len(hashes)==3132 and all(len(h)==1 for h in hashes.values())
    for g in rec['summary']:
        c=counts[tuple(g[x] for x in ('mode','policy','shift','delay','absent'))]; assert sum(c.values())==54 and all(c[k]==g[k] for k in ('correct','wrong','withheld'))
    for name,digest in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/name).read_bytes())==digest
    print('verified',len(rows),'decisions,',len(hashes),'matched captures,',len(counts),'groups')

if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]))
