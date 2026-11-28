"""Refs #456 / #457. Synthetic situated catalogue sessions, not authentication.
Run: python context-memory.py grammar NEW_OUTPUT. Python + NumPy.
Uses exact Interaction predecessor and its pinned PCM sources; session design
inspired by Grammar session-catalogue.py at 33228efc8363a0814a36ebfd175ecfef9920e364.
"""
import hashlib, itertools, json, pathlib, runpy, sys, wave
from collections import Counter
import numpy as np
PARENT='77fc7423e17e4d84d4ed425ef71a4e63be6c74a7'
HASH='a407e139a74ad49befe7cc0554c293bdc1e5f22d575fb84a930d3986057bc45b'
MODES=('full','tagged','cached4','guarded8')
FAULTS=('clean','sender-change','receiver-change','collision4','restart','same-sequence')
sha=lambda b:hashlib.sha256(b).hexdigest()

def session(c,a,books,orders,seed,fault,mode,window,save=False):
    states=[dict(sender=None,receiver=None) for _ in range(2)]; events=[]; outcomes=[]; clips=[]; now=0; seq=0
    def event(name,**kw):events.append(dict(t=now,event=name,round=r,agent=s,**kw))
    for r in range(6):
        now=r*window
        for s in range(2):
            l=13 if s==0 else 18; b=books[s][l]; w=4 if l==13 else 5; deadline=r*window+(window//2+5 if s==0 else window); state=states[s]
            normal=np.arange(len(b)); so,ro=normal,normal
            if fault=='sender-change' and r>=3:so=np.roll(normal,1)
            if fault=='receiver-change' and r>=3:ro=np.roll(normal,1)
            if fault=='collision4':so,ro,*_=orders[s,l]['collision']
            sd,rd=(c['digest'](s,l,b[o]).hexdigest() for o in (so,ro)); tag=lambda d,n:int(d,16)%17**n
            target=int(so[np.flatnonzero(so!=ro)[(seed+r)%np.count_nonzero(so!=ro)]]) if fault=='collision4' else (seed*31+r*113+s*17)%len(b)
            if r==3 and fault=='restart':states[s]=state=json.loads(json.dumps(state));event('snapshot-restored',state=dict(state))
            if mode=='guarded8' and state['receiver'] not in (None,rd):state['receiver']=None;event('local-invalidation')
            def exchange(kind,op,body,full=False):
                nonlocal now,seq
                req=[seq//17,seq%17,op];seq+=1; wire=a['code'](req)+body if full else c['encode'](req+body)
                cost=7+2+len(wire)+2
                if now+cost>deadline:event('cannot-fit',kind=kind,cost=cost,deadline=deadline);return None
                for role,payload in [('query',a['code'](req)),('reply',wire)]:
                    start=now;obs,pcm,trace=a['exchange'](payload,0,seed*1000+seq*2+int(role=='reply'));now+=trace['slots'];event(role,kind=kind,start=start,request=req,wire=trace)
                    if save:clips.append(pcm.ravel())
                    if role=='query':
                        assert a['recover'](obs)==req;now+=2
                        if save:clips.append(np.zeros(2560,dtype='<i2'))
                assert now<=deadline
                if full:
                    h=a['recover'](obs[:5]);hits=np.flatnonzero(2*np.count_nonzero(b!=obs[5:],axis=1)<=4)
                    return int(hits[0]) if h==req and len(hits)==1 else None
                h=c['decode'](obs);return h[3:] if h is not None and h[:3]==req else None
            chosen=None; actual=(target+1)%len(b) if fault=='same-sequence' and r==3 else target
            if mode.startswith(('cached','guarded')) and state['receiver'] is None:
                n=4 if mode=='cached4' else 8; z=exchange('offer',13,c['digits'](tag(sd,n),n))
                if z is not None:
                    state['sender']=sd
                    if c['index'](z)==tag(rd,n):state['receiver']=rd;event('offer-accepted',digits=n)
                    else:event('offer-rejected',digits=n)
            if mode=='tagged' or state['receiver'] is not None:
                if mode=='guarded8' and state['sender']!=sd:
                    z=exchange('revocation',12,[16]);event('sender-revocation',received=z==[16]);state['receiver']=None if z==[16] else state['receiver']
                else:
                    addr=int(np.flatnonzero(so==actual)[0]); tagged=mode=='tagged';z=exchange('address',14,c['digits'](addr,w)+(c['digits'](tag(sd,4),4) if tagged else []))
                    if z is not None and (not tagged or c['index'](z[w:])==tag(rd,4)):chosen=int(ro[c['index'](z[:w])])
                    elif z is not None:event('tag-mismatch')
            if chosen is None:chosen=exchange('full',16,b[actual].tolist(),True)
            status='abstain' if chosen is None else 'correct' if chosen==target else 'wrong'
            event('outcome',target=target,chosen=chosen,status=status,deadline=deadline,sender_digest=sd,receiver_digest=rd);outcomes.append(status)
    return dict(seed=seed,fault=fault,mode=mode,window=window,events=events,outcomes=outcomes,slots=sum(e['wire']['slots']+2*(e['event']=='query') for e in events if 'wire' in e)),np.concatenate(clips) if clips else None

def audit(row):
    frames=[e for e in row['events'] if 'wire' in e]; outcomes=[e for e in row['events'] if e['event']=='outcome'];assert len(outcomes)==12
    assert all(a['t']<=b['t'] for a,b in zip(row['events'],row['events'][1:]));assert all(e['t']<=e['deadline'] for e in outcomes)
    assert len(frames)%2==0 and all(q['event']=='query' and p['event']=='reply' and q['request']==p['request'] and p['start']==q['t']+2 for q,p in zip(frames[::2],frames[1::2]))
    assert len({tuple(e['request']) for e in frames[::2]})==len(frames)//2
    assert row['slots']==sum(e['wire']['slots'] for e in frames)+len(frames)
    assert row['outcomes']==['abstain' if e['chosen'] is None else 'correct' if e['chosen']==e['target'] else 'wrong' for e in outcomes]

def run(root,out):
    p=pathlib.Path(__file__).with_name('catalogue-turns.py');assert sha(p.read_bytes())==HASH;c=runpy.run_path(str(p));a,books=runpy.run_path(str(p.with_name('acoustic-turns.py')))['load'](root)
    orders={(s,l):c['orders'](s,l,b) for s,ls in books.items() for l,b in ls.items()};out.mkdir();rows=[];stats={};spec=[]
    for seed,fault,mode,window in itertools.product(range(4564400,4564404),FAULTS,MODES,(64,100)):
        save=seed==4564400 and window==100 and mode=='guarded8' and fault in ('clean','sender-change','collision4');row,pcm=session(c,a,books,orders,seed,fault,mode,window,save);audit(row);rows.append(row);z=stats.setdefault(f'{window}:{fault}:{mode}',Counter());z.update(row['outcomes']);z['slots']+=row['slots']
        if save:
            name=fault+'.wav';raw=pcm.tobytes()
            with wave.open(str(out/name),'wb') as f:f.setparams((1,2,16000,0,'NONE','not compressed'));f.writeframes(raw)
            spec.append(dict(file=name,sha256=sha(raw),peak=int(abs(pcm).max())))
    receipt=dict(schema='mhac-context-memory-v1',parent=PARENT,parent_sha256=HASH,source_sha256=sha(pathlib.Path(__file__).read_bytes()),numpy=np.__version__,sessions=len(rows),stats=stats,specimens=spec,limits='Aligned clean PCM, known source and length, fixed round windows and agent order; digest change scripted, JSON memory roundtrip only, not durable crash recovery. Matching-sequence content substitution not recorded replay; short fingerprints not authentication. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Context memory</title><h1>Context memory</h1><p>Synthetic aligned PCM; start at low volume. Select session and step through dialogue.</p><select id="case"></select> <button id="prev">Previous</button> <button id="next">Next</button><p id="state"></p><pre id="event"></pre>'''+''.join(f'<p>{s["file"]}<br><audio controls preload="none" src="{s["file"]}"></audio></p>' for s in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">All traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4564400])+''';let i=0;const sel=document.querySelector('#case');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.fault,r.mode,r.window].join(' / ');sel.append(o)});function draw(){let r=rows[+sel.value],e=r.events[i];document.querySelector('#state').textContent=`Event ${i+1}/${r.events.length} | slot ${e.t} | ${r.outcomes.join(', ')}`;document.querySelector('#event').textContent=JSON.stringify(e,null,2)}sel.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+sel.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''');(out/'manifest.json').write_text(json.dumps({f.name:sha(f.read_bytes()) for f in sorted(out.iterdir())},indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
