"""Original synthetic cosine/sine sonification and numerical diameter checks."""
import hashlib
import itertools
import json
import math
import struct
import sys
import wave
from pathlib import Path


def render(values, path):
    # Signed data: sign sets square-wave polarity; no amplitude normalization.
    pcm = [1200 * v * (1 if i % 32 < 16 else -1)
           for v in values for i in range(800)]
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        out.writeframes(struct.pack('<' + 'h' * len(pcm), *pcm))
    raw = path.read_bytes()
    return {'values': values, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def run(folder):
    folder.mkdir(parents=True, exist_ok=True)
    p = list(itertools.combinations(range(4), 2))
    phasors = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    receipt = {'audio': {}, 'nonlinear_diameter_checks': 0, 'sharpness_checks': 0}
    for name, z in [('a', phasors), ('b', [(x, -y) for x, y in phasors])]:
        cos = [z[i][0]*z[j][0]+z[i][1]*z[j][1] for i, j in p]
        sine = z[0][0]*z[1][1]-z[0][1]*z[1][0]
        # Encode signed values as positive distinct pitches' surrogate levels,
        # so the orientation witness is not merely global waveform inversion.
        public = [v+2 for v in cos]
        receipt['audio']['cos-'+name] = render(public, folder/('cos-'+name+'.wav'))
        receipt['audio']['oriented-'+name] = render(public+[sine+2], folder/('oriented-'+name+'.wav'))
    assert receipt['audio']['cos-a']['sha256'] == receipt['audio']['cos-b']['sha256']
    assert receipt['audio']['oriented-a']['sha256'] != receipt['audio']['oriented-b']['sha256']
    # Distinct phase assignments on a path: check sharp arcsin diameter bound.
    for n in range(2, 7):
        for tail in itertools.product(range(8), repeat=n-1):
            a = [0]+list(tail)
            m = max(abs(math.sin((a[i+1]-a[i])*math.pi/4)) for i in range(n-1))
            M = max(abs(math.sin((a[j]-a[i])*math.pi/4)) for i,j in itertools.combinations(range(n), 2))
            bound = math.sin(math.asin(min(1, M))/(n-1))
            assert m+1e-12 >= bound
            receipt['nonlinear_diameter_checks'] += 1
    for D in range(1, 65):
        for M in [0.01, 0.1, 0.5, 0.9, 1.0]:
            e = math.asin(M)/D
            a = [i*e for i in range(D+1)]
            m = max(abs(math.sin(a[i+1]-a[i])) for i in range(D))
            measured = max(abs(math.sin(a[j]-a[i])) for i,j in itertools.combinations(range(D+1), 2))
            assert abs(measured-M)<1e-12 and abs(m-math.sin(e))<1e-12
            receipt['sharpness_checks'] += 1
    return receipt


if __name__ == '__main__':
    output = run(Path(sys.argv[1] if len(sys.argv)>1 else 'results'))
    print(json.dumps(output, indent=2))
