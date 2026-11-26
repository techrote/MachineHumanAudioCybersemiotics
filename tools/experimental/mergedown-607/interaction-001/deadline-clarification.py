"""MHAC #456: deadline-conditioned repair, synthetic symbolic transport.
GPT-6.2 assisted, 2026-11-26. No human or physical channel evidence.
"""
import collections as C
import hashlib, importlib.util, json, pathlib, sys

PIN='c391e0c5bd1cfe6a8c5e44c05decb83849ad153d'
SHA='ac8021e147b9b937e01b7a4b9b535f136a5642ae367d9555713aa98eb29f7a39'
p=pathlib.Path(__file__).with_name('live-clarification.py')
if hashlib.sha256(p.read_bytes()).hexdigest()!=SHA:
    raise ValueError('pinned source mismatch')
spec=importlib.util.spec_from_file_location('live',p)
live=importlib.util.module_from_spec(spec); spec.loader.exec_module(live)
N,W,D,T=live.N,live.W,live.D,live.T
POLICIES=('baseline','priority','bound','bound-priority')
REGIMES=live.REGIMES+('forward-edge','forward-late','delayed-status','duplicate-status')
SEEDS=range(4563600,4563632)
TTL=8

def run(seed,regime,policy):
    q=C.defaultdict(list); tr=[]; c=C.Counter(); effects=set()
    bound=policy.startswith('bound'); priority=policy.endswith('priority')
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
        if k=='STATUS' and regime=='delayed-status': delay=12
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
                if age-pending[nonce]>TTL: del pending[nonce]
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
                    if bound and (nonce not in pending or not pending[nonce]<=stamp<=age):
                        c['status-rejected']+=1; log(t,'status-reject',nonce=nonce); continue
                    pending.pop(nonce,None); c['status-accepted']+=1
                    log(t,'status-accept',nonce=nonce,stamp=stamp,seq=s)
                assert -1<=s<issued and 0<=stamp<=age
                if s>ack: ack=s; log(t,'receipt',ack=ack)
                i=ack+1
                if k=='STATUS' and age<D and s==ack and i<issued and attempts[i]==4 and stamp>=due[i]-8 and i not in credits:
                    credits.add(i); c['repair-credit']+=1; log(t,'credit',seq=i,stamp=stamp,nonce=nonce)
                    if priority: due[i]=age
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

def audit(tr,bound):
    live.audit(tr)
    for e in (1,2):
        queries={}; accepted=set(); statuses=set(); effects=0; sends=C.Counter(); credits=set()
        for x in (x for x in tr if x['t']//T+1==e):
            age=x['t']%T; event=x['event']
            if event=='apply': effects+=1
            elif event=='send':
                if x['kind']=='QUERY':
                    assert x['nonce']==age and age not in queries; queries[age]=age
                elif x['kind']=='STATUS':
                    assert x['seq']==effects-1; statuses.add((x['nonce'],x['stamp'],x['seq']))
                elif x['kind']=='ACT': sends[x['seq']]+=1
            elif event=='credit': credits.add(x['seq'])
            elif event=='status-accept':
                n=x['nonce']; assert (n,x['stamp'],x['seq']) in statuses
                if bound: assert n in queries and n not in accepted and n<=x['stamp']<=age<=n+TTL
                accepted.add(n)
        assert all(v<=4+int(i in credits) for i,v in sends.items())
    return 2

def main(out):
    out.mkdir(parents=True,exist_ok=False); totals={}; hashes=[]; witnesses={}; checked=audited=0
    for r in REGIMES:
        totals[r]={}
        for policy in POLICIES:
            total=C.Counter()
            for seed in SEEDS:
                c,tr=run(seed,r,policy); audited+=audit(tr,policy.startswith('bound')); total.update(c)
                if policy=='baseline' and r in live.REGIMES:
                    old,oldtr=live.run(seed,r,'live-repair')
                    assert {k:v for k,v in c.items() if not k.startswith('status-')}==old
                    assert [{k:v for k,v in x.items() if k!='nonce'} for x in tr if not x['event'].startswith('status-')]==oldtr
                    checked+=1
                hashes.append([seed,r,policy,live.parent.digest(tr)])
                if seed==SEEDS.start: witnesses[r+'/'+policy]=tr
            totals[r][policy]=dict(total)
    assert totals['forward-restored']['bound-priority']['confirmed']==64
    assert totals['forward-edge']['bound-priority']['applied']==0<totals['forward-edge']['baseline']['applied']
    assert totals['delayed-status']['bound']['status-rejected']>0
    assert totals['duplicate-status']['bound']['applied']==totals['duplicate-status']['baseline']['applied']
    receipt=dict(pin=PIN,source_sha256=SHA,seeds=list(SEEDS),ttl=TTL,deadline=D,epoch_slots=T,comparator_checks=checked,audited_epochs=audited,totals=totals,hashes=hashes,witnesses=witnesses)
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    audio=[]
    for r,pol in [('forward-restored','baseline'),('forward-restored','bound-priority'),('delayed-status','baseline'),('delayed-status','bound-priority')]:
        name=r+'-'+pol+'.wav'; live.parent.audio(out/name,witnesses[r+'/'+pol]); audio.append(name)
    page='''<!doctype html><meta charset=utf-8><title>Deadline clarification</title><style>body{font:16px system-ui;max-width:850px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}input,progress{width:100%}button,select{font:inherit}</style><h1>Deadline clarification</h1><p>Fictional ordered tile actions. Applied is ground truth, known is received evidence. Slot 48 ends execution. Status expiry 8 slots for bound policies. Audio is event sonification, not wire encoding.</p><select id="case"></select><button id="prev">Previous</button><button id="next">Next</button><input id="slot" type="range" min="0" max="159" value="0"><p id="summary"></p><label>Applied <progress id="applied" max="8"></progress></label><label>Known <progress id="known" max="8"></progress></label><pre id="events"></pre><button id="export">Export trace</button><h2>Matched audio specimens</h2><div id="audio"></div><script>const traces=DATA,el=id=>document.getElementById(id);for(const k of Object.keys(traces)){const o=document.createElement('option');o.value=o.textContent=k;el('case').append(o)}function render(){const t=+el('slot').value,rows=traces[el('case').value].filter(x=>x.t===t),s=rows.find(x=>x.event==='state');el('summary').textContent='Epoch '+s.epoch+' | age '+s.age+' | issued '+s.issued+' | applied '+s.applied+' | known '+s.known+' | final '+(s.final===null?'unknown':s.final+1);el('applied').value=s.applied;el('known').value=s.known;el('events').textContent=JSON.stringify(rows,null,2)}el('case').onchange=el('slot').oninput=render;el('prev').onclick=()=>{el('slot').value=Math.max(0,+el('slot').value-1);render()};el('next').onclick=()=>{el('slot').value=Math.min(159,+el('slot').value+1);render()};el('export').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(traces[el('case').value])],{type:'application/json'}));a.href=u;a.download='trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};for(const name of AUDIO){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=name+' ';a.src=name;a.controls=true;a.volume=.2;a.preload='none';p.append(a);el('audio').append(p)}render();</script>'''
    (out/'index.html').write_text(page.replace('DATA',json.dumps(witnesses,separators=(',',':'))).replace('AUDIO',json.dumps(audio)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(totals,indent=2))

if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--scenario':
        r,policy,seed=sys.argv[2],sys.argv[3],int(sys.argv[4])
        if r not in REGIMES or policy not in POLICIES: raise ValueError('unknown scenario or policy')
        c,tr=run(seed,r,policy); audit(tr,policy.startswith('bound')); print(json.dumps(dict(metrics=c,trace=tr),indent=2))
    else: main(pathlib.Path(sys.argv[1]))
