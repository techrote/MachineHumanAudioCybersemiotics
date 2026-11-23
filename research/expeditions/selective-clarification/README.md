# The Question That Need Not Be Asked

**Refs #201 — 2026-11-23 — finite mathematical model and synthetic experiment.** This is a counter-expedition to MHAC's recurring anti-collapse motif, not a new empirical finding, a novel theorem in active learning, or a production decision rule.

## A disagreement with the sediment

X001's observer model and X004's quotient guard ask whether a fixed verdict survives loss of information. The latter explicitly tests a vector of single-valued decisions. Both are valid for their stated objects. But a subtle design error can occur before the test: requiring exactly one preferred outcome for every world when several outcomes are acceptable.

Suppose a fictional patch editor has two compatible worlds. In one, either A or B is allowed; in the other, either B or C is allowed. Their complete action sets differ, but B is permitted in both. A classifier that insists on recovering the entire set, or selecting an arbitrary preferred action for each world, may manufacture an apparent information deficit. Asking which world obtains may accomplish nothing needed by the immediate decision.

This is not an objection to maintaining distinctions in research records. Scientific provenance, future decisions, audit requirements and authority can demand distinctions not needed for one current choice. The relevant question is: which specified task has actually been made impossible by compression?

## Formal model

Let W be a finite nonempty set of possible worlds, A a finite action alphabet, and P(w) a nonempty subset of A. P is stipulated by the author, not measured from the world. A belief set S is a nonempty subset of W; no probabilities are assumed. An action can be certified *under this table* exactly when it lies in the intersection I(S) of P(w) over w in S.

Proof: if the selected action belongs to I(S), it is permitted in each possible world by definition. If it does not, at least one world in S supplies a counterexample. A policy that can choose any action in I(S) does not need to recover w or even the complete P(w). Empty S is a modelling contradiction, not a vacuous success.

The singleton special case recovers the factorization condition in X001/X004. With sets, pairwise overlap is not sufficient: {a,b}, {b,c}, {a,c} intersect pairwise but have empty triple intersection. Conversely, all differing sets can share one action. The problem is a specified feasible decision, not equality of semantic representations.

This is precisely related to established **decision region determination**. Javdani, Chen, Karbasi, Krause, Bagnell and Srinivasa, *Near Optimal Bayesian Active Learning for Decision Making*, AISTATS 2014, PMLR 33:430–438, [official proceedings abstract](https://proceedings.mlr.press/v33/javdani14.html), describe sequential tests for overlapping decision regions rather than uncertainty minimization per se. Reading extent for this expedition: the complete official abstract and bibliographic metadata, not the full paper; no claim about the authors' theorem beyond that abstract. We do not implement their HEC algorithm or claim priority. Our contribution to MHAC is a deliberately small worst-case exact comparator and a critique of an overly strong interpretation of its existing single-valued abstraction.

## A price for the question

Each deterministic question q has positive integer cost c(q) and a known answer in every world. It partitions S into nonempty cells S(q,v). State is fixed during questions. A question may be used at most once. Cost is an additive fictional budget, not measured latency, fatigue or risk. Define V(S,Q) as the minimum worst-path cost using remaining questions Q:

- V = 0 if I(S) is nonempty;
- otherwise V = min over informative q in Q of [c(q) + max over attainable answers v of V(S(q,v), Q minus q)];
- V is infinite if no feasible question tree exists.

Proof by induction on the number of remaining questions: a successful leaf needs a common action; otherwise the first query of any successful tree is one of the available informative queries. Each attainable branch must itself be feasible, giving the lower bound; constructing the optimal subtrees gives the matching upper bound. A constant query can be discarded because it costs something without changing S. This also establishes the budget threshold: a finite plan fits budget b precisely when V ≤ b. The recurrence does not allow paid failure, state drift, uncertain answers, or risky actions to buy information.

The static comparator enumerates fixed subsets of questions and checks each resulting cell. Full identification uses singleton leaves; it is an upper requirement, not intrinsically superior. A deliberately naive unweighted greedy comparator minimizes the largest resulting cell, breaking ties by question name. This is not entropy, HEC, Bayesian optimality or a representative empirical model of human querying.

## Synthetic witnesses and falsifiers

| Fictional fixture | Exact adaptive action cost | Fixed-set cost | Adaptive identification | Greedy action |
| --- | ---: | ---: | ---: | ---: |
| Overlapping actions | 0 | 0 | 1 | 0 |
| Pairwise-only overlap | 2 | 2 | 2 | 2 |
| Multiplexer, irrelevant ornament | 2 | 3 | 4 | 4 |
| Expensive exact detail | 1 | 1 | 9 | 9 |
| Indistinguishable incompatible worlds | impossible | impossible | impossible | impossible |

These are derived expectations, pending exact execution receipts until checks actually complete.

The multiplexer uses 32 worlds (mode L/R, two binary values, four ornament values). Only the bit selected by mode determines the action. Asking mode then the corresponding bit costs two on every path. No one question suffices because either it ignores one relevant bit or leaves both modes possible. A fixed subset needs mode and both bits; it can omit ornament. Full identification needs every coordinate. The naive greedy first asks ornament because the four-way split gives smaller cells than the binary queries. It then asks left on a name tie, then mode, then sometimes right. Its worst path costs four. This is an exact counterexample to both indiscriminate state recovery and raw partition-size reduction as an immediate action strategy. It does not disprove the DRD literature or optimal information gathering.

The expensive-decoy fixture assigns cost nine to full identification and cost one to the only distinction relevant to the action. The greedy baseline disregards cost, so the comparison is intentionally easy to defeat. It is a negative control, not evidence that all greedy methods fail.

The unresolvable fixture contains worlds requiring different actions but all available answers coincide. A larger budget cannot help. The closed-world fixture initially appears to permit action a without questions if the author omits world 2. Adding the omitted world makes the plan impossible. The oracle cannot establish completeness of the table, truth of permission sets, query reliability, recipient authority or physical safety.

## An exaptation: decision-oriented detail on demand

For future non-critical artistic or authoring tools, imagine a synthesizer or patch browser which offers clarification only if the set of user-approved operations has no common element. A user asks for a transformation on an ambiguous patch; multiple non-destructive preview transformations might satisfy every compatible interpretation. Rather than forcing an unnecessary categorical choice, the interface can offer the shared preview. Where none exists, it can expose the most useful question under a declared cost budget.

For research agents, the analogous use is in uncertainty about reversible work, not permission to infer the owner's intent. A common reversible artifact may be worthwhile across multiple interpretations. A question about a missing design decision may be essential if every plausible action would violate at least one interpretation. This is an analogy, not permission to bypass actual required authorization or safety policies. Future tasks can change the set of relevant decisions; preserving distinctions for those future tasks may be valuable even when the immediate action needs none.

This also counters a potential MHAC failure mode: responding to every ambiguity with ever-longer metadata, distinctions and clarification. The cost of precision is real only after a relevant cost metric has been specified. The present integer model cannot justify an empirical cognitive-load claim.

## Scope and reproducibility

Base inspected: 495a98ca12bae467a507031f04931aa4254b1866. Reviewed AGENTS, RAG, programme, runbook, integrity and validation; inspected X004 quotient and exaptation notes, X001 transfer, X005 synthesis, migrating timbre, and issue scopes #33, #49, #184, #193, #195, #199. The latter two concern marginal witnesses and spectral descriptors, respectively. No modifications to their work. This expedition changes only its own directory and one uniquely named test bridge. No protocol, registry, empirical corpus or human gate changes.

Run from repository root:

    python3 research/expeditions/selective-clarification/lab.py
    python3 -m unittest discover -s tests -p 'test_mhac_selective_clarification_201.py' -v

The independent budget-game comparison in the test suite enumerates 7^3 nonempty action assignments over three worlds, eight binary answer patterns and four budgets: 10,976 feasibility comparisons. A plan replay also checks every world for legal terminal decisions and realized worst cost. This is independent algorithmic formulation by the same AI, not independent human review.

The model is intentionally bounded to 64 worlds and 14 questions; the search is exponential and the bounds are input limits, not performance guarantees. No external library or human data. This report is AI-assisted original analysis; external source reading is explicitly limited to the proceedings abstract above. No source enters Track E/G from this work.

**Decision:** preserve selective clarification as a candidate mathematical exaptation. Reject the stronger claims that ambiguity always requires clarification, that a common action makes complete information irrelevant forever, or that this planner proves actual safe action. The strongest finding is the difference between an informationally complete model and a decision-complete model under a fixed, explicit permission table.
