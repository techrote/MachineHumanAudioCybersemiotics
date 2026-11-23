"""MHAC-T009 synthetic mapping regression; no participants or generated audio."""
import copy
import sys
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1] / "research" / "tangents" / "multiaxis-semantic-crosstalk"
sys.path.insert(0, str(MODULE_DIR))
import analyze


class MultiaxisContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.policies = analyze.load()

    def test_truth_is_independently_factorial(self):
        analyze.validate_cases(self.cases)
        self.assertEqual(len(self.cases), 30)

    def test_exact_collisions_not_listener_confusion(self):
        r = analyze.audit(self.cases, self.policies)
        self.assertEqual((r['fused']['unique_codes'], r['fused']['extra_cases_in_collision_groups']), (8, 22))
        for name in ('naive', 'engineered', 'serial'):
            self.assertEqual(r[name]['unique_codes'], 30)
            self.assertFalse(r[name]['human_decoding_tested'])

    def test_defective_polarity_fails_closed(self):
        faulty = copy.deepcopy(self.policies)
        faulty['engineered']['dimensions']['certainty']['levels'] = [1, 3, 2]
        with self.assertRaises(AssertionError):
            analyze.validate_mappings(faulty)

    def test_saturation_fails_closed(self):
        faulty = copy.deepcopy(self.policies)
        faulty['naive']['dimensions']['hazard']['levels'] = [0, 0, 2]
        with self.assertRaises(AssertionError):
            analyze.validate_mappings(faulty)

    def test_one_field_change_keeps_other_components(self):
        for name in ('naive', 'engineered', 'serial'):
            p = self.policies[name]
            base = {'certainty':1, 'hazard':1, 'urgency':1, 'requested_action':'inspect', 'addressee':'operator-A'}
            orig = analyze.encode(base, p)
            for field in analyze.FIELDS:
                changed = dict(base, **{field:2})
                other = analyze.encode(changed, p)
                self.assertEqual(sum(a != b for a,b in zip(orig,other)), 1, (name,field))

    def test_unknown_is_not_confidence_zero(self):
        base = {'certainty':0, 'hazard':1, 'urgency':1, 'requested_action':'inspect', 'addressee':'operator-A'}
        other = dict(base, certainty=None)
        for name in ('naive','engineered','serial'):
            self.assertNotEqual(analyze.encode(base,self.policies[name]),analyze.encode(other,self.policies[name]))

    def test_three_way_collision_falsifies_scalar(self):
        a = {'certainty':0,'hazard':1,'urgency':2,'requested_action':'inspect','addressee':'operator-A'}
        b = {'certainty':2,'hazard':0,'urgency':1,'requested_action':'inspect','addressee':'operator-A'}
        self.assertEqual(analyze.encode(a,self.policies['fused']),analyze.encode(b,self.policies['fused']))
        for name in ('naive','engineered','serial'):
            self.assertNotEqual(analyze.encode(a,self.policies[name]),analyze.encode(b,self.policies[name]))


if __name__ == '__main__':
    unittest.main()
