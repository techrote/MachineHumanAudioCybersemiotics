"""Interaction #456 / Draft #457: bounded multi-epoch acoustic repair.
python epoch-repair.py grammar NEW_OUTPUT
Synthetic only. Local repair opcodes, pinned aligned PCM and GF(17) adapters.
Receiver state is bounded; offline transport fixtures and audit logs are not.
No authentication, crash-safe persistence, physical actions or human evidence.
"""
import hashlib,itertools,json,pathlib,runpy,sys,wave
from collections import Counter,OrderedDict
import numpy as np
PARENT='3fda93567cf7fc5b8243b29d2816ed2d42ad2c12'
PIN='feba52809552355db1beb33a36dd7fdd619b2e0f'
sha=lambda b:hashlib.sha256(b).hexdigest()
POLICIES=('drop','tombstone','adaptive','wide')
FAULTS=('clean','wrapped','previous','reply-loss','query-loss','alternate')

def load(root):
    here=pathlib.Path(__file__).parent
    for f,h in [('acoustic-turns.py','d14f133f592f6b9ea97ca8bce18d28eede9eb65dd9958029b1ee40edfefb9e6d'),('catalogue-turns.py','a407e139a74ad49befe7cc0554c293bdc1e5f22d575fb84a930d3986057bc45b')]:
        assert sha((here/f).read_bytes())==h
    a=runpy.run_path(str(here/'acoustic-turns.py'));c=runpy.run_path(str(here/'catalogue-turns.py'))
    for f,b in a['BLOBS'].items():
        raw=(root/f).read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==b
    return runpy.run_path(str(root/'acoustic-clarification.py')),c

def bank(a,c,seed):
    rng=np.random.default_rng(seed);targets=rng.choice(289,24,replace=False).reshape(12,2).tolist();frames={};count=0
    def decode_pcm(x):
        scores=abs(x[:,80:480]@a['BASIS'].T)*2/400
        o=[int(v.argmax()) if v.max()>=600 else None for v in scores]
        return c['decode'](o[1:-1]) if o[0]==17 and o[-1]==18 and all(v is None or v<17 for v in o[1:-1]) else None
    def gen(word,lost=False):
        nonlocal count
        obs,pcm,wire=a['exchange'](c['encode'](word),0,seed*1000+count,-1 if lost else None);count+=1
        got=decode_pcm(pcm);assert got==(None if lost else word)
        return dict(word=got,pcm=pcm,slots=wire['slots'],hash=wire['pcm_sha256'])
    for e,i,width in itertools.product(range(12),range(2),(1,2)):
        h=c['digits'](e%4 if width==1 else e,width)+[i]
        frames[e,i,width,'query']=gen([6]+h)
        frames[e,i,width,'query-loss']=gen([6]+h,True)
        for f,v in [('reply',targets[e][i]),('alternate',(targets[e][i]+1)%289),('reply-loss',targets[e][i])]:
            frames[e,i,width,f]=gen([7]+h+c['digits'](v,2),f=='reply-loss')
    return targets,frames,count

def simulate(targets,frames,policy,fault,capacity,window):
    stones=OrderedDict();high=[-1,-1];log=[];outcomes=[];clips=[];peak=0
    for e in range(12):
        now=0
        for i in range(2):
            key=(e%4,i);repeat=key in stones;width=2 if policy=='wide' or policy=='adaptive' and repeat else 1
            h=[e%4,i] if width==1 else [e%17,e//17,i];q=frames[e,i,width,'query-loss' if fault=='query-loss' and e%3==2 else 'query'];origin=e
            if fault=='wrapped' and e>=4:origin=e-4
            if fault=='previous' and e>=1:origin=e-1
            f='alternate' if fault=='alternate' and e%3==2 else 'reply-loss' if fault=='reply-loss' and e%3==2 else 'reply'
            r=frames[origin,i,width,f];chosen=None;reason='deadline';start=now
            if now+q['slots']+r['slots']<=window:
                now+=q['slots'];clips.append(q['pcm']);log.append(dict(epoch=e,agent=i,t=now,event='repair-query',word=q['word'],hash=q['hash']))
                reason='missing-query'
                if q['word']==[6]+h:
                    now+=r['slots'];clips.append(r['pcm']);w=r['word'];reason='missing-or-foreign-reply'
                    log.append(dict(epoch=e,agent=i,t=now,event='repair-reply',word=w,hash=r['hash']))
                    if w is not None and w[:-2]==[7]+h:
                        reason='retired-id' if width==1 and policy!='drop' and repeat else 'nonmonotonic' if width==2 and e<=high[i] else 'admit'
                        if reason=='admit':
                            chosen=w[-2]+17*w[-1];high[i]=e
                            if policy in ('tombstone','adaptive'):
                                stones[key]=e;stones.move_to_end(key)
                                while len(stones)>capacity:stones.popitem(last=False)
            peak=max(peak,len(stones));assert len(stones)<=capacity and now<=window
            log.append(dict(epoch=e,agent=i,t=now,event=reason,width=width,repeat=repeat,stones=len(stones),cost=now-start,chosen=chosen))
            outcomes.append(dict(epoch=e,agent=i,origin=origin,target=targets[e][i],chosen=chosen,status='abstain' if chosen is None else 'correct' if chosen==targets[e][i] else 'wrong',stale=chosen is not None and origin!=e))
        # JSON roundtrip only, no crash-safe storage claim.
        snapshot=json.loads(json.dumps([list(stones.items()),high]));stones=OrderedDict((tuple(k),v) for k,v in snapshot[0]);high=snapshot[1]
    return dict(policy=policy,fault=fault,capacity=capacity,window=window,peak=peak,log=log,outcomes=outcomes),clips

def run(root,out):
    a,c=load(root);out.mkdir();rows=[];stats={};frames=0;spec=[]
    for seed in (4565100,4565101):
        targets,b,n=bank(a,c,seed);frames+=n
        for p,f,k,w in itertools.product(POLICIES,FAULTS,(2,8),(42,48)):
            x,clips=simulate(targets,b,p,f,k,w);assert x==simulate(targets,b,p,f,k,w)[0];x['seed']=seed;rows.append(x)
            s=stats.setdefault(f'{p}:{f}:{k}:{w}',Counter());s.update(o['status'] for o in x['outcomes']);s['stale']+=sum(o['stale'] for o in x['outcomes']);s['slots']+=sum(e.get('cost',0) for e in x['log']);s['peak']=max(s['peak'],x['peak'])
            if seed==4565100 and k==8 and w==48 and f=='wrapped' and p in ('drop','adaptive','wide'):
                name=p+'.wav';pcm=np.concatenate([z.ravel() for z in clips]);assert abs(pcm.astype('int32')).max()<=1500
                with wave.open(str(out/name),'wb') as v:v.setparams((1,2,16000,0,'NONE','not compressed'));v.writeframes(pcm.tobytes())
                spec.append(name)
    assert stats['drop:wrapped:8:48']['wrong']==32
    assert stats['wide:wrapped:8:48']['wrong']==0
    assert stats['tombstone:wrapped:2:48']['wrong']==32
    assert stats['tombstone:wrapped:8:48']['wrong']==0
    assert stats['wide:alternate:8:48']['wrong']==16
    (out/'traces.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
    receipt=dict(parent=PARENT,grammar=PIN,source_sha256=sha(pathlib.Path(__file__).read_bytes()),python=sys.version.split()[0],numpy=np.__version__,frames=frames,replays=len(rows),stats=stats,limits='Local monotonic epoch supplied by scheduler, 12 epochs only; no exhaustion test or crash safety. Known alignment, clean PCM and marker loss; exact earlier PCM frames replayed from external fixture bank. Shared serial channel with no turnaround. Stipulated ambiguous initial obligations, not decoded initial messages. Tombstone storage count excludes offline logs and fixture bank. Alternate valid content remains wrong. No human evidence.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Epoch repair</title><h1>Epoch repair laboratory</h1><p>Synthetic replay. Select a scenario, step through repairs. Lower system volume; no autoplay. Specimens are actual aligned acoustic wire frames.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre><pre id="result"></pre>'''+''.join(f'<p>{n} <audio controls preload="none" src="{n}"></audio></p>' for n in spec)+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([x for x in rows if x['seed']==4565100])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.policy,r.fault,r.capacity,r.window].join(' / ');s.append(o)});function draw(){let r=rows[+s.value];document.querySelector('#event').textContent=JSON.stringify(r.log[i],null,2);document.querySelector('#result').textContent=JSON.stringify(r.outcomes.filter(o=>o.epoch===r.log[i].epoch),null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].log.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(frames,len(rows))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
