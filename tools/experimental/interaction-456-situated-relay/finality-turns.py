"""Interaction #456 / Draft #457: synthetic persistent application and acknowledgement.
Run: python finality-turns.py grammar NEW_OUTPUT [--interactive]
No physical action, authentication, human evidence or canonical protocol changes.
"""
import collections, hashlib, itertools, json, os, pathlib, runpy, shutil, sqlite3, subprocess, sys, tempfile, wave
import numpy as np
PARENT='aa899fbff2036cff30a94c5e97fb3124fca3582c'
POLICIES=('naive','receipt','retirement')
FAULTS=('clean','ack-loss','request-loss','stale-ack','reopen','ledger-rollback')
NAMES=('applied','duplicate','conflict','retired','unknown')
sha=lambda b:hashlib.sha256(b).hexdigest()
HERE=pathlib.Path(__file__).parent
S=runpy.run_path(str(HERE/'session-renewal.py'))
sql=S['sql']; provision=S['provision']; grant=S['grant']

def init(path):
    provision(path,['CREATE TABLE effects(n INTEGER NOT NULL)','INSERT INTO effects VALUES(0)','CREATE TABLE receipts(g,n,a,lo,hi,v,PRIMARY KEY(g,n,a,lo,hi))','CREATE TABLE retired(g,lo,hi,PRIMARY KEY(g,lo,hi))'])

def apply(path,word,policy,crash=None):
    assert word[0]==6 and len(word)==8
    g,n,a,lo,hi,v,w=word[1:];key=(g,n,a,lo,hi);value=v+17*w
    def operation(db):
        old=db.execute('SELECT v FROM receipts WHERE g=? AND n=? AND a=? AND lo=? AND hi=?',key).fetchone()
        if policy!='naive' and old is not None:return 1 if old[0]==value else 2
        if policy=='retirement' and db.execute('SELECT 1 FROM retired WHERE g=? AND lo=? AND hi=?',(g,lo,hi)).fetchone():return 3
        db.execute('UPDATE effects SET n=n+1')
        db.execute('INSERT OR IGNORE INTO receipts VALUES(?,?,?,?,?,?)',key+(value,))
        if crash=='before':os._exit(91)
        return 0
    result=sql(path,operation)
    if crash=='after':os._exit(92)
    return result

def count(path):return sql(path,lambda d:d.execute('SELECT n FROM effects').fetchone()[0])

def simulate(wire,seed,policy,fault,budget,root,manual=False):
    root.mkdir();peer=root/'peer.db';ledger=root/'ledger.db';init(ledger)
    provision(peer,['CREATE TABLE counter(n)','INSERT INTO counter VALUES(0)','CREATE TABLE grants(agent,nonce,g,PRIMARY KEY(agent,nonce))'])
    shutil.copyfile(ledger,root/'snapshot.db');events=[];clips=[];ack_history={};applied=[];intents={};rng=np.random.default_rng(seed)
    def play(word,lost=False):
        f=wire.frame(word,lost);clips.append(f['pcm']);return f
    def renew(session):
        request=play([9,session%2,session,0]);g,new=grant(peer,request['word'],True);r=play([10]+request['word'][1:]+[g]);assert r['word']==[10,session%2,session,0,g]
        events.append(dict(type='grant',session=session,g=g,allocated=new,query=request['hash'],reply=r['hash']));return g
    def action(h,v,kind='normal'):
        key=tuple(h);word=[6]+h+wire.c['digits'](v,2);intents.setdefault(key,v);slots=0;knowledge='unknown';attempts=[]
        for k in range(2):
            q=wire.frame(word);cost=q['slots']+q['slots']+1
            if slots+cost>budget:break
            q=play(word,fault=='request-loss' and k==0 and kind=='normal');slots+=q['slots'];got=q['word'];status=4 if got is None else apply(ledger,got,policy)
            if status==0:applied.append((key,v))
            origin=None;expected=None
            if got is None:
                pcm=np.zeros((q['slots']+1)*1280,dtype='<i2');clips.append(pcm);r=dict(word=None,hash=sha(pcm.tobytes()),slots=q['slots']+1)
            else:
                ack=[7]+got[1:]+[status];r=wire.frame(ack);origin=(len(events),k);ack_history[origin]=r;expected=r['hash']
                if fault=='stale-ack' and kind=='normal' and len(ack_history)>1 and k==0:
                    origin=next(iter(ack_history));r=ack_history[origin];clips.append(r['pcm'])
                else:r=play(ack,fault=='ack-loss' and k==0 and kind=='normal')
            slots+=r['slots'];assert slots<=budget
            got_ack=r['word'];matches=got_ack is not None and got_ack[:-1]==[7]+word[1:]
            if matches:knowledge=NAMES[got_ack[-1]]
            attempts.append(dict(k=k,request=q['hash'],decoded=got,receiver=NAMES[status],ack=r['hash'],ack_origin=origin,ack_expected=expected,decoded_ack=got_ack,match=matches))
            if knowledge!='unknown':break
        events.append(dict(type='action',kind=kind,key=h,value=v,knowledge=knowledge,attempts=attempts,slots=slots,world=count(ledger)))
        if manual:print(events[-1]);input('Enter for next event: ')
    for session in range(3):
        g=renew(session);h=[g,0,session%2,session,0];v=int(rng.integers(289));action(h,v)
        action([g,1,session%2,session,0],(v+1)%289)
        retire=play([11,g,session,0]);assert retire['word']==[11,g,session,0]
        sql(ledger,lambda d:d.execute('INSERT OR IGNORE INTO retired VALUES(?,?,?)',(g,session,0)));events.append(dict(type='retire',session=session,wire=retire['hash']))
        if fault=='ledger-rollback':shutil.copyfile(root/'snapshot.db',ledger);events.append(dict(type='rollback',world=count(ledger)))
        if fault in ('reopen','ledger-rollback'):
            assert renew(session)==g;action(h,v,'repeated');action(h,(v+2)%289,'conflicting');action([g,2,session%2,session,0],(v+3)%289,'new-after-retirement')
    counts=collections.Counter(k for k,v in applied);actions=[e for e in events if e['type']=='action'];stats=dict(applications=len(applied),duplicate_effects=sum(n-1 for n in counts.values()),conflicting_effects=sum(v!=intents[k] for k,v in applied),new_retired_effects=sum(k[1]==2 for k,v in applied),known=sum(e['knowledge'] in ('applied','duplicate') for e in actions),unknown=sum(e['knowledge']=='unknown' for e in actions),world=count(ledger),slots=sum(e['slots'] for e in actions))
    # Independent recount of effects and emitted acknowledgement identities from trace.
    reconstructed=[];history={}
    for i,e in enumerate(events):
        if e['type']!='action':continue
        for a in e['attempts']:
            history[(i,a['k'])]=a['ack_expected']
            if a['decoded_ack'] is not None:assert a['ack']==history[tuple(a['ack_origin'])]
            if a['receiver']=='applied':reconstructed.append((tuple(e['key']),wire.c['index'](a['decoded'][-2:])))
    assert reconstructed==applied
    return dict(seed=seed,policy=policy,fault=fault,budget=budget,events=events,stats=stats),clips

def probes(root):
    p=root/'crash.db';init(p);word=[6,0,0,0,0,0,1,0];result={}
    for phase,code,expected in [('before',91,0),('after',92,1)]:
        r=subprocess.run([sys.executable,__file__,'--crash',str(p),phase]);assert r.returncode==code and count(p)==expected;result[phase]=count(p)
    assert apply(p,word,'retirement')==1 and count(p)==1;result['retry_after_commit']=count(p)
    return result

def save_wav(path,clips):
    pcm=np.concatenate(clips).astype('<i2');assert abs(pcm.astype('int32')).max()<=1500
    with wave.open(str(path),'wb') as w:w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(pcm.tobytes())

def run(grammar,out,manual=False):
    for name,digest in [('session-renewal.py','69aace071278ba5ac1160b9634092fcfc7ce7766aa03fd148d3334156b493625'),('persistent-issuance.py','1fa37fe83a4362501bc2550c33177e6147394a2828010c15e04eb2c4a29a94dc'),('epoch-repair.py','c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685')]:assert sha((HERE/name).read_bytes())==digest
    a,c=runpy.run_path(str(HERE/'epoch-repair.py'))['load'](grammar);Wire=runpy.run_path(str(HERE/'persistent-issuance.py'))['Wire'];out.mkdir();rows=[];stats={};frames=0
    with tempfile.TemporaryDirectory() as temp:
        root=pathlib.Path(temp);p=probes(root)
        if manual:
            policy=input('Policy (naive/receipt/retirement): ');fault=input('Fault ('+'/'.join(FAULTS)+'): ');assert policy in POLICIES and fault in FAULTS
            row,clips=simulate(Wire(a,c,4565900),4565900,policy,fault,64,root/'live',True);print(row['stats']);(out/'live.json').write_text(json.dumps(row,indent=2));save_wav(out/'live.wav',clips);return
        for seed in (4565900,4565901):
            wire=Wire(a,c,seed)
            for policy,fault,budget in itertools.product(POLICIES,FAULTS,(32,64)):
                path=root/str(len(rows));row,clips=simulate(wire,seed,policy,fault,budget,path);assert row==simulate(wire,seed,policy,fault,budget,path.with_suffix('.repeat'))[0];rows.append(row);stats.setdefault(f'{policy}:{fault}:{budget}',collections.Counter()).update(row['stats'])
                if seed==4565900 and budget==64 and policy in ('naive','retirement') and fault in ('ack-loss','reopen'):
                    save_wav(out/(policy+'-'+fault+'.wav'),clips)
            frames+=len(wire.bank)
    assert stats['naive:ack-loss:64']['duplicate_effects']==12 and stats['receipt:ack-loss:64']['duplicate_effects']==0
    assert stats['retirement:reopen:64']['new_retired_effects']==0 and stats['receipt:reopen:64']['new_retired_effects']==6
    assert stats['retirement:ledger-rollback:64']['duplicate_effects']>0
    for policy in POLICIES:
        assert stats[f'{policy}:ack-loss:32']['unknown']==12 and stats[f'{policy}:ack-loss:32']['applications']==12
        assert stats[f'{policy}:request-loss:32']['unknown']==12 and stats[f'{policy}:request-loss:32']['applications']==0
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frames=frames,replays=len(rows),stats=stats,process_probes=p,python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,numpy=np.__version__,limits='Synthetic atomic SQLite effects, aligned PCM, honest peers, scripted loss. No physical exactly-once guarantee or human evidence.'),indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Finality turns</title><style>body{font:16px system-ui;max-width:850px;margin:2em auto}pre{white-space:pre-wrap}</style><h1>Finality turns laboratory</h1><p>Compare simulated world effects and sender knowledge. Select a replay and step through grants, requests, acknowledgements and retirement. Audio optional; start with low system volume.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><p id="summary"></p><pre id="event"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565900])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=r.policy+' / '+r.fault+' / '+r.budget+' slots';s.append(o)});function draw(){const r=rows[+s.value];document.querySelector('#summary').textContent=(i+1)+' / '+r.events.length+' | '+r.events[i].type;document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(frames,len(rows),sum(sum(e['type']=='action' for e in r['events']) for r in rows))
if __name__=='__main__':
    if sys.argv[1]=='--crash':apply(pathlib.Path(sys.argv[2]),[6,0,0,0,0,0,1,0],'retirement',sys.argv[3])
    else:run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),'--interactive' in sys.argv)
