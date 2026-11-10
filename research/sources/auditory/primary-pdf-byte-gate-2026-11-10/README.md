# R005 → R006: private original-PDF byte gate (10 November 2026)

**Refs #5; downstream #6.** Accepted source baseline: `7e2975466f5c3fb43eb7d099a879090bc5d24818`. This is **an executable source-custody bridge, not new research evidence, new PDF acquisition, eligibility adjudication, independent human screening, or a claim that any source was archived**. Frozen protocol v1 and search publication cutoff **2026-10-04** are unchanged.

## The precise blocking dependency

The first four canonical R006 title/abstract decisions were admitted previously; two more were merged via #132. The present canonical state is **six title/abstract decisions; one full-text exclude, one full-text awaiting original article, four missing FT decisions, zero FT inclusions, zero admitted studies/experiments/samples, zero selected Track E/G**. The two source texts with highest immediate leverage are the original 2025 papers. R005 already has selected page/section readings; **the remaining primary-source custody gap is a durable exact-byte source copy bound to one manifestation and a truthful acquisition/rights record**. This PR does not manufacture an original-file checksum, reading time, reviewer, or independent sample.

| Publication identity (not experiment/sample) | Source version, lawful public route and already accessed content | Existing reproducible discovery IDs | Remaining source gate |
|---|---|---|---|
| **Becker et al. 2025** DOI [10.1145/3706066](https://doi.org/10.1145/3706066), *ACM THRI* 14(2), Article 29, printed pp. 29:1–29:25 | [Hamburg author-hosted publisher-layout PDF](https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf). Previous [R005 original source record](../r006-primary-support-2026-11-10/BECKER-2025.json) documents bounded text §§3.1–3.7, Appendix E Table E1 and selected rendered pp. 29:8, 29:9, 29:24–25; article p.29:1 reports CC BY 4.0. | `HIT-R004-G06-03@1`, `HIT-R004-G06-04@1`, `HIT-R004-LK3-VOICE-NATURALNESS-TRUST-01@1`; also `HIT-R002-PA3-04` | Privately retain exact original PDF bytes and bind original acquisition UTC, SHA-256, actual edition and rights; R006 then examines E1–E6 and pre-study vs main independently. |
| **Romeo et al. 2025** DOI [10.1145/3711938](https://doi.org/10.1145/3711938), *ACM THRI* 14(2), Article 33, printed pp. 33:1–33:22 | [Chalmers public institutional PDF](https://research.chalmers.se/publication/546010/file/546010_Fulltext.pdf) with dynamic repository cover. Previous [R005 visual verification](../r006-romeo25-chalmers-render-2026-11-10/README.md) inspected PDF pages 5–10 / article pp.33:5–33:10, §§2.1–2.4 and figures/tables; article p.33:1 reports CC BY-NC-SA 4.0. Alternative [Heriot-Watt published layout](https://researchportal.hw.ac.uk/files/147098646/3711938.pdf) had partial text extraction. | `HIT-R004-G06-07@1`, `HIT-R004-LK3-VOICE-REPAIR-TRUST-01@1` | Retain one exact PDF, verify edition and cover, record hash/time/rights. Chalmers cover varies between responses: **URL is not immutable file identity**. R006 separately assesses online video pilot vs in-person maze and audiovisual confounds. |
| **Romeo et al. 2023** DOI [10.1109/RO-MAN57019.2023.10309631](https://doi.org/10.1109/RO-MAN57019.2023.10309631), *IEEE RO-MAN* pp. 2045–2050 | [Heriot-Watt original publication entry](https://researchportal.hw.ac.uk/en/publications/putting-robots-in-context-challenging-the-influence-of-voice-and-/): abstract/metadata only. [Zenodo version DOI 10.5281/zenodo.8042317](https://zenodo.org/records/8042317) is a **separate four-page utterance-script supplement**, successfully acquired and checksum-verified in accepted R005 evidence; it is not the IEEE paper. [KTH DiVA institutional author listing](https://kth.diva-portal.org/smash/person.jsf?pid=authority-person%3A75314) provides bibliographic identity/URN `urn:nbn:se:kth:diva-342054`, not proof of original Methods access. | `HIT-R004-LK3-VOICE-NATURALNESS-TRUST-02@1` | Original IEEE six-page report still unavailable through previously checked lawful routes; remain `awaiting_text`. Do not conflate supplement/article DOIs, 2023 online studies, 2025 video pilot or participant samples. |

**Access timestamp precision:** The present cross-source review/checkpoint was assembled **2026-11-10 15:24 UTC**. This is **not** an HTTP retrieval timestamp or an original-file acquisition event. Existing records give their own bounded original observation times and tool limits. No new PDF bytes, complete paper, audio samples, or lawful private retention were obtained during this increment. Two earlier Heriot-Watt/Helsinki 2025 direct-file routes responded HTTP 403; the 2023 IEEE route responded HTTP 202 with empty HTML in [accepted PR #130](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/130). Those results are **route-specific**, not universal proof of publisher unavailability.

## Independently rechecked original HTTP bytes receipts (historical, not newly fetched)

During this R005 gate audit, the [original GitHub runner log for Actions #42812437569, job #129816985315](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42812437569/job/129816985315) was independently read at source. Its three `MHAC_R006_PDF_RECEIPT` lines preserve the following **previously observed original HTTP instances** (the runner did not retain original file bytes):

| Actual runner HTTP Date UTC | Exact original-public-PDF instance | HTTP | PDF pages/bytes | SHA-256 of actual fetched bytes |
|---|---|---|---|---|
| 2026-11-10 12:03:09 | Becker 2025 Hamburg, DOI `10.1145/3706066` | 200, `application/pdf` | 25 / 10,436,314 | `e5a2429e47e15208e285c4f3c1aa35e86529b0591139ff36d46e94babe42f230` |
| 2026-11-10 12:03:12 | Romeo 2025 Chalmers, attempt 1, DOI `10.1145/3711938` | 200, `application/pdf` | 23 / 3,445,682 | `ab894fbe2b707df1a140320910ed71dc2799e200c99a15ad373b07c712a5ea21` |
| 2026-11-10 12:03:14 | Romeo 2025 Chalmers, attempt 2, same URL | 200, `application/pdf` | 23 / 3,445,682 | `1261fc33accc55c7098ddd59e4f507f95b4d79fa31e3a4b308feddfcb2a7c14c` |

The Becker runner lists its **read completion at 12:03:10.966 UTC**; the Romeo attempts report completion at 12:03:14.002 and 12:03:15.581 UTC, respectively. These are source HTTP/byte-acquisition observations performed earlier on GitHub Actions, **not** this R005 PR's new acquisitions, full research readings, or a durable private archive. The two Romeo digests differ even though URL, byte length and PDF page count agree; **no one of those hashes can be designated the canonical Chalmers version without the particular retained file**. A later source custodian may obtain a third digest. The tool in this PR verifies that custodian's *actual* local instance, not that the bytes must equal any one of the historical receipts.

This historical technical observation gives R006 precise original-file identities and a falsifiable acquisition receipt, but **not** lawful persistent custody, sample independence, an empirically qualified Methods reading, or a human reviewer.

## Executable acceptance bridge (R004/Integration as source custodian)

[`scripts/attest_primary_pdf.py`](../scripts/attest_primary_pdf.py) accepts an **already lawfully acquired and privately held local original PDF**. It validates a PDF file signature/EOF, hashes the **actual local bytes** incrementally, records byte count, edition, source URL, operator-supplied timestamp, access/right evidence and reading boundary. It writes a JSON-only receipt in **create-new-only** mode: it will not overwrite previous observations. It never fetches or copies PDF bytes, emits participant data or records a screening decision. A later `verify` checks the precise local bytes against receipt.

Example (illustrative placeholders; **not an executed original-file acquisition**):

```sh
python3 research/sources/auditory/scripts/attest_primary_pdf.py capture \
  --file /PRIVATE/verified-source.pdf --manifest /PRIVATE/source-receipt.json \
  --doi 10.1145/3706066 --edition "ACM THRI 14(2), article 29, 25 pages" \
  --source-url https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf \
  --rights-url https://doi.org/10.1145/3706066 \
  --acquired-at 2026-11-10T12:00:00Z --actor "actual operator identity" \
  --access-proof "exact authorized retrieval route/HTTP receipt held privately" \
  --rights-note "rights and lawful retention basis to be independently checked" \
  --reading-boundary "actual inspected article pages, or none"
python3 research/sources/auditory/scripts/attest_primary_pdf.py verify \
  --file /PRIVATE/verified-source.pdf --manifest /PRIVATE/source-receipt.json
```

The example time is explicitly **fictional**, not a source-access claim. An operator must replace every placeholder with genuine provenance. **Self-attested URL, rights, time, and reading extent are NOT independently verified** by the script; an output JSON cannot by itself establish legal permission, source authenticity, a human second screen, PDF completeness, an exact edition match or an eligible paper. The original must remain in rights-compliant private storage with an independently inspectable access path and custody log. Never commit restricted full articles or raw PDFs to this public repository.

## Validation and anti-fabrication controls

The issue-scoped synthetic tests check successful hash verification while rejecting altered bytes, non-PDF, missing source file, missing rights, insecure/credential-bearing URLs, timestamps lacking offset, future acquisition times, overwrite attempts and receipt schema/status promotion. No real empirical study, new publication/hit, search count, sound or external review is produced. Execute:

```sh
python3 -m unittest discover -s tests -p 'test_r005_private_pdf_attestation_20261110.py' -v
python3 -m unittest discover -s tests
python3 tools/validate.py
python3 -m tools.build_record_fixtures --check
```

## Exact handoff and remaining coverage

**R004/Integration:** select one lawful, retainable original manifestation per Becker 2025 and Romeo 2025, record real acquisition timing/HTTP source and rights evidence, run the attestation script against the privately retained bytes, independently inspect version/rights, and register the receipt/source manifestation through Integration-owned common records/exports. If the PDFs cannot lawfully be retained, report the precise source-access gate; **do not invent an original-file receipt**.

**R006 #6:** remains sole authority for article → phase/experiment → independent participant-sample identity and all frozen E1–E6/Track E–G decisions. Verify the source hash/edition and actual original-paper reading before a full-text decision. Romeo2023 remains `awaiting_text` pending the original report. No second human reviewer is created by technical tool checks.

**R005 #5:** C1 EQ1 remains uncompleted; the latest live page-42/43 check demonstrated index drift relative to historical page boundaries, preventing false append. C5 ICAD 2026 is already owned by an existing active draft; avoid duplicate edits. C9 included-report chaining is incomplete. Resume source-captured search progress only when a genuinely immutable original query/response run can be made. **No new canonical hits, title/abstract screens, included studies, experiments or samples in this PR**. #5/#6 remain open; #7/#8 have no selected corpus.
