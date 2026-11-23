# MHAC-X004 — execution and evidence ledger

**Status:** contemporaneous execution record for the far-horizon X004 tranche. Automated checks validate code/repository structure, not the theoretical interpretation.

## Repository scope

Issue: [#184](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/184)  
Draft PR: [#186](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/186)  
Branch: `mhac-x004/intellectual-sediment-atlas`

X004 writes only under `research/expeditions/intellectual-sediment/` plus `tests/test_x004_intellectual_sediment.py`. The X004 directory is excluded from both current and historical measured corpora.

No frozen protocol, central research registry, programme graph, selected evidence set, existing tangent branch, or other repository was modified.

## Qualified observed baseline

Workflow [#45246032759](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45246032759) completed **success** on source head `c050ffc10c8ca4efbbd225bf056eae7f6a934577` before the later quotient-guard/report additions.

Observed job output:
- **1,158 repository unit tests passed**;
- `tools/validate.py` → `structural_result: pass`;
- deterministic synthetic v1 fixtures reproduced byte-for-byte;
- main atlas, distinction ledger and shadow archive all emitted machine-readable CI summaries.

The dated result is frozen in [BASELINE-20261123.json](BASELINE-20261123.json).

### Current narrative corpus in that baseline

- 128 Markdown documents
- 121,777 tokenized words
- corpus SHA-256 `a72cabb0d87f5b252022e9bae8beded6d9ee7d283492e51f7280114ec13e3474`
- X004 self-excluded

### Shadow corpus in that baseline

- 155 branch/history-only Markdown paths
- 150 unique text blobs
- 5 exact duplicate-content paths
- 183,747 path-weighted tokenized words
- 176,641 tokenized words after exact-content deduplication
- 108 exploratory paths: 94 tangents + 14 expeditions

Shadow results depend on the remote refs fetched by CI at observation time. The same X004 source commit can produce a different shadow count later if branches are added, removed or changed. This is explicitly recorded rather than treated as deterministic commit state.

### Distinction ledger in the baseline

- 206 lexical boundary candidates
- 40 syntactically parsed left/right pairs
- candidates distributed across all six coarse corpus families

The ledger is retrieval scaffolding, not a validated ontology.

## External source inspection

X004 consulted public/author/publisher materials on:
- distributed cognition (Hutchins);
- active externalism (Clark & Chalmers);
- cultural attraction (Buskell; Claidière & Sperber);
- commonplace/miscellany practice (Vine);
- diachronic semantics (Kutuzov et al.; HistLens);
- AI research-agent ideation (Tang & Yang; Yu et al.; Si/Yang/Hashimoto);
- research programmes (Lakatos via SEP);
- stigmergy (Heylighen; Howison et al.);
- boundary objects (Star & Griesemer; Star);
- transactive memory (Peltokorpi);
- MDP state abstraction (Li/Walsh/Littman);
- Blackwell comparison of experiments;
- statistical sufficient statistics / Fisher–Neyman factorization.

Reading extent and limitations are recorded source-by-source in [SOURCES.md](SOURCES.md). Several entries are abstract-level only; they are not silently treated as full-text review.

## Manual branch reading

The analyzer was supplemented by direct reading of:
- accepted founding/protocol documents;
- X001 and X002;
- T018;
- open T003, T009, T013 and T014 branches;
- branch `research/hourly-scope-expansion`, especially its 3–5 November hourly scouting ledgers.

The manual genealogy is recorded in [GENEALOGIES.md](GENEALOGIES.md) and [SHADOW-SEDIMENT.md](SHADOW-SEDIMENT.md).

## Negative / contradictory results preserved

1. Naive lexical bridge ranking mostly rediscovered procedural repository vocabulary.
2. Expanded stoplisting still produced broad house-style terms rather than a clean conceptual genealogy.
3. Accepted-main exploratory history alone was only a same-day 23 November burst.
4. Branch archaeology revealed much older exploratory sediment, changing that interpretation.
5. Recurrence remains strongly confounded by explicit instructions, shared sources, cross-links, model priors and human selection.
6. “Persistent agent philosophy” is not established.
7. Boundary-object, transactive-memory and cultural-attractor vocabulary are kept conditional rather than adopted as universal explanations.

## Artifact boundaries

[sediment_map.html](sediment_map.html) is self-contained source and uses only the frozen baseline. Its actual browser rendering and accessibility have **not** been independently visually qualified in this execution.

[quotient_guard.py](quotient_guard.py) is an exact finite-table checker only. A passing finite fixture cannot establish statistical sufficiency, causal adequacy, dynamic-policy preservation or human comprehension.

## Final-head qualification

The branch continued after baseline capture to add the quotient guard, expanded reports, visual and execution ledger. Therefore **workflow #45246032759 is not the final-head qualification**.

Before merge, the exact final source head must again pass:
- repository unit tests;
- structural validator;
- deterministic fixture check.

Record the final workflow and merge/post-merge status in the PR/issue checkpoint rather than rewriting this historical baseline.
