"""MHAC #456 Interaction Run 032: challenge recovery and bounded action admission.
Synthetic aligned symbolic messages; trusted roles, no authentication or human evidence.
AI-assisted GPT-6.2, 2026-11-26. Python standard library; Draft/HOLD.
"""
import collections as C
import hashlib, itertools, json, math, pathlib, struct, sys, wave

PARENT = '3482edad4147c1c18976345387c7e0894c4d83e6'
GRAMMAR = '9e45f77a11c637c03f7e1ac50b6b6802ffc97cfc'  # context only
BASE = '495a98ca12bae467a507031f04931aa4254b1866'
POLICIES = ('counter-cache', 'challenge-cache', 'challenge-window')
REGIMES = ('clean', 'replay', 'rollback', 'nonce-reuse', 'jitter', 'blackout')
H = 180

def dump(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()

def sha(x):
    return hashlib.sha256(x).hexdigest()

def simulate(seed, regime, policy):
    # Frame: kind, boot token, authority epoch, action sequence. Origin is oracle-only.
    active = (1, 1); epoch = 1; pending = {}; local = None; offer = None
    cache = C.deque((3, 4, 5), maxlen=3); high = 5; bits = 7
    effects = {(0, i) for i in range(6)}; q = C.defaultdict(list)
    counts = C.Counter(); trace = []; tape = []; token = 1; gen = 0; ordinal = 0
    def event(t, kind, **data): trace.append(dict(t=t, event=kind, **data))
    def send(t, frame, origin):
        nonlocal ordinal
        h = int(sha(dump([seed, ordinal]))[:8], 16); ordinal += 1
        delays = [1] if regime != 'jitter' else ([] if h%11==0 else [1+h%5]+([5] if h%4==0 else []))
        if regime == 'blackout' and t>=60 and frame[0]!='ACT': delays=[]
        event(t,'send',frame=frame,origin=origin,delays=delays)
        counts['sent']+=1
        for d in delays: q[t+d].append((frame,origin,False))
    for t in range(H):
        if t%60==0:
            gen=t//60+1; token=gen+1
            if gen==3 and regime in ('rollback','nonce-reuse'):
                if policy=='counter-cache' or regime=='nonce-reuse': token=1
            local=offer=None; boot_active=active; event(t,'boot',generation=gen,token=token)
        pending={k:v for k,v in pending.items() if t<v[1]}
        # Stipulated prehistory: identical literal replay frames and arrival slots for every policy.
        if regime!='clean':
            for k in {0:('ACT','OFFER'),2:('REQ','COMMIT'),4:('CONFIRM',),12:('COMMIT',),26:('ACT',),43:('ACT',)}.get(t%60,()):
                frame=(k,1,0 if k=='REQ' else 1,0)
                tape.append([t,frame]); q[t].append((frame,0,True))
        for frame,origin,replay in q.pop(t,[]):
            k,n,e,s=frame; pair=(n,e); event(t,'arrival',frame=frame,origin=origin,replay=replay)
            if k=='REQ':
                if policy=='counter-cache' and n<active[0]: continue
                if n==active[0]: send(t,('OFFER',*active,0),gen); continue
                if n not in pending and len(pending)<2:
                    epoch+=1; pending[n]=(n if policy=='counter-cache' else epoch,t+15)
                if n in pending: send(t,('OFFER',n,pending[n][0],0),gen)
            elif k=='OFFER' and n==token and local is None and offer is None:
                offer=pair
            elif k=='CONFIRM':
                if pair!=active and n in pending and pending[n][0]==e and e>active[1]:
                    active=pair; pending.clear(); cache.clear(); high=-1; bits=0
                    event(t,'authority-activate',session=active)
                if pair==active: send(t,('COMMIT',n,e,0),gen)
            elif k=='COMMIT' and local is None and pair==offer and n==token:
                local=pair; counts['stale-client-commit']+=int(pair!=active); event(t,'client-activate',session=local)
            elif k=='ACT':
                if pair!=active: outcome='session-rejected'
                elif policy=='challenge-window' and s<=high and (high-s>=3 or bits & (1<<(high-s))): outcome='window-rejected'
                elif policy!='challenge-window' and s in cache: outcome='cache-rejected'
                else:
                    if policy=='challenge-window':
                        if s>high: bits=((bits<<(s-high))|1)&7; high=s
                        else: bits|=1<<(high-s)
                    else: cache.append(s)
                    outcome='stale-effect' if origin!=gen else 'duplicate-effect' if (origin,s) in effects else 'new-effect'
                    effects.add((origin,s))
                counts[outcome]+=1; event(t,'action',outcome=outcome,origin=origin,sequence=s,session=pair)
        if local is None and t%3==0:
            send(t,('REQ',token,0,0) if offer is None else ('CONFIRM',*offer,0),gen)
            # Bounded retry of a stranded offer; no claim of reliable completion under arbitrary loss.
            if t%60 in (18,36,54): offer=None
        schedule={24:0,27:1,30:3,33:4,36:5,39:0,42:2,45:4}
        if t%60 in schedule:
            counts['action-opportunities']+=1
            if local is not None: send(t,('ACT',*local,schedule[t%60]),gen)
            else: counts['action-withheld']+=1
        if t%60==59:
            # Oracle checks fresh identity, not simply equality of the endpoints.
            counts['agreement']+=int(local==active and local is not None)
            counts['fresh-agreement']+=int(local==active and local is not None and active[0]==token and active!=boot_active)
        event(t,'state',authority=active,client=local,offer=offer,pending=len(pending),generation=gen)
        assert len(pending)<=2 and len(cache)<=3 and 0<=bits<=7
    assert sum(counts[k] for k in ('session-rejected','window-rejected','cache-rejected','stale-effect','duplicate-effect','new-effect'))==sum(e['event']=='arrival' and e['frame'][0]=='ACT' for e in trace)
    return dict(counts),trace,sha(dump(tape))

def audio(path, trace):
    by=C.defaultdict(list)
    for e in trace:
        if e['event']=='action': by[e['t']].append(e['outcome'])
    buf=bytearray(); sr=8000
    for t in range(H):
        kinds=by[t]
        for i in range(400):
            freq=320 if 'stale-effect' in kinds else 440 if 'duplicate-effect' in kinds else 660 if 'new-effect' in kinds else 220
            buf+=struct.pack('<h',round(800*min(1,i/40,(399-i)/40)*math.sin(2*math.pi*freq*i/sr)) if kinds else 0)
    with wave.open(str(path),'wb') as w: w.setparams((1,2,sr,0,'NONE','not compressed')); w.writeframes(buf)

def run(out):
    out.mkdir(parents=True,exist_ok=False); totals={}; rows=[]; witnesses={}; tapes={}
    for seed,regime,policy in itertools.product(range(4563200,4563232),REGIMES,POLICIES):
        c,tr,tape=simulate(seed,regime,policy); key=regime+'/'+policy
        assert tapes.setdefault(regime,tape)==tape
        totals.setdefault(key,C.Counter()).update(c)
        rows.append(dict(seed=seed,regime=regime,policy=policy,metrics=c,trace_sha256=sha(dump(tr)),tape_sha256=tape))
        witnesses.setdefault(key,dict(seed=seed,metrics=c,trace=tr))
    for k in ('clean/challenge-cache','clean/challenge-window','replay/challenge-cache','replay/challenge-window','nonce-reuse/challenge-window'):
        audio(out/(k.replace('/','-')+'.wav'),witnesses[k]['trace'])
    receipt=dict(schema='mhac-challenge-recovery-v1',base=BASE,parent=PARENT,grammar_context=GRAMMAR,source_sha256=sha(pathlib.Path(__file__).read_bytes()),rows=rows,totals=totals,tapes=tapes,witnesses=witnesses)
    (out/'receipt.json').write_bytes(dump(receipt))
    gallery=''.join('<p>'+p.stem+' <audio controls preload="none" src="'+p.name+'"></audio></p>' for p in sorted(out.glob('*.wav')))
    page='''<!doctype html><meta charset=utf-8><title>Challenge recovery</title><style>body{font:16px system-ui;max-width:960px;margin:auto;padding:1rem}pre{white-space:pre-wrap;background:#eee;color:#111;padding:1rem}</style><h1>Challenge recovery and bounded action admission</h1><p>Synthetic symbolic replay; audio labels action outcomes only, not wire encoding. Start at low gain.</p><label>Scenario <select id="case"></select></label> <label>Slot <input id="slot" type="range" min="0" max="179" value="0"></label> <button id="next">Next</button><pre id="view"></pre>'''+gallery+'''<p><a href="receipt.json">Full receipt</a></p><script>const W='''+json.dumps(witnesses)+''';const c=document.getElementById('case'),s=document.getElementById('slot');for(const k of Object.keys(W))c.add(new Option(k,k));function show(){let w=W[c.value];document.getElementById('view').textContent=JSON.stringify({metrics:w.metrics,events:w.trace.filter(e=>e.t===+s.value)},null,2)}c.onchange=s.oninput=show;document.getElementById('next').onclick=()=>{s.value=Math.min(179,+s.value+1);show()};show();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_bytes(dump({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())}))
    print(json.dumps(totals,sort_keys=True))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
