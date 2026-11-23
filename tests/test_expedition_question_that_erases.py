"""Independent test bridge for the destructive observation expedition."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "research/expeditions/question-that-erases/oracle.py"
SPEC = importlib.util.spec_from_file_location("question_that_erases", PATH)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class TestQuestionThatErases(unittest.TestCase):
    def setUp(self):
        self.codes = {"A": (1,0), "B": (0,1), "C": (0,0)}
        self.once = M.read_once(self.codes)
        self.keep = M.read_once(self.codes, True)
        self.b = M.belief(self.codes)

    def test_initial_vs_current(self):
        self.assertIsNone(M.solve(self.once,self.b)["depth"])
        self.assertEqual(M.solve(self.once,self.b,"current")["depth"],1)
        self.assertEqual(M.solve(self.keep,self.b)["depth"],2)

    def test_pairwise(self):
        for pair in ("AB","AC","BC"):
            self.assertEqual(M.solve(self.once,M.belief(pair))["depth"],1)

    def test_three_and_four_candidate_families(self):
        for n,total in ((3,64),(4,256)):
            self.assertEqual(M.enumerate_family(n),{
                "total":total,"pairwise":24,"read_once":0,
                "persistent":24,"gap":24})

    def test_adaptive_admissibility(self):
        t=M.adaptive_example()
        r=M.solve(t,M.belief("ABCD"))
        self.assertEqual(r["depth"],2)
        self.assertEqual(r["policy"][r["root"]],"split")
        children=r["graph"][r["root"]]["split"]
        self.assertEqual(r["policy"][children["left"]],"left")
        self.assertEqual(r["policy"][children["right"]],"right")
        self.assertIsNone(M.branches(t,children["right"],"left"))
        self.assertIsNone(M.branches(t,children["left"],"right"))

    def test_noninformative_transition_can_be_essential(self):
        t={("A","prepare"):("same","X"),("B","prepare"):("same","Y"),
           ("X","read"):("0","spent"),("Y","read"):("1","spent")}
        r=M.solve(t,M.belief("AB"))
        self.assertEqual(r["depth"],2)
        self.assertEqual(r["policy"][r["root"]],"prepare")

    def test_loop_is_not_a_solution(self):
        t={("A","loop"):("same","A"),("B","loop"):("same","B")}
        self.assertIsNone(M.solve(t,M.belief("AB"))["depth"])

    def test_single_candidate_terminal_and_forbidden(self):
        self.assertEqual(M.solve({},M.belief("A"))["depth"],0)
        self.assertIsNone(M.solve({},M.belief("AB"))["depth"])
        t={("A","q"):("yes","A")}
        self.assertIsNone(M.solve(t,M.belief("AB"))["depth"])

    def test_audio_negative_control(self):
        q=("q0","q1")
        tb,_=M.execute(self.once,"B",q)
        tc,_=M.execute(self.once,"C",q)
        pb,_=M.execute(self.keep,"B",q)
        pc,_=M.execute(self.keep,"C",q)
        self.assertEqual(tb,tc)
        self.assertEqual(M.pcm(tb),M.pcm(tc))
        self.assertNotEqual(M.pcm(pb),M.pcm(pc))
        self.assertEqual(len(M.pcm(tb)),9600)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): M.solve({},())
        with self.assertRaises(ValueError): M.solve({},(("A","A"),("A","B")))
        with self.assertRaises(ValueError): M.read_once({"A":(2,)})


if __name__=="__main__":
    unittest.main()
