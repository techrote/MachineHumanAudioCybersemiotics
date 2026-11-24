# Stage 0 — applicability and overlap gate (limited GO)

**Checked 2026-11-05 UTC; accepted main `423649d18c54cbf90bf7bf79d49ba69b29f03848`.** Read `README.md`, `RAG.md`, `AGENTS.md`, `docs/PROGRAMME.md`, `docs/AGENT_RUNBOOK.md`, `docs/PROJECT_FOUNDATIONS.md`, `docs/RESEARCH_INTEGRITY.md`, `docs/EXPERIMENTS.md`, frozen protocol v1, live issue #62 (no comments), issue/PR inventories and linked artifact file sets. The main branch remains research-in-progress. No selected empirical corpus, accepted R012 output or human gate exists.

## Applicability

`docs/PROJECT_FOUNDATIONS.md`'s proposed chain *world → observation → estimate → semantic message → acoustic rendering* and observation/diagnosis distinction permit a **hypothetical** bench-monitoring message, e.g. “reading 48.0 PI, accepted under decision rule PI-R1 v1.” Neither such a message nor PI units exist in accepted MHAC interfaces; we introduce fictional, arbitrary units solely to ask a falsifiable logical question. If future R012 rejects derived conformity claims outright, this exercise becomes a counterexample, **not** an implementation demand. If the only intended input is an independently verified categorical event, a measured-value conformity decision rule may be irrelevant.

## Related ownership examined

| Active issue / PR | Owns | T017's narrower difference |
|---|---|---|
| #31 / #40 | signal reliability, priors, alert validity, response criteria | no measured-value acceptance interval with pinned rule |
| #34 / #37 and #38 / #39 | compositional source-event fields; negation/polarity | upstream rule authority is a different semantic field |
| #36 / #53 | persistent state vs discrete event; all-clear semantics | static fixed observation, not lifecycle arbitration |
| #41 / #42 and #45 / #46 | received audio channel and multiaxis acoustic cues | no acoustic experiment here |
| #47 / #48 | queue freshness and action deadlines | message delivery held current; actor permission always false |
| #58 / #59 | correlated alert evidence and false fusion | single measurement, not independent sensor fusion |
| #60 / #61 | observation-to-causal-diagnosis and remedy authority | no diagnosis of why a measurement has a value |

Live PR metadata, branch ownership, descriptions and changed-file inventories were checked. The #40, #53 and #61 code/test contents were additionally consulted; this is **not** an exhaustive adversarial review of all other PR source trees. Their definitions are treated as proposed, not accepted main-line authority.

**Gate result: LIMITED GO** for a small fictional *class-authority* falsifier, with no changes to any sibling PR. A strict **NO-GO** for audio-specific claims, metrological decision standards for real devices, a universal guard band and participant testing. If a reviewer finds existing code already implementing this exact pinned-rule + false-accept/false-reject oracle, retain this stage note and reject the duplicate work; do not force integration.
