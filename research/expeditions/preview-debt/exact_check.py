"""Independent exact rational checks of the first-order construction."""
from fractions import Fraction as F


def conv(x, y):
    z = [F(0)] * (len(x) + len(y) - 1)
    for i, p in enumerate(x):
        for j, q in enumerate(y):
            z[i+j] += p*q
    return z


def check():
    count = witness = 0
    for den in range(2, 12):
        for num in range(1, den):
            a = F(num, den)
            for d in range(1, 33):
                # G has denominator 1, H denominator 1-aw.
                g = conv([1, -a], [a**(d-1-i) for i in range(d)])
                got = conv([-a, 1], g)
                want = conv([-(a**d)] + [F(0)]*(d-1) + [F(1)], [1, -a])
                assert got == want
                count += 1
                for t in range(-8, d+1):
                    assert -a*a**(d-t) + a**(d-t+1) == 0
                    witness += 1
    print(f'{count} exact transfer identities; {witness} exact zero-output steps')


if __name__ == '__main__':
    check()
