"""Synthetic calibration witness; no empirical wear or labour model."""
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import wave

LIMIT = 4
DRIFT = (1, 1, 1, 0, 0, 0, -1, 1)
NOTES = (220, 294, 330, 247, 392, 330, 294, 220)
RATE = 16000
FRAMES = 6400


def trace(deltas, policy, limit=LIMIT):
    raw = correction = 0
    rows = []
    for step in deltas:
        raw += step
        before = raw
        previous = correction
        repair = 0
        if policy == 'repair':
            repair = abs(raw)
            raw = 0
        if policy in ('repair', 'compensate'):
            correction = max(-limit, min(limit, -raw))
        elif policy != 'none':
            raise ValueError(policy)
        rows.append(dict(raw=raw, before=before, correction=correction,
                         error=raw+correction, movement=abs(correction-previous),
                         repair=repair, reserve=max(0, limit-abs(raw))))
    return rows


def guaranteed(limit, raw, steps):
    for delta in steps:
        raw += delta
        if abs(raw) > limit:
            return False
    return True


def qualify():
    words = states = 0
    for limit in range(1, 6):
        for raw in range(-limit, limit+1):
            for horizon in range(7):
                safe = True
                for seq in product((-1, 0, 1), repeat=horizon):
                    safe = guaranteed(limit, raw, seq) and safe
                    words += 1
                assert safe == (horizon <= limit-abs(raw))
                states += 1
    assert trace((1,)*5, 'compensate')[-1]['error'] == 1
    assert trace((1,)*5, 'repair')[-1]['error'] == 0
    return dict(horizon_configurations=states, continuations_checked=words)


def pulse(freq, index, duration, gain):
    ramp = min(1.0, index/160, (duration-1-index)/160)
    return round(32767*gain*ramp*math.sin(2*math.pi*freq*index/RATE))


def pcm(rows, audit=False):
    data = bytearray()
    for f, row in zip(NOTES, rows):
        actual = f + 9*row['error']
        for i in range(FRAMES):
            left = pulse(actual, i, FRAMES, .24)
            right = 0
            if audit and i < 1600:
                if row['movement']:
                    right = pulse(880, i, 1600, .12)
                elif row['repair']:
                    right = pulse(440, i, 1600, .12)
            data.extend(struct.pack('<hh', left, right))
    return bytes(data)


def run(folder):
    folder.mkdir(parents=True, exist_ok=True)
    ledger = qualify()
    cases = {
        '01-stable': (trace((0,)*8, 'none'), False),
        '02-compensated': (trace(DRIFT, 'compensate'), False),
        '03-repaired': (trace(DRIFT, 'repair'), False),
        '04-unserviced': (trace(DRIFT, 'none'), False),
        '05-compensation-audit': (trace(DRIFT, 'compensate'), True),
        '06-repair-audit': (trace(DRIFT, 'repair'), True),
    }
    rendered = {name: pcm(rows, audit) for name, (rows, audit) in cases.items()}
    baseline = rendered['01-stable']
    assert baseline == rendered['02-compensated'] == rendered['03-repaired']
    assert baseline != rendered['04-unserviced']
    assert rendered['05-compensation-audit'] != rendered['06-repair-audit']
    left = lambda data: tuple(x[0] for x in struct.iter_unpack('<hh', data))
    assert left(baseline) == left(rendered['05-compensation-audit']) == left(rendered['06-repair-audit'])
    ledger['cases'] = {}
    for name, (rows, audit) in cases.items():
        data = rendered[name]
        assert data == pcm(rows, audit)
        assert max(abs(x[0]) for x in struct.iter_unpack('<h', data)) <= 7865
        path = folder / (name+'.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, len(NOTES)*FRAMES, 'NONE', 'not compressed'))
            w.writeframes(data)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, len(NOTES)*FRAMES)
            assert w.readframes(w.getnframes()) == data
        ledger['cases'][name] = dict(rows=rows, wav_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (folder/'results.json').write_text(json.dumps(ledger, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in ledger.items() if k != 'cases'}))


if __name__ == '__main__':
    run(Path(sys.argv[1] if len(sys.argv)>1 else 'audio'))
