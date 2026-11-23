"""Exact finite tests for X003. No listener or scientific validation implied."""
import tempfile
import unittest
import wave
from pathlib import Path

from causal_counterpoint import DEMO_GRAPH, EventGraph, generate


class GraphTests(unittest.TestCase):
    def test_six_interleavings(self):
        self.assertEqual(len(list(DEMO_GRAPH.linear_extensions())), 6)

    def test_every_extension_preserves_dependencies(self):
        for order in DEMO_GRAPH.linear_extensions():
            self.assertEqual(len(order), len(set(order)))
            for source, target in DEMO_GRAPH.edges:
                self.assertLess(order.index(source), order.index(target))

    def test_concurrent_witnesses_reverse_pair(self):
        left, right = DEMO_GRAPH.witnesses("A.emit", "B.emit")
        self.assertLess(left.index("A.emit"), left.index("B.emit"))
        self.assertLess(right.index("B.emit"), right.index("A.emit"))
        self.assertEqual(left[-1], "M.combine")
        self.assertEqual(right[-1], "M.combine")

    def test_proven_and_opposite_and_unwarranted(self):
        self.assertEqual(DEMO_GRAPH.order_claim("A.sense", "M.combine"), "entailed")
        self.assertEqual(DEMO_GRAPH.order_claim("M.combine", "A.emit"), "contradicted")
        self.assertEqual(DEMO_GRAPH.order_claim("A.emit", "B.emit"), "not_entailed_either_way")

    def test_absence_of_dependency_does_not_mean_simultaneity(self):
        graph = EventGraph(("x", "y"), ())
        self.assertEqual(list(graph.linear_extensions()), [("x", "y"), ("y", "x")])
        self.assertEqual(graph.order_claim("x", "y"), "not_entailed_either_way")

    def test_chain_has_single_linear_extension(self):
        graph = EventGraph(("x", "y", "z"), (("x", "y"), ("y", "z")))
        self.assertEqual(list(graph.linear_extensions()), [("x", "y", "z")])
        self.assertEqual(graph.order_claim("x", "z"), "entailed")
        with self.assertRaises(ValueError):
            graph.witnesses("x", "z")

    def test_add_dependency_reduces_variance(self):
        stronger = EventGraph(DEMO_GRAPH.nodes, DEMO_GRAPH.edges + (("A.emit", "B.emit"),))
        self.assertLess(len(list(stronger.linear_extensions())), 6)
        self.assertEqual(stronger.order_claim("A.emit", "B.emit"), "entailed")

    def test_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError, "cyclic"):
            EventGraph(("a", "b"), (("a", "b"), ("b", "a")))

    def test_self_edge_duplicate_and_unknown_ref_rejected(self):
        for nodes, edges in [(("a", "b"), (("a", "a"),)),
                             (("a", "b"), (("a", "b"), ("a", "b"))),
                             (("a", "b"), (("a", "c"),))]:
            with self.assertRaises(ValueError):
                EventGraph(nodes, edges)

    def test_duplicate_nodes_rejected(self):
        with self.assertRaises(ValueError):
            EventGraph(("a", "a"), ())

    def test_oversize_oracle_refuses_factorial_explosion(self):
        graph = EventGraph(tuple(str(n) for n in range(9)), ())
        with self.assertRaisesRegex(ValueError, "at most 8"):
            list(graph.linear_extensions())

    def test_invalid_query_fails_closed(self):
        with self.assertRaises(ValueError):
            DEMO_GRAPH.order_claim("A.emit", "A.emit")
        with self.assertRaises(ValueError):
            DEMO_GRAPH.precedes("unknown", "A.emit")

    def test_deterministic_stereo_render_and_receipt(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            left = generate(Path(a))
            right = generate(Path(b))
            self.assertEqual(left, right)
            self.assertEqual(left["linear_extension_count"], 6)
            self.assertEqual((Path(a) / "linear-extensions.csv").read_bytes(),
                             (Path(b) / "linear-extensions.csv").read_bytes())
            self.assertEqual((Path(a) / "two-legal-tellings.wav").read_bytes(),
                             (Path(b) / "two-legal-tellings.wav").read_bytes())
            with wave.open(str(Path(a) / "two-legal-tellings.wav"), "rb") as sound:
                self.assertEqual(sound.getnchannels(), 2)
                self.assertEqual(sound.getframerate(), 22050)
                self.assertEqual(sound.getsampwidth(), 2)
                self.assertEqual(sound.getnframes(), left["audio"]["frames"])


if __name__ == "__main__":
    unittest.main()
