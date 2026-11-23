import importlib.util
import io
from pathlib import Path
import struct
import unittest
import wave

P = Path(__file__).resolve().parents[1] / "research/expeditions/migrating-timbre/lab.py"
spec = importlib.util.spec_from_file_location("migrating_timbre",P)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

class MigratingTimbre(unittest.TestCase):
    def test_nontransitivity(self):
        self.assertEqual(lab.distance(0,1),1)
        self.assertEqual(lab.distance(1,2),1)
        self.assertEqual(lab.distance(0,2),2)

    def test_chain(self):
        r=lab.analyze(range(9))
        self.assertTrue(r["all_local"])
        self.assertEqual(r["endpoint_distance"],8)
        self.assertEqual(r["path_length"],8)
        self.assertFalse(r["anchor_pass"])
        self.assertFalse(r["budget_pass"])

    def test_triangle_bound_exhaustive(self):
        for a in range(9):
            for b in range(9):
                for c in range(9):
                    self.assertLessEqual(lab.distance(a,c),lab.distance(a,b)+lab.distance(b,c))

    def test_graph_closure(self):
        self.assertEqual(lab.component(range(9),0,1),list(range(9)))
        self.assertEqual(lab.component([0,1,7,8],0,1),[0,1])
        self.assertEqual(lab.component(range(9),0,0),[0])

    def test_return_does_not_erase_travel(self):
        r=lab.analyze([0,1,2,3,2,1,0])
        self.assertTrue(r["all_local"])
        self.assertEqual(r["endpoint_distance"],0)
        self.assertEqual(r["max_anchor_distance"],3)
        self.assertEqual(r["path_length"],6)
        self.assertFalse(r["budget_pass"])

    def test_bounded_and_constant(self):
        for p in ([0,1,0,1],[0,0,0]):
            r=lab.analyze(p)
            self.assertTrue(r["all_local"])
            self.assertTrue(r["anchor_pass"])
            self.assertTrue(r["budget_pass"])

    def test_jump(self):
        self.assertFalse(lab.analyze([0,1,8])["all_local"])

    def test_audio_channels(self):
        data=lab.render([0,8])
        self.assertEqual(data,lab.render([0,8]))
        with wave.open(io.BytesIO(data)) as f:
            self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),(2,2,16000))
            frames=list(struct.iter_unpack("<hh",f.readframes(f.getnframes())))
        k=lab.TONE+lab.GAP
        self.assertEqual(len(frames),2*k)
        self.assertTrue(all(l==r for l,r in frames[:k]))
        self.assertEqual([r for l,r in frames[:k]],[r for l,r in frames[k:]])
        self.assertTrue(any(l!=r for l,r in frames[k:]))

    def test_invalid(self):
        for bad in (-1,9,True,1.5):
            with self.assertRaises(ValueError):
                lab.distance(0,bad)
        with self.assertRaises(ValueError):
            lab.analyze([])
        with self.assertRaises(ValueError):
            lab.render([])

    def test_print_execution_receipt(self):
        import json
        result=lab.report()
        self.assertEqual(result["cases"]["migration"]["endpoint_distance"],8)
        print("MHAC_MIGRATING_TIMBRE="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    unittest.main()
