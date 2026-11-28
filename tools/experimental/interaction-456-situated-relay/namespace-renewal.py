"""Interaction #456 / Draft #457: synthetic namespace renewal and snapshot rollback.
Run: python namespace-renewal.py grammar NEW_OUTPUT. No real device control.
Peer grants are unauthenticated; the independent peer database is a stipulated trust boundary.
"""
import collections, hashlib, itertools, json, pathlib, runpy, shutil, sqlite3, sys, tempfile, wave
import numpy as np
PARENT='2d47b93b7abbb5d441f3c55a4adafebac7af62b5'
sha=lambda b:hashlib.sha256(b).hexdigest()
POLICIES=('local','peer')
FAULTS=('clean','issuer-rollback','dual-rollback','stale-grant','grant-loss','alternate','exhaustion')

def init(p):
    with sqlite3.connect(p) as d: d.execute('CREATE TABLE state(g INTEGER NOT NULL,n INTEGER NOT NULL)');d.execute('INSERT INTO state VALUES (-1,0)')
def state(p,change=None):
    with sqlite3.connect(p.resolve().as_uri()+'?mode=rw',uri=True) as d:
        d.execute('PRAGMA synchronous=FULL');d.execute('BEGIN IMMEDIATE');g,n=d.execute('SELECT g,n FROM state').fetchone();assert -1<=g<4 and 0<=n<=4
        if change is not None:
            g,n=change(g,n);d.execute('UPDATE state SET g=?,n=?',(g,n))
        return g,n

def simulate(wire,targets,policy,fault,root):
    root.mkdir();local=root/'issuer.db';peer=root/'peer.db';init(local);init(peer)
    ls=root/'issuer.snapshot';ps=root/'peer.snapshot';shutil.copyfile(peer,ps)
    sent={};grants={};events=[];clips=[];need=True
    for t,target in enumerate(targets):
        agent=t%2;slots=0;origin=None;chosen=None;notice=False;grant_origin=None;issued=None;received=None;emitted=None;grant_received=None;grant_emitted=None;reason=1
        def play(f):
            nonlocal slots
            clips.append(f['pcm']);slots+=f['slots'];return f['word']
        rollback=t==4 and fault in ('issuer-rollback','dual-rollback','stale-grant','grant-loss')
        if rollback:
            shutil.copyfile(ls,local)
            if fault=='dual-rollback':shutil.copyfile(ps,peer)
            need=policy=='peer'
        g,n=state(local)
        if need or n==4:
            if policy=='local':
                if g<3:g,n=state(local,lambda g,n:(g+1,0));need=False
                else:need=True
            else:
                assert play(wire.frame([9,agent]))==[9,agent]
                pg,_=state(peer)
                if pg<3:
                    pg,_=state(peer,lambda g,n:(g+1,0));fresh=wire.frame([10,agent,pg]);grants[t]=fresh;grant_emitted=fresh['hash'];grant_origin=t
                    if fault=='stale-grant' and t==4:grant_origin=0;fresh=grants[0]
                    elif fault=='grant-loss' and t==4:fresh=wire.frame([10,agent,pg],True)
                    grant_received=fresh['hash'];word=play(fresh)
                    if word is not None and word[:2]==[10,agent]:g,n=state(local,lambda g,n:(word[2],0));need=False
                    else:need=True;reason=2
                else:need=True
        if t==0:shutil.copyfile(local,ls)
        if need:
            notice=play(wire.frame([8,agent,reason]))==[8,agent,reason]
        else:
            g,n=state(local);issued=[g,n,agent];state(local,lambda g,n:(g,n+1));assert play(wire.frame([6]+issued))==[6]+issued
            value=(target+1)%289 if fault=='alternate' and t%3==2 else target
            reply=wire.frame([7]+issued+wire.c['digits'](value,2));sent[t]=reply;emitted=reply['hash'];origin=t
            if fault in ('issuer-rollback','dual-rollback','stale-grant','grant-loss') and 4<=t<8 and t-4 in sent:origin=t-4;reply=sent[origin]
            received=reply['hash'];word=play(reply)
            if word is not None and word[:-2]==[7]+issued:chosen=wire.c['index'](word[-2:])
        assert origin is None or received==sent[origin]['hash']
        assert grant_origin is None or grant_origin==t or grant_received==grants[grant_origin]['hash']
        assert issued is not None or chosen is None
        events.append(dict(t=t,agent=agent,rollback=rollback,issued=issued,target=target,chosen=chosen,origin=origin,received=received,emitted=emitted,grant_origin=grant_origin,grant_received=grant_received,grant_emitted=grant_emitted,notice=notice,reason=reason if need else None,slots=slots,status='refused' if issued is None else 'abstain' if chosen is None else 'correct' if chosen==target else 'wrong'))
    return dict(policy=policy,fault=fault,events=events),clips

def run(grammar,out):
    here=pathlib.Path(__file__).parent;prev=here/'persistent-issuance.py';assert sha(prev.read_bytes())=='1fa37fe83a4362501bc2550c33177e6147394a2828010c15e04eb2c4a29a94dc'
    ep=here/'epoch-repair.py';assert sha(ep.read_bytes())=='c3a43e029c177d9e4f5ed445d6373abbb98a3d76dea36ff70d946d0419f97685'
    a,c=runpy.run_path(str(ep))['load'](grammar);Wire=runpy.run_path(str(prev))['Wire'];out.mkdir();rows=[];stats={};frames=0
    with tempfile.TemporaryDirectory() as tmp:
        for seed in (4565600,4565601,4565602):
            wire=Wire(a,c,seed);targets=np.random.default_rng(seed).choice(289,20,replace=False).tolist()
            for policy,fault in itertools.product(POLICIES,FAULTS):
                path=pathlib.Path(tmp)/str(len(rows));row,clips=simulate(wire,targets if fault=='exhaustion' else targets[:12],policy,fault,path)
                assert row==simulate(wire,targets if fault=='exhaustion' else targets[:12],policy,fault,path.with_suffix('.repeat'))[0];row['seed']=seed;rows.append(row)
                s=stats.setdefault(policy+':'+fault,collections.Counter())
                for e in row['events']:
                    s[e['status']]+=1;s['stale']+=int(e['chosen'] is not None and e['origin']!=e['t']);s['slots']+=e['slots'];s['notices']+=int(e['notice'])
                if seed==4565600 and fault in ('issuer-rollback','dual-rollback'):
                    pcm=np.concatenate(clips).astype('<i2');assert abs(pcm.astype('int32')).max()<=1500
                    with wave.open(str(out/(policy+'-'+fault+'.wav')),'wb') as f:f.setparams((1,2,16000,0,'NONE','not compressed'));f.writeframes(pcm.tobytes())
            frames+=len(wire.bank)
    assert stats['local:issuer-rollback']['stale']==12 and stats['peer:issuer-rollback']['stale']==0
    assert stats['peer:dual-rollback']['stale']==12 and stats['peer:stale-grant']['stale']==12
    assert all(stats[p+':exhaustion']['refused']==12 for p in POLICIES)
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frames=frames,replays=len(rows),stats=stats,python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,numpy=np.__version__,limits='Aligned PCM, scripted snapshot restoration with closed databases, four generations of four IDs, serial channel, public unauthenticated grants. No independent peer durability proof, power loss, blind acquisition or human evidence.'),indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Namespace renewal</title><h1>Namespace renewal laboratory</h1><p>Simulated actions only. Start with low system volume.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><pre id="event"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4565600])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=r.policy+' / '+r.fault;s.append(o)});function draw(){document.querySelector('#event').textContent=JSON.stringify(rows[+s.value].events[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(frames,len(rows),json.dumps(stats))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
