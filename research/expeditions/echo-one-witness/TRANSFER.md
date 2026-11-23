# Candidate exaptation: an evidence-provenance envelope

**Proposal, not production/Track E/R012 schema.** This is an optional artifact for source-critical research agents or auditors, not an amendment to shared MHAC validators.

The minimum record would carry claim ID, claim type, expressed proposition, cited-source IDs, direct observation-root IDs, derived-from claim IDs, source reading extent, stance toward each source (supports / opposes / merely mentions / unknown), an **unknown ancestry flag**, and separate verification classifications.

A concrete **fictional** example:

~~~json
{
  "claim_id": "fictional-claim-17",
  "claim_type": "observation-report",
  "proposition": "fictional machine A reports a discrepancy",
  "declared_roots": ["synthetic-reading-0001"],
  "derived_from_claims": ["fictional-claim-02", "fictional-claim-08"],
  "reading_extent": "invented fixture only",
  "relation_to_sources": "paraphrase, not independent checking",
  "unknown_ancestry": false,
  "conditional_independence": "not-evaluated",
  "verification": "synthetic-only"
}
~~~

## Invariants

Emitted **message count** and **declared observation root count** are different fields. Neither is by itself **independent evidence count**. A copied claim can contribute novel argument without magically creating an independently sampled observation. A citation must not be silently treated as a vote for the cited proposition. Unknown ancestry must remain visible; a missing provenance chain is not a known false proposition or a verified new source.

An independence statement must cite a separate joint/causal model whose assumptions were examined. Source IDs are labels, not authentication; the source-reading act must be recorded separately from the fact of citation. Mechanical test agreement and agent rechecking are different from human editorial or peer review.

## Simpler competing candidate

**Do not make an independent corroboration assertion without evidence.** Keep output actionable and concise; place the longer provenance envelope in a secondary inspectable record. This alternative is consistent with T015's synthetic null where separate reporting used fewer fictional tokens than a lineage-narrating policy. If a full envelope proves unnecessary, accept that negative result rather than building an ornamental mechanism.

## Conditional handoffs

R006 would remain owner of actual publication/study/sample identity. X004 can compare lexical similarity with separately established ancestry; no automatic equivalence. R008/R011 can perform the remove-Brier test. R013/R014 may investigate how concise or expanded provenance cues affect future approved listening protocols, but no listener performance claim exists here. R017 can audit later manuscript uses of “multiple independent sources.” None of these future paths is authorized as a production change by this expedition.
