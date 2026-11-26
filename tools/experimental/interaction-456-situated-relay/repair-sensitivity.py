"""MHAC #456: repair timing and purpose-specific expiry, synthetic symbolic transport.
GPT-6.2 assisted, 2026-11-26. No human or physical channel evidence.
"""
import collections as C
import hashlib, importlib.util, json, pathlib, sys

PIN='ec305bf677fb5c0c778dd6f3967c5bf4ed88fb01'
DEADLINE_SHA='4f42b16d3056223967a83047374d3dfb652095db64234368aad51575a3a5f6b2'
if hashlib.sha256(pathlib.Path(__file__).with_name('deadline-clarification.py').read_bytes()).hexdigest()!=DEADLINE_SHA:
    raise ValueError('pinned deadline source mismatch')
SHA='ac8021e147b9b937e01b7a4b9b535f136a5642ae367d9555713aa98eb29f7a39'
p=pathlib.Path(__file__).with_name('live-clarification.py')
if hashlib.sha256(p.read_bytes()).hexdigest()!=SHA:
    raise ValueError('pinned source mismatch')
spec=importlib.util.spec_from_file_location('live',p)
live=importlib.util.module_from_spec(spec); spec.loader.exec_module(live)
N,W,D,T=live.N,live.W,live.D,live.T
POLICIES=('baseline','priority','bound','bound-priority','hold3','hold6','split','split-priority')
REGIMES=live.REGIMES+('forward-edge','forward-late','delayed-status','duplicate-status')
SEEDS=range(4563700,4563732)
TTL=8
SETTLE_TTL=20

def run(seed,regime,policy,restore=None,status_delay=None):
    q=C.defaultdict(list); tr=[]; c=C.Counter(); effects=set()
    split=policy.startswith('split')
    bound=policy.startswith(('bound','hold','split')); priority=policy.endswith('priority') or policy.startswith('hold')
    holdoff={'hold3':3,'hold6':6}.get(policy,0)
    def log(t,event,**kw): tr.append(dict(t=t,event=event,**kw))
    def send(t,k,e,s,stamp=-1,nonce=-1):
        age=t%T; c[k+'-sent']+=1
        if k=='QUERY': nonce=age; pending[nonce]=age
        h=int(live.parent.digest([seed,t,k,e,s,stamp])[:8],16)
        delay=1+h%4 if regime=='mixed' else 1
        if regime=='mixed' and h%5==0: delay=0
        if k=='ACT' and s==1 and ((regime=='mixed' and age<10) or regime=='permanent-gap'): delay=0
        if k=='ACT' and ((regime in ('forward-restored','delayed-status','duplicate-status') and age<25) or (regime=='forward-edge' and age<29) or (regime=='forward-late' and age<33)): delay=0
        if k in ('ACK','STATUS') and (regime=='return-blackout' or regime=='return-restored' and age<25 or regime=='late-return' and age<55): delay=0
        if k=='ACT' and regime=='sweep' and age<restore: delay=0
        if k=='ACT' and regime=='latency' and age<25: delay=0
        if k=='STATUS' and regime=='delayed-status': delay=12
        if k=='STATUS' and regime=='latency': delay=status_delay
        log(t,'send',kind=k,epoch=e,seq=s,stamp=stamp,nonce=nonce,delay=delay)
        if delay:
            msg=(k,e,s,stamp,nonce); q[t+delay].append(msg)
            if k=='STATUS' and regime=='duplicate-status': q[t+delay+3].append(msg)
    for t in range(2*T):
        e=t//T+1; age=t%T
        if age==0:
            floor=ack=-1; issued=0; buf=set(); attempts=[0]*N; due=[0]*N; final=None
            next_probe=probes=0; credits=set(); pending={}; log(t,'epoch',epoch=e)
        if bound:
            for nonce in list(pending):
                if age-pending[nonce]>(SETTLE_TTL if split else TTL): del pending[nonce]
        if regime=='stale-status' and e==2 and age in (3,55): q[t].append(('STATUS',1,7,79,-1))
        for k,ep,s,stamp,nonce in q.pop(t,[]):
            log(t,'arrival',kind=k,epoch=ep,seq=s,stamp=stamp,nonce=nonce)
            if ep!=e:
                c['stale-rejected']+=1; continue
            if k=='ACT':
                if age>=D: c['expired-arrival']+=1
                elif s<=floor or s in buf: c['duplicate']+=1
                elif s>floor+W: c['outside-window']+=1
                else:
                    buf.add(s)
                    while floor+1 in buf:
                        floor+=1; buf.remove(floor); assert (e,floor) not in effects
                        effects.add((e,floor)); log(t,'apply',epoch=e,seq=floor)
                send(t,'ACK',e,floor,age)
            elif k=='QUERY': send(t,'STATUS',e,floor,age,nonce)
            else:
                if k=='STATUS':
                    if bound and (nonce not in pending or not pending[nonce]<=stamp<=age or age-nonce>(SETTLE_TTL if split and stamp>=D else TTL)):
                        c['status-rejected']+=1; log(t,'status-reject',nonce=nonce); continue
                    pending.pop(nonce,None); c['status-accepted']+=1
                    log(t,'status-accept',nonce=nonce,stamp=stamp,seq=s)
                assert -1<=s<issued and 0<=stamp<=age
                if s>ack: ack=s; log(t,'receipt',ack=ack)
                i=ack+1
                if k=='STATUS' and age<D and s==ack and i<issued and attempts[i]==4 and stamp>=due[i]-8 and i not in credits:
                    credits.add(i); c['repair-credit']+=1; log(t,'credit',seq=i,stamp=stamp,nonce=nonce)
                    if priority: due[i]=age+holdoff
                if k=='STATUS' and stamp>=D:
                    final=s; log(t,'settled',prefix=s)
        if age<D:
            i=ack+1
            urgent=priority and i<issued and i in credits and attempts[i]==4 and age>=due[i]
            if urgent: s=i
            elif issued<N and issued-ack<=W: s=issued; issued+=1
            else:
                eligible=[j for j in range(ack+1,issued) if attempts[j]<4+int(j in credits) and age>=due[j]]
                s=min(eligible,key=lambda j:(attempts[j],j)) if eligible else None
            if s is not None:
                send(t,'ACT',e,s); attempts[s]+=1; due[s]=age+2**attempts[s]
            elif ack+1<issued and attempts[ack+1]>=4 and age>=next_probe and probes<6:
                send(t,'QUERY',e,-1); c['live-query']+=1; probes+=1; next_probe=age+6
        elif ack<N-1 and final is None and (age-D)%8==0: send(t,'QUERY',e,-1)
        assert len(buf)<=W and ack<=floor and probes<=6 and issued-ack-1<=W
        if bound: assert len(pending)<=5
        assert all(a<=4+int(i in credits) for i,a in enumerate(attempts))
        if age==T-1:
            c['complete']+=int(floor==N-1); c['confirmed']+=int(ack==N-1)
            c['settled-incomplete']+=int(final is not None and final<N-1)
            c['unknown-issued']+=0 if final is not None else issued-ack-1
            c['not-issued']+=N-issued; c['known-applied']+=ack+1
            c['unknown-epochs']+=int(ack<N-1 and final is None and issued>ack+1)
            assert final is None or final==floor
        log(t,'state',epoch=e,age=age,applied=floor+1,known=ack+1,issued=issued,buffer=sorted(buf),final=final)
    c['applied']=len(effects); c['missing']=2*N-len(effects)
    return dict(c),tr

def audit(tr,policy):
    live.audit(tr)
    bound=policy.startswith(('bound','hold','split')); split=policy.startswith('split')
    for e in (1,2):
        queries=set(); accepted=set(); statuses=set(); effects=0; sends=C.Counter(); credits=set(); admissions=[]
        for x in (x for x in tr if x['t']//T+1==e):
            age=x['t']%T; event=x['event']
            if event=='apply': effects+=1
            elif event=='send':
                if x['kind']=='QUERY':
                    assert x['nonce']==age and age not in queries; queries.add(age)
                elif x['kind']=='STATUS':
                    assert x['seq']==effects-1; statuses.add((x['nonce'],x['stamp'],x['seq']))
                elif x['kind']=='ACT': sends[x['seq']]+=1
            elif event=='credit':
                assert x['seq'] not in credits and sends[x['seq']]==4
                assert any(t==age and stamp<D for t,stamp,s in admissions if s==x['seq']-1)
                credits.add(x['seq'])
            elif event=='status-accept':
                n=x['nonce']; stamp=x['stamp']; s=x['seq']
                assert (n,stamp,s) in statuses
                if bound: assert n in queries and n not in accepted and n<=stamp<=age<=n+(SETTLE_TTL if split and stamp>=D else TTL)
                accepted.add(n); admissions.append((age,stamp,s))
            elif event=='settled':
                assert any(t==age and stamp>=D and s==x['prefix'] for t,stamp,s in admissions)
                assert x['prefix']==effects-1
        assert all(v<=4+int(i in credits) for i,v in sends.items())
    return 2

METRICS=('applied','confirmed','settled-incomplete','unknown-issued','ACT-sent','QUERY-sent','status-rejected','repair-credit')
TIMING=('bound','bound-priority','hold3','hold6')
EXPIRY=('bound','split','bound-priority','split-priority')

def main(out):
    out.mkdir(parents=True,exist_ok=False); rows=[]; traces={}; hashes=[]; audited=0; comparisons=0
    spec=importlib.util.spec_from_file_location('deadline',pathlib.Path(__file__).with_name('deadline-clarification.py'))
    old=importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    for r in REGIMES:
        for policy in old.POLICIES:
            for seed in range(SEEDS.start,SEEDS.start+8):
                c,tr=run(seed,r,policy)
                assert (c,tr)==old.run(seed,r,policy); comparisons+=1
    def collect(regime,param,policies,seeds,**kwargs):
        nonlocal audited
        for policy in policies:
            total=C.Counter()
            for seed in seeds:
                c,tr=run(seed,regime,policy,**kwargs); audited+=audit(tr,policy); total.update(c)
                hashes.append([regime,param,policy,seed,live.parent.digest(tr)])
                if seed==SEEDS.start: traces[f'{regime}/{param}/{policy}']=tr
            rows.append(dict(regime=regime,param=param,policy=policy,epochs=2*len(seeds),**{k:total[k] for k in METRICS}))
    # Deterministic sweeps are a complete parameter grid, not independent random samples.
    for restore in range(20,39): collect('sweep',restore,TIMING,[SEEDS.start],restore=restore)
    for delay in range(1,25): collect('latency',delay,EXPIRY,[SEEDS.start],status_delay=delay)
    for r in ('clean','mixed','return-blackout','permanent-gap','duplicate-status','stale-status'):
        collect(r,0,('bound','bound-priority','hold3','hold6','split','split-priority'),SEEDS)
    def lookup(r,p,pol): return next(x for x in rows if (x['regime'],x['param'],x['policy'])==(r,p,pol))
    assert lookup('sweep',25,'bound-priority')['applied']==16
    assert lookup('sweep',29,'bound-priority')['applied']==0
    assert lookup('sweep',29,'bound')['applied']==10
    for d in range(1,25):
        for a,b in [('bound','split'),('bound-priority','split-priority')]:
            # Longer settlement TTL cannot change predeadline action execution.
            assert lookup('latency',d,a)['applied']==lookup('latency',d,b)['applied']
    assert lookup('latency',12,'split')['settled-incomplete']>lookup('latency',12,'bound')['settled-incomplete']
    receipt=dict(schema='mhac.interaction.repair-sensitivity/1',pin=PIN,deadline_sha256=DEADLINE_SHA,seeds=list(SEEDS),deadline=D,epoch_slots=T,prospective_ttl=TTL,settlement_ttl=SETTLE_TTL,comparator_checks=comparisons,audited_epochs=audited,rows=rows,hashes=hashes,witnesses=traces)
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    audio=[]
    for key in ('sweep/29/bound','sweep/29/bound-priority','sweep/29/hold3','latency/12/bound','latency/12/split'):
        name=key.replace('/','-')+'.wav'; live.parent.audio(out/name,traces[key]); audio.append(name)
    page='''<!doctype html><meta charset=utf-8><title>Repair sensitivity</title><style>body{font:16px system-ui;max-width:900px;margin:2em auto;padding:1em}select,button,input{font:inherit}pre{white-space:pre-wrap}input,progress{width:100%}td,th{padding:.3em;text-align:right}td:first-child,th:first-child{text-align:left}</style><h1>Repair sensitivity</h1><p>Synthetic ordered actions; slot 48 ends execution. Choose a recovery time or status delay and compare policies. Audio is event sonification, not wire encoding. Applied is ground truth, known is sender evidence.</p><label>Scenario <select id="scenario"></select></label> <label>Policy <select id="policy"></select></label><table><thead><tr><th>Policy</th><th>Applied</th><th>Confirmed epochs</th><th>Settled incomplete</th><th>ACT</th><th>QUERY</th></tr></thead><tbody id="table"></tbody></table><p>Table aggregates all seeds; replay shows first seed only.</p><button id="prev">Previous</button> <button id="next">Next</button><input id="slot" type="range" min="0" max="159" value="0"><p id="summary"></p><label>Applied <progress id="applied" max="8"></progress></label><label>Known <progress id="known" max="8"></progress></label><pre id="events"></pre><button id="export">Export trace</button><h2>Audio specimens (opt-in)</h2><div id="audio"></div><script>const traces=TRACE_DATA,rows=ROW_DATA,el=id=>document.getElementById(id);function options(id,values){el(id).replaceChildren();for(const v of values){const o=document.createElement('option');o.value=o.textContent=v;el(id).append(o)}}options('scenario',[...new Set(rows.map(r=>r.regime+'/'+r.param))]);function key(){return el('scenario').value+'/'+el('policy').value}function choose(){const subset=rows.filter(r=>r.regime+'/'+r.param===el('scenario').value);options('policy',subset.map(r=>r.policy));el('table').replaceChildren();for(const r of subset){const tr=document.createElement('tr');for(const v of [r.policy,r.applied+'/'+(r.epochs*8),r.confirmed+'/'+r.epochs,r['settled-incomplete'],r['ACT-sent'],r['QUERY-sent']]){const td=document.createElement('td');td.textContent=v;tr.append(td)}el('table').append(tr)}render()}function render(){const t=+el('slot').value,events=traces[key()].filter(x=>x.t===t),s=events.find(x=>x.event==='state');el('summary').textContent='Epoch '+s.epoch+' | slot '+s.age+' | issued '+s.issued+' | applied '+s.applied+' | known '+s.known+' | final '+(s.final===null?'unknown':s.final+1);el('applied').value=s.applied;el('known').value=s.known;el('events').textContent=JSON.stringify(events,null,2)}el('scenario').onchange=choose;el('policy').onchange=el('slot').oninput=render;el('prev').onclick=()=>{el('slot').value=Math.max(0,+el('slot').value-1);render()};el('next').onclick=()=>{el('slot').value=Math.min(159,+el('slot').value+1);render()};el('export').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(traces[key()])],{type:'application/json'}));a.href=u;a.download='trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};for(const name of AUDIO_DATA){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=name+' ';a.src=name;a.controls=true;a.volume=.2;a.preload='none';p.append(a);el('audio').append(p)}choose();</script>'''
    (out/'index.html').write_text(page.replace('TRACE_DATA',json.dumps(traces,separators=(',',':'))).replace('ROW_DATA',json.dumps(rows)).replace('AUDIO_DATA',json.dumps(audio)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(dict(rows=len(rows),runs=len(hashes),audited_epochs=audited,comparator_checks=comparisons)))

if __name__=='__main__':
    if len(sys.argv)==6 and sys.argv[1]=='--scenario':
        r,parameter,policy,seed=sys.argv[2],int(sys.argv[3]),sys.argv[4],int(sys.argv[5])
        if r not in REGIMES+('sweep','latency') or policy not in POLICIES: raise ValueError('unknown scenario or policy')
        if r=='sweep' and not 0<=parameter<=D or r=='latency' and not 1<=parameter<=24: raise ValueError('parameter outside range')
        c,tr=run(seed,r,policy,restore=parameter,status_delay=parameter); audit(tr,policy); print(json.dumps(dict(metrics=c,trace=tr),indent=2))
    else: main(pathlib.Path(sys.argv[1]))
