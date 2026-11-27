"""Adversarial #448/#449: RTT suppression and observed-peer terminal repair.
Usage: python repair-scheduling.py PINNED_PACKAGE NEW_OUTPUT_DIR
Synthetic event transport only; no new acoustic or human evidence.
"""
import collections as C
import hashlib, json, pathlib, runpy, sys
PARENT='2a3693ff5a71b116b4280f6cfc872fdc4101bf09'
PARENT_SHA='050d4b84f7519f0afa46b525cad2a8b91f8f667c5d70bd0348bfc8f0ad58c202'
sha=lambda b:hashlib.sha256(b).hexdigest()

def variant(p,policy):
    assert sha(p.read_bytes())==PARENT_SHA
    src=p.read_text()
    if policy!='legacy':
        edits=[("n=counts.get((lane,p),0)","n=counts.get((lane,p),0)\n                    if t<counts.get((lane,p,'next'),0): continue"),
               ('counts[lane,p]=n+1','counts[lane,p]=n+1; counts[lane,p,\'next\']=t+2*lag')]
        if policy=='peer':
            edits.append(('n=counts.get((lane,p),0)',"if p=='terminal' and any((l,p) in seen for l in LANES if l!=lane): due=min(due,t)\n                    n=counts.get((lane,p),0)"))
        for a,b in edits:
            assert src.count(a)==1; src=src.replace(a,b)
    ns=dict(__name__='repair_variant'); exec(compile(src,str(p),'exec'),ns)
    return ns['repair']

def run(root,out):
    p=root/'active-repair.py'; assert sha(p.read_bytes())==PARENT_SHA
    a=runpy.run_path(str(p)); old=runpy.run_path(str(root/'retirement-ledger.py'))
    assert sha((root/'retirement-ledger.py').read_bytes())==a['SHA']
    src=root/'ensemble1/ensemble-traces.jsonl'; tr=root/'transport-binding.py'
    assert sha(src.read_bytes())==old['TRACE'] and sha(tr.read_bytes())==old['TRANSPORT']
    replay=old['variant'](root/'acquisition-local.py',4); transport=runpy.run_path(str(tr))
    captures=C.defaultdict(dict)
    for line in src.read_text().splitlines():
        z=json.loads(line); captures[z['pair'],z['condition']][z['mode']]=z
    policies={n:variant(p,n) for n in ('legacy','rtt','peer')}
    stats={}; rows=[]; prefixes=0
    for k,g in sorted(captures.items()):
        epoch=str(k); original=transport['envelopes']({l:g[l]['events'] for l in a['LANES']},epoch); want=C.Counter(map(tuple,g['bank']['expected']))
        for fault in ('clean','drop-start','drop-terminal'):
            wire=transport['fault'](original,fault)
            for loss,lag in ((0,640),(0,6400),(50,640),(50,6400)):
                for name,f in policies.items():
                    label=f'{fault}/{loss}/{lag}/{name}'; seed=448053000+k[0]*100+k[1]
                    d,log,peak=f(original,wire,epoch,3,loss,lag,seed)
                    ev,state=replay(d,a['H'],epoch); settled=old['signature'](ev)
                    got=C.Counter((e['source'],*e['identity']) for e in settled); auth=C.Counter((e['source'],*e['identity']) for e in settled if e['action_authorized'])
                    correct=sum((got&want).values()); authorized=sum((auth&want).values())
                    requests=sum(x[1].startswith('request') for x in log); responses=sum(x[1]=='response' for x in log)
                    s=stats.setdefault(label,C.Counter()); s.update(expected=sum(want.values()),correct=correct,authorized=authorized,wrong=sum(got.values())-correct,wrong_authorized=sum(auth.values())-authorized,requests=requests,responses=responses); s['peak']=max(s['peak'],peak)
                    if name!='legacy':
                        last={}
                        for x in log:
                            if x[1].startswith('request'):
                                slot=(x[2],x[3],x[4]); assert x[0]>=last.get(slot,-2*lag)+2*lag; last[slot]=x[0]
                    if loss==50 and lag==6400:
                        for t in (a['ACTION'],a['H']-1):
                            d1,l1,_=f(original,wire,epoch,3,loss,lag,seed,t)
                            assert d1==[m for m in d if m['arrival']<=t] and l1==[x for x in log if x[0]<=t]; prefixes+=1
                    rows.append(dict(capture=k,policy=label,correct=correct,authorized=authorized,wrong=sum(got.values())-correct,audit=log,settlements=settled,state=state))
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),trace_sha256=old['TRACE'],captures=len(captures),evaluations=len(rows),prefix_checks=prefixes,stats=stats,limits='Exploratory retained PCM event replay; new channel seed only. Known fixed RTT; no adaptive RTT estimation. Peer trigger uses delivered terminal evidence (including rejection), not hidden sender state. No new PCM, actual network, authentication, or fully bounded streaming. Observer retains complete groups until expiry; saturation not qualified.')
    out.mkdir(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
