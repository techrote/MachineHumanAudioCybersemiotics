"""Original miniature scores; not perceptual or participant evidence."""
import hashlib
import json
import math
import struct
import wave
from collections import Counter
from pathlib import Path

RATE = 16000
SLOT = RATE // 4
ROOT = Path(__file__).resolve().parent


def tone(note):
    f = {'A': 220, 'B': 330, '-': 0}[note]
    return [round(8000 * math.sin(2 * math.pi * f * i / RATE)
                  * min(1, i / 160, (SLOT - 1 - i) / 160))
            for i in range(SLOT)]


def render(left, right):
    if len(left) != len(right):
        raise ValueError('channel length mismatch')
    return b''.join(struct.pack('<hh', a, b) for x, y in zip(left, right)
                    for a, b in zip(tone(x), tone(y)))


def main():
    output = ROOT / 'audio'
    output.mkdir(exist_ok=True)
    primary = '--ABABBABBA-'
    local = ['AB', 'BA', 'AB', 'BB'] * 3
    global_ = ['AB', 'BA', 'BB'] * 4
    assert Counter(local) == {'AB': 6, 'BA': 3, 'BB': 3}
    assert Counter(global_) == {'AB': 4, 'BA': 4, 'BB': 4}
    assert all('AA' not in w for w in [primary, *local, *global_])
    l = '-'.join(local)
    g = '-'.join(global_)
    scores = {'silent-rule': (primary, '-' * len(primary)),
              'declared-rule': (primary, 'AA' + '-' * (len(primary) - 2)),
              'local-quota': (l, '-' * len(l)),
              'global-quota': (g, '-' * len(g))}
    receipts = {}
    payloads = {}
    for name, (left, right) in scores.items():
        pcm = render(left, right)
        assert pcm == render(left, right)
        assert max(abs(v[0]) for v in struct.iter_unpack('<h', pcm)) <= 8000
        path = output / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, RATE, len(left) * SLOT)
            assert w.readframes(w.getnframes()) == pcm
        payloads[name] = list(struct.iter_unpack('<hh', pcm))
        receipts[name] = {'left': left, 'right': right, 'frames': len(left) * SLOT,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    a, b = payloads['silent-rule'], payloads['declared-rule']
    assert [x[0] for x in a] == [x[0] for x in b]
    assert not any(x[1] for x in a) and any(x[1] for x in b)
    assert not any(x[1] for x in b[2 * SLOT:])
    assert len({v['sha256'] for v in receipts.values()}) == 4
    result = {'result': 'PASS', 'recordings': receipts,
              'scope': 'Deterministic authored examples; quotas are not random draws.'}
    (ROOT / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
