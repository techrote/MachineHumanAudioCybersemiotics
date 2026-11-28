"""Independent integer PCM oracle for the frozen onset experiment.
Usage: python check_onset.py NEW_SCRATCH [--browser /usr/bin/chromium]
Requires Python 3, NumPy and Node; browser option requires Playwright.
"""
import argparse, hashlib, json, math, subprocess, wave
from pathlib import Path
import numpy as np

PIN = '198ce7fc4c350cd2ec1fc2fa3f85968dc8a7ac96'

def rng(seed):
    s = seed & 0xffffffff
    while True:
        s ^= (s << 13) & 0xffffffff
        s ^= s >> 17
        s ^= (s << 5) & 0xffffffff
        yield s

def template(rate):
    n, period = rate // 50, rate // 500
    values = [math.trunc(3000 * (period - 4*abs(j % period-period//2)) * min(j,n-1-j)/(period*(n//2))) for j in range(n)]
    return np.array(values, dtype=np.int64)

def stimulus(rate, noise, gain, seed, t):
    lo, hi = rate//50, rate*24//1000
    base = seed*65537+rate
    onset = lo + next(rng(base))*(hi-lo+1)//2**32
    g = rng(base+noise*17)
    x = np.array([next(g)*(2*noise+1)//2**32-noise for _ in range(rate//20)],dtype=np.int64)
    if gain:
        x[onset:onset+len(t)] += np.floor(t*gain+0.5).astype(np.int64)
    return x, onset if gain else None

def run_oracle(d):
    groups = {}
    for rate in (8000,16000,48000):
        t=template(rate); lo,hi=rate//50,rate*24//1000; den=int(t@t)
        def scores(x):
            dots=np.correlate(x[lo:hi+len(t)],t,'valid')
            i=int(np.argmax(dots))
            return int(np.max(np.abs(x[lo:hi+len(t)]))),int(dots[i]),lo+i
        peak=0; maxdot=None
        for r in [r for r in d['development'] if r['rate']==rate]:
            x,_=stimulus(rate,r['noise'],0,r['seed'],t); p,dot,at=scores(x)
            assert (r['peak'],r['at'],r['template'],r['threshold'])==(p,at,None,None),r
            peak=max(peak,p); maxdot=dot if maxdot is None else max(maxdot,dot)
        bias=int(np.flatnonzero(np.abs(np.floor(t*.5+.5))>peak)[0])
        assert d['calibration'][str(rate)]==dict(peak=peak,template=maxdot/den,bias=bias)
        for r in [r for r in d['rows'] if r['rate']==rate]:
            x,onset=stimulus(rate,r['noise'],r['gain'],r['seed'],t); p,dot,at=scores(x)
            crossing=np.flatnonzero(np.abs(x[lo:hi+len(t)])>peak)
            threshold=lo+int(crossing[0])-bias if len(crossing) else None
            match=at if dot>maxdot else None
            assert (r['onset'],r['peak'],r['templateScore'],r['threshold'],r['template'])==(onset,p,dot/den,threshold,match),r
            groups.setdefault((rate,r['noise']),[]).append(r)
    def counts(rows,method):
        positives=[r for r in rows if r['onset'] is not None]; negatives=[r for r in rows if r['onset'] is None]
        errors=[r[method]-r['onset'] for r in positives if r[method] is not None]
        return dict(positives=len(positives),negatives=len(negatives),detected=len(errors),falseAccepts=sum(r[method] is not None for r in negatives),exact=errors.count(0),within1=sum(abs(e)<=1 for e in errors),within2=sum(abs(e)<=2 for e in errors),meanSignedSamples=sum(errors)/len(errors) if errors else None,maxAbsSamples=max(map(abs,errors)) if errors else None)
    for row in d['summary']:
        expected=counts(groups[row['rate'],row['noise']],row['method'])
        assert all(row[k]==v for k,v in expected.items()),row
    for method in ('threshold','template'):
        assert counts(d['rows'],method)==d['overall'][method]
    return {'evaluation_rows':len(d['rows']),'development_rows':len(d['development']),'metric_groups':len(d['summary'])+2}

def main():
    p=argparse.ArgumentParser(); p.add_argument('scratch',type=Path); p.add_argument('--browser'); a=p.parse_args()
    src=Path(__file__).resolve().parent/'onset-calibration.cjs'; raw=src.read_bytes()
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==PIN
    root=a.scratch.resolve(); root.mkdir(); out=root/'a'; second=root/'b'
    for target in (out,second): subprocess.run(['node',str(src),str(target)],check=True,stdout=subprocess.DEVNULL)
    assert {p.name for p in out.iterdir()}=={p.name for p in second.iterdir()}
    for path in out.iterdir(): assert path.read_bytes()==(second/path.name).read_bytes(),path
    m=json.loads((out/'manifest.json').read_text()); assert m['scriptSHA256']==hashlib.sha256(raw).hexdigest()
    assert set(m['files'])=={p.name for p in out.iterdir()}-{'manifest.json'}
    for name,digest in m['files'].items(): assert hashlib.sha256((out/name).read_bytes()).hexdigest()==digest
    d=json.loads((out/'receipt.json').read_text()); oracle=run_oracle(d)
    peaks={}
    for name in m['files']:
        if not name.endswith('.wav'): continue
        with wave.open(str(out/name)) as w:
            rate=w.getframerate(); assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getnframes()==rate//20
            x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int64)
            seed=202 if 'alias' in name else 200; noise=512 if 'noisy' in name else 0
            expected,_=stimulus(rate,noise,.125,seed,template(rate)); assert np.array_equal(x,expected)
            peaks[name]=int(np.max(np.abs(x)))
    result={'oracle':oracle,'sha256':m['files'],'peaks_pcm16':peaks,'overall':d['overall']}
    if a.browser:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=a.browser,headless=True,args=['--no-sandbox']); page=browser.new_page(); errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            try:
                page.goto((out/'index.html').as_uri()); result['browser_mode']='file URI'
            except Exception as e:
                result['file_uri_error']=str(e).splitlines()[0]; page.close(); page=browser.new_page(); page.on('pageerror',lambda e:errors.append(str(e))); page.set_content((out/'index.html').read_text()); result['browser_mode']='in-memory DOM fixture'
            for rate in ('8000','16000','48000'):
                page.locator('#rate').select_option(rate); assert page.locator('#rows tr').count()==8
                rows=page.locator('#rows tr').all_inner_texts(); assert len(rows)==8
                for idx,metric in enumerate([r for r in d['summary'] if r['rate']==int(rate)]):
                    expected=[str(metric['noise']),metric['method'],f"{metric['detected']}/{metric['positives']}",f"{metric['falseAccepts']}/{metric['negatives']}",f"{metric['within1']}/{metric['positives']}",str(metric['maxAbsSamples']) if metric['maxAbsSamples'] is not None else '—']
                    assert rows[idx].split('\t')==expected,(rows[idx],expected)
            assert page.locator('audio[autoplay]').count()==0 and page.locator('audio[controls][preload=none]').count()==4
            assert not errors; result['browser_version']=browser.version; result['browser_rows_checked']=24; browser.close()
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
