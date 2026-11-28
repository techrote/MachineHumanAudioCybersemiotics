"""Refs #456 / Draft #457: bounded retirement over frozen PCM settlement traces.
python retirement-turns.py settlement1/bank.jsonl NEW_OUTPUT
Synthetic-only; repair requests are symbolic outputs, not delivered frames.
One AI worker, no human evidence. Fixed two-agent roster; no epoch reuse test.
"""
import hashlib,hmac,itertools,json,pathlib,sys,wave,math,struct
from collections import Counter
PARENT='25c4be97a137387f21634e6ebe49aaf90431202a'
BANK='3295d0048eabe8c752e3328ee45f08cf78d403e14616a05d62620d59eb115004'
KEY=b'MHAC PUBLIC SYNTHETIC TEST KEY 047'
POLICIES=('retain','drop','tombstone')
sha=lambda b:hashlib.sha256(b).hexdigest()

def replay(row,policy,ttl,reversible):
    headers=list(map(tuple,row['headers']));ctx=bytes.fromhex(row['context'])
    body=[None,None];extra=[None,None];retired=[False,False];stone=[None,None]
    tags=set();admitted=[None,None];invalid=set();withdrawn=set();repair=set();log=[];overflow=False;peak=0
    def tag(w):return tuple(int.from_bytes(hmac.digest(KEY,b'MHAC-048-recipient\0'+bytes([1])+ctx+bytes(w),'sha256'),'big')//17**j%17 for j in range(8))
    def conflict(i,t):
        if admitted[i] is not None:
            invalid.add(i)
            if reversible and t-admitted[i][0]<=96:withdrawn.add(i)
        if i not in repair:repair.add(i);log.append(dict(t=t,event='repair-request',agent=i,transport='not sent'))
    for e in row['events']:
        t=e['t'];role=e['role'];w=None if e['word'] is None else tuple(e['word'])
        for i,a in enumerate(admitted):
            if policy!='retain' and a and not retired[i] and t-a[0]>=ttl:
                retired[i]=True
                if policy=='tombstone':stone[i]=tag(body[i])
                body[i]=extra[i]=None
                log.append(dict(t=t,event='retire',agent=i))
        if w is not None and role=='body' and w[:5] in headers:
            i=headers.index(w[:5])
            if retired[i]:
                if stone[i] is not None and tag(w)!=stone[i]:conflict(i,t)
            elif body[i] is None:body[i]=w
            elif body[i]!=w:
                if extra[i] is None:extra[i]=w
                elif extra[i]!=w:overflow=True
                conflict(i,t)
        if w is not None and role=='tag':
            if w not in tags and len(tags)==4:overflow=True
            else:tags.add(w)
        edges={z:[i for i in range(2) if stone[i]==z or any(v is not None and tag(v)==z for v in (body[i],extra[i]))] for z in tags}
        for z,ids in edges.items():
            if len(ids)>1:
                for i in ids:conflict(i,t)
        if overflow:
            for i in range(2):conflict(i,t)
        for i,b in enumerate(body):
            if not overflow and b is not None and extra[i] is None and admitted[i] is None and i not in repair and edges.get(tag(b))==[i] and t<=(120,150)[i]:
                admitted[i]=(t,sum(v*17**j for j,v in enumerate(b[5:])),tag(b));log.append(dict(t=t,event='admit',agent=i,value=admitted[i][1]))
        # Count evidence symbols, not Python memory. Fixed roster/action metadata excluded.
        stored=sum(len(v) for v in body+extra+stone if v is not None)+8*len(tags);peak=max(peak,stored)
        assert stored<=72 and len(tags)<=4
        log.append(dict(t=t,event=role,stored_symbols=stored,retired=retired[:],invalid=sorted(invalid),withdrawn=sorted(withdrawn),overflow=overflow))
    # Offline evaluator only: origin and targets never influence the receiver.
    outcomes=[]
    for i,a in enumerate(admitted):
        witnessed=bool(a and any(e['role']=='tag' and e['origin']==i and e['word'] is not None and tuple(e['word'])==a[2] and e['t']<=a[0] for e in row['events']))
        outcomes.append(dict(agent=i,status='abstain' if a is None else 'withdrawn' if i in withdrawn else 'correct' if a[1]==row['targets'][i] else 'wrong',admitted=a is not None,unwitnessed=bool(a and not witnessed),invalid=i in invalid,withdrawn=i in withdrawn,repair=i in repair))
    return dict(seed=row['seed'],case=row['case'],policy=policy,ttl=ttl,reversible=reversible,peak_symbols=peak,outcomes=outcomes,log=log)

def run(bank,out):
    assert sha(bank.read_bytes())==BANK,'unexpected frozen capture bank'
    rows=[];stats={};out.mkdir();captures=list(map(json.loads,bank.read_text().splitlines()))
    for b,p,ttl,rev in itertools.product(captures,POLICIES,(16,32,96),(False,True)):
        x=replay(b,p,ttl,rev);assert x==replay(b,p,ttl,rev);rows.append(x)
        altered=dict(b,events=[dict(e,origin=None if e['origin'] is None else 1-e['origin']) for e in b['events']]);assert x['log']==replay(altered,p,ttl,rev)['log']
        s=stats.setdefault(f'{b["case"]}:{p}:{ttl}:{int(rev)}',Counter());s['peak']=max(s['peak'],x['peak_symbols'])
        for o in x['outcomes']:s[o['status']]+=1;s.update(k for k in ('admitted','unwitnessed','invalid','repair') if o[k])
    assert stats['collision-late-unwitnessed:drop:16:1']['correct']==8
    assert stats['collision-late-unwitnessed:tombstone:16:1']['withdrawn']==4
    assert stats['collision-late-unwitnessed:tombstone:16:1']['abstain']==4
    assert stats['early-close:tombstone:32:0']['invalid']==4
    receipt=dict(parent=PARENT,bank_sha256=BANK,source_sha256=sha(pathlib.Path(__file__).read_bytes()),python=sys.version.split()[0],captures=len(captures),replays=len(rows),stats=stats,limits='Frozen aligned PCM inputs; no new acoustic decoding. Fixed roster, known roles, fixed evidence caps, no epoch reuse. Repair requests are symbolic and unsent. Compensation only updates simulated outcome. Peak counts evidence symbols, excludes fixed metadata, audit log and offline evaluator. Not human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    examples=[r for r in rows if r['seed']==4564900]
    # Original event sonification, not the acoustic wire protocol. Quiet digital peak, no autoplay.
    example=next(r for r in examples if r['case']=='collision-late-unwitnessed' and r['policy']=='tombstone' and r['ttl']==16 and r['reversible'])
    pcm=bytearray();freq={'admit':440,'retire':330,'repair-request':660}
    for e in example['log']:
        if e['event'] not in freq:continue
        for k in range(2400):pcm+=struct.pack('<h',round(900*math.sin(2*math.pi*freq[e['event']]*k/16000)*math.sin(math.pi*k/2400)**2))
        pcm+=bytes(1600)
    with wave.open(str(out/'events.wav'),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm)
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Retirement turns</title><h1>Retirement turns</h1><p>Synthetic replay. Lower system volume; no autoplay. Event sonification, not wire audio.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre><pre id="result"></pre><audio controls preload="none" src="events.wav"></audio><p><a href="traces.jsonl">Traces</a> | <a href="receipt.json">Receipt</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.case,r.policy,r.ttl,r.reversible?'reversible':'irreversible'].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#event').textContent=JSON.stringify(r.log[i],null,2);document.querySelector('#result').textContent=JSON.stringify(r.outcomes,null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].log.length-1,i+1);draw()};document.querySelector('audio').volume=.2;draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(f'{len(captures)} captures, {len(rows)} replays, {len(examples)} selectable scenarios')
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
