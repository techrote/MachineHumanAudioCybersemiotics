"""MHAC Adversarial #448: synthetic repair lifecycle/capacity stress, not PCM.
Run: python lifecycle-pressure.py NEW_OUTPUT_DIR
Time unit 80 ms. Single missing terminal per known acquisition; no human evidence.
"""
import collections as C
import hashlib, json, pathlib, random, sys

PARENT = '3d52af448ea3904ce96e04ef001f3dcb60bd6172'
ACTION, RETAIN, H = 24, 40, 200
POLICIES = ('generic-hold', 'typed-hold', 'generic-reclaim', 'typed-reclaim')

def draw(seed, *args):
    return int.from_bytes(hashlib.sha256(repr((seed, args)).encode()).digest()[:4], 'big') % 100

def make(seed, spacing):
    r = random.Random(seed)
    return [(i, i*spacing, i*spacing+r.randint(3, 22), r.randrange(5)==0) for i in range(24)]

def simulate(jobs, seed, policy, capacity, loss, lag, horizon=H):
    # Known starts, no identity guessing. One immutable terminal per acquisition.
    typed, reclaim = policy.startswith('typed'), policy.endswith('reclaim')
    cache, meta, observer = {}, {}, {}
    pipe = C.defaultdict(list); audit = []; result = {}; peak = [0,0,0,0]
    # jobs is the external stimulus schedule, not receiver memory.
    def record(t, kind, i, *rest): audit.append([t,kind,i,*rest])
    def bounded_put(d, i, val, cap):
        if i not in d and len(d)==cap: del d[next(iter(d))]
        d[i]=val
    def settle(t,i,status,via):
        if i not in observer or observer[i]['done']: return
        o=observer[i]; o['done']=True
        if status in ('value','cancelled'):
            result[i]=(status,t,t<=o['start']+ACTION and status=='value')
        record(t,'settle' if status in ('value','cancelled') else 'unrecoverable',i,status,via)
        if reclaim: del observer[i]
    for t in range(horizon+1):
        for i,o in list(observer.items()):
            if t>o['start']+RETAIN: del observer[i]
        for i,start,end,cancel in jobs:
            if t==start:
                bounded_put(meta,i,'pending',capacity*2)
                if len(observer)<capacity:
                    observer[i]=dict(start=start,done=False,n=0,spent=0,next=start+6)
                    record(t,'admit',i)
                else: record(t,'observer-refusal',i)
            if t==end:
                # An evicted terminal will never be reinserted; metadata may be evicted too.
                if cancel: bounded_put(meta,i,'cancelled',capacity*2)
                else:
                    if len(cache)==capacity:
                        old=next(iter(cache)); del cache[old]
                        if old in meta: meta[old]='evicted'
                        record(t,'cache-evict',old)
                    cache[i]='value'; bounded_put(meta,i,'emitted',capacity*2)
                record(t,'emit',i,'cancelled' if cancel else 'value')
                if draw(seed,i,'primary')>=65: settle(t,i,'cancelled' if cancel else 'value','primary')
        for kind,i,n,status in pipe.pop(t,[]):
            if kind=='request':
                # No inspection of future jobs. Unknown means metadata unavailable.
                status=cache.get(i,meta.get(i,'unknown'))
                if status=='emitted': status='evicted'
                if not typed and status!='value': status='miss'
                record(t,'reply-sent',i,n,status)
                if draw(seed,i,n,'response')>=loss: pipe[t+lag].append(('reply',i,n,status))
                else: record(t,'reply-lost',i,n,status)
            else:
                record(t,'reply-arrived',i,n,status)
                o=observer.get(i)
                if o is None or o['done']: continue
                if status in ('value','cancelled','evicted'): settle(t,i,status,'repair')
                elif status in ('pending','miss'):
                    o['spent']-=1; o['next']=max(o['next'],t+2)
                # Unknown is not evidence of impossibility, consumes credit.
        budget=2
        for i,o in sorted(observer.items()):
            if not budget or o['done'] or o['n']>=6 or o['spent']>=3 or t<o['next'] or t+2*lag>o['start']+RETAIN: continue
            n=o['n']; o['n']+=1; o['spent']+=1; o['next']=t+2*lag; budget-=1
            record(t,'request',i,n)
            if draw(seed,i,n,'request')>=loss: pipe[t+lag].append(('request',i,n,None))
            else: record(t,'request-lost',i,n)
        for k,v in enumerate((len(cache),len(meta),len(observer),sum(map(len,pipe.values())))): peak[k]=max(peak[k],v)
    assert peak[0]<=capacity and peak[1]<=2*capacity and peak[2]<=capacity and peak[3]<=4*lag
    for i,status in result.items():
        assert status[0]==('cancelled' if jobs[i][3] else 'value') and status[1]>=jobs[i][2]
    counts=C.Counter(x[1] for x in audit); replies=C.Counter(x[4] for x in audit if x[1]=='reply-arrived')
    metrics=dict(values=sum(s[0]=='value' for s in result.values()),timely=sum(s[2] for s in result.values()),cancelled=sum(s[0]=='cancelled' for s in result.values()),requests=counts['request'],replies=counts['reply-sent'],refusals=counts['observer-refusal'],evictions=counts['cache-evict'],received_status=dict(replies),peak=peak)
    return metrics,audit,result

def run(out):
    # Fixed exploratory seeds, no optimization; second block reported separately.
    rows=[]; aggregates={}; checks=0
    for block,base in [('development',448055000),('evaluation',448055100)]:
        for seed in range(base,base+16):
            for spacing in (2,6):
                jobs=make(seed,spacing)
                for cap in (2,4,8):
                    for loss,lag in ((0,1),(35,1),(35,5)):
                        for policy in POLICIES:
                            m,a,r=simulate(jobs,seed,policy,cap,loss,lag)
                            for h in (25,75):
                                _,prefix,_=simulate(jobs,seed,policy,cap,loss,lag,h)
                                assert prefix==[x for x in a if x[0]<=h]; checks+=1
                            label=f'{block}/{spacing}/{cap}/{loss}/{lag}/{policy}'
                            s=aggregates.setdefault(label,C.Counter()); s.update({k:v for k,v in m.items() if isinstance(v,int)}); s['expected_values']+=sum(not j[3] for j in jobs)
                            rows.append(dict(label=label,seed=seed,jobs=jobs,metrics=m,audit=a,result=r))
    out.mkdir(); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,evaluations=len(rows),prefix_checks=checks,aggregates=aggregates,limitations='Synthetic single-slot repair only. All starts visible, known RTT, trusted IDs/statuses, fixed terminal loss 65%, 80ms ticks, no authentication, no PCM or human data. No independent review. Stimulus and audit unbounded; only cache, metadata, observer and in-flight messages bounded.'),indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())},indent=2)+'\n')

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
