import itertools
import math
import unittest
import clock


class ClockTests(unittest.TestCase):
    def test_exact_windows_and_bound(self):
        for q in range(1,9):
            minima={}
            for w in itertools.product((0,1),repeat=q):
                p=sum(w)
                direct=max(abs(q*sum((w+w)[s:s+k])-p*k)
                           for s in range(q) for k in range(q+1))
                self.assertEqual(clock.discrepancy(w),direct)
                minima[p]=min(minima.get(p,q*q),direct)
            for p,d in minima.items():
                self.assertEqual(d,q-math.gcd(q,p))
                for phase in range(q):
                    self.assertEqual(clock.discrepancy(clock.mechanical(q,p,phase)),d)

    def test_exact_witness(self):
        r=clock.solve(6,2,3)
        self.assertEqual(r['pairs_examined'],300)
        self.assertEqual({x['point'] for x in r['front']},
                         {(0,0,3),(0,2,0),(1,0,0)})
        self.assertEqual(r['best_disjoint']['point'],(0,2,0))

    def test_controls(self):
        self.assertEqual(clock.solve(6,2,2)['min_overlap_at_individual_optima'],0)
        self.assertEqual(clock.solve(6,3,3)['min_overlap_at_individual_optima'],0)
        self.assertEqual(clock.solve(4,1,2)['min_overlap_at_individual_optima'],0)
        self.assertRaises(ValueError,clock.solve,6,3,4)
        self.assertRaises(ValueError,clock.solve,13,2,3)

    def test_front_witnesses(self):
        for r in clock.census(8):
            q,p,s=r['q'],r['p'],r['r']
            for entry in r['front']:
                a,b=entry['words']
                self.assertEqual((len(a),len(b),sum(a),sum(b)),(q,q,p,s))
                self.assertEqual(entry['point'],(sum(x*y for x,y in zip(a,b)),
                    clock.discrepancy(a)-q+math.gcd(q,p),
                    clock.discrepancy(b)-q+math.gcd(q,s)))

    def test_coprime_periods(self):
        for a,b in ((2,3),(2,5),(3,4),(4,5),(5,7)):
            q=a*b
            for i,j in itertools.product(range(a),range(b)):
                self.assertEqual(sum(int(t%a==i and t%b==j) for t in range(q)),1)


if __name__=='__main__':
    unittest.main()
