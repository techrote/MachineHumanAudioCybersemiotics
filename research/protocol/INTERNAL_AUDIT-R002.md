# MHAC-R002 internal audit (self-audit)

[Protocol](PROTOCOL-v1.md) · [Freeze record](FREEZE.md) · Record: `AID-R002-INTERNAL-AUDIT`

**Self-audit by the executing agent before the freeze commit.** The same agent prepared everything audited here, so this is a structured check against stated criteria, not independent review. It satisfies the repository's structural requirement that a completed `protocol` stage declaration name a performed internal-audit record; it does not establish scientific adequacy.

## Issue #2 acceptance criteria

| Criterion | Evidence | Result |
|---|---|---|
| Protocol v1 frozen with real date and commit; cut-off 2026-10-04 unless amended | [FREEZE.md](FREEZE.md) (date, digests, base commit; landing commit added after merge); protocol header and §1 | Met at merge; the landing SHA must be appended post-merge |
| Pilot exposure, query revisions, unresolved access gaps and concept revisions disclosed | [Pilot report](PILOT_REPORT.md) §2, §5, §9; [concept register](CONCEPT_REGISTER.md) | Met |
| Source-grounded novelty/overlap matrix treating novelty as a question | [Overlap matrix](../novelty/OVERLAP_MATRIX.md), [comparator record](../novelty/COMPARATOR_NEES_LIEBMAN_2023.md) | Met within stated reading limits (preprint, tool-mediated; several comparators abstract-only) |
| Estimands, pooling eligibility, dependence/missing data and non-pooling route specified before extraction-driven selection | [Analysis plan](ANALYSIS_PLAN-v1.md) §2–§9; two-pass cell formation §3 | Met |
| Realistic verification roles and AI disclosure; agent passes not called independent human screening | Protocol §6.2, §10; FREEZE roles; `AID-R002-*` records | Met; absence of human oversight disclosed as a departure from the 2025 AI position statement |
| No false preregistration; no registration, contact or submission | Protocol §1, §13; FREEZE | Met |
| Feasible priority corpus and execution batches without narrowing to open-access or favourable studies | Protocol §4 (access not a criterion), §5.3 fallback, §12 batches | Met; database coverage depends on the owner gate |

## Integrity checks performed

| Check | How | Outcome |
|---|---|---|
| Search transcription fidelity | Re-compared P-B3, P-A8 and M6 result lists in the export with the tool outputs in the session | No discrepancy found |
| Reading extent | Searched all R002 records for `full_item_read`; reviewed every `access_reason` | None asserted; every tool-mediated access is labelled as such |
| Quotations | Searched new documents for quoted strings of 20+ characters | Only titles and short labels |
| Attribution of project preference | Read protocol §2–§4 and glossary | Preference stated as a project constraint, never as an eligibility rule or Brier's view |
| Unverified bibliographic facts | Reviewed source records' `metadata_status` and identifier statuses | Prepass-derived and inferred identifiers marked `candidate`; DOIs inferred from URLs marked `candidate` |
| Platform-syntax claims | Reviewed reporting applicability rows | OpenAlex capabilities stated as unconfirmed general knowledge |
| Rejected-term check | Searched new documents for the owner's rejected autonomy adverb | Not used |
| Structural validation | `python3 -m unittest discover -s tests`, `python3 tools/validate.py`, fixture check | Recorded in the PR; any failure blocks the freeze |

## Known weaknesses carried forward

Single-agent conduct; no PRESS review; no bibliographic database search in the pilot; tool-mediated paraphrase as the only reading route; Nees–Liebman Version of Record unread; exposure to that review's results before freeze; and unresolved overlap with urgency-mapping, voice-anthropomorphism and semiotic-engineering literatures.
