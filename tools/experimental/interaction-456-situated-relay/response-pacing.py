"""Interaction #456: response-aware pacing under shared budgets; synthetic only.
Pinned predecessor 4237ce0f6654f1613f15653987c16941dd089a3f.
AI-assisted, no human evidence; no real device or acoustic wire transport.
"""
import collections as C
import hashlib, importlib.util, json, pathlib, sys

ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('shared',ROOT/'shared-repair.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
assert hashlib.sha256((ROOT/'shared-repair.py').read_bytes()).hexdigest()=='8f090aaeaa6d8009b7920c1218d170461591ea93237b236a48b70f6a779a0c91'
POLICIES=('fixed2','fixed3','fixed4','adaptive','adaptive-class')
REGIMES=('random-opening','irregular','periodic','return-fault')
SEEDS=range(4563900,4563964)

def rand(seed,*args): return int(b.digest([seed,*args])[:8],16)

def channel(seed,r,k,l,t):
    if r in b.REGIMES: return b.channel(seed,r,k,l,t)
    if k=='REPLY': return rand(seed,'reply',l,t)%100 >= (40 if r=='return-fault' else 10)
    opening=rand(seed,'open',l)% (13 if l==0 else 19)
    if t<opening: return False
    if r=='irregular': return rand(seed,'block',l,t//3)%100>=45
    if r=='periodic': return (t+rand(seed,'phase',l)%7)%7<2+rand(seed,'width',l)%3
    return True

def run(seed,r,p):
    applied=[0,0]; known=[0,0]; last=[-99,-99]; misses=[0,0]; probes=[0,0]; ready=[0,0]
    queue=C.defaultdict(list); pending={}; trace=[]; acts=out=responses=0; turn=0
    def log(t,event,**kw): trace.append(dict(t=t,event=event,**kw))
    for t in range(b.H):
        for k,l,s,n,stamp in queue.pop(t,[]):
            log(t,'arrival',kind=k,lane=l,seq=s,nonce=n,stamp=stamp)
            if k=='REPLY':
                assert n in pending and pending[n][:2]==(l,s)
                sent_kind=pending.pop(n)[2]; known[l]=max(known[l],stamp); misses[l]=0; ready[l]=t
                log(t,'evidence',lane=l,known=known[l],kind=sent_kind,nonce=n,sampled=t-1)
            else:
                if k=='ACT' and t<b.D[l] and s==applied[l]:
                    applied[l]+=1; log(t,'apply',lane=l,seq=s)
                responses+=1; ok=channel(seed,r,'REPLY',l,t)
                log(t,'reply',lane=l,nonce=n,seq=s,prefix=applied[l],delivered=ok)
                if ok: queue[t+1].append(('REPLY',l,s,n,applied[l]))
        for n,(l,s,k) in list(pending.items()):
            if t-n>=2:
                del pending[n]; misses[l]+=1; ready[l]=n+min(6,2+2*misses[l])
                if p.startswith('adaptive'): log(t,'timeout',lane=l,nonce=n,next_eligible=ready[l],misses=misses[l])
        adaptive=p.startswith('adaptive')
        eligible=[l for l in range(2) if t+1<b.D[l] and known[l]<b.N and t-last[l]>=2 and (not adaptive or t>=ready[l])]
        if eligible and out<b.OUT_CAP and acts<b.ACT_CAP and (adaptive or t%int(p[-1])==0):
            l=min(eligible,key=lambda l:(l-turn)%2); k='ACT'
            if p=='adaptive-class' and misses[l]>=2 and probes[l]<2 and b.D[l]-t>4:
                k='CLASS'; probes[l]+=1
            turn=1-l; s=known[l]; n=t; out+=1; last[l]=t
            acts+=k=='ACT'; pending[n]=(l,s,k); ok=channel(seed,r,k,l,t)
            log(t,'send',kind=k,lane=l,seq=s,nonce=n,delivered=ok)
            if ok: queue[t+1].append((k,l,s,n,-1))
        assert all(0<=known[l]<=applied[l]<=b.N for l in range(2)) and len(pending)<=2
        log(t,'state',applied=applied[:],known=known[:],actions=acts,outbound=out)
    return dict(applied=sum(applied),known=sum(known),complete=sum(x==b.N for x in applied),confirmed=sum(x==b.N for x in known),actions=acts,outbound=out,responses=responses,unknown=sum(applied)-sum(known),lane0=applied[0],lane1=applied[1]),trace

def checked(seed,r,p):
    m,tr=run(seed,r,p); b.audit(tr,m)
    sends={x['nonce']:x for x in tr if x['event']=='send'}
    for x in tr:
        if x['event']=='send': assert x['delivered']==channel(seed,r,x['kind'],x['lane'],x['t'])
        if x['event']=='timeout':
            assert x['t']==x['nonce']+2 and sends[x['nonce']]['lane']==x['lane']
            assert not any(y['event']=='evidence' and y['nonce']==x['nonce'] for y in tr)
    assert (m,tr)==run(seed,r,p)
    return m,tr

def main(out):
    out.mkdir(); rows=[]; traces={}; hashes=[]; parity=0
    for r in b.REGIMES:
        for s in b.SEEDS:
            assert run(s,r,'fixed3')==b.run(s,r,'paced'); parity+=1
    for r in (*b.REGIMES,*REGIMES):
        seeds=b.SEEDS if r in b.REGIMES else SEEDS
        for p in POLICIES:
            total=C.Counter()
            for s in seeds:
                m,tr=checked(s,r,p); total.update(m); hashes.append([r,p,s,b.digest(tr)])
                if s==seeds.start: traces[r+'/'+p]=tr
            rows.append(dict(regime=r,policy=p,trials=len(seeds),**total))
    receipt=dict(schema='mhac.interaction.response-pacing/1',parent='4237ce0f6654f1613f15653987c16941dd089a3f',prior_seeds=list(b.SEEDS),new_seeds=list(SEEDS),parity=parity,rows=rows,hashes=hashes,traces=traces)
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    names=[]
    for key in ('irregular/fixed3','irregular/adaptive','periodic/fixed3','periodic/adaptive-class'):
        name=key.replace('/','-')+'.wav'; b.audio(out/name,traces[key]); names.append(name)
    page='''<!doctype html><meta charset=utf-8><title>Response pacing</title><style>body{font:16px system-ui;max-width:900px;margin:auto;padding:1em}pre{white-space:pre-wrap}select,input,button{font:inherit}progress{width:100%}</style><h1>Response-aware conversational pacing</h1><p>Fictional agents, shared caps 8 action / 12 outbound. Select first-seed replay. Audio renders events, not wire messages. Start at low gain.</p><label>Scenario <select id="scene"></select></label><label> Policy <select id="policy"></select></label><pre id="table"></pre><label>Slot <input id="slot" type="range" min="0" max="27" value="0"></label><button id="next">Next</button><p id="state"></p><label>Applied<progress id="applied" max="6"></progress></label><label>Known<progress id="known" max="6"></progress></label><pre id="events"></pre><button id="save">Export trace</button><div id="audio"></div><script>const data=RECEIPT,names=NAMES,e=id=>document.getElementById(id);function options(id,vs){for(const v of vs){const o=document.createElement('option');o.value=o.textContent=v;e(id).append(o)}}options('scene',[...new Set(data.rows.map(r=>r.regime))]);options('policy',[...new Set(data.rows.map(r=>r.policy))]);function trace(){return data.traces[e('scene').value+'/'+e('policy').value]}function render(){const t=+e('slot').value,x=trace().filter(x=>x.t===t),s=x.find(x=>x.event==='state');e('state').textContent='Slot '+t+' | applied '+s.applied+' | known '+s.known+' | ACT '+s.actions+'/8 | outbound '+s.outbound+'/12';e('applied').value=s.applied.reduce((a,b)=>a+b);e('known').value=s.known.reduce((a,b)=>a+b);e('events').textContent=JSON.stringify(x,null,2);e('table').textContent=data.rows.filter(r=>r.regime===e('scene').value).map(r=>r.policy+': applied '+r.applied+'/'+(r.trials*6)+'; confirmed '+r.confirmed+'/'+(r.trials*2)+'; outbound '+r.outbound).join('\\n')}e('scene').onchange=e('policy').onchange=e('slot').oninput=render;e('next').onclick=()=>{e('slot').value=Math.min(27,+e('slot').value+1);render()};e('save').onclick=()=>{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([JSON.stringify(trace())],{type:'application/json'}));a.href=u;a.download='trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};for(const n of names){const a=document.createElement('audio');a.src=n;a.controls=true;a.volume=.2;a.preload='none';e('audio').append(document.createTextNode(n),a,document.createElement('br'))}render();</script>'''
    (out/'index.html').write_text(page.replace('RECEIPT',json.dumps(receipt,separators=(',',':'))).replace('NAMES',json.dumps(names)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(rows,indent=2))

if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--scenario':
        r,p,s=sys.argv[2],sys.argv[3],int(sys.argv[4]); assert r in (*b.REGIMES,*REGIMES) and p in POLICIES
        m,tr=checked(s,r,p); print(json.dumps(dict(metrics=m,trace=tr),indent=2))
    else: main(pathlib.Path(sys.argv[1]))
