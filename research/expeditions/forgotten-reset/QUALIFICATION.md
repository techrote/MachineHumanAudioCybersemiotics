# Qualification — #232

2026-11-24, AI-assisted internal verification, not independent human review.

- Initial main: 495a98ca12bae467a507031f04931aa4254b1866. New issue-scoped branch only; no core manifests, CI configuration or freeze changes.
- Re-fetched committed reset.mjs (blob f575e7cba1e3c2b7d5f725ed01d8e2e3c44c94a3) and executed its exact source in V8 with a minimal process/console adapter. Output byte-matched committed results.synthetic.txt (blob c33d4c99299e8f8d827a9cbaf080bc060a64b409). Not a clean Node checkout.
- All 66,281 labelled ordered map pairs across n=2,3,4 considered; all 52,081 ordinary-synchronizing cases assessed for one-loss robustness (42,091 robust; 9,990 impossible). Every found one-loss witness replayed by explicit deletion branching; every impossible case closure checked. All 3,024 direct trace checks, family n=2..10 and 62 larger one-loss construction checks passed.
- Separate Python frozenset implementation run locally; all 54 populated histogram bins matched JS results exactly. Local source Git blob 3be1d23b947581b23361a9d91036787266aa844a matches committed crosscheck.py.
- Example CLI using `node reset.mjs --solve '[[1,2,3,0],[0,1,2,0]]' 2 --certificate` tested using V8 adapter: impossible, 58 closure states. A budget exit is explicitly distinct from impossibility.
- Local audio generator source blob 2dab7597edf6bbb854c0a28a3b0316d993382d54 matches committed render.py. Two complete local runs byte-identical. 16 kHz, stereo, signed 16-bit PCM. The samples are original integer triangular waveforms with cell envelopes and state-index pitch mapping. No third-party recording, no listening study, no claim of perceptual equivalence.

| WAV | Frames | Terminal L/R | SHA256 |
|---|---:|---|---|
| ordinary-one-loss.wav | 31200 | 0/1 | 44875834c63984cf77976a193385ab50ce517b784828d9d714f04e48f8d9f613 |
| robust-one-loss.wav | 48000 | 0/0 | 4f4373dfc71e5330af673cf02677e7b8dfacfc8d67be8a07143ff7f14a4ae084 |
| robust-two-loss.wav | 48000 | 0/2 | c431a95aab482d93eaac1b31bbb994d617b8ee69893c09fd7d74d4fe8289bdfd |

Audio files regenerated on demand; not committed as binaries. Left=nominal, right=omission; deletion positions are zero-based. For the first two cases omit position 1; third omits 13 and 14. All start in state 0; each mathematical reset claim instead quantifies over *all* starting states.

Remaining: clean Node checkout reproduction, final-head repository-integrity CI and independent review. The existing repo workflow is not claimed to exercise this isolated JS/Python expedition. No merge or core scientific acceptance. The issue remains open; no human participant authorization required for these synthetic checks.
