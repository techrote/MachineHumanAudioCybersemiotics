"""#456 synthetic settlement reconciliation, standalone extension of settlement-lease.py.
Python 3.11+ stdlib: python settlement-confirm.py NEW_OUTPUT. No human evidence.
"""
import itertools, json, math, random, struct, sys, wave, hashlib
from functools import lru_cache
from pathlib import Path

PARENT='8f0e3120b990d77b247dbeaff3a9fa5d1aa67f4f'
MAIN='495a98ca12bae467a507031f04931aa4254b1866'
H,RATE,SLOT,N=28,8000,1600,160
POLICIES=('unconfirmed','individual','cumulative')
QUERY,POSITIVE,BUSY,ACK,POLL,REPORT,CURRENT=range(7)
NAMES=('query','evidence','busy','ack','poll','report','current')
WINDOWS=((0,6),(3,10),(6,15),(1,8),(4,12),(8,16))
BANK=tuple(tuple(math.sin(2*math.pi*(400+100*k)*j/RATE) for j in range(N)) for k in range(16))
sha=lambda b:hashlib.sha256(b).hexdigest()
@lru_cache(maxsize=None)
def pcm(token,lost):
    w=tuple(round(1000*v) if not lost else 0 for k in token for v in BANK[k]); decoded=[]
    for i in range(3):
        z=[abs(sum(a*b for a,b in zip(b,w[i*N:(i+1)*N]))) for b in BANK]; k=max(range(16),key=z.__getitem__)
        if z[k]<30000 or z[k]<4*max(z[:k]+z[k+1:]): decoded=None; break
        decoded.append(k)
    decoded=tuple(decoded) if decoded is not None else None
    assert decoded==(None if lost else token)
    return decoded,sha(struct.pack('<%dh'%len(w),*w)),w

def simulate(c,policy,horizon=H,audio=False):
    # Requester sees only its local ledger, decoded responses, clock and advertised windows.
    local={}; source={}; truth=set(); queried=set(); polls={}; pending=None; trace=[]
    m=dict(evidence=0,settled=0,confirmed=0,unknown=0,source_only=0,busy=0,expired=0,forgotten=0,late=0,polls=0,reports=0,spent=0,peak=0)
    samples=[0]*(SLOT*horizon) if audio else None
    for t in range(horizon):
        for i,(status,until) in list(source.items()):
            if t>=until:
                m['expired' if status=='open' else 'forgotten']+=1; del source[i]
        for i,(status,until) in list(local.items()):
            if status=='open' and t>=until: local[i]=('expired',until)
        owed=[i for i,v in local.items() if v[0]=='open']; unknown=[i for i,v in local.items() if v[0]=='attempted']; token=None; event=None
        if t in c['announced'] or t in c['shock']: token=(CURRENT,0,0)
        elif m['spent']<c['budget']:
            if pending is not None:
                k,i,flag,delivered=pending; pending=None
                if delivered and k==QUERY:
                    token=(BUSY if sum(j//3==i//3 for j in source)>=c['capacity'] else POSITIVE,i,c['ttl'])
                elif delivered and k==POLL:
                    mask=sum(1<<(j%3) for j,v in source.items() if j//3==i//3 and v[0]=='settled' and (flag or j==i))
                    token=(REPORT,i,mask)
            else:
                candidates=[i for i,(a,b) in enumerate(WINDOWS) if i not in queried and a<=t<b]
                urgent=owed and min(local[i][1] for i in owed)<=t+1
                room=min(c['budget']-m['spent'],sum(s not in c['announced'] for s in range(t,H)))
                if candidates and room>=2 and not urgent:
                    token=(QUERY,min(candidates,key=lambda i:(WINDOWS[i][1],i)),0)
                elif owed: token=(ACK,min(owed,key=lambda i:(local[i][1],i)),0)
                elif policy!='unconfirmed' and room>=2:
                    keys=sorted({i if policy=='individual' else 3*(i//3) for i in unknown})
                    keys=[i for i in keys if polls.get(i,0)<2]
                    if keys: token=(POLL,min(keys,key=lambda i:(polls.get(i,0),i)),int(policy=='cumulative'))
        if token is not None:
            k,i,v=token; mode=c['fault']; lost=(mode=='ack0' and k==ACK and i==0 or mode=='evidence0' and k==POSITIVE and i==0 or mode=='report-loss' and k==REPORT and m['reports']%2==0 or mode=='mixed' and k!=CURRENT and random.Random(c['seed']*1009+t).randrange(5)==0)
            decoded,digest,w=pcm(token,lost); event=dict(sent=token,decoded=decoded,sha256=digest)
            if audio: samples[t*SLOT:t*SLOT+len(w)]=w
            if k!=CURRENT: m['spent']+=1
            if k==QUERY: queried.add(i); pending=(k,i,0,decoded is not None)
            elif k==POSITIVE:
                assert i not in source; source[i]=('open',t+c['ttl'])
                if decoded: local[i]=('open',t+decoded[2]); m['evidence']+=1
            elif k==BUSY: m['busy']+=1
            elif k==ACK:
                local[i]=('attempted',local[i][1])
                if decoded:
                    if i in source and source[i][0]=='open': source[i]=('settled',t+c['retention']); truth.add(i)
                    else: m['late']+=1
            elif k==POLL: polls[i]=polls.get(i,0)+1; m['polls']+=1; pending=(k,i,v,decoded is not None)
            elif k==REPORT:
                m['reports']+=1
                if decoded:
                    for j in range(3*(i//3),3*(i//3)+3):
                        if decoded[2]&(1<<(j%3)) and j in local and local[j][0]=='attempted':
                            assert j in truth; local[j]=('confirmed',local[j][1])
        m['peak']=max(m['peak'],*(sum(i//3==a for i in source) for a in range(2)))
        assert m['peak']<=c['capacity'] and m['spent']<=c['budget']
        trace.append(dict(t=t,event=event,local=local.copy(),source=source.copy(),settled=sorted(truth),pending=pending,spent=m['spent']))
    m.update(settled=len(truth),confirmed=sum(v[0]=='confirmed' for v in local.values()),unknown=sum(v[0]=='attempted' for v in local.values()),source_only=sum(x['event'] is not None and x['event']['sent'][0]==POSITIVE and x['event']['decoded'] is None for x in trace))
    assert m['confirmed']<=m['settled']<=m['evidence'] and m['late']==0
    return dict(condition=c,policy=policy,metrics=m,trace=trace),samples

def conditions():
    for seed,ttl,retention,cap,budget,shock,fault in itertools.product((232001,232003),(3,6),(3,12),(1,3),(18,25),(False,True),('none','ack0','evidence0','report-loss','mixed')):
        yield dict(seed=seed,ttl=ttl,retention=retention,capacity=cap,budget=budget,announced=(2,9,16,23),shock=(5,11,19,24) if shock else (),fault=fault)

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=False); rows=[]; stats={p:{} for p in POLICIES}; examples={}; pairs=dict(equal_airtime=0,cumulative_more=0,individual_more=0); checks=0
    for c in conditions():
        group={}
        for p in POLICIES:
            r,_=simulate(c,p); rows.append(r); m=r['metrics']; group[p]=m
            cut=min(c['shock'],default=H); alt,_=simulate(dict(c,shock=()),p,cut); assert r['trace'][:cut]==alt['trace']; checks+=1
            assert m['spent']==sum(x['event'] is not None and x['event']['sent'][0]!=CURRENT for x in r['trace'])
            for k,v in m.items(): stats[p][k]=stats[p].get(k,0)+v
        a,b=group['individual'],group['cumulative']
        if a['spent']==b['spent']:
            pairs['equal_airtime']+=1; pairs['cumulative_more']+=b['confirmed']>a['confirmed']; pairs['individual_more']+=a['confirmed']>b['confirmed']
        if b['confirmed']>a['confirmed']: examples.setdefault('batch-gain',c)
        if a['confirmed']>b['confirmed']: examples.setdefault('batch-cost',c)
        if b['settled']>b['confirmed'] and c['fault']=='report-loss': examples.setdefault('lost-report',c)
        if b['busy'] and c['fault']=='none': examples.setdefault('memory-pressure',c)
    gallery=[]
    for label,c in examples.items():
        for p in POLICIES:
            r,w=simulate(c,p,audio=True); name=label+'-'+p
            with wave.open(str(out/(name+'.wav')),'wb') as f: f.setparams((1,2,RATE,0,'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(w),*w))
            gallery.append(dict(name=name,**r))
    receipt=dict(schema='mhac-interaction-settlement-confirm-v1',parent=PARENT,main=MAIN,units=dict(slot_ms=200,body_ms=60,rate=RATE),kinds=NAMES,stats=stats,pairs=pairs,checks=checks,rows=rows,examples=gallery)
    (out/'receipt.json').write_text(json.dumps(receipt,separators=(',',':')),encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Settlement confirmation</title><h1>Two archive agents: reconciliation</h1><p>Synthetic only. Missing confirmation is unknown, not rejection. Both ledgers are visible to the inspector, not the requester. Start with low playback volume.</p><label>Scenario and policy <select id="choice"></select></label><p><audio id="audio" controls preload="none"></audio></p><label>Slot <input id="slot" type="range" min="0" max="27" value="27"></label><pre id="trace"></pre><script>const data=DATA,q=document.getElementById('choice'),a=document.getElementById('audio'),s=document.getElementById('slot'),p=document.getElementById('trace');for(const x of data)q.add(new Option(x.name,x.name));function draw(){const x=data.find(v=>v.name===q.value);p.textContent=JSON.stringify({condition:x.condition,final:x.metrics,slot:x.trace[+s.value]},null,2)}q.onchange=()=>{a.pause();a.src=q.value+'.wav';draw()};s.oninput=draw;a.volume=.2;q.onchange()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(gallery)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},sort_keys=True),encoding='utf-8')
    print(json.dumps(dict(runs=len(rows),checks=checks,stats=stats,pairs=pairs,examples=examples)))

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else 'confirmation-output')
