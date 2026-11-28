"""Measurement #442 / Draft #443: process interruption at tail reclamation.
Synthetic exclusive-owner SQLite fixtures, not a security or human experiment.
python reclamation-boundaries.py NEW_OUTPUT_DIR
"""
import hashlib, itertools, json, pathlib, queue, runpy, sqlite3, subprocess, sys, tempfile, threading
HERE = pathlib.Path(__file__).resolve()
PARENT = '66e708f930ba2c7e2dba371be6afbb3702e3df06'
PIN = '21c32e5abfe456fc566004a39aeeea47c4f8c26585cd6484d6fb5b3e2a817bab'
CAP = 83521

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def blocks():
    p = HERE.with_name('interrupted-reservations.py')
    if digest(p) != PIN: raise ValueError('parent source mismatch')
    return runpy.run_path(str(p))['blocks']()

def worker(path, width, journal, stage):
    s = blocks()(path, width)
    assert s.db.execute('PRAGMA journal_mode').fetchone()[0] == journal.lower()
    token = s.reserve(); assert token is not None and s.consume(token)
    assert s.pending is None and s.tail() > 0
    high, low = s.hi, s.lo
    s.db.execute('BEGIN IMMEDIATE')
    assert s.cursor() == high
    s.db.execute('UPDATE cursor SET n=?', (low,))
    if stage != 'before': s.db.commit()
    receipt = dict(issued=token[0]*289+token[1], high=high, low=low, visible=s.cursor(), in_transaction=s.db.in_transaction)
    if stage == 'normal': s.close()
    print(json.dumps(receipt), flush=True)
    if stage != 'normal': sys.stdin.read(1)

def launch(path, width, journal, stage):
    p = subprocess.Popen([sys.executable, str(HERE), '--worker', str(path), str(width), journal, stage], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    q = queue.Queue()
    reader = threading.Thread(target=lambda: q.put(p.stdout.readline()), daemon=True)
    reader.start()
    try:
        try: line = q.get(timeout=5)
        except queue.Empty: raise TimeoutError('worker barrier exceeded five seconds')
        if not line: raise RuntimeError('worker exited before barrier')
        r = json.loads(line)
        if stage != 'normal': p.kill()
        reader.join(timeout=1)
        _, err = p.communicate(timeout=5)
        assert (p.returncode == 0) == (stage == 'normal'), err
        return r
    finally:
        if p.poll() is None: p.kill(); p.wait(timeout=5)
        reader.join(timeout=1)
        for stream in (p.stdin, p.stdout, p.stderr): stream.close()

def trial(path, width, journal, stage, start):
    s = blocks()(path, width, start)
    assert s.db.execute('PRAGMA journal_mode='+journal).fetchone()[0] == journal.lower()
    s.close()
    r = launch(path, width, journal, stage)
    s = blocks()(path, width)
    cursor = s.cursor()
    integrity = s.db.execute('PRAGMA integrity_check').fetchone()[0]
    assert integrity == 'ok'
    high = min(CAP, start+width, (start//289+1)*289)
    assert r == dict(issued=start, high=high, low=start+1, visible=start+1, in_transaction=stage=='before')
    expected = high if stage == 'before' else start+1
    assert cursor == expected
    tokens = []
    for _ in range(3):
        t = s.reserve()
        if t is None: break
        assert s.consume(t); tokens.append(t[0]*289+t[1])
    s.close()
    assert tokens == list(range(expected,min(CAP,expected+3)))
    assert start not in tokens
    lost = cursor-start-1
    assert 1+lost+CAP-cursor == CAP-start
    return dict(width=width,journal=journal,stage=stage,start=start,termination='normal' if stage=='normal' else 'parent-kill',receipt=r,reopened_cursor=cursor,lost=lost,next_tokens=tokens,integrity=integrity)

def run(out):
    out.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        rows=[trial(pathlib.Path(tmp)/f'{i}.db',*args) for i,args in enumerate(itertools.product((8,289),('DELETE','WAL'),('before','after','normal'),(0,288-1,CAP-7)))]
    assert len(rows)==36
    receipt=dict(schema='mhac-reclamation-boundaries-v1',parent=PARENT,parent_sha256=PIN,source_sha256=digest(HERE),python=sys.version.split()[0],sqlite=sqlite3.sqlite_version,rows=len(rows),kills=sum(r['termination']=='parent-kill' for r in rows),limits='Exclusive serialized owner. Process kill at flushed barrier, not mid-commit or power loss. No concurrent ownership, snapshot rollback protection, authentication, PCM or human evidence. Issued token resolved before reclaim; no old worker resumes. Deterministic factorial; no random seed needed.')
    for name,data in [('receipt',receipt),('traces',rows)]:
        (out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    html='''<!doctype html><meta charset="utf-8"><title>Reclamation boundaries</title><style>body{font:16px system-ui;max-width:950px;margin:2em auto;padding:1em}table{border-collapse:collapse;width:100%}td,th{padding:.5em;border-bottom:1px solid #aaa;text-align:left}select{margin:1em}</style><h1>Interrupted tail reclamation</h1><p>Actual SQLite process interruption, exclusive owner. Before/after refer to the reclamation commit, not allocation. No power-loss or human evidence.</p><label>Journal <select id="journal"><option>DELETE</option><option>WAL</option></select></label><label>Start <select id="start"><option>0</option><option>287</option><option>83514</option></select></label><table><thead><tr><th>Width</th><th>Stage</th><th>Cursor</th><th>Lost</th><th>Next tokens</th><th>Integrity</th></tr></thead><tbody id="rows"></tbody></table><p><a href="traces.json">Traces</a> | <a href="receipt.json">Receipt</a> | <a href="manifest.json">Hashes</a></p><script>const data=DATA;function draw(){const a=data.filter(r=>['journal','start'].every(k=>String(r[k])===document.getElementById(k).value));document.getElementById('rows').replaceChildren(...a.map(r=>{const t=document.createElement('tr');for(const v of [r.width,r.stage,r.reopened_cursor,r.lost,r.next_tokens.join(', ')||'exhausted',r.integrity]){const d=document.createElement('td');d.textContent=v;t.append(d)}return t}))}document.querySelectorAll('select').forEach(s=>s.onchange=draw);draw()</script>'''
    (out/'index.html').write_text(html.replace('DATA',json.dumps(rows,separators=(',',':'))),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:digest(p) for p in sorted(out.iterdir())},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':
    if sys.argv[1]=='--worker': worker(pathlib.Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5])
    else: run(pathlib.Path(sys.argv[1]))
