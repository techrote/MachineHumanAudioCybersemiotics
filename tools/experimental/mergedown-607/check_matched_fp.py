"""Native, synthetic-only qualification of the frozen #443 matched-FP module."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import wave

REF = '5a1e3a857389ce8f6763c66847c9522179dcbf59'
PREFIX = 'tools/experimental/observatory-442-receipt-inspector/'
BLOBS = {'phase-fit.cjs': 'fd0fbca5bc784fadb9227baa628fb290506b841c',
         'matched-fp.cjs': 'e2c5e29240844a643ba966e5a261909d39f07862'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def max_matches(truth, seen, tol):
    # Independent maximum-cardinality bipartite matching by exhaustive recursion.
    if not truth or not seen:
        return 0
    return max([max_matches(truth[1:], seen, tol)] +
               [1 + max_matches(truth[1:], seen[:i] + seen[i+1:], tol)
                for i, value in enumerate(seen) if abs(truth[0] - value) <= tol])


def audit(r, out):
    require(r['schema'] == 'mhac-matched-fp-v1', 'schema')
    require(r['matchToleranceSamples'] == 8 and r['rate'] == 8000, 'units')
    require(len(r['development']) == 152 and len(r['evaluation']) == len(r['rows']) == 312, 'corpus size')
    require(not ({c['seed'] for c in r['development']} & {c['seed'] for c in r['evaluation']}), 'seed separation')
    require([row['condition'] for row in r['rows']] == r['evaluation'], 'row identity')
    require(r['methods'] == ['fixed', 'quadrature', 'joint-refit'], 'receiver identity')
    require(r['budgets'] == [0, .125, .25, .5] and [o['budget'] for o in r['operating']] == r['budgets'], 'budgets')
    for m, curve in enumerate(r['curves']):
        require([c['threshold'] for c in curve] == r['thresholds'], 'curve grid')
        for c in curve:
            require(c['tp'] + c['fn'] == 384 and c['packets'] == 152 and c['positivePackets'] == 128, 'development accounting')
        for o in r['operating']:
            feasible = [c for c in curve if c['nullFalse'] == 0 and c['positiveFP'] <= o['budget'] * c['positivePackets']]
            best = max(feasible, key=lambda c: (c['tp'], -c['positiveFP'], c['threshold']))
            require(o['receivers'][m]['selected'] == best, 'operating-point selection')
    for row in r['rows']:
        require(len(row['outcomes']) == 3 and len(row['truth']) == (3 if row['condition']['f'] else 0), 'row shape')
        for o in row['outcomes']:
            require(o['seen'] == sorted(e['t'] for e in o['events']) and len(o['seen']) <= 4, 'event accounting')
            tp = max_matches(row['truth'], o['seen'], 8)
            require((o['tp'], o['fp'], o['fn']) == (tp, len(o['seen'])-tp, len(row['truth'])-tp), 'independent matching')
    known = lambda c: c['f'] in (500, 800)
    groups = {'all': lambda c: True, 'known': known,
              'overlap': lambda c: known(c) and c['overlap'],
              'separated': lambda c: known(c) and not c['overlap'],
              'shifted': lambda c: known(c) and c['phase'] == 'shifted',
              'unseen': lambda c: c['f'] == 650, 'null': lambda c: c['f'] == 0}
    require(r['witnessBudget'] == .25, 'witness budget')
    for m, recv in enumerate(r['operating'][2]['receivers']):
        for name, select in groups.items():
            a = dict.fromkeys(('packets', 'tp', 'fp', 'fn', 'exact', 'nullFalse', 'positiveFP', 'positivePackets'), 0)
            for row in r['rows']:
                if not select(row['condition']):
                    continue
                o = row['outcomes'][m]
                a['packets'] += 1
                for k in ('tp', 'fp', 'fn'):
                    a[k] += o[k]
                a['exact'] += int(o['fp'] == o['fn'] == 0)
                if row['condition']['f']:
                    a['positivePackets'] += 1
                    a['positiveFP'] += o['fp']
                else:
                    a['nullFalse'] += int(o['fp'] > 0)
            require(all(recv['evaluation'][name][k] == v for k, v in a.items()), 'evaluation aggregate')
    require([s['i'] for s in r['specimens']] == r['witnesses'] and len(set(r['witnesses'])) == 4, 'specimen coverage')
    peaks = []
    for s in r['specimens']:
        require(s['name'] == f"witness-{s['i']}.wav", 'specimen name')
        p = out / s['name']
        require(sha(p.read_bytes()) == s['sha256'], 'WAV hash')
        with wave.open(str(p), 'rb') as w:
            require((w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, 8000, 3200), 'WAV format')
            peak = max(map(abs, struct.unpack('<3200h', w.readframes(3200))))
        require(peak == r['rows'][s['i']]['peak'] and peak < 10000, 'WAV peak')
        peaks.append(peak)
    require('autoplay' not in (out / 'index.html').read_text(encoding='utf-8').lower(), 'autoplay')
    return {'developmentPackets': 152, 'evaluationPackets': 312, 'matchingDecisions': 936,
            'developmentCurveCells': sum(map(len, r['curves'])), 'operatingSelections': 12,
            'evaluationGroupsAtWitnessBudget': 21, 'wavPeaksPCM16': peaks}


def inventory(path):
    return {p.name: sha(p.read_bytes()) for p in sorted(path.iterdir()) if p.is_file()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('destination', type=Path, help='new output directory')
    p.add_argument('--source-dir', type=Path, help='exact two transferred source files; otherwise use local Git objects')
    args = p.parse_args()
    dest = args.destination.resolve()
    require(not dest.exists(), 'destination must not exist')
    inputs = {}
    for name, expected in BLOBS.items():
        data = ((args.source_dir / name).read_bytes() if args.source_dir else
                subprocess.check_output(['git', 'show', REF + ':' + PREFIX + name]))
        require(blob(data) == expected, 'source blob mismatch: ' + name)
        inputs[name] = data
    src = dest / 'source'
    src.mkdir(parents=True)
    for name, data in inputs.items():
        (src / name).write_bytes(data)
    for name in ('gallery', 'repeat'):
        subprocess.run(['node', str(src / 'matched-fp.cjs'), str(dest / name)], check=True, stdout=subprocess.DEVNULL)
    a, b = dest / 'gallery', dest / 'repeat'
    hashes = inventory(a)
    require(hashes == inventory(b) and len(hashes) == 6, 'repeat export mismatch')
    r = json.loads((a / 'receipt.json').read_text(encoding='utf-8'))
    summary = audit(r, a)
    import copy
    for mutation in ('matching', 'selection', 'hash', 'aggregate'):
        bad = copy.deepcopy(r)
        if mutation == 'matching':
            bad['rows'][24]['outcomes'][2]['tp'] += 1
        elif mutation == 'selection':
            bad['operating'][2]['receivers'][0]['selected']['threshold'] += .01
        elif mutation == 'hash':
            bad['specimens'][0]['sha256'] = '0' * 64
        else:
            bad['operating'][2]['receivers'][0]['evaluation']['known']['tp'] += 1
        try:
            audit(bad, a)
        except ValueError:
            continue
        raise ValueError('corruption accepted: ' + mutation)
    result = {'sourceRef': REF, 'blobs': BLOBS, 'nativeNode': subprocess.check_output(['node', '-v'], text=True).strip(),
              'summary': summary, 'upstreamAssertions': r['assertions'], 'repeatFiles': len(hashes),
              'corruptionControlsRejected': 4, 'files': hashes,
              'scope': 'Recorded curve selection, witness-budget matching/accounting and specimen integrity; not independent DSP or full threshold-curve reconstruction.'}
    (dest / 'qualification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
