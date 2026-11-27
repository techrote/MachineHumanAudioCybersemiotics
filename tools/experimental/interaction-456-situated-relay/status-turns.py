"""Interaction #456 / Draft #457: historical receipt vs sampled world state.
Synthetic only. Run: python status-turns.py grammar NEW_OUTPUT [--interactive]
"""
import collections, itertools, json, pathlib, runpy, shutil, sys, tempfile
import numpy as np
HERE=pathlib.Path(__file__).parent
PARENT='03381d7a57edb847d71b198f5b981c8fcbe4ff1e'
POLICIES=('historical','sample','bound')
FAULTS=('clean','stale-status','query-loss','reply-loss','rollback','change-after-sample')
F=runpy.run_path(str(HERE/'finality-turns.py'))
sql=F['sql']; provision=F['provision']; sha=F['sha']

def init(p):
    provision(p,['CREATE TABLE world(agent PRIMARY KEY,seq,value)','INSERT INTO world VALUES(0,-1,0),(1,-1,0)','CREATE TABLE receipts(agent,seq,value,PRIMARY KEY(agent,seq))'])

def apply(p,word,capacity):
    assert word[0]==6 and len(word)==4
    a,n,v=word[1:]
    def op(db):
        high,=db.execute('SELECT seq FROM world WHERE agent=?',(a,)).fetchone()
        old=db.execute('SELECT value FROM receipts WHERE agent=? AND seq=?',(a,n)).fetchone()
        if old is not None:return 'duplicate' if old[0]==v else 'conflict'
        if n<=high:return 'forgotten-refused'
        if n!=high+1:return 'gap-refused'
        db.execute('UPDATE world SET seq=?,value=? WHERE agent=?',(n,v,a))
        db.execute('INSERT INTO receipts VALUES(?,?,?)',(a,n,v))
        db.execute('DELETE FROM receipts WHERE agent=? AND seq<=?',(a,n-capacity))
        return 'applied'
    return sql(p,op)

def sample(p,a,n):
    def op(db):
        seq,value=db.execute('SELECT seq,value FROM world WHERE agent=?',(a,)).fetchone()
        receipt=db.execute('SELECT value FROM receipts WHERE agent=? AND seq=?',(a,n)).fetchone()
        return [16 if receipt is None else receipt[0],seq+1,value]
    return sql(p,op)

def simulate(wire,seed,policy,fault,capacity,root,manual=False):
    root.mkdir();p=root/'world.db';init(p);events=[];clips=[];history={};rng=np.random.default_rng(seed)
    values=rng.integers(1,15,size=(2,3)).tolist()
    for v in values:
        if v[1]==v[0]:v[1]=v[0]%14+1
        if v[2]==v[1]:v[2]=v[1]%14+1
    def play(word,lost=False):
        f=wire.frame(word,lost);clips.append(f['pcm']);return f
    def act(a,n,v):
        q=play([6,a,n,v]);result=apply(p,q['word'],capacity);events.append(dict(type='action',agent=a,seq=n,value=v,result=result,hash=q['hash']));return result
    def query(a,n,nonce,late):
        q=play([12,a,n,nonce],late and fault=='query-loss');got=q['word'];origin=None;candidate=None;sent=None
        if got is None:
            slots=wire.frame([13,a,n,nonce,0,0,0])['slots'];pcm=np.zeros(slots*1280,dtype='<i2');clips.append(pcm);r=dict(word=None,hash=sha(pcm.tobytes()),slots=slots)
        else:
            sent=sample(p,got[1],got[2]);word=[13]+got[1:]+sent
            f=wire.frame(word,late and fault=='reply-loss');candidate=f['hash'];history[nonce]=f;origin=nonce
            if late and fault=='stale-status':origin=a;r=history[origin]
            else:r=f
            clips.append(r['pcm']);assert r['hash']==history[origin]['hash']
        if late and fault=='change-after-sample':assert act(a,2,values[a][2])=='applied'
        w=r['word'];match=w is not None and w[:3]==[13,a,n] and (policy!='bound' or w[3]==nonce)
        historical=None if not match or w[4]==16 else w[4]
        estimate=historical if policy=='historical' else w[6] if match else None
        actual=sample(p,a,n);observed_revision=w[5]-1 if match else None
        event=dict(type='status',agent=a,seq=n,nonce=nonce,query=q['hash'],reply=r['hash'],candidate_reply=candidate,origin=origin,decoded=w,sampled=sent,receipt=historical,estimate=estimate,actual=actual[2],actual_revision=actual[1]-1,observed_revision=observed_revision,slots=q['slots']+r['slots'],outcome='unknown' if estimate is None else 'correct' if estimate==actual[2] else 'wrong')
        events.append(event)
        if manual:print(json.dumps(event,indent=2));input('Enter to continue: ')
    for a in range(2):assert act(a,0,values[a][0])=='applied';query(a,0,a,False)
    shutil.copyfile(p,root/'snapshot.db')
    for a in range(2):assert act(a,1,values[a][1])=='applied'
    if fault=='rollback':shutil.copyfile(root/'snapshot.db',p);events.append(dict(type='rollback'))
    for a in range(2):query(a,0,a+2,True)
    for a in range(2):assert act(a,0,values[a][0]) in ('duplicate','forgotten-refused')
    stats=collections.Counter(e['outcome'] for e in events if e['type']=='status' and e['nonce']>=2)
    stats['receipt_unknown']=sum(e['receipt'] is None for e in events if e['type']=='status' and e['nonce']>=2)
    stats['forgotten_refused']=sum(e.get('result')=='forgotten-refused' for e in events)
    assert sql(p,lambda db:db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0])<=2*capacity
    return dict(seed=seed,policy=policy,fault=fault,capacity=capacity,events=events,stats=dict(stats)),clips

def run(grammar,out,manual=False):
    assert sha((HERE/'finality-turns.py').read_bytes())=='be72484daa5b1db025ec034495de5e089ba4fed03eb555958c43f659c528b56b'
    a,c=runpy.run_path(str(HERE/'epoch-repair.py'))['load'](grammar);Wire=runpy.run_path(str(HERE/'persistent-issuance.py'))['Wire'];out.mkdir();rows=[];stats={};frames=0
    with tempfile.TemporaryDirectory() as tmp:
        root=pathlib.Path(tmp)
        if manual:
            policy=input('Policy (historical/sample/bound): ');fault=input('Fault ('+'/'.join(FAULTS)+'): ');capacity=int(input('Receipt capacity (1/3): '));assert policy in POLICIES and fault in FAULTS and capacity in (1,3)
            row,clips=simulate(Wire(a,c,4566000),4566000,policy,fault,capacity,root/'live',True);(out/'live.json').write_text(json.dumps(row,indent=2));F['save_wav'](out/'live.wav',clips);return
        for seed in (4566000,4566001):
            wire=Wire(a,c,seed)
            for policy,fault,capacity in itertools.product(POLICIES,FAULTS,(1,3)):
                path=root/str(len(rows));row,clips=simulate(wire,seed,policy,fault,capacity,path);assert row==simulate(wire,seed,policy,fault,capacity,path.with_suffix('.repeat'))[0];rows.append(row);stats.setdefault(f'{policy}:{fault}:{capacity}',collections.Counter()).update(row['stats'])
                if seed==4566000 and policy=='bound' and capacity==1 and fault in ('clean','stale-status','change-after-sample'):F['save_wav'](out/(fault+'.wav'),clips)
            frames+=len(wire.bank)
    assert stats['historical:clean:3']['wrong']==4 and stats['bound:clean:1']['correct']==4
    assert stats['sample:stale-status:1']['wrong']==4 and stats['bound:stale-status:1']['unknown']==4
    assert stats['bound:change-after-sample:1']['wrong']==4 and stats['bound:rollback:1']['correct']==4
    assert stats['bound:clean:1']['forgotten_refused']==4
    (out/'traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'receipt.json').write_text(json.dumps(dict(parent=PARENT,source_sha256=sha(pathlib.Path(__file__).read_bytes()),frames=frames,replays=len(rows),stats=stats,python=sys.version.split()[0],numpy=np.__version__,limits='Aligned PCM, honest peers, ordered per-agent finite sequence, synthetic world only. Status is a sample, not a guarantee of current or continuous state.'),indent=2)+'\n')
    (out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Status turns</title><style>body{font:16px system-ui;max-width:850px;margin:2em auto}pre{white-space:pre-wrap}</style><h1>Status turns</h1><p>Historical receipt versus sampled world state. Select a replay and step through events. Optional audio: start with low hardware volume.</p><select id="s"></select><button id="prev">Previous</button><button id="next">Next</button><p id="summary"></p><pre id="event"></pre>'''+''.join(f'<p>{p.name} <audio controls preload="none" src="{p.name}"></audio></p>' for p in sorted(out.glob('*.wav')))+'''<p><a href="receipt.json">Receipt</a> | <a href="traces.jsonl">Traces</a></p><script>const rows='''+json.dumps([r for r in rows if r['seed']==4566000])+''';let i=0;const s=document.querySelector('#s');rows.forEach((r,j)=>{let o=document.createElement('option');o.value=j;o.textContent=r.policy+' / '+r.fault+' / '+r.capacity+' receipts per agent';s.append(o)});function draw(){const r=rows[+s.value];document.querySelector('#summary').textContent=(i+1)+' / '+r.events.length+' | '+r.events[i].type;document.querySelector('#event').textContent=JSON.stringify(r.events[i],null,2)}s.onchange=()=>{i=0;draw()};document.querySelector('#prev').onclick=()=>{i=Math.max(0,i-1);draw()};document.querySelector('#next').onclick=()=>{i=Math.min(rows[+s.value].events.length-1,i+1);draw()};document.querySelectorAll('audio').forEach(a=>a.volume=.2);draw()</script>''')
    (out/'manifest.json').write_text(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},indent=2)+'\n');print(frames,len(rows),sum(sum(e['type']=='status' for e in r['events']) for r in rows))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]),'--interactive' in sys.argv)
