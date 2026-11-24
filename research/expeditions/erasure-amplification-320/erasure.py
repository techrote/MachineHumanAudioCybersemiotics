"""Pointwise L-infinity amplification for periodic critically retained samples."""
import math


def critical_weights(M, erased, target):
    """Return retained-index -> coefficient for a missing on-grid target.

    Model degree m=(M-len(erased)-1)/2. Floating evaluation of exact formula.
    """
    E = tuple(sorted(set(erased)))
    if not isinstance(M, int) or not 3 <= M <= 4096:
        raise ValueError('grid size must be integer in [3,4096]')
    if any(not isinstance(e, int) or not 0 <= e < M for e in E):
        raise ValueError('invalid erased index')
    n = M-len(E)
    if target not in E or n < 1 or n % 2 != 1 or len(E) > 12:
        raise ValueError('need missing target, positive odd retained count, <=12 erasures')
    others = [e for e in E if e != target]
    den = math.prod(math.sin(math.pi*(target-e)/M) for e in others)
    return {j: (-1 if (j-target+1)%2 else 1)*
            math.prod(math.sin(math.pi*(j-e)/M) for e in others)/den
            for j in range(M) if j not in E}


def certificate(M, erased, target):
    w = critical_weights(M, erased, target)
    return {'gain': math.fsum(abs(v) for v in w.values()),
            'weights': w, 'witness': {j: 1 if v >= 0 else -1 for j,v in w.items()}}


def two_erasure_gain(M, d):
    if not isinstance(M,int) or M < 5 or M%2 != 1 or not 1 <= d < M:
        raise ValueError('odd M>=5 and nonzero separation required')
    # Degree (M-3)/2, erased positions 0,d.
    return 1/math.tan(math.pi/(2*M))/math.sin(math.pi*d/M)-1


def one_remaining_gain(M):
    if not isinstance(M,int) or M < 5 or M%2 != 1:
        raise ValueError('odd M>=5 required')
    # Same degree (M-3)/2, only one missing sample.
    return 1/math.sin(math.pi/(2*M))-1
