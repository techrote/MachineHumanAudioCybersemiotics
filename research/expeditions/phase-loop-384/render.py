"""Independent direct-operator checker and original PCM renderer (stdlib only)."""
import cmath
import hashlib
import json
import math
from pathlib import Path
import struct
import wave


def direct(x, word):
    n = len(x)
    z = cmath.exp(2j * math.pi / n)
    for c in word:
        if c == 'E':
            x = x[-1:] + x[:-1]
        elif c == 'W':
            x = x[1:] + x[:1]
        elif c in 'NS':
            x = [v * z ** (j if c == 'N' else -j) for j, v in enumerate(x)]
        else:
            raise ValueError(c)
    return x


def rectangle(a, b):
    return 'E'*a + 'N'*b + 'W'*a + 'S'*b


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    checks = 0
    err = 0.0
    for n in range(2, 33):
        x = [complex(math.cos(j*0.71), math.sin(j*1.13)) for j in range(n)]
        for a in range(1, 6):
            for b in range(1, 6):
                w = rectangle(a, b)
                for word, area in [(w, a*b), ('N'*b+'E'*a+'S'*b+'W'*a, -a*b)]:
                    y = direct(x, word)
                    expected = cmath.exp(2j*math.pi*area/n)
                    err = max(err, max(abs(v-expected*u) for u,v in zip(x,y)))
                    checks += 1
    assert err < 1e-10
    n, fs = 64, 16000
    x = [0.55*cmath.exp(2j*math.pi*j/n)+0.20*cmath.exp(6j*math.pi*j/n) for j in range(n)]
    cases = [(0, ''), (16, rectangle(4,4)), (32, rectangle(4,8)), (-16, 'N'*4+'E'*4+'S'*4+'W'*4)]
    channels = {name: bytearray() for name in ('phase-reference.wav', 'interference.wav')}
    metrics = []
    for area, word in cases:
        y = direct(x, word)
        energy = sum(abs(v)**2 for v in y)
        assert abs(energy-sum(abs(v)**2 for v in x)) < 1e-10
        residual = max(abs(v+u) for u,v in zip(x,y))
        metrics.append({'area':area,'phase_degrees':area*360/n,'word':word,'complex_energy':energy,'sum_peak':residual})
        for i in range(fs):
            fade = min(1, i/160, (fs-1-i)/160)
            a,b = x[i%n].real,y[i%n].real
            def pcm(v): return round(25000*fade*v)
            channels['phase-reference.wav'].extend(struct.pack('<hh', pcm(a), pcm(b)))
            channels['interference.wav'].extend(struct.pack('<hh', pcm(a), pcm((a+b)/2)))
    assert metrics[2]['sum_peak'] < 1e-10
    hashes = {}
    for name, data in channels.items():
        p = out/name
        with wave.open(str(p),'wb') as f:
            f.setparams((2,2,fs,0,'NONE','not compressed'))
            f.writeframes(data)
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    result = {'direct_operator_checks':checks,'max_absolute_error':err,'cases':metrics,'sha256':hashes}
    (out/'audio-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    print(json.dumps(render(Path(__file__).parent/'run'),indent=2))
