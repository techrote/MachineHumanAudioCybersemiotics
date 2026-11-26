"""MHAC #456: bounded live clarification, synthetic symbolic transport.
AI-assisted GPT-6.2, 2026-11-26. Not wire audio or human evidence.
"""
import collections, hashlib, importlib.util, json, pathlib, sys

PIN='deff7227805ef5c2f9970e9d12d66a7ee05f062c'
PARENT_SHA='1d37bc59e5e025c50dfca2dc6a34941b147ab0c7c4121f372162831c466ee686'
p=pathlib.Path(__file__).with_name('uncertainty-repair.py')
if hashlib.sha256(p.read_bytes()).hexdigest()!=PARENT_SHA:
    raise ValueError('pinned predecessor mismatch')
spec=importlib.util.spec_from_file_location('parent',p)
parent=importlib.util.module_from_spec(spec); spec.loader.exec_module(parent)
N,W,D,T=parent.N,parent.W,parent.D,parent.T
POLICIES=('window','bounded-window','bounded-open','live-window','live-repair')
REGIMES=parent.REGIMES+('forward-restored',)
SEEDS=range(4563500,4563532)

def run(seed,regime,policy):
    q=collections.defaultdict(list); tr=[]; c=collections.Counter(); effects=set()
    live=policy.startswith('live-'); repair=policy=='live-repair'
    def log(t,event,**kw): tr.append(dict(t=t,event=event,**kw))
    def send(t,k,e,s,stamp=-1):
        c[k+'-sent']+=1; age=t%T
        h=int(parent.digest([seed,t,k,e,s,stamp])[:8],16)
        delay=1+h%4 if regime=='mixed' else 1
        if regime=='mixed' and h%5==0: delay=0
        if k=='ACT' and s==1 and ((regime=='mixed' and age<10) or regime=='permanent-gap'): delay=0
        if k=='ACT' and regime=='forward-restored' and age<25: delay=0
        if k in ('ACK','STATUS') and (regime=='return-blackout' or regime=='return-restored' and age<25 or regime=='late-return' and age<55): delay=0
        log(t,'send',kind=k,epoch=e,seq=s,stamp=stamp,delay=delay)
        if delay: q[t+delay].append((k,e,s,stamp))
    for t in range(2*T):
        e=t//T+1; age=t%T
        if age==0:
            floor=ack=-1; issued=0; buf=set(); attempts=[0]*N; due=[0]*N; cursor=0; final=None
            next_probe=probes=0; credits=set(); log(t,'epoch',epoch=e)
        if regime=='stale-status' and e==2 and age in (3,55): q[t].append(('STATUS',1,7,79))
        for k,ep,s,stamp in q.pop(t,[]):
            log(t,'arrival',kind=k,epoch=ep,seq=s,stamp=stamp)
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
            elif k=='QUERY': send(t,'STATUS',e,floor,age)
            else:
                assert -1<=s<issued and 0<=stamp<=age
                if s>ack: ack=s; log(t,'receipt',ack=ack)
                if repair and k=='STATUS' and age<D and s==ack and ack+1<issued and attempts[ack+1]==4 and stamp>=due[ack+1]-8 and ack+1 not in credits:
                    credits.add(ack+1); c['repair-credit']+=1; log(t,'credit',seq=ack+1,stamp=stamp)
                if k=='STATUS' and stamp>=D:
                    final=s; log(t,'settled',prefix=s)
        if age<D:
            if issued<N and (policy=='bounded-open' or issued-ack<=W):
                s=issued; issued+=1
            elif policy=='window' and ack<issued-1:
                s=ack+1+cursor%(issued-ack-1); cursor+=1
            elif policy!='window':
                eligible=[i for i in range(ack+1,issued) if attempts[i]<4+int(i in credits) and age>=due[i]]
                s=min(eligible,key=lambda i:(attempts[i],i)) if eligible else None
            else: s=None
            if s is not None:
                send(t,'ACT',e,s); attempts[s]+=1; due[s]=age+2**attempts[s]
            elif live and ack+1<issued and attempts[ack+1]>=4 and age>=next_probe and probes<6:
                send(t,'QUERY',e,-1); c['live-query']+=1; probes+=1; next_probe=age+6
        elif policy!='window' and ack<N-1 and final is None and (age-D)%8==0:
            send(t,'QUERY',e,-1)
        assert len(buf)<=W and ack<=floor and probes<=6
        if policy!='bounded-open': assert issued-ack-1<=W
        if policy!='window': assert all(a<=4+int(i in credits) for i,a in enumerate(attempts))
        if age==T-1:
            c['complete']+=int(floor==N-1)
            c['confirmed']+=int(ack==N-1)
            c['settled-incomplete']+=int(final is not None and final<N-1)
            c['unknown-issued']+=0 if final is not None else issued-ack-1
            c['not-issued']+=N-issued
            c['known-applied']+=ack+1
            c['unknown-epochs']+=int(ack<N-1 and final is None and issued>ack+1)
            assert final is None or final==floor
        log(t,'state',epoch=e,age=age,applied=floor+1,known=ack+1,issued=issued,buffer=sorted(buf),final=final)
    c['applied']=len(effects); c['missing']=2*N-len(effects)
    return dict(c),tr

def audit(tr):
    # Separate trace walk: check actual effects, evidence provenance and budgets.
    for e in (1,2):
        rows=[x for x in tr if x['t']//T+1==e]; applied=[]; known=-1; credits=set(); sends=collections.Counter(); probes=0
        for x in rows:
            age=x['t']%T; event=x['event']
            if event=='apply':
                assert age<D and x['seq']==len(applied); applied.append(x['seq'])
            elif event=='credit':
                assert age<D and x['seq'] not in credits and sends[x['seq']]==4
                assert any(y['event']=='arrival' and y['kind']=='STATUS' and y['epoch']==e and y['seq']==x['seq']-1 and y['stamp']==x['stamp'] and y['t']==x['t'] for y in rows)
                credits.add(x['seq'])
            elif event=='send' and x['kind']=='ACT':
                assert age<D; sends[x['seq']]+=1
            elif event=='send' and x['kind']=='QUERY' and age<D: probes+=1
            elif event=='receipt':
                assert x['ack']>known and x['ack']<len(applied)
                assert any(y['event']=='arrival' and y['kind'] in ('ACK','STATUS') and y['epoch']==e and y['seq']==x['ack'] and y['t']==x['t'] for y in rows)
                known=x['ack']
            elif event=='state':
                assert x['applied']==len(applied) and x['known']==known+1
        assert probes<=6
        assert all(sends[i]<=5 for i in credits)
    return 2

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    # Exact comparator equivalence, including full trace, on original and fresh seeds.
    checked=0
    for r in parent.REGIMES:
        for pol in parent.POLICIES:
            for seed in (4563400,4563417,SEEDS.start,SEEDS.stop-1):
                assert run(seed,r,pol)==parent.run(seed,r,pol); checked+=1
    totals={}; hashes=[]; witnesses={}; audited=0
    for r in REGIMES:
        totals[r]={}
        for pol in POLICIES:
            total=collections.Counter()
            for seed in SEEDS:
                c,tr=run(seed,r,pol); audited+=audit(tr); total.update(c); hashes.append([seed,r,pol,parent.digest(tr)])
                if seed==SEEDS.start: witnesses[r+'/'+pol]=tr
            totals[r][pol]=dict(total)
    assert totals['return-restored']['live-window']['applied']>totals['return-restored']['bounded-window']['applied']
    assert totals['forward-restored']['live-window']['applied']==0
    assert totals['return-blackout']['live-window']['confirmed']==0
    receipt=dict(parent=PIN,parent_sha256=PARENT_SHA,comparator_checks=checked,audited_epochs=audited,deadline=D,epoch_slots=T,totals=totals,hashes=hashes,witnesses=witnesses)
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    for r,pol in [('return-restored','bounded-window'),('return-restored','live-window'),('forward-restored','live-repair'),('return-blackout','live-repair')]:
        parent.audio(out/(r+'-'+pol+'.wav'),witnesses[r+'/'+pol])
    page='''<!doctype html><meta charset="utf-8"><title>Live clarification</title><style>body{font:16px system-ui;max-width:860px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}input{width:100%}</style><h1>Live clarification</h1><p>Synthetic ordered actions. Applied is ground truth; known is sender evidence. Deadline 48; epoch 80. Audio is event sonification, not wire encoding.</p><select id="case"></select><button id="prev">Previous</button><button id="next">Next</button><input id="slot" type="range" min="0" max="159" value="0"><p id="summary"></p><pre id="events"></pre><button id="export">Export trace</button><h2>Audio specimens</h2><div id="audio"></div><script>const traces=DATA,el=id=>document.getElementById(id);for(const k of Object.keys(traces)){const o=document.createElement('option');o.value=o.textContent=k;el('case').append(o)}function render(){const t=+el('slot').value,rows=traces[el('case').value].filter(x=>x.t===t),s=rows.find(x=>x.event==='state');el('summary').textContent='Epoch '+s.epoch+' | age '+s.age+' | issued '+s.issued+' | applied '+s.applied+' | known '+s.known+' | final '+(s.final===null?'unknown':s.final+1);el('events').textContent=JSON.stringify(rows,null,2)}el('case').onchange=el('slot').oninput=render;el('prev').onclick=()=>{el('slot').value=Math.max(0,+el('slot').value-1);render()};el('next').onclick=()=>{el('slot').value=Math.min(159,+el('slot').value+1);render()};el('export').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(traces[el('case').value])],{type:'application/json'}));a.href=u;a.download='trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};for(const name of AUDIO){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=name+' ';a.src=name;a.controls=true;a.volume=.2;a.preload='none';p.append(a);el('audio').append(p)}render();</script>'''
    (out/'index.html').write_text(page.replace('DATA',json.dumps(witnesses,separators=(',',':'))).replace('AUDIO',json.dumps(sorted(p.name for p in out.glob('*.wav')))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.name!='manifest.json'},sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(totals,indent=2))

if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--scenario':
        r,pol,seed=sys.argv[2],sys.argv[3],int(sys.argv[4])
        if r not in REGIMES or pol not in POLICIES: raise ValueError('unknown scenario or policy')
        c,tr=run(seed,r,pol); audit(tr); print(json.dumps(dict(metrics=c,trace=tr),indent=2))
    else: main(pathlib.Path(sys.argv[1]))
