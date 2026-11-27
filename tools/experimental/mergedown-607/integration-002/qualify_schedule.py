"""Consolidation-side byte pin and negative controls; not an acoustic oracle."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import audit_schedule as audit

# Run 033 native regeneration and Run 032 package agree on all 91 bytesets.
# This is a new consolidation pin, NOT an upstream canonical manifest.
PIN = 'bf6ef5c14903a7211322471e4057d3297c1d58c0cfa955d20abc08dde4e21ff3'
SOURCES = {
    'relay.cjs': '3ba457f85f496e4d57d9789a2dc3b7d68fe2c071',
    'bound-v2.cjs': '2aa2905d4f4d756276814d5ca941c02c51e63f97',
    'scheduled-v2.cjs': '60983bd9369729fb7dcc8f548c5371a74d02c7aa',
    'audit_schedule.py': '7f9e93cdd5e079f12f156322cab946f90f557d40',
}


def verify(root):
    expected = {'manifest.json'} | {
        f'{c}-{p}.{ext}' for c in audit.CASES for p in audit.POLICIES
        for ext in ('json', 'wav')}
    entries = list(root.iterdir())
    audit.require({p.name for p in entries} == expected and
                  all(p.is_file() and not p.is_symlink() for p in entries),
                  'output inventory mismatch')
    listing = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n'
                      for p in sorted(entries, key=lambda p: p.name))
    digest = hashlib.sha256(listing.encode('ascii')).hexdigest()
    audit.require(digest == PIN, 'consolidation output digest mismatch')
    return dict(output_files=len(entries), output_digest=digest, causal_audit=audit.main(root))


def rebuild(root):
    audit.require(not root.exists(), 'output already exists')
    here = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='mhac schedule ') as tmp:
        stage = Path(tmp)
        for name, pin in SOURCES.items():
            src = here / name
            if not src.exists() and name in ('relay.cjs', 'bound-v2.cjs'):
                src = here.parent / 'integration-001' / name
            data = src.read_bytes()
            blob = hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()
            audit.require(blob == pin, 'source blob mismatch: ' + name)
            (stage / name).write_bytes(data)
        subprocess.run(['node', str(stage / 'scheduled-v2.cjs'), str(root)],
                       check=True, stdout=subprocess.DEVNULL)
    return verify(root)


def regression(root):
    verify(root)
    with tempfile.TemporaryDirectory(prefix='mhac negative ') as tmp:
        copy = Path(tmp) / 'evidence'
        shutil.copytree(root, copy)
        p = copy / 'forged-ack-first.json'
        raw = p.read_bytes()
        def refused(label, check, expected):
            try:
                check()
            except ValueError as exc:
                audit.require(expected in str(exc), f'{label}: unexpected error {exc}')
                return label
            raise AssertionError(label + ': accepted corruption')
        passed = []
        for label, alter, causal_error in (
            ('fault label', lambda s: s['trace'][0].update(fault='clean'), None),
            ('decoder score', lambda s: s['trace'][1]['hits'][0].update(score=0.1), None),
            ('genuineness', lambda s: s['trace'][1]['events'][0].update(evaluatorGenuine=True), 'causal trace mismatch'),
            ('metric', lambda s: s['metrics'].update(invalid=0), 'metric mismatch'),
            ('timestamp', lambda s: s['trace'][0].update(atSamples=1), 'slot chronology'),
            ('origin', lambda s: s['trace'][0].update(origin='idle'), 'data scheduling'),
        ):
            s = json.loads(raw)
            alter(s)
            p.write_text(json.dumps(s, indent=2) + '\n', encoding='utf-8', newline='\n')
            if causal_error:
                passed.append(refused(label + ' causal', lambda: audit.audit(s), causal_error))
            else:
                audit.require(audit.audit(s) == s['metrics'], label + ': causal scope changed')
            passed.append(refused(label + ' pin', lambda: verify(copy), 'output digest mismatch'))
            p.write_bytes(raw)
        (copy / 'extra.json').write_text('{}', encoding='utf-8')
        passed.append(refused('extra file', lambda: verify(copy), 'inventory mismatch'))
        (copy / 'extra.json').unlink()
        p.unlink()
        passed.append(refused('missing file', lambda: verify(copy), 'inventory mismatch'))
        p.write_bytes(raw)
        verify(copy)
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--regenerate', action='store_true')
    parser.add_argument('--regression', action='store_true')
    args = parser.parse_args()
    root = args.output.resolve()
    receipt = rebuild(root) if args.regenerate else verify(root)
    if args.regression:
        receipt['negative_controls'] = regression(root)
    print(json.dumps(receipt, indent=2, sort_keys=True))
