"""Wrap original native-rendered PCM16 and report basic measurements. Stdlib only."""
import cmath
import math
import struct
import wave
from pathlib import Path

for path in sorted(Path('.').glob('*.pcm')):
    data = path.read_bytes()
    frames = list(struct.iter_unpack('<hh', data))
    with wave.open(str(path.with_suffix('.wav')), 'wb') as out:
        out.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
        out.writeframes(data)
    peak = max(abs(x) for pair in frames for x in pair) / 32767
    rms = math.sqrt(sum(x*x for pair in frames for x in pair)/(2*len(frames)))/32767
    print(f'{path.name} peak={peak:.9g} rms={rms:.9g}', end='')
    if path.name.startswith(('collision-', 'sidon-')):
        segment = frames[4800:48000]
        projection = sum(complex(l, r)*cmath.exp(-2j*math.pi*400*n/48000) for n,(l,r) in enumerate(segment))/(32767*len(segment))
        print(f' 400Hz-IQ={abs(projection):.9g}', end='')
    print()
