# R006 infrastructure self-review

**Date:** 3 November 2026. **Actor:** ChatGPT, GPT-6 Astra Pro. **Scope:** local
implementation commit `9eab42a6c8d899dbae9eb09b35758c188ddf5ed2` and the focused
follow-up containing the Hermann identity tranche. This is the implementing
agent's own review, not independent human screening or external scholarly review.

## Findings and disposition

| Finding | Consequence | Disposition and evidence |
|---|---|---|
| A source could carry an identifier-level DOI `conflict` while its broader metadata status remained `verified`; the candidate helper previously labelled that pair only `candidate`. | The explicit identifier dispute could be obscured in an identity worklist, although the helper never performed a merge. | Candidate output now preserves the DOI conflict. Regression: `test_identifier_level_doi_conflict_remains_visible`. |
| A malformed string declared as a verified DOI was ignored when normalization returned no DOI. | Such an assertion could evade the new cross-source DOI collision check. | The graph now rejects the malformed verified identifier with `SOURCE_IDENTIFIER`. It can remain candidate/conflict while the actual identifier is checked. Regression: `test_malformed_verified_doi_cannot_escape_collision_checks`. |
| R005 regenerated identity knowledge from sources added after its recorded execution time. | A normal rebuild after R004 could rewrite historical hit resolutions. | Fixed in `9eab42a`: use source revisions available at the original time and preserve later hit revisions. The original builder reproduces the preserved initial decisions. |

## Compatibility and completion gates

The optional screening `track` defaults to empirical for retained v1 records;
the existing synthetic fixtures need no rewritten history. Explicit empirical
track and the legacy absence produce the same flow. Switching tracks in place
and superseding across tracks fail validation.

Empirical inclusion counts exclude theoretical selections. The original
all-track screening aggregate remains available to the unchanged corpus gate,
so pending, uncertain and awaiting-text decisions in either track still block a
complete-corpus declaration. No required review, source-access or human gate was
removed. The Hermann tranche introduces no screening or stage-completion record.

Full-text decisions require a matching title/abstract proceed decision both at
their recorded time and in the current effective state. Later acceptance cannot
retroactively justify an earlier excluded or missing title/abstract stage.
Abstract-only access still cannot produce an asserted full-text decision without
reading evidence. The protocol's verification and retrieval requirements remain
substantive work for #6; structural tests do not perform them.

## Identity, history and remaining limits

The candidate helper does not merge stable IDs. It retains conflicting verified
DOIs, avoids fuzzy title matching, and requires known author/year fields for the
title key. Exact URLs remain resource matches requiring adjudication. A shared
verified DOI across distinct canonical sources is rejected until the identity
or disputed identifier is reconciled explicitly; file manifestations should not
silently inflate publication counts.

The record writer preflights the batch and preserves a longer existing history
when its original prefix matches. It refuses changed original facts or record
envelopes. This does not make a multi-file write transaction crash-proof, and it
does not validate the scientific truth of an asserted identity. The ordinary
append-only comparison, graph checks and review still apply.

The tests establish structural behavior, including contradictory and missing
evidence cases. They do not establish source fidelity, complete literature
coverage, human-review independence, study independence or research acceptance.

## Verification of this isolated follow-up

The full unittest suite passed **269 tests**. The frozen synthetic fixtures still
reproduce byte for byte. The Hermann ledger/table and its pinned record prefixes
pass the tranche builder's `--check`; its negative cases reject an unverified
source URL, a similar but different PDF filename, and a changed publication
count before any canonical record is written.

The historical R005 builder reproduced its original 2,373-record batch while
preserving all three new hit histories and the existing Hermann source byte for
byte. Registry validation with `--previous-ref
9eab42a6c8d899dbae9eb09b35758c188ddf5ed2` passed the append-only comparison on
this isolated snapshot: 3,957 records and 3,960 revisions, research state
`in_progress`. It still reports zero screening decisions, included publications,
studies and samples. These snapshot counts will change when the integrator adds
the other R005 work; shared exports must then be regenerated and revalidated.

## Follow-up from a separate agent's technical review

A separate collaborating agent reviewed the implementation and supplied three
concrete synthetic reproductions after the bounded identity tranche was
committed. This was an additional agent review of code, not human screening,
source verification or external scholarly review.

| Finding | Correction and regression coverage |
|---|---|
| Historical screening filtered decision timestamps but used current source aliases; a later B-to-A merge could retroactively supply A's title/abstract decision to an earlier B full-text decision. | Historical candidate grouping, full-text scope and supersession now resolve aliases as of the decision time. Regressions reject the later-merge repair and future alias targets, retain a valid earlier B scope, and allow aliases actually recorded before full-text screening. |
| URL parsing removed embedded line-feed, carriage-return and tab characters before DOI validation, silently changing a malformed asserted DOI. | Resolver URLs are checked before parsing and after percent decoding. Regressions reject all three controls while retaining deliberate trimming of surrounding whitespace. |
| A material source correction made an earlier title/abstract decision stale, but a full-text decision on the corrected source had no dependency on that prerequisite and remained usable. | Every full-text revision now retains a currency edge to the exact historical qualifying title/abstract pin. Invalidation propagates to full-text decisions; a later TA revision cannot retarget an older FT dependency. Regressions require an explicit current TA recheck followed by a new FT revision before usable inclusion is restored. |

The expanded unittest suite passes **279 tests**. The synthetic fixtures and
bounded Hermann tranche still reproduce unchanged. Registry validation against
`8830fad347c9b362a2d4ecc4f83cd533b01a8f2c` passes with history checked and the same
3,957 records / 3,960 revisions in this isolated snapshot. These corrections
alter validation and currency behavior; they create no new research decisions
and do not relax any completion gate. The separate agent reran all three original
reproductions against the fix and confirmed the expected rejection or stale
disposition in each case, with no remaining finding in that focused scope.
