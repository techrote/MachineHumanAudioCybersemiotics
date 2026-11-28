"""MHAC #456 Interaction: finite uncertain-obligation settlement (synthetic).
AI-assisted GPT-6.2, 2026-11-26. Symbolic transport, not acoustic decoding.
"""
import collections, hashlib, json, math, pathlib, struct, sys, wave

PARENT='b4854cfe5d18be39b3c4e85b519dda28d5b3b814'
N,W,D,T=8,3,48,80
POLICIES=('window','bounded-window','bounded-open')
REGIMES=('clean','mixed','return-blackout','return-restored','permanent-gap','late-return','stale-status')
SEEDS=range(4563400,4563432)

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(seed,regime,policy):
    q=collections.defaultdict(list); tr=[]; c=collections.Counter(); effects=set()
    def log(t,event,**kw): tr.append(dict(t=t,event=event,**kw))
    def send(t,k,e,s,stamp=-1):
        c[k+'-sent']+=1; age=t%T
        h=int(digest([seed,t,k,e,s,stamp])[:8],16)
        delay=1+h%4 if regime=='mixed' else 1
        if regime=='mixed' and h%5==0: delay=0
        if k=='ACT' and s==1 and ((regime=='mixed' and age<10) or regime=='permanent-gap'): delay=0
        if k in ('ACK','STATUS') and (regime=='return-blackout' or regime=='return-restored' and age<25 or regime=='late-return' and age<55): delay=0
        log(t,'send',kind=k,epoch=e,seq=s,stamp=stamp,delay=delay)
        if delay: q[t+delay].append((k,e,s,stamp))
    for t in range(2*T):
        e=t//T+1; age=t%T
        if age==0:
            floor=ack=-1; issued=0; buf=set(); attempts=[0]*N; due=[0]*N; cursor=0; final=None
            log(t,'epoch',epoch=e)
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
                if k=='STATUS' and stamp>=D:
                    final=s; log(t,'settled',prefix=s)
        if age<D:
            if issued<N and (policy=='bounded-open' or issued-ack<=W):
                s=issued; issued+=1
            elif policy=='window' and ack<issued-1:
                s=ack+1+cursor%(issued-ack-1); cursor+=1
            elif policy!='window':
                eligible=[i for i in range(ack+1,issued) if attempts[i]<4 and age>=due[i]]
                s=min(eligible,key=lambda i:(attempts[i],i)) if eligible else None
            else: s=None
            if s is not None:
                send(t,'ACT',e,s); attempts[s]+=1; due[s]=age+2**attempts[s]
        elif policy!='window' and ack<N-1 and final is None and (age-D)%8==0:
            send(t,'QUERY',e,-1)
        assert len(buf)<=W
        assert ack<=floor # truth check only, not policy input
        if policy!='bounded-open': assert issued-ack-1<=W
        if policy!='window': assert max(attempts)<=4
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
    assert c['applied']==sum(x['event']=='apply' for x in tr)
    return dict(c),tr

def audio(path,tr):
    tones={'apply':660,'receipt':880,'settled':440,'epoch':220}; events=collections.defaultdict(list)
    for x in tr:
        if x['event'] in tones: events[x['t']].append(tones[x['event']])
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,8000,0,'NONE','not compressed'))
        for t in range(2*T):
            fs=events[t]; f.writeframes(struct.pack('<400h',*[int(800*math.sin(math.pi*i/399)**2*sum(math.sin(2*math.pi*z*i/8000) for z in fs)/max(1,len(fs))) for i in range(400)]))

def main(out):
    out.mkdir(parents=True,exist_ok=True); totals={}; hashes=[]; witnesses={}
    for regime in REGIMES:
        totals[regime]={}
        for policy in POLICIES:
            total=collections.Counter()
            for seed in SEEDS:
                c,tr=run(seed,regime,policy); total.update(c); hashes.append([seed,regime,policy,digest(tr)])
                if seed==SEEDS.start: witnesses[regime+'/'+policy]=tr
            totals[regime][policy]=dict(total)
    assert totals['return-blackout']['bounded-open']['applied']==512
    assert totals['return-blackout']['bounded-open']['confirmed']==0
    assert totals['late-return']['bounded-open']['confirmed']==64
    assert totals['permanent-gap']['bounded-open']['settled-incomplete']==64
    assert totals['stale-status']['bounded-open']['stale-rejected']==64
    (out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,deadline=D,epoch_slots=T,totals=totals,hashes=hashes,witnesses=witnesses),sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    for r,p in [('return-blackout','window'),('return-blackout','bounded-open'),('late-return','bounded-open'),('permanent-gap','bounded-open')]: audio(out/(r+'-'+p+'.wav'),witnesses[r+'/'+p])
    page='''<!doctype html><meta charset=utf-8><title>MHAC uncertain obligations</title><style>body{font:16px system-ui;max-width:860px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}button,select,input{font:inherit}progress{width:100%}</style><h1>Uncertain obligations</h1><p>Fictional ordered tile placement. Applied is simulator ground truth; known is sender evidence. At slot 48 execution expires; status queries can settle remaining uncertainty. Audio is event sonification, not wire encoding.</p><select id="case"></select><button id="prev">Previous</button><button id="next">Next</button><input type="range" id="slot" min="0" max="159" value="0"><p id="summary"></p><label>Applied <progress id="applied" max="8"></progress></label><label>Known <progress id="known" max="8"></progress></label><pre id="events"></pre><button id="export">Export trace JSON</button><h2>Specimens</h2><div id="audio"></div><script>const traces=DATA;const el=id=>document.getElementById(id);for(const k of Object.keys(traces)){const o=document.createElement('option');o.value=o.textContent=k;el('case').append(o)}function render(){const t=+el('slot').value,rows=traces[el('case').value].filter(x=>x.t===t),s=rows.find(x=>x.event==='state');el('summary').textContent='Epoch '+s.epoch+' age '+s.age+' | issued '+s.issued+' | applied '+s.applied+' | known '+s.known+' | final prefix '+(s.final===null?'unknown':s.final+1);el('applied').value=s.applied;el('known').value=s.known;el('events').textContent=JSON.stringify(rows,null,2)}el('case').onchange=render;el('slot').oninput=render;el('prev').onclick=()=>{el('slot').value=Math.max(0,+el('slot').value-1);render()};el('next').onclick=()=>{el('slot').value=Math.min(159,+el('slot').value+1);render()};el('export').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(traces[el('case').value])],{type:'application/json'}));a.href=u;a.download='trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};for(const name of AUDIO){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=name+' ';a.src=name;a.controls=true;a.volume=.2;a.preload='none';p.append(a);el('audio').append(p)}render();</script>'''
    (out/'index.html').write_text(page.replace('DATA',json.dumps(witnesses,separators=(',',':'))).replace('AUDIO',json.dumps(sorted(p.name for p in out.glob('*.wav')))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.name!='manifest.json'},sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(totals,indent=2))

if __name__=='__main__': main(pathlib.Path(sys.argv[1]))
