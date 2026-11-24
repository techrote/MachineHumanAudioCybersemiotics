"""Independent synthetic audio checker, Python 3.11+, standard library."""
import hashlib
import json
import math
import struct
import wave
from pathlib import Path

N, RATE, MASS = 64, 16000, 64
hard = [0 if i < N//2 else MASS for i in range(N)]
ramp = [2*min(i, N-i) for i in range(N)]

def discrepancy(g):
    return [g[i]-g[i-1] for i in range(N)]

def synth(g, x):
    return [(g[i]+g[i-1])*x[i]/(2*MASS) for i in range(N)]

def write(path, a, b):
    frames = bytearray()
    for t in range(2*RATE):
        envelope = min(1, t/320, (2*RATE-1-t)/320)
        frames.extend(struct.pack('<hh', round(16000*envelope*a[t%N]),
                                  round(16000*envelope*b[t%N])))
    with wave.open(str(path), 'wb') as f:
        f.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
        f.writeframes(frames)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(out):
    out.mkdir(parents=True, exist_ok=True)
    dh, dr = discrepancy(hard), discrepancy(ramp)
    assert sum(v*v for v in dh) == 8192
    assert sum(v*v for v in dr) == 256
    assert max(map(abs, dh)) == 64 and max(map(abs, dr)) == 2
    # Each edge contributes two local copies of the signal. Their difference
    # at a shared vertex is exactly (g_i-g_(i-1))*x_i / MASS.
    x = [math.cos(2*math.pi*i/N) for i in range(N)]
    files = {
        'copy-disagreement.wav': write(out/'copy-disagreement.wav',
                                       [v/MASS for v in dh], [v/MASS for v in dr]),
        'mask-playback.wav': write(out/'mask-playback.wav', synth(hard, x), synth(ramp, x)),
    }
    return {'n': N, 'sample_rate': RATE, 'duration_seconds': 2,
            'hard_squared_jump_sum': 8192, 'ramp_squared_jump_sum': 256,
            'hard_peak_jump': 64, 'ramp_peak_jump': 2, 'sha256': files}

if __name__ == '__main__':
    result = run(Path(__file__).parent/'run')
    assert result == run(Path(__file__).parent/'run')
    (Path(__file__).parent/'run'/'audio-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
