"""MHAC #456 Interaction: bounded cumulative gap repair, synthetic only.
AI-assisted GPT-6.2, 2026-11-26. No acoustic wire codec or human evidence.
"""
import collections, hashlib, json, math, pathlib, struct, sys, wave

PARENT = '95caf9103c190c0dab07f7e0e08a8ccbcc8e3145'
W, N, T = 3, 8, 60
POLICIES = ('one-shot', 'retry-unbound', 'retry-bound')
REGIMES = ('clean', 'gap', 'loss-jitter', 'receipt-blackout', 'old-receipt', 'mixed')

def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def run(seed, regime, policy):
    # Two already-negotiated epochs; actions are ordered fictional tile placements.
    queue = collections.defaultdict(list); trace = []; counts = collections.Counter()
    effects = set(); tape = []; peak = 0
    def log(t, event, **kw): trace.append(dict(t=t, event=event, **kw))
    def send(t, kind, epoch, seq):
        counts[kind+'-sent'] += 1
        h = int(digest([seed,t,kind,epoch,seq])[:8],16)
        delay = 1
        if regime in ('loss-jitter','mixed'):
            delay = 1+h%5 if h%5 else 0
        if regime in ('gap','old-receipt','mixed') and kind=='ACT' and seq==1 and t%T<10: delay=0
        if regime=='receipt-blackout' and kind=='ACK': delay=0
        log(t,'send',kind=kind,epoch=epoch,seq=seq,delay=delay)
        if delay: queue[t+delay].append((kind,epoch,seq))
    for t in range(2*T):
        epoch=t//T+1; age=t%T
        if age==0:
            floor=ack=-1; next_seq=0; buffered=set(); cursor=0
            log(t,'epoch',epoch=epoch)
        # Identical old-epoch traffic for all policies; not adversarial fabrication.
        if epoch==2 and regime in ('old-receipt','mixed') and age in (2,5,15):
            frame=('ACK',1,7) if age!=15 else ('ACT',1,1)
            queue[t].append(frame); tape.append([t,*frame])
        for kind,e,s in queue.pop(t,[]):
            log(t,'arrival',kind=kind,epoch=e,seq=s)
            if kind=='ACK':
                if policy=='one-shot': continue
                if policy=='retry-bound' and e!=epoch:
                    counts['old-ack-rejected']+=1; log(t,'old-ack-rejected',seq=s); continue
                # ACK can only retire actions already issued in this epoch.
                new_ack=min(s,next_seq-1)
                if new_ack>ack:
                    counts['false-retired']+=sum((epoch,i) not in effects for i in range(ack+1,new_ack+1))
                    ack=new_ack; log(t,'receipt',epoch=e,ack=ack)
                continue
            if e!=epoch:
                counts['old-act-rejected']+=1; continue
            if s<=floor or s in buffered:
                counts['duplicate-suppressed']+=1
            elif s>floor+W:
                counts['outside-window']+=1; log(t,'gap-refusal',seq=s)
            else:
                buffered.add(s); peak=max(peak,len(buffered))
                while floor+1 in buffered:
                    floor+=1; buffered.remove(floor)
                    assert (epoch,floor) not in effects
                    effects.add((epoch,floor)); log(t,'apply',epoch=epoch,seq=floor)
            send(t,'ACK',epoch,floor)
        if policy=='one-shot':
            if age%2==0 and next_seq<N:
                send(t,'ACT',epoch,next_seq); next_seq+=1
        elif next_seq<N and next_seq-ack<=W:
            send(t,'ACT',epoch,next_seq); next_seq+=1
        elif ack<next_seq-1:
            seq=ack+1+cursor%(next_seq-ack-1); cursor+=1
            send(t,'ACT',epoch,seq)
        assert len(buffered)<=W
        if policy!='one-shot': assert next_seq-ack-1<=W
        log(t,'state',epoch=epoch,floor=floor,ack=ack,issued=next_seq,buffer=sorted(buffered))
        if age==T-1:
            counts['completed-epochs']+=int(floor==N-1)
            counts['confirmed-epochs']+=int(ack==N-1 and floor==N-1)
            counts['false-complete']+=int(ack==N-1 and floor!=N-1)
    counts['applied']=len(effects); counts['missing']=2*N-len(effects); counts['peak-buffer']=peak
    assert counts['applied']==sum(x['event']=='apply' for x in trace)
    return dict(counts),trace,digest(tape)

def audio(path, trace):
    tones={'apply':660,'gap-refusal':330,'receipt':880,'old-ack-rejected':220}
    events=collections.defaultdict(list)
    for x in trace:
        if x['event'] in tones: events[x['t']].append(tones[x['event']])
    with wave.open(str(path),'wb') as f:
        f.setparams((1,2,8000,0,'NONE','not compressed'))
        for t in range(2*T):
            fs=events[t]; samples=[int(800*math.sin(math.pi*i/399)**2*sum(math.sin(2*math.pi*z*i/8000) for z in fs)/max(1,len(fs))) for i in range(400)]
            f.writeframes(struct.pack('<400h',*samples))

def main(out):
    out.mkdir(parents=True,exist_ok=True); totals={}; witnesses={}; hashes=[]
    for regime in REGIMES:
        totals[regime]={}
        for policy in POLICIES:
            aggregate=collections.Counter()
            for seed in range(4563300,4563332):
                c,tr,tape=run(seed,regime,policy); p=c.pop('peak-buffer'); aggregate.update(c)
                aggregate['peak-buffer']=max(aggregate['peak-buffer'],p)
                hashes.append([seed,regime,policy,digest(tr),tape])
                if seed==4563300: witnesses[regime+'/'+policy]=tr
            totals[regime][policy]=dict(aggregate)
    for regime in REGIMES:
        for seed in range(4563300,4563332):
            rows=[r for r in hashes if r[:2]==[seed,regime]]
            assert len({r[4] for r in rows})==1
    assert totals['clean']['retry-bound']['applied']==512
    assert totals['old-receipt']['retry-bound'].get('false-retired',0)==0
    assert totals['old-receipt']['retry-unbound']['false-retired']>0
    assert totals['receipt-blackout']['retry-bound']['applied']==192
    receipt=dict(parent=PARENT,window=W,actions=N,slots=T,totals=totals,hashes=hashes,witnesses=witnesses)
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    for regime,policy in [('gap','one-shot'),('gap','retry-bound'),('old-receipt','retry-unbound'),('old-receipt','retry-bound'),('receipt-blackout','retry-bound')]:
        audio(out/(regime+'-'+policy+'.wav'),witnesses[regime+'/'+policy])
    data=json.dumps(witnesses,separators=(',',':'))
    page='''<!doctype html><meta charset=utf-8><title>MHAC gap repair</title><style>body{font:16px system-ui;max-width:860px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}button,select,input{font:inherit}progress{width:100%}</style><h1>Bounded action gap repair</h1><p>Choose a replay; advance the slot to inspect issued actions, cumulative execution and receipts. Fictional actions only. Audio is event sonification, not a wire codec.</p><select id="case"></select><button id="prev">Previous</button><button id="next">Next</button><input type="range" min="0" max="119" value="0" id="slot"><p id="summary"></p><progress id="progress" max="8" value="0"></progress><pre id="events"></pre><h2>Original specimens</h2><div id="audio"></div><script>const traces=DATA;const el=id=>document.getElementById(id);for(const k of Object.keys(traces)){const o=document.createElement('option');o.value=o.textContent=k;el('case').append(o)}function render(){const t=Number(el('slot').value),rows=traces[el('case').value].filter(x=>x.t===t),s=rows.find(x=>x.event==='state');el('summary').textContent='Slot '+t+' | epoch '+s.epoch+' | applied '+(s.floor+1)+'/8 | receipt '+(s.ack+1)+'/8 | issued '+s.issued+' | buffered '+s.buffer.join(',');el('progress').value=s.floor+1;el('events').textContent=JSON.stringify(rows,null,2)}el('case').onchange=render;el('slot').oninput=render;el('prev').onclick=()=>{el('slot').value=Math.max(0,+el('slot').value-1);render()};el('next').onclick=()=>{el('slot').value=Math.min(119,+el('slot').value+1);render()};for(const name of AUDIO){const p=document.createElement('p'),a=document.createElement('audio');p.textContent=name+' ';a.src=name+'.wav';a.controls=true;a.volume=.2;a.preload='none';p.append(a);el('audio').append(p)}render();</script>'''
    names=[p.stem for p in sorted(out.glob('*.wav'))]
    (out/'index.html').write_text(page.replace('DATA',data).replace('AUDIO',json.dumps(names)),encoding='utf-8')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(manifest,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(totals,indent=2))

if __name__=='__main__': main(pathlib.Path(sys.argv[1]))
