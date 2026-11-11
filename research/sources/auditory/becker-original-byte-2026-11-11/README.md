# R005 → R006: Becker 2025 original-layout PDF direct-byte receipt — 11 November 2026

Refs #5, R006 #6. This is an **actual direct HTTP original-response acquisition**, not a saved source manifestation, publisher database search, new TA/FT decision, empirical extraction, independent participant assessment or human review. Frozen v1 eligibility and **2026-10-04** literature cutoff remain unchanged.

## Exact publication and source identity

Becker et al. (2025), *Influence of Robots' Voice Naturalness on Trust and Compliance*, *ACM Transactions on Human-Robot Interaction* 14(2), **Article 29**, printed **29:1–29:25**, DOI [10.1145/3706066](https://doi.org/10.1145/3706066). The [University of Hamburg institutional publication listing](https://wtmbib.informatik.uni-hamburg.de/Basilic/publis/928/) identifies the [lawfully public author-hosted, publisher-layout PDF](https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf). Its printed first page identifies the DOI, journal edition, copyright holder and **CC BY 4.0** licence. On **2026-11-11**, the public PDF web renderer was opened and printed first page visually inspected. That separate visual reading is not a raw-byte pin to the newly obtained HTTP response.

## Actual one-time original HTTP evidence

[Source-probe GitHub Actions job #130253391166](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42938201965/job/130253391166), head `33b25580a347e4866c0ce4a92a8faf8c8831f8a8`, directly fetched the publicly hosted PDF by Python urllib **without login, cookies, institution proxy, paywall bypass or payment**. Observations in [OBSERVATIONS.json](OBSERVATIONS.json) are taken from its `MHAC_R005_BECKER_PDF_DIRECT_RECEIPT=` stdout marker.

| Field | Actual value |
|---|---|
| Request UTC | 2026-11-11 01:20:21.272933 |
| HTTP Date | Wed, 11 Nov 2026 01:20:21 GMT |
| Finished UTC | 2026-11-11 01:20:23.038218 |
| HTTP result | **200**, `application/pdf`, PDF magic confirmed |
| Original body bytes | **10,436,314**, matching Content-Length |
| Original response SHA-256 | `e5a2429e47e15208e285c4f3c1aa35e86529b0591139ff36d46e94babe42f230` |
| Effective URL | Same original Hamburg URL; no redirect |
| Direct-test reading | **No text extracted and no sound inspected** |
| Original bytes retained | **No** (held in runner memory only, never committed) |

The [first scoped probe](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42937937920/job/130252528805) genuinely returned HTTP 200 and Content-Length 10,436,314, but its deliberately conservative 5 MB cap stopped at 5,000,001 bytes. It **did not** supply a complete original-body hash. The retry raised the cap to 12 MB after observing the response header; no extra search query, URL change or credentials were used.

## Source-reading extent and identity boundary

The older R005 [Becker primary-access memo](../r006-primary-support-2026-11-10/BECKER-2025.json) reports *separate*, selected web-assisted reading of §3.1–3.7, opening Results and appendices, with selected page images, and is not retroactively asserted to have used this exact hashed 10,436,314-byte response. The new direct byte acquisition is useful for later byte comparison, but a transient SHA does **not** establish durable custody, publisher source certification, or an actually performed Methods/Results reading tied to a retained manifestation.

Publication and procedure identity: one journal article reports a voice-selection pre-study (author-reported N1=60) and cooperative-game main experiment (author-reported N2=68). These are **not** automatically two independent sample admissions. The article's actual voice files were not heard. Previously registered discovery IDs (not new hits): `HIT-R004-G06-03@1`, `HIT-R004-G06-04@1`, `HIT-R004-LK3-VOICE-NATURALNESS-TRUST-01@1`, `HIT-R002-PA3-04`.

## Scientific handoff

**R006:** keep Becker full-text `pending` until exact-source retention/manifestation and independently documented source-pinned E1–E6 reading occur; decide publication versus experiments and independent samples itself. No new screening decision, study, outcome or participant set in this PR.

**R004 / Integration:** identify a permitted durable *private* storage location and retention basis; obtain a genuine source copy there, independently verify the actual byte count/SHA or preserve a new justified version, register source manifestation and performed-reading provenance; coordinate common indexes and R006 records. This public PR stores only the receipt. The CC BY 4.0 article statement is evidence of its published licence, **not** authorization from the owner to choose a storage policy or grant repository redistribution rights.

**Next R005:** original IEEE Romeo 2023 report remains unacquired, even though its Zenodo supplement was checked; EQ1 page 45 received 429 and beyond remains incomplete; unfinished C9 chaining/ICAD publication identity remain bounded gaps. Do not invent coverage or external database exports.

## Qualification

Source execution [Actions #42938201965](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42938201965) succeeded on the **probe** head, not this final documentation head. This branch replaces the one-time network test with offline-only receipt invariants and negative cases; final source head must be independently CI-qualified before Integration merge. AI-authored technical checks are not independent human screening.
