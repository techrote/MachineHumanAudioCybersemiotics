# C9: three remaining review bibliographies

This recovery closes the **reference-list access gaps** for the three reviews below.
It supplies **312 ordered reference occurrences**, without deduplication,
eligibility screening, independent human review, or extraction of empirical
results. These exports do not themselves establish completion of R005 or R006.

| Review | Verified source identity | Bibliography locator | Occurrences |
|---|---|---|---:|
| Totland | Jonas Totland, *Design Considerations for Auditory Alarms in the Process Industry: A Systematic Literature Review*, master's thesis, University of South-Eastern Norway, June 2021 | Printed/PDF pp. 42–47 | 47 |
| Edworthy | Judy Edworthy, *Medical audible alarms: a review*, JAMIA 2013, 20(3), 584–589; DOI `10.1136/amiajnl-2012-001061` | Printed pp. 588–589; PDF pp. 5–6 | 80 |
| Ruskin and colleagues | *ATC Signaling Systems: A Review of the Literature on Alarms, Alerts, and Warnings*, FAA report; ROSA P date 2020-09-01 | Printed/PDF pp. 55–79 | 185 |

`MANIFEST.json` holds source identities, precise retrieval records and hashes,
bibliography counts, per-page counts, first and last references, access outcomes,
and the hashes of the three exports. `access.jsonl` is the append-only capture
log of **22 actual public GET requests**, including failures and route discovery.
Each log entry records its requested URL, actual start/finish timestamps, HTTP
status, content type, retained response path and SHA256. Successful HTTP status
alone is not treated as successful document retrieval.

## Exports and interpretation

- `totland-2021-references.json`: all 47 bibliography occurrences, in source order.
- `edworthy-2013-references.json`: printed reference numbers 1–80, read down the
  left column then down the right column on each page.
- `ruskin-2020-references.json`: all 185 bibliography occurrences, in source order.

Every occurrence has a stable local `occurrence_id`, an `ordinal`, the original
`source_number` if present, complete `citation_text`, the source's individual
`citation_lines`, printed/PDF page pointers and line bounding boxes. Coordinates
are PDF points from the top-left of the page, expressed as
`[x0, top, x1, bottom]`. The source SHA256 applies to the entire PDF byte stream.

**Use `citation_text` and `citation_lines` as the authoritative bibliography
metadata.** Whitespace is normalized by joining PDF text-layer words; line breaks
and coordinates remain available. `bibliographic_parse_hints` provide mechanical
author/date/title splits and literal DOI/URL tokens for discovery. They are
explicitly unverified, can split a multi-sentence title incorrectly, and do not
repair line-wrapped identifiers. They must not be promoted automatically to
verified canonical source identities. Apparent errors, missing delimiters and
incomplete citations in the source are deliberately preserved.

The review identities were checked against their title pages and current
repository metadata. Several material distinctions remain explicit:

- Totland's NVA record lists Steven Mallam as **supervisor**, not coauthor. Its
  migration/import timestamps in 2025 do not change the thesis date of June 2021.
- Edworthy's issue year is 2013; its online-first date is 25 October 2012.
- The FAA PDF title page orders authors **Keith J Ruskin, Chase Corvin, Stephen
  Rice**. ROSA P metadata orders them **Ruskin, Rice, Corvin**. The manifest keeps
  both orders.

## Retrieval and access outcomes

### Totland: migrated USN repository

The original [USN handle](https://hdl.handle.net/11250/2764585) redirects to the
[NVA registration](https://nva.sikt.no/registration/019913c778ff-dc8521c4-eeb9-4fb2-ac17-83acb6271313).
The public publication endpoint returns its JSON metadata when requested with
`Accept: application/json`:

```text
https://api.nva.unit.no/publication/019913c778ff-dc8521c4-eeb9-4fb2-ac17-83acb6271313
```

The record identifies an `OpenFile`, file UUID
`02e585a1-2cd2-4b78-bf4d-b7ecdf7542e5`, with `download` and `read-metadata`
operations. The older `/download/.../files/...` route returned 403. Inspection of
the publicly linked NVA frontend identified the currently supported anonymous
filelink route:

```text
https://api.nva.unit.no/publication/019913c778ff-dc8521c4-eeb9-4fb2-ac17-83acb6271313/filelink/02e585a1-2cd2-4b78-bf4d-b7ecdf7542e5
```

That endpoint supplied a public download alias. An initial alias request with
`Accept: application/pdf` returned **406 JSON**, retained under the attempted
filename `totland-2021.pdf`; it is not a thesis PDF. Retrying the alias with default
content negotiation returned the actual **821,130-byte PDF**, retained as
`totland-2021-alias-response`. Its SHA256 is
`caf75fd9f71016b869d1c27aa238c56a8f302a4ae2ce4459647203432e8d600d`.
The temporary storage redirect's credential-bearing query is omitted from the
committed log. The stable public filelink endpoint can issue a new download.

### Edworthy: repository PDF

The PMC route returned a **203 challenge page**; the publisher PDF route returned
**403**; the Europe PMC `fullTextXML` endpoint returned **500**. These response
bytes and their provenance were retained. No challenge or access restriction was
bypassed.

The public [Europe PMC PDF link](https://europepmc.org/articles/PMC3628049?pdf=render)
successfully returned a **100,569-byte, six-page PDF**, SHA256
`e708a1d3a57082e3532bebfd6ec37631fe66bea8af1bf99858e7ec5e573c7cb2`.
The PDF's bibliography, rather than the separately retrieved indexed-reference
API, defines the complete list. Europe PMC metadata reports `isOpenAccess=N`;
public retrieval does not imply an unrestricted redistribution license.

### FAA review: ROSA P PDF

The [official ROSA P landing page](https://rosap.ntl.bts.gov/view/dot/59041) and its
[document link](https://rosap.ntl.bts.gov/view/dot/59041/dot_59041_DS1.pdf) were
retrieved successfully. The **1,196,825-byte, 79-page PDF** has SHA256
`fa14019c4a211467a5f9e1622b4d96306823e5ffb69bc1ac4bcd5458604097ec`.
Its SHA512 also matches the checksum published by ROSA P; the complete value is
in the manifest.

## Boundary verification

A separate AI subagent independently compared PDF word geometry, `pdftotext`
layout output and rendered bibliography pages. It obtained the same **47 + 80 +
185** counts. This is an **AI technical check**, not independent human review.
No reference spans a page or column boundary in these three lists.

The extractor explicitly handles the source's layout exceptions:

- Totland p. 44 has an unindented `IEEE 92(4): 742-758.` continuation within the
  Johannsen (2004) reference. Totland p. 46 has two unindented URL continuation
  lines within the UKEssays (2018) reference. Treating all three as fresh entries
  would inflate 47 references to 50.
- Ruskin p. 64 has a Hickling et al. reference starting at x75 rather than the
  usual x72. It remains a separate occurrence; an exact-x72 rule would miss it.
- Edworthy's p. 588 contains references 1–33 in the left column and 34–69 in the
  right. P. 589 contains 70–75 and 76–80 respectively. Full column height is
  retained while the footer is excluded.

## Reproduction

Source PDFs and all raw access responses remain outside the repository in
`/tmp/mhac-r005-reviews/`. The repository contains no full article or thesis copy.
The temporary paths are capture locations, not a promise of permanent storage;
future reproduction may require reacquiring the same source bytes. The manifest
and access log identify the required bytes by hash.

Run from the repository root, using Python with `pdfplumber` (the recorded
version is in each export):

```sh
python research/searches/auditory/recovery-2026-11-03/reviews/extract_r005_reviews.py --check
```

`--input-dir` may point to another directory containing the three source
basenames. Source SHA256 and total PDF page counts must match before extraction.
The checker verifies deterministic byte-for-byte export reproduction, expected
reference counts, Edworthy's complete numbering sequence and the exact reviewed
layout exceptions. Omitting `--check` regenerates only the three reference JSON
files. `fetch_r005_review.py` retains new responses and refuses to overwrite an
existing capture; its output is provenance, not a statement that a document was
successfully accessed.
