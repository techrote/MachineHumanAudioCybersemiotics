#!/usr/bin/env python3
"""MHAC-X002: deterministic symbolic coordinate-frame oracle (fictional, not human data).

Headings are toy compass bearings indexed clockwise N=0, E=1, S=2, W=3.
A phrase "left" interpreted in frame f requires action heading(f)-1 modulo 4.
Frames are recipient, emitter, and panel. A missing frame tag makes the action
set-valued; decision safety is a property of the *set*, not a psychological claim.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

DIRECTIONS = ("N", "E", "S", "W")
FRAMES = ("recipient", "emitter", "panel")
ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class Scene:
    recipient: int
    emitter: int
    panel: int

    def __post_init__(self) -> None:
        for f in FRAMES:
            h = getattr(self, f)
            if type(h) is not int or not 0 <= h < 4:
                raise ValueError(f"{f} heading must be integer 0..3")

    def rotate(self, quarter_turns: int) -> "Scene":
        if type(quarter_turns) is not int:
            raise TypeError("quarter_turns must be an integer")
        return Scene(*((getattr(self, f) + quarter_turns) % 4 for f in FRAMES))

    def with_rotation(self, frame: str, quarter_turns: int) -> "Scene":
        if frame not in FRAMES:
            raise ValueError("unknown reference frame")
        if type(quarter_turns) is not int:
            raise TypeError("quarter_turns must be an integer")
        values = {f: getattr(self, f) for f in FRAMES}
        values[frame] = (values[frame] + quarter_turns) % 4
        return Scene(**values)


def left_action(scene: Scene, frame: str) -> str:
    """Resolve a fictional command "left" relative to one explicit anchor."""
    if frame not in FRAMES:
        raise ValueError("explicit frame must be recipient/emitter/panel")
    return DIRECTIONS[(getattr(scene, frame) - 1) % 4]


def possible_actions(scene: Scene, frame: str | None = None) -> frozenset[str]:
    """All action directions consistent with a known scene and possible referents."""
    if frame is None:
        return frozenset(left_action(scene, f) for f in FRAMES)
    return frozenset((left_action(scene, frame),))


def action_equivalence(scene: Scene) -> bool:
    """Semantic referent may remain ambiguous, though world action is invariant."""
    return len(possible_actions(scene)) == 1


def guarded_policy(
    scene: Scene, frame: str | None = None, *, transform_current: bool = True
) -> str:
    """Artificial conservative policy. Stale transforms are a separate epistemic gate."""
    if not transform_current:
        return ABSTAIN
    outcomes = possible_actions(scene, frame)
    return next(iter(outcomes)) if len(outcomes) == 1 else ABSTAIN


def default_recipient_policy(scene: Scene) -> str:
    """Deliberately defective comparator: blindly assumes listener-relative left."""
    return left_action(scene, "recipient")


def encode(scene: Scene) -> dict[str, object]:
    truth = {frame: left_action(scene, frame) for frame in FRAMES}
    return {
        "headings": {frame: DIRECTIONS[getattr(scene, frame)] for frame in FRAMES},
        "required_action_by_frame": truth,
        "possible_actions_without_frame": sorted(possible_actions(scene)),
        "untagged_decision": guarded_policy(scene),
        "untagged_equivalent_action": action_equivalence(scene),
        "explicit_recipient_decision": guarded_policy(scene, "recipient"),
        "stale_recipient_decision": guarded_policy(
            scene, "recipient", transform_current=False
        ),
        "blind_recipient_default": default_recipient_policy(scene),
    }


def census() -> dict[str, object]:
    scenes = [Scene(*h) for h in itertools.product(range(4), repeat=3)]
    records = [encode(s) for s in scenes]
    ambiguous = sum(not action_equivalence(s) for s in scenes)
    correct_defaults = sum(
        default_recipient_policy(s) == left_action(s, true_frame)
        for s in scenes
        for true_frame in FRAMES
    )
    safe_untagged_true_actions = sum(
        guarded_policy(s) == left_action(s, true_frame)
        for s in scenes
        for true_frame in FRAMES
    )
    return {
        "classification": "fictional_exhaustive_enumeration",
        "headings": list(DIRECTIONS),
        "frames": list(FRAMES),
        "scene_count": len(scenes),
        "scene_frame_pairs": len(scenes) * len(FRAMES),
        "untagged_action_equivalent_scenes": len(scenes) - ambiguous,
        "untagged_action_ambiguous_scenes": ambiguous,
        "unguarded_default_correct_scene_frame_pairs": correct_defaults,
        "unguarded_default_wrong_scene_frame_pairs":
            len(scenes) * len(FRAMES) - correct_defaults,
        "guarded_untagged_correct_scene_frame_pairs": safe_untagged_true_actions,
        "guarded_untagged_abstained_scene_frame_pairs":
            len(scenes) * len(FRAMES) - safe_untagged_true_actions,
        "explicit_frame_correct_scene_frame_pairs": sum(
            guarded_policy(s, f) == left_action(s, f)
            for s in scenes for f in FRAMES
        ),
        "records": records,
    }


def canonical_bytes(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("utf-8")


def verify() -> dict[str, object]:
    data = census()
    expected = {
        "scene_count": 64,
        "scene_frame_pairs": 192,
        "untagged_action_equivalent_scenes": 4,
        "untagged_action_ambiguous_scenes": 60,
        "unguarded_default_correct_scene_frame_pairs": 96,
        "unguarded_default_wrong_scene_frame_pairs": 96,
        "guarded_untagged_correct_scene_frame_pairs": 12,
        "guarded_untagged_abstained_scene_frame_pairs": 180,
        "explicit_frame_correct_scene_frame_pairs": 192,
    }
    for key, val in expected.items():
        if data[key] != val:
            raise AssertionError((key, data[key], val))
    data_bytes = canonical_bytes(data)
    return {
        "enumeration": expected,
        "sha256_full_census_json": hashlib.sha256(data_bytes).hexdigest(),
        "note": "Synthetic mathematical enumeration; no real listeners/agents tested.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="recompute known-answer census and invariants")
    parser.add_argument("--out", type=Path, default=None,
                        help="optional disposable output directory (not canonical)")
    args = parser.parse_args()
    receipt = verify()
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "census.json").write_bytes(canonical_bytes(census()))
        (args.out / "receipt.json").write_bytes(canonical_bytes(receipt))
    if args.check or args.out is None:
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
