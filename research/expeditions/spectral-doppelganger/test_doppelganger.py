import unittest
from itertools import combinations
import doppelganger as d

A=(0,1,4,6)
B=(0,1,3,7)
X=(0,1,2,3,4,5,6,8,10,11,19,21)
Y=(0,1,2,3,4,6,7,8,9,11,17,22)

class TestDoppelganger(unittest.TestCase):
    def test_classic_pair(self):
        self.assertNotEqual(d.canonical(A,12),d.canonical(B,12))
        self.assertEqual(d.autocorr(A,12),d.autocorr(B,12))
        self.assertNotEqual(d.triple_invariant(A,12),d.triple_invariant(B,12))
    def test_orbit_invariance(self):
        for s in d.orbit(A,12):
            self.assertEqual(d.autocorr(s,12),d.autocorr(A,12))
            self.assertEqual(d.triple_invariant(s,12),d.triple_invariant(A,12))
            self.assertEqual(d.canonical(s,12),d.canonical(A,12))
    def test_noncollision(self):
        self.assertNotEqual(d.autocorr(A,12),d.autocorr((0,1,2,3),12))
    def test_third_order_counterexample(self):
        self.assertNotEqual(d.canonical(X,24),d.canonical(Y,24))
        self.assertEqual(d.autocorr(X,24),d.autocorr(Y,24))
        self.assertEqual(d.triples(X,24),d.triples(Y,24))
        self.assertNotEqual(d.fourth_invariant(X,24),d.fourth_invariant(Y,24))
    def test_complement_identity(self):
        for s in (X,Y):
            self.assertEqual({(x+12)%24 for x in s},set(range(24))-set(s))
            p=d.autocorr(s,24); t=d.triples(s,24)
            for a in range(24):
                for b in range(24):
                    self.assertEqual(2*t[a*24+b],p[a]+p[b]+p[(b-a)%24]-12)
    def test_exhaustive_small_independent(self):
        for n in range(3,9):
            reps=set(); groups={}
            for k in range(n+1):
                for s in combinations(range(n),k):
                    rep=d.canonical(s,n)
                    reps.add(rep)
                    signal=[int(i in s) for i in range(n)]
                    direct=tuple(sum(signal[i]*signal[(i+j)%n] for i in range(n)) for j in range(n))
                    self.assertEqual(d.autocorr(s,n),direct)
                    groups.setdefault(direct,set()).add(rep)
            r=d.survey(n)
            self.assertEqual(r['bracelets'],len(reps))
            self.assertEqual(r['ambiguous_pair_classes'],sum(len(g)>1 for g in groups.values()))
    def test_pcm_exact_circular(self):
        # Small step with nonoverlap. Independent sparse pair-sum over integer samples.
        def corr(x):
            out=[0]*len(x); nz=[(i,v) for i,v in enumerate(x) if v]
            for i,a in nz:
                for j,b in nz:
                    out[(j-i)%len(x)]+=a*b
            return out
        a,b=d.render(A,12,120),d.render(B,12,120)
        self.assertNotEqual(a,b)
        self.assertEqual(corr(a),corr(b))
        # Finite nonperiodic window is explicitly not guaranteed.
    def test_anchored_count_control(self):
        # Different fixed phase; pair descriptor deliberately discards origin.
        self.assertEqual(d.autocorr(A,12),d.autocorr(tuple((x+2)%12 for x in A),12))
        self.assertNotEqual(d.render(A,12),d.render(tuple((x+2)%12 for x in A),12))

if __name__=='__main__':unittest.main()
