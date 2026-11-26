"""Synthetic signed-role oracle and original reversible stereo score (stdlib)."""
import hashlib
import itertools as it
import json
import math
import struct
import wave
from pathlib import Path


def predicted(n, edges, anchors):
    adj = [[] for _ in range(n)]
    for a, b, parity in edges:
        adj[a].append((b, parity))
        adj[b].append((a, parity))
    rel = {}
    free = 0
    for root in range(n):
        if root in rel:
            continue
        rel[root] = 0
        todo = [root]
        component = []
        while todo:
            a = todo.pop()
            component.append(a)
            for b, parity in adj[a]:
                wanted = rel[a] ^ parity
                if b in rel:
                    if rel[b] != wanted:
                        return 0
                else:
                    rel[b] = wanted
                    todo.append(b)
        roots = {anchors[a] ^ rel[a] for a in component if a in anchors}
        if len(roots) > 1:
            return 0
        free += not roots
    return 2 ** free


def solutions(n, edges, anchors):
    return [x for x in it.product((0, 1), repeat=n)
            if all(x[a] ^ x[b] == p for a, b, p in edges)
            and all(x[a] == v for a, v in anchors.items())]


def qualify():
    graphs = cases = 0
    for n in range(1, 6):
        pairs = list(it.combinations(range(n), 2))
        anchor_sets = list(it.product((-1, 0, 1), repeat=n)) if n <= 4 else [(-1,) * n]
        for labels in it.product((-1, 0, 1), repeat=len(pairs)):
            edges = [(a, b, p) for (a, b), p in zip(pairs, labels) if p >= 0]
            graphs += 1
            for values in anchor_sets:
                anchors = {a: v for a, v in enumerate(values) if v >= 0}
                assert predicted(n, edges, anchors) == len(solutions(n, edges, anchors))
                cases += 1
    assert predicted(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)], {}) == 0
    assert predicted(2, [(0, 1, 0)], {0: 0, 1: 1}) == 0
    return graphs, cases


def render(out):
    out.mkdir(parents=True, exist_ok=True)
    rate, frames = 16000, 64000
    edges = [(0, 1, 1), (1, 2, 0), (3, 4, 1), (4, 5, 1)]
    roles = solutions(6, edges, {})
    assert len(roles) == 4 and predicted(6, edges, {0: 0, 3: 0}) == 1
    stems = []
    for j, f in enumerate((110, 165, 220, 277, 330, 440)):
        stem = []
        for i in range(frames):
            t = i / rate
            u = (t * (1 + j % 3) + j / 6) % 1
            env = math.sin(math.pi * u) ** 2 * math.sin(math.pi * i / (frames - 1)) ** 2
            stem.append(round(3200 * env * (0.8 * math.sin(2 * math.pi * f * t) +
                                             0.2 * math.sin(4 * math.pi * f * t))))
        stems.append(stem)
    dry = [sum(v) for v in zip(*stems)]
    assert max(map(abs, dry)) <= 19200
    records = {}
    def save(name, channels, pcm):
        path = out / (name + '.wav')
        data = struct.pack('<' + 'h' * len(pcm), *pcm)
        with wave.open(str(path), 'wb') as w:
            w.setparams((channels, 2, rate, frames, 'NONE', 'not compressed'))
            w.writeframes(data)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (channels, 2, rate, frames)
            assert w.readframes(frames) == data
        records[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    save('dry', 1, dry)
    for x in roles:
        left = [sum(v[j] for j in range(6) if x[j] == 0) for v in zip(*stems)]
        right = [sum(v[j] for j in range(6) if x[j] == 1) for v in zip(*stems)]
        assert [a + b for a, b in zip(left, right)] == dry
        assert max(map(abs, left + right)) <= 19200
        save('roles-' + ''.join(map(str, x)), 2, list(it.chain.from_iterable(zip(left, right))))
    assert len(set(records.values())) == 5
    return records, roles


if __name__ == '__main__':
    graphs, cases = qualify()
    out = Path(__file__).parent / 'audio'
    hashes, roles = render(out)
    again, _ = render(out)
    assert hashes == again
    receipt = dict(graphs=graphs, graph_anchor_cases=cases, roles=roles,
                   frames=64000, rate=16000, wav_sha256=hashes, result='PASS')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
