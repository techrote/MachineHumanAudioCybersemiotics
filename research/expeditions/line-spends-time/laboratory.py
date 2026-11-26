"""Finite recursive traversal and two clocks; no physical coast or listener model."""
from fractions import Fraction
from pathlib import Path
import hashlib, json, math, platform, struct, sys, wave

SR = 16000
PITCH = {(1, 0): 220, (0, 1): 330, (-1, 0): 165, (0, -1): 275}


def vertices(depth):
    if type(depth) is not int or not 0 <= depth <= 6:
        raise ValueError('depth must be integer in [0,6]')
    pts = [(0, 0), (1, 0)]
    for _ in range(depth):
        result = [(0, 0)]
        for (x, y), (z, w) in zip(pts, pts[1:]):
            dx, dy = z-x, w-y
            for a, b in [(dx, dy), (-dy, dx), (dx, dy), (dy, -dx), (dx, dy)]:
                u, v = result[-1]
                result.append((u+a, v+b))
        pts = result
    return pts


def edges(pts):
    return [(b[0]-a[0], b[1]-a[1]) for a, b in zip(pts, pts[1:])]


def render(depth, clock):
    if clock not in ('duration', 'speed'):
        raise ValueError('unknown clock')
    es = edges(vertices(depth))
    duration = Fraction(2) if clock == 'duration' else 2*Fraction(5,3)**depth
    frames = round(duration*SR)
    out = bytearray()
    for i, direction in enumerate(es):
        start, end = round(Fraction(i*frames,len(es))), round(Fraction((i+1)*frames,len(es)))
        size = end-start
        for j in range(size):
            env = math.sin(math.pi*j/max(1,size-1))**2
            sample = round(0.30*32767*env*math.sin(2*math.pi*PITCH[direction]*j/SR))
            out += struct.pack('<h', sample)
    return bytes(out), frames


def qualify(outdir):
    results = []
    comparisons = 0
    for d in range(7):
        pts = vertices(d)
        es = edges(pts)
        h = sum(abs(x) for x,y in es)
        v = sum(abs(y) for x,y in es)
        assert pts[0] == (0,0) and pts[-1] == (3**d,0)
        assert len(es) == 5**d and all(e in PITCH for e in es)
        assert (h,v) == ((5**d+1)//2,(5**d-1)//2)
        assert Fraction(h+v,3**d) == Fraction(5,3)**d
        if d:
            assert pts[::5] == [(3*x,3*y) for x,y in vertices(d-1)]
        for a,b in [(1,1),(2,1),(1,2),(0,1),(1,0)]:
            measured = sum(a*abs(x)+b*abs(y) for x,y in es)
            assert measured == a*((5**d+1)//2)+b*((5**d-1)//2)
            comparisons += 1
        results.append({'depth':d,'segments':len(es),'horizontal':h,'vertical':v,'length':str(Fraction(h+v,3**d))})
    for d,clock in [(-1,'duration'),(7,'duration'),(1.5,'duration'),(1,'invalid')]:
        try:
            render(d,clock)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid control accepted')
    outdir.mkdir(parents=True,exist_ok=True)
    audio = []
    for d,clock in [(0,'duration'),(1,'duration'),(2,'duration'),(3,'duration'),(3,'speed')]:
        raw,frames = render(d,clock)
        assert (raw,frames) == render(d,clock)
        peak = max(abs(s[0]) for s in struct.iter_unpack('<h',raw))
        assert 0 < peak <= round(.30*32767)
        path = outdir / f'd{d}-{clock}.wav'
        with wave.open(str(path),'wb') as f:
            f.setparams((1,2,SR,frames,'NONE','not compressed'))
            f.writeframes(raw)
        with wave.open(str(path),'rb') as f:
            assert (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes()) == (1,2,SR,frames)
            assert f.readframes(frames) == raw
        audio.append({'file':path.name,'frames':frames,'peak_pcm':peak,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert len({r['sha256'] for r in audio}) == len(audio)
    assert all(r['frames']==2*SR for r in audio[:-1])
    assert audio[-1]['frames']==round(2*Fraction(5,3)**3*SR)
    return {'status':'PASS','python':platform.python_version(),'path_levels':results,'directional_metric_comparisons':comparisons,'rejected_controls':4,'audio':audio,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    out = Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio')
    print(json.dumps(qualify(out),indent=2))
