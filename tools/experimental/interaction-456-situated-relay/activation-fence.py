"""Interaction #456: synthetic single grammatical activation, not human evidence.
Run: python activation-fence.py PINNED_GRAMMAR_DIR NEW_OUTPUT_DIR (NumPy upstream).
Original AI-assisted experiment; Draft/HOLD, 2026-11-26.
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave, html
from collections import Counter, defaultdict
PIN='e500334db2d6f03ff6e788084dc09e5e3cd2d85d'
BLOB='6400cf4c1b42fbe958b0265da43ef657bb355401'
PARENT='3defc6747918bf17598f153742f7fd80530ec101'
POLICIES=('eager','gated','drain','drain-veto')
REGIMES=('clean','duplicate','mixed','overrun','restart')
H=90

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def inputs(root):
    raw=(root/'version-bridge.py').read_bytes()
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==BLOB
    m=runpy.run_path(str(root/'version-bridge.py'))
    u,books,_,bridge,*_=m['build'](root)
    old=books['relocated-cubic']; new=books['unified']
    lookup={tuple(w):i for i,w in enumerate(new.tolist())}
    pairs=[(i,lookup[tuple(w)],tuple(w)) for i,w in enumerate(old.tolist()) if tuple(w) in lookup]
    assert sum(i!=j for i,j,w in pairs)==2031
    a=next(p for p in pairs if p[0]!=p[1]); b=next(p for p in pairs if p[0]==p[1])
    words={k:tuple(bridge[m['IDENTITIES'].index((k,'relocated-to-unified',0))].tolist()) for k in ('PROPOSE','ACCEPT','COMMIT','RECEIPT')}
    words.update(alias=a[2],shared=b[2]); assert len(set(words.values()))==6
    return words,{'alias':a[:2],'shared':b[:2]},u['audio']

def simulate(seed,D,regime,policy,ids):
    # A initiates once; B is responder. One send opportunity per endpoint/slot.
    # Slot arrival precedes emission. No protocol decision uses origin metadata.
    q=defaultdict(list); counts=Counter(); ordinal=Counter(); trace=[]
    version=[0,0]; phase=['old','old']; accepted=None; completed=None
    def event(t,kind,**data): trace.append(dict(t=t,event=kind,**data))
    def send(t,s,k):
        n=ordinal[s,k]; ordinal[s,k]+=1
        h=int.from_bytes(hashlib.sha256(dump([seed,s,k,n])).digest()[:8],'big')
        delays=[1] if regime=='clean' else [1+h%min(D,3)]
        if regime!='clean' and h%3==0: delays.append(D if regime!='overrun' else 4*D)
        if regime in ('mixed','overrun','restart') and h%7==0: delays=[]
        origin=version[s] if k in ids else None
        counts['payload_sent' if k in ids else 'control_sent']+=1
        event(t,'send',s=s,k=k,origin=origin,delays=delays)
        for d in delays: q[t+d].append((s,k,origin,t))
    for t in range(H):
        if regime=='restart' and t==45:
            phase[1]='old'; version[1]=0; event(t,'restart',s=1)
        if t==8: phase[0]='proposing'; event(t,'begin',s=0)
        for s,k,origin,emitted in q.pop(t,[]):
            r=1-s; event(t,'arrival',s=s,k=k,origin=origin,emitted=emitted)
            if k in ids:
                if policy!='eager' and phase[r] not in ('old','new'):
                    outcome='gated'
                elif policy=='drain-veto' and ids[k][0]!=ids[k][1]: outcome='ambiguous'
                else: outcome='correct' if ids[k][version[r]]==ids[k][origin] else 'wrong'
                counts[outcome]+=1; event(t,'payload',r=r,k=k,outcome=outcome,receiver_version=version[r],origin=origin,emitted=emitted)
            elif r==1 and k=='PROPOSE' and phase[1]=='old': phase[1]='accepting'
            elif r==0 and k=='ACCEPT' and phase[0]=='proposing': phase[0]='committing'; accepted=t
            elif r==1 and k=='COMMIT' and phase[1] in ('accepting','new'):
                phase[1]='new'; version[1]=1; counts['commit_arrivals']+=1
            elif r==0 and k=='RECEIPT' and phase[0]=='committing':
                phase[0]='new'; version[0]=1; completed=t
        if version[0]!=version[1]: counts['split_slots']+=1
        for s in range(2):
            p=phase[s]; k=None
            if s==0 and p=='proposing' and (t-8)%3==0: k='PROPOSE'
            if s==0 and p=='committing' and t>=accepted+(D+1 if policy.startswith('drain') else 0) and (t-accepted-(D+1 if policy.startswith('drain') else 0))%3==0: k='COMMIT'
            if s==1 and p=='accepting' and t%3==0: k='ACCEPT'
            # Repeat receipt while new; no inference of remote receipt from silence.
            if s==1 and p=='new' and t%3==0: k='RECEIPT'
            if k is None and t%3==s and p in ('old','new'): k='alias' if (t//3)%2==0 else 'shared'
            if k: send(t,s,k)
        event(t,'state',phase=phase.copy(),version=version.copy())
    counts['pending']=sum(map(len,q.values())); counts['completed']=int(completed is not None)
    counts['both_new_end']=int(version==[1,1]); counts['completion_slot']=completed if completed is not None else H
    assert sum(counts[k] for k in ('correct','wrong','gated','ambiguous'))==sum(e['event']=='arrival' and e['k'] in ids for e in trace)
    assert sum(len(e['delays']) for e in trace if e['event']=='send')==counts['pending']+sum(e['event']=='arrival' for e in trace)
    return dict(counts),trace

def run(root,out):
    words,ids,audio=inputs(root); out.mkdir(parents=True,exist_ok=False)
    rows=[]; witnesses={}; totals={}
    for seed,D,regime,policy in itertools.product(range(456290,456306),(3,8,15),REGIMES,POLICIES):
        c,tr=simulate(seed,D,regime,policy,ids); key=regime+'/'+policy
        totals.setdefault(key,Counter()).update(c)
        rows.append(dict(seed=seed,D=D,regime=regime,policy=policy,metrics=c,trace_sha256=sha(dump(tr))))
        if key not in witnesses or (c.get('wrong',0)>0 and not witnesses[key]['metrics'].get('wrong',0)):
            witnesses[key]=dict(seed=seed,D=D,metrics=c,trace=tr)
    for regime in ('clean','duplicate','mixed'):
        assert totals[regime+'/drain'].get('wrong',0)==0
    assert sum(totals[r+'/gated'].get('wrong',0) for r in ('duplicate','mixed'))>0
    assert totals['overrun/drain'].get('wrong',0)>0
    assert all(c.get('wrong',0)==0 for k,c in totals.items() if k.endswith('/drain-veto'))
    for k,w in words.items(): audio(out/(k+'.wav'),list(w))
    receipt=dict(schema='mhac-activation-fence-v1',pin=PIN,blob=BLOB,parent=PARENT,slot_ms=800,horizon=H,words=words,identities=ids,rows=rows,totals=totals,witnesses=witnesses,source_sha256=sha(pathlib.Path(__file__).read_bytes()))
    (out/'receipt.json').write_bytes(dump(receipt))
    # Embedded traces keep the file:// demo offline; no fetch or external JS.
    data=json.dumps(witnesses).replace('<','\\u003c')
    gallery=''.join(f'<p>{html.escape(k)} <audio controls preload="none" src="{k}.wav"></audio></p>' for k in words)
    page='''<!doctype html><meta charset=utf-8><title>Activation fence</title><style>body{font:16px system-ui;max-width:960px;margin:2rem auto;padding:1rem}pre{white-space:pre-wrap;background:#eee;padding:1rem}audio{vertical-align:middle}</style><h1>Activation fence replay</h1><p>Two synthetic agents; aligned symbols, no physical control. Select a scenario and scrub its trace. Start at low volume. No autoplay.</p><select id="case"></select> <input id="slot" type="range" min="0" max="89" value="0"><output id="time"></output><pre id="view"></pre><h2>Original frame specimens</h2>'''+gallery+'''<p><a href="receipt.json">Full machine-readable receipt</a></p><script>const W='''+data+''';const c=document.getElementById('case'),s=document.getElementById('slot');for(const k of Object.keys(W))c.add(new Option(k,k));function show(){let w=W[c.value],t=+s.value;document.getElementById('time').textContent='slot '+t+' ('+(t*.8).toFixed(1)+' s)';document.getElementById('view').textContent=JSON.stringify({seed:w.seed,D:w.D,metrics:w.metrics,events:w.trace.filter(e=>e.t===t)},null,2)}c.onchange=s.oninput=show;show();document.querySelectorAll('audio').forEach(a=>a.volume=.2)</script>'''
    (out/'index.html').write_text(page,encoding='utf-8')
    for f in out.glob('*.wav'):
        with wave.open(str(f),'rb') as w: assert w.getparams()[:4]==(1,2,16000,12800)
    (out/'manifest.json').write_bytes(dump({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())}))
    print(json.dumps(totals,sort_keys=True))

if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
