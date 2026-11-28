"""Refs #442 / Draft #443. Synthetic process interruption apparatus, not a security protocol.
python interrupted-reservations.py NEW_OUTPUT_DIR (standard library; exclusive owner).
"""
import hashlib,itertools,json,pathlib,runpy,shutil,sqlite3,subprocess,sys,tempfile
PARENT='1fc3d8cf80fff30d272d5772add74406d29fa1f5'
PIN='eeec73e6b105ce2de9a060a3a1a3d88b90d42c2c5766c32062c1d8fd6f610a0a'
HERE=pathlib.Path(__file__).resolve(); CAP=83521

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blocks():
    p=HERE.with_name('reservation-blocks.py');assert digest(p)==PIN
    return runpy.run_path(str(p))['Blocks']

def worker(path,width,policy,stage,count):
    s=blocks()(path,width);issued=[]
    if stage=='precommit':
        s.db.execute('BEGIN IMMEDIATE');n=s.cursor();s.db.execute('UPDATE cursor SET n=?',(min(CAP,n+width,(n//289+1)*289),))
    elif stage=='postcommit':
        s.reserve() # persisted block, token not handed outside process
    else:
        for i in range(count):
            t=s.reserve()
            if t is None:break
            issued.append(t[0]*289+t[1]);assert s.consume(t)
        if stage=='clean' and policy=='reclaim' and s.tail():
            assert s.pending is None
            with s.db:
                s.db.execute('BEGIN IMMEDIATE')
                assert s.cursor()==s.hi
                s.db.execute('UPDATE cursor SET n=?',(s.lo,))
    receipt=dict(issued=issued,writes=s.writes+int(stage=='clean' and policy=='reclaim' and s.tail()>0),visible_cursor=s.cursor())
    if stage=='clean':s.close()
    print(json.dumps(receipt),flush=True)
    if stage!='clean':sys.stdin.read(1) # parent terminates process at witnessed barrier

def launch(path,width,policy,stage,count):
    p=subprocess.Popen([sys.executable,str(HERE),'--worker',str(path),str(width),policy,stage,str(count)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        line=p.stdout.readline();assert line, p.stderr.read()
        r=json.loads(line)
        if stage!='clean':p.kill()
        _,err=p.communicate(timeout=10)
        assert (p.returncode==0)==(stage=='clean'),err
        r['termination']='normal' if stage=='clean' else 'parent-kill';return r
    finally:
        if p.poll() is None:p.kill();p.wait()

def trial(root,width,policy,stage,count,start):
    p=root/'trial.db';s=blocks()(p,width,start);s.close()
    a=launch(p,width,policy,stage,count)
    s=blocks()(p,width);cursor=s.cursor();t=s.reserve();n=None if t is None else t[0]*289+t[1];s.close();p.unlink()
    assert n is None or n not in a['issued']
    expected=start if stage=='precommit' else min(CAP,start+width,(start//289+1)*289) if stage=='postcommit' else (start+len(a['issued']) if stage=='clean' and policy=='reclaim' else a['visible_cursor'])
    assert cursor==expected and n==(cursor if cursor<CAP else None)
    lost=cursor-start-len(a['issued']);assert lost>=0
    return dict(width=width,policy=policy,stage=stage,count=count,start=start,reopened_cursor=cursor,next_token=n,lost=lost,**a)

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        root=pathlib.Path(tmp)
        rows=[trial(root,w,policy,stage,1,start) for w in (1,8,289) for policy,stage in [('discard','precommit'),('discard','postcommit'),('discard','issued'),('discard','clean'),('reclaim','clean')] for start in (0,CAP-7)]
        # snapshot rollback remains a negative witness, even with clean tail reclamation
        p=root/'rollback.db';s=blocks()(p,8,0);s.close();snap=root/'snapshot.db';shutil.copyfile(p,snap)
        a=launch(p,8,'reclaim','clean',1);shutil.copyfile(snap,p);b=launch(p,8,'reclaim','clean',1);assert a['issued']==b['issued']==[0]
    receipt=dict(schema='mhac-interrupted-reservations-v1',parent=PARENT,parent_sha256=PIN,source_sha256=digest(HERE),python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,rows=len(rows),actual_kills=sum(r['termination']=='parent-kill' for r in rows),rollback_reissued_token=0,limits='Exclusive serialized owner. Actual child termination after flushed barriers; precommit dirty-page state not controlled. No physical power loss, concurrent ownership, acoustic or human evidence. Reclaim only unissued tail after all issued tokens resolved. Allocation writes count committed allocation/reclaim only; postcommit token is conservatively undisclosed.')
    for name,data in [('receipt',receipt),('traces',rows)]: (out/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Interrupted reservations</title><style>body{font:16px system-ui;max-width:950px;margin:2em auto;padding:1em}table{border-collapse:collapse;width:100%}td,th{padding:.6em;border-bottom:1px solid #aaa;text-align:left}select{margin:1em}</style><h1>Interrupted reservation laboratory</h1><p>Actual child termination; exclusive owner. Lost = persistent cursor advance minus externally issued identifiers. No power-loss or human evidence.</p><label>Stage <select id="stage"><option>precommit</option><option>postcommit</option><option>issued</option><option>clean</option></select></label><label>Requested issues <select id="count"><option>1</option></select></label><label>Start <select id="start"><option>0</option><option>83514</option></select></label><table><thead><tr><th>Width</th><th>Policy</th><th>Issued</th><th>Lost</th><th>Next</th><th>Writes</th></tr></thead><tbody id="rows"></tbody></table><p><a href="traces.json">Traces</a> | <a href="receipt.json">Receipt</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;function draw(){const a=data.filter(r=>['stage','count','start'].every(k=>String(r[k])===document.getElementById(k).value));document.getElementById('rows').replaceChildren(...a.map(r=>{const t=document.createElement('tr');for(const v of [r.width,r.policy,r.issued.length,r.lost,r.next_token??'exhausted',r.writes]){const d=document.createElement('td');d.textContent=v;t.append(d)}return t}))}document.querySelectorAll('select').forEach(s=>s.onchange=draw);draw()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(rows,separators=(',',':'))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:digest(p) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':
    if sys.argv[1]=='--worker':worker(pathlib.Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5],int(sys.argv[6]))
    else:run(pathlib.Path(sys.argv[1]))
