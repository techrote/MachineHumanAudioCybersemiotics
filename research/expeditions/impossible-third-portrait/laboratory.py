"""Original digital sound art and exact scalar minimax qualification."""
from itertools import product
from pathlib import Path
import hashlib, math, struct, wave

RATE = 16000
SLOT = 6400


def reconcile(a, b, c):
    # Inputs divisible by three; output is exact signed integer PCM.
    r = c - a - b
    assert r % 3 == 0
    return a + r // 3, b + r // 3


def qualify():
    cases = 0
    for a, b, c in product(range(-12, 13, 3), repeat=3):
        m, s = reconcile(a, b, c)
        e = max(abs(m-a), abs(s-b), abs(m+s-c))
        # Independent integer search, covering the attained witness.
        brute = min(max(abs(x-a), abs(y-b), abs(x+y-c))
                    for x, y in product(range(-24, 25), repeat=2))
        assert e == brute == abs(c-a-b)//3
        assert (m-a, s-b, c-m-s) == ((c-a-b)//3,)*3
        cases += 1
    # A third target can be feasible yet exceed a stereo headroom contract.
    assert reconcile(24000, 24000, 48000) == (24000, 24000)
    assert sum(reconcile(24000, 24000, 48000)) > 32767
    return cases


def phrase(notes, partial):
    result = []
    for n in notes:
        f = 220 * 2**(n/12)
        for i in range(SLOT):
            t = i / RATE
            env = min(1, i/240, (SLOT-1-i)/480)
            v = math.sin(math.tau*f*t) + partial*math.sin(math.tau*2*f*t)
            result.append(3*round(1500*env*v))
    return result


def wav(path, frames, channels):
    flat = [v for frame in frames for v in frame]
    assert max(map(abs, flat)) <= 32767
    pcm = struct.pack('<'+'h'*len(flat), *flat)
    with wave.open(str(path), 'wb') as w:
        w.setparams((channels, 2, RATE, len(frames), 'NONE', 'not compressed'))
        w.writeframes(pcm)
    with wave.open(str(path), 'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (channels, 2, RATE, len(frames))
        assert w.readframes(len(frames)) == pcm
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    a = phrase([0, 4, 7, 9, 7, 4, 2, 0], .15)
    b = phrase([12, 9, 5, 2, 5, 9, 12, 14], .35)
    c = phrase([7, 7, 10, 5, 3, 10, 3, 7], -.25)
    m, s = map(list, zip(*(reconcile(x,y,z) for x,y,z in zip(a,b,c))))
    l = [x+y for x,y in zip(m,s)]
    r = [x-y for x,y in zip(m,s)]
    for x,y,z,u,v,w,q in zip(a,b,c,m,s,l,r):
        assert (w+q, w-q) == (2*u, 2*v)
        assert max(abs(u-x),abs(v-y),abs(w-z)) == abs(z-x-y)//3
    tracks = {'target-mid': a, 'target-side': b, 'target-left': c,
              'priority-left': [x+y for x,y in zip(a,b)],
              'compromise-mid': m, 'compromise-side': s, 'compromise-left': l}
    files = {name: ([(x,) for x in xs], 1) for name,xs in tracks.items()}
    files['priority-stereo'] = (list(zip(tracks['priority-left'], [x-y for x,y in zip(a,b)])), 2)
    files['compromise-stereo'] = (list(zip(l,r)), 2)
    hashes = {name: wav(out/(name+'.wav'), frames, ch) for name,(frames,ch) in files.items()}
    assert hashes == {name: wav(out/(name+'.wav'), frames, ch) for name,(frames,ch) in files.items()}
    print('frames:',len(a),'max residual:',max(abs(z-x-y) for x,y,z in zip(a,b,c)))
    for name,h in hashes.items():
        print(name, h)


if __name__ == '__main__':
    print('Exact scalar cases:', qualify())
    render(Path(__file__).resolve().parent/'audio')
