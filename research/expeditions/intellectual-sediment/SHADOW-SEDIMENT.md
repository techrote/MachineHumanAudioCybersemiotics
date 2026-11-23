# MHAC-X004 — shadow sediment: the noncanonical corpus is larger than it looked

This note records one exact branch/history observation from GitHub workflow run **#45246032759**, executed on 23 November 2026. It is an archival measurement, not a claim that branch material is accepted research.

The measured X004 source head was `c050ffc10c8ca4efbbd225bf056eae7f6a934577`; GitHub Actions tested a PR checkout at `edd1701215ecf856d860b3777b089aba3f7fd464`. X004's own directory was excluded.

## Path volume and unique content

At this observation:

| Layer | Markdown paths / documents | Text volume |
| --- | ---: | ---: |
| Current narrative HEAD | **128** | **121,777** tokenized words |
| Branch/history-only paths | **155** | **183,747** path-weighted words |
| Unique branch/history-only text blobs | **150** | **176,641** tokenized words |
| Exact duplicate-content shadow paths | **5** | included only in path-weighted total |

The duplicate-content correction matters. The shadow corpus remains large even after exact content deduplication: only five of 155 loaded paths duplicated another shadow blob byte-for-byte.

This does **not** mean 150 independent ideas. Shared ancestors, templates, sources and copied conceptual structures can produce different bytes.

## What kind of material is outside HEAD?

Coarse family counts for the 155 branch/history-only paths:

| Family | Shadow paths |
| --- | ---: |
| exploratory research | **108** |
| other / checkpoint and misc | 44 |
| evidence / retrieval | 2 |
| theory / analysis | 1 |

Fine-family counts:

- **94 tangents**
- **14 expeditions**
- 44 other/checkpoint material
- 2 search documents
- 1 analysis document

The accepted-main corpus therefore radically underrepresents the amount of exploratory work MHAC has attempted.

This is selection, not necessarily loss. Open branches can contain duplicated, failed, superseded, under-reviewed or deliberately unmerged work.

## The old hourly scouting branch is a major sediment layer

The highest-volume shadow witnesses are three research ledgers on `origin/research/hourly-scope-expansion`:

| Ledger | Tokenized words |
| --- | ---: |
| 2026-11-03 | **40,996** |
| 2026-11-04 | **39,736** |
| 2026-11-05 | **13,722** |
| Combined | **94,454** |

The ledgers repeatedly classify leads as **parallel / orthogonal / perpendicular**, record source provenance, identify counterpositions, and propose explicit stop/duplicate gates.

The November 3 ledger alone repeatedly separates endpoints that later tangents formalize:

- trust vs calibrated decision quality;
- semantic urgency vs interruption/delivery windows;
- source validity vs persuasive alarm sound;
- decision criterion vs message severity;
- recognition vs correct action;
- recipient repair vs acknowledgement;
- continuous state vs discrete event;
- silence vs verified all-clear;
- physical cue independence vs perceptual/semantic independence;
- sound audibility vs accessibility;
- isolated recognition vs change detection in a crowded scene.

This predates X001/X002's free-range expedition style. It supplies a concrete ancestor for the anti-collapse research operator rather than requiring a story of spontaneous same-day emergence.

## Shadow genealogies

Manual reading of open branches strengthens this:

### T003 — recipient repair

Open PR #35 separates delivery, interpretation, acknowledgement, action, resolution and repair state. Acknowledgement cannot promote understanding or resolution.

### T013 — historical presupposition

Open PR #55 makes **unsupported history ≠ false history** operational. An unobserved previous event remains unknown.

### T014 — post-emission correction

Open PR #57 requires **unknown action to remain unknown**, and separates cancellation from undo, correction offer from correction delivery, and policy closure from independent resolution evidence.

### T009 — multi-axis semantic crosstalk

Open PR #46 separates physical parameter control from perceptual/semantic independence and keeps human outcomes outside a synthetic mapping oracle.

These are noncanonical branches, but they demonstrate that the problem-solving style had already been elaborated into executable falsifiers before today's expedition wave.

## A moving archive, not an immutable dataset

Shadow counts changed during X004 without any change to the measured main corpus.

That is expected: `git --all` observes whatever remote branches are present in the CI checkout. New scheduled-agent work creates new shadow paths. For example, the newly opened X005 *Sound of Nothing* PR added a fresh branch-only expedition while X004 was running.

Therefore:

- a source commit alone does **not** fully identify a shadow observation;
- workflow run/time and visible remote refs matter;
- the frozen baseline JSON records the exact observed run;
- future comparisons should treat shadow growth as an event stream, not a deterministic function of main HEAD.

This is not a bug in the research question. It is a property of a live stigmergic work surface.

## What shadow sediment is good for

The strongest practical use is **negative RAG**:

> Before claiming a novel direction, search not only accepted main but also prior branch sediment for similar attempts, counterexamples, dead ends and unmerged machinery.

This does not give abandoned work authority. It gives later workers memory of what has already been thought through.

A useful retrieval result should say explicitly:

- accepted on main;
- open Draft/PR;
- abandoned/superseded;
- historical checkpoint;
- unknown current status.

Without that distinction, shadow RAG would launder rejected ideas into doctrine.

## What this result does not prove

The shadow corpus does not demonstrate:

- independent agent generations;
- conceptual originality;
- persistent machine identity;
- an emergent philosophy;
- scientific acceptance;
- usefulness proportional to volume.

It does establish something narrower and operational:

**MHAC's external intellectual environment is substantially larger than its current accepted tree, and later agents can in principle be influenced by a large noncanonical archive of prior explorations.**

That makes branch status part of the epistemology of the project, not merely Git housekeeping.
