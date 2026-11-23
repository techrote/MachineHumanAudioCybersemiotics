"""Exact finite diagnostic policies with state-changing probes (fictional models)."""
from collections import defaultdict, deque, Counter
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import struct
import wave

# Table: (current state, probe) -> (observation, next state).
# Missing entries mean forbidden, not a diagnostic observation.
# Belief: tuple of (original candidate, current state) pairs, unique origins.
def belief(states):
    return tuple((s, s) for s in sorted(set(states)))


def branches(table, b, probe):
    if not all((s, probe) in table for _, s in b):
        return None
    groups = defaultdict(list)
    for origin, state in b:
        obs, new = table[state, probe]
        groups[obs].append((origin, new))
    return {obs: tuple(group) for obs, group in sorted(groups.items())}


def solve(table, b, goal="origin"):
    """Exact minimum worst-case probe count, or None for impossibility.

    Finite reachable graph, no arbitrary depth cutoff. Each allowed action
    must succeed for every possible observation. Costs are unit probe costs.
    Returns a policy and the fixed-point rank of every winning belief.
    """
    if goal not in ("origin", "current"):
        raise ValueError("invalid goal")
    if not b or len({o for o, _ in b}) != len(b):
        raise ValueError("belief must be nonempty with distinct origin tags")
    probes = sorted({p for _, p in table})
    b = tuple(sorted(b))
    i = 0 if goal == "origin" else 1
    terminal = lambda node: len({pair[i] for pair in node}) == 1
    graph, seen, queue = {}, {b}, deque([b])
    while queue:
        node = queue.popleft()
        graph[node] = {}
        if terminal(node):
            continue
        for p in probes:
            groups = branches(table, node, p)
            if groups is None:
                continue
            graph[node][p] = groups
            for child in groups.values():
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
    ranks = {node: 0 for node in graph if terminal(node)}
    policy = {}
    while True:
        additions = {}
        for node, actions in graph.items():
            if node in ranks:
                continue
            choices = [(1 + max(ranks[c] for c in children.values()), p)
                       for p, children in actions.items()
                       if all(c in ranks for c in children.values())]
            if choices:
                additions[node] = min(choices)
        if not additions:
            break
        for node, (rank, p) in additions.items():
            ranks[node] = rank
            policy[node] = p
    return {"depth": ranks.get(b), "policy": policy, "ranks": ranks,
            "graph": graph, "root": b}


def read_once(codes, persistent=False):
    """Each binary column is a probe; a read-once probe erases all cells."""
    states = sorted(codes)
    if not states or "spent" in states:
        raise ValueError("invalid candidates")
    width = len(codes[states[0]])
    if not width or any(len(codes[s]) != width or
                        any(bit not in (0, 1) for bit in codes[s])
                        for s in states):
        raise ValueError("expected nonempty equal-width binary codes")
    table = {}
    for s in states:
        for j, bit in enumerate(codes[s]):
            table[s, f"q{j}"] = (str(bit), s if persistent else "spent")
    for j in range(width):
        table["spent", f"q{j}"] = ("empty", "spent")
    return table


def execute(table, state, probes):
    observations = []
    for p in probes:
        obs, state = table[state, p]
        observations.append((p, obs))
    return tuple(observations), state


def adaptive_example():
    # q partitions origins into groups; the two branches allow different probes.
    # No single fixed universally admissible sequence solves this machine.
    return {
        ("A","split"):("left","L0"), ("B","split"):("left","L1"),
        ("C","split"):("right","R0"), ("D","split"):("right","R1"),
        ("L0","left"):("0","spent"), ("L1","left"):("1","spent"),
        ("R0","right"):("0","spent"), ("R1","right"):("1","spent"),
    }


def enumerate_family(n):
    """All labelled n-candidate, two binary-probe response matrices."""
    counts = Counter(total=0, pairwise=0, read_once=0, persistent=0, gap=0)
    states = tuple(chr(65+i) for i in range(n))
    for entries in product((0, 1), repeat=2*n):
        codes = {s: entries[2*i:2*i+2] for i, s in enumerate(states)}
        once, keep = read_once(codes), read_once(codes, True)
        pair = all(solve(once, belief(pair))["depth"] is not None
                   for pair in combinations(states, 2))
        one = solve(once, belief(states))["depth"] is not None
        persist = solve(keep, belief(states))["depth"] is not None
        # Independent closed-form checks, not just self-comparison.
        assert pair == (len(set(codes.values())) == n)
        assert persist == pair
        assert one == any(len({c[j] for c in codes.values()}) == n
                          for j in range(2))
        counts.update(total=1, pairwise=int(pair), read_once=int(one),
                      persistent=int(persist), gap=int(pair and not one))
    return dict(counts)


def pcm(trace, rate=8000, duration=1200):
    """Original integer triangle pulses for observed symbol and query only.
    Identical transcripts imply byte-identical PCM; no perceptual claim.
    """
    out = bytearray()
    note = {"0": 173, "1": 261, "empty": 97}
    for probe, obs in trace:
        for freq in (137 + 47 * int(probe[1:]), note[obs]):
            for t in range(duration):
                phase = (t*freq) % rate
                triangle = rate - 4*abs(phase - rate//2)
                envelope = min(t, duration-1-t, 80)
                sample = triangle * 5000 * envelope // (rate * 80)
                out.extend(struct.pack("<h", sample))
    return bytes(out)


def demo(output=None):
    codes = {"A": (1,0), "B": (0,1), "C": (0,0)}
    once, keep = read_once(codes), read_once(codes, True)
    root = belief(codes)
    traces = {}
    for name, table, state in (("erased_B",once,"B"),
                               ("erased_C",once,"C"),
                               ("persistent_B",keep,"B"),
                               ("persistent_C",keep,"C")):
        trace, final = execute(table, state, ("q0","q1"))
        data = pcm(trace)
        traces[name] = {"trace":trace,"final":final,"pcm_sha256":hashlib.sha256(data).hexdigest()}
        if output is not None:
            output.mkdir(parents=True, exist_ok=True)
            with wave.open(str(output / (name + ".wav")), "wb") as w:
                w.setparams((1,2,8000,0,"NONE","not compressed"))
                w.writeframes(data)
    return {"three_candidate": enumerate_family(3),
            "four_candidate": enumerate_family(4),
            "origin_once":solve(once,root)["depth"],
            "current_once":solve(once,root,"current")["depth"],
            "origin_persistent":solve(keep,root)["depth"],
            "adaptive_depth":solve(adaptive_example(),belief("ABCD"))["depth"],
            "audio":traces}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wav-dir",type=Path)
    args = parser.parse_args()
    print(json.dumps(demo(args.wav_dir),indent=2,sort_keys=True))
