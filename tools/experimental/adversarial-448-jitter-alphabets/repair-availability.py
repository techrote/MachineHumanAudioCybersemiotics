"""Adversarial #448/#449: explicit cache-miss replies, bounded probe budgets.
Usage: python repair-availability.py PINNED_PACKAGE NEW_OUTPUT_DIR
Synthetic event replay only. A cache miss does not prove future availability.
"""
import collections as C
import hashlib, json, pathlib, runpy, sys
PARENT='85503b2f2ffb8a665b095482eaa1882df665dd05'
SCHEDULE='588ccac9679f450d77ad0618c8562b9b5b17a519f45f3fe1e18e311f57a6166e'
sha=lambda b:hashlib.sha256(b).hexdigest()

def variant(p, parent, policy):
    if policy in ('peer3','peer6','rtt3'):
        f=parent['variant'](p,'rtt' if policy=='rtt3' else 'peer')
        return lambda *args: f(*args[:3],6 if policy=='peer6' else 3,*args[3:])
    src=p.read_text(); assert sha(p.read_bytes())==parent['PARENT_SHA']
    edits=[('sender={}; groups={};','feedback=C.defaultdict(list); sender={}; groups={};'),
           ('if result==\'response\' and t+lag<=h:', '''if result=='unavailable' and t+lag<=h:
                if draw(seed,g,lane,p,n,'response')>=loss:
                    feedback[t+lag].append((g,lane,p,n)); times.add(t+lag)
                else: audit.append([t,'miss-reply-lost',g,lane,p,n])
            if result=='response' and t+lag<=h:'''),
           ('if t%TICK: continue', '''for g,lane,p,n in feedback.pop(t,[]):
            audit.append([t,'miss-reply',g,lane,p,n])
            if g in groups:
                counts=groups[g][1]; slot=(lane,p)
                counts[lane,p,'refund']=counts.get((lane,p,'refund'),0)+1
                counts[lane,p,'next']=max(counts.get((lane,p,'next'),0),t+2*TICK)
        if t%TICK: continue'''),
           ('n=counts.get((lane,p),0)', '''if p=='terminal' and any((l,p) in seen for l in LANES if l!=lane): due=min(due,t)
                    n=counts.get((lane,p),0)
                    if t<counts.get((lane,p,'next'),0) or n>=6: continue
                    spent=n-counts.get((lane,p,'refund'),0)'''),
           ('n>=retries','spent>=retries'),
           ('counts[lane,p]=n+1',"counts[lane,p]=n+1; counts[lane,p,'next']=t+2*lag")]
    for a,b in edits:
        assert src.count(a)==1; src=src.replace(a,b)
    ns={'__name__':'availability_variant'}; exec(compile(src,str(p),'exec'),ns)
    return lambda *args: ns['repair'](*args[:3],3,*args[3:])

def run(root,out):
    s=root/'repair-scheduling.py'; assert sha(s.read_bytes())==SCHEDULE
    parent=runpy.run_path(str(s)); p=root/'active-repair.py'; assert sha(p.read_bytes())==parent['PARENT_SHA']
    a=runpy.run_path(str(p)); old=runpy.run_path(str(root/'retirement-ledger.py')); assert sha((root/'retirement-ledger.py').read_bytes())==a['SHA']
    q=root/'acquisition-local.py'; tr=root/'transport-binding.py'; src=root/'ensemble1/ensemble-traces.jsonl'
    assert sha(q.read_bytes())==old['LOCAL'] and sha(tr.read_bytes())==old['TRANSPORT'] and sha(src.read_bytes())==old['TRACE']
    replay=old['variant'](q,4); transport=runpy.run_path(str(tr)); captures=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); captures[z['pair'],z['condition']][z['mode']]=z
    policies={n:variant(p,parent,n) for n in ('rtt3','peer3','peer6','miss-aware')}
    stats={}; rows=[]; prefixes=0
    for k,g in sorted(captures.items()):
        epoch=str(k); original=transport['envelopes']({l:g[l]['events'] for l in a['LANES']},epoch); want=C.Counter(map(tuple,g['bank']['expected']))
        for fault in ('clean','drop-start','drop-terminal'):
            wire=transport['fault'](original,fault)
            for loss,lag in ((0,640),(0,6400),(50,640),(50,6400)):
                for name,f in policies.items():
                    label=f'{fault}/{loss}/{lag}/{name}'; seed=448053000+k[0]*100+k[1]
                    d,log,peak=f(original,wire,epoch,loss,lag,seed)
                    settled=old['signature'](replay(d,a['H'],epoch)[0]); got=C.Counter((e['source'],*e['identity']) for e in settled); auth=C.Counter((e['source'],*e['identity']) for e in settled if e['action_authorized'])
                    correct=sum((got&want).values()); authorized=sum((auth&want).values()); wrong=sum(got.values())-correct
                    counts=C.Counter(x[1] for x in log); requests=counts['request']+counts['request-lost']; st=stats.setdefault(label,C.Counter()); st.update(expected=sum(want.values()),correct=correct,authorized=authorized,wrong=wrong,wrong_authorized=sum(auth.values())-authorized,requests=requests,miss_replies=counts['miss-reply'],unavailable=counts['unavailable']); st['peak']=max(st['peak'],peak)
                    per=C.Counter((tuple(x[2]),x[3],x[4]) for x in log if x[1].startswith('request')); assert max(per.values(),default=0)<=(3 if name in ('peer3','rtt3') else 6)
                    if name=='miss-aware':
                        for t in (a['ACTION'],a['H']-1):
                            dd,ll,_=f(original,wire,epoch,loss,lag,seed,t); assert dd==[m for m in d if m['arrival']<=t] and ll==[x for x in log if x[0]<=t]; prefixes+=1
                    rows.append(dict(capture=k,policy=label,correct=correct,authorized=authorized,wrong=wrong,requests=requests,audit=log,settlements=settled))
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),trace_sha256=old['TRACE'],evaluations=len(rows),prefix_checks=prefixes,stats=stats,limits='Exploratory retained PCM/event replay; same Run053 channel seed. Cache miss reply is not proof of pending evidence. Delivered misses refund effective attempt only; maximum six requests per slot, two/tick, four groups, fixed RTT and 160ms miss backoff. Peer6 matches hard request ceiling, not actual traffic. Reply loss uses same response draw; no real network, capacity stress, authentication or human evidence.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
