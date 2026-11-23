#!/usr/bin/env python3
"""MHAC-X006: a deterministic, deliberately limited chiastic audio instrument.

The acoustic alphabet is independent of the interpretation of an event label.
Two interpretations can therefore have byte-identical ABBA audio and different
state transitions. This is a constructed witness, not a human-listening study.
Only Python's standard library is used.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
import struct
from typing import Mapping, Sequence
import wave

ALPHABET = frozenset(("A", "B"))
CHI = ("A", "B", "B", "A")
SAMPLE_RATE = 16000
TONE_FRAMES = 3200
GAP_FRAMES = 800

# State is one of {0, 1, 2}. A permutation is represented by a tuple giving
# the image of each element. Two transpositions need not commute.
INVOLUTIVE_ACTIONS: dict[str, tuple[int, ...]] = {
    "A": (1, 0, 2),  # interchange 0 and 1
    "B": (0, 2, 1),  # interchange 1 and 2
}
NONINVOLUTIVE_ACTIONS: dict[str, tuple[int, ...]] = {
    "A": (1, 2, 0),  # advance 0->1->2->0
    "B": (0, 2, 1),
}
# A third interpretation keeps its codebook fixed but is state-dependent:
# the same audible phrase closes state 3, but moves states 0, 1, 2.
CONDITIONAL_ACTIONS: dict[str, tuple[int, ...]] = {
    "A": (1, 2, 0, 3),
    "B": (0, 2, 1, 3),
}
PITCHES = {"A": (293.66, 587.33), "B": (440.0, 659.25)}


def is_palindrome(tokens: Sequence[str]) -> bool:
    """A spelling-level property only. Does not certify rhetoric or state."""
    return tuple(tokens) == tuple(reversed(tokens))


def is_permutation(action: Sequence[int]) -> bool:
    return tuple(sorted(action)) == tuple(range(len(action)))


def validate_actions(actions: Mapping[str, Sequence[int]]) -> int:
    if set(actions) != ALPHABET:
        raise ValueError("actions must supply precisely A and B")
    n = len(actions["A"])
    if n < 2 or any(len(x) != n or not is_permutation(x) for x in actions.values()):
        raise ValueError("all actions must be permutations of the same finite state set")
    return n


def execute(
    tokens: Sequence[str], actions: Mapping[str, Sequence[int]], state: int
) -> int:
    n = validate_actions(actions)
    if not isinstance(state, int) or not (0 <= state < n):
        raise ValueError("state outside the finite model")
    for token in tokens:
        if token not in ALPHABET:
            raise ValueError("unknown token")
        state = actions[token][state]
    return state


def effects(
    tokens: Sequence[str], actions: Mapping[str, Sequence[int]]
) -> tuple[int, ...]:
    return tuple(execute(tokens, actions, i) for i in range(validate_actions(actions)))


def is_identity(
    tokens: Sequence[str], actions: Mapping[str, Sequence[int]]
) -> bool:
    return effects(tokens, actions) == tuple(range(validate_actions(actions)))


def involution(action: Sequence[int]) -> bool:
    if not is_permutation(action):
        raise ValueError("expected a permutation")
    return all(action[action[i]] == i for i in range(len(action)))


def commute(actions: Mapping[str, Sequence[int]]) -> bool:
    """True iff AB(s) == BA(s) for every state in the finite model."""
    validate_actions(actions)
    return effects(("A", "B"), actions) == effects(("B", "A"), actions)


def state_history(
    tokens: Sequence[str], actions: Mapping[str, Sequence[int]], state: int
) -> list[int]:
    validate_actions(actions)
    out = [state]
    for t in tokens:
        state = execute((t,), actions, state)
        out.append(state)
    return out


def render_pcm(tokens: Sequence[str]) -> bytes:
    """An original two-register stereo study. No external recordings or melody.

    All samples are deterministic. The rendering uses only token names,
    independent of an operation's intended meaning or resulting state.
    """
    frames = bytearray()
    for token in tokens:
        if token not in PITCHES:
            raise ValueError("unrecognised acoustic token")
        left_hz, right_hz = PITCHES[token]
        for i in range(TONE_FRAMES):
            # Short linear fades suppress hard-cut clicks.
            ramp = min(1.0, i / 96.0, (TONE_FRAMES - i - 1) / 96.0)
            l = int(round(10500 * ramp * math.sin(2 * math.pi * left_hz * i / SAMPLE_RATE)))
            r = int(round(10500 * ramp * math.sin(2 * math.pi * right_hz * i / SAMPLE_RATE)))
            frames.extend(struct.pack("<hh", l, r))
        frames.extend(bytes(GAP_FRAMES * 4))
    return bytes(frames)


def render_wav(tokens: Sequence[str]) -> bytes:
    bio = BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(render_pcm(tokens))
    return bio.getvalue()


def provenance_record(
    name: str, actions: Mapping[str, Sequence[int]],
    tokens: Sequence[str] = CHI
) -> dict:
    n = validate_actions(actions)
    data = render_wav(tokens)
    return {
        "schema": "mhac-x006-chiastic-trap-v1",
        "name": name,
        "token_sequence": list(tokens),
        "acoustic_palindrome_at_token_level": is_palindrome(tokens),
        "event_functions": {k: list(v) for k, v in sorted(actions.items())},
        "state_count": n,
        "effects_all_states": list(effects(tokens, actions)),
        "returns_every_state": is_identity(tokens, actions),
        "a_is_involution": involution(actions["A"]),
        "b_is_involution": involution(actions["B"]),
        "a_b_commute": commute(actions),
        "state_history_from_zero": state_history(tokens, actions, 0),
        "wav_sha256": sha256(data).hexdigest(),
        "wav_bytes": len(data),
        "sample_rate_hz": SAMPLE_RATE,
        "channels": 2,
        "audio_is_semantically_untyped": True,
    }


def run_lab(directory: Path) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    cases = (
        ("closed_involutions", INVOLUTIVE_ACTIONS),
        ("open_rotation", NONINVOLUTIVE_ACTIONS),
        ("conditional_four_states", CONDITIONAL_ACTIONS),
    )
    records = []
    for name, actions in cases:
        wav_data = render_wav(CHI)
        (directory / (name + ".wav")).write_bytes(wav_data)
        record = provenance_record(name, actions)
        (directory / (name + ".json")).write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        records.append(record)
    comparison = {
        "schema": "mhac-x006-chiastic-trap-v1",
        "acoustic_tokens": list(CHI),
        "rendered_byte_identity": (
            (directory / "closed_involutions.wav").read_bytes()
            == (directory / "open_rotation.wav").read_bytes()
        ),
        "effect_identity": records[0]["effects_all_states"]
                           == records[1]["effects_all_states"],
        "all_three_wavs_identical": len({
            (directory / (name + ".wav")).read_bytes() for name, _ in cases
        }) == 1,
        "closed_case": records[0],
        "open_case": records[1],
        "conditional_case": records[2],
        "conditional_returning_states": [
            state for state, image in enumerate(records[2]["effects_all_states"])
            if state == image
        ],
        "nonpalindromic_identity_witness": {
            "tokens": ["A", "A", "B", "B"],
            "is_palindrome": is_palindrome(("A", "A", "B", "B")),
            "returns_every_state": is_identity(("A", "A", "B", "B"), INVOLUTIVE_ACTIONS),
        },
        "noncommutativity_control": {
            "tokens": ["A", "B", "A", "B"],
            "is_palindrome": is_palindrome(("A", "B", "A", "B")),
            "returns_every_state": is_identity(("A", "B", "A", "B"), INVOLUTIVE_ACTIONS),
        },
        "limits": [
            "Identical audio does not imply identical machine action.",
            "Token palindrome is not proof of intentional human rhetorical figure.",
            "State-return is proved only for three explicit finite states and actions.",
            "No listener hearing, comprehension, safety or emotional response was measured.",
            "This audio does not reproduce any existing composition.",
        ],
    }
    (directory / "comparative-report.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=Path("build/mhac-x006"),
        help="directory for generated WAV and JSON evidence"
    )
    args = parser.parse_args()
    out = run_lab(args.out)
    print(json.dumps({
        "rendered_byte_identity": out["rendered_byte_identity"],
        "effect_identity": out["effect_identity"],
        "all_three_wavs_identical": out["all_three_wavs_identical"],
        "conditional_effects": out["conditional_case"]["effects_all_states"],
        "conditional_returning_states": out["conditional_returning_states"],
        "closed_effects": out["closed_case"]["effects_all_states"],
        "open_effects": out["open_case"]["effects_all_states"],
        "a_b_commute": out["closed_case"]["a_b_commute"],
        "wav_sha256": out["closed_case"]["wav_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
