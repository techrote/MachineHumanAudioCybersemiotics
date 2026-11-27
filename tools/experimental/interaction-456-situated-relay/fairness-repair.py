"""Interaction #456: repair arbitration, synthetic aligned PCM, no human evidence.
Run: python fairness-repair.py grammar NEW_OUTPUT
"""
import collections, hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np
PARENT = 'e5de108c259589c7855b3cb7797899bdde20e609'
POLICIES = ('fixed','rotate','first-pass','deficit','edf')
FAULTS = ('clean','loss-replay','asymmetric','alternate','query-loss')
sha = lambda b: hashlib.sha256(b).hexdigest()

def simulate(targets, bank, policy, fault, capacity, window, urgent):
    cache=collections.OrderedDict(); sent={}; debt=[0,0]; events=[]; outcomes=[]; clips=[]; peak=0
    for e in range(12):
        now=0; attempts=[0,0]; chosen=[None,None]; origin=[None,None]; widths=[None,None]
        deadlines=[window,window]
        if urgent: deadlines[e%2]=min(window,42)
        while True:
            options=[]
            for i in range(2):
                width=widths[i] or (2 if (e%4,i) in cache else 1)
                cost=bank[e,i,width,'query']['slots']+bank[e,i,width,'reply']['slots']
                if chosen[i] is not None or attempts[i]>=2 or now+cost>deadlines[i]: continue
                priority={'fixed':(i,), 'rotate':((i-e)%2,), 'first-pass':(attempts[i],(i-e)%2), 'deficit':(-debt[i],(i-e)%2), 'edf':(deadlines[i],attempts[i],(i-e)%2)}[policy]
                options.append((priority,i,width,cost))
            if not options: break
            _,i,width,cost=min(options); widths[i]=width; attempt=attempts[i]; attempts[i]+=1
            header=[e%4,i] if width==1 else [e%17,e//17,i]
            qlost=attempt==0 and fault=='query-loss' and e%3==0
            lost=attempt==0 and ((fault=='loss-replay' and e<4) or (fault=='asymmetric' and (i==0 or e%3==0)))
            alt=attempt==0 and fault=='alternate' and e%3==2
            q=bank[e,i,width,'query-loss' if qlost else 'query']; clean=bank[e,i,width,'alternate' if alt else 'reply']
            start=now; now+=cost; clips.append(q['pcm'].ravel()); key=(e%4,i)
            cache[key]=e; cache.move_to_end(key)
            while len(cache)>capacity: cache.popitem(last=False)
            peak=max(peak,len(cache)); old=None; emitted=None; received=None; word=None
            reply_slots=cost-q['slots']; samples=reply_slots*1280
            if q['word']==[6]+header:
                old=sent.get((e-4,i)) if attempt==0 and fault=='loss-replay' and e>=4 else None
                r=old if old is not None else bank[e,i,width,'reply-loss'] if lost else clean
                sent[e,i]=clean; emitted=clean['hash']; received=r['hash']
                raw=r['pcm'].ravel(); assert len(raw)==r['slots']*1280
                clips.append(np.pad(raw[:samples],(0,max(0,samples-len(raw)))))
                if r['slots']<=reply_slots: word=r['word']
                if word is not None and word[:-2]==[7]+header:
                    chosen[i]=word[-2]+17*word[-1]; origin[i]=e-4 if old is not None else e
            else: clips.append(np.zeros(samples,dtype=np.int16))
            events.append(dict(epoch=e,agent=i,start=start,end=now,deadline=deadlines[i],attempt=attempt,width=width,query=q['word'],query_hash=q['hash'],emitted=emitted,received=received,replay_epoch=e-4 if old is not None else None,word=word,admitted=chosen[i],debt=debt.copy()))
        for i in range(2):
            debt[i]+=int(chosen[i] is None)
            outcomes.append(dict(epoch=e,agent=i,attempts=attempts[i],chosen=chosen[i],target=targets[e][i],origin=origin[i],status='abstain' if chosen[i] is None else 'correct' if chosen[i]==targets[e][i] else 'wrong'))
    return dict(policy=policy,fault=fault,capacity=capacity,window=window,urgent=urgent,peak=peak,events=events,outcomes=outcomes),clips

def audit(row):
    end={}; seen={}; count=collections.Counter(); admitted={}
    for v in row['events']:
        e,i=v['epoch'],v['agent']; k=e,i
        assert v['start']==end.get(e,0) and v['start']<v['end']<=v['deadline']<=row['window']
        end[e]=v['end']; assert v['attempt']==count[k]<2; count[k]+=1
        assert k not in admitted
        if v['replay_epoch'] is not None: assert v['received']==seen[v['replay_epoch'],i]
        if v['emitted'] is not None: seen[k]=v['emitted']
        if v['admitted'] is not None: admitted[k]=v['admitted']
    assert row['peak']<=row['capacity'] and len(row['outcomes'])==24
    for o in row['outcomes']:
        k=o['epoch'],o['agent']; assert o['attempts']==count[k] and o['chosen']==admitted.get(k)
        assert o['status']==('abstain' if o['chosen'] is None else 'correct' if o['chosen']==o['target'] else 'wrong')

def run(root,out):
    here=pathlib.Path(__file__).parent; parent=here/'issued-repair.py'; epoch=here/'epoch-repair.py'
    assert sha(parent.read_bytes())=='385abcb338d609acc6d5d2b53752155a33d45b02c9006321d392f6d9edff0171'
    assert sha(epoch.read_bytes())=='c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685'
    prev=runpy.run_path(str(epoch)); a,c=prev['load'](root); out.mkdir(); rows=[]; stats={}; frames=0
    for seed in (4565300,4565301):
        targets,b,n=prev['bank'](a,c,seed); frames+=n
        for p,f,k,w,u in itertools.product(POLICIES,FAULTS,(2,8),(48,64,88),(False,True)):
            row,clips=simulate(targets,b,p,f,k,w,u); assert row==simulate(targets,b,p,f,k,w,u)[0]; audit(row); row['seed']=seed; rows.append(row)
            s=stats.setdefault(f'{p}:{f}:{k}:{w}:{int(u)}',collections.Counter())
            for o in row['outcomes']:
                s[o['status']]+=1; s[f"{o['status']}-{o['agent']}"]+=1; s['stale']+=int(o['chosen'] is not None and o['origin']!=o['epoch'])
            s['slots']+=sum(v['end']-v['start'] for v in row['events']); s['attempts']+=len(row['events'])
            if seed==4565300 and f=='loss-replay' and k==8 and w==48 and not u and p in ('fixed','rotate','deficit','first-pass'):
                pcm=np.concatenate(clips).astype('<i2'); assert abs(pcm.astype('int32')).max()<=1500
                with wave.open(str(out/(p+'.wav')),'wb') as v: v.setparams((1,2,16000,0,'NONE','not compressed')); v.writeframes(pcm.tobytes())
    assert stats['fixed:loss-replay:8:48:0']['correct-1']==0
    assert stats['rotate:loss-replay:8:48:0']['correct-0']==stats['rotate:loss-replay:8:48:0']['correct-1']
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,frames=frames,replays=len(rows),stats=stats,limits='Known alignment, shared serialized channel, fixed reservation per attempted exchange including silence; replay truncation if longer than reserved reply. Scripted loss, clean retry. Deficit counts failed admissions (not ground-truth errors), updated per epoch. Declared deadlines, no oracle of future faults. Finite receiver cache only; offline sender history and logs excluded. No durable allocation, blind acquisition, human evidence or physical audition.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Repair arbitration</title><h1>Repair arbitration laboratory</h1><p>Synthetic agents; opt-in sound. Lower system volume first.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre><pre id="result"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565300])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.policy,r.fault,r.capacity,r.window,r.urgent].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2);document.querySelector('#result').textContent=JSON.stringify(r.outcomes.filter(o=>o.epoch===r.events[i].epoch),null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(frames,len(rows))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
