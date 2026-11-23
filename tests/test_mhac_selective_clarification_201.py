import importlib.util
from pathlib import Path
from itertools import product
import sys
import unittest

path = Path(__file__).resolve().parents[1] / "research/expeditions/selective-clarification/lab.py"
spec = importlib.util.spec_from_file_location("mhac_201_lab", path)
lab = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lab
spec.loader.exec_module(lab)


class SelectiveClarification(unittest.TestCase):
    def test_multiplexer(self):
        p = lab.multiplexer()
        opt = p.optimum()
        self.assertEqual(opt.cost, 2)
        self.assertEqual(opt.name, "mode")
        self.assertEqual(p.static()[0], 3)
        self.assertEqual(p.optimum(identify=True).cost, 4)
        self.assertEqual(p.static(identify=True)[0], 4)
        greedy = p.greedy()
        self.assertEqual(greedy.name, "ornament")
        self.assertGreater(greedy.cost, opt.cost)
        self.assertEqual(max(p.verify(opt)), 2)
        self.assertIsNone(p.optimum(budget=1))
        self.assertEqual(p.optimum(budget=2), opt)

    def test_overlap(self):
        p = lab.examples()["overlap"]
        self.assertEqual(p.optimum(), lab.Plan(0, "action", "b"))
        self.assertEqual(p.optimum(identify=True).cost, 1)
        self.assertEqual(p.static(), (0, ()))

    def test_pairwise_is_not_global(self):
        p = lab.examples()["pairwise_only"]
        self.assertTrue(all(p.common(pair) for pair in ((0,1),(1,2),(0,2))))
        self.assertFalse(p.common((0,1,2)))
        self.assertEqual(p.optimum().cost, 2)
        self.assertIsNone(p.optimum(budget=1))

    def test_impossibility_and_omitted_world(self):
        p = lab.examples()["unresolvable"]
        self.assertIsNone(p.optimum())
        self.assertIsNone(p.static())
        self.assertIsNone(p.greedy())
        q = lab.examples()["closed_world_trap"]
        sub = lab.Problem(q.worlds[:2], (("detail",1,("x","x")),))
        self.assertEqual(sub.optimum().cost, 0)
        self.assertIsNone(q.optimum())

    def test_expensive_decoy(self):
        p = lab.examples()["expensive_decoy"]
        self.assertEqual(p.optimum().cost, 1)
        self.assertEqual(p.greedy().cost, 9)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            lab.Problem((), ())
        with self.assertRaises(ValueError):
            lab.Problem((("a",frozenset()),), ())
        with self.assertRaises(ValueError):
            lab.Problem((("a",frozenset("a")),), (("q",0,("a",)),))
        with self.assertRaises(ValueError):
            lab.multiplexer().common(())
        with self.assertRaises(ValueError):
            lab.multiplexer().optimum(budget=-1)
        with self.assertRaises(ValueError):
            lab.multiplexer().verify(lab.Plan(0,"action","x"))

    def test_exhaustive_against_independent_budget_game(self):
        # 7^3 assignments of nonempty action subsets, times 8 partitions.
        # Compare to direct AND/OR enumeration at every budget 0..3.
        subsets = tuple(frozenset(a for i,a in enumerate("abc") if mask & (1<<i))
                        for mask in range(1,8))
        fixed = ("0","0","1")
        cases = 0
        for actions in product(subsets, repeat=3):
            for varying in product("01",repeat=3):
                p = lab.Problem(tuple((str(i),a) for i,a in enumerate(actions)),
                                (("fixed",1,fixed),("varying",2,varying)))
                def feasible(s, qs, budget):
                    # Intentionally independent of lab.common/split/optimum.
                    if any(all(a in actions[i] for i in s) for a in "abc"):
                        return True
                    for j in qs:
                        _, cost, ans = p.questions[j]
                        if cost > budget:
                            continue
                        children = tuple(tuple(i for i in s if ans[i] == v)
                                         for v in set(ans[i] for i in s))
                        if all(feasible(c, tuple(k for k in qs if k != j),
                                        budget-cost) for c in children):
                            return True
                    return False
                for b in range(4):
                    result = p.optimum(budget=b)
                    self.assertEqual(result is not None, feasible((0,1,2),(0,1),b))
                    if result is not None:
                        p.verify(result)
                cases += 1
        self.assertEqual(cases, 2744)

if __name__ == "__main__":
    unittest.main()
