"""Synthetic permission-scoped editions; not a privacy or legal compliance system."""
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import struct
import wave


def project(stems, mask):
    return tuple(sum(s[j] for i, s in enumerate(stems) if mask & (1 << i))
                 for j in range(len(stems[0])))


def census():
    histories = tuple(it.product(tuple(it.product((-1, 0, 1), repeat=2)), repeat=3))
    cases = mixed = ambiguous = receipts = 0
    for live, grant in it.product(range(8), repeat=2):
        allowed = live & grant
        n, r = live.bit_count(), allowed.bit_count()
        classes = {}
        for stems in histories:
            public = project(stems, live)
            edition = project(stems, allowed)
            classes.setdefault(public, set()).add(edition)
            # Independently enumerate legal sub-editions; intersection is maximal.
            legal = [m for m in range(8) if (m & live) == m and (m & grant) == m]
            assert allowed in legal and all((m & allowed) == m for m in legal)
            cases += 1
        if 0 < r < n:
            mixed += 1
        for total, observed in classes.items():
            # Independent interval oracle, one coordinate per integer PCM frame.
            ranges = [range(max(-r, t - (n-r)), min(r, t + (n-r)) + 1) for t in total]
            assert observed == set(it.product(*ranges))
            assert (len(observed) > 1) == (0 < r < n and any(abs(t) < n for t in total))
            ambiguous += len(observed) > 1
            receipts += 1
    return dict(stem_histories=len(histories), permission_pairs=64, cases=cases,
                mixed_permission_pairs=mixed, receipt_classes=receipts,
                ambiguous_receipt_classes=ambiguous)


RATE = 16000
FRAMES = 6 * RATE


def motif(events):
    out = [0] * FRAMES
    for start, length, freq, amp in events:
        a, count = round(start * RATE), round(length * RATE)
        for j in range(count):
            t = j / RATE
            e = math.sin(math.pi * j / count) ** 2
            out[a+j] += round(amp * e * (math.sin(2*math.pi*freq*t) + 0.22*math.sin(4*math.pi*freq*t)))
    return tuple(out)


def add(*stems):
    return tuple(map(sum, zip(*stems)))


def write_wav(path, frames):
    assert len(frames) == FRAMES and max(map(abs, frames)) < 32768
    payload = struct.pack('<' + 'h'*len(frames), *frames)
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, RATE, len(frames), 'NONE', 'not compressed'))
        f.writeframes(payload)
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (1, 2, RATE, FRAMES)
        assert f.readframes(FRAMES) == payload
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(root):
    a = motif([(0, 2, 165, 2800), (3, 2.5, 220, 2600)])
    b = motif([(0.5, 1.4, 247, 2400), (3.5, 1.8, 196, 2300)])
    c = motif([(i, 0.5, 82.5, 1600) for i in range(6)])
    crossing = motif([(0.8, 0.6, 440, 3200), (2, 0.8, 523.25, 3000), (4.5, 0.9, 392, 3300)])
    # Same live sum, different provenance and therefore different permitted edition.
    w1, w2 = (add(a, crossing), b, c), (a, add(b, crossing), c)
    live1, live2 = project(w1, 7), project(w2, 7)
    archive1, archive2 = project(w1, 5), project(w2, 5)
    assert live1 == live2 and archive1 != archive2
    assert tuple(x-y for x, y in zip(archive1, archive2)) == crossing
    # Muting the prohibited contribution in a retained dry mix cannot fix provenance.
    assert project(w1, 7) != archive1 and project(w2, 7) != archive2
    root.mkdir(parents=True, exist_ok=True)
    files = {'live-i.wav': live1, 'live-ii.wav': live2,
             'edition-i.wav': archive1, 'edition-ii.wav': archive2}
    hashes = {name: write_wav(root / name, pcm) for name, pcm in files.items()}
    assert hashes['live-i.wav'] == hashes['live-ii.wav'] and len(set(hashes.values())) == 3
    return dict(sample_rate=RATE, frames=FRAMES, channels=1, sha256=hashes,
                peak_abs={name: max(map(abs, pcm)) for name, pcm in files.items()})


if __name__ == '__main__':
    root = Path(__file__).resolve().parent / 'audio'
    receipt = {'synthetic': True, 'census': census(), 'audio': render(root)}
    (root / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
