"""Refs #448/#449: frozen coarse vs fine clock estimates; synthetic only.
Usage: python clock-refinement.py PINNED_PACKAGE NEW_OUTPUT_DIR
"""
import inspect, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='1e3c8a497f7c8543fb4026536f9ea2cd1ebccd30'
S=1280; SEED=4480440
# preamble ppm, body ppm, gain, noise SD, relative phase ms, third onset slots
CASES=[(0,0,1,0,0,None),(25000,25000,1,0,0,None),(-25000,-25000,1,0,0,None),(17000,17000,.8,100,10,None),(-17000,-17000,.8,100,-10,None),(25000,0,1,0,0,None),(-25000,0,1,0,0,None),(0,25000,1,0,0,None),(25000,-25000,1,0,0,None),(0,0,1,0,0,19.5),(-25000,-25000,1,0,0,19.5),(0,0,1,0,0,10.5)]
GRID=np.arange(-12,13)/4
BASIS=np.exp(-2j*np.pi*(np.array([2400,2600])[:,None]*(1+GRID/100))[:,:,None]*np.arange(320)/16000)
def refine(win,v): return float(GRID[abs(BASIS[v]@win).argmax()])
def fine_factory(p):
    src=inspect.getsource(p['receiver'])
    assert src.count('int(bank[v].argmax())-3')==2 and src.count('env=dict(np=np,')==1
    src=src.replace('int(bank[v].argmax())-3','refine(win,v)').replace('env=dict(np=np,','env=dict(refine=refine,np=np,')
    env=dict(p,refine=refine); exec(src,env); return env['receiver']
def stretch(x,ppm):
    r=1+ppm/1e6; t=np.arange(round(len(x)*r))/r
    return np.rint(np.interp(t,np.arange(len(x)),x,right=0)).astype(np.int32)
def run(root,out):
    def load(f): return runpy.run_path(str(root/f))
    p=load('clock-propagation.py'); h=load('window-holdout.py'); v=load('interval-admission.py'); s=load('discourse-sync.py'); m=load('version-bound-payload.py'); joint=load('prefix-disjoint.py')['joint']
    pins={**h['BLOBS'],'clock-propagation.py':'7fe8f5f4ad93095932f9127e0e10f787e6ff7d99','window-holdout.py':'5bb0110f12858ca96009bb5dcbb70bc6689b7c26','acquisition-factorial.py':'2e11ec803706d10f15de8200dff97781b2a3b489'}
    for f,b in pins.items(): assert p['blob'](root/f)==b,f
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    obs=h['window'](5,25); receivers={k:p['receiver'](v['acquire'],k) for k in ('bank','joint')}; receivers['fine']=fine_factory(p)(v['acquire'],'joint')
    rng=np.random.default_rng(SEED); rows=[]; stats={}; specimens=[]; checks=0; out.mkdir(parents=True,exist_ok=False)
    for j in range(6):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); q=int(rng.integers(len(old)))
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]; z=s['preamble'](a)+books[a][13][q].tolist()+[18,18]
        clean=np.zeros(len(y)*S,np.int32); v['put'](clean,y,0)
        for ci,(pre,body,gain,noise,phase,third) in enumerate(CASES):
            aa=np.zeros(48*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); offset=lead+int(2.5*S)+phase*16
            split=round(2*S*(1+pre/1e6)); altered=stretch(clean,pre) if pre==body else np.concatenate([stretch(clean[:2*S],pre),stretch(clean[2*S:],body)])
            bb[offset:offset+len(altered)]=altered; expected=[[a,18,i],[b,13,k]]; starts=[lead+2*S,offset+split]
            if third is not None:
                at=lead+round(third*S); v['put'](aa,z,at); expected.append([a,13,q]); starts.append(at+2*S)
            ns=SEED*10000+j*100+ci; mix=aa+gain*bb+np.random.default_rng(ns).normal(0,noise,len(aa)); assert abs(mix).max()<6000
            pcm=np.rint(mix).astype('<i2'); digest=p['sha'](pcm.tobytes())
            for mode,receive in receivers.items():
                ev=receive(pcm,books,obs,joint,'multiplex'); got=[[e['source'],*e['identity']] for e in ev if e['kind']=='release']; correct=sum((Counter(map(tuple,expected))&Counter(map(tuple,got))).values())
                detected=[e for e in ev if e['kind']=='start']; used=set(); estimates=[]
                for idx,(identity,t) in enumerate(zip(expected,starts)):
                    choices=[(abs(e['body_start']-t),n) for n,e in enumerate(detected) if n not in used and e['source']==identity[0] and abs(e['body_start']-t)<=S//2]
                    if choices:
                        _,n=min(choices); used.add(n); estimates.append(dict(index=idx,scale=detected[n]['scale'],body_start_error=detected[n]['body_start']-t))
                if j==0:
                    for t in sorted({e['sample'] for e in ev if e['kind'] in ('start','release')}):
                        assert receive(pcm[:t],books,obs,joint,'multiplex')==[e for e in ev if e['sample']<=t]; checks+=1
                row=dict(pair=j,condition=ci,mode=mode,expected=expected,body_starts=starts,decoded=got,correct=correct,wrong=len(got)-correct,matched=len(used),unmatched=len(detected)-len(used),estimates=estimates,noise_seed=ns,pcm_sha256=digest,events=ev); rows.append(row)
                stats.setdefault(str(ci),{}).setdefault(mode,Counter()).update(expected=len(expected),correct=correct,wrong=row['wrong'],matched=row['matched'],unmatched=row['unmatched'],evicted=sum(e['kind']=='evict' for e in ev),protected=sum(e['kind']=='overflow-ready-protected' for e in ev),third_released=int(third is not None and expected[-1] in got))
            if j==0:
                name=f'case-{ci:02d}.wav'
                with wave.open(str(out/name),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,condition=ci,pcm_sha256=digest,peak=int(abs(pcm).max())))
    for j in range(6):
        for ci in range(len(CASES)): assert len({r['pcm_sha256'] for r in rows if r['pair']==j and r['condition']==ci})==1
    receipt=dict(schema='mhac-clock-refinement-v1',parent=PARENT,grammar_pin=h['PIN'],blobs=pins,seed=SEED,numpy=np.__version__,source_sha256=p['sha'](pathlib.Path(__file__).read_bytes()),conditions=CASES,modes=list(receivers),physical_pcm=6*len(CASES),evaluations=len(rows),prefix_checks=checks,stats=stats,specimens=specimens,limits='Fixed exploratory grid; 25 frequency hypotheses only at coarse persistence trigger, not adaptive acquisition. Split preamble/body stretch is a constructed discontinuity, not calibrated oscillator. Same capacity two, no EOF flush, offline PCM. No CPU parity or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    html='<!doctype html><meta charset="utf-8"><title>Clock refinement</title><h1>Clock refinement</h1><p>Synthetic PCM; begin at low volume. No autoplay. Conditions: preamble ppm, body ppm, gain, noise counts, phase ms, third start slots.</p>'
    for g in specimens:
        ci=g['condition']; html+=f'<h2>Case {ci}: {CASES[ci]}</h2><audio controls preload="none" src="{g["file"]}"></audio><pre>'+json.dumps(stats[str(ci)],indent=2)+'</pre>'
    (out/'index.html').write_text(html+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>')
    (out/'manifest.json').write_text(json.dumps({f.name:p['sha'](f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
