"""Synthetic aligned binary melody consensus; no inference of real ancestry."""
from itertools import product
from pathlib import Path
from math import sin, pi
import hashlib
import json
import struct
import wave


def majority(a, b, c):
    return (a & b) | (a & c) | (b & c)


def loss(x, witnesses):
    return sum((x ^ w).bit_count() for w in witnesses)


def absent_count(n):
    return 2**n * (4**n - 3*3**n + 3*2**n - 1)


def census():
    rows = []
    for n in range(1, 7):
        total = absent = brute = 0
        for ws in product(range(2**n), repeat=3):
            a, b, c = ws
            m = majority(a, b, c)
            masks = [w ^ m for w in ws]
            assert not (masks[0]&masks[1] or masks[0]&masks[2] or masks[1]&masks[2])
            cost = loss(m, ws)
            medoid = min(loss(w, ws) for w in ws)
            assert medoid-cost == min(x.bit_count() for x in masks)
            assert (m not in ws) == (medoid > cost)
            if n <= 4:
                scores = [loss(x, ws) for x in range(2**n)]
                assert scores[m] == min(scores) and scores.count(scores[m]) == 1
                brute += len(scores)
            total += 1
            absent += m not in ws
        assert absent == absent_count(n)
        rows.append(dict(length=n, triples=total, absent=absent, candidate_losses=brute))
    for k in range(1, 5):
        M = 2**k
        unresolved = sum(len(set(ws)) == 3 for ws in product(range(M), repeat=3))
        assert unresolved == M*(M-1)*(M-2)
    return rows


def render(word):
    rate, size = 16000, 3200
    frames = []
    for bit in word:
        f = {'0': 220, '1': 330}[bit]
        frames.extend(round(10000*sin(2*pi*f*i/rate)*sin(pi*i/(size-1))**2) for i in range(size))
    assert max(map(abs, frames)) <= 10000
    return struct.pack('<' + 'h'*len(frames), *frames)


def main():
    rows = census()
    words = ['00110001', '11010101', '10101101']
    ws = tuple(int(w, 2) for w in words)
    m = majority(*ws)
    assert format(m, '08b') == '10110101' and m not in ws
    assert loss(m, ws) == 6 and min(loss(w, ws) for w in ws) == 8
    blocks = [len({w[i:i+2] for w in words}) for i in range(0, 8, 2)]
    assert blocks == [3, 3, 3, 1]
    assert majority(0, 0, 7) == 0  # witnessed-majority negative control
    assert majority(1, 2, 4) == 0  # unwitnessed majority positive control
    out = Path(__file__).resolve().parent / 'audio'
    out.mkdir(exist_ok=True)
    hashes = {}
    for name, word in zip(['witness-a', 'witness-b', 'witness-c', 'edition'], words+[format(m, '08b')]):
        data = render(word)
        assert data == render(word)
        path = out / (name+'.wav')
        with wave.open(str(path), 'wb') as f:
            f.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
            f.writeframes(data)
        with wave.open(str(path), 'rb') as f:
            assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (1, 2, 16000, 25600)
            assert f.readframes(25600) == data
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(set(hashes.values())) == 4
    receipt = dict(rows=rows, witness_words=words, edition=format(m, '08b'), majority_loss=loss(m, ws), witness_losses=[loss(w, ws) for w in ws], block_distinct_counts=blocks, audio_sha256=hashes)
    (out.parent / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
