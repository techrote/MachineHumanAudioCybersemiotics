"""MHAC Interaction #456: synthetic conversational reconstitution, Run 031.
Python 3 standard library. Run: python reconstitution.py NEW_OUTPUT_DIRECTORY
No acoustic allocation for session metadata; original WAV motifs are event labels only.
Draft/HOLD, AI-assisted GPT-6.2, 2026-11-26. No human or physical evidence.
"""
import collections, hashlib, itertools, json, math, pathlib, struct, sys, wave

BASE = '495a98ca12bae467a507031f04931aa4254b1866'
PARENT = 'c8d9c3aca353c8a3fea2c697bdc8b9539fb0e4e1'
GRAMMAR = '7c40f0e533245d129881729722210ac6e9a65d9c'
# Narrow symbolic stand-in: actual alias row IDs from pinned activation-fence.py.
ALIAS = (56, 53700)
POLICIES = ('unbound', 'session-bound', 'monotonic')
REGIMES = ('clean', 'mixed', 'old-control', 'old-payload', 'all-replay', 'blackout', 'counter-rollback')
H = 180
BOOTS = (12, 66, 120)
LEASE = 42
KINDS = ('REQ', 'GRANT', 'ACK', 'COMMIT', 'RECEIPT', 'PAYLOAD')

def dump(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def simulate(seed, bound, regime, policy):
    # A is an authoritative journalled coordinator, B can lose all local session state.
    # B's boot counter is an independently supplied monotonic identity except in rollback.
    # Payload/control fields are delivered intact; source role is trusted, not authenticated.
    s = [dict(phase='active', epoch=0, version=0, until=0),
         dict(phase='active', epoch=0, version=0, until=0)]
    boot = 0
    q = collections.defaultdict(list)
    archive = [(1, 'REQ', 0, 0), (0, 'GRANT', 0, 0), (1, 'ACK', 0, 0),
               (0, 'COMMIT', 0, 0), (1, 'RECEIPT', 0, 0), (0, 'PAYLOAD', 0, 0),
               (1, 'PAYLOAD', 0, 0)]  # stipulated prehistory for session zero
    c = collections.Counter(); ordinals = collections.Counter(); trace = []; pending_receipt = False
    def event(t, kind, **kw):
        trace.append(dict(t=t, event=kind, **kw))
    def tx(t, m, replay=False):
        src,k,epoch,v = m
        n = ordinals[src,k,replay]; ordinals[src,k,replay] += 1
        h = int(sha(dump([seed, src, k, n, replay]))[:12], 16)
        delays = [1] if regime == 'clean' or replay else [1+h%bound]
        if not replay and regime != 'clean' and h%4 == 0: delays.append(bound)
        if not replay and regime != 'clean' and h%9 == 0: delays = []
        if regime == 'blackout' and t >= BOOTS[1] and k != 'PAYLOAD': delays = []
        if not replay and k != 'PAYLOAD': c['control_sent'] += 1
        if replay: c['replay_sent'] += 1
        if not replay and m not in archive: archive.append(m)
        event(t,'send',message=m,replay=replay,delays=delays)
        for d in delays: q[t+d].append((m,replay))
    for t in range(H):
        if t in BOOTS:
            boot += 1
            if regime == 'counter-rollback' and t == BOOTS[2]: boot = 1
            s[1] = dict(phase='request',epoch=None,version=None,until=t+LEASE)
            pending_receipt = False
            event(t,'storage-loss',boot=boot)
        # Reinject archived authentic-role frames, not fabricated future messages.
        if regime in ('old-control','old-payload','all-replay','counter-rollback') and any(t==b+d for b in BOOTS for d in (2,16,32)):
            stale = [m for m in archive if m[2] < boot or regime=='counter-rollback' and m[2]==boot]
            stale = [m for m in stale if regime not in ('old-control','old-payload') or (m[1]=='PAYLOAD')==(regime=='old-payload')]
            if stale:
                # At most one archived frame per direction per slot (extra replay traffic).
                for src in (0,1):
                    choices = [m for m in stale if m[0]==src]
                    if choices: tx(t,choices[(seed+t+src)%len(choices)],True)
        for m,replay in q.pop(t,[]):
            src,k,epoch,v = m; dst=1-src; a=s[dst]; phase=a['phase']
            event(t,'arrival',message=m,replay=replay)
            if k=='PAYLOAD':
                if phase!='active': outcome='gated'
                elif policy!='unbound' and epoch!=a['epoch']: outcome='epoch-rejected'
                elif ALIAS[v]!=ALIAS[a['version']]: outcome='wrong'
                else: outcome='correct'
                c[outcome]+=1
                if outcome in ('wrong','correct') and epoch!=boot: c['obsolete_admitted']+=1
                event(t,'interpret',outcome=outcome,source_epoch=epoch,local_epoch=a['epoch'],boot=boot,replay=replay)
                continue
            match = policy=='unbound' or epoch==(a['epoch'] if dst==0 else boot)
            prior = a.copy()
            if dst==0 and k=='REQ':
                # Same epoch is idempotent: it never resets an in-progress or completed handshake.
                if epoch!=a['epoch'] and (policy!='monotonic' or epoch>a['epoch']):
                    if epoch<a['epoch']: c['authority_rollback']+=1
                    s[0]=dict(phase='grant',epoch=epoch,version=epoch%2,until=t+LEASE)
            elif dst==1 and k=='GRANT' and phase=='request' and match:
                s[1]=dict(phase='ack',epoch=epoch,version=v,until=a['until'])
            elif dst==0 and k=='ACK' and phase=='grant' and match:
                a['phase']='commit'
            elif dst==1 and k=='COMMIT' and phase in ('ack','active') and match and (policy=='unbound' or epoch==a['epoch'] and v==a['version']):
                a['phase']='active'; pending_receipt=True
            elif dst==0 and k=='RECEIPT' and phase=='commit' and match:
                a['phase']='active'
            if prior!=s[dst]: event(t,'transition',endpoint=dst,before=prior,after=s[dst].copy(),cause=k,replay=replay)
        for src,a in enumerate(s):
            if a['phase'] in ('request','ack','grant','commit') and t>=a['until']:
                a['phase']='timeout'; c['timeouts']+=1; event(t,'timeout',endpoint=src)
            if t%3!=src: continue
            phase=a['phase']; k={'request':'REQ','ack':'ACK','grant':'GRANT','commit':'COMMIT'}.get(phase)
            if src==1 and phase=='active' and pending_receipt:
                k='RECEIPT'; pending_receipt=False
            elif phase=='active': k='PAYLOAD'
            if k: tx(t,(src,k,boot if k=='REQ' else a['epoch'],0 if k=='REQ' else a['version']))
        agreement=all(a['phase']=='active' and a['epoch']==boot and a['version']==boot%2 for a in s)
        c['agreement_slots']+=int(agreement)
        if t in tuple(b-1 for b in BOOTS[1:])+(H-1,): c['recovered_episodes']+=int(agreement)
        event(t,'state',boot=boot,A=s[0].copy(),B=s[1].copy(),agreement=agreement)
    c['final_agreement']=int(agreement); c['pending']=sum(map(len,q.values()))
    assert sum(len(e['delays']) for e in trace if e['event']=='send')==c['pending']+sum(e['event']=='arrival' for e in trace)
    assert sum(c[k] for k in ('correct','wrong','gated','epoch-rejected'))==sum(e['event']=='arrival' and e['message'][1]=='PAYLOAD' for e in trace)
    assert c['recovered_episodes']<=3 and c['control_sent']<=2*H//3
    if policy=='monotonic': assert c['authority_rollback']==0 and c['wrong']==0
    return dict(c),trace

def audio(path, trace):
    # Auditory event map, NOT a wire encoder. Separate role pitches, 80 ms/slot.
    sr=16000; n=1280; buf=bytearray(); by=collections.defaultdict(list)
    for e in trace:
        if e['event']=='send' and not e['replay']: by[e['t']].append(e['message'])
    for t in range(H):
        for i in range(n):
            env=min(1,i/80,(n-1-i)/80)
            x=sum(math.sin(2*math.pi*(360+src*180+KINDS.index(k)*65)*i/sr) for src,k,_,_ in by[t])
            buf+=struct.pack('<h',round(900*env*x))
    with wave.open(str(path),'wb') as w: w.setparams((1,2,sr,0,'NONE','not compressed')); w.writeframes(buf)

def run(out):
    out.mkdir(parents=True,exist_ok=False); totals={}; rows=[]; witnesses={}
    for seed,bound,regime,policy in itertools.product(range(4563100,4563116),(1,4,8),REGIMES,POLICIES):
        c,tr=simulate(seed,bound,regime,policy); key=regime+'/'+policy
        totals.setdefault(key,collections.Counter()).update(c)
        rows.append(dict(seed=seed,bound=bound,regime=regime,policy=policy,metrics=c,trace_sha256=sha(dump(tr))))
        if key not in witnesses or c.get('wrong',0)>0 and not witnesses[key]['metrics'].get('wrong',0):
            witnesses[key]=dict(seed=seed,bound=bound,metrics=c,trace=tr)
    assert totals['clean/monotonic']['recovered_episodes']==144
    assert totals['counter-rollback/monotonic']['final_agreement']==0
    assert totals['all-replay/session-bound']['authority_rollback']>0
    for key in ('clean/monotonic','all-replay/unbound','all-replay/session-bound','all-replay/monotonic','counter-rollback/monotonic'):
        audio(out/(key.replace('/','-')+'.wav'),witnesses[key]['trace'])
    receipt=dict(schema='mhac-reconstitution-v1',base=BASE,parent=PARENT,grammar=GRAMMAR,alias=ALIAS,horizon=H,boots=BOOTS,lease=LEASE,source_sha256=sha(pathlib.Path(__file__).read_bytes()),rows=rows,totals=totals,witnesses=witnesses)
    (out/'receipt.json').write_bytes(dump(receipt))
    gallery=''.join('<p>'+p.stem+' <audio controls preload="none" src="'+p.name+'"></audio></p>' for p in sorted(out.glob('*.wav')))
    page='''<!doctype html><meta charset=utf-8><title>Reconstitution laboratory</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:1rem}pre{white-space:pre-wrap;background:#eee;padding:1rem;color:#111}input{width:70%}</style><h1>Conversational reconstitution</h1><p>Two synthetic agents, aligned symbolic frames. Replay three storage-loss episodes. Audio is an event sonification, not a wire codec. No autoplay. Start at low volume.</p><label>Scenario <select id="case"></select></label><p><label>Slot <input id="slot" type="range" min="0" max="179" value="0"></label> <button id="next">Next slot</button></p><pre id="view"></pre><h2>Original event sonifications (80 ms per slot, compressed replay time)</h2>'''+gallery+'''<p><a href="receipt.json">Machine-readable receipt</a></p><script>const W='''+json.dumps(witnesses).replace('<','\\u003c')+''';const c=document.getElementById('case'),s=document.getElementById('slot');for(const k of Object.keys(W))c.add(new Option(k,k));function show(){let w=W[c.value],t=+s.value;document.getElementById('view').textContent=JSON.stringify({slot:t,seed:w.seed,bound:w.bound,metrics:w.metrics,events:w.trace.filter(e=>e.t===t)},null,2)}c.onchange=s.oninput=show;document.getElementById('next').onclick=()=>{s.value=Math.min(179,+s.value+1);show()};show();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    (out/'manifest.json').write_bytes(dump({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())}))
    print(json.dumps(totals,sort_keys=True))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]))
