"""Independent audit of frozen Measurement v2. Python 3, NumPy, Node 22.
Usage: python check_onset_v2.py PINNED_SOURCE_DIR NEW_OUTPUT_DIR
No network, no human data. Source and test must be exact upstream blobs.
"""
import hashlib, io, itertools, json, math, subprocess, sys, wave
from pathlib import Path
import numpy as np

PINS = {'onset-calibration.cjs':'82f576e19936e3b8cecf193f01d891788c0647e0',
        'onset-calibration-test.cjs':'44553d014be7e809792854bcb8e21f3a5be4f621'}
RATES, NOISE, DEV, EVAL = (8000,16000,48000),(0,32,128,512),range(100,112),range(200,216)

def digest(b): return hashlib.sha256(b).hexdigest()
def rng(seed):
    s=seed & 0xffffffff
    while True:
        s ^= (s<<13)&0xffffffff; s ^= s>>17; s ^= (s<<5)&0xffffffff
        yield s

def stimulus(rate,noise,seed,gain):
    n,p=rate//50,rate//500
    t=np.array([math.trunc(3000*(p-4*abs(j%p-p//2))*min(j,n-1-j)/(p*(n//2))) for j in range(n)],dtype=np.int64)
    lo,hi=rate//50,rate*24//1000
    base=seed*65537+rate
    onset=lo+next(rng(base))*(hi-lo+1)//2**32
    g=rng(base+noise*17)
    x=np.array([next(g)*(2*noise+1)//2**32-noise for _ in range(rate//20)],dtype=np.int64)
    if gain: x[onset:onset+n]+=np.floor(t*gain+.5).astype(np.int64)
    dots=np.correlate(x[lo:hi+n],t,'valid'); idx=int(np.argmax(dots)); dot=int(dots[idx]); den=int(t@t)
    return x,t,onset if gain else None,int(np.max(np.abs(x[lo:hi+n]))),dot/den,lo+idx

def wav_bytes(rate,x):
    f=io.BytesIO()
    with wave.open(f,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(x.astype('<i2').tobytes())
    return f.getvalue()

def counts(rows,method):
    pos=[r for r in rows if r['onset'] is not None]; neg=[r for r in rows if r['onset'] is None]
    err=[r[method]-r['onset'] for r in pos if r[method] is not None]
    return dict(positives=len(pos),negatives=len(neg),detected=len(err),falseAccepts=sum(r[method] is not None for r in neg),exact=err.count(0),within1=sum(abs(e)<=1 for e in err),within2=sum(abs(e)<=2 for e in err),meanSignedSamples=sum(err)/len(err) if err else None,maxAbsSamples=max(map(abs,err)) if err else None)

def audit(src,out):
    for name,pin in PINS.items():
        raw=(src/name).read_bytes(); assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==pin,name
    regression=json.loads(subprocess.check_output(['node',str(src/'onset-calibration-test.cjs')]))
    assert regression['status']=='PASS'
    subprocess.run(['node',str(src/'onset-calibration.cjs'),str(out)],check=True,stdout=subprocess.DEVNULL)
    d=json.loads((out/'receipt.json').read_text()); m=json.loads((out/'manifest.json').read_text())
    assert d['schema']==m['schema']=='mhac-onset-calibration-v2'
    assert d['previousReceiptRef']=='92db2601aae859f0860eecb0acd03f44049688db'
    assert d['sourceRef']==m['sourceRef']=='5a1e3a857389ce8f6763c66847c9522179dcbf59'
    assert d['sourceBlob']==m['sourceBlob']=='47938c769604ae56a1f8cb92e5d4ccc3e20f8d59'
    assert d['developmentSeeds']==list(DEV) and d['evaluationSeeds']==list(EVAL)
    assert m['scriptSHA256']==digest((src/'onset-calibration.cjs').read_bytes())
    assert set(m['files'])=={p.name for p in out.iterdir()}-{'manifest.json'}
    for name,h in m['files'].items(): assert digest((out/name).read_bytes())==h,name
    dev=[]; ev=[]; audits=[]; cal={}; summary=[]
    for rate in RATES:
        group=[]
        for noise,seed in itertools.product(NOISE,DEV):
            x,t,onset,peak,score,at=stimulus(rate,noise,seed,0)
            group.append(dict(rate=rate,noise=noise,seed=seed,onset=onset,peak=peak,templateScore=score,templateBestAt=at,thresholdEstimate=None,templateEstimate=None,wavSHA256=digest(wav_bytes(rate,x))))
        peak=max(r['peak'] for r in group); score=max(r['templateScore'] for r in group)
        bias=int(np.flatnonzero(np.abs(np.floor(t*.5+.5))>peak)[0]); cal[str(rate)]=dict(peak=peak,template=score,bias=bias)
        witnesses=[dict(noise=r['noise'],seed=r['seed'],at=r['templateBestAt'],wavSHA256=r['wavSHA256']) for r in group if r['templateScore']==score]
        audits.append(dict(rate=rate,rows=len(group),**cal[str(rate)],templateMaxWitnesses=witnesses)); dev+=group
        for noise in NOISE:
            rows=[]
            for seed,gain in itertools.product(EVAL,(0,.125,.25,.5,1)):
                x,t,onset,p,q,at=stimulus(rate,noise,seed,gain)
                lo,hi=rate//50,rate*24//1000
                crossings=np.flatnonzero(np.abs(x[lo:hi+len(t)])>peak)
                rows.append(dict(rate=rate,noise=noise,seed=seed,gain=gain,onset=onset,peak=p,templateScore=q,threshold=lo+int(crossings[0])-bias if len(crossings) else None,template=at if q>score else None))
            ev+=rows
            for method in ('threshold','template'): summary.append(dict(rate=rate,noise=noise,method=method,**counts(rows,method)))
    assert len(dev)==144 and len(ev)==960
    assert d['development']==dev and d['developmentAudit']==audits and d['calibration']==cal
    assert d['rows']==ev and d['summary']==summary and d['overall']=={m:counts(ev,m) for m in ('threshold','template')}
    for name in ('clean.wav','noisy.wav','alias-clean.wav','alias-noisy.wav'):
        rate,seed=(8000,202) if name.startswith('alias') else (48000,200)
        x,*_=stimulus(rate,512 if 'noisy' in name else 0,seed,.125)
        assert (out/name).read_bytes()==wav_bytes(rate,x),name
    # Scope control: upstream development verifier is not a full receipt validator.
    altered=json.loads(json.dumps(d)); altered['rows'][0]['template']=123456
    bad=out.parent/(out.name+'-eval-corrupted.json'); assert not bad.exists(); bad.write_text(json.dumps(altered))
    try:
        subprocess.run(['node',str(src/'onset-calibration.cjs'),'--verify-development',str(bad)],check=True,stdout=subprocess.DEVNULL)
    finally: bad.unlink()
    assert altered['rows']!=ev
    return dict(status='PASS',development=len(dev),evaluation=len(ev),metricGroups=len(summary)+2,witnesses=audits,manifest=m,upstreamRegression=regression,scopeControl='development-only verifier accepts evaluation mutation as expected; full independent oracle detects it')

if __name__=='__main__': print(json.dumps(audit(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve()),indent=2))
