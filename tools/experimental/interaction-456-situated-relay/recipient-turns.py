"""Refs #456 / Draft #457. Multi-outstanding recipient verification.
Run: python recipient-turns.py grammar NEW_OUTPUT
Local fixture-key adapter following Grammar detached-verification (2b351ea8b770bd628bf6963bd938f6f6de7af933) and run 049 handoff. No authentication or human evidence.
"""
import hashlib, hmac, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np

PARENT='8c0b31ae3788b21cbe86ff15775dbbc381de1075'
PIN='2b351ea8b770bd628bf6963bd938f6f6de7af933'
KEY=b'MHAC interaction 048 public fixture key'
CASES=('clean','reverse','missing','foreign','alternate','duplicate','noise','foreign-alternate')
POLICIES=('fifo','eager','closed','partial','header')
DEADLINES=((70,100),(85,105),(100,120))
sha=lambda b:hashlib.sha256(b).hexdigest()

def capture(a,c,books,seed,case,header):
    rng=np.random.default_rng(seed); events=[]; audio=[]; tasks=[]; now=0
    def wire(data,role,erase=None):
        nonlocal now
        obs,x,t=a['exchange'](c['encode'](data),2500 if case=='noise' else 0,seed*100+len(events),erase)
        now+=t['slots']; got=c['decode'](obs) if obs is not None else None
        events.append(dict(t=now,role=role,decoded=got,wire=t));audio.append(x.ravel());return got
    for s in range(2):
        book=books[s][13];target,rival=map(int,rng.choice(len(book),2,False));hdr=[seed%17,s,0,11,15]
        ctx=c['digest'](s,13,book).digest();tasks.append(dict(agent=s,target=target,rival=rival,hdr=hdr,context=ctx.hex()))
        assert wire(hdr,'query')==hdr
    def tag(t,body,recipient):
        msg=b'MHAC-048-recipient\0'+bytes([recipient])+bytes.fromhex(t['context'])+bytes(body)
        return c['digits'](int.from_bytes(hmac.digest(KEY,msg,'sha256'),'big')%17**8,8)
    tags=[]
    for t in tasks:
        s=t['agent'];sent=t['rival'] if s==1 and case in ('alternate','foreign-alternate') else t['target']
        body=t['hdr']+c['digits'](sent,4);got=wire(body,'body');assert got==body
        t['candidate']=c['index'](got[5:]);t['body_time']=now
        t['expected_tag']=tag(t,got,s+1)
        actual=tag(t,body,3 if s==1 and case in ('foreign','foreign-alternate') else s+1)
        tags.append((s,(t['hdr'] if header else [])+actual))
    if case=='reverse':tags.reverse()
    if case=='duplicate':tags.append(tags[0])
    for s,data in tags:wire(data,'tag',-1 if case=='missing' and s==1 else None)
    return dict(seed=seed,case=case,header=header,tasks=tasks,events=events,closure=now),np.concatenate(audio)

def replay(row,policy,deadlines):
    tasks=row['tasks'];pending=set();used=set();admitted={};log=[];matches=[]
    for e in row['events']:
        if e['role']=='body':
            i=next(i for i,t in enumerate(tasks) if t['hdr']==e['decoded'][:5]);pending.add(i)
            log.append(dict(t=e['t'],event='provisional',agent=i,candidate=tasks[i]['candidate']))
        if e['role']!='tag':continue
        d=e['decoded']; candidates=[i for i in sorted(pending) if d is not None and d==(tasks[i]['hdr'] if row['header'] else [])+tasks[i]['expected_tag']]
        matches.append(candidates); log.append(dict(t=e['t'],event='association',candidates=candidates))
        if policy=='fifo':
            i=next((i for i in sorted(pending) if i not in used),None)
            if i is not None:
                used.add(i)
                if i in candidates and e['t']<=deadlines[i]:admitted[i]=e['t']
        elif policy in ('eager','header') and len(candidates)==1:
            i=candidates[0]
            if i not in admitted and e['t']<=deadlines[i]:admitted[i]=e['t']
    if policy in ('closed','partial'):
        counts=Counter(i for m in matches if len(m)==1 for i in m)
        complete=len(matches)==2 and counts=={0:1,1:1}
        for i in range(2):
            if (complete or policy=='partial' and counts[i]==1 and not any(i in m and len(m)>1 for m in matches)) and row['closure']<=deadlines[i]:admitted[i]=row['closure']
    outcomes=[]
    for i,t in enumerate(tasks):
        at=admitted.get(i);status='abstain' if at is None else 'correct' if t['candidate']==t['target'] else 'wrong'
        if at is not None:assert t['body_time']<=at<=deadlines[i] and any(i in m for m in matches)
        outcomes.append(dict(agent=i,status=status,admitted_at=at,deadline=deadlines[i],candidate=t['candidate'],target=t['target']))
    return dict(policy=policy,deadlines=deadlines,case=row['case'],seed=row['seed'],closure=row['closure'],outcomes=outcomes,log=log)

def run(root,out):
    here=pathlib.Path(__file__).parent
    for f,h in [('acoustic-turns.py','d14f133f592f6b9ea97ca8bce18d28eede9eb65dd9958029b1ee40edfefb9e6d'),('catalogue-turns.py','a407e139a74ad49befe7cc0554c293bdc1e5f22d575fb84a930d3986057bc45b')]:assert sha((here/f).read_bytes())==h
    a,books=runpy.run_path(str(here/'acoustic-turns.py'))['load'](root);c=runpy.run_path(str(here/'catalogue-turns.py'))
    out.mkdir();bank=[];rows=[];stats={};spec=[]
    for seed,case,header in itertools.product(range(4564800,4564808),CASES,(False,True)):
        b,pcm=capture(a,c,books,seed,case,header);bank.append(b)
        if seed==4564800 and case in ('clean','reverse','duplicate') and not header:
            name=case+'.wav';
            with wave.open(str(out/name),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())
            spec.append(dict(file=name,peak=int(np.abs(pcm.astype('int32')).max()),pcm_sha256=sha(pcm.tobytes())))
        for p,d in itertools.product(POLICIES,DEADLINES):
            if header!=(p=='header'):continue
            x=replay(b,p,d);assert x==replay(b,p,d);rows.append(x);stats.setdefault(f'{case}:{d[0]}:{p}',Counter()).update(o['status'] for o in x['outcomes'])
    for p in ('eager','partial','closed','header'):
        assert stats[f'reverse:100:{p}']['correct']==16 and stats[f'foreign-alternate:100:{p}']['wrong']==0
        assert stats[f'alternate:100:{p}']['wrong']==8
    assert stats['reverse:100:fifo']['correct']==0 and stats['missing:100:closed']['correct']==0 and stats['missing:100:partial']['correct']==8
    receipt=dict(parent=PARENT,grammar_reference=PIN,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,captures=len(bank),frames=sum(len(b['events']) for b in bank),replays=len(rows),stats=stats,specimens=spec,limits='Known aligned PCM, local public fixture key, provisioned recipient and external closure. Serial channel, no retry, no authentication, no collision search, no live device or human evidence. Deadline slots are 80 ms. No turnaround allowance; transmission-only lower bound.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'bank.jsonl').write_text(''.join(json.dumps(b)+'\n' for b in bank));(out/'traces.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
    examples=[x for x in rows if x['seed']==4564800]
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Recipient turns</title><h1>Recipient turns</h1><p>Synthetic only. Start at low system volume; no autoplay.</p><select id="case" aria-label="Scenario"></select><button id="prev">Previous event</button><button id="next">Next event</button><pre id="state"></pre><pre id="event"></pre>'''+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="bank.jsonl">PCM evidence</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps(examples)+''';let i=0;const s=document.querySelector('#case');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.case,r.policy,r.deadlines].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#state').textContent=JSON.stringify(r.outcomes,null,2);document.querySelector('#event').textContent=JSON.stringify(r.log[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].log.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
