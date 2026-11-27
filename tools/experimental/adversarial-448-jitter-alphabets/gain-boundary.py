"""Adversarial #448/#449. Run 060: gain and clipping boundary, synthetic PCM.
Usage: OPENBLAS_NUM_THREADS=1 python gain-boundary.py RUN059_PACKAGE OUT
AI-assisted exploratory simulation, no human evidence or action authorization.
"""
import hashlib, inspect, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='b8c040809c015c59ae0936dd931c51356a41a03a'
PINS={'decoder-budget.py':'eda822f5942e73d6b83c83c9c5dc92bac78feae9','shared-clock.py':'5876b059f8f6789d61e3fe7821f2a326eb170772','clock-propagation.py':'7fe8f5f4ad93095932f9127e0e10f787e6ff7d99','clock-refinement.py':'dc24cdcac40e10252b070da8073028544c98ef21','window-holdout.py':'5bb0110f12858ca96009bb5dcbb70bc6689b7c26'}
SEED=4480600
MODES=('absolute','preamble-relative','joint-relative','joint-contrast')
CASES=('clean','gain20','gain05','clip350','clip100','noise100','gain20-noise100','opposed-clock-load','noise-only','preamble-only')
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def run(root,out):
    def load(f): return runpy.run_path(str(root/f))
    for f,b in PINS.items(): assert blob(root/f)==b,f
    h=load('window-holdout.py')
    for f,b in h['BLOBS'].items(): assert blob(root/f)==b,f
    d=load('decoder-budget.py'); src=inspect.getsource(d['run']); prefix=src.split("    g['SEED']=",1)[0]; assert len(prefix)<len(src)
    env=dict(d); exec(prefix+'    return g\n',env); g=env['run'](root,out,'fresh')
    p=load('clock-propagation.py'); r=load('clock-refinement.py'); m=load('version-bound-payload.py'); v=load('interval-admission.py'); s=load('discourse-sync.py'); joint=load('prefix-disjoint.py')['joint']; S=g['S']
    _,raw,_=m['build'](root); old,new=raw; long=np.concatenate([m['extend'](w,i,'polynomial') for i,w in enumerate(raw)])
    books={a:{13:np.column_stack((np.zeros((len(old),3),int),(old+a*np.arange(10)**5)%17)),18:np.column_stack((np.full((len(long),3),16),(long+np.arange(15)**4+a*np.arange(15)**5)%17))} for a in (0,1)}
    detsrc=inspect.getsource(g['detect']); needle='scores[k]>=600 and scores[k]>=np.sqrt(np.mean(win**2))'; assert detsrc.count(needle)==1
    denv=dict(g); exec(detsrc.replace(needle,'scores[k]>=40 and scores[k]>=np.sqrt(np.mean(win**2))'),denv)
    def observe(slot,scale,timing,pitch,contrast):
        a,b=round(80*scale),round(480*scale); x=slot[a:b]; n=len(x)
        basis=np.exp(-2j*np.pi*np.array([*range(400,2001,100),2200])[:,None]*np.arange(n)/16000/scale)
        scores=abs(basis@x)*2/n; k=int(scores.argmax()); rms=np.sqrt(np.mean(x.astype(float)**2))
        ok=scores[k]>=max(40,1.1*rms) and (not contrast or scores[k]>=1.25*np.partition(scores,-2)[-2])
        return (18 if k==17 else k) if ok else None
    out.mkdir(parents=True,exist_ok=False); rows=[]; checks=0; specimens=[]
    def evaluate(pcm,want,ends,split,j,case,prior=None):
        nonlocal checks
        digest=sha(pcm.tobytes()); events={}
        for mode in MODES:
            detect=g['detect'] if mode=='absolute' else denv['detect']; acq,det=detect(pcm)
            obs=p['observe_scaled'] if mode in MODES[:2] else lambda x,z,t,f:observe(x,z,t,f,mode=='joint-contrast')
            ev,w=g['receive'](pcm,acq,books,joint,obs,'prune1m'); events[mode]=ev
            rel=[e for e in ev if e['kind']=='release']; got=Counter((e['source'],*e['identity']) for e in rel); expected=Counter(map(tuple,want)); correct=sum((got&expected).values())
            strict=Counter((e['source'],*e['identity']) for e in rel if not(e['incomplete'] or e['decoder_incomplete'] or e['unadmitted']))
            row=dict(split=split,pair=j,case=case,mode=mode,expected=want,ends=ends,pcm_sha256=digest,correct=correct,wrong=sum(got.values())-correct,strict=sum((strict&expected).values()),timely=sum(any([e['source'],*e['identity']]==a and e['sample']<=b+3200 for e in rel) for a,b in zip(want,ends)),starts=sum(e['kind']=='start' for e in ev),detector_products=det,work=w,events=ev)
            assert w.get('slots',0)<=66 and w.get('book_cells',0)<=1000000
            rows.append(row)
            if prior is not None and mode=='absolute': assert digest==prior['pcm_sha256'] and ev==prior['events']
            if j==0:
                for t in sorted({e['sample'] for e in ev if e['kind'] in ('start','release')}):
                    sub,_=detect(pcm[:t]); assert sub==[a for a in acq if a[0]<=t]
                    assert g['receive'](pcm[:t],sub,books,joint,obs,'prune1m')[0]==[e for e in ev if e['sample']<=t]; checks+=1
    prior=[q for q in map(json.loads,(root/'decoder-fresh'/'traces.jsonl').read_text().splitlines()) if q['pair']==0 and q['mode']=='prune1m']
    for q in prior:
        with wave.open(str(root/'decoder-fresh'/f"case-{q['condition']:02d}.wav"),'rb') as f: pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2')
        evaluate(pcm,q['expected'],q['ends'],'retained',0,str(q['condition']),q)
    rng=np.random.default_rng(SEED)
    for j in range(8):
        a=j%2; b=1-a; i=int(rng.integers(len(long))); k=int(rng.integers(len(old))); q=int(rng.integers(len(old))); lead=S+int(rng.integers(80)); off=lead+int(2.5*S)
        x=s['preamble'](a)+books[a][18][i].tolist()+[18,18]; y=s['preamble'](b)+books[b][13][k].tolist()+[18,18]; z=s['preamble'](a)+books[a][13][q].tolist()+[18,18]
        aa=np.zeros(48*S,np.int32); bb=aa.copy(); v['put'](aa,x,lead); v['put'](bb,y,off)
        for ci,case in enumerate(CASES):
            mix=(aa+bb).astype(float); want=[[a,18,i],[b,13,k]]; ends=[lead+22*S,off+17*S]; noise=np.random.default_rng(SEED*10000+j*100+ci).normal(0,100,len(aa))
            if case=='gain20': mix*=.2
            if case=='gain05': mix*=.05
            if case=='clip350': mix=np.clip(mix,-350,350)
            if case=='clip100': mix=np.clip(mix,-100,100)
            if case=='noise100': mix+=noise
            if case=='gain20-noise100': mix=.2*mix+noise
            if case=='opposed-clock-load':
                cc=np.zeros_like(aa); v['put'](cc,y,0); ypcm=cc[:17*S]; alt=np.concatenate([r['stretch'](ypcm[:2*S],30000),r['stretch'](ypcm[2*S:],-30000)]); dd=np.zeros_like(aa); dd[off:off+len(alt)]=alt; at=lead+round(18*S); v['put'](dd,z,at); mix=aa+.65*dd+noise; want.append([a,13,q]); ends=[ends[0],off+len(alt),at+17*S]
            if case=='noise-only': mix=noise; want=[]; ends=[]
            if case=='preamble-only':
                cc=np.zeros_like(aa); v['put'](cc,s['preamble'](a),lead); v['put'](cc,s['preamble'](b),off); mix=.2*cc+noise; want=[]; ends=[]
            pcm=np.rint(mix).astype('<i2'); evaluate(pcm,want,ends,'fresh',j,case)
            if j==0:
                name=case+'.wav'
                with wave.open(str(out/name),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
                specimens.append(dict(file=name,pcm_sha256=sha(pcm.tobytes()),peak=int(abs(pcm).max())))
    stats={}
    for row in rows:
        for case in ('total',row['case']):
            stats.setdefault(row['split'],{}).setdefault(case,{}).setdefault(row['mode'],Counter()).update(expected=len(row['expected']),**{k:row[k] for k in ('correct','wrong','strict','timely','starts','detector_products')},**{k:row['work'].get(k,0) for k in ('slots','book_cells')})
    priorids={tuple(x) for q in map(json.loads,(root/'decoder-fresh'/'traces.jsonl').read_text().splitlines()) for x in q['expected']}; freshids={tuple(x) for q in rows if q['split']=='fresh' for x in q['expected']}; assert not priorids&freshids
    assert all(len({q['pcm_sha256'] for q in rows[i:i+4]})==1 for i in range(0,len(rows),4))
    (out/'traces.jsonl').write_text(''.join(json.dumps(q)+'\n' for q in rows)); result=dict(parent=PARENT,pins=PINS,seed=SEED,rows=len(rows),prefix_checks=checks,retained_baselines=len(prior),fresh_identities=len(freshids),stats=stats,specimens=specimens,limits='Synthetic exploratory conditions, fixed thresholds, same PCM and body/decoder ceilings. Not equal end-to-end CPU, no acoustic calibration or human evidence.')
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(stats,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
