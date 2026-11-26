"""Refs #452 / Draft #453. Matched-PCM window comparison, synthetic only.
python window-admission.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
No human evidence or source authentication. Fixed slot clock, no device control.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='f215e18d8cbcbaa7c19fd5f199cd69bb510c1c22'
BLOB='32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3'
SEEDS=(452380,452381); PHASES=(-30,-20,-10,-5,0,5,10,20,30)
POLICIES=('original','early20','split20')
S=1280

def observe_factory(mode):
    basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(320)/16000)
    def measure(w):
        scores=abs(basis@w)*2/320; k=int(scores.argmax()); top=float(scores[k]); second=float(np.partition(scores,-2)[-2]); return (18 if k==17 else k),top,(top-second)/max(top,1)
    def observe(slot):
        a=measure(slot[160:480])
        if mode=='early20': return a[0] if a[1]>=200 else None
        b=measure(slot[480:800]); best=max((a,b),key=lambda v:v[2] if v[1]>=200 else -1)
        return best[0] if best[1]>=200 and best[2]>=.35 else None
    return observe

def run(root,out):
    m=runpy.run_path(str(root/'interval-admission.py')); assert m['blob'](root/'interval-admission.py')==BLOB
    p=runpy.run_path(str(root/'competing-starts.py')); s=runpy.run_path(str(root/'discourse-sync.py'))
    pins={**s['BLOBS'],'discourse-sync.py':p['SYNC_BLOB'],'competing-starts.py':m['PARENT'],'interval-admission.py':BLOB}
    for f,b in pins.items(): assert m['blob'](root/f)==b,f
    c=runpy.run_path(str(root/'causal-frame.py')); v=runpy.run_path(str(root/'version-bound-payload.py')); joint=runpy.run_path(str(root/'prefix-disjoint.py'))['joint']
    _,raw,names=v['build'](root); old,new=raw; long=np.concatenate([v['extend'](w,k,'polynomial') for k,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs={'original':c['observe'],**{k:observe_factory(k) for k in POLICIES[1:]}}; out.mkdir(parents=True,exist_ok=False); rows=[]; specimens=[]; stats={}; checks=0
    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        for j in range(4):
            a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); want=[[a,18,i],[b,13,k]]
            x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
            for phase in PHASES:
                pcm=np.zeros(55*S,dtype=np.int32); m['put'](pcm,x,lead); m['put'](pcm,y,lead+int(2.5*S)+16*phase); assert np.max(abs(pcm))<=3000; pcm=pcm.astype('<i2'); digest=m['sha'](pcm.tobytes())
                for mode in POLICIES:
                    ev=m['acquire'](pcm,books,obs[mode],joint,'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values()); wrong=len(got)-correct
                    for e in ev:
                        if e['kind']=='release':
                            assert m['acquire'](pcm[:e['sample']],books,obs[mode],joint,'multiplex')==[z for z in ev if z['sample']<=e['sample']]; checks+=1
                    row=dict(seed=seed,pair=j,phase_ms=phase,mode=mode,expected=want,decoded=got,correct=correct,wrong=wrong,missing=2-correct,pcm_sha256=digest,events=ev); rows.append(row)
                    stats.setdefault(f'{seed}:{phase}:{mode}',Counter()).update(correct=correct,wrong=wrong,missing=2-correct,starts=sum(e['kind']=='start' for e in ev))
                if seed==SEEDS[1] and j==0:
                    f=f'phase-{phase:+d}.wav'
                    with wave.open(str(out/f),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                    specimens.append(dict(file=f,phase_ms=phase,pcm_sha256=digest,peak=int(np.max(abs(pcm)))))
    assert len(rows)==len(SEEDS)*4*len(PHASES)*len(POLICIES)
    assert all(len({r['pcm_sha256'] for r in rows if (r['seed'],r['pair'],r['phase_ms'])==(seed,j,phase)})==1 for seed in SEEDS for j in range(4) for phase in PHASES)
    receipt=dict(schema='mhac-window-admission-v1',pin=PIN,blobs=pins,source_sha256=m['sha'](pathlib.Path(__file__).read_bytes()),seeds=SEEDS,phases_ms=PHASES,observations=len(rows),prefix_checks=checks,stats=stats,specimens=specimens,limits='Both seeds exploratory; no tuning/evaluation separation claimed. Fixed amplitude and clock, half-slot +/- phase. Same detector and decoder. Split20 selects strongest relative spectral margin, threshold .35; no authentication, real-time or human evidence. Original and split use equal correlation sample counts, not measured equal runtime.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    gallery=''.join(f'<h2>{z["file"]}</h2><audio controls preload="none" src="{z["file"]}"></audio><pre>'+json.dumps([{k:r[k] for k in ('mode','expected','decoded','correct','wrong')} for r in rows if r['seed']==SEEDS[1] and r['pair']==0 and r['phase_ms']==z['phase_ms']],indent=2)+'</pre>' for z in specimens)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Window admission</title><h1>Matched PCM window comparison</h1><p>Synthetic only. Begin at low volume. No autoplay.</p>'+gallery+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:m['sha'](p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
