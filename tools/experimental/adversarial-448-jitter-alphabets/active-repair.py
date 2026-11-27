"""Adversarial #448/#449: bounded request/response replay, not acoustic ARQ.
python active-repair.py PINNED_PACKAGE NEW_OUTPUT_DIR
Uses exact Run051 ledger; sender is a finite trace-backed oracle only for
previously emitted envelopes. No network, human evidence or authentication.
"""
import collections as C
import hashlib, json, pathlib, runpy, sys
PARENT='91e24ceb3430edb2243c0b7c41cfcfa4972af5a2'
SHA='f1a6d8cb4558760ce970652d3c19de2e8e823e0856505d2908773d39d08a69f1'
H=61440; ACTION=30720; RETAIN=51200; TICK=1280
LANES=('bank','fine'); START=('start','overflow-ready-protected')
def sha(b): return hashlib.sha256(b).hexdigest()
def key(m): return (m['event']['source'],m['origin'])
def slots(m):
    k=m['event']['kind']; return ('start',) if k=='start' else ('start','terminal') if k==START[1] else ('terminal',)
def draw(seed,*x): return int(sha(repr((seed,x)).encode())[:8],16)%100

def repair(original,wire,epoch,retries,loss,lag,seed,h=H):
    # Receiver observes delivered envelopes only; sender lookup happens at request arrival.
    incoming=C.defaultdict(list)
    for m in wire:
        if m['arrival']<=h: incoming[m['arrival']].append(m)
    sender={}; groups={}; requests=C.defaultdict(list); audit=[]; delivered=[]; peak=0
    emitted=C.defaultdict(list)
    for m in original: emitted[m['event']['sample']].append(m)
    times=set(incoming)|set(emitted)|set(range(0,h+1,TICK))
    while times:
        t=min(times); times.remove(t)
        if t>h: break
        for g in list(sender):
            if t>g[1]+RETAIN: del sender[g]
        for m in emitted[t]:
            g=key(m)
            if g not in sender and len(sender)>=4: continue
            d=sender.setdefault(g,{})
            for p in slots(m): d[m['lane'],p]=m
        for g in list(groups):
            if t>g[1]+RETAIN: del groups[g]
        for g,lane,p,n in requests.pop(t,[]):
            m=sender.get(g,{}).get((lane,p))
            result='unavailable' if m is None else 'response-lost' if draw(seed,g,lane,p,n,'response')<loss else 'response'
            audit.append([t,result,g,lane,p,n])
            if result=='response' and t+lag<=h:
                incoming[t+lag].append(dict(m,arrival=t+lag)); times.add(t+lag)
        for m in incoming.pop(t,[]):
            delivered.append(m); g=key(m)
            if m['epoch']!=epoch or t>g[1]+RETAIN: continue
            if g not in groups:
                if len(groups)>=4: continue
                groups[g]=[set(),{}]; peak=max(peak,len(groups))
            groups[g][0].update((m['lane'],p) for p in slots(m))
        if t%TICK: continue
        # At most two requests per tick, four tracked groups, four slots/group.
        budget=2
        for g,(seen,counts) in sorted(groups.items()):
            for lane in LANES:
                for p in ('start','terminal'):
                    due=g[1]+(TICK if p=='start' else ACTION)
                    n=counts.get((lane,p),0)
                    if not budget or (lane,p) in seen or t<due or n>=retries or t+2*lag>g[1]+RETAIN: continue
                    budget-=1; counts[lane,p]=n+1
                    lost=draw(seed,g,lane,p,n,'request')<loss
                    audit.append([t,'request-lost' if lost else 'request',g,lane,p,n])
                    if not lost and t+lag<=h: requests[t+lag].append((g,lane,p,n)); times.add(t+lag)
    return delivered,audit,peak

def run(root,out):
    p=root/'retirement-ledger.py'; assert sha(p.read_bytes())==SHA
    old=runpy.run_path(str(p)); q=root/'acquisition-local.py'; tr=root/'transport-binding.py'; src=root/'ensemble1/ensemble-traces.jsonl'
    assert sha(q.read_bytes())==old['LOCAL'] and sha(tr.read_bytes())==old['TRANSPORT'] and sha(src.read_bytes())==old['TRACE']
    replay=old['variant'](q,4); transport=runpy.run_path(str(tr)); captures=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); captures[z['pair'],z['condition']][z['mode']]=z
    stats={}; rows=[]; prefixes=0
    for k,g in sorted(captures.items()):
        epoch=str(k); original=transport['envelopes']({l:g[l]['events'] for l in LANES},epoch); want=C.Counter(map(tuple,g['bank']['expected']))
        for fault in ('clean','drop-start','drop-terminal','erase-group'):
            wire=transport['fault'](original,fault) if fault!='erase-group' else [m for m in original if key(m)!=key(original[0])]
            for retries,loss,lag in ((0,0,640),(1,0,640),(3,0,640),(3,50,640),(3,100,640),(3,0,6400)):
                label=f'{fault}/{retries}/{loss}/{lag}'; seed=448052000+k[0]*100+k[1]
                delivered,audit,peak=repair(original,wire,epoch,retries,loss,lag,seed)
                ev,state=replay(delivered,H,epoch); settled=old['signature'](ev)
                got=C.Counter((e['source'],*e['identity']) for e in settled); auth=C.Counter((e['source'],*e['identity']) for e in settled if e['action_authorized'])
                correct=sum((got&want).values()); authorized=sum((auth&want).values()); requests=sum(a[1].startswith('request') for a in audit)
                s=stats.setdefault(label,C.Counter()); s.update(expected=sum(want.values()),correct=correct,wrong=sum(got.values())-correct,authorized=authorized,wrong_authorized=sum(auth.values())-authorized,requests=requests,responses=sum(a[1]=='response' for a in audit)); s['peak']=max(s['peak'],peak)
                if retries==0: assert settled==old['signature'](replay(wire,H,epoch)[0])
                if retries==3 and loss==50 and lag==640:
                    for t in (ACTION,H//2+TICK,H-1):
                        d,a,_=repair(original,wire,epoch,retries,loss,lag,seed,t)
                        assert d==[m for m in delivered if m['arrival']<=t] and a==[x for x in audit if x[0]<=t]; prefixes+=1
                rows.append(dict(capture=k,policy=label,correct=correct,authorized=authorized,wrong=sum(got.values())-correct,audit=audit,settlements=settled,state=state))
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),trace_sha256=old['TRACE'],captures=len(captures),evaluations=len(rows),prefix_checks=prefixes,stats=stats,limits='Retained synthetic event replay, no new PCM. Trusted sender history, no actual transport. Four observed groups and four sender groups retained through origin+retention; completed groups also consume observer capacity. Two requests per tick; retries are consecutive ticks, not RTT-adaptive. Batch queues and logs not bounded. No recovery of wholly unseen groups by repair alone.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
