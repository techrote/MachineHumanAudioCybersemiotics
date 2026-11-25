"""Independent direct-cell oracle and original pulse sonification (Python 3.11+)."""
import hashlib
import json
import math
import struct
import wave
from pathlib import Path


def evolve(x, n, t):
    a = [(x >> i) & 1 for i in range(n)]
    for _ in range(t):
        a = [v ^ a[i - 1] for i, v in enumerate(a)]
    return sum(v << i for i, v in enumerate(a))


def census():
    counts = dict(rings=0, kernel_states=0, transition_comparisons=0,
                  pilot_masks=0, budget_contracts=0, decodes=0,
                  impossible=0, odd_surcharge=0)
    for n in range(1, 13):
        for t in range((n & -n) + 2):
            ker = [x for x in range(1, 1 << n) if evolve(x, n, t) == 0]
            counts['rings'] += 1
            counts['kernel_states'] += len(ker)
            counts['transition_comparisons'] += 1 << n  # includes zero
            counts['pilot_masks'] += 1 << n
            best = [n + 1] * (n + 2)
            for mask in range(1 << n):
                dist = min(((mask & k).bit_count() for k in ker), default=n + 1)
                best[dist] = min(best[dist], mask.bit_count())
            for i in range(n, -1, -1):
                best[i] = min(best[i], best[i + 1])
            d = (len(ker) + 1).bit_length() - 1
            p = 1 << max(0, d.bit_length() - 1)
            for e in range(n + 1):
                counts['budget_contracts'] += 1
                r = e + 1
                expected = 0 if not d else d if r == 1 else r*p
                if d and r > 1 and d != p and r % 2:
                    b = 1 << (2*p-d-1).bit_length()
                    expected += p-b
                if d and r > n//p:
                    assert best[r] == n+1
                    counts['impossible'] += 1
                else:
                    assert best[r] == expected, (n,t,e,best[r],expected)
                    counts['decodes'] += 1  # feasible contracts, not decoder execution
                    counts['odd_surcharge'] += int(bool(d and e and expected > r*p))
    counts['feasible_contracts'] = counts.pop('decodes')
    return counts


def sound(path, stages, tick=.09, rate=16000):
    frames = []
    k = int(rate*tick)
    for left, right, n in stages:
        for i in range(n):
            for j in range(k):
                # Smooth, zero-at-both-ends pulse, common gain on both channels.
                z = round(10500 * math.sin(math.pi*j/(k-1))**2 * math.sin(2*math.pi*440*j/rate))
                frames.append((z*((left>>i)&1), z*((right>>i)&1)))
    raw = b''.join(struct.pack('<hh', *f) for f in frames)
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, rate, len(frames), 'NONE', 'not compressed'))
        f.writeframes(raw)
    return dict(frames=len(frames), rate=rate, peak=max(abs(v) for f in frames for v in f),
                unequal_frames=sum(a!=b for a,b in frames), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    out=Path(__file__).resolve().parent
    x, y = 0x96, 0x96 ^ 0x33
    stages = [(evolve(x,8,t),evolve(y,8,t),8) for t in range(4)]
    assert stages[-1][0] == stages[-1][1] and x != y
    six, seven = 0xcf, 0xef  # six pilots omit bits 4,5; seven omit bit 4
    ker = [k for k in range(1,256) if evolve(k,8,3)==0]
    assert min((six&k).bit_count() for k in ker)==2
    assert min((seven&k).bit_count() for k in ker)==3
    # N=16 vs N=17, identical first 16 cells; right has one extra zero.
    widths = [(evolve(1,16,t),evolve(1,17,t),17) for t in range(17)]
    assert widths[-1][0] == 0 and widths[-1][1] != 0
    receipt = {'classification':'synthetic only','census':census(),
               'example':{'stage_words':stages,'six_pilot_mask':six,'seven_pilot_mask':seven},
               'width_final_words': widths[-1][:2],
               'audio':{'shared-future.wav':sound(out/'shared-future.wav',stages),
                        'one-extra-cell.wav':sound(out/'one-extra-cell.wav',widths,.035)}}
    (out/'independent.synthetic.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
