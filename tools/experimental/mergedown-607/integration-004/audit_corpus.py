"""Refs #607. Independent byte/format/inventory audit, not independent PCM decoding."""
import hashlib
import json
import pathlib
import wave

ROOT = pathlib.Path(__file__).resolve().parent
pins = json.loads((ROOT / 'source-pins.json').read_text())['blobs']
pins['test-journal-v42.cjs'] = 'ddd1cfc16ae87049ff8602fe9a8169edb7a12450'
assert {p.name for p in (ROOT / 'source').iterdir()} == set(pins)
for name, sha in pins.items():
    data = (ROOT / 'source' / name).read_bytes()
    assert hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() == sha, name
expected = {71: '994ee9bfc323b049d83bf2c3bd015529b244c755f17dc835649eac951f3d5ded',
            113: '7ee5b3534f354db9b5e7f4ec70b611181e1828a25fe996ada4a3548b557df9fb'}
for seed, digest in expected.items():
    d = ROOT / f'seed{seed}'
    raw = (d / 'receipt.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    r = json.loads(raw)
    assert r['seed'] == seed and r['rate'] == 16000 and len(r['rows']) == 14
    names = [row['file'] for row in r['rows']]
    assert len(set(names)) == 14
    assert {p.name for p in d.iterdir()} == set(names) | {'receipt.json'}
    count = 0
    for row in r['rows']:
        f = d / row['file']
        assert f.is_file() and not f.is_symlink()
        assert hashlib.sha256(f.read_bytes()).hexdigest() == row['sha256'], f
        with wave.open(str(f)) as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, 16000, row['samples'])
        slots = [t['slot'] for t in row['trace'] if 'role' in t]
        assert slots == list(range(len(slots)))
        assert len(slots) * r['step'] == row['samples']
        count += len(slots)
    assert count == r['rescans'] == 32
    print(f'seed {seed}: 14 WAVs, 32 slots, exact receipt digest PASS')
print('25 source blob pins PASS')
