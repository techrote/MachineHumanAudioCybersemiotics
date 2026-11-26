"""Refs #456 / Draft #457. Synthetic symbolic dialogue, not acoustic decoding.
Interface inspected: #453 b9c0af501b38ac516f194a362c8688c95657b32b
(ambiguity-admission.py, status/count/ids); balanced query inspiration:
#453 60b7f27f7260d1a8ac00be5c3d13dc853a00a72c (discriminating-reply.py).
No runtime upstream dependency; full replies and fault models are stand-ins.
"""
import argparse, collections, hashlib, html, json, math, pathlib, random, struct, wave

POLICIES = ('first', 'unique', 'balanced', 'full', 'double-full')
FAULTS = ('clean', 'missing', 'overflow', 'narrowed', 'lost', 'late', 'stale', 'corrupt', 'common', 'mixed')
SEED = 4564000

def fixture(seed, fault):
    rng = random.Random(seed)
    rows = []
    for a in range(2):
        target = rng.randrange(16)
        ids = sorted([target] + rng.sample([i for i in range(16) if i != target], (1, 3, 7)[seed % 3]))
        rival = next(i for i in ids if i != target)
        status = 'ambiguous'
        if fault == 'missing': status, ids = 'none', []
        if fault == 'overflow': status, ids = 'overflow', []
        if fault == 'narrowed': status, ids = 'unique', [rival]
        plan = []
        for attempt in range(4):
            kind = rng.choice(('clean','clean','lost','late','corrupt','stale')) if fault == 'mixed' else fault
            plan.append(dict(kind=kind, delay=9 if kind == 'late' else 2, wrong=rival))
        rows.append(dict(target=target, report=dict(status=status,count=12 if status=='overflow' else len(ids),ids=ids), plan=plan, deadline=7+4*a, arrival=2*a))
    return rows

def simulate(rows, policy):
    states = [dict(ids=list(r['report']['ids']), pending=None, tries=0, votes=[], action=None, stopped=False) for r in rows]
    events, cost = [], 0
    def log(t,a,kind,**kw): events.append(dict(slot=t,agent=a,kind=kind,**kw))
    for t in range(12):
        for a,(r,s) in enumerate(zip(rows,states)):
            if t == r['arrival']: log(t,a,'report',report=r['report'])
            p=s['pending']
            if p and p['due']==t:
                s['pending']=None
                kind=p['fault']['kind']; val=p['fault']['wrong'] if kind in ('corrupt','common') and (kind=='common' or p['attempt']==0) else r['target']
                if kind=='lost': log(t,a,'timeout',qid=p['qid']); continue
                qid=p['qid']-1 if kind=='stale' else p['qid']
                if qid!=p['qid'] or t>=r['deadline']:
                    log(t,a,'rejected',qid=qid,expected=p['qid'],reason='correlation' if qid!=p['qid'] else 'deadline'); continue
                if p['bit'] is not None:
                    bit=p['bit']; s['ids']=[i for i in s['ids'] if (i>>bit)&1==(val>>bit)&1]
                else:
                    s['votes'].append(val)
                    if policy=='full' or len(s['votes'])==2 and s['votes'][0]==s['votes'][1]: s['ids']=[val]
                    else: s['ids']=[]
                log(t,a,'reply',qid=qid,ids=s['ids'][:],votes=s['votes'][:])
            if not r['arrival']<=t<r['deadline'] or s['stopped']: continue
            ready=bool(s['ids']) and (policy=='first' or len(s['ids'])==1 and (policy in ('unique','balanced') or policy=='full' and s['votes'] or policy=='double-full' and len(s['votes'])==2))
            if ready:
                s['action']=s['ids'][0]; s['stopped']=True; log(t,a,'act',identity=s['action']); continue
            if policy in ('first','unique') or policy=='balanced' and len(s['ids'])<2 or policy=='double-full' and len(s['votes'])>=2: s['stopped']=True
        # One query start per slot, earliest deadline first; reserve its symbolic cost.
        for a,(r,s) in enumerate(zip(rows,states)):
            charge=1 if policy=='balanced' else 2
            if s['stopped'] or s['pending'] or not r['arrival']<=t<r['deadline'] or s['tries']>=4 or cost+charge>6: continue
            bit=None
            if policy=='balanced':
                bit=min(range(4),key=lambda b: max(sum((i>>b)&1 for i in s['ids']),sum(not ((i>>b)&1) for i in s['ids'])))
            attempt=s['tries']; f=r['plan'][attempt]; qid=100*a+attempt+1
            s['tries']+=1; cost+=charge; s['pending']=dict(qid=qid,attempt=attempt,bit=bit,fault=f,due=t+f['delay']+charge-1)
            log(t,a,'query',qid=qid,bit=bit,cost=charge,due=s['pending']['due']); break
    metrics=collections.Counter(cost=cost)
    for a,(r,s) in enumerate(zip(rows,states)):
        m='abstain' if s['action'] is None else 'correct' if s['action']==r['target'] else 'wrong'; metrics[m]+=1; metrics[m+str(a)]+=1
        acts=[e for e in events if e['agent']==a and e['kind']=='act']; assert len(acts)<=1 and all(e['slot']<r['deadline'] for e in acts)
    assert cost<=6 and cost==sum(e['cost'] for e in events if e['kind']=='query')
    return dict(metrics=dict(metrics),events=events,fixture=rows,policy=policy)

def generate(out):
    out.mkdir(parents=True,exist_ok=False); summary={}; traces=[]; hashes=[]
    for fault in FAULTS:
        for policy in POLICIES:
            c=collections.Counter()
            for seed in range(SEED,SEED+64):
                rows=fixture(seed,fault); r=simulate(rows,policy); assert r==simulate(rows,policy); c.update(r['metrics']); hashes.append(hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest())
                if seed==SEED: traces.append(dict(fault=fault,**r))
            assert sum(c[x] for x in ('correct','wrong','abstain'))==128; summary[fault+':'+policy]=dict(c)
    receipt=dict(schema='mhac-situated-ambiguity-v1',seed=SEED,cases=len(hashes),summary=summary,hashes=hashes)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.json').write_text(json.dumps(traces,indent=2)+'\n')
    for fault in ('clean','corrupt','common'):
        r=next(x for x in traces if x['fault']==fault and x['policy']=='double-full'); samples=[0]*24000
        for e in r['events']:
            freq={'report':330,'query':440,'reply':550,'act':660,'rejected':220,'timeout':165}[e['kind']]+e['agent']*110
            for i in range(800): samples[e['slot']*2000+i]+=round(500*math.sin(2*math.pi*freq*i/8000)*min(i/80,(799-i)/80,1))
        with wave.open(str(out/(fault+'.wav')),'wb') as w: w.setparams((1,2,8000,0,'NONE','not compressed')); w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
    page='<!doctype html><meta charset="utf-8"><title>Situated ambiguity</title><h1>Situated ambiguity</h1><p>Synthetic symbolic transport. No human evidence. Select a trace, then step through slots. Audio is event sonification only.</p><select id="case"></select> <input id="slot" type="range" min="0" max="11" value="11"><output id="time"></output><pre id="trace"></pre>'
    for fault in ('clean','corrupt','common'): page+=f'<p>{fault} / double-full <audio controls preload="none" src="{fault}.wav"></audio></p>'
    page+='<p><a href="receipt.json">Receipt</a> | <a href="traces.json">Trace export</a></p><script>const rows='+json.dumps(traces)+';const c=document.getElementById("case"),s=document.getElementById("slot");rows.forEach((r,i)=>c.add(new Option(r.fault+" / "+r.policy,i)));function show(){const r=rows[+c.value];document.getElementById("time").textContent=s.value;document.getElementById("trace").textContent=JSON.stringify({fixture:r.fixture,events:r.events.filter(e=>e.slot<=+s.value),final:r.metrics},null,2)}c.onchange=s.oninput=show;show();document.querySelectorAll("audio").forEach(a=>a.volume=.2)</script>'
    (out/'index.html').write_text(page); (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('output',nargs='?'); p.add_argument('--scenario',nargs=3); a=p.parse_args()
    if a.scenario:
        fault,policy,seed=a.scenario; assert fault in FAULTS and policy in POLICIES; print(json.dumps(simulate(fixture(int(seed),fault),policy),indent=2))
    else: generate(pathlib.Path(a.output))
