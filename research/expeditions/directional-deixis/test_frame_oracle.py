"""MHAC-X002 exhaustive syntactic and algebraic checks, not human listening tests."""
import hashlib
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame_oracle as m  # noqa: E402


class FrameOracleTests(unittest.TestCase):
    def test_bounded_census_and_reproducible_digest(self):
        receipt = m.verify()
        counts = receipt["enumeration"]
        self.assertEqual(counts["scene_count"], 64)
        self.assertEqual(counts["untagged_action_equivalent_scenes"], 4)
        self.assertEqual(counts["untagged_action_ambiguous_scenes"], 60)
        self.assertEqual(counts["unguarded_default_wrong_scene_frame_pairs"], 96)
        self.assertEqual(counts["guarded_untagged_abstained_scene_frame_pairs"], 180)
        self.assertEqual(counts["explicit_frame_correct_scene_frame_pairs"], 192)
        self.assertEqual(
            hashlib.sha256(m.canonical_bytes(m.census())).hexdigest(),
            receipt["sha256_full_census_json"],
        )
        self.assertEqual(m.canonical_bytes(m.census()), m.canonical_bytes(m.census()))

    def test_identical_surface_three_incompatible_correct_actions(self):
        # Same spoken "left", same visible headings, unknown intended frame.
        scene = m.Scene(0, 1, 2)
        self.assertEqual(m.left_action(scene, "recipient"), "W")
        self.assertEqual(m.left_action(scene, "emitter"), "N")
        self.assertEqual(m.left_action(scene, "panel"), "E")
        self.assertEqual(m.possible_actions(scene), frozenset(("W", "N", "E")))
        self.assertEqual(m.guarded_policy(scene), m.ABSTAIN)

    def test_action_equivalence_does_not_establish_reference_agreement(self):
        scene = m.Scene(2, 2, 2)
        self.assertTrue(m.action_equivalence(scene))
        self.assertEqual(m.guarded_policy(scene), "E")
        # Three distinct frame hypotheses remain semantically possible.
        self.assertEqual(len(m.FRAMES), 3)
        self.assertEqual(m.guarded_policy(scene, transform_current=False), m.ABSTAIN)

    def test_full_rotation_equivariance_for_each_explicit_frame(self):
        for headings in itertools.product(range(4), repeat=3):
            s = m.Scene(*headings)
            for k in range(4):
                rotated = s.rotate(k)
                expected = {
                    m.DIRECTIONS[(m.DIRECTIONS.index(d) + k) % 4]
                    for d in m.possible_actions(s)
                }
                self.assertEqual(m.possible_actions(rotated), expected)
                for f in m.FRAMES:
                    direction = m.left_action(s, f)
                    actual = m.left_action(rotated, f)
                    self.assertEqual(
                        actual, m.DIRECTIONS[(m.DIRECTIONS.index(direction) + k) % 4]
                    )
                decision = m.guarded_policy(s)
                rotated_decision = m.guarded_policy(rotated)
                if decision == m.ABSTAIN:
                    self.assertEqual(rotated_decision, m.ABSTAIN)
                else:
                    self.assertEqual(
                        rotated_decision,
                        m.DIRECTIONS[(m.DIRECTIONS.index(decision) + k) % 4],
                    )

    def test_only_selected_anchor_affects_explicit_direction(self):
        for headings in itertools.product(range(4), repeat=3):
            s = m.Scene(*headings)
            for f in m.FRAMES:
                original = m.left_action(s, f)
                for other in m.FRAMES:
                    for k in range(4):
                        updated = s.with_rotation(other, k)
                        if other != f:
                            self.assertEqual(original, m.left_action(updated, f))
                        else:
                            expected = m.DIRECTIONS[(m.DIRECTIONS.index(original) + k) % 4]
                            self.assertEqual(expected, m.left_action(updated, f))

    def test_tag_is_not_sufficient_when_transform_untrusted(self):
        s = m.Scene(0, 1, 2)
        for f in m.FRAMES:
            self.assertEqual(m.guarded_policy(s, f), m.left_action(s, f))
            self.assertEqual(
                m.guarded_policy(s, f, transform_current=False), m.ABSTAIN
            )

    def test_unknown_frame_and_invalid_headings_fail_closed(self):
        s = m.Scene(0, 1, 2)
        for f in ("", "speaker", "world", "out-of-band"):
            with self.assertRaises(ValueError):
                m.left_action(s, f)
            with self.assertRaises(ValueError):
                m.possible_actions(s, f)
        for bad in (-1, 4, 2.5, True, "N"):
            with self.assertRaises(ValueError):
                m.Scene(bad, 0, 0)
        with self.assertRaises(TypeError):
            s.rotate(0.5)
        with self.assertRaises(ValueError):
            s.with_rotation("wrong", 1)

    def test_counterexample_to_frame_tag_necessity(self):
        # No frame identity is known, yet all candidate actions coincide.
        self.assertEqual(m.guarded_policy(m.Scene(0, 0, 0)), "W")
        # Known tag can still result in a wrong action if the world heading is
        # invalid or old; the policy requires external temporal/source checks.
        self.assertEqual(
            m.guarded_policy(m.Scene(0, 0, 0), "recipient", transform_current=False),
            m.ABSTAIN,
        )

    def test_different_frame_hypotheses_not_laundered_into_listener_data(self):
        data = m.census()
        self.assertEqual(data["classification"], "fictional_exhaustive_enumeration")
        self.assertEqual(len(data["records"]), 64)
        for record in data["records"]:
            self.assertEqual(
                record["untagged_equivalent_action"],
                len(record["possible_actions_without_frame"]) == 1,
            )
            self.assertEqual(record["stale_recipient_decision"], m.ABSTAIN)


if __name__ == "__main__":
    unittest.main()
