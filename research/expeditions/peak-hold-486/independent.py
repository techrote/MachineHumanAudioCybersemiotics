"""Synthetic max-meter oracle and block-envelope audio demonstration (stdlib)."""
import hashlib
import itertools
import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def readings(x, widths):
    n = len(x)
    return tuple(max((x+x)[i:i+w]) for w in widths for i in range(n))


def census():
    rows = []
    for n in range(2, 8):
        signals = list(itertools.product(range(3), repeat=n))
        families = [(w,) for w in range(1, n+1)] + list(itertools.combinations(range(1, n+1), 2))
        classes = 0
        for widths in families:
            groups = {}
            for x in signals:
                groups.setdefault(readings(x, widths), []).append(x)
            classes += len(groups)
            for y, xs in groups.items():
                cap = tuple(map(max, zip(*xs)))
                assert readings(cap, widths) == y
                # The maximal trace must dominate all feasible traces.
                # Independent census of minima by complete enumeration.
                support = lambda x: sum(v != 0 for v in x)
                energy = lambda x: sum(v*v for v in x)
                m = min(map(support, xs))
                e = min(map(energy, xs))
                s = min(map(sum, xs))
                assert any(support(x)==m and energy(x)==e and sum(x)==s for x in xs)
        rows.append(dict(n=n, instances=len(signals)*len(families), classes=classes))
    return rows


def audio():
    # 16 control cells, 100 ms each, repeat three times. The carrier is identical.
    # Compare maxima of cell amplitudes, NOT sliding sample-level waveform maxima.
    dense = (4,)*16
    sparse = tuple(4 if i in (0,5,10,15) else 0 for i in range(16))
    assert readings(dense, (5,8)) == readings(sparse, (5,8))
    assert all(readings(tuple(0 if mask>>i&1 else x for i,x in enumerate(dense)), (5,8)) == readings(dense,(5,8)) for mask in range(1<<16) if mask.bit_count()<=4)
    assert readings((0,)*5+dense[5:], (5,8)) != readings(dense,(5,8))
    rate, block, repeats = 16000, 1600, 3
    path = ROOT/'same-hold-different-excitation.wav'
    data = bytearray()
    for i in range(block*len(dense)*repeats):
        j = (i//block)%16
        carrier = round(2400*math.sin(2*math.pi*440*i/rate))
        data.extend(struct.pack('<hh', dense[j]*carrier, sparse[j]*carrier))
    with wave.open(str(path),'wb') as f:
        f.setparams((2,2,rate,0,'NONE','not compressed'))
        f.writeframes(data)
    pcm = list(struct.iter_unpack('<hh', data))
    energies = [sum(row[c]**2 for row in pcm) for c in (0,1)]
    peaks = [max(abs(row[c]) for row in pcm) for c in (0,1)]
    assert energies[0] == 4*energies[1] and peaks[0]==peaks[1]==9600
    return dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), frames=len(pcm), sample_rate=rate, pcm_energy=energies, pcm_peak=peaks, dense=dense,sparse=sparse, control_widths=[5,8])


if __name__ == '__main__':
    result = dict(byN=census(), audio=audio())
    (ROOT/'independent.synthetic.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
