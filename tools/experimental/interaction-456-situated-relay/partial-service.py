"""Interaction #456 / #457: partial service under surprise current traffic.
Synthetic only; no human evidence, real devices, authentication or Grammar interoperability.
Run: python partial-service.py NEW_OUTPUT_DIR (Python 3.11+, standard library).
"""
import itertools, json, math, random, struct, sys, wave, hashlib
from functools import lru_cache
from pathlib import Path

PARENT = 'b42943bae17b2d5478e747d1a146ce5169f2ae7a'
MAIN = '495a98ca12bae467a507031f04931aa4254b1866'
POLICIES = ('opportunistic', 'strict', 'partial')
TOKENS = ('repair','receipt','report','report_ack','query','negative','positive','archive_ack','current')
H, RATE, SLOT, N = 12, 8000, 1600, 320
BANK = tuple(tuple(math.sin(2*math.pi*(400+100*k)*i/RATE) for i in range(N)) for k in range(len(TOKENS)))
def sha(b): return hashlib.sha256(b).hexdigest()

@lru_cache(maxsize=4096)
def pcm(token, seed, tick, lost):
    rng = random.Random(seed*1009+tick)
    w = tuple(round((0 if lost else 1200*v)+rng.randint(-20,20)) for v in BANK[TOKENS.index(token)])
    z = [abs(sum(v*s for v,s in zip(b,w))) for b in BANK]
    k = max(range(len(z)),key=z.__getitem__)
    decoded = TOKENS[k] if z[k]>50000 and z[k]>4*max(z[:k]+z[k+1:]) else None
    assert decoded == (None if lost else token)
    b = struct.pack('<%dh'%N,*w)
    return decoded, sha(b), w

def simulate(c, policy, horizon=H, audio=False):
    assert policy in POLICIES and 0 <= horizon <= H
    state = dict(receipt=False, disputed=False, report_ack=False, positive=False, archive_ack=False)
    attempts = dict(A=0,B=0,C=0,D=0); ready = dict(A=0,B=0,C=0,D=0)
    counts = {}; tx = None; spent = current = exposure = 0; trace = []; starts = []
    samples = [0]*(SLOT*horizon) if audio else None
    for t in range(horizon):
        token = None; rejected = []; event = None
        # Surprise traffic is revealed only at this slot. Future forecast uses announced slots only.
        if t in c['announced'] or t in c['surprise']:
            token = 'current'
        elif spent < c['cap']:
            if tx is None:
                expiry = c['advert']
                can = dict(A=not state['receipt'], B=not state['positive'] and (expiry is None or t<expiry), C=c['rival'] and not state['report_ack'], D=state['positive'] and not state['archive_ack'])
                order = ('B','C','D','A') if expiry is not None and t+3>=expiry else ('C','B','D','A')
                for k in order:
                    if not can[k] or attempts[k]>=2 or t<ready[k]: continue
                    need = {'A':2,'B':2 if policy=='partial' else 3,'C':2,'D':1}[k]
                    slots = sum(s not in c['announced'] for s in range(t,H))
                    if policy!='opportunistic' and min(c['cap']-spent,slots)<need:
                        rejected.append(k); continue
                    attempts[k]+=1; tx = (k,{'A':'repair','B':'query','C':'report','D':'archive_ack'}[k])
                    starts.append(dict(t=t,kind=k,need=need,remaining=c['cap']-spent,forecast=slots)); break
            if tx: token = tx[1]
        if token:
            counts[token]=counts.get(token,0)+1
            lost = c['loss']==token and counts[token]==1
            decoded,digest,w = pcm(token,c['seed'],t,lost)
            if audio: samples[t*SLOT:t*SLOT+N]=w
            event=dict(token=token,decoded=decoded,sha256=digest)
            if token=='current': current+=1
            else:
                spent+=1; k=tx[0]; nxt=None
                if decoded=='repair': nxt='receipt'
                elif decoded=='receipt': state['receipt']=True
                elif decoded=='report': state['disputed']=True; nxt='report_ack'
                elif decoded=='report_ack': state['report_ack']=True
                elif decoded=='query': nxt='positive' if c['start']<=t<c['expiry'] else 'negative'
                elif decoded=='positive':
                    state['positive']=True
                    if policy!='partial': nxt='archive_ack'
                elif decoded=='archive_ack': state['archive_ack']=True
                tx=(k,nxt) if nxt else None
                if not nxt: ready[k]=t+2
        exposure+=int(c['rival'] and not state['disputed'])
        assert spent<=c['cap'] and (not state['archive_ack'] or state['positive']) and (not state['report_ack'] or state['disputed'])
        trace.append(dict(t=t,event=event,state=dict(state),pending=tx,spent=spent,rejected=rejected))
    metrics=dict(**{k:int(v) for k,v in state.items()},spent=spent,current=current,exposure=exposure,unfinished=int(tx is not None),debt=int(state['positive'] and not state['archive_ack']),unacquired=int(tx is not None and tx[1] in ('positive','negative')))
    return dict(condition=c,policy=policy,metrics=metrics,starts=starts,trace=trace),samples

def conditions():
    for seed,start,duration,mode,rival,loss,announced,shock,cap in itertools.product((221071,221073),(1,4,7),(2,4),('exact','early','missing'),(False,True),('none','positive','archive_ack','report'),((2,5,8),(0,2,4,6,8,10)),(False,True),(3,5,7)):
        expiry=start+duration
        surprise=tuple(t for t in (9,11) if shock and t not in announced)
        yield dict(seed=seed,start=start,expiry=expiry,advert={'exact':expiry,'early':expiry-2,'missing':None}[mode],rival=rival,loss=loss,announced=announced,surprise=surprise,cap=cap)

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    for token in TOKENS:
        for lost in (False,True): pcm(token,1,0,lost)
    stats={}; rows=[]; examples={}; paired=dict(equal=0,partial_more=0,strict_more=0,partial_ack_less=0); checks=0
    for c in conditions():
        group={}
        for policy in POLICIES:
            row,_=simulate(c,policy); m=row['metrics']; group[policy]=m; rows.append(row)
            # Causal prefix: changing future surprise arrivals cannot affect earlier output.
            alt=dict(c,surprise=())
            prefix=min(c['surprise'],default=H)
            other,_=simulate(alt,policy,prefix)
            assert row['trace'][:prefix]==other['trace']; checks+=1
            assert m['current']==len(set(c['announced'])|set(c['surprise']))
            if policy!='opportunistic' and not c['surprise']: assert not m['unfinished']
            key=f"{c['cap']}/{bool(c['surprise'])}/{policy}"
            agg=stats.setdefault(key,{'runs':0}); agg['runs']+=1
            for k,v in m.items(): agg[k]=agg.get(k,0)+v
        p,s=group['partial'],group['strict']
        if p['spent']==s['spent']:
            paired['equal']+=1; paired['partial_more']+=p['positive']>s['positive']; paired['strict_more']+=s['positive']>p['positive']; paired['partial_ack_less']+=p['archive_ack']<s['archive_ack']
            if p['positive']>s['positive'] and 'gain' not in examples: examples['gain']=c
            if s['positive']>p['positive'] and 'regression' not in examples: examples['regression']=c
        if c['surprise'] and s['unfinished'] and 'shock' not in examples: examples['shock']=c
        if p['debt'] and c['loss']=='archive_ack' and 'debt' not in examples: examples['debt']=c
    gallery=[]
    for name,c in examples.items():
        for policy in POLICIES:
            r,w=simulate(c,policy,audio=True); label=name+'-'+policy
            with wave.open(str(out/(label+'.wav')),'wb') as f:
                f.setparams((1,2,RATE,0,'NONE','not compressed')); f.writeframes(struct.pack('<%dh'%len(w),*w))
            gallery.append(dict(name=label,**r))
    receipt=dict(schema='mhac-interaction-partial-service-v1',parent=PARENT,main=MAIN,units=dict(slot_ms=200,body_ms=40,rate=RATE),stats=stats,paired=paired,causal_checks=checks,rows=rows,examples=gallery)
    (out/'receipt.json').write_text(json.dumps(receipt,separators=(',',':')),encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Partial service</title><h1>Situated partial service</h1><p>Synthetic dialogue. Positive evidence and receipt settlement are separate. Start at low volume. No autoplay.</p><label>Scenario and policy <select id="choice"></select></label><p><audio id="audio" controls preload="none"></audio></p><label>Slot <input id="slot" type="range" min="0" max="11" value="11"></label><pre id="trace"></pre><script>const data=DATA;const q=document.getElementById('choice'),a=document.getElementById('audio'),s=document.getElementById('slot'),p=document.getElementById('trace');for(const x of data)q.add(new Option(x.name,x.name));function draw(){const x=data.find(v=>v.name===q.value);p.textContent=JSON.stringify({condition:x.condition,final_metrics:x.metrics,trace:x.trace.slice(0,+s.value+1)},null,2)}q.onchange=()=>{a.pause();a.src=q.value+'.wav';draw()};s.oninput=draw;a.volume=.2;q.onchange()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(gallery)),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},sort_keys=True),encoding='utf-8')
    print(json.dumps(dict(runs=len(rows),causal_checks=checks,stats=stats,paired=paired,examples=examples)))

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else 'partial-output')
