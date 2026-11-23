"""Exact finite-population calibration laboratory (fictional, not empirical)."""
from itertools import combinations_with_replacement
from math import lcm
import argparse
import json

def partitions(n):
    """Restricted growth strings: every set partition exactly once."""
    if n < 1:
        raise ValueError("nonempty population required")
    def visit(prefix, next_label):
        if len(prefix) == n:
            yield tuple(prefix)
            return
        for i in range(next_label + 1):
            yield from visit(prefix + [i], max(next_label, i + 1))
    yield from visit([0], 1)

def condition(y, keys):
    """Group conditional expectation; require exact divisibility on the grid."""
    if not y or len(y) != len(keys):
        raise ValueError("nonempty matched rows required")
    groups = {}
    for a, k in zip(y, keys):
        s, n = groups.get(k, (0, 0))
        groups[k] = s + a, n + 1
    if any(s % n for s, n in groups.values()):
        raise ValueError("grid does not represent conditional means")
    return tuple(groups[k][0] // groups[k][1] for k in keys)

def squares(a, b):
    return sum((x-z)**2 for x,z in zip(a,b))

def assess(y, x, z, scale):
    """Two equal-weight calibrated forecasts on identical equally weighted rows.

    All y,x,z values are integer multiples of 1/scale. Returned sums of
    squared errors divide by n*scale**2; var_num divides by n**2*scale**2.
    """
    if not y or len(y)!=len(x) or len(y)!=len(z) or scale<=0:
        raise ValueError("invalid population or scale")
    if any(v not in (0, scale) for v in y) or any(not 0<=v<=scale for v in (*x,*z)):
        raise ValueError("invalid binary outcome or probability")
    if condition(y,x)!=tuple(x) or condition(y,z)!=tuple(z):
        raise ValueError("individual forecasts must be calibrated")
    if any((a+b)%2 for a,b in zip(x,z)):
        raise ValueError("pool off grid")
    p=tuple((a+b)//2 for a,b in zip(x,z))
    q=condition(y,p)
    j=condition(y,tuple(zip(x,z)))
    n=len(y)
    sx,sz,sp=squares(x,y),squares(z,y),squares(p,y)
    d=squares(x,p)
    c=squares(p,q)
    v=n*sum(a*a for a in p)-sum(p)**2
    gain=squares(j,q)
    # Exact integer cross-checks, not floating-point tolerances.
    if 2*sp != sx+sz-2*d or n*d*d > c*v or bool(d)!=bool(c):
        raise AssertionError("calibration or scoring identity violated")
    if squares(p,y)-squares(q,y)!=c or squares(q,y)-squares(j,y)!=gain:
        raise AssertionError("conditional projection identity violated")
    return dict(p=p,q=q,j=j,sx=sx,sz=sz,sp=sp,d=d,c=c,var_num=v,joint_gain=gain)

def census(max_n=6):
    """Unordered partition pairs incl. diagonal, one outcome vector per prevalence.

    Different partitions inducing identical forecasts retain their multiplicity.
    Not a population of independent datasets or uniformly weighted forecasters.
    """
    if not 1 <= max_n <= 6:
        raise ValueError("census budget is 1..6")
    result=[]
    for n in range(1,max_n+1):
        scale=2*lcm(*range(1,n+1))
        ps=list(partitions(n))
        counts=dict(n=n,pairs=0,distinct=0,beats_both=0,strict_bound=0,joint_gain=0)
        for k in range(n+1):
            y=(scale,)*k+(0,)*(n-k)
            forecasts=[condition(y,p) for p in ps]
            for x,z in combinations_with_replacement(forecasts,2):
                a=assess(y,x,z,scale)
                counts["pairs"]+=1
                counts["distinct"]+=bool(a["d"])
                counts["beats_both"]+=a["sp"]<min(a["sx"],a["sz"])
                counts["strict_bound"]+=n*a["d"]**2<a["c"]*a["var_num"]
                counts["joint_gain"]+=bool(a["joint_gain"])
        result.append(counts)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-n",type=int,default=6)
    print(json.dumps(census(p.parse_args().max_n),indent=2))
