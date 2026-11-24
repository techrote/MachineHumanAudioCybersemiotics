"""Independent implementation (same AI author): dynamic programming for contiguous partitions.
Uses exact integer costs (12*N times mean squared receiver loss)."""
from functools import lru_cache
import json

def frontier(n, B):
    """Map action count to minimal receiver loss numerator; retain one witness."""
    @lru_cache(None)
    def dp(remaining, previous):
        if remaining == 0:
            return {0: (0, ())}
        result = {}
        for l in range(1, remaining + 1):
            if previous and not (B - 2 <= l - previous <= B + 2):
                continue
            for k, (cost, lens) in dp(remaining-l, l).items():
                candidate = (cost + l**3-l, (l,) + lens)
                if k+1 not in result or candidate < result[k+1]:
                    result[k+1] = candidate
        return result
    return dp(n, 0)

def run():
    checks=0
    less_actions_better=[]
    for n in range(1,41):
        for B in range(-32,33):
            f=frontier(n,B)
            d=max(0,abs(B)-2)
            expected=max(k for k in range(1,n+1) if k+d*k*(k-1)//2<=n)
            assert max(f)==expected,(n,B,f)
            assert set(f)==set(range(1,expected+1)),(n,B,f)
            # A census, not a theorem, of receiver-optimal resolution.
            if min(v[0] for v in f.values()) < f[expected][0]:
                less_actions_better.append((n,B))
            checks+=1
    rows=[]
    for B in (0,2,3,4,6,10,16,17):
        f=frontier(16,B); k=max(f); cost,lens=min(f.values())
        rows.append(dict(B=B,maximum=k,loss_numerator=cost,loss_denominator=192,lengths=lens))
    return dict(dp_checks=checks,strictly_better_lower_resolution_cases=less_actions_better,frontier=rows)

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
