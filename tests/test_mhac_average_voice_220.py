"""Qualification bridge for the isolated #220 finite synthetic oracle."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/"research/expeditions/average-voice/oracle.py"
spec=importlib.util.spec_from_file_location("average_voice_oracle",path)
oracle=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)

class AverageVoice(unittest.TestCase):
    def test_partition_counts(self):
        self.assertEqual([len(list(oracle.partitions(n))) for n in range(1,7)],[1,2,5,15,52,203])

    def test_sharp_bound_and_pool_beats_both(self):
        a=oracle.assess((120,0,0),(60,60,0),(60,0,60),120)
        self.assertEqual((a["sx"],a["sz"],a["sp"],a["d"],a["c"],a["var_num"]),(7200,7200,5400,1800,5400,1800))
        self.assertEqual(3*a["d"]**2,a["c"]*a["var_num"])

    def test_strict_bound(self):
        a=oracle.assess((120,0,0),(60,60,0),(120,0,0),120)
        self.assertLess(3*a["d"]**2,a["c"]*a["var_num"])

    def test_mean_hides_joint_information(self):
        a=oracle.assess((120,120,0,0,0,0),(30,60,30,30,30,60),(30,120,30,30,30,0),120)
        self.assertEqual(a["p"],(30,90,30,30,30,30))
        self.assertEqual(a["q"],(24,120,24,24,24,24))
        self.assertEqual(a["j"],(30,120,30,30,30,0))
        self.assertEqual(a["joint_gain"],720)

    def test_identical_and_constant(self):
        a=oracle.assess((120,0),(60,60),(60,60),120)
        self.assertEqual((a["d"],a["c"],a["var_num"],a["joint_gain"]),(0,0,0,0))

    def test_reject_invalid_inputs(self):
        for y,x,z,s in [((120,0),(0,0),(120,120),120),((1,),(1,),(1,),120),((120,0),(60,),(60,60),120),((),(),(),120)]:
            with self.subTest(y=y,x=x,z=z):
                with self.assertRaises(ValueError):
                    oracle.assess(y,x,z,s)
        with self.assertRaises(ValueError):
            oracle.condition((1,0),(0,0))
        with self.assertRaises(ValueError):
            oracle.census(7)

    def test_independent_census_crosscheck(self):
        expected=[
            (1,2,0,0,0,0),(2,9,1,0,0,0),(3,60,18,2,8,0),
            (4,600,280,62,202,0),(5,8268,4876,1340,4568,0),
            (6,144942,96712,31066,89409,292),
        ]
        keys=("n","pairs","distinct","beats_both","strict_bound","joint_gain")
        self.assertEqual([tuple(a[k] for k in keys) for a in oracle.census()],expected)

if __name__=="__main__":
    unittest.main()
