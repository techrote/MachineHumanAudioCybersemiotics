# Search, selection and access strategy

[Protocol](RESEARCH_PROTOCOL.md) · [Data model](DATA_MODEL.md) · [Seed sources](SEED_SOURCES.md)

## Three lanes

**Brier:** author/name variants, core publications and editions, citations and reception. Track Brier's own claims separately from collaborators, editors and interpreters.

**Related theory/HCI:** sources needed for Peircean relations, second-order cybernetics, autopoiesis/biosemiotics, grounding, pragmatics/common ground/repair, semiotic engineering, formal information accounts and conventional cognitive/human-factors alternatives. Include substantive objections. Document purposive/theoretical sampling rather than claiming every adjacent discipline was exhaustively searched.

**Empirical audio:** speech, auditory icons, earcons, spearcons, sonification and hybrid interfaces; recognition, action, learning, retention, workload, interruption, uncertainty, urgency, severity, source attribution and perceived human likeness/affect. No requirement for the term cybersemiotics.

## Channels to assess in the pilot

Target disciplinary indexes/proceedings such as ACM Digital Library, IEEE Xplore, ICAD, relevant psychology and philosophy indexes, and broad citation databases where genuinely accessible. Supplement with publisher/author repositories, reference lists and forward citations. Open metadata services and web search can aid discovery; they are not substitutes for falsely claiming a subscription database was searched. Record actual platform/interface, not just database brand.

Searches must use the user's/agent's actual authorized access. Do not buy access, create accounts, bypass paywalls or redistribute restricted sources. Seek lawful author manuscripts, institutional copies and alternate editions; record version differences. Failed/429/403 requests are access failures, not absence of the article.

## Draft query families — not executed searches

```text
("cybersemiotics" OR "cyber-semiotics") AND (Brier OR "Søren Brier" OR "Soren Brier")
("cybersemiotics" OR "semiotic engineering") AND (critique OR criticism OR limitation OR communication)
(earcon* OR "auditory icon*" OR spearcon* OR sonification OR "auditory display*")
  AND (comprehension OR learn* OR retention OR workload OR error* OR response)
(speech OR "synthetic voice" OR "auditory warning*" OR "audio notification*")
  AND (uncertainty OR urgency OR severity OR anthropomorph* OR "human likeness" OR affect)
("common ground" OR repair OR pragmatics OR "symbol grounding" OR "semantic information")
  AND (communication OR interface OR machine)
```

MHAC-R002 must translate these into each platform's actual syntax, field scopes and limits. Broad recall and narrower complementary searches should be tested rather than over-constraining every paper to every concept. Include spelling/diacritic variants and relevant language/translation strategies. Record term evolution and why a query changed.

## Required search record

Stable search ID, lane, protocol version, pilot/production/update status, platform/interface, exact query, filters, coverage dates, actual run date/time, result count, hit IDs and export/file hash, pagination/completion status, agent/reviewer, access failures and notes. Preserve raw exports where permitted. A result count from a search preview is not a completed export. Never manufacture records from memory after the fact.

Track a hit separately from a publication: the same paper may occur in several channels. Deduplication retains all discovery provenance. One publication may report several experiments; several publications may reuse one sample. Link these levels explicitly before synthesis.

## Screening and retrieval

Apply empirical title/abstract and full-text eligibility as frozen. Keep uncertain eligibility pending, with a reason and next action. Record full-text exclusion reasons and unavailable reports separately. Do not treat lack of full text as proof of ineligibility. Report genuine dual-review status, adjudication and limits; a model checking its own extraction is not independent human review.

Read enough contiguous source material to support each claim. Verify tables, figures and supplements directly when needed; use page images when extraction is incomplete or visual detail matters. Record edition, printed versus file page and exact range. No abstract-only source may be marked fully extracted. Do not upload source books or large copyrighted excerpts to the public repo.

## Coverage and bias audit

Check retrieval against the verified core source list and relevant existing reviews, including the [Nees author publication record](https://www.lafayette.edu/our-faculty/people/michael-a-nees/) identifying the 2023 audio-alert review. The review is a discovery/overlap comparator until its full text and methods are examined. Search null results, disconfirming cases, publication families and relevant grey literature. Report access, language, indexing and selective-publication limits without numerical bias corrections that the data cannot justify.

Predefine completion by channels and screening state, not an arbitrary number of papers. Use bounded batches with checkpoints rather than silently truncating search results. If a necessary channel remains unavailable, state exactly what was not searched and narrow completeness claims.

## Refresh and amendments

At MHAC-R017, run a dated update from the baseline to the actual final-search date, including corrections/retractions and source-version changes where supported by authoritative records. Screen new hits and propagate material findings through extraction, analysis, claims, requirements and paper. Record negative updates as actual searches too. Do not change the baseline date retrospectively or describe a future search as completed.
