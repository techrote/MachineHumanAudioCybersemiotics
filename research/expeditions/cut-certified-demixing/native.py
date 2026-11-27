"""Synthetic LP comparison for cut-certified two-period demixing."""
import json
import sys
import numpy as np
import scipy
from scipy.optimize import linprog


def design(p, q, times):
    x = np.zeros((len(times), p + q))
    for i, t in enumerate(times):
        x[i, t % p] = 1
        x[i, p + t % q] = -1
    return x[:, 1:]


def lad(x, y, weights=None):
    n, d = x.shape
    eye = np.eye(n)
    cost = np.r_[np.zeros(d), np.ones(n) if weights is None else weights]
    res = linprog(cost, A_ub=np.block([[x, -eye], [-x, -eye]]),
                  b_ub=np.r_[y, -y], bounds=[(None, None)] * d + [(0, None)] * n,
                  method='highs')
    if not res.success:
        raise RuntimeError(res.message)
    return res.x[:d]


def run():
    rng = np.random.default_rng(754)
    rows = []
    for p, q in [(3, 5), (5, 7), (7, 11), (11, 17)]:
        for e, f in [(1, 0), (1, 2), (2, 1), (3, 2)]:
            n = (2 * e + f + 1) * q
            worst_lad = worst_ols = worst_noisy_ratio = 0.0
            ols_failures = 0
            for _ in range(20):
                order = rng.permutation(n)
                times = sorted(order[f:])
                bad = np.isin(times, order[f:f+e])
                x = design(p, q, times)
                theta = rng.integers(-20, 21, size=p+q-1)
                y = x @ theta
                y[bad] += rng.choice([-1, 1], e) * rng.integers(1000, 10001, e)
                fit = lad(x, y)
                err = np.max(np.abs(fit-theta))
                assert err < 1e-6
                worst_lad = max(worst_lad, float(err))
                ols_err = float(np.max(np.abs(np.linalg.lstsq(x, y, rcond=None)[0]-theta)))
                worst_ols = max(worst_ols, ols_err)
                ols_failures += ols_err > 1e-6
                noise = rng.uniform(-0.1, 0.1, len(times))
                noise[bad] = 0
                h = np.r_[0, lad(x, y+noise)-theta]
                # Residual cut margin is at least one at the sharp deadline.
                bound = 2 * np.sum(np.abs(noise))
                ratio = float(np.ptp(h) / bound)
                assert ratio <= 1 + 1e-6
                worst_noisy_ratio = max(worst_noisy_ratio, ratio)
            rows.append(dict(p=p, q=q, e=e, f=f, n=n, trials=20,
                             worst_lad=round(worst_lad, 9), worst_ols=round(worst_ols, 6),
                             ols_failures=int(ols_failures), worst_noisy_bound_ratio=round(worst_noisy_ratio, 9)))
    # Weighted objective may prefer the wrong reconstruction despite lambda=3.
    x = design(5, 7, range(21))
    h = np.zeros(11)
    h[4] = 1  # B residue 0, degree three.
    diff = x @ h
    i = np.flatnonzero(diff)[0]
    y = np.zeros(21)
    y[i] = diff[i]
    weights = np.ones(21)
    weights[i] = 3
    u = lad(x, y)
    w = lad(x, y, weights)
    assert np.max(np.abs(u)) < 1e-6
    assert np.sum(weights * np.abs(x @ w-y)) < np.sum(weights * np.abs(y))
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                trials=sum(r['trials'] for r in rows), ols_failures=sum(r['ols_failures'] for r in rows),
                rows=rows, weighted_counterexample_cost=float(np.sum(weights*np.abs(x@w-y))), failures=0)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
