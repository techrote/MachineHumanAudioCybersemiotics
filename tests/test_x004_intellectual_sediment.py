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
import shadow_sediment as shadow  # noqa: E402
import distinction_miner as distinctions  # noqa: E402
import atlas_diff  # noqa: E402


class IntellectualSedimentAtlasTests(unittest.TestCase):
    def test_atlas_excludes_its_own_research_bundle(self):
        self.assertFalse(atlas.eligible(
            "research/expeditions/intellectual-sediment/README.md"
        ))
        self.assertTrue(atlas.eligible(
            "research/expeditions/observers-solecism/README.md"
        ))

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
            (root / "docs" / "a2.md").write_text(
                "Observer context meaning. Keep state distinct from action.", encoding="utf-8"
            )
            (root / "research" / "analysis" / "b.md").write_text(
                "Observer context meaning. Separate certainty from urgency.", encoding="utf-8"
            )
            (root / "research" / "expeditions" / "tiny" / "c.md").write_text(
                "Observer context meaning. Do not conflate frame with identity.", encoding="utf-8"
            )
            result = atlas.build(root)
            self.assertEqual(result["corpus"]["documents"], 4)
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


    def test_shadow_archive_synthetic_git_branch(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-b", "main", str(root)], check=True,
                           capture_output=True, text=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email",
                            "x004@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name",
                            "MHAC X004 fixture"], check=True)
            (root / "README.md").write_text("meaning context\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "main"],
                           check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", str(root), "checkout", "-b", "shadow"],
                           check=True, capture_output=True, text=True)
            note = root / "research" / "tangents" / "ghost" / "NOTE.md"
            note.parent.mkdir(parents=True)
            note.write_text("observer uncertainty repair context\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "shadow note"],
                           check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", str(root), "checkout", "main"],
                           check=True, capture_output=True, text=True)
            result = shadow.analyze_shadow(root)
            self.assertEqual(result["branch_or_history_only_paths"], 1)
            self.assertEqual(result["witnesses_loaded"], 1)
            self.assertEqual(result["unique_content_blobs"], 1)
            self.assertEqual(result["duplicate_content_paths"], 0)
            self.assertGreater(result["unique_content_words"], 0)
            self.assertEqual(
                result["high_motif_witnesses"][0]["path"],
                "research/tangents/ghost/NOTE.md",
            )
            self.assertIn("uncertainty_epistemics",
                          result["high_motif_witnesses"][0]["motifs"])

    def test_live_shadow_archive_emits_summary(self):
        result = shadow.analyze_shadow(ROOT, max_docs=400)
        self.assertGreaterEqual(result["historical_markdown_paths"],
                                result["current_markdown_paths"])
        self.assertGreater(result["branch_or_history_only_paths"], 0)
        self.assertGreater(result["witnesses_loaded"], 0)
        compact = {
            key: result[key]
            for key in (
                "head_sha", "historical_markdown_paths", "current_markdown_paths",
                "branch_or_history_only_paths", "witnesses_loaded",
                "unique_content_blobs", "duplicate_content_paths",
                "total_path_words", "unique_content_words", "truncated",
                "families", "fine_families", "latest_content_dates",
                "refs_by_witness_count", "motif_documents", "motif_hits",
                "high_motif_witnesses",
            )
        }
        print("MHAC_X004_SHADOW=" + json.dumps(compact, sort_keys=True))


    def test_distinction_miner_extracts_pairs_and_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "a.md").write_text(
                "Distinguish urgency from hazard. A receipt is not the same as resolution.\n"
                "Do not conflate source identity with action authority.\n",
                encoding="utf-8",
            )
            result = distinctions.build(root)
            self.assertGreaterEqual(result["summary"]["records"], 3)
            pairs = [r for r in result["records"] if r["paired"]]
            self.assertTrue(any(r["kind"] == "distinguish_from" for r in pairs))
            self.assertTrue(any(r["kind"] == "not_same_as" for r in pairs))
            self.assertTrue(any(r["kind"] == "do_not_conflate"
                                for r in result["records"]))

    def test_live_distinction_ledger_emits_summary(self):
        result = distinctions.build(ROOT)
        self.assertGreater(result["summary"]["records"], 50)
        self.assertGreater(result["summary"]["paired_records"], 10)
        self.assertGreaterEqual(len(result["summary"]["families"]), 5)
        print("MHAC_X004_DISTINCTIONS=" +
              json.dumps(result["summary"], sort_keys=True))


    def test_snapshot_diff_reports_growth_and_bridge_churn(self):
        before = {
            "head_sha": "a",
            "corpus": {"documents": 2, "words": 100,
                       "families": {"exploratory_research": 1}},
            "style": {"by_family": {
                "exploratory_research": {
                    "anti_collapse": {"per_1000": 1.0}
                }
            }},
            "motifs": {
                "meaning_semiosis": {
                    "documents": 1, "family_count": 1,
                    "families": {"exploratory_research": 1}
                }
            },
            "top_bridges": [{"phrase": "old bridge"}],
            "sparse_bridges": [],
        }
        after = {
            "head_sha": "b",
            "corpus": {"documents": 4, "words": 180,
                       "families": {"exploratory_research": 3}},
            "style": {"by_family": {
                "exploratory_research": {
                    "anti_collapse": {"per_1000": 1.5}
                }
            }},
            "motifs": {
                "meaning_semiosis": {
                    "documents": 3, "family_count": 1,
                    "families": {"exploratory_research": 3}
                }
            },
            "top_bridges": [{"phrase": "new bridge"}],
            "sparse_bridges": [{"phrase": "rare bridge"}],
        }
        result = atlas_diff.compare(before, after)
        self.assertEqual(result["corpus"]["documents"], 2)
        self.assertEqual(result["corpus"]["words"], 80)
        self.assertAlmostEqual(
            result["style_per_1000_deltas"]["exploratory_research"]
                  ["anti_collapse"], 0.5
        )
        self.assertEqual(
            result["motif_deltas"]["meaning_semiosis"]["documents"], 2
        )
        self.assertEqual(result["bridges"]["new_top"], ["new bridge"])
        self.assertEqual(result["bridges"]["lost_top"], ["old bridge"])


if __name__ == "__main__":
    unittest.main()
