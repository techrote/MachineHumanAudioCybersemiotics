"""Synthetic full-support signed sequence witnesses; standard library only."""
import hashlib
import itertools
import json
import math
import struct
import wave
from pathlib import Path


def waveform(m, bits):
    out = []
    for n in range(3**m):
        value = 1
        for j in range(m):
            digit = (n // 3**j) % 3
            value *= (1, 2, -1)[digit]
            if digit != 1 and bits & (1 << j):
                value = -value
        out.append(value)
    return out


def autocorrelation(x):
    return [sum(a*b for a, b in zip(x, x[k:])) for k in range(len(x))]


def main():
    target = Path(__file__).resolve().parent / 'results'
    target.mkdir(exist_ok=True)
    rows = []
    for m in range(1, 7):
        reference = waveform(m, 0)
        ac = autocorrelation(reference)
        for bits in range(2**m):
            x = waveform(m, bits)
            assert autocorrelation(x) == ac
            assert list(map(abs, x)) == list(map(abs, reference))
            assert x == waveform(m, (2**m-1)^bits)[::-1]
        rows.append({'depth':m,'members':2**m,'length':3**m,'correlation_cells':2**m*3**m})
    # A non-overlapping integer pulse preserves both magnitude contracts exactly.
    # 2 ms tapered 1000 Hz pulse, 8 kHz; block spacing 2 ms.
    pulse = [round(2200*math.sin(2*math.pi*1000*i/8000)*math.sin(math.pi*i/15)**2) for i in range(16)]
    # Render two 27-tap trains, followed by silence; repeat identical finite block 12 times.
    # Repetition is convolution with a common impulse train and preserves equal spectrum.
    receipts = []
    first_block = None
    first_render = None
    for label,bits in [('a',0),('b',1),('c',2)]:
        x = waveform(3,bits)
        block = [v*p for v in x for p in pulse]
        rendered = (block + [0]*368)*12
        assert max(map(abs, rendered)) < 32768
        if first_block is None:
            first_block = block
            first_render = rendered
        else:
            assert autocorrelation(block) == autocorrelation(first_block)
            assert list(map(abs, rendered)) == list(map(abs, first_render))
            assert rendered != first_render
        path = target / (label+'.wav')
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,8000,0,'NONE','not compressed'))
            f.writeframes(struct.pack('<'+'h'*len(rendered),*rendered))
        receipts.append({'file':path.name,'bits':bits,'samples':len(rendered),'energy':sum(v*v for v in rendered),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    result={'qualification':rows,'audio':receipts,'assertion_failures':0,'audio_note':'Exact per-sample magnitudes for entire PCM; exact aperiodic autocorrelation for 432-sample block checked directly. Common zero-padding and repetition preserve magnitude by convolution.'}
    (target/'witness.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
