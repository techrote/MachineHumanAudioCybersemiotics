import sympy as s

x=s.Symbol('x')
phis={q:tuple(map(int,reversed(s.Poly(s.cyclotomic_poly(q,x),x).all_coeffs()))) for q in range(1,61)}
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def stage(a,b,f):
    aa=a+(0,);az=(0,)+a;bb=b+(0,);bz=(0,)+b
    if f==0:return tuple(2*x for x in az),tuple(2*x for x in bb)
    if f==1:return tuple(2*x for x in aa),tuple(2*x for x in bz)
    sign=1 if f==2 else -1
    return add(add(aa,az),tuple(sign*x for x in sub(bz,bb))),add(add(bb,bz),tuple(sign*x for x in sub(az,aa)))
def divisible(a,b):
    a=list(a)
    for i in range(len(a)-1,len(b)-2,-1):
        v=a[i]
        for j,x in enumerate(b):a[i-len(b)+1+j]-=v*x
    return not any(a)
def balance(a,d):
    c=[2*sum(a[i]*a[i+j] for i in range(len(a)-j)) for j in range(len(a))];c[0]-=4**d
    return tuple(c[:0:-1]+c)
states={((1,),(0,)):''}; witnesses={}
for d in range(1,9):
    ns={}
    for (a,b),w in states.items():
        for f in range(4):ns.setdefault(stage(a,b,f),w+str(f))
    states=ns
    for (a,b),w in states.items():
        c=balance(a,d)
        for q,p in phis.items():
            if q not in witnesses and len(p)<=len(c) and divisible(c,p):witnesses[q]=(d,w)
    print(d,len(states),sorted(witnesses.items()),flush=True)
