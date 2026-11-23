"""Tests for MHAC-X004's transparent corpus-archaeology baseline."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPEDITION = ROOT / "research" / "expeditions" / "intellectual-sediment"
sys.path.insert(0, str(EXPEDITION))

import sediment_atlas as atlas  # noqa: E402


class IntellectualSedimentAtlasTests(unittest.TestCase):
    def test_family_partition(self):
        self.assertEqual(atlas.family("docs/PROGRAMME.md"), "governance_foundations")
        self.assertEqual(atlas.family("research/analysis/brier/a.md"), "theory_analysis")
        self.assertEqual(atlas.family("research/protocol/a.md"), "method_novelty")
        self.assertEqual(atlas.family("research/sources/auditory/a.md"), "evidence_retrieval")
        self.assertEqual(atlas.family("research/expeditions/x/a.md"), "exploratory_research")

    def test_entropy_and_score_reward_dispersion(self):
        concentrated = {"a": 4}
        dispersed = {"a": 2, "b": 2}
        self.assertEqual(atlas.entropy(concentrated), 0.0)
        self.assertAlmostEqual(atlas.entropy(dispersed), 1.0)
        self.assertGreater(atlas.score(4, dispersed), atlas.score(4, concentrated))

    def test_markdown_cleaning_avoids_code_and_urls(self):
        tick = chr(96)
        text = (
            "meaning [repair](https://example.test/x) "
            + tick + "hidden_token" + tick + " "
            + tick * 3 + "secret field" + tick * 3
        )
        cleaned = atlas.clean(text)
        self.assertIn("meaning", cleaned)
        self.assertIn("repair", cleaned)
        self.assertNotIn("hidden_token", cleaned)
        self.assertNotIn("secret field", cleaned)
        self.assertNotIn("https", cleaned)

    def test_synthetic_bridge_and_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "research" / "analysis").mkdir(parents=True)
            (root / "research" / "expeditions" / "tiny").mkdir(parents=True)
            (root / "docs" / "a.md").write_text(
                "Observer context meaning. Distinguish state from action.", encoding="utf-8"
            )
            (root / "research" / "analysis" / "b.md").write_text(
                "Observer context meaning. Separate certainty from urgency.", encoding="utf-8"
            )
            (root / "research" / "expeditions" / "tiny" / "c.md").write_text(
                "Observer context meaning. Do not conflate frame with identity.", encoding="utf-8"
            )
            result = atlas.build(root)
            self.assertEqual(result["corpus"]["documents"], 3)
            phrases = {x["phrase"]: x for x in result["top_bridges"]}
            self.assertIn("observer", phrases)
            self.assertEqual(phrases["observer"]["family_count"], 3)
            self.assertGreater(result["style"]["totals"]["anti_collapse"], 0)

    def test_live_corpus_smoke_and_emit_summary(self):
        result = atlas.build(ROOT)
        self.assertGreaterEqual(result["corpus"]["documents"], 120)
        self.assertGreaterEqual(len(result["corpus"]["families"]), 5)
        self.assertGreaterEqual(
            result["motifs"]["meaning_semiosis"]["family_count"], 4
        )
        self.assertGreaterEqual(
            result["motifs"]["provenance_identity_authority"]["family_count"], 4
        )
        self.assertTrue(result["top_bridges"])
        self.assertEqual(len(result["corpus"]["sha256"]), 64)
        print("MHAC_X004_SUMMARY=" + json.dumps(atlas.ci(result), sort_keys=True))


if __name__ == "__main__":
    unittest.main()
