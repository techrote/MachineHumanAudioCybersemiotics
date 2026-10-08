# MachineHumanAudioCybersemiotics

Foundational research for explicit machine–human audio communication: information, contextual state, uncertainty, urgency and action without dependence on performed human emotion.

**Current status: the MHAC-R001 record pipeline is implemented; live research remains not_started.** The seed reading list is not a reviewed corpus. Green CI means repository and record integrity, not scientific validity or effective human communication. See the [implementation record](docs/R001_IMPLEMENTATION.md) and live issue/PR acceptance evidence.

## Start here

| Entry | Purpose |
|---|---|
| [RAG.md](RAG.md) | Authority map, reading routes and evidence boundaries. |
| [Programme](docs/PROGRAMME.md) | Twenty dependency-linked issues, parallel lanes and completion gates. |
| [Preserved prepasses](docs/PREPASS_CHECKPOINTS.md) | Complete original packets, publication identities and remaining acceptance boundaries. |
| [KICKOFF.md](KICKOFF.md) | Paste-ready first-task and programme-continuation prompts. |
| [Agent instructions](AGENTS.md) | Scope, evidence integrity and execution rules. |
| [Research protocol](docs/RESEARCH_PROTOCOL.md) | Questions, review design and protocol-freeze requirements. |
| [Seed sources](docs/SEED_SOURCES.md) | Initial discovery leads and methodology references, with access caveats. |
| [Record schemas](schemas/README.md) | Exact v1 record fields, revisions and lifecycle contracts. |
| [Validation](docs/VALIDATION.md) | Offline commands, provenance/citation checks, exports and honest limits. |
| [Paper plan](docs/PAPER_PLAN.md) | Extended dossier, applied paper and reproducible research package. |

## Research objective

Study Søren Brier's cybersemiotics seriously enough to challenge it, and auditory interfaces seriously enough to challenge the project's own preferences. Maintain two tracks: a general critical investigation of Brier and related work, and an applied investigation of what that work contributes to machine–human auditory communication.

The working paper title is **From Signal to Situated Understanding: Cybersemiotics and the Design of Explicit Machine–Human Audio Communication**. The method combines a systematic empirical evidence map, a separately governed critical theoretical synthesis, and statistical meta-analysis only where justified. The result may support, narrow or reject candidate design ideas.

## Project direction, not a predetermined finding

The intended system is linguistically intelligible but perceptually non-human. Speech, learned motifs and continuous sonification are candidate components. The system should distinguish certainty, hazard, task consequence, urgency and requested action rather than perform worry or apology. This is a project constraint and research question, not a conclusion attributed to Brier. His name and the term cybersemiotics do not imply endorsement.

## Execution

Verify the actual merge and post-merge checks for [#1 — MHAC-R001](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/1) before starting [#2 — MHAC-R002](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/2). After the protocol is accepted, #3/#4/#5 may run in parallel. The full graph is in the programme. Issues #1–#18 form the internal foundational-research programme; #19 and #20 are separately gated external-review and real-participant extensions.

From the repository root, using Python 3.11 or newer:

```sh
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The validator retains the bootstrap checks and adds all sixteen record schemas,
typed revision references, reading/provenance checks, correction propagation,
evidence counts, citation bindings and deterministic exports. History comparison
uses an explicit prior snapshot or locally available accepted Git SHA; CI supplies
the actual base. The synthetic worked example contains a deliberate extraction
error that passes structure, demonstrating why source fidelity still needs review.

## Boundaries

No production voice engine, real device control, participant recruitment, external submission, reviewer outreach, paid acquisition or license grant is authorized by this bootstrap. Public GitHub content must not include restricted source books, personal participant data or private correspondence. See [research integrity](docs/RESEARCH_INTEGRITY.md) and [human gates](docs/HUMAN_GATES.md).

Baseline planning date and proposed initial literature cut-off: **4 October 2026**. Actual pilot, freeze and final-search dates must be recorded when they occur. An internal protocol commit is not external preregistration.
