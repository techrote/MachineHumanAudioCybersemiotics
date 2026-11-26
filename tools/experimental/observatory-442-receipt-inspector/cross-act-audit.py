"""Measurement #442: exact finite mixed-fault accounting, synthetic only.
Independent reconstruction of #453's four-class decoder; not its native DSP.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
import math
from pathlib import Path
import struct
import wave

PIN = {'commit': '0fe95f804a20a8f3a6e59a2f8089d8b83f438204',
       'blob': 'dae13404d68c00bbe537d128802a1848aac2d952',
       'path': 'tools/experimental/grammar-452-scoped-clauses/conflict-certificate.cjs'}
KINDS = ('ack', 'terminal', 'quote', 'certificate')
SYS = (0, 1, 4, 5)
PAIRS = tuple(combinations(range(20), 2))


def semantic(row):
    # Prefix expression with arities 0, 1, 2; unused tail must be padding 13.
    pending = 1
    for i, v in enumerate(row):
        if v in (0, 1, 2, 3, 14):
            pending -= 1
        elif 4 <= v <= 10:
            pass
        elif v in (11, 12):
            pending += 1
        else:
            return False
        if pending == 0:
            return all(x == 13 for x in row[i+1:])
    return False


def digits(k):
    return tuple(k // 17**i % 17 for i in (3, 2, 1, 0))


def word(row):
    # Independent polynomial interpolation using modular inverses in Python.
    return tuple(sum(y * math.prod((x-j)*pow(i-j, -1, 17)
                     for j in SYS if j != i)
                     for i, y in zip(SYS, row)) % 17 for x in range(8))


def catalogue():
    free = [k for k in range(4913, 13*4913) if not semantic(digits(k))]
    assert len(free) == 55858
    assert sum(semantic(digits(k)) for k in range(17**4)) == 3100
    rows = []
    for kind in KINDS:
        for address in range(192):
            acts = PAIRS if kind == 'certificate' else tuple((a,) for a in range(20))
            for i, act in enumerate(acts):
                j = address * len(acts) + i
                k = (j if kind == 'ack' else 14*4913+j if kind == 'terminal'
                     else free[36480+j] if kind == 'quote' else free[j])
                rows.append((kind, address, act, word(digits(k))))
    assert len({r[3] for r in rows}) == len(rows) == 48000
    h = g = 0
    for _, _, _, w in rows:
        for v in w:
            h = (h*31+v+1) % 1000000007
            g = (g*37+v+1) % 1000000009
    # Exact pinned JS encoder's full catalogue fingerprints (connector V8).
    assert (h, g) == (95787044, 408117442)
    return rows, [h, g]


def audit(rows):
    # Exactly one wrong retained symbol and four known erasures. For each
    # three unchanged positions, each ordered pair of distinct legal words
    # sharing that triple differs in every other position (distance >= 5).
    # Thus five distinct choices of the substituted retained position.
    totals = {k: Counter() for k in KINDS}
    same_address = {k: Counter() for k in KINDS}
    detail = []
    for pos in combinations(range(8), 3):
        groups = defaultdict(list)
        for kind, address, _, w in rows:
            groups[tuple(w[i] for i in pos)].append((kind, address))
        assert len(groups) <= 17**3 and max(map(len, groups.values())) <= 17
        cell = {k: Counter() for k in KINDS}
        for group in groups.values():
            c = Counter(k for k, _ in group)
            for a, na in c.items():
                for b, nb in c.items():
                    cell[a][b] += 5*na*(nb-(a == b))
            by_addr = defaultdict(Counter)
            for k, addr in group:
                by_addr[addr][k] += 1
            for c in by_addr.values():
                for a, na in c.items():
                    for b, nb in c.items():
                        same_address[a][b] += 5*na*(nb-(a == b))
        for k in KINDS:
            totals[k].update(cell[k])
        detail.append({'unchanged': pos, 'matrix': cell})
    counts = Counter(r[0] for r in rows)
    out = {}
    for k in KINDS:
        attempts = counts[k]*56*5*16
        accepted = sum(totals[k].values())
        assert 0 <= accepted <= attempts
        assert all(same_address[k][b] <= totals[k][b] for b in KINDS)
        out[k] = {'attempts': attempts, 'wrong_by_kind': dict(totals[k]),
                  'same_address_by_kind': dict(same_address[k]),
                  'rejected': attempts-accepted,
                  'expected_kind_wrong': totals[k][k],
                  'expected_kind_address_wrong': same_address[k][k]}
    for a, b in product(KINDS, repeat=2):
        assert totals[a][b] == totals[b][a]  # inverse corruption is also counted
    return out, detail


def direct_check(rows, detail):
    # Independent literal lookup of four-symbol projections for first triple;
    # all five corrupted positions, all 16 wrong values, 48 fixed sent rows.
    selected = rows[::1000]
    pos = (0, 1, 2)
    n = 0
    for j in range(3, 8):
        ix = pos+(j,)
        lookup = {tuple(w[i] for i in ix): (k, a, t) for k, a, t, w in rows}
        assert len(lookup) == len(rows)
        for k, a, t, w in selected:
            vals = tuple(w[i] for i in pos)
            expected = Counter((b, addr, act) for b, addr, act, z in rows
                               if z != w and tuple(z[i] for i in pos) == vals)
            observed = Counter(lookup[vals+(v,)] for v in range(17)
                               if v != w[j] and vals+(v,) in lookup)
            assert expected == observed
            n += 16
    assert detail[0]['unchanged'] == pos
    return n


def specimen(out, name, symbols):
    rate, slot, active, amp = 16000, 1280, 960, 2048
    samples = [0]*(8*slot)
    for i, v in enumerate(symbols):
        if v is not None:
            for n in range(active):
                samples[i*slot+n] = round(amp*min(1,n/80,(active-1-n)/80)
                                          *math.sin(2*math.pi*(400+100*v)*n/rate+.137))
    # Independent aligned quadrature decoder for the generated specimens only.
    observed = []
    for i in range(8):
        x = samples[i*slot+160:i*slot+800]
        if not any(x):
            observed.append(None)
            continue
        scores = [sum(v*math.cos(2*math.pi*f*n/rate) for n,v in enumerate(x))**2+
                  sum(v*math.sin(2*math.pi*f*n/rate) for n,v in enumerate(x))**2
                  for f in range(400,2001,100)]
        observed.append(max(range(17), key=scores.__getitem__))
    assert observed == list(symbols)
    with wave.open(str(out/name), 'wb') as f:
        f.setparams((1,2,rate,len(samples),'NONE','not compressed'))
        f.writeframes(struct.pack('<'+'h'*len(samples), *samples))
    return {'file': name, 'symbols': symbols, 'observed': observed,
            'peak_counts': max(map(abs,samples)), 'sha256': sha256((out/name).read_bytes()).hexdigest()}


def main(out):
    rows, fingerprints = catalogue()
    totals, detail = audit(rows)
    direct = direct_check(rows, detail)
    sent = next(r[3] for r in rows if r[:3] == ('certificate',0,(0,1)))
    ack = next(r[3] for r in rows if r[:3] == ('ack',1,(1,)))
    damaged = (0,0,15,10,None,None,None,None)
    assert sent == (1,0,15,10,0,0,8,5) and ack[:4] == damaged[:4]
    assert sum(r[3][:4] == damaged[:4] for r in rows) == 1
    out.mkdir()
    specs = [specimen(out,n,s) for n,s in [('certificate.wav',sent),('damaged.wav',damaged),('ack.wav',ack)]]
    data = {'schema':'mhac-cross-act-audit-v1','source':PIN,'seed':None,
            'conditions':'exhaustive uniform counting, one substitution among four retained positions; four known erasures; not channel probability',
            'fingerprints':fingerprints,'codewords':len(rows),'literal_fault_checks':direct,
            'totals':totals,'by_unchanged_triple':detail,'specimens':specs,
            'baseline':'require >=5 observations: rejects all modeled mixed faults, but also every clean four-erasure observation',
            'limits':'only four accepted classes of pinned decoder; no other semantic rows, authentication, noise or human inference; side-information filters not free'}
    (out/'receipt.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    header = '<tr><th>Sent</th>'+''.join(f'<th>{k}</th>' for k in KINDS)+'<th>Reject</th></tr>'
    body = ''.join('<tr><th>'+k+'</th>'+''.join(f'<td>{totals[k]["wrong_by_kind"].get(b,0):,}</td>' for b in KINDS)+f'<td>{totals[k]["rejected"]:,}</td></tr>' for k in KINDS)
    audio = ''.join(f'<h2>{s["file"]}</h2><p>{s["symbols"]}</p><audio controls preload="none" src="{s["file"]}"></audio>' for s in specs)
    (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Mixed-fault audit</title><style>body{font:16px system-ui;max-width:1000px;margin:2em auto}td,th{padding:.5em;border:1px solid #888}audio{width:100%}</style><h1>Mixed-fault audit</h1><p>Exact finite symbol-fault counts, not measured channel probabilities. All accepted outputs are wrong. Original aligned FSK examples, common 2048-count amplitude; start at low hardware volume. No SPL claim.</p><table>'+header+body+'</table>'+audio+'<p><a href="receipt.json">Full receipt</a> · <a href="manifest.json">Hashes</a></p></html>',encoding='utf-8')
    files = {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}
    (out/'manifest.json').write_text(json.dumps({'source':PIN,'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'files':files},indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'totals':totals,'literal_fault_checks':direct,'codewords':len(rows)},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    main(parser.parse_args().output)
