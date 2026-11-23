"""Exact cyclic exclusive-slot minimax solver, using discrepancy bands."""
from math import gcd
from clock import discrepancy


def bounded(q, p, r, da, db):
    """Return a witness satisfying both scaled discrepancy caps, or None.

    Rotate both streams so A has its minimum prefix error at zero. Enumerate
    only B's possible lower band endpoints, which are multiples of gcd(q,r).
    Each layer stores reachable pairs of cumulative counts and predecessors.
    """
    if not (1 <= p <= r and p+r <= q) or min(da,db)<0:
        raise ValueError('invalid density or discrepancy cap')
    if da < q-gcd(q,p) or db < q-gcd(q,r):
        return None
    step = gcd(q,r)
    for low in range(-(db//step)*step, 1, step):
        prev = {(0,0):None}
        history = [prev]
        for t in range(1,q+1):
            layer = {}
            for i,j in prev:
                for x,y in ((0,0),(1,0),(0,1)):
                    u,v=i+x,j+y
                    if not (0<=u<=p and 0<=v<=r and p-u+r-v<=q-t):
                        continue
                    if 0<=q*u-p*t<=da and low<=q*v-r*t<=low+db:
                        layer.setdefault((u,v),(i,j,x,y))
            if not layer:
                break
            history.append(layer)
            prev=layer
        if len(history)==q+1 and (p,r) in history[-1]:
            a,b=[],[]
            u,v=p,r
            for layer in reversed(history[1:]):
                u,v,x,y=layer[u,v]
                a.append(x); b.append(y)
            return tuple(reversed(a)),tuple(reversed(b))
    return None


def minimax(q,p,r):
    """Find exact least max excess, without enumerating binary placements."""
    if not (1<=p<=r and p+r<=q):
        raise ValueError('invalid density')
    base_a,base_b=q-gcd(q,p),q-gcd(q,r)
    # A trivially feasible upper bound: place p A pulses then r B pulses.
    a=(1,)*p+(0,)*(q-p)
    b=(0,)*p+(1,)*r+(0,)*(q-p-r)
    hi=max(discrepancy(a)-base_a,discrepancy(b)-base_b)
    lo=-1
    while hi-lo>1:
        m=(lo+hi)//2
        if bounded(q,p,r,base_a+m,base_b+m) is None:
            lo=m
        else:
            hi=m
    witness=bounded(q,p,r,base_a+hi,base_b+hi)
    assert witness is not None
    return {'max_excess':hi,'words':witness,
            'excesses':(discrepancy(witness[0])-base_a,
                        discrepancy(witness[1])-base_b)}
