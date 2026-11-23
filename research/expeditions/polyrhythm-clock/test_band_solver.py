import unittest
import clock
import band_solver


class BandSolverTests(unittest.TestCase):
    def test_exhaustive_crosscheck(self):
        for row in clock.census(10):
            q,p,r=row['q'],row['p'],row['r']
            result=band_solver.minimax(q,p,r)
            m=result['max_excess']
            self.assertEqual(m,max(row['best_disjoint']['point'][1:]))
            a,b=result['words']
            self.assertEqual((len(a),len(b),sum(a),sum(b)),(q,q,p,r))
            self.assertFalse(any(x*y for x,y in zip(a,b)))
            self.assertEqual(max(result['excesses']),m)
            da,db=row['individual_bounds']
            if m:
                self.assertIsNone(band_solver.bounded(q,p,r,da+m-1,db+m-1))

    def test_asymmetric_caps(self):
        self.assertIsNone(band_solver.bounded(6,2,3,4,3))
        self.assertIsNone(band_solver.bounded(6,2,3,5,5))
        self.assertIsNotNone(band_solver.bounded(6,2,3,6,3))
        self.assertIsNotNone(band_solver.bounded(6,2,3,4,6))

    def test_large_odd_family(self):
        for a in (3,5,7,15,31,63):
            self.assertEqual(band_solver.minimax(2*a,2,a)['max_excess'],2)


if __name__=='__main__':
    unittest.main()
