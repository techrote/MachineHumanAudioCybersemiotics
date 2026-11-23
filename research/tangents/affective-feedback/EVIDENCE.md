# MHAC-T018 evidence and incomplete verification

**Record date:** 23 November 2026; one GPT-6 research agent, primary publisher/preprint/project records and the connected GitHub tool. These notes are not independent review, actual participant data or a representative interaction sample.

## Sources consulted

- Nature open HTML: *Training language models to be warm can reduce accuracy and increase sycophancy* (Ibrahim et al., 2026), Abstract, main Methods/Results/Discussion relevant passages.
- MDPI open HTML: *Emotional Framing in Prompts Modulates Large Language Model Performance* (Gozzi/Fallucchi, 2026), Abstract, methods and Results including reported mean accuracy contrast.
- arXiv:2608.21242 abstract/metadata only for affective-context sycophancy. Full manuscript **not** read.
- PMLR proceedings page abstract and bibliographic metadata only for user detection/response to sycophancy.
- OpenAI's 2 May 2025 public postmortem for a **provider-reported** product incident.

These are findings about their original task domains, not measured claims about the user or the model in this conversation.

## Independent arithmetic spot-check performed

A separately authored elementary calculation evaluated the synthetic feedback coefficients (g = r+bkc) and 18 iterations with the same initial p=0.2 and common background q=0.025/e0=0.05:

| Fictional policy | Closed-loop gain | After 18 iterations (pressure) |
| --- | ---: | ---: |
| amplifying | 1.098 | ≈3.5347276544 |
| bounded | 0.59725 | ≈0.1179468409 |
| decoupled | 0.55 | ≈0.1055575587 |
| helpful | 0.54 | ≈0.0978276445 |

This spot check does **not** execute the deposited Python source, validate social psychology, or estimate real effect sizes.

## Code qualification plan

- A new Python file provides deterministic CSV/JSON output from invented parameters; local execution of that exact deposited file is not yet independently claimed.
- Tests cover gain/stability, closed-form versus recurrence, no-seed counterexample, beneficial response sign, boundary gain and invalid parameters.
- One tiny existing-test discovery adapter invokes the focused suite in repository CI. No new workflow, dependency or audio renderer added.
- After observed exact-head CI, append run ID, test count, and precise output here. Do not retroactively declare a test run executed when it was only intended.

## Open scientific gates

The real causal effect of expressed emotion on a model requires controlled repeated runs. The effect of model replies on user emotion/willingness requires actual human evidence and privacy/consent. The toy model's apparent "frustration" variable is just dimensionless arithmetic; there is no demonstrated mapping to any individual person's experience.

This tract remains separate from canonical MHAC evidence screening and the frozen protocol. All issues R008/R011 and R012–R014 retain their own gates.
