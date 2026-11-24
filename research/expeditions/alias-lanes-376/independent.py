"""Independent numerical SVD oracle and original synthetic audio, Python + NumPy."""
import hashlib
import itertools as it
import json
from pathlib import Path
import wave
import numpy as np

ROOT = Path(__file__).resolve().parent


def oracle(q, c):
    # Each two-column matrix is unitarily equivalent to columns 0 and gap.
    phase = np.exp(2j*np.pi*np.arange(1, q)[:, None]*np.array(c)[None, :]/q)
    a = np.stack((np.ones_like(phase), phase), axis=-1)/np.sqrt(len(c))
    return float(np.linalg.svd(a, compute_uv=False)[:, -1].min()) if len(c) > 1 else 0.


def write_wav(name, a, b):
    x = np.rint(np.column_stack((a, b))*12000).astype('<i2')
    assert np.max(np.abs(x.astype(int))) <= 24000
    path = ROOT/name
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(12000)
        f.writeframes(x.tobytes())
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'nonzero': np.count_nonzero(x, axis=0).tolist(),
            'peak': np.max(np.abs(x.astype(int)), axis=0).tolist()}


def main():
    rows = json.loads((ROOT/'results.synthetic.txt').read_text())['results']
    cached = {}
    max_error = 0.
    comparisons = 0
    for row in rows:
        q, m, e = (row[k] for k in ('q', 'm', 'e'))
        def value(c):
            key = (q, c)
            if key not in cached:
                cached[key] = oracle(q, c)
            return cached[key]
        def robust(c):
            return min(value(keep) for keep in it.combinations(c, m-e))
        scores = [(robust(c), c) for c in it.combinations(range(q), m)]
        comparisons += len(scores)
        best = max(x[0] for x in scores)
        errors = [abs(best-row['best']), abs(robust(tuple(row['witness']))-best),
                  abs(robust(tuple(range(m)))-row['consecutive'])]
        max_error = max(max_error, *errors)
        assert max(errors) < 1e-10
        assert sum(abs(x[0]-best) <= 1e-12 for x in scores) == row['ties']
    # An exact difference set: each nonzero directed difference occurs once.
    assert sorted((a-b)%7 for a,b in it.permutations((0,1,3),2)) == list(range(1,7))
    assert abs(oracle(7,(0,1,3))-np.sqrt(1-np.sqrt(2)/3)) < 1e-12
    # Blind-support falsifier: two different 2-sparse vectors, same 3 lanes.
    A = np.exp(2j*np.pi*np.outer(range(3),range(4))/4)
    assert np.max(np.abs(A@np.array([1,1j,0,0])-A@np.array([0,0,1,1j]))) < 1e-12
    # Direct finite-tone observations. The analytic pair is known, amplitudes unknown.
    n = np.arange(24000); fs = 12000; q = 12
    carriers = np.exp(2j*np.pi*np.outer(n,[400,4400])/fs)
    x = carriers@np.array([1.,-1.])
    bad = np.isin(n%q,[0,3,6]); good = np.isin(n%q,[0,1,2])
    assert np.max(np.abs(x[bad])) < 1e-9
    assert np.linalg.matrix_rank(carriers[good],tol=1e-8)==2
    assert np.linalg.matrix_rank(carriers[bad],tol=1e-8)==1
    fit, *_ = np.linalg.lstsq(carriers[good], x[good],rcond=None)
    reconstructed = carriers@fit
    assert np.max(np.abs(reconstructed-x)) < 1e-10
    audio = {'lost-lanes.wav':write_wav('lost-lanes.wav',np.where(bad,x.real,0.),np.where(good,x.real,0.)),
             'recovered.wav':write_wav('recovered.wav',x.real,reconstructed.real)}
    # Verify the bad stream really quantizes to zero; do not conflate refusal with reconstruction.
    assert np.all(np.rint(x[bad].real*12000)==0)
    receipt = {'numpy':np.__version__,'population_count':len(rows),'pattern_comparisons':comparisons,
               'unique_svd_subsets':len(cached),'max_numeric_error':max_error,
               'bad_analytic_peak':float(np.max(np.abs(x[bad]))),'fit_error':float(np.max(np.abs(reconstructed-x))),
               'audio':audio,'blind_support_negative':'passed'}
    (ROOT/'independent.synthetic.txt').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__':
    main()
