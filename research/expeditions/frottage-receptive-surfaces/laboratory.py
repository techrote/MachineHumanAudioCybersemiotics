"""Synthetic frottage: exact local stencil census and original PCM editions."""
import collections
import hashlib
import itertools
import json
import math
import struct
import sys
import wave
from pathlib import Path

TOOLS = {'point': ((0, 0),), 'horizontal': ((0, 0), (0, 1)),
         'vertical': ((0, 0), (1, 0)),
         'square': ((0, 0), (0, 1), (1, 0), (1, 1))}
RATE = 16000
TILE = 1600


def scan(s, n, tool):
    return tuple(sum(s[((r+dr)%n)*n+(c+dc)%n] for dr, dc in TOOLS[tool])
                 for r in range(n) for c in range(n))


def census(n):
    square, paired, anchored = (collections.Counter() for _ in range(3))
    for s in itertools.product(range(2), repeat=n*n):
        a = scan(s, n, 'square')
        b = scan(s, n, 'horizontal') + scan(s, n, 'vertical')
        square[a] += 1
        paired[b] += 1
        anchored[b+(s[0],)] += 1
    assert len(anchored) == 2**(n*n) and max(anchored.values()) == 1
    assert len(paired) == 2**(n*n) - (n%2 == 0)
    if n%2:
        assert len(square) == 2**(n*n)
    return {name: {'distinct': len(c), 'max_fibre': max(c.values()),
                   'ambiguous_surfaces': sum(v for v in c.values() if v>1)}
            for name,c in [('square',square),('paired',paired),('anchored',anchored)]}


def render(values, area):
    # Identical normalized stencil readings always yield identical tiles.
    out = bytearray()
    for value in values:
        f = 180 + 480*value/area
        for j in range(TILE):
            e = math.sin(math.pi*j/(TILE-1))**2
            a = .46*e*(math.sin(2*math.pi*f*j/RATE)+.28*math.sin(2*math.pi*2.01*f*j/RATE))
            out.extend(struct.pack('<h', round(32767*a)))
    return bytes(out)


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    counts = {str(n): census(n) for n in (2,3,4)}
    n = 8
    # A diagonal ridge / checker modulation pair on a toroidal surface.
    base = tuple(3+int((c-r)%n in (0,1,2)) for r in range(n) for c in range(n))
    other = tuple(x+(-1)**(r+c) for (r,c),x in zip(itertools.product(range(n),repeat=2),base))
    third = tuple(x+(-1)**c for (r,c),x in zip(itertools.product(range(n),repeat=2),base))
    # Values are in [0,6], so divide by area*6 for normalized pitch mapping.
    assert scan(base,n,'square') == scan(other,n,'square') == scan(third,n,'square')
    assert scan(base,n,'horizontal') == scan(other,n,'horizontal') == scan(third,n,'horizontal')
    assert scan(base,n,'vertical') == scan(other,n,'vertical') != scan(third,n,'vertical')
    assert scan(base,n,'point') != scan(other,n,'point')
    editions = [('square-a',base,'square'),('square-b',other,'square'),
                ('vertical-a',base,'vertical'),('vertical-c',third,'vertical'),
                ('point-a',base,'point'),('point-b',other,'point')]
    files = {}
    for name,s,tool in editions:
        values = scan(s,n,tool)
        pcm = render(values,len(TOOLS[tool])*6)
        assert pcm == render(values,len(TOOLS[tool])*6)
        path = out/(name+'.wav')
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,RATE,len(values)*TILE,'NONE','not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (1,2,RATE,len(values)*TILE)
            assert w.readframes(w.getnframes()) == pcm
        peak = max(abs(v[0]) for v in struct.iter_unpack('<h',pcm))
        assert peak < 32767
        files[name] = {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'peak':peak,'values':values}
    assert files['square-a']['sha256'] == files['square-b']['sha256']
    assert files['vertical-a']['sha256'] != files['vertical-c']['sha256']
    assert files['point-a']['sha256'] != files['point-b']['sha256']
    receipt = {'python':sys.version.split()[0], 'binary_surfaces':sum(2**(n*n) for n in (2,3,4)),
               'census':counts,'surfaces':{'a':base,'b':other,'c':third},'files':files}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'binary_surfaces':receipt['binary_surfaces'],'census':counts,'hashes':{k:v['sha256'] for k,v in files.items()}},indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio'))
