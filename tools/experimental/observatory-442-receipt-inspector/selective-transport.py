"""Measurement #442/#443: aligned synthetic PCM control and selective retry.
Run: python selective-transport.py fresh64 OUTPUT
No participants, physical transport, authentication or blind synchronisation.
"""
import hashlib, json, sys, wave, itertools
from collections import Counter
from pathlib import Path
import numpy as np

PARENT='6577a91e14d5ca3bb9c241fa908dd7fa97978cee'
INPUT='65e8e9f709581fe3d6b56bb316e4179ea5a5c85d0244a0df48ce0033084280ee'
SEED=4426501
RATE=16000; SLOT=320; AMP=1600; ALL=127
T=np.arange(160)/RATE
BANK=np.exp(-2j*np.pi*(1000+100*np.arange(16))[:,None]*T)
POL=('full','selective')
def sha(x): return hashlib.sha256(x).hexdigest()
def crc(data):
    c=0
    for x in data:
        c^=x
        for _ in range(8): c=((c<<1)^ (7 if c&128 else 0))&255
    return c

def packet(data): return [n for x in [*data,crc(data)] for n in (x>>4,x&15)]
def unpack(v):
    if None in v or len(v)%2: return None
    p=[a*16+b for a,b in zip(v[::2],v[1::2])]
    return p[:-1] if p and crc(p[:-1])==p[-1] else None

def fingerprint(frame,meaning):
    return list(hashlib.sha256(json.dumps([frame,list(meaning)],separators=(',',':')).encode()).digest()[:2])

def direct(x):
    if None in x or len(x)!=7 or x[0] not in range(4) or x[1]!=0 or any(v not in range(3) for v in x[2:5]): return None
    e,s,a=x[2:5]
    return x[:5] if x[5:]==[(e+s+a)%5,(e+2*s+3*a)%5] else None

def channel(symbols,z,shift,sd,mix):
    n=len(symbols); noise=z[:n].copy()
    if mix:
        smooth=np.array([np.convolve(v,np.ones(12)/12,'same') for v in noise]); smooth/=np.sqrt(np.mean(smooth*smooth,axis=1,keepdims=True)); noise=(1-mix)*noise+mix*smooth
    noise*=sd/np.sqrt(np.mean(noise*noise,axis=1,keepdims=True))
    x=np.zeros((n,SLOT)); t=np.arange(192)/RATE; env=np.minimum(1,np.minimum(np.arange(192),191-np.arange(192))/16)
    for i,v in enumerate(symbols):
        if v is not None: x[i,:192]=AMP*env*np.sin(2*np.pi*(1000+100*v+shift)*t)
    y=np.clip(np.rint(x+noise),-32768,32767).astype('<i2')
    mag=abs(y[:,16:176].astype(float)@BANK.T)*2/160
    order=np.argsort(mag,axis=1); top=order[:,-1]; best=mag[np.arange(n),top]; margin=best-mag[np.arange(n),order[:,-2]]
    got=[int(v) if a>=350 and m>=200 else None for v,a,m in zip(top,best,margin)]
    return got,y,dict(sent=symbols,observed=got,pcm_sha256=sha(y.tobytes()),noise_sha256=sha(noise.astype('<f8').tobytes()),peak=int(np.max(abs(y.astype(int)))),best=best.tolist(),margin=margin.tolist())

def outcome(g,expected): return 'withheld' if g is None else 'correct' if g==expected else 'wrong'

def run(src,out):
    raw=(src/'traces.jsonl').read_bytes(); assert sha(raw)==INPUT
    rows=[json.loads(s) for s in raw.splitlines()]; by={(r['condition'],r['fixture']):r for r in rows}; rng=np.random.default_rng(SEED); traces=[]; gallery={}
    for r,stale in [(r,False) for r in rows]+[(r,True) for r in rows if r['condition']=='white']:
        frame=r['fixture']; c=r['condition']; other=by[(c,(frame+1)%54)] if stale else r
        expected=None if c=='absent' else r['expected'][:5]; initial=r['observed'][0]; shift=0 if c=='clean' else 27 if c in ('offgrid','persistent_mixed','transient_mixed') else 25; sd=0 if c=='clean' else 1000; mix=1 if c=='colored' else .25 if c=='offgrid' else 0
        z=rng.normal(size=(4,16,SLOT)); tag=None if expected is None else fingerprint(frame,expected)
        initial_header=packet([frame,*tag]) if tag is not None else [None]*8
        h,hy,ht=channel(initial_header,z[0],shift,sd,mix); hd=unpack(h); valid=hd is not None and hd[0]==frame
        for policy in POL:
            seconds=.24+len(h)*.02; g=direct(initial); parts={'initial_header':ht}; audio=[hy]; retry=False; request_mask=0; reason='initial_tag_invalid'
            if not valid: g=None
            elif g is not None and fingerprint(frame,g)==hd[1:]: reason='initial_valid'
            else:
                g=None; retry=True; reason='request_invalid'; request_mask=ALL if policy=='full' or None not in initial else sum(1<<i for i,v in enumerate(initial) if v is None)
                req,qy,qt=channel(packet([frame,request_mask]),z[1],shift,sd,mix); parts['request']=qt; audio.append(qy); seconds+=len(req)*.02+.01
                q=unpack(req)
                if q is not None and q[0]==frame and 0<q[1]<=ALL:
                    mask=q[1]; ids=[i for i in range(7) if mask>>i&1]; reply_frame=other['fixture']; symbols=[other['transmitted'][2][i] for i in ids]
                    if c=='absent': symbols=[None]*len(ids)
                    rh,ry,rt=channel(packet([reply_frame,mask]),z[2],shift,sd,mix); body,byy,bt=channel(symbols,z[3][ids],shift,sd,mix); parts.update(reply_header=rt,body=bt); audio.extend([ry,byy]); seconds+=(len(rh)+len(body))*.02+.01; reason='reply_invalid'
                    if unpack(rh)==[frame,request_mask]:
                        combined=list(initial)
                        for i,v in zip(ids,body): combined[i]=v
                        g=direct(combined); reason='candidate_invalid'
                        if g is not None and fingerprint(frame,g)==hd[1:]: reason='retry_valid'
                        else: g=None
            tr=dict(condition='stale_white' if stale else c,fixture=frame,policy=policy,expected=expected,initial=initial,initial_pcm_sha256=r['pcm_sha256'][0],retry_frame=other['fixture'],decoded=g,status=outcome(g,expected),seconds=round(seconds,8),retry=retry,request_mask=request_mask,reason=reason,parts=parts)
            traces.append(tr)
            if c=='white' and not stale and retry and len(gallery)<2 and (not gallery or frame==next(iter(gallery.values()))[0]): gallery[policy]=(frame,np.concatenate([v.ravel() for v in audio]))
    groups=[]
    for c,p in itertools.product(sorted({r['condition'] for r in traces}),POL):
        rr=[r for r in traces if (r['condition'],r['policy'])==(c,p)]; counts=Counter(r['status'] for r in rr); sec=sum(r['seconds'] for r in rr)
        groups.append(dict(condition=c,policy=p,n=len(rr),correct=counts['correct'],wrong=counts['wrong'],withheld=counts['withheld'],seconds=round(sec,6),correct_per_second=counts['correct']/sec,retries=sum(r['retry'] for r in rr),body_symbols=sum(len(r['parts'].get('body',{}).get('sent',[])) for r in rr)))
    out.mkdir(); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in traces)); receipt=dict(parent=PARENT,input_sha256=INPUT,seed=SEED,source_sha256=sha(Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,groups=groups,limits='Run64 initial body observations replayed, not newly rendered. New aligned 16-FSK PCM headers, request and reply, no blind acquisition. 20 ms slots; 10 ms each turnaround. CRC8 is not authentication; 16-bit tag from pre-fault intended message. Tags not proof of source identity. Matched peak not matched total energy. Synthetic only.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    for p,(f,y) in gallery.items():
        with wave.open(str(out/f'{p}.wav'),'wb') as w: w.setparams((1,2,RATE,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Selective transport</title><h1>Selective transport</h1><p>Synthetic aligned PCM. Initial body replay, new control and retry PCM. Audio excludes initial body and turnaround silence.</p><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{p}<br><audio controls preload="none" src="{p}.wav"></audio></p>' for p in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(groups)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.condition)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.condition===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); verify(out)

def verify(out):
    rows=[json.loads(s) for s in (out/'traces.jsonl').read_text().splitlines()]; rec=json.loads((out/'receipt.json').read_text()); assert len(rows)==972
    for r in rows:
        p=r['parts']; h=unpack(p['initial_header']['observed']); g=direct(r['initial']); valid=h is not None and h[0]==r['fixture']; cost=400
        if not valid: g=None
        elif g is None or fingerprint(r['fixture'],g)!=h[1:]:
            g=None; cost+=130
            if 'body' in p:
                cost+=130+20*len(p['body']['sent']); q=unpack(p['reply_header']['observed'])
                if q==[r['fixture'],r['request_mask']]:
                    x=list(r['initial']); ids=[i for i in range(7) if q[1]>>i&1]
                    for i,v in zip(ids,p['body']['observed']): x[i]=v
                    g=direct(x)
                    if g is not None and fingerprint(r['fixture'],g)!=h[1:]: g=None
        assert g==r['decoded'] and outcome(g,r['expected'])==r['status'] and abs(cost/1000-r['seconds'])<1e-8
    for g in rec['groups']:
        rr=[r for r in rows if (r['condition'],r['policy'])==(g['condition'],g['policy'])]; assert len(rr)==g['n']==54 and all(sum(r['status']==s for r in rr)==g[s] for s in ('correct','wrong','withheld')); assert abs(sum(r['seconds'] for r in rr)-g['seconds'])<1e-6
    for p,h in json.loads((out/'manifest.json').read_text()).items(): assert sha((out/p).read_bytes())==h
    for f in range(54):
        x=packet([f,127]); assert unpack(x)==[f,127]
        for k in range(len(x)):
            for bit in (1,2,4,8): y=x.copy(); y[k]^=bit; assert unpack(y) is None
    z=np.ones((16,SLOT)); got,_,_=channel(list(range(16)),z,27,0,0); assert got==list(range(16))
    print('verified',len(rows),'decisions,',len(rec['groups']),'groups, 1296 CRC bit flips, 16 clean off-grid tones')

if __name__=='__main__':
    if sys.argv[1]=='--verify': verify(Path(sys.argv[2]))
    else: run(Path(sys.argv[1]),Path(sys.argv[2]))
