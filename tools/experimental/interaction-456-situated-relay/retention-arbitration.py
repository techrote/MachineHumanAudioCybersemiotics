"""Interaction #456: bounded issuance memory under unequal acoustic access.
Run: python retention-arbitration.py grammar NEW_OUTPUT. Synthetic only.
"""
import collections, hashlib, itertools, json, pathlib, runpy, sys, wave
import numpy as np
PARENT = '983e13dd614a27e6f154c0c35b1b37381f10e6a6'
SHA = lambda b: hashlib.sha256(b).hexdigest()

class Memory:
    def __init__(self, mode, capacity):
        self.mode, self.capacity = mode, capacity
        self.records = collections.OrderedDict()
        self.bits = 0
    def seen(self, key):
        return bool(self.bits & (1 << (key[0]*2+key[1]))) if self.mode == 'bitmap' else key in self.records
    def issue(self, key):
        if self.mode == 'bitmap':
            self.bits |= 1 << (key[0]*2+key[1])
            return
        self.records[key] = True
        self.records.move_to_end(key)
        if self.mode == 'partition':
            own = [k for k in self.records if k[1] == key[1]]
            if len(own) > self.capacity//2: del self.records[own[0]]
        elif len(self.records) > self.capacity: self.records.popitem(last=False)
        assert len(self.records) <= self.capacity
    def snapshot(self):
        return self.bits if self.mode == 'bitmap' else list(self.records)

def simulate(targets, bank, mode, cap, policy, fault, window):
    memory = Memory(mode, cap); sent = {}; debt = [0,0]; events = []; outcomes = []; clips = []
    for e in range(12):
        now = 0; attempts = [0,0]; widths = [0,0]; chosen = [None,None]; origins = [None,None]
        while True:
            options = []
            for i in range(2):
                width = widths[i] or (2 if memory.seen((e%4,i)) else 1)
                cost = bank[e,i,width,'query']['slots'] + bank[e,i,width,'reply']['slots']
                if chosen[i] is None and attempts[i]<2 and now+cost<=window:
                    priority = (i,) if policy=='fixed' else ((i-e)%2,) if policy=='rotate' else (-debt[i],(i-e)%2)
                    options.append((priority,i,width,cost))
            if not options: break
            _,i,width,cost = min(options); widths[i] = width; attempt = attempts[i]; attempts[i] += 1
            key = (e%4,i); remembered = memory.seen(key); before = memory.snapshot(); memory.issue(key)
            h = [e%4,i] if width==1 else [e%17,e//17,i]
            q = bank[e,i,width,'query']; clean = bank[e,i,width,'reply']; r = clean; origin = e
            if attempt==0 and fault=='alternate' and e%3==2: clean = r = bank[e,i,width,'alternate']
            elif attempt==0 and fault in ('symmetric','mixed'):
                if fault=='mixed' and i==1 and e%3==0: q = bank[e,i,width,'query-loss']
                elif e>=4 and (e-4,i) in sent: r = sent[e-4,i]; origin = e-4
                elif fault=='symmetric' or i==0: r = bank[e,i,width,'reply-loss']
            start = now; now += cost; clips.append(q['pcm'].ravel()); slots = cost-q['slots']; samples = slots*1280
            emitted = received = word = None
            if q['word']==[6]+h:
                sent[e,i] = clean; emitted = clean['hash']; received = r['hash']; raw = r['pcm'].ravel()
                clips.append(np.pad(raw[:samples],(0,max(0,samples-len(raw)))))
                if r['slots']<=slots: word = r['word']
                if word is not None and word[:-2]==[7]+h: chosen[i] = word[-2]+17*word[-1]; origins[i] = origin
            else: clips.append(np.zeros(samples,dtype=np.int16)); origin = None
            events.append(dict(epoch=e,agent=i,start=start,end=now,attempt=attempt,width=width,remembered=remembered,before=before,after=memory.snapshot(),emitted=emitted,received=received,origin=origin,word=word,admitted=chosen[i]))
        for i in range(2):
            debt[i] = min(4,debt[i]+1) if chosen[i] is None else max(0,debt[i]-1)
            outcomes.append(dict(epoch=e,agent=i,target=targets[e][i],chosen=chosen[i],origin=origins[i],status='abstain' if chosen[i] is None else 'correct' if chosen[i]==targets[e][i] else 'wrong'))
    return dict(mode=mode,capacity=cap,policy=policy,fault=fault,window=window,events=events,outcomes=outcomes),clips

def audit(row):
    sent={}; ends={}; admitted={}; attempts=collections.Counter(); issued=set()
    for v in row['events']:
        e,i=v['epoch'],v['agent']; k=(e,i); key=(e%4,i)
        assert v['start']==ends.get(e,0) and v['start']<v['end']<=row['window']
        assert v['attempt']==attempts[k]<2 and k not in admitted
        if row['mode']=='bitmap':
            assert v['remembered']==(key in issued) and 0<=v['after']<256
            if v['attempt']==0 and key in issued: assert v['width']==2
        else: assert len(v['after'])<=row['capacity']
        issued.add(key); ends[e]=v['end']; attempts[k]+=1
        if v['origin'] is not None and v['origin']!=e: assert v['received']==sent[v['origin'],i]
        if v['emitted'] is not None: sent[k]=v['emitted']
        if v['admitted'] is not None: admitted[k]=v['admitted']
    for o in row['outcomes']:
        assert o['chosen']==admitted.get((o['epoch'],o['agent']))
        if row['mode']=='bitmap' and o['chosen'] is not None: assert o['origin']==o['epoch']
    assert len(row['outcomes'])==24

def run(root,out):
    here=pathlib.Path(__file__).parent; p=here/'fairness-repair.py'; epoch=here/'epoch-repair.py'
    assert SHA(p.read_bytes())=='69fcdfb9909419fd65d00989acd96f03dcbe638b5fd368cd1c769cd7410d7ca1'
    assert SHA(epoch.read_bytes())=='c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685'
    prev=runpy.run_path(str(epoch)); a,c=prev['load'](root); out.mkdir(); rows=[]; stats={}; frames=0
    for seed in (4565400,4565401,4565402):
        targets,b,n=prev['bank'](a,c,seed); frames+=n
        for (mode,cap),policy,fault,window in itertools.product((('shared',4),('shared',6),('shared',8),('partition',4),('partition',6),('bitmap',8)),('fixed','rotate','debt'),('clean','symmetric','mixed','alternate'),(48,64,88)):
            row,clips=simulate(targets,b,mode,cap,policy,fault,window); audit(row); assert row==simulate(targets,b,mode,cap,policy,fault,window)[0]; row['seed']=seed; rows.append(row)
            s=stats.setdefault(f'{mode}:{cap}:{policy}:{fault}:{window}',collections.Counter())
            for o in row['outcomes']:
                s[o['status']]+=1; s[f"{o['status']}-{o['agent']}"]+=1; s['stale']+=int(o['chosen'] is not None and o['origin']!=o['epoch'])
            s['slots']+=sum(v['end']-v['start'] for v in row['events']); s['wide']+=sum(v['width']==2 for v in row['events'])
            if seed==4565400 and fault=='mixed' and window==48 and policy=='fixed' and (mode,cap) in (('shared',4),('partition',4),('bitmap',8)):
                pcm=np.concatenate(clips).astype('<i2'); assert abs(pcm.astype('int32')).max()<=1500
                with wave.open(str(out/(mode+'.wav')),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    receipt=dict(parent=PARENT,source_sha256=SHA(pathlib.Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,frames=frames,replays=len(rows),stats=stats,limits='Fixed two-agent mod-4 compact namespace; bitmap is eight sticky issuance bits, not a general replay cache. Wider IDs unique only within 12 epochs. Known alignment, scripted loss and clean retry, fixed reservations, no turnaround. Cache record counts not bytes; sender history and traces excluded. No restart, blind acquisition, authentication, physical audition or human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Retention arbitration</title><h1>Retention arbitration laboratory</h1><p>Synthetic replay. Lower system volume before opt-in listening.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre><pre id="result"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565400])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.mode,r.capacity,r.policy,r.fault,r.window].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2);document.querySelector('#result').textContent=JSON.stringify(r.outcomes.filter(o=>o.epoch===r.events[i].epoch),null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:SHA(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(frames,len(rows))
if __name__=='__main__': run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
