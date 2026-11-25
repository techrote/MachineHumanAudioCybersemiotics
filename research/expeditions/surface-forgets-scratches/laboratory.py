"""Synthetic patina: exact symbolic surface, original audio, no external dependencies."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, sin, pi
from pathlib import Path
import hashlib
import json
import struct
import wave


def trace(word):
    state = Fraction(0)
    out = [state]
    for event in word:
        if event == 'A':
            state += 1
        elif event == 'P':
            state /= 2
        else:
            raise ValueError(event)
        out.append(state)
    return out


def words(a, p):
    for positions in combinations(range(a+p), a):
        s = set(positions)
        yield ''.join('A' if i in s else 'P' for i in range(a+p))


def min_coins(n, p):
    q, r = divmod(n, 2**p)
    return q + r.bit_count()


def predicted(a, p):
    return {n for n in range(a, a*2**p+1) if min_coins(n, p) <= a}


def qualify():
    histories = candidates = families = 0
    for a in range(8):
        for p in range(8):
            observed = Counter()
            for w in words(a, p):
                scaled = trace(w)[-1] * 2**p
                assert scaled.denominator == 1
                observed[int(scaled)] += 1
                histories += 1
            assert sum(observed.values()) == comb(a+p, a)
            assert set(observed) == predicted(a, p)
            assert min(observed) == a and max(observed) == a*2**p
            candidates += a*2**p-a+1
            families += 1
    try:
        trace('X')
    except ValueError:
        pass
    else:
        raise AssertionError('invalid operation accepted')
    assert trace('AP')[-1] != trace('PA')[-1]
    assert trace('AAPPA')[-1] == trace('PAAAP')[-1] == Fraction(3, 2)
    assert trace('AAPPA') != trace('PAAAP')
    return dict(families=families, histories=histories, candidate_endpoints=candidates)


RATE = 16000
SLOT = RATE // 2
PITCH = (196, 247, 294, 220, 330, 262)


def render(states):
    samples = []
    for k, surface in enumerate(states):
        f = PITCH[k % len(PITCH)]
        # Artistic mapping, not a physical abrasion model. Increased relief
        # increases the third and seventh partial; fundamental stays constant.
        relief = float(surface) / (1 + float(surface))
        for i in range(SLOT):
            t = i / RATE
            env = min(1, i/160, (SLOT-1-i)/320)
            s = env * (0.28*sin(2*pi*f*t) + relief*(0.14*sin(2*pi*3*f*t) + 0.09*sin(2*pi*7*f*t)))
            samples.append(round(32767*s))
    assert max(map(abs, samples), default=0) <= 32767
    return struct.pack('<'+'h'*len(samples), *samples)


def write_wav(path, pcm):
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        out.writeframes(pcm)
    with wave.open(str(path), 'rb') as inp:
        assert (inp.getnchannels(), inp.getsampwidth(), inp.getframerate()) == (1, 2, RATE)
        assert inp.getnframes() == len(pcm)//2
        assert inp.readframes(inp.getnframes()) == pcm
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = qualify()
    out = Path(__file__).resolve().parent / 'audio'
    out.mkdir(exist_ok=True)
    a, b = 'AAPPA', 'PAAAP'
    states = {'history-a': trace(a), 'history-b': trace(b),
              'surface-a': [trace(a)[-1]]*6, 'surface-b': [trace(b)[-1]]*6,
              'surface-min': [trace('AAAPP')[-1]]*6,
              'surface-max': [trace('PPAAA')[-1]]*6}
    pcm = {k: render(v) for k,v in states.items()}
    assert pcm['surface-a'] == pcm['surface-b']
    assert pcm['history-a'] != pcm['history-b']
    assert pcm['surface-min'] != pcm['surface-max']
    hashes = {}
    for k, v in states.items():
        assert render(v) == pcm[k]
        hashes[k] = write_wav(out / (k+'.wav'), pcm[k])
    assert hashes['surface-a'] == hashes['surface-b']
    result.update(wavs=len(hashes), frames_per_wav=6*SLOT, rate=RATE, hashes=hashes,
                  collision_histories=[a,b], surface=str(trace(a)[-1]),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    receipt = json.dumps(result, indent=2, sort_keys=True) + '\n'
    (out.parent/'receipt.json').write_text(receipt)
    print(receipt, end='')


if __name__ == '__main__':
    main()
