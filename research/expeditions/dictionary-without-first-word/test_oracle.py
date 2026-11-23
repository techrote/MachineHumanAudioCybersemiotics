import functools
import itertools
import tempfile
import unittest
from pathlib import Path
import wave
import oracle as o


class Tests(unittest.TestCase):
    def test_census(self):
        self.assertEqual(o.census(6), {'n': 6,
            'labeled': {0:5760, 1:16920, 2:8244, 3:1680, 4:162, 5:2},
            'classes': {0:8, 1:48, 2:56, 3:30, 4:12, 5:2},
            'twinless_labeled': {0:5760, 1:7560, 2:504}})

    def test_wrong_anchor(self):
        n = 5
        m = o.mask_of(n, [(i,i+1) for i in range(n-1)])
        self.assertEqual(len(o.candidates(n,m,m,[(2,2)])), 2)
        self.assertEqual(len(o.candidates(n,m,m,[(0,0)])), 1)
        self.assertEqual(o.action_values(o.candidates(n,m,m), 2), {2})
        self.assertEqual(o.action_values(o.candidates(n,m,m), 0), {0,4})

    def test_cycle(self):
        n = 5
        m = o.mask_of(n, [(i,(i+1)%n) for i in range(n)])
        a = o.automorphisms(n,m)
        self.assertEqual(len(a),10)
        self.assertEqual(len(o.determining(n,a)),10)
        self.assertEqual(len(o.determining(n,a)[0]),2)
        self.assertTrue(all(sum(i!=x for i,x in enumerate(p))!=2 for p in a))

    def test_nonisomorphic_and_contradiction(self):
        self.assertEqual(o.candidates(3,0,1), [])
        self.assertEqual(o.candidates(3,0,0,[(0,0),(0,1)]), [])
        with self.assertRaises(ValueError): o.candidates(3,0,0,[(0,3)])
        with self.assertRaises(ValueError): o.candidates(3,0,8)
        with self.assertRaises(ValueError): o.automorphisms(3,-1)
        self.assertEqual(o.mask_of(3,[(0,1),(1,0)]),1)

    def test_cosets_and_adaptive(self):
        # Independent decision-tree search: does not call determining().
        @functools.lru_cache(None)
        def cost(maps):
            if len(maps) <= 1: return 0
            n = len(maps[0]); options = []
            for i in range(n):
                blocks = {}
                for p in maps: blocks.setdefault(p[i], []).append(p)
                if len(blocks)>1:
                    options.append(1+max(cost(tuple(v)) for v in blocks.values()))
            return min(options)
        total = 0
        for n in range(1,6):
            edges,_ = o.geometry(n); unseen=set(range(1<<len(edges)))
            while unseen:
                m=min(unseen); im=o.images(n,m); unseen -= {v for _,v in im}
                autos=tuple(o.automorphisms(n,m)); k=len(o.determining(n,autos)[0])
                self.assertEqual(cost(autos),k)
                # Test a nontrivial relabeling, with every single anchor.
                p, physical=im[-1]
                actual=set(o.candidates(n,m,physical))
                self.assertEqual(actual,{tuple(p[a[i]] for i in range(n)) for a in autos})
                for i in range(n):
                    self.assertEqual(set(o.candidates(n,m,physical,[(i,p[i])])),
                        {tuple(p[a[j]] for j in range(n)) for a in autos if a[i]==i})
                total+=1
        self.assertEqual(total, 52)

    def test_sonic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); o.sonic_witness(root)
            self.assertEqual((root/'relations-a.wav').read_bytes(),(root/'relations-b.wav').read_bytes())
            self.assertNotEqual((root/'target-a.wav').read_bytes(),(root/'target-b.wav').read_bytes())
            with wave.open(str(root/'target-a.wav'),'rb') as w:
                self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()),(1,2,8000,800))


if __name__ == '__main__': unittest.main()
