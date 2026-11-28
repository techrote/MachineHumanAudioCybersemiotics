"""Interaction #456: issued vs admitted repair memory. Synthetic, aligned PCM.
Run: python issued-repair.py grammar NEW_OUTPUT [seed]
Uses exact Run 051 source and its pinned dependencies; no human evidence.
"""
import collections, hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np
PARENT = '012908da3b6960371fcc3a9364fce892dbbbc317'
POLICIES = ('admitted','issued','issued-retry','issued-reserve','wide')
FAULTS = ('clean','reply-loss-replay','query-loss-replay','reply-loss','alternate')
sha = lambda x: hashlib.sha256(x).hexdigest()

def simulate(targets, bank, policy, fault, capacity, window):
    cache = collections.OrderedDict(); sent = {}; events = []; outcomes = []; clips = []; peak = 0
    for e in range(12):
        now = 0
        for i in range(2):
            key = (e%4,i); repeat = key in cache
            width = 2 if policy == 'wide' or repeat else 1
            header = [e%4,i] if width == 1 else [e%17,e//17,i]
            chosen = None; origin = None; attempts = 0
            for attempt in range(2 if policy in ('issued-retry','issued-reserve') else 1):
                qlost = attempt == 0 and fault == 'query-loss-replay' and e < 4
                lost = attempt == 0 and ((fault == 'reply-loss-replay' and e < 4) or (fault == 'reply-loss' and e%3 == 2))
                alt = attempt == 0 and fault == 'alternate' and e%3 == 2
                q = bank[e,i,width,'query-loss' if qlost else 'query']
                clean = bank[e,i,width,'alternate' if alt else 'reply']
                old = sent.get((e-4,i)) if attempt == 0 and e >= 4 and fault.endswith('-replay') else None
                r = old[0] if old else bank[e,i,width,'reply-loss'] if lost else clean
                reserve = 22 if attempt and policy == 'issued-reserve' and i == 0 else 0
                if now + q['slots'] + clean['slots'] + reserve > window:
                    events.append(dict(epoch=e,agent=i,t=now,event='budget-refusal',attempt=attempt)); break
                attempts += 1; now += q['slots']; clips.append(q['pcm'])
                events.append(dict(epoch=e,agent=i,t=now,event='query',width=width,attempt=attempt,hash=q['hash'],word=q['word']))
                if policy.startswith('issued'):
                    cache[key] = e; cache.move_to_end(key)
                    while len(cache)>capacity: cache.popitem(last=False)
                if q['word'] != [6]+header: continue
                # Sender emits the current clean frame; channel may erase its marker or substitute an actual earlier emission.
                sent[e,i] = (clean,e)
                available = window-now-reserve
                if r['slots'] > available:
                    clips.append(r['pcm'][:available]); now += available
                    events.append(dict(epoch=e,agent=i,t=now,event='truncated-reply',attempt=attempt,emitted_hash=clean['hash'])); continue
                now += r['slots']; clips.append(r['pcm']); w = r['word']
                origin = old[1] if old else e
                events.append(dict(epoch=e,agent=i,t=now,event='reply',attempt=attempt,hash=r['hash'],emitted_hash=clean['hash'],origin=origin,word=w))
                if w is not None and w[:-2] == [7]+header:
                    chosen = w[-2]+17*w[-1]
                    if policy == 'admitted':
                        cache[key] = e; cache.move_to_end(key)
                        while len(cache)>capacity: cache.popitem(last=False)
                    break
            peak = max(peak,len(cache)); assert len(cache)<=capacity and now<=window
            outcomes.append(dict(epoch=e,agent=i,width=width,repeat=repeat,attempts=attempts,chosen=chosen,target=targets[e][i],origin=origin,status='abstain' if chosen is None else 'correct' if chosen==targets[e][i] else 'wrong',stale=chosen is not None and origin!=e))
        events.append(dict(epoch=e,t=now,event='epoch-end',cache=len(cache)))
    return dict(policy=policy,fault=fault,capacity=capacity,window=window,peak=peak,events=events,outcomes=outcomes),clips

def audit(x):
    sent={}; count=collections.Counter(); times={}; outcomes=x['outcomes']
    for v in x['events']:
        e=v['epoch']; t=v['t']; assert times.get(e,0)<=t<=x['window']; times[e]=t
        if v['event']=='query': count[e,v['agent']]+=1
        if v['event']=='reply':
            k=(e,v['agent']); origin=v['origin']
            if origin!=e: assert sent[origin,v['agent']]==v['hash']
            sent[k]=v['emitted_hash']
        if v['event']=='truncated-reply': sent[e,v['agent']]=v['emitted_hash']
    for o in outcomes:
        assert count[o['epoch'],o['agent']]==o['attempts']<=2
        assert o['status']==('abstain' if o['chosen'] is None else 'correct' if o['chosen']==o['target'] else 'wrong')
    assert len(outcomes)==24

def allocate(next_id, digits=2):
    if not 0 <= next_id < 17**digits: return None,next_id
    return next_id,next_id+1

def run(root,out,seeds):
    here=pathlib.Path(__file__).parent; parent=here/'epoch-repair.py'
    assert sha(parent.read_bytes())=='c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685'
    prev=runpy.run_path(str(parent)); a,c=prev['load'](root); out.mkdir(); rows=[]; stats={}; frames=0
    for seed in seeds:
        targets,b,n=prev['bank'](a,c,seed); frames+=n
        for p,f,k,w in itertools.product(POLICIES,FAULTS,(2,8),(48,88)):
            x,clips=simulate(targets,b,p,f,k,w); assert x==simulate(targets,b,p,f,k,w)[0]; audit(x); x['seed']=seed; rows.append(x)
            s=stats.setdefault(f'{p}:{f}:{k}:{w}',collections.Counter()); s.update(o['status'] for o in x['outcomes']); s['stale']+=sum(o['stale'] for o in x['outcomes']); s['attempts']+=sum(o['attempts'] for o in x['outcomes']); s['slots']+=sum(v['t'] for v in x['events'] if v['event']=='epoch-end')
            if seed==seeds[0] and f=='reply-loss-replay' and k==8 and w==48 and p in ('admitted','issued','issued-retry'):
                pcm=np.concatenate([z.ravel() for z in clips]); assert abs(pcm.astype('int32')).max()<=1500
                with wave.open(str(out/(p+'.wav')),'wb') as v:v.setparams((1,2,16000,0,'NONE','not compressed'));v.writeframes(pcm.tobytes())
    cursor=0; ids=[]
    for _ in range(290):
        v,cursor=allocate(cursor); ids.append(v)
    assert ids==list(range(289))+[None] and allocate(cursor)==(None,289)
    assert stats['admitted:reply-loss-replay:8:48']['stale']>0 and stats['issued:reply-loss-replay:8:48']['stale']==0
    assert stats['issued:reply-loss-replay:2:48']['stale']>0 and stats['wide:reply-loss-replay:8:48']['stale']==0
    (out/'traces.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
    receipt=dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,frames=frames,replays=len(rows),seeds=seeds,allocator=dict(unique=289,exhaustion='refuse',reset='not tested'),stats=stats,limits='Aligned clean and marker-erased PCM from frozen bank, reused by scheduling replays. Earlier sender emissions recorded only after query reception, channel replay replaces current response. Budget checks use expected current frame lengths, not replay origin. The sender ledger is offline fixture machinery, not receiver memory. No turnaround, durable persistence, authentication, blind acquisition, physical audition or human evidence. The allocator probe is symbolic, not a 289-epoch PCM run.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Issued repair</title><h1>Issued repair laboratory</h1><p>Synthetic replay. Lower system volume. No autoplay.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre><pre id="result"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([x for x in rows if x['seed']==seeds[0]])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.policy,r.fault,r.capacity,r.window].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2);document.querySelector('#result').textContent=JSON.stringify(r.outcomes.filter(o=>o.epoch===r.events[i].epoch),null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(frames,len(rows))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),[int(sys.argv[3])] if len(sys.argv)>3 else [4565200,4565201])
