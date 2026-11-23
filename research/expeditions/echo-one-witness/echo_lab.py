#!/usr/bin/env python3
"""MHAC-X008: fictional provenance DAG, Bayes trap, and original PCM instrument.

All observations, reliability assumptions and links in these demonstrations are
invented. Root counts describe stipulated ancestry, not statistical independence.
Python >=3.11, standard library only. No network or optional packages.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Mapping
import argparse
import csv
import io
import json
import math
import re
import struct
import wave

NODE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
KINDS = {"observation", "derivative", "untraced"}
POLARITIES = {"support", "oppose"}
SAMPLE_RATE = 24000
PCM_AMPLITUDE = 11500
DURATION_SECONDS = 7.5
PREFIX_SECONDS = 5.5


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    parents: tuple[str, ...] = ()
    polarity: str | None = None


def validated_nodes(nodes: list[Node]) -> Mapping[str, Node]:
    """Reject malformed nodes, parent references, cycles and unsupported semantics."""
    ids: dict[str, Node] = {}
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("requires nonempty list of nodes")
    for node in nodes:
        if not isinstance(node, Node):
            raise ValueError("nodes must be Node instances")
        if not isinstance(node.id, str) or not NODE_ID.fullmatch(node.id):
            raise ValueError("invalid node ID")
        if node.id in ids:
            raise ValueError("duplicate node ID")
        if node.kind not in KINDS:
            raise ValueError("invalid node kind")
        if not isinstance(node.parents, tuple) or any(not isinstance(x, str) for x in node.parents):
            raise ValueError("parents must be tuple of IDs")
        if len(set(node.parents)) != len(node.parents):
            raise ValueError("duplicate parent reference")
        if node.kind == "derivative":
            if not node.parents or node.polarity is not None:
                raise ValueError("derivative requires parents and no polarity")
        elif node.parents:
            raise ValueError("observation and untraced nodes have no parents")
        elif node.kind == "observation" and node.polarity not in POLARITIES:
            raise ValueError("observation requires support/oppose polarity")
        elif node.kind == "untraced" and node.polarity is not None:
            raise ValueError("untraced root has unknown polarity")
        ids[node.id] = node
    for node in nodes:
        for p in node.parents:
            if p not in ids:
                raise ValueError(f"unknown parent: {p}")
    colors: dict[str, int] = {}
    def visit(node_id: str) -> None:
        state = colors.get(node_id, 0)
        if state == 1:
            raise ValueError("cycle in declared provenance")
        if state == 2:
            return
        colors[node_id] = 1
        for parent in ids[node_id].parents:
            visit(parent)
        colors[node_id] = 2
    for node_id in ids:
        visit(node_id)
    return ids


def ancestry(nodes: list[Node], outputs: list[str]) -> dict:
    """Compute transitive known and untraced roots for declared outputs.

    Parent edges encode declared provenance, *not* scientific evidential support.
    """
    ids = validated_nodes(nodes)
    if not isinstance(outputs, list) or not outputs or len(set(outputs)) != len(outputs):
        raise ValueError("requires nonempty distinct output IDs")
    if any(n not in ids for n in outputs):
        raise ValueError("unknown output")
    cache: dict[str, tuple[frozenset[str], frozenset[str]]] = {}
    def roots(node_id: str) -> tuple[frozenset[str], frozenset[str]]:
        if node_id in cache:
            return cache[node_id]
        n = ids[node_id]
        if n.kind == "observation":
            out = (frozenset({node_id}), frozenset())
        elif n.kind == "untraced":
            out = (frozenset(), frozenset({node_id}))
        else:
            known, unknown = set(), set()
            for parent in n.parents:
                a, b = roots(parent)
                known.update(a)
                unknown.update(b)
            out = (frozenset(known), frozenset(unknown))
        cache[node_id] = out
        return out
    lines: list[dict] = []
    all_roots: set[str] = set()
    all_unknowns: set[str] = set()
    for output in outputs:
        a, b = roots(output)
        all_roots.update(a)
        all_unknowns.update(b)
        lines.append({"message": output, "known_roots": sorted(a), "untraced_roots": sorted(b)})
    return {
        "messages": lines,
        "message_count": len(outputs),
        "unique_known_roots": sorted(all_roots),
        "known_root_count": len(all_roots),
        "untraced_nodes": sorted(all_unknowns),
        "complete_declared_ancestry": not all_unknowns,
        "disclaimer": "Known roots and unique IDs do not establish source truth, endorsement or statistical independence.",
    }


def posterior_for_observations(
    supports: int, opposes: int, *, prior: float = 0.5,
    sensitivity: float = 0.8, false_positive: float = 0.2,
) -> float:
    """Bayesian *toy* conditioned on mutually independent evidence given H and not-H.

    This conditional independence is an EXTERNAL assumption, not DAG output.
    A support has P(+|H)=sensitivity, P(+|not-H)=false_positive.
    A contrary observation has P(-|H)=1-sensitivity and P(-|not-H)=1-false_positive.
    """
    if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 for x in (supports, opposes)):
        raise ValueError("nonnegative integer counts required")
    if not (0 < prior < 1 and 0 < sensitivity < 1 and 0 < false_positive < 1):
        raise ValueError("probability parameters strictly between 0 and 1")
    logodds = (
        math.log(prior / (1 - prior))
        + supports * math.log(sensitivity / false_positive)
        + opposes * math.log((1 - sensitivity) / (1 - false_positive))
    )
    if logodds >= 0:
        return 1 / (1 + math.exp(-logodds))
    z = math.exp(logodds)
    return z / (1 + z)


def naive_toy_posterior(output_count: int, opposing_messages: int = 0) -> float:
    """Defective comparator: treat each emitted claim as fresh conditional evidence.

    The fictional outward utterances explicitly say positive/negative, even if
    their source link is copied, untraced, or inherited.
    """
    return posterior_for_observations(output_count - opposing_messages, opposing_messages)


def conditional_root_toy_posterior(nodes: list[Node], outputs: list[str]) -> float | None:
    """Return None if ancestry is incomplete. DOES NOT verify conditional independence."""
    result = ancestry(nodes, outputs)
    if not result["complete_declared_ancestry"]:
        return None
    ids = {n.id: n for n in nodes}
    positive = sum(ids[r].polarity == "support" for r in result["unique_known_roots"])
    negative = sum(ids[r].polarity == "oppose" for r in result["unique_known_roots"])
    return posterior_for_observations(positive, negative)


def scenario(name: str) -> tuple[list[Node], list[str]]:
    """Five deliberately small fictional ancestry networks."""
    outputs = [f"M{i}" for i in range(1, 9)]
    if name == "echo":
        return [Node("S1", "observation", polarity="support")] + [
            Node(m, "derivative", ("S1",)) for m in outputs
        ], outputs
    if name == "independent":
        return [Node(f"S{i}", "observation", polarity="support") for i in range(1, 9)] + [
            Node(m, "derivative", (f"S{i}",)) for i, m in enumerate(outputs, 1)
        ], outputs
    if name == "mixed":
        return [Node("S1", "observation", polarity="support"), Node("S2", "observation", polarity="support")] + [
            Node(m, "derivative", ("S1" if i < 8 else "S2",)) for i, m in enumerate(outputs, 1)
        ], outputs
    if name == "untraced":
        return [Node("S1", "observation", polarity="support"), Node("U1", "untraced")] + [
            Node(m, "derivative", ("S1" if i < 8 else "U1",)) for i, m in enumerate(outputs, 1)
        ], outputs
    if name == "opposing":
        return [Node("S1", "observation", polarity="support"), Node("S2", "observation", polarity="oppose")] + [
            Node(m, "derivative", ("S1" if i <= 7 else "S2",)) for i, m in enumerate(outputs, 1)
        ], outputs
    raise ValueError("unknown scenario")


def scenario_summary(name: str) -> dict:
    nodes, outputs = scenario(name)
    data = ancestry(nodes, outputs)
    return {
        "scenario": name,
        **data,
        "defective_independent_message_posterior": naive_toy_posterior(len(outputs), 1 if name == "opposing" else 0),
        "outward_negative_claims": 1 if name == "opposing" else 0,
        "conditional_independent_root_posterior": conditional_root_toy_posterior(nodes, outputs),
        "posterior_assumptions": {
            "prior_H": 0.5, "P_positive_given_H": 0.8,
            "P_positive_given_not_H": 0.2,
            "conditional_independence_of_root_observations": "ASSUMED ONLY IN THE ROOT-BASED TOY; NOT INFERRED",
            "input_class": "fictional"
        }
    }


def triangle_sine_samples(t: float, duration: float, freq: float) -> float:
    """Original short Hann-windowed sinusoidal pulse, t relative to pulse start."""
    if not (0 <= t < duration):
        return 0.0
    envelope = math.sin(math.pi * t / duration) ** 2
    return math.sin(2 * math.pi * freq * t) * envelope


def sound_samples(root_count: int) -> bytes:
    """Eight identical public messages then 1 or 8 distinct root-count witness pulses.

    Root count changes ONLY the interval after PREFIX_SECONDS.
    The first 5.5 seconds are therefore byte-identical by construction.
    """
    if root_count not in (1, 8):
        raise ValueError("audio example requires 1 or 8 roots")
    out = bytearray()
    for i in range(round(SAMPLE_RATE * DURATION_SECONDS)):
        t = i / SAMPLE_RATE
        val = 0.0
        for k in range(8):
            val += triangle_sine_samples(t - (0.4 + 0.54 * k), 0.11, 620)
        if t >= PREFIX_SECONDS:
            for k in range(root_count):
                start = 5.8 + k * (0.15 if root_count == 8 else 0.0)
                val += triangle_sine_samples(t - start, 0.09, 910)
        amp = int(round(max(-1.0, min(1.0, val)) * PCM_AMPLITUDE))
        out.extend(struct.pack('<h', amp))
    return bytes(out)


def sound_wav(root_count: int) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(sound_samples(root_count))
    return stream.getvalue()


def generate(outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    summaries = {name: scenario_summary(name) for name in ('echo', 'independent', 'mixed', 'untraced', 'opposing')}
    for name, info in summaries.items():
        (outdir / f'{name}.json').write_text(json.dumps(info, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    wav1 = sound_wav(1)
    wav8 = sound_wav(8)
    p1, p8 = outdir / 'echo-1-root.wav', outdir / 'eight-independent-roots.wav'
    p1.write_bytes(wav1)
    p8.write_bytes(wav8)
    first = sound_samples(1)
    second = sound_samples(8)
    prefix_bytes = round(SAMPLE_RATE * PREFIX_SECONDS) * 2
    assert first[:prefix_bytes] == second[:prefix_bytes]
    assert first != second
    with (outdir / 'message_lineage.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(('scenario', 'message', 'known_root_ids', 'untraced_root_ids'))
        for name, result in summaries.items():
            for m in result['messages']:
                writer.writerow((name, m['message'], ';'.join(m['known_roots']), ';'.join(m['untraced_roots'])))
    filenames = ['echo.json', 'independent.json', 'mixed.json', 'untraced.json', 'opposing.json', 'echo-1-root.wav', 'eight-independent-roots.wav', 'message_lineage.csv']
    receipt = {
        'schema': 'mhac-x008-echo-one-witness-receipt-v1',
        'fictional': True,
        'sample_rate_hz': SAMPLE_RATE,
        'samples_per_file': round(SAMPLE_RATE * DURATION_SECONDS),
        'format': 'PCM16 mono, original synthesis',
        'prefix_seconds': PREFIX_SECONDS,
        'prefix_identical': first[:prefix_bytes] == second[:prefix_bytes],
        'full_pcm_identical': first == second,
        'root_counts': {'echo': 1, 'independent': 8, 'mixed': 2, 'untraced': 'unknown', 'opposing': 2},
        'files_sha256': {name: sha256((outdir / name).read_bytes()).hexdigest() for name in filenames},
    }
    (outdir / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('build/mhac-x008'))
    args = parser.parse_args()
    print(json.dumps(generate(args.out), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
