"""Adversarial tests of MHAC-X007's fictional parity instrument."""
import importlib.util
from itertools import combinations, product
from pathlib import Path
import tempfile
import unittest
import wave


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("choir", HERE / "choir.py")
choir = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = choir
spec.loader.exec_module(choir)
Edge = choir.Edge


class FrustratedChoirTests(unittest.TestCase):
    def test_ambiguous_absolute_assignment(self):
        graph = [Edge("ab", "A", "B", 1), Edge("bc", "B", "C", 0)]
        b = choir.brute_assignments(("A", "B", "C", "D"), graph)
        self.assertEqual(b["assignment_count"], 4)  # two components
        self.assertTrue(choir.analyse(("A", "B", "C", "D"), graph)["satisfiable"])

    def test_self_loops(self):
        yes = (Edge("s", "A", "A", 0),)
        no = (Edge("n", "A", "A", 1),)
        for edges, expected in ((yes, True), (no, False)):
            a = choir.analyse(("A",), edges)
            self.assertEqual(a["satisfiable"], expected)
            self.assertTrue(choir.verify_cycles(edges, a))
            self.assertEqual(a["cycles"][0].path_nodes, ("A",))
            self.assertEqual(a["cycles"][0].path_ids, ())

    def test_parallel_edges(self):
        edges = (Edge("one", "A", "B", 0), Edge("two", "A", "B", 1))
        a = choir.analyse(("A", "B"), edges)
        self.assertEqual(a["rejected"], ("two",))
        self.assertEqual(a["cycles"][0].path_ids, ("one",))
        self.assertEqual(a["cycles"][0].flux, 1)
        self.assertTrue(choir.verify_cycles(edges, a))

    def test_even_and_odd_triangle(self):
        good = (
            Edge("ab", "A", "B", 1), Edge("bc", "B", "C", 1),
            Edge("ca", "C", "A", 0),
        )
        bad = good[:2] + (Edge("ca", "C", "A", 1),)
        self.assertEqual(choir.cycle_notes(choir.analyse(("A", "B", "C"), good)), (0,))
        self.assertEqual(choir.cycle_notes(choir.analyse(("A", "B", "C"), bad)), (1,))
        self.assertEqual(choir.brute_assignments(("A", "B", "C"), good)["assignment_count"], 2)
        self.assertEqual(choir.brute_assignments(("A", "B", "C"), bad)["assignment_count"], 0)

    def test_order_controls_which_edge_is_rejected_not_satisfiability(self):
        edges = choir.FRUSTRATED
        reordered = (edges[3],) + edges[:3]
        first = choir.analyse(choir.VERTICES, edges)
        second = choir.analyse(choir.VERTICES, reordered)
        self.assertFalse(first["satisfiable"])
        self.assertFalse(second["satisfiable"])
        self.assertEqual(first["rejected"], ("e4",))
        self.assertEqual(second["rejected"], ("e3",))
        self.assertTrue(choir.verify_cycles(reordered, second))

    def test_greedy_rejection_is_not_minimum_repair(self):
        edges = (
            Edge("ab", "A", "B", 1),
            Edge("ac", "A", "C", 0),
            Edge("ad", "A", "D", 0),
            Edge("bc", "B", "C", 0),
            Edge("bd", "B", "D", 0),
            Edge("cd", "C", "D", 0),
        )
        a = choir.analyse(choir.VERTICES, edges)
        brute = choir.brute_assignments(choir.VERTICES, edges)
        self.assertEqual(len(a["rejected"]), 2)
        self.assertEqual(brute["minimum_unsatisfied_edges"], 1)
        self.assertTrue(choir.verify_cycles(edges, a))

    def test_forest_has_no_closed_loop_sound_and_is_satisfiable(self):
        edges = (Edge("ab", "A", "B", 1), Edge("bc", "B", "C", 1))
        analysis = choir.analyse(("A", "B", "C"), edges)
        self.assertEqual(analysis["cycles"], ())
        self.assertTrue(analysis["satisfiable"])
        self.assertEqual(choir.pcm_bytes(choir.cycle_notes(analysis)), b"")

    def test_invalid_records_fail_closed(self):
        invalid = [
            (("A",), [Edge("x", "A", "Q", 0)]),
            (("A",), [Edge("x", "A", "A", -1)]),
            (("A",), [Edge("x", "A", "A", True)]),
            (("A",), [Edge("x", "A", "A", 2)]),
            (("A",), [Edge("", "A", "A", 0)]),
            (("A",), [Edge("x", "A", "A", 0), Edge("x", "A", "A", 0)]),
            (("A", "A"), []),
            ((), []),
        ]
        for vertices, edges in invalid:
            with self.subTest(vertices=vertices, edges=edges):
                with self.assertRaises(ValueError):
                    choir.analyse(vertices, edges)
        with self.assertRaises(ValueError):
            choir.gauge_switch(choir.BALANCED, {"A": 1, "B": 0})
        with self.assertRaises(ValueError):
            choir.pcm_bytes([2])

    def test_729_graphs_vs_independent_exhaustive_assignments(self):
        vertices = choir.VERTICES
        pairs = tuple(combinations(vertices, 2))
        counts = {True: 0, False: 0}
        for statuses in product((-1, 0, 1), repeat=len(pairs)):
            edges = tuple(
                Edge(f"e{k}", a, b, p)
                for k, ((a, b), p) in enumerate(zip(pairs, statuses))
                if p >= 0
            )
            analysis = choir.analyse(vertices, edges)
            brute = choir.brute_assignments(vertices, edges)
            self.assertEqual(analysis["satisfiable"], brute["satisfiable"])
            self.assertTrue(choir.verify_cycles(edges, analysis))
            accepted = tuple(e for e in edges if e.id in analysis["accepted"])
            self.assertTrue(choir.brute_assignments(vertices, accepted)["satisfiable"])
            for rejected_id in analysis["rejected"]:
                added = accepted + tuple(e for e in edges if e.id == rejected_id)
                self.assertFalse(choir.brute_assignments(vertices, added)["satisfiable"])
            counts[analysis["satisfiable"]] += 1
        self.assertEqual(sum(counts.values()), 729)
        self.assertGreater(counts[True], 0)
        self.assertGreater(counts[False], 0)

    def test_all_16_gauge_switches_on_all_729_graphs(self):
        vertices = choir.VERTICES
        pairs = tuple(combinations(vertices, 2))
        for statuses in product((-1, 0, 1), repeat=len(pairs)):
            edges = tuple(
                Edge(f"e{k}", a, b, p)
                for k, ((a, b), p) in enumerate(zip(pairs, statuses))
                if p >= 0
            )
            original = choir.analyse(vertices, edges)
            for flip_bits in product((0, 1), repeat=4):
                flips = dict(zip(vertices, flip_bits))
                # Function switches only endpoints; isolated vertices are immaterial.
                localized = {v: flips[v] for e in edges for v in (e.u, e.v)}
                transformed = choir.gauge_switch(edges, localized)
                switched = choir.analyse(vertices, transformed)
                self.assertEqual(original["satisfiable"], switched["satisfiable"])
                self.assertEqual(original["rejected"], switched["rejected"])
                self.assertEqual(choir.cycle_notes(original), choir.cycle_notes(switched))
                self.assertTrue(choir.verify_cycles(transformed, switched))

    def test_cycle_tamper_detected(self):
        a = choir.analyse(choir.VERTICES, choir.FRUSTRATED)
        c = a["cycles"][0]
        forged = dict(a)
        forged["cycles"] = (choir.Cycle(c.closing_id, c.path_nodes, c.path_ids, c.inferred, c.declared, 0),)
        self.assertFalse(choir.verify_cycles(choir.FRUSTRATED, forged))

    def test_pcm_and_receipt_gauge_invariance(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = choir.generate(Path(temporary))
            paths = [Path(temporary) / f"{key}.wav" for key in result["scenarios"]]
            self.assertTrue(all(p.exists() for p in paths))
            with wave.open(str(paths[1]), "rb") as audio:
                self.assertEqual(audio.getnchannels(), 2)
                self.assertEqual(audio.getsampwidth(), 2)
                self.assertEqual(audio.getframerate(), 22050)
                self.assertEqual(audio.getnframes(), 13230)
            self.assertEqual(paths[1].read_bytes(), paths[2].read_bytes())
            self.assertNotEqual(paths[0].read_bytes(), paths[1].read_bytes())
            self.assertEqual(
                result["scenarios"]["frustrated"]["brute_force"]["assignment_count"], 0)
            self.assertEqual(
                result["scenarios"]["balanced"]["brute_force"]["assignment_count"], 2)
            self.assertTrue((Path(temporary) / "receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
