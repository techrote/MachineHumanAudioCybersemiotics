"""Refs #448/#449. Fixed acquisition ablation; synthetic PCM only.
python acquisition-factorial.py PINNED_PACKAGE NEW_OUTPUT_DIR
AI-assisted; no participant or physical-device evidence.
"""
import hashlib, inspect, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PIN='68232af33ab7b5666ab6a89d84a5e24d3532c973'
PARENT='68e0be789e9704b4e9323d07b45d0068f5eeca49'
SEED=4480420
S=1280
MODES={'fixed4':((0,),4),'bank4':((-3,-2,-1,0,1,2,3),4),'fixed3':((0,),3),'bank3':((-3,-2,-1,0,1,2,3),3)}
# kind, B waveform stretch ppm, B/A gain, noise SD PCM counts, phase ms
CASES=[('dual',0,1,0,0),('dual',10000,1,0,0),('dual',-10000,1,0,0),('dual',25000,1,0,0),('dual',-25000,1,0,0),('dual',15000,.55,150,10),('dual',0,.35,100,0),('dual',0,1,0,40),('single',18000,1,100,0),('single',-18000,1,100,0),('noise',0,1,300,0),('near-preamble',20000,1,0,0),('repeated-tone',0,1,0,0),('short-preamble',0,1,0,0)]
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def variant(f,offsets,persistence):
    # Preserve the complete pinned receiver except the two declared detector factors.
    source=inspect.getsource(f); a='np.array([2400,2600])[:,None]'; b='scores=abs(basis@win)*2/320'; c='count==4'
    assert all(source.count(x)==1 for x in (a,b,c))
    source=source.replace(a,'(np.array([2400,2600])[:,None]*(1+np.array(OFFSETS)[None,:]/100)).reshape(-1,1)').replace(b,'scores=(abs(basis@win)*2/320).reshape(2,-1).max(axis=1)').replace(c,f'count=={persistence}')
    env={'np':np,'S':S,'OFFSETS':offsets}; exec(source,env); return env['acquire']
def run(root,out):
    assert blob(root/'window-holdout.py')=='5bb0110f12858ca96009bb5dcbb70bc6689b7c26'
    h=runpy.run_path(str(root/'window-holdout.py')); assert h['PIN']==PIN
    for f,b in h['BLOBS'].items(): assert blob(root/f)==b,f
    def load(f): return runpy.run_path(str(root/f))
    v=load('interval-admission.py'); s=load('discourse-sync.py'); m=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs=h['window'](5,25); receivers={k:variant(v['acquire'],*z) for k,z in MODES.items()}
    rng=np.random.default_rng(SEED); rows=[]; stats={}; specimens=[]; checks=0; equivalence=0
    out.mkdir(parents=True,exist_ok=False)
    for j in range(6):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80))
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
        for ci,(kind,ppm,gain,noise,phase) in enumerate(CASES):
            aa=np.zeros(36*S,np.int32); bb=aa.copy(); offset=lead+int(2.5*S)+phase*16; ratio=1+ppm/1e6; expected=[]; starts=[]
            if kind=='dual':
                v['put'](aa,x,lead); expected.append([a,18,i]); starts.append(lead+2*S)
            if kind in ('dual','single','near-preamble','repeated-tone','short-preamble'):
                word=y if kind in ('dual','single') else s['preamble'](b) if kind in ('near-preamble','short-preamble') else [20,20]
                clean=np.zeros(len(word)*S,np.int32); v['put'](clean,word,0)
                if kind=='short-preamble':
                    for q in range(len(word)): clean[q*S+240:(q+1)*S]=0
                t=np.arange(round(len(clean)*ratio))/ratio; bb[offset:offset+len(t)]=np.rint(np.interp(t,np.arange(len(clean)),clean,right=0)).astype(np.int32)
                if kind in ('dual','single'): expected.append([b,13,k]); starts.append(offset+round(2*S*ratio))
            noise_seed=SEED*10000+j*100+ci; mix=aa+gain*bb+np.random.default_rng(noise_seed).normal(0,noise,len(aa)); assert abs(mix).max()<5000
            pcm=np.rint(mix).astype('<i2'); digest=sha(pcm.tobytes())
            for mode,receive in receivers.items():
                ev=receive(pcm,books,obs,joint,'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,expected))&Counter(map(tuple,got))).values())
                if mode=='fixed4': assert ev==v['acquire'](pcm,books,obs,joint,'multiplex'); equivalence+=1
                detected=[e for e in ev if e['kind']=='start']; used=set(); errors=[]
                for z,t in zip(expected,starts):
                    choices=[(abs(e['body_start']-t),q) for q,e in enumerate(detected) if q not in used and e['source']==z[0] and abs(e['body_start']-t)<=S//2]
                    if choices:
                        _,q=min(choices); used.add(q); errors.append(detected[q]['body_start']-t)
                if j==0:
                    for t in sorted({e['sample'] for e in ev if e['kind'] in ('start','release')}):
                        assert receive(pcm[:t],books,obs,joint,'multiplex')==[e for e in ev if e['sample']<=t]; checks+=1
                # A near-preamble is an intentional framing mimic, not a valid message.
                row=dict(pair=j,condition=ci,mode=mode,expected=expected,body_starts=starts,decoded=got,correct=correct,wrong=len(got)-correct,matched=len(used),unmatched=len(detected)-len(used),start_errors_samples=errors,noise_seed=noise_seed,pcm_sha256=digest,events=ev); rows.append(row)
                stats.setdefault(str(ci),{}).setdefault(mode,Counter()).update(expected=len(expected),correct=correct,wrong=row['wrong'],matched=row['matched'],unmatched=row['unmatched'])
            if j==0:
                name=f'case-{ci:02d}.wav'
                with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    assert len(rows)==6*len(CASES)*len(MODES)
    for j in range(6):
        for ci in range(len(CASES)):
            group=[r for r in rows if r['pair']==j and r['condition']==ci]; assert len({r['pcm_sha256'] for r in group})==1
    assert all(r['matched']<=len(r['expected']) and r['correct']+r['wrong']==len(r['decoded']) for r in rows)
    receipt=dict(schema='mhac-acquisition-factorial-v1',parent=PARENT,grammar_pin=PIN,blobs=h['BLOBS'],seed=SEED,numpy=np.__version__,source_sha256=sha(pathlib.Path(__file__).read_bytes()),conditions=CASES,modes=MODES,physical_pcm=6*len(CASES),evaluations=len(rows),baseline_equivalence=equivalence,prefix_checks=checks,stats=stats,specimens=specimens,limits='Fixed exploratory factorial, no parameter search or population inference. Bank uses seven frequencies per label (14 total vs 2); no measured CPU parity. Full waveform linear interpolation, fixed body clock and 25ms extractor. Start matching by source and within 40ms; unmatched start includes intentional framing mimic, not necessarily detector error. No authentication or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset="utf-8"><title>Acquisition factorial</title><h1>Acquisition factorial</h1><p>Original synthetic PCM; begin at low volume. No autoplay. Near-preamble controls deliberately imitate framing without a message.</p>'
    for g in specimens:
        ci=g['condition']; html+=f'<h2>Case {ci}: {CASES[ci]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[str(ci)],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
