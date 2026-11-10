# R005 → R004/R006: executable private XML custody preflight — 10 Nov 2026

**Refs #5; downstream #6.** Base accepted main: \`1071c360e03246db72a7028bd654da9ae7795fea\`. Frozen protocol v1 §§5, 6, 10–12 and search cutoff **2026-10-04** unchanged. This is an additive, offline verifier of **actual local source bytes**, not another provisional publication, new search hit, new screening decision, a full-text reading or an approved archival destination.

## Why this is the R006 throughput bottleneck

The already registered Stevens, Brennan, Petocz & Howell (2009) publication (DOI \`10.2478/v10053-008-0064-6\`, PMCID \`PMC2865004\`) has a source-backed R006 full-text E1–E6 preassessment. It remains **FT \`pending\`** because no approved, retained, hash-bound original source manifestation and matching performed-reading event have been registered.

Canonical existing source: \`SRC-R006-E-STEVENS-INFORMATIVE@1\`. Representative discovery: \`HIT-R005R-C1LOAD-EQ1-02138@2\`; EQ5/EQ7 appearances are duplicate occurrences, not new studies. The [accepted original-source receipt](../stevens-2009-original-route-2026-11-10/OBSERVATIONS.json) documents two **ephemeral** direct GETs of the Europe PMC fullTextXML (10 Nov 2026, 20:15:16.864 and 20:19:06.280 UTC), HTTP 200, **74,338 actual bytes** and SHA-256 \`1390d7a4def94ad6b0926a5f1ae2608999f31713fb3ee5dad20b9e3fcc52658b\`. The source record reports CC BY 2.5. Neither temporary response was retained. **An operator's new copy may have different bytes and must be rehashed.** This SHA is not an attestation of the separate PMC HTML view previously read by R006.

## Deliverable and exact boundary

\`research/sources/auditory/scripts/attest_primary_xml.py\` operates on an **existing lawful private local XML file only**, with no outbound request, download, login, source redistribution or repository write. It computes SHA-256 directly on the local bytes, parses JATS XML, verifies the exact DOI embedded in article front matter and checks the PMCID when present (absence is marked unverified), checks article body/back presence, and inventories actual section headings and exposed license hyperlinks. It rejects XML entity declarations and oversized/invalid files. It cannot validate the provenance of an operator-supplied timestamp, copyright authorization, edition equivalence or performed reading.

The operator must first establish a permissible **private retention location and license/attribution policy**. On that already obtained source, run from repo root with locally accurate details; do not copy the sample timestamp as a claimed new acquisition:

\`\`\`sh
python3 research/sources/auditory/scripts/attest_primary_xml.py capture \
  --file /approved-private-path/stevens2009-original.xml \
  --manifest /approved-private-path/stevens2009-receipt.json \
  --source-url https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML \
  --edition "Europe PMC JATS original-paper XML (verify specific edition)" \
  --acquired-at "ACTUAL-UTC-TIME-OF-THE-NEW-LOCAL-ACQUISITION" \
  --actor "ACTUAL-OPERATOR-IDENTITY" \
  --access-proof "ACTUAL-RETRIEVAL-RECEIPT-OR-LOG-IDENTIFIER" \
  --rights-note "ACTUAL-REVIEWED-RETENTION/ATTRIBUTION-LIMIT"
python3 research/sources/auditory/scripts/attest_primary_xml.py verify \
  --file /approved-private-path/stevens2009-original.xml \
  --manifest /approved-private-path/stevens2009-receipt.json
\`\`\`

\`capture\` uses exclusive creation and refuses to replace a prior receipt. \`verify\` rehashes the original local XML, checks the DOI and any embedded PMCID and rejects altered bytes or fabricated promotion flags. **Do not commit the original full article or unapproved private manifests to this public repository.**

## Explicit source identity and gate handoff

- **R004/Integration**: authorise/designate the appropriate private source location and applicable retention/attribution basis; independently acquire the *specific* licensed XML source, preserve actual response UTC/HTTP headers alongside the private original, run the attester, then register a truthful source manifestation and coordinate common exports. This R005 helper alone does **not** register SRC.
- **R006 exclusively**: use that registered source for actual source-pinned Methods/Results reading and frozen E1–E6 final adjudication. Separate the 36-person warning-recognition experiment, its auditory/visual conditions and the distinct 40-person pre-stimulus selection exercise; **do not** add N=36 and N=40 as one sample or assert that related Perry/Petocz studies recruited independent people. No human second assessor is claimed.
- **R005**: retain frozen EQ1 historical **4,200 / 9,368** incomplete search status, with live-index drift disclosed; C3/C4/C6/C7, full C5 and C9 gaps remain. No new SRCH/HIT or completed channel is created here. After R004 custody is supplied or explicitly blocked, the next independent research priority is a fresh immutable EQ1 query invocation with real response bytes/hashes or an unfilled C9 review bibliography, not an invented historical-page continuation.

Current canonical main remains **9 title/abstract decisions, 5 FT pending, 3 FT awaiting original, 1 FT exclusion, 0 FT inclusion, 0 admitted publications/studies/experiments/samples and 0 selected Track E/G**. This patch changes **no** canonical count, source record, source-owned author's branch, generated manifest or export. R007/R008 are not selected-corpus-ready.

## Qualification

\`\`\`sh
python3 -m unittest discover -s tests -p test_r005_primary_xml_attestation.py -v
python3 -m unittest discover -s tests
python3 tools/validate.py
python3 -m tools.build_record_fixtures --check
\`\`\`

The 13 new tests are synthetic fixture checks, including false DOI/PMCID, altered bytes, entity declarations, missing body, timestamp/URL contamination, false human or source-manifestation status, and receipt overwrite. Successful tests prove bounded software behavior **only**. Exact-PR-head Actions and Integration's separate source/rights review remain necessary; this is a Draft/HOLD handoff, not issue #5 or #6 completion.
