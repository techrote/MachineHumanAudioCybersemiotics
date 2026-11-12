# MHAC-T010: freshness is not an action deadline

**Exploratory synthetic-only research for [#47](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/47); not an accepted MHAC finding or a R012 schema.** Based on `main` `423649d18c54cbf90bf7bf79d49ba69b29f03848` (3 November 2026). Research check: 4 November 2026 UTC.

## Decision and boundaries

**Go, narrowly:** R012/#12 already requires stale and superseded message handling and acknowledgment distinct from resolution; #36 tests continuous/discrete playback and false all-clear; #43 tests addressee/actor binding. None of their current accepted outputs establishes the **queue-policy comparison** with independently truth-labelled durable obligations versus replaceable snapshots. Therefore the falsifier below adds one bounded question. It MUST NOT be adopted as the R012 lifecycle, nor construed as evidence for acoustic efficacy. If subsequent R012 work already demonstrates equivalent guarantees, stop and prefer that implementation.

## Reproduction

Run from repository root (Python 3.11+ standard library):

```sh
python research/tangents/freshness-action-deadlines/oracle.py --check
python -m unittest discover -s tests -p 'test_t010_freshness.py' -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

`FICTIONAL-TRACES.json` contains **30 explicitly fictional** cases, independently labelled for required versus released event IDs. `oracle.py` evaluates **five declared policy abstractions** on the same immutable fixture. It emits JSON to stdout, including SHA-256 of the fixture, per-case diagnostics and policy totals. The fixture SHA-256 at this checkpoint is `5485f22b6c46f5a774d4f4fff2547473f29d8e0096713ee9615b0374dce2f6d6`. Calculations use arbitrary integer logical time, not measurements of listeners, networks, hearing, action execution or real temporal thresholds.

See [SOURCES](SOURCES.md) for audited identities/access, [CONTRACT](CONTRACT.md) for operational semantics, [COMPARISON](COMPARISON.md) for model outputs and limitations, [PROTOCOL-SKETCH](PROTOCOL-SKETCH.md) for an unexecuted empirical study, and [DECISION](DECISION.md) for go/no-go and future handoffs. This package has no live registry entries, protocol edits, human subjects, production scheduler or audio renders.

**AI disclosure:** GPT-6 prepared this limited code and source-critical synthesis using public publisher/repository information, with self-run Python tests. It is not an independent human reviewer, empirical replication, R005/R006 screening or ethics authorization.
