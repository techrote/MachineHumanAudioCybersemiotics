"""Adversarial #448/#449: falsify aligned transport at pinned Measurement #443.
python control-boundaries.py PATH_TO_SELECTIVE_TRANSPORT OUTPUT
Synthetic PCM only, no human, physical or authentication evidence.
"""
import hashlib, itertools, json, runpy, sys, wave
from collections import Counter
from pathlib import Path
import numpy as np

REF='8656394a04100f9dd6d835397cd2831f58356b36'
PIN='2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf'
SEED=4480650

def sha(b): return hashlib.sha256(b).hexdigest()
def run(source,out):
    assert sha(source.read_bytes())==PIN
    p=runpy.run_path(str(source)); rng=np.random.default_rng(SEED)
    channel,packet,unpack,tag,direct=[p[k] for k in ('channel','packet','unpack','fingerprint','direct')]
    meanings=[[l,0,e,s,a] for l,e,s,a in itertools.product(range(4),range(3),range(3),range(3))]
    def decode(y):
        mag=abs(y[:,16:176].astype(float)@p['BANK'].T)*2/160
        order=np.argsort(mag,axis=1); best=mag[np.arange(len(y)),order[:,-1]]; second=mag[np.arange(len(y)),order[:,-2]]
        return [int(k) if a>=350 and a-b>=200 else None for k,a,b in zip(order[:,-1],best,second)]
    rows=[]; collisions=[]; groups={}; samples={}
    for frame in range(54):
        buckets={}
        for meaning in meanings:
            buckets.setdefault(tuple(tag(frame,meaning)),[]).append(meaning)
        for t,ms in buckets.items():
            for a,b in itertools.combinations(ms,2): collisions.append(dict(frame=frame,tag=list(t),intended=a,alternate=b))
        meaning=meanings[int(rng.integers(len(meanings)))]; data=[frame,*tag(frame,meaning)]; sent=packet(data); z=rng.normal(size=(8,320))
        for shift in (0,27,50,75):
            got,y,_=channel(sent,z,shift,1000,0); assert decode(y)==got
            for delay in (-160,-80,-32,0,32,80,160):
                capture=np.zeros(y.size+640,dtype='<i2'); start=320+delay; capture[start:start+y.size]=y.ravel()
                window=capture[320:320+y.size].reshape(y.shape); fixed=decode(window)
                oracle=decode(capture[start:start+y.size].reshape(y.shape)); assert oracle==got
                for mode,v in [('fixed',fixed),('oracle',oracle)]:
                    q=unpack(v); status='correct' if q==data else 'withheld' if q is None or q[0]!=frame else 'wrong_tag'
                    row=dict(frame=frame,shift_hz=shift,delay_samples=delay,mode=mode,sent=sent,observed=v,status=status,pcm_sha256=sha(capture.tobytes()))
                    rows.append(row); groups.setdefault((shift,delay,mode),Counter())[status]+=1
                if frame==0 and shift==27 and delay in (0,80,160): samples[f'delay-{delay}']=capture
    assert collisions
    for w in collisions:
        frame=w['frame']; a=w['intended']; b=w['alternate']; h=packet([frame,*w['tag']]); assert tag(frame,a)==tag(frame,b)
        def body(m):
            e,s,o=m[2:]; return m+[(e+s+o)%5,(e+2*s+3*o)%5]
        hb,hy,_=channel(h,np.ones((8,320)),0,0,0); hd=unpack(hb); assert hd==[frame,*w['tag']]
        for label,m in [('intended',a),('alternate',b)]:
            v,y,_=channel(body(m),np.ones((7,320)),0,0,0); g=direct(v); assert g==m and tag(frame,g)==hd[1:]
            w[label+'_pcm_sha256']=sha(y.tobytes()); w[label+'_observed']=v
            if w is collisions[0]: samples['collision-'+label]=np.concatenate((hy.ravel(),y.ravel()))
    out.mkdir(); summary=[dict(shift_hz=s,delay_samples=d,mode=m,**{k:c[k] for k in ('correct','wrong_tag','withheld')}) for (s,d,m),c in sorted(groups.items())]
    assert all(sum(g[k] for k in ('correct','wrong_tag','withheld'))==54 for g in summary)
    assert len(rows)==3024 and len(summary)==56
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipt=dict(ref=REF,source_sha256=PIN,seed=SEED,python=sys.version.split()[0],numpy=np.__version__,rows=len(rows),summary=summary,collision_pairs=collisions,limits='Known frame ID, 16 kHz, 20 ms slots, 10 ms observation, noise 1000 PCM counts RMS. Delay is integer sample displacement with zero padding, not clock drift. Oracle knows true offset. Collisions are finite-domain intentional alternate messages, not stochastic error rates. No physical/human evidence or authentication.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    for name,y in samples.items():
        with wave.open(str(out/(name+'.wav')),'wb') as f:
            f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Control boundaries</title><h1>Aligned transport boundaries</h1><p>Synthetic only. Delay samples at 16 kHz. Oracle alignment is supplied, not acquired.</p><select id="s"></select><pre id="r"></pre>'+''.join(f'<p>{n}<br><audio controls preload="none" src="{n}.wav"></audio></p>' for n in samples)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(summary)+';for(const v of [0,27,50,75])s.add(new Option(v+" Hz",v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.shift_hz==s.value),null,2)}s.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html)
    (out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]))
