"""Refs #456 / Draft #457. Synthetic transaction admission, independent narrow FSK.
No human evidence, authentication, streaming, or compatibility with Grammar profiles.
"""
import itertools, json, math, random, struct, sys, wave, hashlib
from functools import lru_cache
from pathlib import Path

PINS = dict(main='495a98ca12bae467a507031f04931aa4254b1866', parent='a51d73f23306b6974542dce54840b8b52520b996', grammar='7773a123a29881a22d7c1893df1dd609c4ef25d1')
TOKENS = ('repair','receipt','report','report_ack','query','negative','positive','archive_ack','current')
POLICIES = ('opportunistic','budget','budget_and_slots')
RATE, N, SLOT, H = 8000, 320, 1600, 12
BANK = tuple(tuple(math.sin(2*math.pi*(400+100*k)*i/RATE) for i in range(N)) for k in range(len(TOKENS)))
SHA = lambda b: hashlib.sha256(b).hexdigest()

@lru_cache(maxsize=4096)
def render(token, seed, tick, lost):
    rng = random.Random(seed*1009+tick)
    return tuple(round((0 if lost else 1200*v)+rng.randint(-20,20)) for v in BANK[TOKENS.index(token)])

@lru_cache(maxsize=4096)
def decode(w):
    z = [abs(sum(v*s for v,s in zip(b,w))) for b in BANK]
    k = max(range(len(z)),key=z.__getitem__)
    return TOKENS[k] if z[k]>50000 and z[k]>4*max(z[:k]+z[k+1:]) else None

def simulate(c, policy, audio=False):
    assert policy in POLICIES
    state = dict(receipt=False, disputed=False, report_ack=False, positive=False, archive_ack=False)
    attempts = dict(A=0,C=0,B=0); ready = dict(A=0,C=0,B=0)
    counts = {}; trace = []; tx = None; spent = 0; denied = 0; exposure = 0; current = 0
    starts = []; samples = [0]*(H*SLOT) if audio else None
    for t in range(H):
        token = None; event = None; rejected = []
        if t in c['traffic']:
            token = 'current'
        elif spent < c['cap']:
            if tx is None:
                expiry = c['advert']
                can = dict(A=not state['receipt'], C=c['rival'] and not state['report_ack'], B=not state['positive'] and (expiry is None or t<expiry))
                order = ('B','C','A') if expiry is not None and t+3>=expiry else ('C','B','A')
                for k in order:
                    if not can[k] or attempts[k]>=2 or t<ready[k]: continue
                    need = 3 if k=='B' else 2
                    slots = sum(s not in c['traffic'] for s in range(t,H))
                    if (policy!='opportunistic' and c['cap']-spent<need) or (policy=='budget_and_slots' and slots<need):
                        denied += 1; rejected.append(k); continue
                    attempts[k]+=1; tx = [k, {'A':'repair','B':'query','C':'report'}[k]]
                    starts.append(dict(t=t,kind=k,need=need,budget=c['cap']-spent,slots=slots)); break
            if tx: token = tx[1]
        if token:
            counts[token] = counts.get(token,0)+1
            lost = c['loss']==token and counts[token]==1
            w = render(token,c['seed'],t,lost); decoded = decode(w)
            assert decoded == (None if lost else token)
            if audio: samples[t*SLOT:t*SLOT+N] = w
            event = dict(token=token,decoded=decoded,lost=lost,sha=SHA(struct.pack('<%dh'%N,*w)))
            if token=='current': current+=1
            else:
                spent+=1; k=tx[0]
                nxt = None
                if decoded=='repair': nxt='receipt'
                elif decoded=='receipt': state['receipt']=True
                elif decoded=='report': state['disputed']=True; nxt='report_ack'
                elif decoded=='report_ack': state['report_ack']=True
                elif decoded=='query': nxt='positive' if c['start']<=t<c['expiry'] else 'negative'
                elif decoded=='positive': state['positive']=True; nxt='archive_ack'
                elif decoded=='archive_ack': state['archive_ack']=True
                if nxt: tx[1]=nxt
                else: tx=None; ready[k]=t+2
        exposure += int(c['rival'] and not state['disputed'])
        trace.append(dict(t=t,event=event,rejected=rejected,state=dict(state),spent=spent,pending=list(tx) if tx else None))
    assert spent<=c['cap'] and current==len(c['traffic'])
    assert not state['report_ack'] or state['disputed']
    assert not state['archive_ack'] or state['positive']
    if policy=='budget_and_slots': assert tx is None
    metrics = dict(**{k:int(v) for k,v in state.items()},spent=spent,current=current,denied=denied,unfinished=int(tx is not None),exposure=exposure,starts=len(starts))
    return dict(condition=c,policy=policy,metrics=metrics,starts=starts,trace=trace),samples

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    for token in TOKENS:
        assert decode(render(token,1,0,False))==token and decode(render(token,1,0,True)) is None
    rows=[]; stats={}; examples=[]
    for seed,start,duration,ad,rival,loss,traffic,cap in itertools.product((221051,221053),(0,3,7),(2,4),('exact','early','late','missing'),(False,True),('none','receipt','report','positive'),((2,5,8),(0,2,4,6,8,10)),(3,5,7)):
        expiry=start+duration; advert={'exact':expiry,'early':expiry-2,'late':expiry+2,'missing':None}[ad]
        c=dict(seed=seed,start=start,expiry=expiry,advert=advert,advert_mode=ad,rival=rival,loss=loss,traffic=traffic,cap=cap)
        for policy in POLICIES:
            row,_=simulate(c,policy); rows.append(row)
            agg=stats.setdefault(f'{cap}/{ad}/{policy}',dict(runs=0)); agg['runs']+=1
            for k,v in row['metrics'].items(): agg[k]=agg.get(k,0)+v
            if seed==221051 and start==3 and duration==2 and ad in ('exact','late') and rival and loss=='receipt' and len(traffic)==6 and cap==5:
                name=f'{ad}-{policy}'; again,samples=simulate(c,policy,True); assert again==row
                with wave.open(str(out/(name+'.wav')),'wb') as f:
                    f.setparams((1,2,RATE,0,'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(samples),*samples))
                examples.append(dict(name=name,**row))
    receipt=dict(schema='mhac-interaction-transaction-admission-v1',pins=PINS,units=dict(slot_ms=200,body_ms=40,rate=RATE),stats=stats,rows=rows,examples=examples)
    (out/'receipt.json').write_text(json.dumps(receipt,separators=(',',':')),encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Transaction admission</title><h1>Transaction admission</h1><p>Synthetic dialogue. Select a trace and step through its state. Start with low volume. No autoplay.</p><select id="choice"></select><audio id="audio" controls preload="none"></audio><p><label>Slot <input id="slot" type="range" min="0" max="11" value="11"></label></p><pre id="trace"></pre><script>const data=DATA;const q=document.getElementById('choice'),a=document.getElementById('audio'),s=document.getElementById('slot'),p=document.getElementById('trace');for(const x of data)q.add(new Option(x.name,x.name));function draw(){const x=data.find(v=>v.name===q.value);p.textContent=JSON.stringify({condition:x.condition,metrics:x.metrics,trace:x.trace.slice(0,+s.value+1)},null,2)}q.onchange=()=>{a.src=q.value+'.wav';draw()};s.oninput=draw;q.onchange()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(examples)),encoding='utf-8')
    manifest={p.name:SHA(p.read_bytes()) for p in sorted(out.iterdir())}
    (out/'manifest.json').write_text(json.dumps(manifest,sort_keys=True),encoding='utf-8')
    print(json.dumps(dict(runs=len(rows),stats=stats,examples=[dict(name=x['name'],metrics=x['metrics']) for x in examples])))

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else 'transaction-output')
