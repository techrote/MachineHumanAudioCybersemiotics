"""Refs #448/#449. Frozen window falsification: onset-only vs full waveform clock error.
python clock-stress.py PINNED_PACKAGE NEW_OUTPUT_DIR
Synthetic computational receivers only; no human evidence. AI-assisted.
"""
import hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PARENT='e2cbc57d92a6af386b8745a3891b3cc7d818ef70'
PARENT_BLOB='5bb0110f12858ca96009bb5dcbb70bc6689b7c26'
SEED=4480410
S=1280
# phase relative to half slot in ms, gain B/A, Gaussian noise SD, ppm, warp type
CASES=[(0,1,0,0,'full'),(35,1,0,0,'full'),(40,1,0,0,'full'),(0,.35,0,0,'full'),(0,.55,200,0,'full'),(0,1,0,10000,'onset'),(0,1,0,10000,'full'),(0,1,0,-10000,'onset'),(0,1,0,-10000,'full'),(0,1,0,30000,'onset'),(0,1,0,30000,'full'),(25,.65,150,-20000,'full')]
MODES=('original','early20','w05-25')
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def run(root,out):
    assert blob(root/'window-holdout.py')==PARENT_BLOB
    h=runpy.run_path(str(root/'window-holdout.py'))
    for f,b in h['BLOBS'].items(): assert blob(root/f)==b,f
    def load(f): return runpy.run_path(str(root/f))
    v=load('interval-admission.py'); s=load('discourse-sync.py'); c=load('causal-frame.py'); m=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs={'original':c['observe'],**{k:h['window'](*h['WINDOWS'][k]) for k in MODES[1:]}}
    rng=np.random.default_rng(SEED); rows=[]; stats={}; specimens=[]; checks=0
    out.mkdir(parents=True,exist_ok=False)
    for j in range(6):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80))
        want=[[a,18,i],[b,13,k]]; x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
        for ci,(phase,gain,noise,ppm,warp) in enumerate(CASES):
            aa=np.zeros(36*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); offset=lead+int(2.5*S)+phase*16; ratio=1+ppm/1e6
            if warp=='onset':
                for q,tok in enumerate(y): v['put'](bb,[tok],offset+round(q*S*ratio))
            else:
                clean=np.zeros(len(y)*S,np.int32); v['put'](clean,y,0); t=np.arange(round(len(clean)*ratio))/ratio
                bb[offset:offset+len(t)]=np.rint(np.interp(t,np.arange(len(clean)),clean,right=0)).astype(np.int32)
            noise_seed=SEED*10000+j*100+ci; mix=aa+gain*bb+np.random.default_rng(noise_seed).normal(0,noise,len(aa)); assert abs(mix).max()<5000
            pcm=np.rint(mix).astype('<i2'); digest=sha(pcm.tobytes()); starts=[lead+2*S,offset+round(2*S*ratio)]
            for mode in MODES:
                ev=v['acquire'](pcm,books,obs[mode],joint,'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,want))&Counter(map(tuple,got))).values()); wrong=len(got)-correct
                # Source and estimated body start must match within 40 ms; one intended frame per source.
                admitted=[any(e['kind']=='start' and e['source']==z[0] and abs(e['body_start']-t)<=S//2 for e in ev) for z,t in zip(want,starts)]
                missing_no_start=sum(z not in got and not ok for z,ok in zip(want,admitted)); missing_after_start=2-correct-missing_no_start
                if j==0:
                    for t in sorted({e['sample'] for e in ev if e['kind']=='release'}):
                        assert v['acquire'](pcm[:t],books,obs[mode],joint,'multiplex')==[e for e in ev if e['sample']<=t]; checks+=1
                row=dict(pair=j,condition=ci,mode=mode,expected=want,body_starts=starts,matched_start=admitted,decoded=got,correct=correct,wrong=wrong,missing_no_start=missing_no_start,missing_after_start=missing_after_start,noise_seed=noise_seed,pcm_sha256=digest,events=ev); rows.append(row)
                stats.setdefault(str(ci),{}).setdefault(mode,Counter()).update(correct=correct,wrong=wrong,missing_no_start=missing_no_start,missing_after_start=missing_after_start,matched_starts=sum(admitted))
            if j==0:
                name=f'case-{ci:02d}.wav'
                with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    assert len(rows)==6*len(CASES)*len(MODES)
    for j in range(6):
        for ci in range(len(CASES)):
            group=[r for r in rows if r['pair']==j and r['condition']==ci]; assert len({r['pcm_sha256'] for r in group})==1 and len({tuple(r['matched_start']) for r in group})==1
    assert all(r['correct']+r['missing_no_start']+r['missing_after_start']==2 and r['correct']+r['wrong']==len(r['decoded']) for r in rows)
    receipt=dict(schema='mhac-clock-stress-v1',parent=PARENT,parent_blob=PARENT_BLOB,grammar_pin=h['PIN'],blobs=h['BLOBS'],seed=SEED,numpy=np.__version__,source_sha256=sha(pathlib.Path(__file__).read_bytes()),conditions=CASES,modes=MODES,physical_pcm=6*len(CASES),evaluations=len(rows),prefix_checks=checks,stats=stats,specimens=specimens,limits='Fixed exploratory grid; full warp uses linear interpolation of B waveform, stretches duration and shifts pitch; not calibrated hardware resampling. Onset comparator shifts only symbol times. Matched PCM within condition, not matched energy across conditions. Start match tolerance 40 ms; after-start loss includes terminal, body and admission failures, not necessarily extraction. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset="utf-8"><title>Clock stress</title><h1>Clock stress</h1><p>Synthetic PCM. Begin at low volume. Full warp shifts pitch and timing; onset only shifts symbol times. No autoplay.</p>'
    for g in specimens:
        ci=g['condition']; html+=f'<h2>Case {ci}: {CASES[ci]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[str(ci)],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
