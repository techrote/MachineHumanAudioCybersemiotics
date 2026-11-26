"""Interaction #456: shared repair budget, synthetic two-agent relay (GPT-6.2 assisted).
Predecessor 35565c92761a474247158a83acfc5ffc4409f4fc motivates this new model;
not a drop-in comparator for that single-stream experiment. No human evidence.
"""
import collections as C
import hashlib, json, math, pathlib, struct, sys, wave

D=(16,24); N=3; H=28; ACT_CAP=8; OUT_CAP=12
POLICIES=('round-robin','paced','earliest','status-gate','class-gate','class-fallback')
REGIMES=('clean','staggered','reverse','late','return-loss','mixed','permanent','bursty')
SEEDS=range(4563800,4563832)

def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def channel(seed,regime,kind,lane,t):
    # Exogenous matched conditions: independent of policy or number of sends.
    r=int(digest([seed,kind,lane,t])[:8],16)%100
    opening={'clean':(0,0),'staggered':(9,15),'reverse':(13,3),'late':(15,20),'return-loss':(4,8),'mixed':(3,7),'permanent':(99,4),'bursty':(2,2)}[regime][lane]
    if kind=='STATUS': return True  # separate diagnostic forward class
    if kind=='REPLY': return not (regime=='return-loss' and t<17 or regime=='mixed' and r<25)
    if t<opening: return False
    if regime=='mixed': return int(digest([seed,'data',lane,t])[:8],16)%100>=25
    if regime=='bursty': return (t+lane*3)%7<3
    return True  # ACT and CLASS share forward availability at a given slot

def run(seed,regime,policy):
    applied=[0,0]; known=[0,0]; fresh=[-99,-99]; last=[-99,-99]; probe=[-99,-99]
    queue=C.defaultdict(list); pending={}; trace=[]; acts=out=responses=0; turn=0
    def log(t,event,**kw): trace.append(dict(t=t,event=event,**kw))
    for t in range(H):
        for k,l,s,n,stamp in queue.pop(t,[]):
            log(t,'arrival',kind=k,lane=l,seq=s,nonce=n,stamp=stamp)
            if k=='REPLY':
                assert n in pending and pending[n][:2]==(l,s)
                sent_kind=pending.pop(n)[2]; known[l]=max(known[l],stamp)
                if sent_kind in ('CLASS','STATUS'): fresh[l]=n
                log(t,'evidence',lane=l,known=known[l],kind=sent_kind,nonce=n,sampled=t-1)
            else:
                if k=='ACT' and t<D[l] and s==applied[l]:
                    applied[l]+=1; log(t,'apply',lane=l,seq=s)
                responses+=1; ok=channel(seed,regime,'REPLY',l,t)
                log(t,'reply',lane=l,nonce=n,seq=s,prefix=applied[l],delivered=ok)
                if ok: queue[t+1].append(('REPLY',l,s,n,applied[l]))
        # Correlation is bounded by a two-slot transport model; expire lost requests.
        pending={n:v for n,v in pending.items() if t-n<2}
        eligible=[l for l in range(2) if t+1<D[l] and known[l]<N and t-last[l]>=2]
        if eligible and out<OUT_CAP and (policy!='paced' or t%3==0):
            gated=policy in ('status-gate','class-gate','class-fallback')
            ready=[l for l in eligible if not gated or t-fresh[l]<=4 or (policy=='class-fallback' and D[l]-t<=4)]
            ready=[l for l in ready if acts<ACT_CAP]
            if ready:
                l=min(ready,key=lambda l:(D[l],l)) if policy=='earliest' else min(ready,key=lambda l:(l-turn)%2)
                k='ACT'
            elif gated:
                candidates=[l for l in eligible if t-probe[l]>=3 and t-fresh[l]>4]
                l=min(candidates,key=lambda l:(l-turn)%2) if candidates else None
                k='STATUS' if policy=='status-gate' else 'CLASS'
            else: l=None; k='ACT'
            if l is not None:
                turn=1-l; s=known[l]; n=t; out+=1; last[l]=t
                if k=='ACT': acts+=1
                else: probe[l]=t
                pending[n]=(l,s,k); ok=channel(seed,regime,k,l,t)
                log(t,'send',kind=k,lane=l,seq=s,nonce=n,delivered=ok)
                if ok: queue[t+1].append((k,l,s,n,-1))
        assert all(0<=known[l]<=applied[l]<=N for l in range(2)) and len(pending)<=2
        log(t,'state',applied=applied[:],known=known[:],actions=acts,outbound=out)
    return dict(applied=sum(applied),known=sum(known),complete=sum(x==N for x in applied),confirmed=sum(x==N for x in known),actions=acts,outbound=out,responses=responses,unknown=sum(applied)-sum(known),lane0=applied[0],lane1=applied[1]),trace

def audit(trace,metrics):
    applied=[0,0]; known=[0,0]; sent={}; replies={}; accepted=set(); acts=0
    for x in trace:
        t=x['t']; e=x['event']; l=x.get('lane')
        if e=='send':
            assert t not in sent and x['seq']==known[l] and t+1<D[l]; sent[t]=x; acts+=x['kind']=='ACT'
        elif e=='apply':
            p=sent[t-1]; assert p['kind']=='ACT' and p['delivered'] and p['lane']==l and p['seq']==x['seq']==applied[l] and t<D[l]; applied[l]+=1
        elif e=='reply':
            p=sent[x['nonce']]; assert p['delivered'] and p['lane']==l and t==p['t']+1 and x['prefix']==applied[l]; replies[x['nonce']]=x
        elif e=='evidence':
            n=x['nonce']; p=replies[n]; assert n not in accepted and p['delivered'] and p['lane']==l and t==n+2 and x['kind']==sent[n]['kind']; accepted.add(n); known[l]=max(known[l],p['prefix']); assert x['known']==known[l]
        elif e=='state': assert x['applied']==applied and x['known']==known and x['actions']==acts and x['outbound']==len(sent)
    assert acts<=ACT_CAP and len(sent)<=OUT_CAP and metrics['applied']==sum(applied) and metrics['known']==sum(known) and metrics['responses']==len(replies)

def audio(path,trace):
    sr=8000; slot=1200; data=[0.0]*(H*slot)
    for x in trace:
        if x['event'] not in ('send','apply','evidence'): continue
        f=({'send':330,'apply':660,'evidence':495}[x['event']])*(1+x['lane']*.5)
        for i in range(600): data[x['t']*slot+i]+=.025*math.sin(2*math.pi*f*i/sr)*math.sin(math.pi*i/600)**2
    with wave.open(str(path),'wb') as w: w.setparams((1,2,sr,0,'NONE','not compressed')); w.writeframes(struct.pack('<%dh'%len(data),*(round(v*32767) for v in data)))

def main(out):
    out.mkdir(); rows=[]; traces={}; hashes=[]
    for r in REGIMES:
        for p in POLICIES:
            total=C.Counter()
            for s in SEEDS:
                m,tr=run(s,r,p); audit(tr,m); assert (m,tr)==run(s,r,p); total.update(m); hashes.append([r,p,s,digest(tr)])
                if s==SEEDS.start: traces[r+'/'+p]=tr
            rows.append(dict(regime=r,policy=p,**total))
    for p in POLICIES: assert run(SEEDS.start,'clean',p)[0]['applied']==6
    # A successful diagnostic probe does not establish action-class availability.
    assert channel(SEEDS.start,'permanent','STATUS',0,5) and not channel(SEEDS.start,'permanent','ACT',0,5)
    bad=json.loads(json.dumps(traces['clean/class-gate'])); next(x for x in bad if x['event']=='evidence')['known']=99
    try: audit(bad,run(SEEDS.start,'clean','class-gate')[0])
    except AssertionError: pass
    else: raise AssertionError('tamper accepted')
    receipt=dict(schema='mhac.interaction.shared-repair/1',predecessor='35565c92761a474247158a83acfc5ffc4409f4fc',seeds=list(SEEDS),deadlines=D,action_cap=ACT_CAP,outbound_cap=OUT_CAP,rows=rows,hashes=hashes,traces=traces)
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    names=[]
    for key in ('staggered/round-robin','staggered/status-gate','staggered/class-gate','return-loss/class-fallback'):
        name=key.replace('/','-')+'.wav'; audio(out/name,traces[key]); names.append(name)
    page='''<!doctype html><meta charset=utf-8><title>Shared repair</title><style>body{font:16px system-ui;max-width:850px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}select,input,button{font:inherit}progress{width:100%}</style><h1>Shared repair budget</h1><p>Two fictional agents, three ordered actions each. Deadlines 16 and 24 slots. Replay first seed; table totals across 32 seeds. Audio is an event rendering, not wire transport. Start playback at low gain.</p><label>Scenario <select id="scene"></select></label><label> Policy <select id="policy"></select></label><pre id="table"></pre><button id="prev">Previous</button><button id="next">Next</button><input id="slot" type="range" min="0" max="27" value="0"><p id="state"></p><label>Applied<progress id="applied" max="6"></progress></label><label>Known<progress id="known" max="6"></progress></label><pre id="events"></pre><button id="save">Export trace</button><div id="audio"></div><script>const data=RECEIPT,names=NAMES,e=id=>document.getElementById(id);function options(id,vs){for(const v of vs){const o=document.createElement('option');o.value=o.textContent=v;e(id).append(o)}}options('scene',[...new Set(data.rows.map(r=>r.regime))]);options('policy',[...new Set(data.rows.map(r=>r.policy))]);function trace(){return data.traces[e('scene').value+'/'+e('policy').value]}function render(){const t=+e('slot').value,x=trace().filter(x=>x.t===t),s=x.find(x=>x.event==='state');e('state').textContent='Slot '+t+' | applied '+s.applied+' | known '+s.known+' | ACT '+s.actions+'/8 | outbound '+s.outbound+'/12';e('applied').value=s.applied.reduce((a,b)=>a+b);e('known').value=s.known.reduce((a,b)=>a+b);e('events').textContent=JSON.stringify(x,null,2);e('table').textContent=data.rows.filter(r=>r.regime===e('scene').value).map(r=>r.policy+': applied '+r.applied+'/192; completed '+r.complete+'/64; outbound '+r.outbound).join('\\n')}e('scene').onchange=e('policy').onchange=e('slot').oninput=render;e('prev').onclick=()=>{e('slot').value=Math.max(0,+e('slot').value-1);render()};e('next').onclick=()=>{e('slot').value=Math.min(27,+e('slot').value+1);render()};e('save').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(trace())],{type:'application/json'}));a.href=u;a.download='trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};for(const n of names){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=n+' ';a.src=n;a.controls=true;a.volume=.2;a.preload='none';p.append(a);e('audio').append(p)}render();</script>'''
    (out/'index.html').write_text(page.replace('RECEIPT',json.dumps(receipt,separators=(',',':'))).replace('NAMES',json.dumps(names)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(rows,indent=2))

if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--scenario':
        r,p,s=sys.argv[2],sys.argv[3],int(sys.argv[4]); assert r in REGIMES and p in POLICIES; m,tr=run(s,r,p); audit(tr,m); print(json.dumps(dict(metrics=m,trace=tr),indent=2))
    else: main(pathlib.Path(sys.argv[1]))
