"""Native reconstruction and durable regression tests for frozen Integration #607."""
import hashlib
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import check_binding as check

HERE = Path(__file__).resolve().parent
PINS = {'relay.cjs': '3ba457f85f496e4d57d9789a2dc3b7d68fe2c071',
        'bound-v2.cjs': '2aa2905d4f4d756276814d5ca941c02c51e63f97'}
EXPECTED = {'wavs': 11, 'aligned_slots': 19, 'v1_packets': 18,
            'v2_packets': 15, 'parity_pairs': 84}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def blob(path):
    b = path.read_bytes()
    return hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()


def reject(fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(reason in str(exc), f'unexpected failure: {exc}')
    else:
        raise ValueError('negative control accepted: ' + reason)


def parity_controls():
    # Known-answer codeword from a direct systematic parity calculation.
    data = [0, 1, 2, 3, 4, 5]
    a = sum(data)
    b = sum((i+1)*v for i, v in enumerate(data))
    z = (7*a-b) % 17
    words = data + [(-a-z) % 17, z]
    require(check.repair(words) == words, 'clean parity')
    counts = dict(single_substitution=0, one_erasure=0, two_erasure=0, three_erasure=0)
    for i in range(8):
        for v in range(17):
            if v != words[i]:
                w = words.copy(); w[i] = v
                require(check.repair(w) is None, 'single substitution accepted')
                counts['single_substitution'] += 1
    for n, key in [(1, 'one_erasure'), (2, 'two_erasure'), (3, 'three_erasure')]:
        for positions in itertools.combinations(range(8), n):
            w = words.copy()
            for i in positions:
                w[i] = None
            require(check.repair(w) == (words if n <= 2 else None), key)
            counts[key] += 1
    return counts


def qualify(out):
    out = out.resolve()
    require(not out.exists(), 'output already exists')
    for name, pin in PINS.items():
        require(blob(HERE/name) == pin, 'source blob mismatch: '+name)
    out.mkdir(parents=True)
    for name in (*PINS, 'check_binding.py', 'qualify_binding.py', 'check_binding_browser.cjs', 'index.html', 'README.md'):
        shutil.copyfile(HERE/name, out/name)
    run = out/'bound-v2-output'
    commands = []
    for dest in (run, out/'repeat'):
        p = subprocess.run(['node', str(out/'bound-v2.cjs'), str(dest)],
                           check=True, capture_output=True, text=True)
        require(json.loads(p.stdout)['assertions'] == 45, 'upstream assertions')
        commands.append(p.stdout)
    (out/'generator.log').write_text(commands[0], encoding='utf-8')
    names = sorted(p.name for p in run.iterdir())
    require(len(names) == 12 and names == sorted(p.name for p in (out/'repeat').iterdir()), 'inventory')
    for name in names:
        require((run/name).read_bytes() == (out/'repeat'/name).read_bytes(), 'repeat: '+name)
    require(check.audit(run) == EXPECTED, 'audit counts')
    require(check.audit(out/'repeat') == EXPECTED, 'repeat audit counts')
    shutil.rmtree(out/'repeat')
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp)/'bad'
        def reset():
            if bad.exists(): shutil.rmtree(bad)
            shutil.copytree(run, bad)
        reset(); p = bad/'clean.wav'; b = bytearray(p.read_bytes()); b[-1] ^= 1; p.write_bytes(b)
        reject(lambda: check.audit(bad), 'WAV digest')
        r = json.loads((bad/'receipt.json').read_text())
        next(s for s in r['stimuli'] if s['file']=='clean.wav')['sha256'] = check.digest(p)
        (bad/'receipt.json').write_text(json.dumps(r), encoding='utf-8')
        reject(lambda: check.audit(bad), 'frozen receipt mismatch')
        reset(); (bad/'receipt.json').write_bytes((bad/'receipt.json').read_bytes()+b' ')
        reject(lambda: check.audit(bad), 'frozen receipt mismatch')
        reset(); shutil.copyfile(bad/'clean.wav', bad/'extra.wav')
        reject(lambda: check.audit(bad), 'WAV inventory')
    receipt = {'schema': 'mhac.integration-qualification/1', 'python': sys.version.split()[0],
               'node': subprocess.check_output(['node','--version'], text=True).strip(),
               'source_blobs': PINS, 'generated_files_identical': len(names), 'audit': EXPECTED,
               'parity_controls': parity_controls(), 'negative_controls': 4,
               'browser': 'NOT_RUN', 'physical_audition': 'NOT_RUN'}
    (out/'qualification.json').write_bytes((json.dumps(receipt, sort_keys=True, indent=2)+'\n').encode())
    manifest = {p.relative_to(out).as_posix(): check.digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'manifest.json').write_bytes((json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode())
    return receipt


if __name__ == '__main__':
    print(json.dumps(qualify(Path(sys.argv[1])), sort_keys=True))
