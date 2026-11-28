"""Recount exported evidence and compare optional deterministic replay."""
import hashlib,json,sys,wave
from pathlib import Path
from collections import Counter
p=Path(sys.argv[1]); manifest=json.loads((p/'manifest.json').read_text()); r=json.loads((p/'receipt.json').read_text()); t=json.loads((p/'traces.json').read_text())
assert set(manifest)=={x.name for x in p.iterdir()}-{'manifest.json'}
for n,h in manifest.items(): assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h
assert len(t)==r['signals']==1440 and sum(len(x['results']) for x in t)==r['decisions']==5760
assert len({(x['index'],x['condition']) for x in t})==len(t)
for c,ms in r['summary'].items():
    for m,counts in ms.items():
        got=Counter()
        for x in t:
            if x['condition']!=c: continue
            y=x['results'][m]; status='withheld' if y['decoded'] is None else 'correct' if y['decoded']==x['tree'] else 'wrong'
            assert status==y['status']; got[status]+=1
        assert got==counts and sum(got.values())==90
for w in p.glob('*.wav'):
    with wave.open(str(w)) as f: assert (f.getnchannels(),f.getsampwidth(),f.getframerate())==(1,2,16000) and f.getnframes()%3840==0
for c in r['contrasts']: assert all(x['decoded']==c['tree'] for x in c['results'].values())
if len(sys.argv)>2:
    q=Path(sys.argv[2]); assert {x.name for x in p.iterdir()}=={x.name for x in q.iterdir()}; assert all(x.read_bytes()==(q/x.name).read_bytes() for x in p.iterdir())
print(f'PASS: {len(manifest)} hashes, 64 comparative groups, {len(list(p.glob("*.wav")))} WAVs, 4 contrasts; repeat comparison={len(sys.argv)>2}')
