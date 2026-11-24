"""Independent Python cross-check and deterministic audio render, MHAC #230."""
from itertools import combinations
from math import comb, ceil, log2
from functools import lru_cache
from pathlib import Path
import hashlib, json, wave, struct

@lru_cache(None)
def minimax(candidates, n):
    if len(candidates) == 1:
        return 0
    possible = []
    for i in range(n):
        yes = tuple(c for c in candidates if i in c)
        no = tuple(c for c in candidates if i not in c)
        if yes and no:
            possible.append(1 + max(minimax(yes, n), minimax(no, n)))
    return min(possible)

def allocations(n):
    return tuple((0,) + c for c in combinations(range(1, n), n//2 - 1))

def render(owner):
    periods = (32, 28, 24, 20, 16, 14, 12, 10)
    a, b = [], []
    for j, half in enumerate(periods):
        slot = [(3000 * min(i+1, 2400-i, 160)//160) * (-1 if (i//half)%2 else 1) for i in range(2400)] + [0]*800
        a.extend(slot if j in owner else [0]*3200)
        b.extend(slot if j not in owner else [0]*3200)
    return a, b, [x+y for x,y in zip(a,b)]

def write_wav(path, *channels):
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(len(channels)); f.setsampwidth(2); f.setframerate(16000)
        f.writeframes(b''.join(struct.pack('<'+'h'*len(channels),*row) for row in zip(*channels)))

def main():
    root=Path(__file__).parent
    checks=0
    rows=[]
    for n in range(2,17,2):
        candidates=allocations(n)
        assert len(candidates)==comb(n-1,n//2-1); checks+=1
        same=sum(1 in c for c in candidates)
        assert same==(comb(n-2,n//2-2) if n>2 else 0); checks+=1
        if n<=8:
            assert minimax(candidates,n)==n-2; checks+=1
        rows.append(dict(n=n,assignments=len(candidates),localWorst=n-2,arbitraryBinaryLowerBound=ceil(log2(len(candidates))),pairSame=same,pairDifferent=len(candidates)-same))
    p=render((0,1,2,3)); q=render((0,2,4,6)); energy=sum(x*x for x in p[0])
    for c in allocations(8):
        a,b,mix=render(c)
        assert mix==p[2]; checks+=1
        assert sum(x*x for x in a)==sum(x*x for x in b)==energy; checks+=1
    assert p[0]!=q[0]; checks+=1
    files={'mix-grouped.wav':(p[2],),'mix-alternating.wav':(q[2],),'grouped-stereo.wav':p[:2],'alternating-stereo.wav':q[:2],'grouped-solo-A.wav':(p[0],),'alternating-solo-A.wav':(q[0],)}
    hashes={}
    for name,channels in files.items():
        write_wav(root/name,*channels); hashes[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
    assert hashes['mix-grouped.wav']==hashes['mix-alternating.wav']; checks+=1
    assert hashes['grouped-stereo.wav']!=hashes['alternating-stereo.wav']; checks+=1
    result=dict(independent_python_assertions=checks,rows=rows,samples=len(p[2]),energyEach=energy,energyMix=sum(x*x for x in p[2]),sha256=hashes)
    (root/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
