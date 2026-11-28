"""Independent exported-record checks. Run: python verify_matched_calibration.py OUTPUT."""
import collections, hashlib, json, sys
from pathlib import Path


def verify(p):
    r=json.loads((p/'receipt.json').read_text())
    counts=collections.defaultdict(collections.Counter)
    paired=collections.defaultdict(list)
    for line in (p/'traces.jsonl').read_text().splitlines():
        x=json.loads(line); got=x['decoded']; v=x['observed']; e=x['expected']
        if got is None:
            expected='withheld'
        else:
            assert v[0] is not None and 0<=v[0]<4 and v[1]==0
            assert all(a is None or a==b for a,b in zip(v[2:],got[0]))
            expected='correct' if not x['condition'].startswith('absent') and v[:2]==e[:2] and got[0][:3]==e[2:5] else 'wrong'
        assert x['status']==expected
        counts[x['mode'],x['condition'],x['policy']][expected]+=1
        paired[x['fixture'],x['mode'],x['condition']].append((x['policy'],x['pcm_sha256']))
    assert len(counts)==len(r['groups'])==72
    for g in r['groups']:
        assert counts[g['mode'],g['condition'],g['policy']]==g['counts']
    assert len(paired)==r['pcm_trials']==1944
    for pairs in paired.values():
        assert len(pairs)==4 and len({p for p,h in pairs})==4 and len({h for p,h in pairs})==1
    assert sum(sum(c.values()) for c in counts.values())==r['decisions']==7776
    assert len(r['null_audit'])==28
    assert all(0<=a['exceed']<=a['n']==2048 for a in r['null_audit'])
    manifest=json.loads((p/'manifest.json').read_text())
    assert set(manifest)=={'receipt.json','traces.jsonl','index.html'}
    for name,h in manifest.items():
        assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h
    print('PASS: 7776 status checks, 72 groups, 1944 paired hashes, 28 null records, 3 manifest entries')


if __name__=='__main__': verify(Path(sys.argv[1]))
