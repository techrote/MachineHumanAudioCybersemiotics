"""Exact finite selective-clarification lab. No empirical or physical safety claims."""
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from typing import NamedTuple
import json


class Plan(NamedTuple):
    cost: int
    kind: str
    name: str
    children: tuple = ()


@dataclass(frozen=True)
class Problem:
    # Each row: (world identifier, nonempty set of model-permitted actions).
    worlds: tuple
    # Each question: (name, strictly positive integer cost, answers in row order).
    questions: tuple

    def __post_init__(self):
        if not self.worlds or len(self.worlds) > 64 or len(self.questions) > 14:
            raise ValueError("requires 1..64 worlds and at most 14 questions")
        ids = [w[0] for w in self.worlds]
        names = [q[0] for q in self.questions]
        if len(set(ids)) != len(ids) or len(set(names)) != len(names):
            raise ValueError("duplicate world or question")
        for name, actions in self.worlds:
            if not isinstance(name, str) or not isinstance(actions, frozenset) or not actions:
                raise ValueError("world must have nonempty frozenset of actions")
            if not all(isinstance(a, str) for a in actions):
                raise ValueError("actions must be strings")
        for name, cost, answers in self.questions:
            if not isinstance(name, str) or type(cost) is not int or cost <= 0:
                raise ValueError("question requires name and positive integer cost")
            if len(answers) != len(ids) or not all(isinstance(a, str) for a in answers):
                raise ValueError("one string answer per world required")

    def common(self, states):
        if not states:
            raise ValueError("empty possibility set is not a successful decision")
        return frozenset.intersection(*(self.worlds[i][1] for i in states))

    def split(self, states, q):
        out = {}
        for i in states:
            out.setdefault(self.questions[q][2][i], []).append(i)
        return tuple((a, tuple(v)) for a, v in sorted(out.items()))

    def optimum(self, *, identify=False, budget=None):
        """Minimum worst-path cost; None means no certified feasible tree."""
        if budget is not None and (type(budget) is not int or budget < 0):
            raise ValueError("budget must be nonnegative integer")
        @lru_cache(None)
        def rec(states, remaining):
            common = self.common(states)
            if (len(states) == 1 if identify else bool(common)):
                name = self.worlds[states[0]][0] if identify else min(common)
                return Plan(0, "world" if identify else "action", name)
            best = None
            for q in remaining:
                parts = self.split(states, q)
                if len(parts) == 1:
                    continue
                later = tuple(j for j in remaining if j != q)
                sub = tuple((a, rec(s, later)) for a, s in parts)
                if any(p is None for a, p in sub):
                    continue
                name, cost, _ = self.questions[q]
                candidate = Plan(cost + max(p.cost for a, p in sub), "ask", name, sub)
                if best is None or (candidate.cost, candidate.name) < (best.cost, best.name):
                    best = candidate
            return best
        result = rec(tuple(range(len(self.worlds))), tuple(range(len(self.questions))))
        return None if result is None or (budget is not None and result.cost > budget) else result

    def static(self, *, identify=False):
        """Minimum-cost fixed set of questions, asked in full in every world."""
        best = None
        for n in range(len(self.questions) + 1):
            for qs in combinations(range(len(self.questions)), n):
                cost = sum(self.questions[q][1] for q in qs)
                names = tuple(self.questions[q][0] for q in qs)
                if best is not None and (cost, names) >= best:
                    continue
                cells = {}
                for i in range(len(self.worlds)):
                    key = tuple(self.questions[q][2][i] for q in qs)
                    cells.setdefault(key, []).append(i)
                if all(len(s) == 1 if identify else bool(self.common(s)) for s in cells.values()):
                    best = (cost, names)
        return best

    def greedy(self):
        """Unweighted smallest-largest-cell heuristic; NOT entropy or DRD HEC."""
        def rec(states, qs):
            common = self.common(states)
            if common:
                return Plan(0, "action", min(common))
            candidates = []
            for q in qs:
                parts = self.split(states, q)
                if len(parts) > 1:
                    candidates.append((max(len(s) for a,s in parts), self.questions[q][0], q, parts))
            if not candidates:
                return None
            _, name, q, parts = min(candidates)
            sub = tuple((a, rec(s, tuple(j for j in qs if j != q))) for a,s in parts)
            if any(p is None for a,p in sub):
                return None
            return Plan(self.questions[q][1] + max(p.cost for a,p in sub), "ask", name, sub)
        return rec(tuple(range(len(self.worlds))), tuple(range(len(self.questions))))

    def verify(self, plan, *, identify=False):
        """Replay all worlds. Reject wrong answers, repeated queries, and cost claims."""
        if plan is None:
            raise ValueError("no plan to verify")
        names = {q[0]: q for q in self.questions}
        realized = []
        for i, (world, actions) in enumerate(self.worlds):
            p, used, paid = plan, set(), 0
            while p.kind == "ask":
                if p.name not in names or p.name in used:
                    raise ValueError("unknown or repeated question")
                used.add(p.name)
                _, cost, answers = names[p.name]
                children = dict(p.children)
                if len(children) != len(p.children) or answers[i] not in children:
                    raise ValueError("invalid answer branches")
                if p.cost != cost + max(v.cost for v in children.values()):
                    raise ValueError("incorrect internal cost")
                paid += cost
                p = children[answers[i]]
            if p.cost != 0 or p.children:
                raise ValueError("malformed terminal")
            if (p.kind != "world" or p.name != world) if identify else (p.kind != "action" or p.name not in actions):
                raise ValueError("invalid terminal decision")
            realized.append(paid)
        if max(realized) != plan.cost:
            raise ValueError("wrong worst-case cost")
        return tuple(realized)


def multiplexer():
    rows = list(product("LR", "01", "01", "0123"))
    worlds = tuple(("/".join(r), frozenset({r[1] if r[0] == "L" else r[2]})) for r in rows)
    questions = tuple((name, 1, tuple(r[i] for r in rows))
                      for i,name in enumerate(("mode", "left", "right", "ornament")))
    return Problem(worlds, questions)


def examples():
    def make(sets, qs=()):
        return Problem(tuple((str(i), frozenset(s)) for i,s in enumerate(sets)), qs)
    return {
        "multiplexer": multiplexer(),
        "overlap": make(("ab","bc"), (("detail",1,("x","y")),)),
        "pairwise_only": make(("ab","bc","ac"), (("detail",2,("x","y","z")),)),
        "unresolvable": make(("a","b"), (("ornament",1,("x","x")),)),
        "expensive_decoy": make(("a","a","b","b"),
            (("cheap",1,("x","x","y","y")), ("precise",9,("0","1","2","3")))),
        "closed_world_trap": make(("a","a","b"), (("detail",1,("x","x","x")),)),
    }


def summarize():
    report = {}
    for name,p in examples().items():
        opt, identity, greedy = p.optimum(), p.optimum(identify=True), p.greedy()
        for plan,ident in [(opt,False),(identity,True),(greedy,False)]:
            if plan is not None:
                p.verify(plan, identify=ident)
        report[name] = {
            "worlds": len(p.worlds), "common": sorted(p.common(tuple(range(len(p.worlds))))),
            "adaptive": opt, "static": p.static(),
            "identify_adaptive": identity, "identify_static": p.static(identify=True),
            "greedy": greedy,
        }
    return report


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2))
