# Version 1 synthetic record fixtures

Every report, person, study, result, review and event timestamp here is fictional. The fixtures exercise the record contract and do not belong in the live research register.

Rebuild with `python -m tools.build_record_fixtures`; verify byte identity with `python -m tools.build_record_fixtures --check`. The generator first reproduces and hash checks all five recovered prepass snapshots, then explicitly converts them to `mhac-records/1`. `provenance.json` records the actual input identities and the limits of the conversion.

## Worked sequence

| Snapshot | Purpose |
|---|---|
| valid_before | Structurally valid initial 8 ms extraction, deliberately wrong against the source's 80 ms. |
| valid_correction_pending | Appended 80 ms correction; dependent claims and requirements await rework. |
| valid_corrected | Reappraisal, exact revision recheck, revised claim and requirement. |
| valid_source_invalidated | Source A invalidated; dependent releases withheld while source B remains usable. |
| valid_empty_live | An empty live register is explicitly not started. |
| valid_all_families | All 16 families; three search hits map to two reports; full-text screening includes A and leaves partially read B uncertain; participant readiness is blocked. |

The source texts are original synthetic fixture text, with form feeds separating file pages. The preserved example has two publications, one study, one experiment, one sample and two dependent outcomes. Full text access to report B coexists with reading only pages 1–2 of 4. A passing structural check proves neither source fidelity nor research acceptance.
