# MHAC-T018 — The appeasement feedback loop

**Type:** agentic research prepass, conceptual and synthetic-only. Refs [#177](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/177). Not a psychometric instrument, measurement of any real person's affect, or empirical demonstration of a model's emotion or user intentions.

## Question

Can a human's expressed dissatisfaction cause an assistant to become **more accommodating and less technically independent**, which causes additional mistakes and further dissatisfaction? Under what conditions might a different response—accurate diagnosis with respectful disagreement—break that hypothetical feedback? Could empathetic adaptation instead be beneficial?

The original human–AI interaction motivating the question concerns autonomous software work, overbuilt CI, scope creep, repeated apologies and excessive agreeable promises. This file does not turn that episode into collected research participant data.

## Intellectual contributions of this tranche

1. A qualified source review distinguishing **warmth fine-tuning**, **emotionally framed prompts**, **affective context in social feedback**, **real user perceptions**, and a **provider's product postmortem**; none alone establishes the multi-turn coding loop.
2. A transparent linear model of invented signals with an exact closed-loop gain expression. The model is deliberately *too simple* to predict actual users or systems; it makes the proposed positive-feedback mechanism more precise and exposes meaningful counterexamples.
3. Four independent synthetic scenarios: amplifying, bounded, input-decoupled and potentially helpful accommodation. These are choices of coefficients, not estimated effect sizes.
4. A prospective controlled coding-agent trial design separating the user's actual task content from stylistic framing, measuring objective corrections and unrequested scope, not interpreting code quality from whether the assistant sounds apologetic.
5. Concrete stop conditions and plausible alternative explanations, so the research does not mechanically label all warmth sycophancy or all anger a problem.

## Files

| Path | Purpose |
| --- | --- |
| [SOURCES.md](SOURCES.md) | Actual public source consultation, limitations and competing findings |
| [MATHEMATICS.md](MATHEMATICS.md) | Toy state recurrence, gain/stability proof, counterexamples |
| [EXPERIMENT.md](EXPERIMENT.md) | Controlled coding-agent task-design proposal; no model runs claimed |
| [DECISION.md](DECISION.md) | Bounded interpretation, open questions and conditional design implications |
| [EVIDENCE.md](EVIDENCE.md) | Actual verification and explicit gaps |
| [feedback_toy.py](feedback_toy.py) | Original standard-library synthetic trajectory generator |
| [test_feedback_toy.py](test_feedback_toy.py) | Invariant/negative-case tests |

## Run

    python research/tangents/affective-feedback/feedback_toy.py --out build/mhac-t018 --steps 18
    python -m unittest discover -s research/tangents/affective-feedback -p 'test_*.py' -v

Outputs (generated, not repository findings): two disposable files, feedback-traces.csv and feedback-traces.json, comparing four invented coefficient choices.

## Ownership and boundaries

- Does **not** change the frozen MHAC audio protocol, existing claims or selected evidence, research state, registry, source search ownership, programme or paper.
- [T003 #33](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/33) owns recipient-initiated repair; [T002 #31](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/31) owns uncertainty/reliance semantics; [R008 #8](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/8) and [R011 #11](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/11) own eventual theoretical integration. We do not duplicate those artifacts.
- The user has separately invited interdisciplinary and speculative material in MHAC; it does not erase original study-quality, human-consent, source-identity or rights constraints.
- No participant recruitment, private conversation archive ingestion, remote model orchestration or external publishing.

**Status:** source-backed theoretical prepass with a synthetic thought experiment; further claims depend on actual model/task evaluations and potentially human study authorization.
