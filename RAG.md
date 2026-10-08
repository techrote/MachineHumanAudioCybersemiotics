# RAG — authority and retrieval map

This file routes workers to the smallest relevant authoritative set. It is not a corpus of established research findings. Read [AGENTS.md](AGENTS.md) and the entire issue/comments first.

## Always read

| Document | What it controls |
|---|---|
| [Programme](docs/PROGRAMME.md) | Work packages, dependencies, paths and stage boundaries. |
| [Agent runbook](docs/AGENT_RUNBOOK.md) | Reconciliation, implementation, review, checks, merge and checkpoints. |
| [Research integrity](docs/RESEARCH_INTEGRITY.md) | Claim types, source truthfulness, AI disclosure, rights and review status. |
| [Validation](docs/VALIDATION.md) | Actual automated checks versus scientific and human gates. |

## Topic authorities

| Task | Required route |
|---|---|
| Infrastructure or records | [Data model](docs/DATA_MODEL.md) → [record templates](research/templates/README.md). |
| Protocol and novelty | [Protocol](docs/RESEARCH_PROTOCOL.md) → [search strategy](docs/SEARCH_STRATEGY.md) → [synthesis method](docs/SYNTHESIS_METHOD.md). |
| Prepass or checkpoint reconciliation | [Preserved prepasses](docs/PREPASS_CHECKPOINTS.md) → immutable original packet and preservation record → live issue/PR acceptance. |
| Finding sources | [Search strategy](docs/SEARCH_STRATEGY.md) → [seed sources](docs/SEED_SOURCES.md) → actual source/access records. |
| Critical reading and evidence synthesis | [Synthesis method](docs/SYNTHESIS_METHOD.md) → frozen protocol → selected corpus/extractions. |
| Design derivation | [Project foundations](docs/PROJECT_FOUNDATIONS.md) → accepted claim register and synthesis. |
| Experiments | [Experiments](docs/EXPERIMENTS.md) → [human gates](docs/HUMAN_GATES.md) → accepted design hypotheses. |
| Dossier/manuscript/release | [Paper plan](docs/PAPER_PLAN.md) → accepted analyses/designs → [human gates](docs/HUMAN_GATES.md). |
| Resume or handoff | [KICKOFF](KICKOFF.md) → target issue checkpoint → live PR/check state. |

## Authority layers

`docs/` holds the programme's methodological and engineering instructions. The frozen protocol and amendments under `research/protocol/` will become the method authority once MHAC-R002 creates them. `research/` will hold source, screening, extraction, appraisal, claim and design records; generated views are not independent sources. `paper/` will hold claims derived from those records. Search-result snippets and prior chats remain discovery-only.

Bootstrap directories may not yet contain later-stage deliverables. Their absence is expected until the owning issue is executed; never synthesize nonexistent files from an index entry. [research/README.md](research/README.md) defines the planned layout. The machine-readable [programme](programme.json) maps issue IDs and ownership.

## Retrieval discipline

Read the necessary complete source range, not disconnected snippets. Include edition and exact locators in extraction records. Keep source wording, researcher interpretation and proposed design implication in separate fields. Record inaccessible reports and missing text. Do not use a seed as reviewed evidence, a generated summary as the original, or an agent agreement as a human review.

## Current state

The MHAC-R001 record infrastructure is implemented; [live evidence](research/registry/README.md) remains explicitly not_started. No completed systematic search, frozen protocol, included study set, full Brier reconstruction, meta-analysis, manuscript, external review or participant evaluation is asserted. Run the validator for repository/record integrity; check the live issues and recorded merge/acceptance evidence before advancing the research. The [implementation record](docs/R001_IMPLEMENTATION.md) explains the prepass migration and remaining scientific boundaries.
