"""Refs #448/#449. Synthetic bounded window search, disjoint evaluation seeds.
python window-holdout.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
No human or physical-device evidence. Same PCM and admission for every comparator.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='68232af33ab7b5666ab6a89d84a5e24d3532c973'
BLOBS=dict(zip(('causal-frame.py','competing-starts.py','control-namespace.py','discourse-sync.py','distributed-profile.py','frame-length-commit.py','interval-admission.py','migration-namespace.py','prefix-disjoint.py','version-bound-payload.py','version-bridge.py'),('fc5dd44fe87ebcabc2a1e0213726a3fd43cb2a60','af3f673f28e65bb4fc241a22cc603a6cbb041dfb','8e27fe89f2734a0b5fd666bb2018b0d379736493','cc6b996d6314fdcbb92edc85e12878d5d2077aa7','a780404e8c76820976ad6fb407429ec895a6313f','1538e258e53b62fc62315ca11eb9ba34496c5919','32cf07a2f23ddf6af7d1e819d9a44a3647c9f8e3','b3562781a974c47b41cbe066ceb755288a51b6b1','f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942','7ef6881cefa9c34355d024aeea671d021b674a55','6400cf4c1b42fbe958b0265da43ef657bb355401')))
WINDOW_SOURCE_BLOB='83eafc7eae1fd9ff8961bb510af22afa4eb4a0fb'
S=1280; DEV=4480400; TEST=4480401
# name: onset ms, duration ms. early20 independently transcribes pinned window-admission.py's early20.
WINDOWS={'early20':(10,20),'w05-10':(5,10),'w10-10':(10,10),'w05-15':(5,15),'w05-20':(5,20),'w05-25':(5,25)}
# phase relative to half-slot stagger (ms), B/A gain, noise SD (PCM counts), B-only inter-symbol clock error (ppm).
DISCOVERY=[(-20,1,0,0),(20,1,0,0),(-10,.75,120,0),(10,1.35,120,0),(0,1,120,0),(30,1,0,0)]
HOLDOUT=[(-20,1,0,0),(20,1,0,0),(-15,.65,150,0),(15,1.5,150,0),(0,1,200,0),(30,1,0,0),(-30,1,0,0),(0,1,0,5000),(0,1,0,-5000),(10,.8,100,10000)]
def sha(b): return hashlib.sha256(b).hexdigest()
def window(start,duration):
    a,n=start*16,duration*16; basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(n)/16000)
    def observe(slot):
        scores=abs(basis@slot[a:a+n])*2/n; k=int(scores.argmax())
        return (18 if k==17 else k) if scores[k]>=200 else None
    return observe
def run(root,out):
    for f,h in BLOBS.items():
        b=(root/f).read_bytes(); assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==h,f
    def load(f): return runpy.run_path(str(root/f))
    v=load('interval-admission.py'); s=load('discourse-sync.py'); c=load('causal-frame.py'); m=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs={'original':c['observe'],**{k:window(*z) for k,z in WINDOWS.items()}}
    out.mkdir(parents=True,exist_ok=False); rows=[]; specimens=[]; stats={}; identities={}; checks=0
    def batch(label,seed,pairs,conditions,modes):
        nonlocal checks
        rng=np.random.default_rng(seed); identities[label]=[]
        for j in range(pairs):
            a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); want=[[a,18,i],[b,13,k]]; identities[label].extend(want)
            x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
            for ci,(phase,gain,noise,ppm) in enumerate(conditions):
                aa=np.zeros(32*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); offset=lead+int(2.5*S)+phase*16
                for q,tok in enumerate(y): v['put'](bb,[tok],offset+round(q*S*(1+ppm/1e6)))
                noise_seed=seed*10000+j*100+ci; mix=aa+gain*bb+np.random.default_rng(noise_seed).normal(0,noise,len(aa)); assert abs(mix).max()<5000
                pcm=np.rint(mix).astype('<i2'); digest=sha(pcm.tobytes()); key=f'{label}:{ci}'
                for mode in modes:
                    ev=v['acquire'](pcm,books,obs[mode],joint,'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values()); wrong=len(got)-correct
                    if label=='holdout' and j==0:
                        for t in sorted({e['sample'] for e in ev if e['kind']=='release'}):
                            assert v['acquire'](pcm[:t],books,obs[mode],joint,'multiplex')==[e for e in ev if e['sample']<=t]; checks+=1
                    row=dict(split=label,pair=j,condition=ci,phase_ms=phase,gain=gain,noise_sd=noise,clock_ppm=ppm,noise_seed=noise_seed,mode=mode,expected=want,decoded=got,correct=correct,wrong=wrong,missing=2-correct,pcm_sha256=digest,rms=float(np.sqrt(np.mean(pcm.astype(float)**2))),events=ev); rows.append(row)
                    stats.setdefault(key,{}).setdefault(mode,Counter()).update(correct=correct,wrong=wrong,missing=2-correct,starts=sum(e['kind']=='start' for e in ev))
                if label=='holdout' and j==0:
                    name=f'case-{ci:02d}.wav'
                    with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                    specimens.append(dict(file=name,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    batch('discovery',DEV,3,DISCOVERY,tuple(obs))
    scores={mode:dict(correct=sum(r['correct'] for r in rows if r['mode']==mode),wrong=sum(r['wrong'] for r in rows if r['mode']==mode)) for mode in obs}
    # Predeclared lexicographic rule: minimize wrong, then maximize correct, then prefer early20, then insertion order.
    chosen=min(WINDOWS,key=lambda k:(scores[k]['wrong'],-scores[k]['correct'],list(WINDOWS).index(k)))
    (out/'selection.json').write_text(json.dumps(dict(seed=DEV,rule='min wrong, max correct, insertion order',scores=scores,chosen=chosen),indent=2)+'\n')
    batch('holdout',TEST,8,HOLDOUT,tuple(dict.fromkeys(('original','early20',chosen))))
    assert not set(map(tuple,identities['discovery']))&set(map(tuple,identities['holdout']))
    for key in {(r['split'],r['pair'],r['condition']) for r in rows}:
        assert len({r['pcm_sha256'] for r in rows if (r['split'],r['pair'],r['condition'])==key})==1
    assert all(r['correct']+r['wrong']==len(r['decoded']) and r['correct']+r['missing']==2 for r in rows)
    receipt=dict(schema='mhac-window-holdout-v1',pin=PIN,blobs=BLOBS,reference_window_blob=WINDOW_SOURCE_BLOB,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,seeds=[DEV,TEST],windows=WINDOWS,discovery=DISCOVERY,holdout=HOLDOUT,chosen=chosen,scores=scores,physical_pcm=18+80,evaluations=len(rows),prefix_checks=checks,stats=stats,specimens=specimens,limits='Synthetic finite discovery and disjoint holdout message identities. Clock error shifts symbol onsets without pitch resampling; fixed receiver clock. Matched PCM within groups, not energy-normalized across conditions. No authentication, streaming resource, human or physical evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset="utf-8"><title>Window holdout</title><h1>Window holdout</h1><p>Original synthetic PCM, opt-in audio; begin at low volume. Clock error changes onset timing, not pitch. Chosen on discovery only: '+chosen+'</p>'
    for g in specimens:
        ci=g['condition']; html+=f'<h2>Case {ci}: {HOLDOUT[ci]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[f'holdout:{ci}'],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="selection.json">Selection</a> | <a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
