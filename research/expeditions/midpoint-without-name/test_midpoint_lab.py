import unittest
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import tempfile, wave, hashlib
import midpoint_lab as lab


class MidpointTests(unittest.TestCase):
    def test_constructive_sharpness(self):
        for lo,hi in [(F(1,2),F(2)),(F(3,4),F(3,2)),(F(1),F(1))]:
            for a in [((0,0),(1,1)),((0,0),(F(1,2),F(1,2)),(1,1))]:
                for i in range(65):
                    t=F(i,64); l,h=lab.bounds(t,a,lo,hi)
                    for x in [l,(l+h)/2,h]:
                        p=lab.witness(t,x,a,lo,hi)
                        self.assertEqual(lab.interp(p,x),t)
                        for (u,v),(w,z) in zip(p,p[1:]):
                            self.assertTrue(lo <= (z-v)/(w-u) <= hi)
    def test_invalid(self):
        for a in [((0,0),(F(1,2),F(1,8)),(1,1)),((0,0),(0,F(1,2)),(1,1))]:
            with self.assertRaises(ValueError):lab.bounds(F(1,2),a)
        with self.assertRaises(ValueError):lab.bounds(F(2))
        with self.assertRaises(ValueError):lab.witness(F(1,2),F(1,8))
    def test_affine_and_rank_controls(self):
        for x,y,z in product(range(5),repeat=3):
            f=lambda t:3*t+7
            self.assertEqual((f(x)+f(y))/F(2),f((x+y)/F(2)))
            g=lambda t:t**3+1
            self.assertEqual(sorted(map(g,(x,y,z)))[1],g(sorted((x,y,z))[1]))
        self.assertNotEqual((0**3+2**3)/2,1**3)
    def test_grid(self):
        r=lab.grid_census()
        self.assertEqual(r['valid_charts'],{'None':3823,'1/2':961,'3/8':440})
        self.assertEqual(sum(row['grid_attains_both'] for row in r['rows']),39)
        self.assertEqual(len(r['rows']),51)
        self.assertEqual(lab.bounds(F(1,2)),(F(1,4),F(3,4)))
    def test_audio(self):
        with tempfile.TemporaryDirectory() as d:
            r=lab.score(Path(d))
            self.assertEqual([r[k]['frequencies_hz'][4] for k in ('early','identity','late')],[400,600,800])
            data=[]
            for k in r:
                p=Path(d)/(k+'.wav')
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r[k]['sha256'])
                with wave.open(str(p),'rb') as w:
                    self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()),(1,2,16000,28800))
                    data.append(w.readframes(w.getnframes()))
            self.assertEqual(len(set(data)),3)
            self.assertEqual(len({x[:6400] for x in data}),1)
            self.assertEqual(len({x[-6400:] for x in data}),1)

if __name__=='__main__':unittest.main()
