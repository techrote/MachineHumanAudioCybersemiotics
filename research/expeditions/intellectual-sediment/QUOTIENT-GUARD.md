# MHAC-X004 — quotient safety as the formal skeleton of “do not conflate”

**Status:** elementary finite-state formalization and reusable audit tool, not a new theorem in statistics, reinforcement learning or information theory.

The manual genealogies suggest that MHAC's recurring anti-collapse move can be phrased more precisely:

> If a representation merges full states that require different downstream decisions, that representation is insufficient for those decisions.

X001 already proved the one-verdict set-theoretic version: a verdict V can be computed from an observation q exactly when V is constant on each fibre of q. X004 reuses that result for a vector of declared decisions and supplies a finite-table checker.

## Exact finite claim

Let X be a finite set of explicit states. Let

- q:X→Q be a proposed collapsed representation;
- D=(D1,...,Dk):X→Y1×...×Yk be the declared downstream decision vector.

Then there exists a deterministic function h:Q→Y1×...×Yk with

    D = h ∘ q

if and only if D is constant on every fibre q⁻¹(q(x)).

This is just X001's factorization argument applied to a product-valued verdict. It requires no probability model.

The tool quotient_guard.py checks the finite table directly. When the condition fails, it returns concrete states with the same retained representation and different decisions.

## Why this is useful to MHAC

The research programme repeatedly debates whether fields can be collapsed:

- certainty into urgency;
- acknowledgement into resolution;
- present state into historical transition;
- source identity into event identity;
- coordinate token into reference frame;
- social accommodation into technical success.

The right question is not “should these concepts always be separate?”

It is:

> **For which declared downstream decisions can this particular collapse be made without changing an answer?**

That changes anti-collapse from a permanent prohibition into a falsifiable design test.

A simple system is preferred when the collapse is decision-safe on its declared domain. Separation earns its complexity only when a witness state demonstrates a lost distinction.

## What the tool does

Given JSON-compatible rows, retained fields and decision fields, quotient_guard.py:

1. groups states by the retained-field tuple;
2. checks whether every group has one decision tuple;
3. emits exact conflict groups and witness row IDs;
4. lists omitted fields that vary within conflicting groups as **candidates for inspection**, not causal explanations;
5. optionally brute-forces inclusion-minimal sufficient retained-field sets across at most 12 candidate fields.

The field-search cap is deliberate. This tool is a small exact audit, not a feature-selection framework.

A passing result proves only that the supplied finite table contains no counterexample for the declared decisions.

## Nearby established ideas, and why they are not the same thing

### State abstraction in Markov decision processes

Li, Walsh & Littman (2006), *Towards a Unified Theory of State Abstraction for MDPs*, explicitly frame state aggregation around questions such as what information an abstraction loses and when an optimal policy is preserved. Their abstraction hierarchy preserves increasingly weaker structures such as the one-step model, Q-values or optimal actions.

Public author/Microsoft-hosted PDF:
https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/camera-ready-9.pdf

**Actually inspected for X004:** abstract, introduction and accessible sections describing abstraction criteria and optimal-action preservation.

Relation to X004: the concern is closely analogous, but an MDP abstraction must reason about reward and transition dynamics. quotient_guard.py checks only an explicit static finite table of declared decisions. It supplies **no optimal-control or learning guarantee**.

### Blackwell comparison of experiments

Blackwell-style sufficiency compares information structures by whether one can be obtained from another by a stochastic transformation and, equivalently under stated conditions, whether one is at least as useful across decision problems. Recent general-state treatments continue to study the exact conditions for these equivalences.

X004 consulted:
- M. Ali Khan, Haomiao Yu & Zhixiang Zhang (2025), “A simple proof of Blackwell's theorem on the comparison of experiments for a general state space,” *Economics Letters* 247:112146, DOI 10.1016/j.econlet.2024.112146.
- Prem K. Goel & Morris H. DeGroot (1979), “Comparison of Experiments and Information Measures,” *Annals of Statistics* 7(5):1066–1077, DOI 10.1214/aos/1176344790.

Relation to X004: these are genuinely decision-theoretic notions of information quality. Our checker has no priors, stochastic experiments, utilities or randomization and should not be called Blackwell sufficiency.

### Statistical sufficient statistics

In classical statistics, a statistic is sufficient for a parameter when, informally, it retains all sample information about that parameter; the Fisher–Neyman factorization theorem supplies a familiar criterion for dominated families.

Relation to X004: the word **sufficient** is useful English, but our “decision-sufficient finite representation” is not a sufficient statistic unless an explicit statistical model satisfying that definition is supplied. The similarity is data reduction without losing a specified kind of information; the mathematical objects differ.

## A small philosophical consequence

The anti-collapse posture can now be stated without fetishizing distinctions.

Two quantities deserve separate representation when collapsing them creates a fibre containing different required outcomes.

That gives the programme a way to distinguish:

- **necessary distinction** — an actual counterexample exists for a declared decision;
- **contingent distinction** — separate fields are currently useful but no decision conflict has been shown;
- **safe collapse on a bounded domain** — all supplied states in each fibre agree;
- **unknown** — the state table is incomplete, so no broad conclusion is warranted.

This is more disciplined than either “everything is context-dependent” or “reduce every state to the smallest convenient schema.”

## Exaptation opportunity

The distinction miner can retrieve candidate conceptual separations from prose. The quotient guard can then evaluate a deliberately constructed finite state table for a concrete interface or protocol.

The two should **not** be automatically chained into a magic ontology generator. A person/agent must still formulate the full states, retained representation and downstream decisions.

If later applied to CyberSand, radiCADSAC, Xenovection or another project, that would be a separate commissioned experiment. X004 does not modify those repositories.

## Limitations

- finite authored rows can omit the decisive counterexample;
- decisions are declared inputs, not discovered objectives;
- minimal field sets may be artifacts of correlated fixture fields;
- varying omitted fields are not automatically causal;
- dynamic systems need stronger preservation conditions;
- human interpretation cannot be reduced to a finite truth table without empirical justification.

**Disposition:** keep the quotient guard as a small reusable exaptation of X001 and the X004 distinction genealogy. Do not inflate it into a general theory of meaning.
