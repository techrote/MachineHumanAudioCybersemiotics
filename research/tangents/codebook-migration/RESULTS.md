# MHAC-T012 — 34-case symbolic comparator matrix

Replay with `python research/tangents/codebook-migration/oracle.py --check`. [TRACES.json](TRACES.json) is independently scripted fictional event truth; [REPORT.json](REPORT.json) is a reproducible machine-readable summary; [MANIFEST.json](MANIFEST.json) stores the actual input SHA-256.

| Comparator | Offers | Wrong referent | Wrong priority | Wrong action | Invalid/unknown offers | Audio false compatibility | Unresolved | Omitted valid obligations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| silent_replacement | 31 | 7 | 8 | 9 | 7 | 10 | 3 | 3 |
| frozen_legacy | 29 | 1 | 1 | 3 | 7 | 10 | 5 | 5 |
| versioned_manifest | 13 | 0 | 0 | 0 | 0 | 0 | 21 | 14 |
| alternate_family_unknown | 0 | 0 | 0 | 0 | 0 | 0 | 34 | 27 |

**Strong counterexamples:** T04–T05 preserve cue identity while changing referent; T06–T07 preserve referent while changing action; T19 changes priority; T13/T24 are expired replays; T14–T16 are absent, forged or unknown labels; T27/T28/T32 demonstrate authoritative nonaudio fallback. T02/T08/T29 remain compatible/no-version-needed controls. All comparator counts reflect **symbolic offers** or withheld offers, not actual human hearing, recognition, action, burden or safety.

`false_compatibility_offers` counts audio-legend offers despite incompatible generation/receiver dictionaries. Verified external nonaudio fallback is not an erroneous audio-version claim. The versioned comparator's zero symbolic misbindings are **conditional on idealized trusted version and action-time state attestations** in the fixtures; it omits 14 otherwise-valid obligations. The alternate icon/voice comparator is intentionally unresolved (human transfer unmeasured), **not measured zero recognition**. The no-learned-cue case and truthful external-display comparator preserve a possible *reject versioning* conclusion.

**Boundary:** not accepted Track E/G evidence, no participant testing, no approved R012/R013 contract, no production or certified alert logic. External source-appraisal and consent gates remain outstanding. These counts are not comparative effect sizes.
