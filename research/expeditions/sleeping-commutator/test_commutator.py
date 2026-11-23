import itertools
import tempfile
import unittest
import wave
from pathlib import Path
import struct
from commutator import audit, extremal, trace, render, survey


class CommutatorTests(unittest.TestCase):
    def test_sharp_family(self):
        for n in range(3,65):
            r = audit(*extremal(n))
            self.assertEqual(r['witness']['prefix'], 'B'*(n-3))
            self.assertEqual(r['global_disagreement'], list(range(n-3,n)))
            self.assertNotEqual(r['witness']['AB_trace'][-1],r['witness']['BA_trace'][-1])

    def test_unreachable_disagreement(self):
        r = audit((0,2,1,3),(0,1,3,2))
        self.assertEqual(r['global_disagreement'], [1,2,3])
        self.assertEqual(r['reachable'], [0])
        self.assertTrue(r['reachable_equal'])

    def test_commuting_nontrivial(self):
        r = audit((1,2,3,0),(2,3,0,1))
        self.assertTrue(r['reachable_equal'])
        self.assertEqual(r['reachable'], [0,1,2,3])
        self.assertIsNone(r['witness'])

    def test_reject_nonpermutation(self):
        for a,b,s in [((0,0),(0,1),0), ((0,1),(0,),0), ((0,),(0,),1), ((),(),0)]:
            with self.assertRaises(ValueError): audit(a,b,s)

    def test_independent_word_enumeration(self):
        # Brute-force words, not BFS, over all ordered pairs of S4.
        ps = list(itertools.permutations(range(4)))
        for a,b in itertools.product(ps,repeat=2):
            r = audit(a,b)
            hits=[]
            for depth in range(4):
                for w in itertools.product('AB',repeat=depth):
                    w=''.join(w)
                    if trace(a,b,0,w+'AB')[-1]!=trace(a,b,0,w+'BA')[-1]: hits.append(w)
                if hits: break
            self.assertEqual(r['witness']['prefix'] if r['witness'] else None, min(hits) if hits else None)

    def test_relabel(self):
        a,b=extremal(6); q=(5,3,1,4,2,0)
        def relabel(f): return tuple(q[f[q.index(s)]] for s in range(len(q)))
        r=audit(relabel(a),relabel(b),q[0]); self.assertEqual(r['witness']['prefix'],'BBB')
        self.assertEqual(r['global_disagreement'],sorted(q[s] for s in (3,4,5)))

    def test_audio_channel_prefix_and_terminal(self):
        w=audit(*extremal(8))['witness']
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.wav'; a=render(p,w['AB_trace'],w['BA_trace']); b=render(p,w['AB_trace'],w['BA_trace'])
            self.assertEqual(a,b)
            with wave.open(str(p),'rb') as f:
                frames=list(struct.iter_unpack('<hh',f.readframes(f.getnframes())))
            self.assertTrue(all(l==r for l,r in frames[:6*3520]))
            self.assertTrue(any(l!=r for l,r in frames[-3520:]))

    def test_small_census(self):
        self.assertEqual(survey(4)['counts'], {'hidden':54,'immediate':384,'reachable_equal':138,'unreachable_disagreement_subset':18})


if __name__ == '__main__': unittest.main()
