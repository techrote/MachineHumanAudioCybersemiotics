"""Synthetic cyclic two-voice allocation, exact census and original PCM stems.
Run: python laboratory.py [output-directory]; no external dependencies.
"""
from collections import Counter
from itertools import combinations
from math import comb, pi, sin
from pathlib import Path
import hashlib
import sys
import wave
from array import array


def runs(w):
    starts = [i for i in range(len(w)) if w[i] != w[i-1]]
    out = [[], []]
    for i, start in enumerate(starts):
        length = (starts[(i+1) % len(starts)] - start) % len(w)
        out[w[start]].append(length)
    return out


def bounded_parts(total, r, lo, hi):
    # Ordered positive compositions with bounded parts, independent DP.
    dp = {0: 1}
    for _ in range(r):
        nxt = Counter()
        for s, c in dp.items():
            for a in range(lo, hi+1):
                if s+a <= total:
                    nxt[s+a] += c
        dp = nxt
    return dp.get(total, 0)


def qualify():
    words = cases = 0
    for a in range(1, 8):
        for b in range(1, 8):
            n = a+b
            hist = Counter()
            for pos in combinations(range(n), a):
                w = [1]*n
                for i in pos:
                    w[i] = 0
                x,y = runs(w)
                assert len(x)==len(y) and sum(x)==a and sum(y)==b
                hist[len(x), min(x), max(x), min(y), max(y)] += 1
                words += 1
            for r in range(1,min(a,b)+1):
                count = sum(c for k,c in hist.items() if k[0]==r)
                assert count*r == n*comb(a-1,r-1)*comb(b-1,r-1)
                for la in range(1,a+1):
                    for ua in range(la,a+1):
                        for lb in range(1,b+1):
                            for ub in range(lb,b+1):
                                observed = sum(c for (q,i,j,k,l),c in hist.items() if q==r and la<=i<=j<=ua and lb<=k<=l<=ub)
                                p = bounded_parts(a,r,la,ua)*bounded_parts(b,r,lb,ub)
                                assert observed*r == n*p
                                assert bool(observed)==(r*la<=a<=r*ua and r*lb<=b<=r*ub)
                                cases += 1
    return words,cases


RATE = 16000
SLOT = RATE//4
PITCH = [220, 275, 330, 247, 294, 370, 262, 330, 220, 294, 349, 247]
SCORES = {'alternating':'AB'*6, 'even_pairs':'AABB'*3,
          'uneven_pairs':'ABAAAABBBABB', 'blocks':'AAAAAABBBBBB'}


def pcm(score):
    stems = [array('h'), array('h')]
    for _ in range(3):
        for f, owner in zip(PITCH, score):
            for i in range(SLOT):
                t = i/RATE
                env = min(1, i/160, (SLOT-1-i)/160)
                sample = round(6500*env*(sin(2*pi*f*t)+0.2*sin(4*pi*f*t)))
                for j in range(2):
                    stems[j].append(sample if owner=='AB'[j] else 0)
    mix = array('h', (a+b for a,b in zip(*stems)))
    assert max(map(abs,mix)) <= 7800
    return stems[0],stems[1],mix


def write(path, samples):
    samples = array('h', samples)
    if sys.byteorder != 'little':
        samples.byteswap()
    data = samples.tobytes()
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,RATE,0,'NONE','not compressed'))
        w.writeframes(data)
    with wave.open(str(path),'rb') as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1,2,RATE)
        assert w.readframes(w.getnframes()) == data
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out):
    print('words, bounded cases:', qualify())
    out.mkdir(parents=True,exist_ok=True)
    reference = None
    for name,score in SCORES.items():
        assert len(score)==12 and score.count('A')==6
        x,y = runs(['AB'.index(c) for c in score])
        a,b,mix = pcm(score)
        assert (a,b,mix)==pcm(score)
        if reference is None:
            reference=mix
        assert mix==reference
        print(name, score, 'runs:', x,y, 'mix:',write(out/(name+'-mix.wav'),mix))
        for label,samples in [('A',a),('B',b)]:
            print(name,label,write(out/(name+'-'+label+'.wav'),samples))


if __name__=='__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('audio'))
