# R006 live nine-publication admission preflight — 2026-11-10

**Refs #6. Read-only executable gate; not a new SCR, study, experiment, sample, selected corpus or human review.** Branch base: accepted main 1071c360e03246db72a7028bd654da9ae7795fea.

Run on a complete checkout:

    python research/screening/r006_live_corpus_gate_20261110/check_live.py
    python -m unittest tests.test_r006_live_nine_corpus_gate_20261110 -v
    python -m unittest discover -s tests -v
    python tools/validate.py
    python -m tools.build_record_fixtures --check

The script reads the **actual canonical nine** source, title/abstract and full-text records plus Integration-owned research/registry/generated/evidence-flow.json. It checks DOI identity, frozen Track E protocol, agent/decision attribution, revision sequence, source pins, stage chronology, performed/manifestation-bound reading for any decisive full-text decision and exact per-publication generated coverage. It permits later legitimate other batches instead of freezing global counts at zero. Its 13 synthetic mutation tests check false full-text promotion, wrong DOI, fabricated first human assessor, missing PDF manifestation/reading and stale exports. The existing four-candidate live auditor separately guards the original registration provenance and Kühne's later exclusion recheck.

The four initial accepted title/abstract decisions are already serialised: Becker 2025 (10.1145/3706066) and Romeo 2025 (10.1145/3711938) proceed to full text; Kühne 2020 (10.3389/fnbot.2020.593732) and Romeo 2023 (10.1109/RO-MAN57019.2023.10309631) were uncertain and also proceed. Current full-text statuses: pending, pending, exclude, awaiting_text, respectively. Kühne is source-located against the R004 FRONTIERS-PDF manifestation and its performed R006 reading. Others lack original-article source manifestations; the Romeo 2023 Zenodo script supplement is **not** the parent IEEE paper.

Five further publications were admitted to screening, not the included corpus: Nees 2016, Edworthy 2014, Arrabito 2004, Šabić 2021 and Stevens 2009. Their full-text statuses are respectively pending, awaiting_text, awaiting_text, pending, pending. Previous original article/author-manuscript access histories and partial tool-mediated readings are valuable, but canonical SRC records have no registered original-text manifestation. R005 transient PDF/XML hashes must not be re-labelled as stored original bytes or conflated with web-rendered editions.

**Scientific accounting at branch base:** TA 9; FT 5 pending / 3 awaiting text / 1 excluded / 0 included; publications/studies/experiments/independent samples admitted 0/0/0/0; Track E/G selected 0/0. Refresh counts from generated main exports after any merge. Discovery occurrences, author-described experiments and article phases are not admitted units.

**Highest leverage one owner/source action:** R004/Integration should establish approved lawful private source custody, acquire the precise Stevens 2009 Europe PMC original XML again, preserve actual bytes with original UTC, DOI, licence and SHA, and register a truthful SRC manifestation. R005 Draft PR #159 includes an offline verifier for a local XML but does not prove rights, retrieval or a performed semantic reading. R006 then performs genuinely source-pinned E1–E6 final reading. The original warning recognition experiment (author-reported N=36) is separate from its stimulus-selection task (N=40); cross-report Perry/Petocz sample overlap remains unknown. The prior PMC HTML reading and R005 XML checksum are not automatically equivalent manifestations. Frozen v1 §6.2 does not demand a second independent human screener, and none exists here.

**Ownership and readiness:** This change adds only R006-owned preflight code and tests; no canonical scientific record or shared generated file is modified. Integration owns export regeneration, independent technical review, guarded merging and exact-head and post-merge CI. R007/R008 have no selected-corpus-ready E/G publications. Passing preflight cannot establish source custody, scientific eligibility or empirical effect sizes; run full history-aware validation and fixture checks separately.
