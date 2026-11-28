"""Refs #607: compare real package export with frozen independent oracle (synthetic only)."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import unittest


def require(ok, message):
    if not ok:
        raise ValueError(message)


def near(a, b):
    return (a is None and b is None) or (a is not None and b is not None and abs(a-b) < 1e-9)


def q(x):
    return None if x is None else math.floor(x*100_000_000 + .5)


def measure(rows):
    groups = defaultdict(list)
    counts = defaultdict(set)
    cells = 0
    for row in rows:
        c = row['condition']
        key = c['frame'] + '|' + row['model']
        condition = tuple(c[k] for k in ('p','q','rate','ms'))
        require(condition not in counts[key], 'duplicate condition')
        counts[key].add(condition)
        ordered = sorted(row['cells'], key=lambda x: ','.join(map(str,x['samples'])))
        require(len({tuple(x['samples']) for x in ordered}) == len(ordered), 'duplicate cell')
        require(near(sum(sum(x['mass']) for x in ordered), 1), 'row mass')
        entries = []
        for x in ordered:
            require(len(x['mass']) == 4 and all(math.isfinite(v) and v >= 0 for v in x['mass']), 'invalid cell mass')
            require(near(max(x['mass']),x['oracleCorrect']), 'cell oracle')
            require(near(sum(x['mass']),x['probability']), 'cell probability')
            pred = x['prediction']
            require(pred is None or type(pred) is int and 1 <= pred <= 4, 'prediction range')
            require((pred is None) == (x['confidence'] is None), 'prediction/confidence disagreement')
            correct = 0 if pred is None else x['mass'][pred-1]
            require(near(x['correct'],correct) and near(x['wrong'],x['probability']-correct), 'cell accounting')
            entries.append([x['samples'],[q(v) for v in x['mass']],q(x['confidence']),q(x['oracleCorrect'])])
        cells += len(entries)
        groups[key].append([list(condition),entries])
    return {'rows':len(rows),'cells':cells,'counts':{k:len(v) for k,v in counts.items()},
            'fingerprints':{k:sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest() for k,v in groups.items()}}


def check_receipt(receipt, oracle):
    result = measure(receipt['rows'])
    for key in ('rows','cells','fingerprints'):
        require(result[key] == oracle[key], 'oracle mismatch: '+key)
    require(all(n == 144 for n in result['counts'].values()), 'factorial coverage')
    observed = {}
    for s in receipt['summary']:
        key = s['frame']+'|'+s['model']
        require(key not in observed and s['conditions']==144, 'summary coverage')
        x = next(v for v in s['curve'] if v['cutoff']==1)
        observed[key] = {'oov':s['oov'],'oracle':s['oracle'],'certainty_coverage':x['coverage'],
                         'certainty_correct':x['correct'],'certainty_wrong':x['wrong'],
                         'certainty_conditional_error':x['conditionalError']}
    require(observed.keys() == oracle['summary'].keys(),'summary keys')
    for key, row in observed.items():
        for metric, actual in row.items():
            require(near(actual, oracle['summary'][key][metric]), 'summary mismatch: '+key+' '+metric)
    return result


def inventory(root):
    files = {}
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink(),'unexpected symlink')
        if p.is_file():
            files[p.relative_to(root).as_posix()] = sha256(p.read_bytes()).hexdigest()
    return files


def verify(first, second):
    from check_selective_transfer import run
    from build_observatory import PINS, REF, blob
    a,b = inventory(first),inventory(second)
    require(a == b,'repeated package mismatch')
    manifest = json.loads((first/'package-manifest.json').read_text(encoding='utf-8'))
    listed = dict(a); del listed['package-manifest.json']
    require(listed == manifest['files'],'package inventory mismatch')
    require(manifest['sourcePins']==PINS and manifest['frozenRef']==REF,'package source authority')
    for name, pin in PINS.items():
        require(blob((first/'source'/name).read_bytes())==pin,'frozen blob '+name)
    oracle = run()
    receipt = json.loads((first/'selective/receipt.json').read_text(encoding='utf-8'))
    result = check_receipt(receipt, oracle)
    hashes = []
    for i,w in enumerate(receipt['witnesses']):
        digest = a[f'selective/witness-{i}.wav']
        require(digest == w['sha256'],'receipt WAV hash')
        hashes.append(digest)
    require(hashes == oracle['wav_hashes'],'oracle WAV hashes')
    return {'status':'PASS','packageFiles':len(a),'sourceBlobs':len(PINS),
            'rows':result['rows'],'cells':result['cells'],'fingerprints':result['fingerprints'],
            'certaintySummaryComparisons':len(oracle['summary'])*6,'oracleWavHashes':hashes,
            'packageManifestSHA256':a['package-manifest.json'],'audio':manifest['audio']}


class ContractTests(unittest.TestCase):
    def row(self):
        return {'condition':{'frame':'receipt','p':1,'q':1,'rate':8000,'ms':200},'model':'nominal',
                'cells':[{'samples':[1,2,3],'mass':[.25]*4,'oracleCorrect':.25,'probability':1,
                          'prediction':1,'confidence':.25,'correct':.25,'wrong':.75}]}

    def test_measure(self):
        r=measure([self.row()]); self.assertEqual((r['rows'],r['cells']),(1,1))
        self.assertEqual(r['fingerprints']['receipt|nominal'],sha256(b'[[[1,1,8000,200],[[[1,2,3],[25000000,25000000,25000000,25000000],25000000,25000000]]]]').hexdigest())

    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError,'duplicate condition'): measure([self.row(),self.row()])

    def test_wrong_mass(self):
        r=self.row(); r['cells'][0]['wrong']=0
        with self.assertRaisesRegex(ValueError,'cell accounting'): measure([r])

    def test_wrong_oracle(self):
        r=self.row(); r['cells'][0]['oracleCorrect']=.5
        with self.assertRaisesRegex(ValueError,'cell oracle'): measure([r])

    def test_wrong_prediction(self):
        r=self.row(); r['cells'][0]['prediction']=0
        with self.assertRaisesRegex(ValueError,'prediction range'): measure([r])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('first',type=Path); p.add_argument('second',type=Path)
    args=p.parse_args(); print(json.dumps(verify(args.first,args.second),indent=2,sort_keys=True))
