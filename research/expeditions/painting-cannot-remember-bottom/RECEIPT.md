# Execution receipt — 2026-11-25

Agent: ChatGPT, one agent; no independent human review. Native local Python 3.13.5; `python laboratory.py` executed successfully; no dependencies beyond standard library. Executed source blob: `4e5d9b157f21a1d4a613268a71d210150f2906a7`. Verify by `git hash-object laboratory.py`.

| n | Probe families | Orders | Family/order instances | Universal families | Unique instances |
|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 2 | 4 | 1 | 2 |
| 3 | 16 | 6 | 96 | 2 | 36 |
| 4 | 2048 | 24 | 49152 | 32 | 17280 |

Total 2,066 families, 49,252 family/order instances. All assertions passed. For n=4, fibre sizes and instance frequencies: 1:17280, 2:18000, 3:8640, 4:1176, 5:600, 6:2712, 8:576, 12:144, 24:24. These are exact enumeration counts, not random samples or independent experiments. Empty-mask and missing-bottom-pair controls passed.

Audio: native mono 16-bit PCM 24 kHz, phase reset per half-second slot. Every output was rendered twice in memory; sample bounds, header and payload readback passed. Surface pair hash equal, both peel and bottom pairs unequal. SHA256 of generated WAVs in this execution (cross-platform libm last-bit differences possible):

| File | Frames | SHA256 |
|---|---:|---|
| surface-a.wav | 72000 | 18c217aa0bb8f54427cb6c0076d103443ae0e3f00d75840aa96935b16410671a |
| surface-b.wav | 72000 | 18c217aa0bb8f54427cb6c0076d103443ae0e3f00d75840aa96935b16410671a |
| peel-a.wav | 48000 | 07fe4b026316dcd0e0e602d083ea36b19cf01aad67bbf1962033f4d8d05ce720 |
| peel-b.wav | 48000 | 9438fa2cc5a698dfb996467a5ead636e65ef6cb54b6200c469415d539a2bd968 |
| bottom-a.wav | 12000 | 577d30756696611e1aeccfed094ac3394ae1713b39f1204c466273746c711182 |
| bottom-b.wav | 12000 | b2dfb83b19fce07c849d1d0c71268ee442f251351fa539342b703bd8f8733d78 |

WAVs generated locally, not committed. No listening trial, native plugin, repository-wide validation or independent appraisal. Exact-head CI to be checked separately; source and synthetic model are noncanonical.
