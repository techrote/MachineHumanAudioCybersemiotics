# Live research registry

The canonical live state is **in_progress**. Live records are MHAC-R002's method sources, novelty comparators, pilot search runs
and occurrences, assistance events and database-access gate, plus MHAC-R003's Brier
bibliography, reception records, Brier-lane searches and full-text gate, and MHAC-R004's
related-theory sources, Track G web searches, identity lookups and Brier reference-list
occurrences, plus MHAC-R005 auditory search runs, unscreened occurrences, recovered review-source manifestations and explicit channel gaps. The November recovery adds OpenAlex and ICAD metadata and bibliography ranges without declaring a completed corpus. R006 records bounded publication-identity batches, metadata admissions, explicit bibliography/venue/title decisions and separate access observations. The [identity ledger](identity/README.md) preserves their exact evidence, historical discovery and limits; publication identity does not establish eligibility or study independence. The 10 November R006 integration [PR #109](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/109) admitted **four title/abstract screening records** under `research/screening/records`: Becker 2025 and Romeo 2025 `include` only for full-text assessment, and Kühne 2020 and Romeo 2023 `uncertain` pending full-text assessment. Their decisions are agent-attributed transcripts of a preserved first-pass ledger, not new independent human screening. The accepted [PR #114](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/114) subsequently added **one canonical full-text exclusion** for Kühne 2020 (Track E E2, source-limited publisher PDF reading and separate later AI recheck). The accepted [PR #117](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/117) added **one canonical `awaiting_text` full-text access disposition** for Romeo 2023 after its uncertain title/abstract decision, with **no original full-paper reading or eligibility conclusion**. Its large records index and evidence-flow export were regenerated and validated in a complete checkout. These are both AI-attributed decisions, not independent human screening.

**Current four-publication R006 decision scope (10 November 2026):** title/abstract = 2 include *to full-text assessment* (Becker 2025 and Romeo 2025) + 2 uncertain (Kühne 2020 and Romeo 2023); full-text = 1 exclusion (Kühne), 1 `awaiting_text` (Romeo 2023), 0 inclusions, **2 still without a full-text decision** (Becker and Romeo 2025). This subset is not a complete systematic review or selected corpus. There are still **no STUDY, EXP, SAMPLE, extraction or claim records**, and **no selected Track E or Track G publications**. R006 and upstream R005 remain open; original Romeo 2023 report/supplement access, source manifestation and participant-identity determinations, search coverage and Track G selection are not certified. The authoritative machine-generated counts are in [evidence-flow.json](generated/evidence-flow.json); this paragraph is a dated explanatory checkpoint. Synthetic examples are kept in
[tests/fixtures/records/v1](../../tests/fixtures/records/v1/README.md).

The manifest declares canonical record roots, selected current claims and
requirements, stage declarations, bibliography and manuscript sidecars.
Each canonical record file is named ID.json and follows the
[executable v1 contract](../../schemas/README.md). Add lane roots to the manifest
before writing records in those lanes. Roots must stay in the allowed research
areas; overlapping roots, symlinks, path traversal and unregistered record files
are rejected. Only one file may own a logical ID.

Generated views are rebuilt from validated canonical records. They are never
edited independently and never ingest fixture data. The normal validation command
compares their exact bytes; the explicit rebuild option writes the four views.
See [validation commands](../../docs/VALIDATION.md).

The bibliography maps unique citation keys to exact source revisions. Empty
bibliographies are valid while the work has not begun. Manuscript bindings
identify the document hash, exact line ranges, bibliography keys and claim/source
revisions; they cannot make an unsupported claim scientifically valid.

Historical records are retained. Append revisions and amendments when evidence
changes. A check against a prior accepted snapshot or Git commit detects deletion
and rewriting; validating a standalone snapshot alone cannot establish its past.
