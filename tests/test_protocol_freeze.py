"""MHAC-R002: the freeze record, the live stage declaration and the frozen bytes agree."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "research/protocol/FREEZE.md"
STATE = ROOT / "research/registry/state.json"
FROZEN = ("PROTOCOL-v1.md", "ANALYSIS_PLAN-v1.md", "GLOSSARY-v1.md")


def freeze_table(text: str) -> dict[str, str]:
    rows = re.findall(r"^\| \[([A-Z_]+-v1\.md)\]\([^)]+\) \| [\d,]+ \| `([0-9a-f]{64})` \|$", text, re.M)
    return dict(rows)


def declared(state: dict) -> dict[str, str]:
    gate = next(g for g in state["stage_gates"] if g["stage"] == "protocol")
    return {Path(a["path"]).name: a["sha256"] for a in gate["artifacts"]
            if a["path"].startswith("research/protocol/")}


class ProtocolFreezeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.freeze = freeze_table(FREEZE.read_text(encoding="utf-8"))
        self.state = json.loads(STATE.read_text(encoding="utf-8"))

    def test_freeze_record_lists_exactly_the_frozen_files(self) -> None:
        self.assertEqual(set(self.freeze), set(FROZEN))

    def test_freeze_record_matches_bytes_and_declaration(self) -> None:
        stage = declared(self.state)
        for name in FROZEN:
            actual = hashlib.sha256((ROOT / "research/protocol" / name).read_bytes()).hexdigest()
            self.assertEqual(self.freeze[name], actual, name)
            self.assertEqual(stage[name], actual, name)

    def test_protocol_stage_is_internal_and_limited(self) -> None:
        gate = next(g for g in self.state["stage_gates"] if g["stage"] == "protocol")
        self.assertEqual(gate["human_gate_refs"], [])
        self.assertIn("unregistered", gate["limitations"])
        self.assertIn("no human review", gate["limitations"])

    def test_mismatched_digest_is_detected(self) -> None:
        text = FREEZE.read_text(encoding="utf-8")
        name = FROZEN[0]
        tampered = text.replace(self.freeze[name], "0" * 64)
        self.assertNotEqual(freeze_table(tampered)[name], self.freeze[name])
        actual = hashlib.sha256((ROOT / "research/protocol" / name).read_bytes()).hexdigest()
        self.assertNotEqual(freeze_table(tampered)[name], actual)


if __name__ == "__main__":
    unittest.main()
