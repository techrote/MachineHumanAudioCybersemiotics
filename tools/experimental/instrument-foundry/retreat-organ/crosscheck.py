"""Independent Boolean tuple BFS oracle for the exported atlas."""
import csv
from collections import deque
start = ((False,)*8, (False,)*8, 0)
q = deque([start]); depths = {start: 0}; best = {}
while q:
    a,b,x = s = q.popleft()
    n = depths[s]
    best.setdefault((x, sum(a)-sum(b)), n)
    for y in range(17):
        aa = tuple(y >= 9+i or (v and y >= (8 if i==7 else 7-i)) for i,v in enumerate(a))
        bb = tuple(y >= 9+i or (v and y >= 8-i) for i,v in enumerate(b))
        t = aa,bb,y
        if t not in depths:
            depths[t] = n+1
            q.append(t)
with open('trajectory-atlas.csv', newline='') as f:
    rows = list(csv.DictReader(f))
observed = {(int(r['final_level']), int(r['signed_relay_difference'])): int(r['transitions']) for r in rows}
assert len(depths) == 4188 and len(rows) == 81 and observed == best
print('Independent representation: all 81 minimum transition counts match; 4188 states.')
