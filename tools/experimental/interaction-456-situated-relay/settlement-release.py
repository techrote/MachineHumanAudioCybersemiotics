"""Interaction #456: explicit forgetting, duplicate reports/releases and bounded epochs.
Synthetic only; standalone Python 3.11+; python settlement-release.py NEW_OUTPUT.
"""
import hashlib, itertools, json, math, random, struct, sys, wave
from functools import lru_cache
from pathlib import Path

PARENT='6ccb0e76362b7dc249b8bcdfe9aa95cd2a767eeb'
MAIN='495a98ca12bae467a507031f04931aa4254b1866'
H,RATE,SLOT,N=200,8000,1600,160
QUERY,EVIDENCE,ACK,REPORT,RELEASE,CURRENT=range(6)
NAMES=('query','evidence','ack','report','release','current')
POLICIES=('ttl','unbound','epoch2','full')
BANK=tuple(tuple(math.sin(2*math.pi*(400+100*k)*j/RATE) for j in range(N)) for k in range(16))
sha=lambda b:hashlib.sha256(b).hexdigest()
@lru_cache(None)
def acoustic(token):
    w=tuple(round(1000*x) for k in token for x in BANK[k]); result=[]
    for i in range(3):
        segment=w[i*N:(i+1)*N]; scores=[abs(sum(x*y for x,y in zip(segment,b))) for b in BANK]
        k=max(range(16),key=scores.__getitem__); assert scores[k]>30000 and scores[k]>4*max(scores[:k]+scores[k+1:]); result.append(k)
    assert tuple(result)==token
    return tuple(result),sha(struct.pack('<%dh'%len(w),*w)),w

def wire(policy,k,g):
    return (0 if policy=='unbound' else g%2 if policy=='epoch2' else g) if k in (REPORT,RELEASE) else g

def simulate(c,policy,horizon=H,audio=False):
    # Truth metadata travels only in the simulator's audit envelope, never to a protocol decision.
    local=[dict(g=0,stage='query',next=0) for _ in range(2)]; source=[None,None]; queue=[]; truth=set(); confirmed=set(); events=[]
    m=dict(spent=0,queries=0,busy=0,evidence=0,settled=0,confirmed=0,false_confirmation=0,wrong_report=0,releases=0,stale_release=0,premature_release=0,expired=0,forgotten=0,ignored=0,peak_queue=0)
    samples=[0]*(SLOT*horizon) if audio else None
    for t in range(horizon):
        log=[]
        for a,s in enumerate(source):
            if s and t>=s['until']:
                m['forgotten' if s['settled'] else 'expired']+=1; source[a]=None; log.append(['expiry',a,s['g']])
        due=[p for p in queue if p[0]==t]; queue=[p for p in queue if p[0]!=t]
        for _,token,origin,emitted in due:
            k,a,v=token; l=local[a]; s=source[a]; outcome='ignored'
            if k==QUERY:
                if s is None:
                    source[a]=dict(g=v,settled=False,until=t+24,pending=EVIDENCE); outcome='admitted'
                elif s['g']==v and not s['settled']:
                    s['pending']=EVIDENCE; outcome='repeat-evidence'
                else: m['busy']+=1; outcome='busy'
            elif k==EVIDENCE and l['stage']=='query' and l['g']==v:
                l.update(stage='ack',next=t); m['evidence']+=1; outcome='evidence'
            elif k==ACK and s and s['g']==v:
                if not s['settled']:
                    s.update(settled=True,until=t+c['retention']); truth.add((a,v)); m['settled']=len(truth)
                s['pending']=REPORT; outcome='settled'
            elif k==REPORT and l['stage']=='ack' and v==wire(policy,k,l['g']):
                g=l['g']; m['wrong_report']+=int(origin!=g); m['false_confirmation']+=int((a,g) not in truth)
                if (a,g) in truth and origin==g: confirmed.add((a,g))
                m['confirmed']=len(confirmed); outcome='confirm'
                if policy=='ttl': l.update(g=g+1,stage='query',next=t)
                else: l.update(stage='release',next=t)
            elif k==RELEASE and s and s['settled'] and v==wire(policy,k,s['g']):
                m['stale_release']+=int(origin!=s['g']); m['premature_release']+=int((a,s['g']) not in confirmed)
                source[a]=None; outcome='released'
            if outcome=='ignored': m['ignored']+=1
            log.append(['receive',list(token),origin,emitted,outcome])
        a=t%2; l=local[a]; s=source[a]; token=None; origin=None
        if t%13==3 or (c['shock'] and t%17==6): token=(CURRENT,0,0); origin=0
        elif s and s['pending'] is not None:
            k=s['pending']; s['pending']=None; origin=s['g']; token=(k,a,wire(policy,k,origin))
        elif l['g']<6 and t>=l['next']:
            k={'query':QUERY,'ack':ACK,'release':RELEASE}[l['stage']]; origin=l['g']; token=(k,a,wire(policy,k,origin))
            if k==RELEASE: l.update(g=origin+1,stage='query',next=t+2); m['releases']+=1
            else: l['next']=t+6; m['queries']+=int(k==QUERY)
        if token:
            k,a,v=token; decoded,digest,w=acoustic(token)
            if audio: samples[t*SLOT:t*SLOT+len(w)]=w
            rng=random.Random(c['seed']*1000003+t*97+k*7+a); lost=c['channel']=='mixed' and rng.randrange(5)==0 and k!=CURRENT
            delays=[] if lost or k==CURRENT else [1]
            if delays and k in (REPORT,RELEASE) and c['channel']!='clean':
                if c['channel']=='mixed': delays=[1+rng.randrange(5)]
                delays.append((12 if c['channel']=='short' else 36 if c['channel']=='long' else 72)+rng.randrange(4))
            for d in delays: queue.append((t+d,decoded,origin,t))
            m['spent']+=int(k!=CURRENT); log.append(['send',list(token),origin,digest,delays])
        m['peak_queue']=max(m['peak_queue'],len(queue)); assert len(queue)<=76 and all(s is None or 0<=s['g']<6 for s in source)
        events.append(dict(t=t,events=log,local=[l.copy() for l in local],source=[s.copy() if s else None for s in source],spent=m['spent']))
    assert m['confirmed']<=m['settled']<=12 and m['false_confirmation']<=m['wrong_report']
    if policy in ('ttl','full'): assert m['wrong_report']==m['stale_release']==m['premature_release']==0
    return dict(condition=c,policy=policy,metrics=m,trace=events),samples

def conditions():
    for seed,retention,channel,shock in itertools.product(range(233001,233009),(12,24,48),('clean','short','long','mixed'),(False,True)):
        yield dict(seed=seed,retention=retention,channel=channel,shock=shock)

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=False); rows=[]; stats={}; witnesses={}; pairs=dict(equal_airtime=0,full_more=0,ttl_more=0,tied=0); checks=0
    for c in conditions():
        group={}
        for p in POLICIES:
            r,_=simulate(c,p); m=r['metrics']; group[p]=m; rows.append(dict(condition=c,policy=p,metrics=m,trace_sha256=sha(json.dumps(r['trace'],sort_keys=True).encode())))
            for scope in ('all',c['channel']):
                z=stats.setdefault(scope,{}).setdefault(p,{}); z.update({k:z.get(k,0)+v for k,v in m.items()})
            cut=81; prefix,_=simulate(c,p,cut); assert prefix['trace']==r['trace'][:cut]; checks+=1
            assert m['spent']==sum(e[0]=='send' and e[1][0]!=CURRENT for x in r['trace'] for e in x['events']); checks+=1
        f,b=group['full'],group['ttl']
        if f['spent']==b['spent']:
            pairs['equal_airtime']+=1; pairs['full_more' if f['confirmed']>b['confirmed'] else 'ttl_more' if f['confirmed']<b['confirmed'] else 'tied']+=1
        if f['confirmed']>b['confirmed']: witnesses.setdefault('admission-gain',c)
        if f['confirmed']<b['confirmed']: witnesses.setdefault('release-cost',c)
        if group['unbound']['false_confirmation']: witnesses.setdefault('stale-report',c)
        if group['epoch2']['stale_release']: witnesses.setdefault('epoch-wrap-release',c)
        if group['epoch2']['false_confirmation']: witnesses.setdefault('epoch-wrap-report',c)
    examples={}
    for name,c in witnesses.items():
        examples[name]={}
        for p in POLICIES:
            r,w=simulate(c,p,audio=True); file=name+'-'+p+'.wav'; payload=struct.pack('<%dh'%len(w),*w)
            with wave.open(str(out/file),'wb') as f: f.setparams((1,2,RATE,0,'NONE','not compressed')); f.writeframes(payload)
            assert max(map(abs,w))<=1000; r.update(wav=file,pcm_sha256=sha(payload)); examples[name][p]=r
    receipt=dict(schema='interaction-456-release-v1',parent=PARENT,main=MAIN,slot_ms=200,body_ms=60,rate=RATE,horizon=H,conditions=len(rows)//4,checks=checks,stats=stats,pairs=pairs,rows=rows,examples=examples,limitations='Central scheduler, trusted endpoints, aligned PCM, delay/duplication after extraction, no insertion/substitution, generations 0..5 per address; no epoch wrap in full policy. Expiry is a fallback, not proof of release.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':')),encoding='utf-8')
    data=json.dumps(examples,separators=(',',':')).replace('</','<\\/')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Settlement release laboratory</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto;padding:0 1em;background:#161c25;color:#e6edf5}select,input,button{font:inherit}pre{white-space:pre-wrap;background:#232e3b;padding:1em}audio{width:100%}</style><h1>Negotiated forgetting</h1><p>Synthetic dialogue; emitted PCM only. Delayed copies are modeled after extraction, not overlapping physical sound. Start with low output volume.</p><label>Witness <select id="case"></select></label> <label>Policy <select id="policy"></select></label><p><audio id="audio" controls preload="none"></audio></p><label>Slot <input id="slot" type="range" min="0" max="199" value="0"></label> <button id="prev">Previous event</button> <button id="next">Next event</button><pre id="metrics"></pre><pre id="state"></pre><script>const data=DATA;const $=id=>document.getElementById(id);for(const k of Object.keys(data))$('case').add(new Option(k,k));for(const k of ['ttl','unbound','epoch2','full'])$('policy').add(new Option(k,k));const row=()=>data[$('case').value][$('policy').value];function render(){const r=row();$('metrics').textContent=JSON.stringify(r.metrics,null,2);$('state').textContent=JSON.stringify(r.trace[+$('slot').value],null,2)}function change(){const a=$('audio');a.pause();a.src=row().wav;a.volume=.2;render()}for(const id of ['case','policy'])$(id).onchange=change;$('slot').oninput=render;for(const [id,dir] of [['prev',-1],['next',1]])$(id).onclick=()=>{let i=+$('slot').value+dir;while(i>=0&&i<200&&!row().trace[i].events.length)i+=dir;if(i>=0&&i<200)$('slot').value=i;render()};change()</script></html>'''.replace('DATA',data)
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},sort_keys=True),encoding='utf-8')
    print(json.dumps(dict(conditions=receipt['conditions'],checks=checks,stats=stats,pairs=pairs,witnesses=witnesses),indent=2))

if __name__=='__main__': run(sys.argv[1])
