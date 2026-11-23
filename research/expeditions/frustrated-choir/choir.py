#!/usr/bin/env python3
"""MHAC-X007: finite signed-graph certificates and original parity-loop audio.

Pure Python 3.11+ standard library. All inputs/examples are fictional binary
relations; this program does not establish source truth or human audibility.
"""
from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Sequence
import argparse
import json
import math
import struct
import wave


@dataclass(frozen=True)
class Edge:
    id: str
    u: str
    v: str
    parity: int  # 0: same; 1: different


@dataclass(frozen=True)
class Cycle:
    closing_id: str
    path_nodes: tuple[str, ...]
    path_ids: tuple[str, ...]
    inferred: int
    declared: int
    flux: int  # XOR around the closed walk; 0 balanced, 1 frustrated


def validate(vertices: Sequence[str], edges: Sequence[Edge]) -> None:
    if not vertices or len(vertices) != len(set(vertices)):
        raise ValueError("vertices must be nonempty and unique")
    if any(not isinstance(v, str) or not v for v in vertices):
        raise ValueError("vertex labels must be nonempty strings")
    ids = set()
    for edge in edges:
        if (not isinstance(edge.id, str) or not edge.id
                or edge.id in ids):
            raise ValueError("edge IDs must be nonempty and unique")
        ids.add(edge.id)
        if edge.u not in vertices or edge.v not in vertices:
            raise ValueError("edge endpoint not declared")
        if type(edge.parity) is not int or edge.parity not in (0, 1):
            raise ValueError("parity must be integer zero or one")


def shortest_path(adj: dict, start: str, goal: str):
    """Shortest edge-count path through previously accepted edges."""
    queue = deque([start])
    previous = {start: None}
    while queue:
        here = queue.popleft()
        if here == goal:
            break
        for nxt, edge in adj[here]:
            if nxt not in previous:
                previous[nxt] = (here, edge)
                queue.append(nxt)
    if goal not in previous:
        return None
    nodes = [goal]
    selected = []
    at = goal
    while at != start:
        parent, edge = previous[at]
        selected.append(edge)
        at = parent
        nodes.append(at)
    return tuple(reversed(nodes)), tuple(reversed(selected))


def analyse(vertices: Sequence[str], edges: Sequence[Edge]) -> dict:
    """Accept a maximal *inclusion-wise* consistent prefix-order subset.

    A rejected edge has a verified inconsistent cycle relative to accepted
    edges. Rejection counts are order-dependent and are NOT optimal repairs.
    """
    validate(vertices, edges)
    adj = {v: [] for v in vertices}
    accepted: list[Edge] = []
    rejected: list[str] = []
    cycles: list[Cycle] = []
    for edge in edges:
        found = shortest_path(adj, edge.u, edge.v)
        if found is not None:
            nodes, path_edges = found
            inferred = 0
            for link in path_edges:
                inferred ^= link.parity
            flux = inferred ^ edge.parity
            cycles.append(Cycle(
                edge.id, nodes, tuple(x.id for x in path_edges),
                inferred, edge.parity, flux))
            if flux:
                rejected.append(edge.id)
                continue
        accepted.append(edge)
        adj[edge.u].append((edge.v, edge))
        if edge.u != edge.v:
            adj[edge.v].append((edge.u, edge))
    return {
        "vertices": tuple(vertices),
        "edges": tuple(edges),
        "accepted": tuple(x.id for x in accepted),
        "rejected": tuple(rejected),
        "cycles": tuple(cycles),
        "satisfiable": not rejected,
    }


def verify_cycles(edges: Sequence[Edge], analysis: dict) -> bool:
    """Independent path-and-parity verification of all emitted certificates."""
    table = {e.id: e for e in edges}
    accepted_so_far = set()
    cycles_by_closing = {c.closing_id: c for c in analysis["cycles"]}
    if len(cycles_by_closing) != len(analysis["cycles"]):
        return False
    for edge in edges:
        cycle = cycles_by_closing.get(edge.id)
        if cycle is not None:
            if (len(cycle.path_nodes) != len(cycle.path_ids) + 1
                    or cycle.path_nodes[0] != edge.u
                    or cycle.path_nodes[-1] != edge.v):
                return False
            parity = 0
            for a, b, edge_id in zip(
                cycle.path_nodes, cycle.path_nodes[1:], cycle.path_ids
            ):
                if edge_id not in accepted_so_far:
                    return False
                link = table[edge_id]
                if {a, b} != {link.u, link.v}:
                    return False
                parity ^= link.parity
            if (parity != cycle.inferred or
                    cycle.declared != edge.parity or
                    cycle.flux != (parity ^ edge.parity)):
                return False
            if (cycle.flux == 1) != (edge.id in analysis["rejected"]):
                return False
        if edge.id not in analysis["rejected"]:
            accepted_so_far.add(edge.id)
        elif cycle is None:
            return False
    return True


def brute_assignments(vertices: Sequence[str], edges: Sequence[Edge]):
    """Independent exhaustive comparator, intentionally limited to <=16 nodes."""
    validate(vertices, edges)
    if len(vertices) > 16:
        raise ValueError("brute-force comparator limited to sixteen nodes")
    assignments = []
    minimum_unsatisfied = len(edges)
    for bits in product((0, 1), repeat=len(vertices)):
        label = dict(zip(vertices, bits))
        missed = sum(
            (label[e.u] ^ label[e.v]) != e.parity for e in edges
        )
        minimum_unsatisfied = min(minimum_unsatisfied, missed)
        if missed == 0:
            assignments.append(label)
    return {
        "satisfiable": bool(assignments),
        "assignment_count": len(assignments),
        "minimum_unsatisfied_edges": minimum_unsatisfied,
    }


def gauge_switch(edges: Sequence[Edge], flips: dict[str, int]) -> tuple[Edge, ...]:
    """Switch local 0/1 conventions; cycle XOR is invariant under switching."""
    names = {v for e in edges for v in (e.u, e.v)}
    if set(flips) != names or any(type(x) is not int or x not in (0, 1) for x in flips.values()):
        raise ValueError("flips must cover all edge endpoints with binary values")
    return tuple(
        Edge(e.id, e.u, e.v, e.parity ^ flips[e.u] ^ flips[e.v])
        for e in edges
    )


def cycle_notes(analysis: dict) -> tuple[int, ...]:
    """Only closed-loop fluxes enter the invariant audio mapping."""
    return tuple(c.flux for c in analysis["cycles"])


def pcm_bytes(notes: Sequence[int], sample_rate: int = 22050) -> bytes:
    """Stereo PCM16 original synthetic sonification of loop XOR.

    Each loop: left reference 440 Hz; right 440 Hz when flux=0, 466.16 Hz
    when flux=1. Musical choice only; perceptual reliability is NOT tested.
    """
    if sample_rate < 4000 or any(type(n) is not int or n not in (0, 1) for n in notes):
        raise ValueError("invalid audio parameters")
    frames_per_note = round(sample_rate * 0.60)
    result = bytearray()
    for flux in notes:
        right_hz = 440.0 if flux == 0 else 466.16
        for j in range(frames_per_note):
            elapsed = j / sample_rate
            envelope = math.sin(math.pi * (j + 0.5) / frames_per_note) ** 2
            left = round(16000 * envelope * math.sin(math.tau * 440.0 * elapsed))
            right = round(16000 * envelope * math.sin(math.tau * right_hz * elapsed))
            result.extend(struct.pack("<hh", left, right))
    return bytes(result)


def render_wav(path: Path, notes: Sequence[int]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = pcm_bytes(notes)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(22050)
        stream.writeframes(data)
    blob = path.read_bytes()
    return {
        "file": path.name,
        "sha256": sha256(blob).hexdigest(),
        "frames": len(data) // 4,
        "sample_rate_hz": 22050,
        "channels": 2,
        "flux_notes": list(notes),
    }


VERTICES = ("A", "B", "C", "D")
BALANCED = (
    Edge("e1", "A", "B", 0),
    Edge("e2", "B", "C", 1),
    Edge("e3", "C", "D", 0),
    Edge("e4", "D", "A", 1),
)
FRUSTRATED = BALANCED[:3] + (Edge("e4", "D", "A", 0),)
FLIPS = {"A": 1, "B": 0, "C": 1, "D": 1}
ORDER_FIRST = (
    Edge("ab", "A", "B", 1),
    Edge("ac", "A", "C", 0),
    Edge("ad", "A", "D", 0),
    Edge("bc", "B", "C", 0),
    Edge("bd", "B", "D", 0),
    Edge("cd", "C", "D", 0),
)
ORDER_LAST = ORDER_FIRST[1:] + ORDER_FIRST[:1]


def generate(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    scenarios = {
        "balanced": BALANCED,
        "frustrated": FRUSTRATED,
        "switched_frustrated": gauge_switch(FRUSTRATED, FLIPS),
        "order_ab_first": ORDER_FIRST,
        "order_ab_last": ORDER_LAST,
    }
    payload: dict = {
        "schema": "mhac-x007-v1",
        "meaning": "synthetic binary same/different relations only",
        "flips": FLIPS,
        "scenarios": {},
    }
    for name, edges in scenarios.items():
        analysis = analyse(VERTICES, edges)
        if not verify_cycles(edges, analysis):
            raise AssertionError("certificate verification failed")
        brute = brute_assignments(VERTICES, edges)
        if analysis["satisfiable"] != brute["satisfiable"]:
            raise AssertionError("independent exhaustive comparator disagrees")
        audio = render_wav(out / (name + ".wav"), cycle_notes(analysis))
        payload["scenarios"][name] = {
            "edges": [asdict(x) for x in edges],
            "accepted": list(analysis["accepted"]),
            "rejected": list(analysis["rejected"]),
            "cycles": [asdict(x) for x in analysis["cycles"]],
            "brute_force": brute,
            "audio": audio,
        }
    first = payload["scenarios"]["frustrated"]["audio"]["sha256"]
    switched = payload["scenarios"]["switched_frustrated"]["audio"]["sha256"]
    balanced = payload["scenarios"]["balanced"]["audio"]["sha256"]
    if first != switched or first == balanced:
        raise AssertionError("gauge invariance or sound distinction failed")
    order_first = payload["scenarios"]["order_ab_first"]
    order_last = payload["scenarios"]["order_ab_last"]
    if (
        cycle_notes(analyse(VERTICES, ORDER_FIRST)) != (1, 1, 0)
        or cycle_notes(analyse(VERTICES, ORDER_LAST)) != (0, 0, 1)
        or order_first["audio"]["sha256"] == order_last["audio"]["sha256"]
        or {e.id for e in ORDER_FIRST} != {e.id for e in ORDER_LAST}
    ):
        raise AssertionError("same-graph stream-order negative control failed")
    payload["verified"] = {
        "same_graph_stream_order_can_change_sound": True,
        "gauge_invariant_wav_sha256_equal": True,
        "single_edge_flip_changes_wav_sha256": True,
        "all_cycle_certificates_verified": True,
    }
    receipt = out / "receipt.json"
    receipt.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/mhac-x007"))
    args = parser.parse_args()
    result = generate(args.out)
    print(json.dumps({
        "out": str(args.out),
        "verified": result["verified"],
        "scenarios": {
            name: {
                "cycles": len(p["cycles"]),
                "rejected": p["rejected"],
                "assignments": p["brute_force"]["assignment_count"],
                "wav_sha256": p["audio"]["sha256"],
            }
            for name, p in result["scenarios"].items()
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
