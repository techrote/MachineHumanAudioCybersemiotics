"""Refs #448/#449; synthetic clock propagation, no human evidence.
Usage: python clock-propagation.py PINNED_PACKAGE NEW_OUTPUT_DIR
"""
import inspect, hashlib, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='97ec83f9f79902edfb0c84f3e9c10dfdfedcf8e2'
S=1280; SEED=4480430
MODES=('bank','timing','pitch','joint')
# B stretch ppm, gain, noise SD PCM counts, phase ms, extra preamble
CASES=[(0,1,0,0,False),(10000,1,0,0,False),(-10000,1,0,0,False),(25000,1,0,0,False),(-25000,1,0,0,False),(15000,.55,150,10,False),(-18000,.8,100,-10,False),(0,1,0,40,False),(0,1,0,0,True),(-25000,1,0,0,True)]
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def observe_scaled(slot,scale,timing,pitch):
    a,b=round(80*(scale if timing else 1)),round(480*(scale if timing else 1)); x=slot[a:b]; n=len(x)
    basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(n)/16000/(scale if pitch else 1))
    scores=abs(basis@x)*2/n; k=int(scores.argmax()); return (18 if k==17 else k) if scores[k]>=200 else None
def receiver(f,mode):
    src=inspect.getsource(f)
    def replace(a,b):
        nonlocal src
        assert src.count(a)==1,a
        src=src.replace(a,b)
    replace('np.array([2400,2600])[:,None]','(np.array([2400,2600])[:,None]*(1+np.arange(-3,4)[None,:]/100)).reshape(-1,1)')
    replace('scores=abs(basis@win)*2/320','bank=(abs(basis@win)*2/320).reshape(2,7); scores=bank.max(axis=1)')
    replace("h=dict(source=prior[0],start=prior[1]+2*S,seen=[],done=None); prior=None", "scale=1/(1+(prior[2]+int(bank[v].argmax())-3)/200); h=dict(source=prior[0],start=prior[1]+round(2*S*scale) if TIMING else prior[1]+2*S,seen=[],done=None,scale=scale); prior=None")
    replace('else: prior=(v,onset)','else: prior=(v,onset,int(bank[v].argmax())-3)')
    replace("if h is not None: active.append(h); emit('start',h)","if h is not None: active.append(h); emit('start',h,scale=h['scale'])")
    replace("while t>=start+(len(seen)+1)*S:\n                a=start+len(seen)*S; seen.append(observe(audio[a:a+S]))", "step=S*h['scale'] if TIMING else S\n            while t>=start+round((len(seen)+1)*step):\n                a=start+round(len(seen)*step); b=start+round((len(seen)+1)*step); seen.append(observe_scaled(audio[a:b],h['scale'],TIMING,PITCH))")
    replace("return b['start']-2*S < a['start']+len(a['seen'])*S","return b['start']-round(2*S*(b['scale'] if TIMING else 1)) < a['start']+round(len(a['seen'])*S*(a['scale'] if TIMING else 1))")
    replace("start=x['start']-2*S,end=x['start']+len(x['seen'])*S", "start=x['start']-round(2*S*(x['scale'] if TIMING else 1)),end=x['start']+round(len(x['seen'])*S*(x['scale'] if TIMING else 1))")
    env=dict(np=np,S=S,TIMING=mode in ('timing','joint'),PITCH=mode in ('pitch','joint'),observe_scaled=observe_scaled); exec(src,env); return env['acquire']
def run(root,out):
    assert blob(root/'acquisition-factorial.py')=='2e11ec803706d10f15de8200dff97781b2a3b489'
    assert blob(root/'window-holdout.py')=='5bb0110f12858ca96009bb5dcbb70bc6689b7c26'
    def load(f): return runpy.run_path(str(root/f))
    h=load('window-holdout.py'); p=load('acquisition-factorial.py'); v=load('interval-admission.py'); s=load('discourse-sync.py'); m=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']
    for f,b in h['BLOBS'].items(): assert blob(root/f)==b,f
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs=h['window'](5,25); baseline=p['variant'](v['acquire'],*p['MODES']['bank4']); receivers={k:receiver(v['acquire'],k) for k in MODES}
    rng=np.random.default_rng(SEED); rows=[]; stats={}; specimens=[]; checks=0; equivalence=0; out.mkdir(parents=True,exist_ok=False)
    for j in range(6):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); expected=[[a,18,i],[b,13,k]]
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]
        for ci,(ppm,gain,noise,phase,mimic) in enumerate(CASES):
            aa=np.zeros(36*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); offset=lead+int(2.5*S)+phase*16; ratio=1+ppm/1e6
            clean=np.zeros(len(y)*S,np.int32); v['put'](clean,y,0); t=np.arange(round(len(clean)*ratio))/ratio; bb[offset:offset+len(t)]=np.rint(np.interp(t,np.arange(len(clean)),clean,right=0)).astype(np.int32)
            if mimic: v['put'](aa,s['preamble'](a),lead+int(19.5*S))
            noise_seed=SEED*10000+j*100+ci; mix=aa+gain*bb+np.random.default_rng(noise_seed).normal(0,noise,len(aa)); assert abs(mix).max()<5000
            pcm=np.rint(mix).astype('<i2'); digest=sha(pcm.tobytes()); starts=[lead+2*S,offset+round(2*S*ratio)]
            for mode,receive in receivers.items():
                ev=receive(pcm,books,obs,joint,'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,expected))&Counter(map(tuple,got))).values())
                if mode=='bank':
                    assert [{k:v for k,v in e.items() if k!='scale'} for e in ev]==baseline(pcm,books,obs,joint,'multiplex'); equivalence+=1
                detected=[e for e in ev if e['kind']=='start']; used=set(); estimates=[]
                for z,t in zip(expected,starts):
                    choices=[(abs(e['body_start']-t),q) for q,e in enumerate(detected) if q not in used and e['source']==z[0] and abs(e['body_start']-t)<=S//2]
                    if choices:
                        _,q=min(choices); used.add(q); estimates.append(dict(source=z[0],true_scale=1 if z==expected[0] else ratio,scale=detected[q]['scale'],start_error=detected[q]['body_start']-t))
                if j==0:
                    for t in sorted({e['sample'] for e in ev if e['kind'] in ('start','release')}):
                        assert receive(pcm[:t],books,obs,joint,'multiplex')==[e for e in ev if e['sample']<=t]; checks+=1
                row=dict(pair=j,condition=ci,mode=mode,expected=expected,decoded=got,correct=correct,wrong=len(got)-correct,matched=len(used),unmatched=len(detected)-len(used),estimates=estimates,noise_seed=noise_seed,pcm_sha256=digest,events=ev); rows.append(row)
                stats.setdefault(str(ci),{}).setdefault(mode,Counter()).update(expected=2,correct=correct,wrong=row['wrong'],matched=row['matched'],unmatched=row['unmatched'])
            if j==0:
                name=f'case-{ci:02d}.wav'
                with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    for j in range(6):
        for ci in range(len(CASES)): assert len({r['pcm_sha256'] for r in rows if r['pair']==j and r['condition']==ci})==1
    receipt=dict(schema='mhac-clock-propagation-v1',parent=PARENT,grammar_pin=h['PIN'],blobs=h['BLOBS'],seed=SEED,numpy=np.__version__,source_sha256=sha(pathlib.Path(__file__).read_bytes()),conditions=CASES,modes=MODES,physical_pcm=6*len(CASES),evaluations=len(rows),baseline_equivalence=equivalence,prefix_checks=checks,stats=stats,specimens=specimens,limits='Exploratory fixed grid. Scale from mean winning frequency offset of two preamble persistence-trigger windows, quantized bank; not a calibrated clock estimator. Fixed thresholds, capacity two, offline PCM and traces. No measured CPU parity, human evidence or authentication.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset="utf-8"><title>Clock propagation</title><h1>Clock propagation</h1><p>Synthetic PCM; begin at low volume. No autoplay. Conditions: ppm, gain, noise counts, phase ms, extra preamble.</p>'
    for g in specimens:
        ci=g['condition']; html+=f'<h2>Case {ci}: {CASES[ci]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[str(ci)],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
