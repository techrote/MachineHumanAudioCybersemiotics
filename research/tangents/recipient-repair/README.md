# MHAC-T003 — Recipient-initiated repair under deadlines

Issue: [#33](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/33) · Status: **exploratory synthetic-only research tangent** · Prepared: 2026-11-03 UTC.

## Objective and scope

Determine whether recipient-requested clarification can be distinguished from receipt, acknowledged interaction, reported interpretation, reported action, and hazard resolution without silently accepting stale answers, confusing source/event attribution, or allowing unbounded dialogue under a deadline.

**Nothing in this package constitutes accepted empirical evidence, an R012 state-model adoption, a real safety policy, acoustic software, real device control, a speech agent, or human testing.** Fixed time units, retry counts, and fallback status names are invented test conventions. A logical test pass does not imply comprehension, accessibility, effective communication or physical safety.

## Contents and reproduction

| Artifact | What it supplies |
|---|---|
| [SOURCES](SOURCES.md) | Candidate primary bibliography, provenance/access limits, contradiction and overlap. |
| [STATE-MACHINE](STATE-MACHINE.md) | Proposed fields, transitions, provenance, objections, rejection conditions and ownership. |
| [COMPARATORS](COMPARATORS.md) | One-way, repeat-only, structured repair and accessible non-audio alternatives. |
| [PROTOCOL-SKETCH](PROTOCOL-SKETCH.md) | Falsifiable future human-comparison outline, not executed or preregistered. |
| [DECISION-MEMO](DECISION-MEMO.md) | Conditional positive, null, negative and inconclusive handoffs. |
| [TRACE-CASES.json](TRACE-CASES.json) | 39 explicitly fictional positive/negative adversarial traces; no participant data. |
| [protocol.py](protocol.py), [test_protocol.py](test_protocol.py) | Standard-library deterministic model and negative/atomicity tests. |
| ../../../tests/test_recipient_repair_t003.py | Repository unittest discovery adapter. |

From repository root, Python 3.11+:

    python3 -m unittest discover -s research/tangents/recipient-repair -p 'test_*.py' -v
    python3 -m unittest discover -s tests -v
    python3 tools/validate.py
    python3 -m tools.build_record_fixtures --check

The isolated tests were exercised before publication using an issue-scoped offline copy (39 fictional cases, six unittest methods passed). This did **not** run the full repository tests or validators from a real checkout; the GitHub Actions exact-head job must establish those results. Negative cases reject malformed actions, and tests explicitly verify that invalid events do not partially mutate the model.

## Authority and boundaries

Read [AGENTS](../../../AGENTS.md), [RAG](../../../RAG.md), [programme](../../../docs/PROGRAMME.md), [research integrity](../../../docs/RESEARCH_INTEGRITY.md), [frozen protocol](../../protocol/PROTOCOL-v1.md), [experiments](../../../docs/EXPERIMENTS.md) and [human gates](../../../docs/HUMAN_GATES.md). This issue owns only its sharded tangent files and one test adapter; it does not change the frozen protocol, selected empirical/theory corpus, generated registries or R012–R014 design authorities.

The related [#30 failure attribution](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/30), [#31 epistemic calibration](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/31), and [#34 compositional semantics](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/34) remain separate questions.

**AI disclosure:** One GPT-6 agent used the connected GitHub repository, public IBM/publisher abstracts and offline deterministic Python checks on 3 November 2026. No independent human review, full-paper critical appraisal, eligibility decision, safe-listening assessment, preregistration or participant work occurred.
