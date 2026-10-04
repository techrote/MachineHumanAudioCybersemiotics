# Research implementation programme

[Home](../README.md) · [RAG](../RAG.md) · [Runbook](AGENT_RUNBOOK.md) · [Machine-readable graph](../programme.json)

## Scope

An auditable foundational metastudy, critical theoretical analysis, broad research dossier, applied paper, evidence-to-design framework and prepared empirical agenda. Eighteen core work packages precede two genuinely human-gated extensions. Production TTS/sonification software is outside this programme except minimal schemas, fixtures and analysis tools needed to express and test the research specification.

The bootstrap creates this plan, real GitHub issues and baseline integrity CI. It does not claim to have executed MHAC-R001 or the research. All issue states must be reconciled live.

## Work packages

| ID / issue | Deliverable | Dependencies | Ownership / parallel lane |
|---|---|---|---|
| MHAC-R001 [#1](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/1) | Registries, provenance validators and reproducible CI | Bootstrap | tools, tests, schemas, registry foundation |
| MHAC-R002 [#2](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/2) | Pilot, novelty audit and two-track protocol freeze | #1 | protocol, pilot searches, novelty |
| MHAC-R003 [#3](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/3) | Brier bibliography, editions and lawful access | #2 | sources/brier, searches/brier |
| MHAC-R004 [#4](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/4) | Related theory/HCI and contrary positions | #2 | sources/related, searches/related |
| MHAC-R005 [#5](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/5) | Auditory empirical search and retrieval | #2 | sources/auditory, searches/auditory |
| MHAC-R006 [#6](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6) | Screening and publication–study–sample identity | #3, #4, #5 | screening and identity integration |
| MHAC-R007 [#7](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/7) | Brier close reading and reconstruction | #6 + core access | extractions/brier, analysis/brier |
| MHAC-R008 [#8](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/8) | Critical comparison of alternative accounts | #6 | extractions/related, comparisons |
| MHAC-R009 [#9](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/9) | Empirical extraction and appraisal | #6 | empirical extractions, appraisal |
| MHAC-R010 [#10](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/10) | Evidence map and conditional quantitative synthesis | #9 | analysis, generated evidence |
| MHAC-R011 [#11](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/11) | Integrative critical synthesis and subtraction test | #7, #8, #10 | synthesis and integrative claims |
| MHAC-R012 [#12](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/12) | Contextual-state and lifecycle specification | #11 | design/state-model |
| MHAC-R013 [#13](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/13) | Auditory hypotheses and implementation contracts | #12 | design/communication |
| MHAC-R014 [#14](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/14) | Experiment protocols and synthetic rehearsal | #10, #13 | experiments/protocols and simulation |
| MHAC-R015 [#15](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/15) | Extended general dossier and reading guide | #11 | dossier; parallel with #12–#14 |
| MHAC-R016 [#16](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/16) | Integrated paper and reproducible figures | #13, #14, #15 | paper |
| MHAC-R017 [#17](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/17) | Adversarial audit and final search refresh | #16 | review/internal and scoped corrections |
| MHAC-R018 [#18](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/18) | Internal research package and design handoff | #17 | release, indexes and completion reconciliation |
| MHAC-R019 [#19](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/19) | Actual external human critique and response | #18 + authorization/feedback | Deferred human gate |
| MHAC-R020 [#20](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/20) | Authorized real pilot and evidence-led extension | #14, #18 + readiness/participants | Deferred human gate |

## Dependency graph

```text
Bootstrap → 1 → 2 → {3,4,5} → 6 → {7,8,9}
                                      9 → 10
                              {7,8,10} → 11
                                 11 → 12 → 13 → 14
                                 11 → 15      ↑
                                         10 ──┘
                               {13,14,15} → 16 → 17 → 18
                                                      ├→ 19 [human]
                                               {14,18}→ 20 [human]
```

## Acceptance stages

**Infrastructure:** repeatable checks and record models exist; live research may still be empty.

**Protocol:** pilot exposure and access constraints are disclosed; empirical rules frozen, theoretical revisions governed; no false preregistration.

**Corpus:** searches and identity/selection decisions auditable; coverage-limited inventory does not imply unread core texts were analysed.

**Analysis:** primary-source reconstruction, alternatives, evidence map and conditional pooling are complete; uncertainty and contradictory evidence retained.

**Foundation:** synthesis identifies what changes under the remove-Brier test; state model and requirements are traceable and provisional where necessary.

**Internal package:** paper, general dossier, reproducibility bundle and experiment protocols pass internal audit. This is not external peer review, participant validation or a doctoral credential.

**External extensions:** actual authorizations, reviewer feedback and participant evidence are required. Preparatory PRs cannot close these gates.

## Scheduling and shared ownership

Parallelize #3/#4/#5 and later #7/#8/#9 only after their actual prerequisites are accepted. #15 can accompany #12–#14. Use per-source/per-issue records, not a shared frequently rewritten monolith. Each worker owns a branch and disjoint paths; one integrator regenerates shared indexes and programme status after rebasing onto live main. The validator checks a DAG, not scientific readiness.

Issues can be split into bounded implementation PRs when necessary. Use `Refs` until all acceptance conditions are met. Record new dependencies explicitly, avoid cycles, and do not close a parent because a scaffold landed. After #17 finds material new evidence, targeted correction work must complete before #18; earlier results are not immutable conclusions.

## First ready work

After the bootstrap PR is merged and its checks succeed: #1 only. #2 follows #1. The first three-way parallel wave is #3/#4/#5, not before the protocol. No GPU, physical hardware, paid service or participant recruitment is needed to start.
