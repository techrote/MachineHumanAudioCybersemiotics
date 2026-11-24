# Executed local render receipt

Run on 2026-11-24: `python render.py audio`. Python standard library, local Linux container. No human listener; all material synthetic. Five WAVs, 24,000 Hz stereo PCM16, 57,600 frames each; 28,800 identical final left-channel frames. All assertions passed; each WAV reopened and payload matched. Repeated PCM synthesis matched within the run. Committed renderer Git blob matches local executed file: `7f51293c122f7aa6d9b69960163fda8f27e04c6e`.

| File | SHA-256 |
| --- | --- |
| 01-clean.wav | 6c2203bdab36a657b0b4eabdcf9ee5025a1083fb34cfa1c4e39893fbc1d4e541 |
| 02-interrupt.wav | 753526a6ea456800f7f05b293ba66d223e2ecdf4b1250ef6be9ccaa9eb3bc3ba |
| 03-repair.wav | 3a19154fa0009939b45cb83c81bd77f2bd1ef25edb9920b0909b199e9fbca9f9 |
| 04-revision-A.wav | a4eb6ac82df3f100179a8c0e6172310d2a03fab036bb00a72dfc899293f3c798 |
| 05-revision-B.wav | 8ea5aedb1a0b490b4481e80c497e64b7776a02f1d2fe56d97d0a07c6e3504598 |

The WAVs are distributed separately in the conversation's experimental package and reproducible from the committed source; no binary corpus or third-party material is committed. The hashes are observations from this environment, not a cross-platform guarantee. Full repository validation and independent review are not claimed here.
