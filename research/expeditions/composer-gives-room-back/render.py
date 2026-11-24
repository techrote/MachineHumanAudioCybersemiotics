"""Original synthetic artwork; no perceptual or alarm validation. Python 3.11+."""
import hashlib, json, math, struct, sys, wave
from pathlib import Path

RATE = 16000
PITCHES = (300, 450, 300, 600, 450, 300, 300, 450, 300, 600, 450, 300)
MODES = ('room', 'in-phase', 'disjoint', 'opposite-phase')

def tone(f):
    return [math.sin(math.tau*f*i/RATE) for i in range(RATE)]

def energy(x):
    return math.fsum(v*v for v in x)/len(x)

def pcm(x):
    assert max(map(abs, x)) < 1
    return struct.pack('<'+'h'*len(x), *(round(v*32767) for v in x))

def render(out):
    out.mkdir(parents=True, exist_ok=True)
    tones = {f:tone(f) for f in {90, 150, 300, 450, 600, 750}}
    bed = [.05*a+.035*b for a,b in zip(tones[90], tones[150])]
    scene = [[], [], [], []]
    rows = []
    for frame, f in enumerate(PITCHES):
        target = [.08*v for v in tones[f]]
        base = [a+b for a,b in zip(bed,target)]
        gain = (frame+1)/6 if frame<6 else 0
        overlays = [[0.0]*RATE, [gain*v for v in target],
                    [.08*gain*v for v in tones[750]], [-gain*v for v in target]]
        powers = [energy(v) for v in overlays]
        assert max(powers[1:])-min(powers[1:]) < 1e-14
        for j, (name, overlay) in enumerate(zip(MODES, overlays)):
            mix = [a+b for a,b in zip(base,overlay)]
            scene[j].append(pcm(mix))
            projection = 2*math.fsum(a*b for a,b in zip(mix,tones[f]))/RATE
            expected = .08*(1+gain) if j==1 else .08*(1-gain) if j==3 else .08
            assert abs(projection-expected) < 1e-12
            if frame==5:
                rows.append(dict(mode=name, overlay_power=round(powers[j],10),
                                 mix_power=round(energy(mix),10), target_bin_amplitude=round(projection,10)))
    assert rows[1]['mix_power'] > rows[2]['mix_power'] > rows[0]['mix_power'] > rows[3]['mix_power']
    assert rows[3]['target_bin_amplitude']==0
    assert all(s[6:]==scene[0][6:] for s in scene)
    hashes = {}
    for name, frames in zip(MODES,scene):
        path = out/(name+'.wav')
        raw = b''.join(frames)
        with wave.open(str(path),'wb') as w:
            w.setparams((1,2,RATE,0,'NONE','not compressed'))
            w.writeframes(raw)
        with wave.open(str(path),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,RATE,12*RATE)
            assert w.readframes(12*RATE)==raw
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(rate=RATE, seconds=12, invariant_suffix_samples=6*RATE,
                  full_gain_frame=rows, sha256=hashes)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    out = Path(sys.argv[1]) if len(sys.argv)>1 else Path('room-back-audio')
    print(json.dumps(render(out),indent=2))
