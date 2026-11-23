#!/usr/bin/env python3
"""X003: a finite causal-order oracle and an explicitly fictional stereo score.

Standard library only. A graph edge represents an *asserted* causal dependency;
absence of an edge is not evidence that full real-world telemetry was captured.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class EventGraph:
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.nodes or len(self.nodes) != len(set(self.nodes)):
            raise ValueError("nodes must be nonempty and unique")
        if any(not isinstance(n, str) or not n for n in self.nodes):
            raise ValueError("node IDs must be nonempty strings")
        if len(self.edges) != len(set(self.edges)):
            raise ValueError("duplicate dependency edge")
        for source, target in self.edges:
            if source not in self.nodes or target not in self.nodes or source == target:
                raise ValueError("invalid or self-loop dependency edge")
        if not self._acyclic():
            raise ValueError("cyclic graph has no causal serialization")

    def _acyclic(self) -> bool:
        parents = {n: set() for n in self.nodes}
        for source, target in self.edges:
            parents[target].add(source)
        done = set()
        while len(done) < len(self.nodes):
            ready = next((n for n in self.nodes if n not in done and parents[n] <= done), None)
            if ready is None:
                return False
            done.add(ready)
        return True

    def precedes(self, source: str, target: str) -> bool:
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("unregistered event ID")
        if source == target:
            return False
        seen = set()
        stack = [source]
        while stack:
            node = stack.pop()
            for a, b in self.edges:
                if a == node and b not in seen:
                    if b == target:
                        return True
                    seen.add(b)
                    stack.append(b)
        return False

    def order_claim(self, source: str, target: str) -> str:
        """Classification for *causal* before, conditional on declared edges."""
        if source not in self.nodes or target not in self.nodes or source == target:
            raise ValueError("distinct registered IDs required")
        if self.precedes(source, target):
            return "entailed"
        if self.precedes(target, source):
            return "contradicted"
        return "not_entailed_either_way"

    def linear_extensions(self) -> Iterator[tuple[str, ...]]:
        """Enumerate all valid serial orders; deliberately refuse factorial blowups."""
        if len(self.nodes) > 8:
            raise ValueError("finite exhaustive oracle supports at most 8 events")
        parents = {n: set() for n in self.nodes}
        for source, target in self.edges:
            parents[target].add(source)

        def visit(prefix: tuple[str, ...]) -> Iterator[tuple[str, ...]]:
            if len(prefix) == len(self.nodes):
                yield prefix
                return
            placed = set(prefix)
            for node in self.nodes:
                if node not in placed and parents[node] <= placed:
                    yield from visit(prefix + (node,))

        yield from visit(())

    def witnesses(self, first: str, second: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if self.order_claim(first, second) != "not_entailed_either_way":
            raise ValueError("reversal witnesses require an incomparable pair")
        left = right = None
        for order in self.linear_extensions():
            if order.index(first) < order.index(second) and left is None:
                left = order
            if order.index(second) < order.index(first) and right is None:
                right = order
            if left is not None and right is not None:
                return left, right
        raise AssertionError("missing witness for incomparable pair in a DAG")


DEMO_GRAPH = EventGraph(
    ("A.sense", "A.emit", "B.sense", "B.emit", "M.combine"),
    (("A.sense", "A.emit"), ("B.sense", "B.emit"),
     ("A.emit", "M.combine"), ("B.emit", "M.combine")),
)
PITCH_HZ = {"A.sense": 220, "A.emit": 277, "B.sense": 330,
            "B.emit": 392, "M.combine": 523}


def score_audio(path: Path, first: tuple[str, ...], second: tuple[str, ...]) -> dict:
    """Stereo PCM16: LEFT and RIGHT are *alternative* linearizations.

    Stereo coincidence is NOT a claim that fictional events were simultaneous.
    Pitches, tempo and channel mapping are declared artistic conventions.
    """
    sample_rate = 22050
    step = 0.32
    sounding = 0.22
    n_step = round(sample_rate * step)
    n_on = round(sample_rate * sounding)
    n_total = (len(first) + 1) * n_step
    tracks = []
    for ordering in (first, second):
        track = [0] * n_total
        for index, event in enumerate(ordering):
            hz = PITCH_HZ[event]
            for j in range(n_on):
                attack = min(1.0, j / (sample_rate * 0.012))
                release = min(1.0, (n_on - 1 - j) / (sample_rate * 0.025))
                amp = 0.22 * min(attack, release)
                t = j / sample_rate
                tone = math.sin(2 * math.pi * hz * t) + 0.18 * math.sin(4 * math.pi * hz * t)
                track[index * n_step + j] = round(32767 * amp * tone / 1.18)
        tracks.append(track)
    payload = b"".join(struct.pack("<hh", l, r) for l, r in zip(*tracks))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(payload)
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "sample_rate": sample_rate, "channels": 2, "sample_width_bytes": 2,
            "frames": n_total, "duration_seconds": round(n_total / sample_rate, 5)}


def generate(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    graph = DEMO_GRAPH
    first, second = graph.witnesses("A.emit", "B.emit")
    all_orders = list(graph.linear_extensions())
    with (out / "linear-extensions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("extension", "position_A_emit", "position_B_emit", "sequence"))
        for number, order in enumerate(all_orders, 1):
            writer.writerow((number, order.index("A.emit") + 1,
                             order.index("B.emit") + 1, " ".join(order)))
    audio = score_audio(out / "two-legal-tellings.wav", first, second)
    result = {
        "status": "original_synthetic_only",
        "hypothesis": "sequential audible presentation is not proof of causal precedence",
        "nodes": list(graph.nodes), "edges": [list(e) for e in graph.edges],
        "tested_pair": ["A.emit", "B.emit"],
        "causal_order_claim": graph.order_claim("A.emit", "B.emit"),
        "linear_extension_count": len(all_orders),
        "left_channel_order": list(first), "right_channel_order": list(second),
        "audio": audio,
        "limitations": ["unverified completeness of real telemetry", "no listener study",
                        "no physical timestamps", "arbitrary sound-to-event mapping"],
    }
    (out / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/mhac-x003"))
    args = parser.parse_args()
    print(json.dumps(generate(args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
