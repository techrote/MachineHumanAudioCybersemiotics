"""MHAC-X008 independent (standard-library) negative, positive and exhaustive tests."""
import itertools
from pathlib import Path
import sys
import tempfile
import unittest
import wave

EXPEDITION = Path(__file__).resolve().parents[1] / 'research' / 'expeditions' / 'echo-one-witness'
sys.path.insert(0, str(EXPEDITION))
import echo_lab as lab  # noqa: E402


class EchoOneWitnessTests(unittest.TestCase):
    def test_eight_messages_one_source(self):
        s = lab.scenario_summary('echo')
        self.assertEqual(s['message_count'], 8)
        self.assertEqual(s['known_root_count'], 1)
        self.assertEqual(s['unique_known_roots'], ['S1'])
        self.assertTrue(s['complete_declared_ancestry'])

    def test_eight_genuine_declarations(self):
        s = lab.scenario_summary('independent')
        self.assertEqual(s['message_count'], 8)
        self.assertEqual(s['known_root_count'], 8)
        self.assertEqual(len(set(s['unique_known_roots'])), 8)

    def test_mixed_two_roots(self):
        s = lab.scenario_summary('mixed')
        self.assertEqual(s['known_root_count'], 2)
        self.assertEqual(s['messages'][6]['known_roots'], ['S2'])

    def test_unknown_ancestry_forbids_complete_count(self):
        s = lab.scenario_summary('untraced')
        self.assertEqual(s['untraced_nodes'], ['U1'])
        self.assertEqual(s['known_root_count'], 1)
        self.assertIsNone(s['conditional_independent_root_posterior'])
        self.assertFalse(s['complete_declared_ancestry'])

    def test_untraced_descendant_is_transitive(self):
        n = [lab.Node('U', 'untraced'), lab.Node('A', 'derivative', ('U',)), lab.Node('B', 'derivative', ('A',))]
        o = lab.ancestry(n, ['B'])
        self.assertEqual(o['untraced_nodes'], ['U'])
        self.assertFalse(o['complete_declared_ancestry'])

    def test_opposing_evidence_cancels_under_toy(self):
        s = lab.scenario_summary('opposing')
        self.assertAlmostEqual(s['conditional_independent_root_posterior'], .5, places=12)
        self.assertGreater(s['defective_independent_message_posterior'], .999)

    def test_naive_and_source_corrected_probability(self):
        a = lab.scenario_summary('echo')
        b = lab.scenario_summary('independent')
        self.assertAlmostEqual(a['conditional_independent_root_posterior'], .8)
        self.assertGreater(a['defective_independent_message_posterior'], .99998)
        self.assertAlmostEqual(a['defective_independent_message_posterior'], b['conditional_independent_root_posterior'])

    def test_bayes_numerical_marginals(self):
        self.assertAlmostEqual(lab.posterior_for_observations(0, 0), .5)
        self.assertAlmostEqual(lab.posterior_for_observations(1, 0), .8)
        self.assertAlmostEqual(lab.posterior_for_observations(0, 1), .2)
        self.assertAlmostEqual(lab.posterior_for_observations(1, 1), .5)
        self.assertAlmostEqual(lab.posterior_for_observations(0, 0, prior=.3), .3)

    def test_bayes_invalid_probabilities_counts(self):
        for args in [(-1, 0), (1.2, 1), (True, 0)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                lab.posterior_for_observations(*args)
        for p in (0., 1., -1., 1.2):
            with self.subTest(p=p), self.assertRaises(ValueError):
                lab.posterior_for_observations(1, 0, prior=p)

    def test_bad_sources_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unknown parent'):
            lab.ancestry([lab.Node('A','derivative',('B',))], ['A'])
        with self.assertRaisesRegex(ValueError, 'cycle'):
            lab.ancestry([lab.Node('A','derivative',('B',)),lab.Node('B','derivative',('A',))], ['A'])

    def test_self_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError, 'cycle'):
            lab.ancestry([lab.Node('A','derivative',('A',))], ['A'])

    def test_dup_id_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate node ID'):
            lab.ancestry([lab.Node('A','observation',polarity='support'),lab.Node('A','untraced')], ['A'])

    def test_dup_parents_and_output_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate parent'):
            lab.ancestry([lab.Node('S','observation',polarity='support'),lab.Node('A','derivative',('S','S'))], ['A'])
        with self.assertRaisesRegex(ValueError, 'distinct output'):
            lab.ancestry([lab.Node('S','observation',polarity='support')], ['S','S'])

    def test_bad_node_types_rejected(self):
        cases = [
            [lab.Node('S','observation')],
            [lab.Node('S','observation',('Q',), 'support')],
            [lab.Node('X','untraced',polarity='support')],
            [lab.Node('X','derivative')],
            [lab.Node('X','derivative',('X',),'support')],
            [lab.Node('A/B','untraced')],
            [lab.Node('X','alien')],
        ]
        for xs in cases:
            with self.subTest(xs=xs), self.assertRaises(ValueError):
                lab.validated_nodes(xs)

    def test_parent_order_does_not_change_ancestry(self):
        first = [lab.Node('S','observation',polarity='support'),lab.Node('T','observation',polarity='oppose'),lab.Node('M','derivative',('S','T'))]
        second = [lab.Node('M','derivative',('T','S')),lab.Node('T','observation',polarity='oppose'),lab.Node('S','observation',polarity='support')]
        self.assertEqual(lab.ancestry(first,['M']),lab.ancestry(second,['M']))

    def test_exhaustive_small_dag_oracle_against_independent_iterative_closure(self):
        # Every forward-edge DAG over 4 vertices: 2^6=64. Every nonempty
        # output subset: 15. 960 cases, independently recomputed by set union.
        pairs = list(itertools.combinations(range(4),2))
        cases = 0
        for mask in range(1 << len(pairs)):
            parents = [[] for _ in range(4)]
            for bit,(lo,hi) in enumerate(pairs):
                if (mask >> bit) & 1:
                    parents[hi].append(f'N{lo}')
            nodes = [
                lab.Node(f'N{i}', 'derivative' if parents[i] else 'observation',
                         tuple(parents[i]), None if parents[i] else 'support')
                for i in range(4)
            ]
            expected = {}
            for i in range(4):
                if not parents[i]:
                    expected[f'N{i}']={f'N{i}'}
                else:
                    expected[f'N{i}']=set().union(*[expected[k] for k in parents[i]])
            for output_mask in range(1,16):
                outputs=[f'N{i}' for i in range(4) if output_mask & (1<<i)]
                got=lab.ancestry(nodes,outputs)
                wanted=set().union(*(expected[n] for n in outputs))
                self.assertEqual(set(got['unique_known_roots']),wanted)
                self.assertTrue(got['complete_declared_ancestry'])
                cases+=1
        self.assertEqual(cases,960)

    def test_one_vs_eight_acoustic_prefix_exact_identity(self):
        a,b=lab.sound_samples(1),lab.sound_samples(8)
        limit=round(lab.PREFIX_SECONDS*lab.SAMPLE_RATE)*2
        self.assertEqual(a[:limit],b[:limit])
        self.assertNotEqual(a,b)
        self.assertEqual(len(a),round(lab.DURATION_SECONDS*lab.SAMPLE_RATE)*2)
        self.assertGreater(sum(1 for i in range(0, limit, 2) if a[i:i+2]!=b'\0\0'),1000)

    def test_invalid_sonification_count_rejected(self):
        for n in (-1,0,2,7,9):
            with self.subTest(n=n), self.assertRaises(ValueError):
                lab.sound_samples(n)

    def test_wav_headers_and_receipt_reproducibility(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            x=lab.generate(Path(a));y=lab.generate(Path(b))
            self.assertEqual(x,y)
            self.assertTrue(x['prefix_identical'])
            self.assertFalse(x['full_pcm_identical'])
            self.assertEqual(len(x['files_sha256']),8)
            for name in ('echo-1-root.wav','eight-independent-roots.wav'):
                with wave.open(str(Path(a)/name),'rb') as w:
                    self.assertEqual(w.getnchannels(),1)
                    self.assertEqual(w.getsampwidth(),2)
                    self.assertEqual(w.getframerate(),24000)
                    self.assertEqual(w.getnframes(),180000)


if __name__ == '__main__':
    unittest.main()
