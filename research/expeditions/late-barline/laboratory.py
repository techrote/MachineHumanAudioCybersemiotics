"""Synthetic annotation model and original offline score; Python 3.11+, stdlib."""
from itertools import product
from math import gcd, lcm, sin, pi, exp
from pathlib import Path
import hashlib
import json
import struct
import wave


def grid(p, phase, n):
    return tuple(int(i % p == phase) for i in range(n))


def verify():
    grids = 0
    for p, q in product(range(2, 10), repeat=2):
        L = lcm(p, q)
        for a, b in product(range(p), range(q)):
            observed = sum(x != y for x, y in zip(grid(p, a, L), grid(q, b, L)))
            expected = L//p + L//q - 2*int((a-b) % gcd(p,q) == 0)
            assert observed == expected
            grids += 1
    # On D contested positions, 0 means support hypothesis A, 1 supports B,
    # 2 defers. Exhaust all ternary assignments, not just balanced ones.
    assignments = 0
    for d in range(10):
        best = [d+1]*(d+1)
        for word in product(range(3), repeat=d):
            z = word.count(2)
            best[z] = min(best[z], max(word.count(0), word.count(1)))
            assignments += 1
        assert best == [(d-b+1)//2 for b in range(d+1)]
    assert sum(x != y for x,y in zip(grid(3,0,24),grid(4,0,24))) == 10
    return {"phase_pairs": grids, "ternary_assignments": assignments}


RATE, PULSE, PREFIX, TOTAL = 16000, 4000, 24, 48


def render(mode):
    if mode not in ("three", "four", "unresolved", "double"):
        raise ValueError(mode)
    out = bytearray()
    for i in range(TOTAL):
        for j in range(PULSE):
            t = j/RATE
            env = min(1, j/80, (PULSE-1-j)/160)*exp(-15*t)
            left = env*(.23*sin(2*pi*330*t) + (.17 if i%4==0 else .035)*sin(2*pi*660*t))
            right = 0.
            if i >= PREFIX:
                if mode in ("three", "double") and i%3==0:
                    right += .28*env*sin(2*pi*110*t)
                if mode in ("four", "double") and i%4==0:
                    right += .28*env*sin(2*pi*146.83*t)
            assert max(abs(left), abs(right)) <= 1
            out.extend(struct.pack('<hh', round(32767*left), round(32767*right)))
    return bytes(out)


def main():
    receipt = verify()
    directory = Path(__file__).resolve().parent/'audio'
    directory.mkdir(exist_ok=True)
    payloads, hashes = {}, {}
    for mode in ("three", "four", "unresolved", "double"):
        pcm = render(mode)
        assert pcm == render(mode)
        path = directory/(mode+'.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (2,2,RATE,TOTAL*PULSE)
            assert w.readframes(w.getnframes()) == pcm
        payloads[mode] = pcm
        hashes[mode] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert len({v[:PREFIX*PULSE*4] for v in payloads.values()}) == 1
    assert len({b''.join(v[i:i+2] for i in range(0,len(v),4)) for v in payloads.values()}) == 1
    assert len(set(payloads.values())) == 4
    assert not any(payloads['unresolved'][i] for i in range(2,len(payloads['unresolved']),4))
    try:
        render('invalid')
    except ValueError:
        pass
    else:
        raise AssertionError('invalid mode accepted')
    receipt.update({"status":"PASS", "frames_per_wav":TOTAL*PULSE,"sample_rate":RATE,"prefix_frames":PREFIX*PULSE,"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"wav_sha256":hashes})
    (directory.parent/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
