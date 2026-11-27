"""Synthetic fixed-sum mixer frontier and original offline sound study."""
from itertools import product
from pathlib import Path
from collections import defaultdict
import hashlib, json, math, struct, wave, sys


def extrema(n, q, s):
    a, r = divmod(s, n)
    low = (n-r)*a*a + r*(a+1)**2
    k, rem = divmod(s+n*q, 2*q)
    high = n*q*q if rem == 0 else (n-1)*q*q + (rem-q)**2
    return low, high


def census():
    total = classes = holes = 0
    for n in range(2, 7):
        for q in range(1, 4):
            groups = defaultdict(set)
            for x in product(range(-q, q+1), repeat=n):
                groups[sum(x)].add(sum(v*v for v in x))
                total += 1
            assert len(groups) == 2*n*q+1
            for s, energies in groups.items():
                low, high = extrema(n, q, s)
                assert (min(energies), max(energies)) == (low, high)
                assert all((e-s)%2 == 0 for e in energies)
                holes += len(set(range(low, high+1, 2))-energies)
                classes += 1
    assert extrema(2, 2, 0) == (0, 8)
    assert {sum(v*v for v in x) for x in product(range(-2,3),repeat=2) if sum(x)==0} == {0,2,8}
    return dict(vectors=total, sum_classes=classes, parity_compatible_holes=holes)


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    rate, length = 16000, 4000
    configs = {'frugal':(0,0,1,1), 'ornate':(-1,1,1,1), 'extravagant':(-2,0,2,2)}
    results, masters = {}, []
    def save(name, channels):
        frames = list(zip(*channels))
        assert all(-32768 <= x <= 32767 for f in frames for x in f)
        pcm = struct.pack('<'+'h'*(len(frames)*len(channels)),*(x for f in frames for x in f))
        p = out/(name+'.wav')
        with wave.open(str(p),'wb') as w:
            w.setparams((len(channels),2,rate,0,'NONE','not compressed'))
            w.writeframes(pcm)
        with wave.open(str(p),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()) == (len(channels),2,rate,len(frames))
            assert w.readframes(len(frames)) == pcm
        results[name] = dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),frames=len(frames),channels=len(channels))
    for name, gains in configs.items():
        stems = [[] for _ in range(4)]
        for j, hz in enumerate([196,247,294,330,392,330,247,196,220,277,330,220,196,294,247,196]):
            tile = [round(3200*math.sin(2*math.pi*hz*i/rate)*math.sin(math.pi*i/(length-1))**2) for i in range(length)]
            for i in range(4):
                stems[i].extend(gains[(i+j)%4]*v for v in tile)
        master = [sum(f) for f in zip(*stems)]
        masters.append(master)
        assert sum(sum(x*x for x in st) for st in stems)*4 == sum(x*x for x in master)*sum(g*g for g in gains)
        save(name+'-master',[master])
        save(name+'-stems',stems)
        # A separately composed monitor: solo one stem on right, master on left.
        save(name+'-monitor',[master,stems[0]])
    assert masters[0]==masters[1]==masters[2]
    assert len({results[n+'-master']['sha256'] for n in configs})==1
    assert len({results[n+'-monitor']['sha256'] for n in configs})==3
    return results


def main():
    out = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'audio'
    receipt = dict(scope='synthetic only',census=census(),audio=render(out))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':
    main()
