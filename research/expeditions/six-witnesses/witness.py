"""Original integer PCM witnesses for #724; Python 3.11+ and NumPy."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import wave
import numpy as np

ROOT = Path(__file__).resolve().parent


def period(primes, signs, weights=None):
    weights = weights or [1] * len(primes)
    return [(-1)**(t % 2) * sum(s*a*(p-1 if t % p == 0 else -1)
                               for p,s,a in zip(primes, signs, weights))
            for t in range(2*math.prod(primes))]


def deck5(x):
    """Literal sums; x restricted to small integers to keep int64 exact."""
    n = len(x)
    assert n * max(map(abs, x))**5 < 2**63
    x = np.asarray(x, dtype=np.int64)
    shifts = np.array([np.roll(x, -j) for j in range(n)])
    pairs = (shifts[:, None, :] * shifts[None, :, :]).reshape(n*n, n)
    return (pairs*x) @ pairs.T


def corr(x, lags):
    return sum(math.prod(x[(t+j) % len(x)] for j in (0,*lags))
               for t in range(len(x)))


def six(x):
    return sum(int(v)**6 for v in x)


def render(primes, signs, label, rate, scale, seconds=1):
    x = period(primes, signs)
    assert rate*seconds % len(x) == 0
    data = np.tile(np.array(x, dtype=np.int64)*scale, rate*seconds//len(x))
    assert max(abs(data)) <= 32767
    path = ROOT / (label + '.wav')
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        f.writeframes(data.astype('<i2').tobytes())
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (1, 2, rate)
        decoded = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').astype(np.int64)
    assert np.array_equal(decoded, data)
    assert np.all(decoded % scale == 0)
    recovered = (decoded[:len(x)]//scale).tolist()
    assert recovered == x
    return recovered, {'file':path.name, 'frames':len(decoded), 'rate':rate,
                       'scale':scale, 'peak':int(max(abs(decoded))),
                       'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                       'normalized_sixth_sum':six(recovered)}


def main():
    records = []
    recovered = []
    for signs, name in [([1,1],'plus'),([1,-1],'minus')]:
        x, row = render([3,5],signs,'six-30-'+name,9000,1800)
        records.append(row)
        recovered.append(x)
    a,b = recovered
    assert not any(a == b[j:]+b[:j] for j in range(len(b)))
    counts = 0
    for dc in (0,7):
        x,y = ([v+dc for v in z] for z in (a,b))
        D,E = deck5(x),deck5(y)
        assert np.array_equal(D,E)
        counts += D.size
        # Cumulative lower orders: centering gives zero odd decks, not zero even decks.
        for order in range(1,5):
            for lags in itertools.product(range(30),repeat=order-1):
                assert corr(x,lags)==corr(y,lags)
                counts += 1
    assert six(a)-six(b) == 30*40*2*12
    # Larger exact integer waveforms, all four relative sign configurations.
    rng = random.Random(724)
    baseline = None
    lags = [tuple(rng.randrange(770) for _ in range(4)) for _ in range(64)]
    four_moments = []
    for s in itertools.product((1,-1),repeat=2):
        signs = (1,*s)
        label = 'six-770-'+''.join('p' if i==1 else 'm' for i in s)
        x,row = render([5,7,11],signs,label,15400,600)
        records.append(row)
        values = [corr([v+21 for v in x],l) for l in lags]
        if baseline is None:
            baseline = values
        assert values == baseline
        four_moments.append(six(x))
    assert len(set(four_moments)) == 4
    # Explicit unweighted collision of scalar sixth moments, not waveform orbits.
    p = [5,7,11,13,17]
    s,t = [1,1,1,-1,1],[1,1,1,-1,-1]
    z1,z2 = period(p,s),period(p,t)
    assert six(z1)==six(z2)
    # Two private weight changes make third-moment weights superincreasing here.
    bs = [(q-1)*(q-2)*a**3 for q,a in zip(p,[1,1,1,2,3])]
    assert all(b>sum(bs[:i]) for i,b in enumerate(bs))
    codes = {sum(b*s for b,s in zip(bs,(1,*u)))**2
             for u in itertools.product((1,-1),repeat=len(p)-1)}
    assert len(codes)==16
    result = {'numpy':np.__version__, 'complete_literal_correlation_entries':counts,
              'larger_sampled_fifth_entries':4*len(lags),
              'decoded_frames':sum(r['frames'] for r in records),
              'sixth_sums_770':four_moments,
              'scalar_collision_period':len(z1),'scalar_collision_sixth_sum':six(z1),
              'weighted_scalar_codes':len(codes),'records':records}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
