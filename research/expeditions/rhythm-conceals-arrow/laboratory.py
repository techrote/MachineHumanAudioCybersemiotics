"""Exact symbolic reversal experiments; floating point only for entropy/KL.
Run: python3 laboratory.py --out DIRECTORY
No dependencies, participants, or empirical inputs.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb, log2
from pathlib import Path
import struct
import wave
from io import BytesIO


def words(n):
    return map(''.join, product('01', repeat=n))


def counts(s, n):
    return Counter(''.join(s[(i+j) % len(s)] for j in range(n))
                   for i in range(len(s)))


def tv(c):
    return Fraction(sum(abs(c[w]-c[w[::-1]]) for w in c.keys() | {w[::-1] for w in c}),
                    2*sum(c.values()))


def h(p):
    return -sum(t*log2(t) for t in (p, 1-p) if t)


def block(k, theta, n):
    # Integer numerators, denominator 2**k * 4**(n-k) for n>=k.
    if n < k:
        return Counter({w: 1 for w in words(n)})
    ans = Counter()
    for w in words(n):
        v = 1
        for i in range(n-k):
            t = theta[w[i+1:i+k]]
            v *= t if w[i] == w[i+k] else 4-t
        ans[w] = v
    return ans


def entropy_rate(theta):
    return sum(h(t/4) for t in theta.values())/len(theta)


def kl(c):
    return sum(v*log2(v/c[w[::-1]]) for w, v in c.items() if v)/sum(c.values())


def alpha(k):
    return 1-Fraction(1, 2**((k-1)//2))


def cyclic_census():
    result = []
    for n in range(1, 13):
        best = Fraction(0)
        witness = None
        nonzero = 0
        for s in words(n):
            assert all(tv(counts(s, j)) == 0 for j in (1, 2, 3))
            c = counts(s, 4)
            delta = c['0010']-c['0100']
            assert c['0101']-c['1010'] == delta
            assert c['1100']-c['0011'] == delta
            assert c['1011']-c['1101'] == delta
            assert tv(c) == Fraction(4*abs(delta), n) <= Fraction(2, 3)
            nonzero += bool(delta)
            if tv(c) > best:
                best, witness = tv(c), s
        assert best == Fraction(4*(n//6), n)
        result.append(dict(period=n, words=2**n, irreversible_at_4=nonzero,
                           max_tv=str(best), witness=witness))
    assert tv(counts('001011', 4)) == Fraction(2, 3)
    for n in range(6, 201):
        s = '0'*(n%6) + '001011'*(n//6)
        assert tv(counts(s,4)) == Fraction(4*(n//6),n)
    return result


def grid_census():
    result = []
    for k in range(1, 5):
        ctx = list(words(k-1))
        for levels in ((0, 2, 4), (1, 2, 3)):
            best = Fraction(0)
            rev = 0
            for values in product(levels, repeat=len(ctx)):
                theta = dict(zip(ctx, values))
                c = block(k, theta, k+1)
                # Both marginals independently uniform.
                for w in words(k):
                    assert c[w+'0']+c[w+'1'] == 4
                    assert c['0'+w]+c['1'+w] == 4
                d = tv(c)
                formula = sum(abs(theta[u]-theta[u[::-1]]) for u in ctx)
                assert d == Fraction(formula, 4*len(ctx))
                bound = alpha(k)*Fraction(max(levels)-min(levels), 4)
                assert d <= bound
                rev += d == 0
                best = max(best, d)
                H = entropy_rate(theta)
                if alpha(k):
                    upper = 1-float(alpha(k)) + float(alpha(k))*h((1+float(d/alpha(k)))/2)
                    assert H <= upper+1e-12
                else:
                    assert H <= 1+1e-12
            assert best == bound
            result.append(dict(order=k, levels=levels, tables=len(levels)**len(ctx),
                               reversible=rev, max_tv=str(best)))
    return result


def matched_census():
    result = []
    for k in range(3, 8):
        ctx = list(words(k-1))
        rev = dict.fromkeys(ctx, 3)
        irr = {u: 3 if u <= u[::-1] else 1 for u in ctx}
        # Palindromic contexts use 3 here, not 2: entropy-matched, not entropy-maximal.
        assert entropy_rate(rev) == entropy_rate(irr) or abs(entropy_rate(rev)-entropy_rate(irr)) < 1e-12
        d = tv(block(k, irr, k+1))
        assert d == alpha(k)/2
        rate = kl(block(k, irr, k+1))
        assert abs(rate - float(alpha(k))*0.5*log2(3)) < 1e-12
        tested = 0
        for n in range(1, k+8):
            a, b = block(k, rev, n), block(k, irr, n)
            assert Counter(a.values()) == Counter(b.values())
            if n >= k:
                expect = Counter({3**j: 2**k*comb(n-k, j) for j in range(n-k+1)})
                assert Counter(b.values()) == expect
            assert tv(a) == 0
            assert (tv(b) == 0) == (n <= k)
            assert abs(kl(b)-max(0,n-k)*rate) < 1e-9
            tested += len(b)
        result.append(dict(order=k, max_uniform_tv=str(alpha(k)), first_arrow=k+1,
                           tv_at_first=str(d), entropy_bits=round(h(.75), 12),
                           kl_bits_per_step=round(rate, 12),
                           block_lengths=k+7, word_weights_checked=tested))
    return result


def pcm(s):
    a = (3,3,2,1,-1,-2,-3,-3,-3,-3,-2,-1,1,2,3,3)
    b = (3,2,-2,-3,-3,-2,2,3)
    return [2000*v for bit in s for v in (a*20 if bit=='0' else b*40)]


def wav(samples):
    buf = BytesIO()
    with wave.open(buf, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
        f.writeframes(struct.pack('<'+'h'*len(samples), *samples))
    return buf.getvalue()


def autocorr(x):
    return [sum(a*b for a,b in zip(x, x[lag:])) for lag in range(len(x))]


def audio(out):
    s = '001011'
    a,b = pcm(s),pcm(s[::-1])
    assert a != b and a == b[::-1]
    assert autocorr(a) == autocorr(b)
    assert all(counts(s,j) == counts(s[::-1],j) for j in (1,2,3))
    assert counts(s,4) != counts(s[::-1],4)
    result = []
    for name, seq, x in [('forward',s,a),('retrograde',s[::-1],b)]:
        data = wav(x)
        with wave.open(BytesIO(data),'rb') as f:
            assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (1,2,8000,len(x))
        (out/(name+'.wav')).write_bytes(data)
        result.append(dict(name=name, word=seq, bytes=len(data), sha256=sha256(data).hexdigest()))
    return dict(samples=len(a), exact_autocorrelation_lags=len(a), recordings=result)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    out=p.parse_args().out; out.mkdir(parents=True,exist_ok=True)
    report=dict(model='synthetic', cyclic=cyclic_census(), grid=grid_census(),
                matched=matched_census(), audio=audio(out))
    data=json.dumps(report,indent=2,sort_keys=True)+'\n'
    (out/'execution.json').write_text(data,encoding='utf-8')
    print(data,end='')


if __name__ == '__main__':
    main()
