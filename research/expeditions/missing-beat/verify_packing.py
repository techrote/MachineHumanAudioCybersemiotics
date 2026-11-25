"""Exact certificate verifier, independent of numerical solver; stdlib only."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from math import floor
import json
from laboratory import shapes, ratios, packing_exact

root=Path(__file__).resolve().parent
proof=json.loads((root/'packing-proof.json').read_text())
rows=[]
for L in range(3,19):
    candidates=shapes(L,4); sets=[ratios(x) for x in candidates]
    if L<9:
        optimum,states=packing_exact(sets)
        rows.append((L,optimum,'exact recurrence',states))
        continue
    spec=proof[str(L)]; R={F(a,b) for b in range(2,L+1) for a in range(1,b)}
    extras={F(r) for r in spec['extra']}; assert extras<=R
    cover={r:F(1+(r in extras),4) for r in R}
    assert all(sum(cover[r] for r in s)>=1 for s in sets)
    words=[tuple(w) for w in spec['words']]
    assert all(w in candidates for w in words)
    assert all(not ratios(a)&ratios(b) for a,b in combinations(words,2))
    upper=sum(cover.values()); assert len(words)==floor(upper)
    rows.append((L,len(words),'rational certificate',str(upper)))
print(json.dumps(rows,indent=2))
