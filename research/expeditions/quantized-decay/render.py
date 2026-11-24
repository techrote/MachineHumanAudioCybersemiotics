"""Independent integer oracle and synthetic stereo render; Python standard library."""
import heapq
import hashlib
import json
import math
import struct
import sys
import wave
from pathlib import Path


def step(s, a, b, q, mode='N'):
    def quantize(n):
        i, rem = divmod(abs(n), q)
        return (1 if n >= 0 else -1) * (i + (mode == 'N' and 2*rem >= q))
    x, y = s
    return quantize(a*x-b*y), quantize(b*x+a*y)


def oracle(a, b, q):
    # Tuple-weight Dijkstra, rather than scalar encoded cost.
    delta = q*q-a*a-b*b
    R = (3*q*q+2*delta-1)//(2*delta)
    S = [(x,y) for x in range(-R,R+1) for y in range(-R,R+1) if x*x+y*y <= R*R]
    rev = {s: [] for s in S}
    for s in S:
        for mode in 'NT':
            rev[step(s,a,b,q,mode)].append((s, int(mode=='T')))
    d = {(0,0):(0,0)}
    heap = [((0,0),(0,0))]
    while heap:
        cost, s = heapq.heappop(heap)
        if cost != d[s]:
            continue
        for v, k in rev[s]:
            z = (cost[0]+k,cost[1]+1)
            if z < d.get(v,(math.inf,math.inf)):
                d[v]=z
                heapq.heappush(heap,(z,v))
    assert len(d)==len(S)
    return d


def trajectory(start,a,b,q,policy,d=None):
    s=start
    path=[s]
    actions=[]
    seen=set()
    while s!=(0,0) and s not in seen:
        seen.add(s)
        n,t=step(s,a,b,q),step(s,a,b,q,'T')
        if policy=='optimal':
            mode='N' if d[s]==(d[n][0],d[n][1]+1) else 'T'
        elif policy=='greedy':
            mode='N' if sum(v*v for v in n)<sum(v*v for v in s) else 'T'
        else:
            mode='N'
        s=n if mode=='N' else t
        path.append(s)
        actions.append(mode)
    return path,actions


def write_wav(path, frames, rate):
    with wave.open(str(path),'wb') as f:
        f.setparams((2,2,rate,0,'NONE','not compressed'))
        f.writeframes(b''.join(struct.pack('<hh',l,r) for l,r in frames))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out):
    out.mkdir(parents=True,exist_ok=True)
    d=oracle(8,4,9)
    start=(-16,4)
    cycle,_=trajectory(start,8,4,9,'nominal')
    repair,actions=trajectory(start,8,4,9,'optimal',d)
    assert cycle[-1]==start and len(cycle)==69 and repair[-1]==(0,0)
    assert d[start]==(actions.count('T'),len(actions))
    # Direct state samples: hold each integer x coordinate for two PCM samples.
    # The unmodified orbit repeats for 100 complete cycles before repair starts.
    frames=[]
    switch=6800
    for i in range(20400):
        l=cycle[i%68][0]
        r=l if i<switch else repair[min(i-switch,len(repair)-1)][0]
        frames.extend([(l*900,r*900)]*2)
    h1=write_wav(out/'persistent-orbit.wav',frames,16000)
    d2=oracle(4,8,9)
    p1,a1=trajectory((-81,12),4,8,9,'optimal',d2)
    p2,a2=trajectory((-81,12),4,8,9,'greedy')
    assert d2[(-81,12)]==(9,len(a1)) and a2.count('T')==48
    # Artistic mapping: radius -> amplitude of 400 Hz triangle-wave carrier.
    # 20 ms per state; both channels share the same scale, no normalization per path.
    frames=[]
    for i in range(max(len(p1),len(p2))+20):
        amps=[math.isqrt(sum(v*v for v in p[min(i,len(p)-1)])) for p in (p1,p2)]
        for j in range(320):
            carrier=20-abs((j%40)-20)*2
            frames.append(tuple(carrier*a*14 for a in amps))
    h2=write_wav(out/'intervention-debt.wav',frames,16000)
    # Independent quarter-turn construction checks, including q outside JS cap.
    checks=0
    for q in range(2,65):
        m=q//2
        for x in range(-m,m+1):
            for y in range(-m,m+1):
                n=step((x,y),0,q-1,q)
                t=step((x,y),0,q-1,q,'T')
                assert n==(-y,x)
                assert max(map(abs,t))==max(0,max(abs(x),abs(y))-1)
                checks+=1
    data={'quarter_turn_state_checks':checks,'orbit_period':68,'orbit_optimal':d[start],
          'switch_update':switch,'orbit_wav_sha256':h1,'greedy_gap':{'optimal_cost':a1.count('T'),'optimal_steps':len(a1),'greedy_cost':a2.count('T'),'greedy_steps':len(a2)},'debt_wav_sha256':h2}
    (out/'audio-manifest.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))


if __name__=='__main__':
    main(Path(sys.argv[1] if len(sys.argv)>1 else 'run'))
