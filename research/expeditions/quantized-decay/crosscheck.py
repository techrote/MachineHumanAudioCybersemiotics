"""Independent Python census using tuple shortest paths and per-orbit memoization."""
from collections import Counter
import json
from render import oracle, step


def census():
    out=Counter()
    periods=Counter()
    for q in range(2,11):
        for a in range(q):
            for b in range(q):
                if a*a+b*b>=q*q:
                    continue
                d=oracle(a,b,q)
                nxt={s:step(s,a,b,q) for s in d}
                zero=(0,0)
                basins={zero:False}
                found=0
                for root in d:
                    path=[]
                    index={}
                    s=root
                    while s not in basins and s not in index:
                        index[s]=len(path)
                        path.append(s)
                        s=nxt[s]
                    if s in index:
                        periods[len(path)-index[s]]+=1
                        found+=1
                        persistent=True
                    else:
                        persistent=basins[s]
                    for v in path:
                        basins[v]=persistent
                g={zero:0}
                for s in sorted(d,key=lambda z:z[0]**2+z[1]**2):
                    if s==zero:continue
                    n=nxt[s]
                    if n[0]**2+n[1]**2<s[0]**2+s[1]**2:
                        g[s]=g[n]
                    else:
                        g[s]=1+g[step(s,a,b,q,'T')]
                out.update(models=1,states=len(d),modelsWithNonzeroCycle=int(found>0),nonzeroCycles=found,persistentBasinStates=sum(basins.values()),greedyWorseStates=sum(g[s]>d[s][0] for s in d))
                out['maxInterventions']=max(out['maxInterventions'],max(x[0] for x in d.values()))
                out['maxGreedyExcess']=max(out['maxGreedyExcess'],max(g[s]-d[s][0] for s in d))
    out['maxPeriod']=max(periods)
    return {**out,'periodHistogram':dict(sorted(periods.items()))}


if __name__=='__main__':
    print(json.dumps(census(),indent=2))
