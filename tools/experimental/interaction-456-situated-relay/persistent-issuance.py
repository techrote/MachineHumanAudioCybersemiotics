"""Interaction #456 / Draft #457. Synthetic finite issuance; no device control.
Run: python persistent-issuance.py grammar NEW_OUTPUT
SQLite process-exit probes are not power-loss or filesystem rollback qualification.
"""
import collections, hashlib, itertools, json, os, pathlib, runpy, sqlite3, subprocess, sys, tempfile, wave
import numpy as np
PARENT = '6113ac2cf4ef7108144ddf9a3aa3e8b3bcb9be6a'
CAP = 8
sha = lambda b: hashlib.sha256(b).hexdigest()

def provision(path):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE issuance (singleton INTEGER PRIMARY KEY CHECK(singleton=1), high INTEGER NOT NULL CHECK(high BETWEEN 0 AND 8))')
        db.execute('INSERT INTO issuance VALUES (1,0)')

def reserve(path, count, crash=None):
    db = sqlite3.connect(path.resolve().as_uri()+'?mode=rw', uri=True, isolation_level=None)
    try:
        db.execute('PRAGMA synchronous=FULL'); db.execute('BEGIN IMMEDIATE')
        high, = db.execute('SELECT high FROM issuance WHERE singleton=1').fetchone()
        if not isinstance(high,int) or not 0<=high<=CAP: raise ValueError('invalid high watermark')
        end = min(CAP, high+count)
        db.execute('UPDATE issuance SET high=? WHERE singleton=1',(end,))
        if crash=='before': os._exit(91)
        db.execute('COMMIT')
        if crash=='after': os._exit(92)
        return list(range(high,end))
    finally: db.close()

class Issuer:
    def __init__(self,path,policy): self.path=path; self.policy=policy; self.lease=[]; self.local=0
    def take(self):
        if self.policy=='volatile':
            if self.local==CAP: return None
            value=self.local; self.local+=1; return value
        if not self.lease: self.lease=reserve(self.path,1 if self.policy=='durable' else 3)
        return self.lease.pop(0) if self.lease else None

def crash_probes(root):
    p=root/'crash.db'; provision(p); results={}
    for phase,code,expected in [('before',91,[0]),('after',92,[4])]:
        r=subprocess.run([sys.executable,__file__,'--crash',str(p),phase],capture_output=True)
        assert r.returncode==code,(phase,r.returncode,r.stderr)
        got=reserve(p,1); assert got==expected; results[phase]=got
    a=Issuer(p,'lease3'); b=Issuer(p,'lease3'); got=[a.take(),b.take(),a.take(),a.take(),b.take()]; assert got==[5,None,6,7,None]; results['interleaved']=got
    missing=root/'missing.db'
    try: reserve(missing,1)
    except sqlite3.Error: assert not missing.exists(); results['missing_refused']=True
    else: raise AssertionError('implicit reprovision')
    corrupt=root/'corrupt.db'; corrupt.write_bytes(b'not a database')
    try: reserve(corrupt,1)
    except sqlite3.Error: results['corrupt_refused']=True
    else: raise AssertionError('corrupt state accepted')
    return results

class Wire:
    def __init__(self,a,c,seed): self.a=a; self.c=c; self.seed=seed; self.bank={}
    def frame(self,word,lost=False):
        key=(tuple(word),lost)
        if key not in self.bank:
            a,c=self.a,self.c
            _,pcm,meta=a['exchange'](c['encode'](word),0,self.seed*1000+len(self.bank),-1 if lost else None)
            scores=abs(pcm[:,80:480]@a['BASIS'].T)*2/400
            obs=[int(v.argmax()) if v.max()>=600 else None for v in scores]
            got=c['decode'](obs[1:-1]) if obs[0]==17 and obs[-1]==18 and all(v is None or v<17 for v in obs[1:-1]) else None
            assert got==(None if lost else word)
            self.bank[key]=dict(word=got,pcm=pcm.ravel(),hash=meta['pcm_sha256'],slots=meta['slots'])
        return self.bank[key]

def simulate(wire,targets,policy,fault,restart,path):
    provision(path); issuer=Issuer(path,policy); sent={}; trace=[]; clips=[]; issued=set()
    for t,target in enumerate(targets):
        agent=t%2; reset=restart and t in (4,8)
        if reset: issuer=Issuer(path,policy)
        ident=issuer.take(); chosen=None; origin=None; notice=False; emitted=None; received=None; repeated=ident is not None and ident in issued; slots=0
        def play(f):
            nonlocal slots
            clips.append(f['pcm']); slots+=f['slots']; return f['word']
        if ident is None:
            notice=play(wire.frame([8,agent,1],fault=='refusal-loss'))==[8,agent,1]
        else:
            if policy!='volatile': assert not repeated
            issued.add(ident); header=[ident,agent]; assert play(wire.frame([6]+header))==[6]+header
            actual=(target+1)%289 if fault=='alternate' and t%3==2 else target
            reply=wire.frame([7]+header+wire.c['digits'](actual,2)); sent[t]=reply; emitted=reply['hash']; origin=t
            if fault in ('replay','loss-replay') and t-4 in sent: origin=t-4; reply=sent[origin]
            elif fault=='loss-replay' and t<4: reply=wire.frame([7]+header+wire.c['digits'](actual,2),True)
            received=reply['hash']; word=play(reply)
            if word is not None and word[:-2]==[7]+header: chosen=wire.c['index'](word[-2:])
        if origin is not None and origin!=t: assert received==sent[origin]['hash']
        assert slots<=20 and (ident is not None or chosen is None)
        trace.append(dict(t=t,agent=agent,restart=reset,id=ident,repeated=repeated,target=target,chosen=chosen,origin=origin,emitted=emitted,received=received,notice=notice,slots=slots,status='refused' if ident is None else 'abstain' if chosen is None else 'correct' if chosen==target else 'wrong'))
    return dict(policy=policy,fault=fault,restart=restart,events=trace),clips

def run(root,out):
    here=pathlib.Path(__file__).parent; prev=here/'retention-arbitration.py'; assert sha(prev.read_bytes())=='a25c903dd9b7f6057ba52edf6e1be09421ee755eeb37c96b168408b974f8ca4e'
    ep=here/'epoch-repair.py'; assert sha(ep.read_bytes())=='c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685'
    a,c=runpy.run_path(str(ep))['load'](root); out.mkdir(); rows=[]; stats={}; frames=0
    with tempfile.TemporaryDirectory() as temp:
        work=pathlib.Path(temp); probes=crash_probes(work)
        for seed in (4565500,4565501,4565502):
            wire=Wire(a,c,seed); targets=np.random.default_rng(seed).choice(289,12,replace=False).tolist()
            for policy,fault,restart in itertools.product(('volatile','durable','lease3'),('clean','replay','loss-replay','alternate','refusal-loss'),(False,True)):
                p=work/f'{len(rows)}.db'; row,clips=simulate(wire,targets,policy,fault,restart,p)
                assert row==simulate(wire,targets,policy,fault,restart,p.with_suffix('.repeat'))[0]; row['seed']=seed; rows.append(row)
                s=stats.setdefault(f'{policy}:{fault}:{restart}',collections.Counter())
                for e in row['events']:
                    s[e['status']]+=1; s['stale']+=int(e['chosen'] is not None and e['origin']!=e['t']); s['notices']+=int(e['notice']); s['slots']+=e['slots']; s['reused']+=int(e['repeated'])
                    if policy!='volatile' and e['chosen'] is not None: assert e['origin']==e['t']
                if seed==4565500 and fault=='loss-replay' and restart:
                    pcm=np.concatenate(clips).astype('<i2'); assert abs(pcm.astype('int32')).max()<=1500
                    with wave.open(str(out/(policy+'.wav')),'wb') as f: f.setparams((1,2,16000,0,'NONE','not compressed')); f.writeframes(pcm.tobytes())
            frames+=len(wire.bank)
    assert stats['volatile:replay:True']['stale']==24 and stats['durable:replay:True']['stale']==0
    assert stats['durable:clean:True']['correct']==24 and stats['lease3:clean:True']['correct']==18
    assert stats['durable:refusal-loss:True']['notices']==0 and stats['durable:refusal-loss:True']['refused']==12
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)); (out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frames=frames,replays=len(rows),probes=probes,stats=stats,python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,numpy=np.__version__,limits='Synthetic aligned PCM, eight IDs total, serial two-agent requests, scripted faults. SQLite local process exits only; no power-loss, backup rollback, DB replacement, authentication, human evidence or real control.'),indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Persistent issuance</title><h1>Persistent issuance laboratory</h1><p>Simulated actions only. Lower system volume before listening.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565500])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=[r.policy,r.fault,'restart='+r.restart].join(' / ');s.append(o)});function draw(){document.querySelector('#event').textContent=JSON.stringify(rows[+s.value].events[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(11,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n'); print(frames,len(rows),probes)
if __name__=='__main__':
    if sys.argv[1]=='--crash': reserve(pathlib.Path(sys.argv[2]),3,sys.argv[3])
    else: run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
