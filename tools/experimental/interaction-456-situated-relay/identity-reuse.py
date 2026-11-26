"""Interaction #456: bounded identity reuse, synthetic dialogue, original PCM.
Python 3.11+ stdlib; run: python identity-reuse.py NEW_OUTPUT.
AI-assisted single-agent experiment, 2026-11-26; not human or physical-channel evidence.
"""
import hashlib,itertools,json,math,random,struct,sys,wave
from functools import lru_cache
from pathlib import Path
PARENT='3c991baa6ebece18aeb48f751ef42ff2d0533f5b'
MAIN='495a98ca12bae467a507031f04931aa4254b1866'
RATE,SLOT,N,H=8000,1600,160,600
Q,E,A,R,F,C=range(6)
POLICIES=('none','delay-only','bounded','unique')
BAD=('wrong_evidence','wrong_ack','wrong_report','false_confirmation','stale_release','unconfirmed_release')
def digest(b): return hashlib.sha256(b).hexdigest()
def dump(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
BANK=tuple(tuple(math.sin(2*math.pi*(400+100*k)*j/RATE) for j in range(N)) for k in range(16))
@lru_cache(None)
def acoustic(token):
    w=tuple(round(1000*x) for k in token for x in BANK[k]); decoded=[]
    for i in range(3):
        scores=[abs(sum(x*y for x,y in zip(w[i*N:(i+1)*N],b))) for b in BANK]
        k=max(range(16),key=scores.__getitem__); assert scores[k]>4*max(scores[:k]+scores[k+1:]); decoded.append(k)
    assert tuple(decoded)==token
    return tuple(decoded),w,digest(struct.pack('<480h',*w))
def simulate(c,p,horizon=H,audio=False):
    D,L=c['delay'],c['lifetime']; modulus=16 if p=='unique' else 2
    guard={'none':0,'delay-only':D+1,'bounded':2*D+L,'unique':0}[p]
    local=[dict(g=0,stage=Q,start=None,next=0) for _ in range(2)]; last=[{},{}]; sources=[None,None]; queue=[]
    valid=set(); confirmed=set(); trace=[]; samples=[0]*(SLOT*horizon) if audio else None
    m=dict.fromkeys(('spent','current','busy','wait','timeouts','finished','evidence','confirmed','settled','release','peak_queue')+BAD,0)
    for t in range(horizon):
        log=[]
        for a,s in enumerate(sources):
            if s and t>=s['end']: sources[a]=None; log.append(['expire',a,s['id'],s['origin']])
        for a,l in enumerate(local):
            if l['start'] is not None and t-l['start']>=100:
                log.append(['timeout',a,l['g']]); m['timeouts']+=1; l.update(g=l['g']+1,stage=Q,start=None,next=t)
        due=[x for x in queue if x[0]==t]; queue=[x for x in queue if x[0]!=t]
        for _,token,origin,emitted in due:
            k,a,v=token; l=local[a]; s=sources[a]; outcome='ignore'; active=l['start'] is not None and l['g']<16
            if k==Q:
                if s is None:
                    sources[a]=dict(id=v,origin=origin,end=t+L,settled=False,pending=E); outcome='admit'
                elif s['id']==v and not s['settled']:
                    s['pending']=E; outcome='repeat'
                else: m['busy']+=1; outcome='busy'
            elif k==E and active and l['stage']==Q and v==l['g']%modulus:
                m['evidence']+=1; m['wrong_evidence']+=origin!=l['g']; l.update(stage=A,next=t); outcome='evidence'
            elif k==A and s and s['id']==v:
                m['wrong_ack']+=origin!=s['origin']; s.update(settled=True,pending=R); outcome='settle'
                if origin==s['origin']: valid.add((a,origin))
            elif k==R and active and l['stage']==A and v==l['g']%modulus:
                g=l['g']; m['wrong_report']+=origin!=g; m['false_confirmation']+=(a,g) not in valid
                if origin==g and (a,g) in valid: confirmed.add((a,g))
                l.update(stage=F,next=t); outcome='confirm'
            elif k==F and s and s['settled'] and s['id']==v:
                m['stale_release']+=origin!=s['origin']; m['unconfirmed_release']+=(a,s['origin']) not in confirmed
                sources[a]=None; outcome='release'
            log.append(['receive',list(token),origin,emitted,outcome])
        a=t%2; l=local[a]; s=sources[a]; token=None; origin=None
        if t%13==3 or (c['shock'] and t%17==6): token=(C,0,0); origin=0
        elif s and s['pending'] is not None:
            token=(s['pending'],a,s['id']); origin=s['origin']; s['pending']=None
        elif l['g']<16 and t>=l['next']:
            g=l['g']; v=g%modulus
            if l['start'] is None and t<last[a].get(v,-10000)+guard: m['wait']+=1
            else:
                if l['start'] is None: l['start']=t
                k=l['stage']; token=(k,a,v); origin=g; last[a][v]=t
                if k==F: l.update(g=g+1,stage=Q,start=None,next=t+2); m['release']+=1
                else: l['next']=t+6
        if token:
            k,a,v=token; decoded,w,hash_=acoustic(token)
            if audio: samples[t*SLOT:t*SLOT+len(w)]=w
            rng=random.Random(c['seed']*1000003+t*97+k*7+a)
            lost=c['channel'] in ('mixed','overrun') and rng.randrange(7)==0
            delays=[] if lost or k==C else [1]
            if delays and c['channel']!='clean':
                delays=[1+rng.randrange(min(D,3))]; delays.append(D+rng.randrange(1 if c['channel']!='overrun' else D*3+1))
            for d in delays: queue.append((t+d,decoded,origin,t))
            m['spent']+=k!=C; m['current']+=k==C; log.append(['send',list(token),origin,hash_,delays])
        m['peak_queue']=max(m['peak_queue'],len(queue)); assert len(queue)<=8*D+2
        trace.append(dict(t=t,events=log,local=[x.copy() for x in local],source=[x.copy() if x else None for x in sources],spent=m['spent']))
    m.update(settled=len(valid),confirmed=len(confirmed),finished=sum(x['g'] for x in local)); assert confirmed<=valid
    if p=='unique' or (p=='bounded' and c['channel']!='overrun'): assert not any(m[k] for k in BAD),(c,p,m)
    return dict(condition=c,policy=p,guard_slots=guard,metrics=m,trace=trace),samples

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=False); rows=[]; totals={}; witnesses={}; checks=0
    for seed,D,L,channel,shock in itertools.product(range(234001,234007),(4,12,36),(12,32),('clean','duplicate','mixed','overrun'),(False,True)):
        c=dict(seed=seed,delay=D,lifetime=L,channel=channel,shock=shock); group={}
        for p in POLICIES:
            r,_=simulate(c,p); m=r['metrics']; group[p]=m
            rows.append(dict(condition=c,policy=p,metrics=m,trace_sha256=digest(dump(r['trace']))))
            z=totals.setdefault(channel,{}).setdefault(p,dict.fromkeys(m,0))
            for k,v in m.items(): z[k]+=v
            pre,_=simulate(c,p,101); assert pre['trace']==r['trace'][:101]; checks+=1
            assert m['spent']==sum(e[0]=='send' and e[1][0]!=C for x in r['trace'] for e in x['events']); checks+=1
        if channel!='overrun' and any(group['none'][k] for k in BAD): witnesses.setdefault('reuse-failure',c)
        if channel!='overrun' and any(group['delay-only'][k] for k in BAD): witnesses.setdefault('delay-only-failure',c)
        if channel=='overrun' and any(group['bounded'][k] for k in BAD): witnesses.setdefault('contract-violation',c)
        if channel=='clean' and group['bounded']['wait']>0: witnesses.setdefault('quarantine-cost',c)
    examples={}
    for name,c in witnesses.items():
        examples[name]={}
        for p in POLICIES:
            r,w=simulate(c,p,audio=True); file=name+'-'+p+'.wav'; payload=struct.pack('<%dh'%len(w),*w)
            with wave.open(str(out/file),'wb') as f: f.setparams((1,2,RATE,0,'NONE','not compressed')); f.writeframes(payload)
            assert max(map(abs,w))<=1000; r.update(wav=file,pcm_sha256=digest(payload)); examples[name][p]=r
    receipt=dict(schema='interaction-456-reuse-v1',parent=PARENT,main=MAIN,slot_ms=200,body_ms=60,rate=RATE,horizon=H,checks=checks,conditions=len(rows)//4,totals=totals,rows=rows,examples=examples,limitations='Truthful endpoints; common clock; fixed hard source expiry never extended; bounded delivery after emission except overrun; origin audit only; 16 generations/address; no restarts, authentication, streaming or physical-channel claim. Peak queue aggregate is sum of per-run maxima.')
    (out/'receipt.json').write_bytes(dump(receipt))
    data=dump(examples).decode().replace('</','<\\/')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Identity reuse laboratory</title><style>body{font:16px system-ui;max-width:960px;margin:2em auto;padding:0 1em;background:#19212b;color:#eef3f8}select,button,input{font:inherit}pre{white-space:pre-wrap;background:#263545;padding:1em}audio{width:100%}</style><h1>Conversation identity quarantine</h1><p>Synthetic trace and emitted audio, not received overlapping sound. Start at low volume.</p><label>Case <select id="c"></select></label> <label>Policy <select id="p"></select></label><p><audio id="a" controls preload="none"></audio></p><label>Slot <input id="t" type="range" min="0" max="599" value="0"></label> <button id="next">Next event</button> <button id="prev">Previous event</button><pre id="m"></pre><pre id="s"></pre><script>const d=DATA,$=x=>document.getElementById(x);for(const k of Object.keys(d))$('c').add(new Option(k,k));for(const k of ['none','delay-only','bounded','unique'])$('p').add(new Option(k,k));const row=()=>d[$('c').value][$('p').value];function render(){const r=row();$('m').textContent=JSON.stringify({condition:r.condition,guard_slots:r.guard_slots,metrics:r.metrics},null,2);$('s').textContent=JSON.stringify(r.trace[+$('t').value],null,2)}function change(){const a=$('a');a.pause();a.src=row().wav;a.volume=.2;render()}$('c').onchange=$('p').onchange=change;$('t').oninput=render;for(const [id,dir] of [['next',1],['prev',-1]])$(id).onclick=()=>{let i=+$('t').value+dir;while(i>=0&&i<600&&!row().trace[i].events.length)i+=dir;if(i>=0&&i<600)$('t').value=i;render()};change()</script></html>'''.replace('DATA',data)
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_bytes(dump({x.name:digest(x.read_bytes()) for x in sorted(out.iterdir())}))
    print(json.dumps(dict(conditions=receipt['conditions'],checks=checks,totals=totals,witnesses=witnesses),indent=2))
if __name__=='__main__': run(sys.argv[1])
