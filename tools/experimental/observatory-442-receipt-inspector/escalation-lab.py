"""Measurement #442/#443. Fresh Dual3 PCM, bounded retry, aligned synthetic transport."""
import hashlib, importlib.util, itertools, json, sys, wave
from pathlib import Path
from collections import Counter
import numpy as np
PIN='56383207d8d5d8d4b2fb6db1802688ae826679e0'
SEED=4427301

def load(name, digest):
    p=Path(__file__).with_name(name+'.py')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
s=load('selective-transport','2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf')
a=load('evidence-admission','bb426d8e81a2fce162bf446b06c6dc305f54298acf876fd936cea073fb4b6fe2')
b,l=a.b,a.l
POL=('full1','selective1','escalate2','full2')
CONDS={'clean':(0,0,0,0),'white':(25,1000,0,1000),'colored':(25,1000,1,1000),'offgrid':(27,1000,.25,1000),'transient':(27,1000,0,1000),'persistent':(27,1000,0,1000),'weak_control':(27,1000,0,3500),'absent':(25,1000,0,1000)}
def rank(x): return 27*x[0]+9*x[2]+3*x[3]+x[4]
def valid(x,tag):
    g=s.direct(x); return g if g is not None and rank(g)==tag else None

def run(out):
    out.mkdir(); rng=np.random.default_rng(SEED); rows=[]; gallery={}
    train=l.null(l.SEED+1,(0,.5,1),a.MODE)
    th=np.max([np.quantile(v,.99,axis=0,method='higher') for v in train.values()],axis=0)[:,0]
    for i,(lex,e,src,op) in enumerate(itertools.product(range(4),range(3),range(3),range(3))):
        expected=[lex,0,*b.code((e,src,op),a.MODE)]; phase=float(rng.uniform(0,2*np.pi)); z=rng.normal(size=(3,b.d.SLOT)); ctrl=rng.normal(size=(7,7,s.SLOT))
        for c,(shift,sd,mix,csd) in CONDS.items():
            changed=expected.copy()
            if c in ('transient','persistent'): changed[2]=(e+1)%3; changed[3]=(src+2)%3; changed[6]=None
            scale=1600/np.max(abs(a.p.render(expected,a.MODE,shift,phase,2)))
            signal=a.p.render(changed,a.MODE,shift,phase,2)*scale
            if c=='absent': signal[:]=0
            y=b.d.pcm(signal+sd*l.a.mix(z,mix)); win,j,d,h=l.measure(y[:,160:800].astype(float),a.MODE)
            initial=[v if j[k]>=max(80,th[k]*d[k,0]) else None for k,v in enumerate(win)]
            header=s.packet([i,rank(expected)]) if c!='absent' else [None]*6
            obs,hy,ht=s.channel(header,ctrl[0],shift,csd,mix); hd=s.unpack(obs)
            for p in POL:
                state=list(initial); parts=[]; audio=[hy.ravel(),y.ravel()]; cost=360; g=None
                if hd is not None and hd[0]==i and hd[1]<108:
                    g=valid(state,hd[1])
                    for attempt in range(2 if p.endswith('2') else 1):
                        if g is not None: break
                        mask=sum(1<<k for k,v in enumerate(state) if v is None) if p in ('selective1','escalate2') and attempt==0 else 127
                        mask=mask or 127; ids=[k for k in range(7) if mask>>k&1]
                        q,qy,qt=s.channel(s.packet([i,mask]),ctrl[1+3*attempt],shift,csd,mix); cost+=130; audio.extend([np.zeros(160,dtype='<i2'),qy.ravel()]); part={'mask':mask,'request':qt}; parts.append(part)
                        if s.unpack(q)!=[i,mask]: break
                        rh,ry,rt=s.channel(s.packet([i,mask]),ctrl[2+3*attempt],shift,csd,mix)
                        sent=changed if c=='persistent' else expected
                        v,by,bt=s.channel([sent[k] for k in ids],ctrl[3+3*attempt][ids],shift,csd,mix); cost+=130+20*len(ids); audio.extend([np.zeros(160,dtype='<i2'),ry.ravel(),by.ravel()]); part.update(reply=rt,body=bt)
                        if s.unpack(rh)!=[i,mask]: break
                        for k,w in zip(ids,v): state[k]=w
                        g=valid(state,hd[1])
                status=s.outcome(g,None if c=='absent' else expected[:5]); rows.append(dict(condition=c,fixture=i,policy=p,expected=expected,initial=initial,initial_pcm_sha256=s.sha(y.astype('<i2').tobytes()),header=ht,parts=parts,decoded=g,status=status,ms=cost))
                if i==0 and c in ('white','transient'): gallery[c+'-'+p]=np.concatenate(audio)
    groups=[]
    for c,p in itertools.product(CONDS,POL):
        rr=[r for r in rows if (r['condition'],r['policy'])==(c,p)]; n=Counter(r['status'] for r in rr); ms=sum(r['ms'] for r in rr); groups.append(dict(condition=c,policy=p,correct=n['correct'],wrong=n['wrong'],withheld=n['withheld'],ms=ms,correct_per_second=1000*n['correct']/ms,retry_requests=sum(len(r['parts']) for r in rr)))
    verify(rows,groups)
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipt=dict(parent=PIN,seed=SEED,source_sha256=s.sha(Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,conditions=CONDS,thresholds=th.tolist(),groups=groups,limits='Aligned slots; known frame ID; trusted pre-fault rank; no authentication. Request validity at sender modeled by matching sent request (ideal feedback association); no timeout cost beyond sent slots and 10ms turnaround. Shared peak not energy; absent only has no target. Two retries max.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    for name,y in gallery.items():
        with wave.open(str(out/(name+'.wav')),'wb') as w: w.setparams((1,2,16000,0,'NONE','not compressed')); w.writeframes(np.rint(y*.25).astype('<i2').tobytes())
    html='<!doctype html><meta charset=utf-8><title>Bounded escalation</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto}pre{white-space:pre-wrap}</style><h1>Bounded escalation — synthetic PCM</h1><p>Matched initial capture and staged noise; 360 ms initial packet. Four policies, at most two retries.</p><select id="c"></select><pre id="r"></pre>'+''.join(f'<p>{n}<br><audio controls preload="none" src="{n}.wav"></audio></p>' for n in gallery)+'<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const d='+json.dumps(groups)+';const c=document.getElementById("c"),r=document.getElementById("r");for(const v of new Set(d.map(x=>x.condition)))c.add(new Option(v,v));function draw(){r.textContent=JSON.stringify(d.filter(x=>x.condition===c.value),null,2)}c.onchange=draw;document.querySelectorAll("audio").forEach(a=>a.volume=.2);draw()</script>'
    (out/'index.html').write_text(html); (out/'manifest.json').write_text(json.dumps({p.name:s.sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')

def verify(rows,groups):
    assert len(rows)==108*len(CONDS)*len(POL)
    for r in rows:
        hd=s.unpack(r['header']['observed']); x=list(r['initial']); cost=360
        eligible=hd is not None and hd[0]==r['fixture'] and hd[1]<108
        g=valid(x,hd[1]) if eligible else None
        assert len(r['parts'])<=(2 if r['policy'].endswith('2') else 1)
        for part in r['parts']:
            assert eligible and g is None; mask=part['mask']; cost+=130
            if 'body' not in part: assert s.unpack(part['request']['observed'])!=[r['fixture'],mask]; break
            cost+=130+20*len(part['body']['observed'])
            assert s.unpack(part['request']['observed'])==[r['fixture'],mask]
            if s.unpack(part['reply']['observed'])!=[r['fixture'],mask]: break
            for k,v in zip([k for k in range(7) if mask>>k&1],part['body']['observed']): x[k]=v
            g=valid(x,hd[1])
        assert g==r['decoded'] and cost==r['ms'] and r['status']==s.outcome(g,None if r['condition']=='absent' else r['expected'][:5])
    for j in range(0,len(rows),4): assert len({r['initial_pcm_sha256'] for r in rows[j:j+4]})==1 and len({r['header']['pcm_sha256'] for r in rows[j:j+4]})==1
    for g in groups:
        rr=[r for r in rows if (r['condition'],r['policy'])==(g['condition'],g['policy'])]; assert len(rr)==108 and sum(r['ms'] for r in rr)==g['ms'] and all(sum(r['status']==v for r in rr)==g[v] for v in ('correct','wrong','withheld'))
    print('verified',len(rows),'decisions',len(groups),'groups')

if __name__=='__main__': run(Path(sys.argv[1]))
