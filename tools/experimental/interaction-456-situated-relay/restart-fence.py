"""Interaction #456, Run 030: synthetic restart and receipt lifecycle.
Run: python restart-fence.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR
Requires sibling activation-fence.py and its pinned NumPy inputs.
DONE is a symbolic stand-in, not an allocated acoustic grammar word.
"""
import hashlib, itertools, json, pathlib, runpy, sys
from collections import Counter, defaultdict
PARENT='2bd38aef335bdcf7bdc7cd31a17e58929b695f10'
BASE='495a98ca12bae467a507031f04931aa4254b1866'
H=120
POLICIES=('volatile','version-only','journal','journal-done','fail-closed-done')
REGIMES=('clean','mixed','early-B','early-A','late-B','late-A','lost-B','done-loss','overrun')
CRASH={'early-B':(14,1),'early-A':(14,0),'late-B':(60,1),'late-A':(60,0),'lost-B':(60,1)}
def dump(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def gitblob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def simulate(seed,D,regime,policy,ids):
    # Phase, version, acceptance time, completion time, receipt stopped.
    initial=('old',0,-1,-1,False)
    state=[initial,initial]; disk=[initial,initial]; q=defaultdict(list)
    tr=[]; c=Counter(); ordinal=Counter(); done=policy.endswith('done')
    def event(t,e,**kw): tr.append(dict(t=t,event=e,**kw))
    def setstate(t,s,value):
        state[s]=value
        if policy!='volatile':
            disk[s]=value if policy!='version-only' else ('new' if value[1] else 'old',value[1],-1,-1,False)
        event(t,'transition',s=s,state=value,disk=disk[s])
    def send(t,s,k):
        n=ordinal[s,k]; ordinal[s,k]+=1
        h=int.from_bytes(hashlib.sha256(dump([seed,s,k,n])).digest()[:8],'big')
        delays=[1] if regime=='clean' else [1+h%min(D,3)]
        if regime!='clean' and h%3==0: delays.append(4*D if regime=='overrun' else D)
        if regime!='clean' and h%7==0 or regime=='done-loss' and k=='DONE': delays=[]
        origin=state[s][1] if k in ids else None
        c['send_'+k]+=1
        event(t,'send',s=s,k=k,origin=origin,delays=delays)
        for d in delays: q[t+d].append((s,k,origin,t))
    for t in range(H):
        if CRASH.get(regime,(None,None))[0]==t:
            s=CRASH[regime][1]
            if regime=='lost-B': disk[s]=None
            state[s]=disk[s] or (('recovery',0,-1,-1,False) if policy=='fail-closed-done' else initial)
            event(t,'restart',s=s,state=state[s],disk=disk[s])
        if t==8: setstate(t,0,('proposing',0,-1,-1,False))
        for s,k,origin,emitted in q.pop(t,[]):
            r=1-s; p,v,a,f,z=state[r]
            event(t,'arrival',s=s,k=k,origin=origin,emitted=emitted)
            if k in ids:
                result='gated' if p not in ('old','new') else 'correct' if ids[k][v]==ids[k][origin] else 'wrong'
                c[result]+=1; event(t,'payload',r=r,k=k,outcome=result,version=v,origin=origin,emitted=emitted)
            elif r==1 and k=='PROPOSE' and p=='old': setstate(t,r,('accepting',0,-1,-1,False))
            elif r==0 and k=='ACCEPT' and p=='proposing': setstate(t,r,('committing',0,t,-1,False))
            elif r==1 and k=='COMMIT' and p=='accepting': setstate(t,r,('new',1,-1,t,False))
            elif r==0 and k=='RECEIPT' and p=='committing':
                setstate(t,r,('new',1,a,t,False)); c['completed']+=1
            elif r==1 and k=='DONE' and p=='new' and done and not z:
                setstate(t,r,(p,v,a,f,True)); c['receipt_stopped']+=1
        c['split_slots']+=int(state[0][1]!=state[1][1])
        c['recovery_slots']+=sum(x[0]=='recovery' for x in state)
        for s,(p,v,a,f,z) in enumerate(state):
            k=None
            if s==0 and p=='proposing' and (t-8)%3==0: k='PROPOSE'
            if s==0 and p=='committing' and t>=a+D+1 and (t-a-D-1)%3==0: k='COMMIT'
            if s==1 and p=='accepting' and t%3==0: k='ACCEPT'
            if s==1 and p=='new' and not z and t%3==0: k='RECEIPT'
            if s==0 and done and p=='new' and 0<=t-f<=6 and (t-f)%3==0: k='DONE'
            if k is None and p in ('old','new') and t%3==s: k='alias' if (t//3)%2==0 else 'shared'
            if k: send(t,s,k)
        event(t,'state',state=state.copy())
    c['both_new_end']=int(all(x[0]=='new' for x in state)); c['pending']=sum(map(len,q.values()))
    assert sum(c[k] for k in ('correct','wrong','gated'))==sum(e['event']=='arrival' and e['k'] in ids for e in tr)
    assert sum(len(e['delays']) for e in tr if e['event']=='send')==c['pending']+sum(e['event']=='arrival' for e in tr)
    return dict(c),tr

def run(root,out):
    parent=pathlib.Path(__file__).with_name('activation-fence.py')
    assert gitblob(parent.read_bytes())=='61cfb9149e34eabff98dc8caf2080fce44ec7a46'
    pins={'version-bridge.py':'6400cf4c1b42fbe958b0265da43ef657bb355401','control-namespace.py':'8e27fe89f2734a0b5fd666bb2018b0d379736493','migration-namespace.py':'b3562781a974c47b41cbe066ceb755288a51b6b1','distributed-profile.py':'a780404e8c76820976ad6fb407429ec895a6313f'}
    for p,b in pins.items(): assert gitblob((root/p).read_bytes())==b
    upstream=runpy.run_path(str(parent)); words,ids,audio=upstream['inputs'](root)
    out.mkdir(parents=True,exist_ok=False); totals={}; rows=[]; witnesses={}
    for seed,D,regime,policy in itertools.product(range(4563000,4563016),(3,8,15),REGIMES,POLICIES):
        c,tr=simulate(seed,D,regime,policy,ids); k=regime+'/'+policy
        totals.setdefault(k,Counter()).update(c)
        rows.append(dict(seed=seed,D=D,regime=regime,policy=policy,metrics=c,trace_sha256=sha(dump(tr))))
        if k not in witnesses or c.get('wrong',0)>0 and not witnesses[k]['metrics'].get('wrong',0): witnesses[k]=dict(seed=seed,D=D,metrics=c,trace=tr)
    for r in REGIMES:
        if r!='overrun': assert totals[r+'/fail-closed-done'].get('wrong',0)==0
    assert totals['lost-B/journal-done']['wrong']>0 and totals['lost-B/fail-closed-done']['recovery_slots']>0
    assert totals['done-loss/journal-done'].get('receipt_stopped',0)==0
    for k,w in words.items(): audio(out/(k+'.wav'),list(w))
    receipt=dict(schema='mhac-restart-fence-v1',parent=PARENT,base=BASE,pin=upstream['PIN'],pins=pins,source_sha256=sha(pathlib.Path(__file__).read_bytes()),slot_ms=800,horizon=H,ids=ids,rows=rows,totals=totals,witnesses=witnesses,done='symbolic only; single transition')
    (out/'receipt.json').write_bytes(dump(receipt))
    gallery=''.join(f'<p>{k} <audio controls preload="none" src="{k}.wav"></audio></p>' for k in words)
    page='''<!doctype html><meta charset=utf-8><title>Restart fence</title><style>body{font:16px system-ui;max-width:960px;margin:2rem auto;padding:1rem}pre{white-space:pre-wrap;background:#eee;padding:1rem}</style><h1>Restart and receipt fence</h1><p>Synthetic aligned frames. Atomic journal model; no physical device or human evidence. DONE is symbolic only. Select a case and scrub time. Start at low gain.</p><select id="case"></select> <input id="slot" type="range" min="0" max="119" value="0"><output id="time"></output><pre id="view"></pre><h2>Original upstream frame specimens</h2>'''+gallery+'''<a href="receipt.json">Full receipt</a><script>const W='''+json.dumps(witnesses).replace('<','\\u003c')+''';const c=document.getElementById('case'),s=document.getElementById('slot');for(const k of Object.keys(W))c.add(new Option(k,k));function show(){let w=W[c.value],t=+s.value;document.getElementById('time').textContent='slot '+t;document.getElementById('view').textContent=JSON.stringify({seed:w.seed,D:w.D,metrics:w.metrics,events:w.trace.filter(e=>e.t===t)},null,2)}c.onchange=s.oninput=show;show();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_bytes(dump({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())}))
    print(json.dumps(totals,sort_keys=True))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
