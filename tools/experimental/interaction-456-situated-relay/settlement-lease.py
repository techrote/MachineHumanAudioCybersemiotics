"""Interaction #456 / #457: bounded deferred receipt leases, synthetic only.
Run: python settlement-lease.py NEW_OUTPUT (Python 3.11+, stdlib). No human evidence.
"""
import itertools, json, math, random, struct, sys, wave, hashlib
from functools import lru_cache
from pathlib import Path

PARENT='76e792a223c87d2d5827268d493cce6bb9515c6e'
MAIN='495a98ca12bae467a507031f04931aa4254b1866'
POLICIES=('immediate','defer-local','defer-contract')
H,RATE,SLOT,N=16,8000,1600,320
KINDS=('query','offer','negative','positive','short','long','ack')
TOKENS=tuple((i,k) for i in range(3) for k in KINDS)+((-1,'current'),)
BANK=tuple(tuple(math.sin(2*math.pi*(400+100*k)*j/RATE) for j in range(N)) for k in range(len(TOKENS)))
def sha(b): return hashlib.sha256(b).hexdigest()
@lru_cache(maxsize=8192)
def pcm(token,seed,t,lost):
    rng=random.Random(seed*1009+t); b=BANK[TOKENS.index(token)]
    w=tuple(round((0 if lost else 1000*v)+rng.randint(-20,20)) for v in b)
    z=[abs(sum(v*s for v,s in zip(b,w))) for b in BANK]; k=max(range(len(z)),key=z.__getitem__)
    decoded=TOKENS[k] if z[k]>50000 and z[k]>4*max(z[:k]+z[k+1:]) else None
    assert decoded==(None if lost else token)
    return decoded,sha(struct.pack('<%dh'%N,*w)),w

def simulate(c,policy,horizon=H,audio=False):
    assert policy in POLICIES and 0<=horizon<=H
    local={}; source={}; queried=set(); pending=None; spent=0; peak=0; trace=[]; late=0; received=0; blocked=0
    samples=[0]*(SLOT*horizon) if audio else None
    for t in range(horizon):
        for ledger in (local,source):
            for v in ledger.values():
                if v[0]=='open' and t>=v[1]: v[0]='expired'
        owed=[i for i,v in local.items() if v[0]=='open']; token=None; event=None; decision='idle'
        if t in c['announced'] or t in c['shock']: token=(-1,'current'); decision='preempt'
        elif spent<c['budget']:
            if pending is not None:
                i,ok,contract=pending; pending=None; decision='response' if ok is not None else 'timeout'
                if ok is not None: token=(i,('short' if c['ttl'][i]==3 else 'long') if ok and contract else 'positive' if ok else 'negative')
            else:
                candidates=[i for i,(a,b) in enumerate(c['windows']) if i not in queried and a<=t<b]
                slots=sum(s not in c['announced'] for s in range(t,H)); need=3 if policy=='immediate' else 2
                can_query=min(slots,c['budget']-spent)>=need and len(owed)<c['capacity']
                if candidates and not can_query: blocked+=1
                urgent=owed and (policy=='immediate' or min(local[i][1] for i in owed)<=t+1)
                if candidates and can_query and not urgent:
                    i=min(candidates,key=lambda i:(c['windows'][i][1],i)); token=(i,'offer' if policy=='defer-contract' else 'query'); decision='enquire'
                elif owed:
                    i=min(owed,key=lambda i:(local[i][1],i)); token=(i,'ack'); decision='settle-attempt'
        if token is not None:
            i,k=token; lost=(i,k) in c['faults'] or (i,'response') in c['faults'] and k in ('positive','short','long')
            decoded,digest,w=pcm(token,c['seed'],t,lost); event=dict(sent=token,decoded=decoded,sha256=digest)
            if audio: samples[t*SLOT:t*SLOT+N]=w
            if k!='current':
                spent+=1
                if k in ('query','offer'):
                    queried.add(i); a,b=c['windows'][i]; pending=(i,a<=t<b if decoded else None,k=='offer')
                elif k in ('positive','short','long'):
                    source[i]=['open',t+c['ttl'][i]]
                    if decoded:
                        received+=1; local[i]=['open',t+(3 if k=='short' or policy=='immediate' else 6)]
                elif k=='ack':
                    local[i][0]='attempted'
                    if decoded:
                        if source[i][0]=='open': source[i][0]='settled'
                        else: late+=1
        peak=max(peak,sum(v[0]=='open' for v in local.values())); assert peak<=c['capacity'] and spent<=c['budget']
        trace.append(dict(t=t,decision=decision,event=event,local={i:v[:] for i,v in local.items()},source={i:v[:] for i,v in source.items()},pending=pending,spent=spent))
    count=lambda ledger,status:sum(v[0]==status for v in ledger.values())
    m=dict(received=received,settled=count(source,'settled'),source_expired=count(source,'expired'),source_open=count(source,'open'),local_expired=count(local,'expired'),local_open=count(local,'open'),attempted=count(local,'attempted'),late=late,spent=spent,peak=peak,blocked=blocked,source_only=len(source.keys()-local.keys()))
    assert sum(m[k] for k in ('settled','source_expired','source_open'))==len(source)
    assert m['local_expired']+m['local_open']+m['attempted']==received
    return dict(condition=c,policy=policy,metrics=m,trace=trace),samples

def conditions():
    for seed,windows,ttl,announced,shock,budget,cap,fault in itertools.product((231001,231003),(((0,4),(3,7),(6,10)),((0,6),(1,5),(2,9))),((3,3,3),(3,6,3),(6,3,6)),((2,5,8,11,14),(1,3,5,7,9,11,13,15)),(False,True),(5,8,11),(1,2),((),((0,'response'),),((0,'ack'),),((1,'ack'),))):
        yield dict(seed=seed,windows=windows,ttl=ttl,announced=announced,shock=tuple(t for t in (6,10,12) if shock and t not in announced),budget=budget,capacity=cap,faults=fault)

def run(out):
    for token in TOKENS:
        for lost in (False,True): pcm(token,1,0,lost)
    out=Path(out); out.mkdir(parents=True,exist_ok=False); rows=[]; stats={p:{} for p in POLICIES}; examples={}; pairs=dict(equal=0,contract_more_settled=0,local_more_settled=0,contract_more_received=0,local_more_received=0); checks=0
    for c in conditions():
        group={}
        for p in POLICIES:
            r,_=simulate(c,p); rows.append(r); m=r['metrics']; group[p]=m
            prefix=min(c['shock'],default=H); alt,_=simulate(dict(c,shock=()),p,prefix); assert r['trace'][:prefix]==alt['trace']; checks+=1
            assert m['spent']==sum(x['event'] is not None and x['event']['sent'][1]!='current' for x in r['trace'])
            for k,v in m.items(): stats[p][k]=stats[p].get(k,0)+v
        l,n=group['defer-local'],group['defer-contract']
        if l['spent']==n['spent']:
            pairs['equal']+=1
            for k in ('settled','received'):
                pairs['contract_more_'+k]+=n[k]>l[k]; pairs['local_more_'+k]+=l[k]>n[k]
            if n['settled']>l['settled']: examples.setdefault('gain',c)
        if l['received']>n['received']: examples.setdefault('cost',c)
        if n['source_only']: examples.setdefault('lost-evidence',c)
        final=r['trace'][-1]
        if any(v[0]=='attempted' and final['source'][i][0]=='expired' for i,v in final['local'].items()): examples.setdefault('unconfirmed',c)
    gallery=[]
    for label,c in examples.items():
        for p in POLICIES:
            r,w=simulate(c,p,audio=True); name=label+'-'+p
            with wave.open(str(out/(name+'.wav')),'wb') as f: f.setparams((1,2,RATE,0,'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(w),*w))
            gallery.append(dict(name=name,**r))
    receipt=dict(schema='mhac-interaction-settlement-lease-v1',parent=PARENT,main=MAIN,units=dict(slot_ms=200,body_ms=40,rate=RATE),stats=stats,pairs=pairs,checks=checks,rows=rows,examples=gallery)
    (out/'receipt.json').write_text(json.dumps(receipt,separators=(',',':')),encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Settlement leases</title><h1>Situated archive settlement</h1><p>Synthetic model. Attempted ACK is not confirmed receipt. Both endpoint ledgers are shown for diagnosis, not as shared knowledge. Start at low volume.</p><label>Replay <select id="choice"></select></label><p><audio id="audio" controls preload="none"></audio></p><label>Slot <input id="slot" type="range" min="0" max="15" value="15"></label><pre id="trace"></pre><script>const data=DATA,q=document.getElementById('choice'),a=document.getElementById('audio'),s=document.getElementById('slot'),p=document.getElementById('trace');for(const x of data)q.add(new Option(x.name,x.name));function draw(){const x=data.find(v=>v.name===q.value);p.textContent=JSON.stringify({condition:x.condition,final:x.metrics,trace:x.trace.slice(0,+s.value+1)},null,2)}q.onchange=()=>{a.pause();a.src=q.value+'.wav';draw()};s.oninput=draw;a.volume=.2;q.onchange()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(gallery)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},sort_keys=True),encoding='utf-8')
    print(json.dumps(dict(runs=len(rows),checks=checks,stats=stats,pairs=pairs,examples=examples)))

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else 'settlement-output')
