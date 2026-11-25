"""Original synthetic circular scores; no listener or clinical data."""
import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import struct
import wave


def score(lengths):
    return [bit for length in lengths for bit in [1]*length+[0]*4]


def gate(bits, h):
    age = 0
    out = []
    for bit in bits:
        age = age+1 if bit else 0
        out.append(int(age > h))
    return out


def histogram(bits, w):
    return Counter(tuple(bits[(i+j)%len(bits)] for j in range(w))
                   for i in range(len(bits)))


def render(bits, path):
    rate, frames = 8000, 320
    pulse = [round(6000*math.sin(2*math.pi*250*j/rate)*
                   math.sin(math.pi*j/(frames-1))**2) for j in range(frames)]
    pcm = [x for bit in bits for x in (pulse if bit else [0]*frames)]
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, rate, len(pcm), 'NONE', 'not compressed'))
        f.writeframes(struct.pack('<'+'h'*len(pcm), *pcm))
    return {'frames': len(pcm), 'sum_squares': sum(x*x for x in pcm),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    a, b = score([5]*20), score([4]*19+[24])
    assert all(histogram(a, w) == histogram(b, w) for w in range(1, 6))
    assert histogram(a, 6) != histogram(b, 6)
    ga, gb = gate(a, 4), gate(b, 4)
    stats = {}
    for name, seq in [('raw-a', a), ('raw-b', b), ('gated-a', ga), ('gated-b', gb)]:
        stats[name] = {'slots': len(seq), 'active': sum(seq),
                       'episodes': sum(v and not seq[i-1] for i, v in enumerate(seq)),
                       **render(seq, out/(name+'.wav'))}
    assert stats['raw-a']['sum_squares'] == stats['raw-b']['sum_squares']
    assert stats['gated-a']['sum_squares'] == stats['gated-b']['sum_squares']
    assert [stats[k]['episodes'] for k in ['gated-a','gated-b']] == [20,1]
    # Exact boundary-family calculation over different horizons and caps.
    checks = 0
    for h in range(1, 17):
        for M in range(h+1, h+65):
            p = Fraction(1, M-h)
            assert (1-p)*h+p*M == h+1
            assert p*(M-h) == 1
            assert p*(M-h+1)*(M-h)/2 == Fraction(M-h+1, 2)
            checks += 1
    result = {'score': stats, 'boundary_family_checks': checks,
              'equal_histograms_through': 5, 'assertions': 'passed'}
    (out/'witness.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('build'))
    main(parser.parse_args().out)
