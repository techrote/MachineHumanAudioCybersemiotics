"""Exact dyadic FIR column compiler and root-of-unity balance certificate."""
from functools import lru_cache


def divide(a, b):
    """Monic integer polynomial division, ascending coefficients."""
    a = list(a)
    if not b or b[-1] != 1:
        raise ValueError('monic divisor required')
    quo = [0] * max(0, (len(a)-len(b)+1))
    for i in range(len(a)-1, len(b)-2, -1):
        v = a[i]
        k = i-len(b)+1
        quo[k] = v
        for j, t in enumerate(b):
            a[k+j] -= v*t
    return tuple(quo), tuple(a[:len(b)-1])


@lru_cache(None)
def phi(q):
    if type(q) is not int or not 1 <= q <= 256:
        raise ValueError('root order must be 1..256')
    a = (-1,) + (0,)*(q-1) + (1,)
    for d in range(1,q):
        if q%d == 0:
            a, rem = divide(a,phi(d))
            assert not any(rem)
    return a


def stage(a,b,f):
    """Multiply by 2(I-P+zP), P an axis or diagonal projector."""
    if f not in 'AB+-' or len(f)!=1 or len(a)!=len(b):
        raise ValueError('invalid stage or column')
    aa,az,bb,bz=a+(0,),(0,)+a,b+(0,),(0,)+b
    if f=='A': return tuple(2*x for x in az),tuple(2*x for x in bb)
    if f=='B': return tuple(2*x for x in aa),tuple(2*x for x in bz)
    sign=1 if f=='+' else -1
    return (tuple(x+y+sign*(w-v) for x,y,v,w in zip(aa,az,bb,bz)),
            tuple(x+y+sign*(w-v) for x,y,v,w in zip(bb,bz,aa,az)))


def compile_word(word):
    if not isinstance(word,str) or len(word)>128:
        raise ValueError('word must be a string of at most 128 stages')
    a,b=(1,),(0,)
    for f in word: a,b=stage(a,b,f)
    return a,b,2**len(word)


def autocorr(a):
    return tuple(sum(a[i]*a[i+j] for i in range(len(a)-j)) for j in range(len(a)))


def lossless(a,b,den):
    if len(a)!=len(b) or not a or type(den) is not int or den<=0: return False
    return tuple(x+y for x,y in zip(autocorr(a),autocorr(b))) == (den*den,)+(0,)*(len(a)-1)


def balance(a,den,q):
    """Exact remainder of z^D (2|a(z)/den|^2 -1) times den^2."""
    c=[2*x for x in autocorr(a)]; c[0]-=den*den
    return divide(tuple(c[:0:-1]+c),phi(q))[1]


def order_contract(q):
    """Proved bounds; no claim of completeness outside the marked families."""
    degree=len(phi(q))-1
    if q in (1,2): return ('impossible',None,None)
    # Phi_q(1) or Phi_q(-1) > 1 is the odd prime-power obstruction.
    p=phi(q)
    if any(v>1 and v%2 for v in (abs(sum(p)),abs(sum(c*(-1)**i for i,c in enumerate(p))))):
        return ('impossible',None,None)
    lo=(degree+1)//2
    # At exact degree phi/2, leading balance coefficient is at most den^2/2.
    # If Phi_q(1)=1, divisibility would instead require magnitude den^2.
    if sum(p)==1 and degree%2==0: lo+=1
    if q%4==0:
        hi=q//4
        return ('optimal' if lo==hi else 'bounded',lo,hi)
    return ('unresolved',lo,None)


def census(max_depth=8,max_order=60):
    if not 1<=max_depth<=8 or not 1<=max_order<=60: raise ValueError('census cap')
    states={((1,),(0,)):''}; witnesses={}; counts=[]; checks=0
    for d in range(1,max_depth+1):
        ns={}
        for (a,b),w in states.items():
            for f in 'AB+-': ns.setdefault(stage(a,b,f),w+f)
        states=ns
        for (a,b),w in states.items():
            den=2**d
            assert lossless(a,b,den)
            assert (sum(a),sum(b))==(den,0)
            assert sorted(map(abs,(sum(x*(-1)**i for i,x in enumerate(a)),sum(x*(-1)**i for i,x in enumerate(b)))))==[0,den]
            for q in range(1,max_order+1):
                if len(phi(q))>2*d+1: continue
                checks+=1
                if not any(balance(a,den,q)):
                    contract=order_contract(q)
                    assert contract[0]!='impossible' and d>=contract[1]
                    witnesses.setdefault(q,(d,w))
        counts.append(len(states))
    return {'distinct_columns_by_depth':counts,'balance_remainders_checked':checks,'first_witnesses':witnesses}


if __name__=='__main__':
    import json
    for q in range(4,257,4):
        a,b,den=compile_word('+'*(q//4))
        assert lossless(a,b,den) and not any(balance(a,den,q))
    result=census()
    print(json.dumps(result,sort_keys=True,indent=2))
