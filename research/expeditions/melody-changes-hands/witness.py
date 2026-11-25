"""Literal permutation and PCM witnesses for MHAC 530. Standard library."""
import itertools as it
import math, hashlib, json, struct, wave
from pathlib import Path


def census():
    result=[]
    for n in (2,3,4):
        grids=list(it.combinations(range(6),n)); perms=list(it.permutations(range(n)))
        cases=feasible=assignments=checks=0; gap=None
        for x in grids:
            for y in grids:
                for v in range(4):
                    cases+=1
                    p=[a for a in perms if all(abs(x[i]-y[a[i]])<=v for i in range(n))]
                    identity=tuple(range(n))
                    assert bool(p)==(identity in p)
                    if not p: continue
                    feasible+=1; assignments+=len(p)
                    # Directly compare all feasible assignments for every anchor mask.
                    universal_edges=set(); sorted_edges=set()
                    for a,b in it.combinations(p,2):
                        changed=tuple(i for i in range(n) if a[i]!=b[i])
                        if len(changed)==2:
                            universal_edges.add(changed)
                            if a==identity or b==identity: sorted_edges.add(changed)
                    sorted_min=universal_min=n
                    for mask in range(1<<n):
                        selected=[i for i in range(n) if mask>>i&1]
                        receipts=[tuple(a[i] for i in selected) for a in p]
                        unique=len(set(receipts))==len(p)
                        cert=receipts.count(tuple(selected))==1
                        assert unique==all(any(mask>>i&1 for i in e) for e in universal_edges)
                        assert cert==all(any(mask>>i&1 for i in e) for e in sorted_edges)
                        if unique: universal_min=min(universal_min,len(selected))
                        if cert: sorted_min=min(sorted_min,len(selected))
                        checks+=2
                    if gap is None and universal_min>sorted_min:
                        gap=dict(x=x,y=y,v=v,sorted_min=sorted_min,universal_min=universal_min)
                    # Weighted symbol distance, including zero copies.
                    weights=tuple((i+v)%3 for i in range(n))
                    if len(p)>1:
                        actual=min(sum(weights[i] for i in range(n) if a[i]!=b[i]) for a,b in it.combinations(p,2))
                        predicted=min(sum(weights[i] for i in e) for e in universal_edges)
                        assert actual==predicted
                        checks+=1
        result.append(dict(n=n,cases=cases,feasible=feasible,assignments=assignments,checks=checks,first_gap=gap))
    return result


def audio(output):
    rate=8000; n=rate; split=n//2
    # Phases in cycles. At t=1/2 both are integral and differ by 50 cycles.
    def tone(i, descending):
        t=i/rate
        phase=(600*t-100*t*t) if descending else (400*t+100*t*t)
        env=math.sin(math.pi*i/(n-1))**2
        return round(10000*env*math.sin(2*math.pi*phase))
    low=[tone(i,False) for i in range(n)]; high=[tone(i,True) for i in range(n)]
    cross=list(zip(low,high)); bounce=[(a,b) if i<split else (b,a) for i,(a,b) in enumerate(cross)]
    assert cross!=bounce
    def render(name, data, channels):
        path=output/(name+'.wav')
        flat=[sample for frame in data for sample in frame]
        with wave.open(str(path),'wb') as f:
            f.setparams((channels,2,rate,0,'NONE','not compressed'))
            f.writeframes(struct.pack('<'+'h'*len(flat),*flat))
        return hashlib.sha256(path.read_bytes()).hexdigest()
    hashes={}
    for name,data in [('cross',cross),('bounce',bounce)]:
        hashes[name+'-stereo']=render(name+'-stereo',data,2)
        hashes[name+'-mono']=render(name+'-mono',[(a+b,) for a,b in data],1)
    assert hashes['cross-mono']==hashes['bounce-mono']
    assert hashes['cross-stereo']!=hashes['bounce-stereo']
    return dict(rate=rate,frames=n,splice=split,sha256=hashes)

if __name__=='__main__':
    output=Path(__file__).resolve().parent/'results';output.mkdir(exist_ok=True)
    print(json.dumps(dict(profiles=census(),audio=audio(output),status='pass'),indent=2))
