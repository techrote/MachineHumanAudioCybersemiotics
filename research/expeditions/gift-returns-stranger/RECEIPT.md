# Native qualification — 2026-11-25

Python 3.13.5, local container; twice executed laboratory.py, identical stdout (cmp success). Source Git blob abd485025a51415a9a67cfe0f68d3ee99d57441c. All simulation, closed-form, uniqueness, conservation and negative-control assertions passed.

| Seats | Edge schedules | Schedule/outcome pairs |
|---:|---:|---:|
|2|2|4|
|3|6|18|
|4|24|104|
|5|120|750|
|6|720|6492|
|7|5040|65562|

Four distinct 4-second stereo WAVs and one invariant mono sum, 16 kHz signed PCM16, 64,000 frames each. Exact payload readback, amplitude bounds, repeat hash consistency and samplewise sum equality passed. SHA-256 hashes:

```
keep-00.wav 98201d15cd41c7a4bf55705666b3961a07370d45c5cb34d8aaa3e3d420db090d
keep-01.wav 4a7a3c7221e8d048ba6649883e89e3f9c198b7d5c7d1c663d60e7ae2a8321458
keep-10.wav 54ec421fce36c3b34025bade0f48619a3fec1e968514486e31773a94fa188947
keep-11.wav bef27c5d2ab5000cde40a46fdf20091cd3e4db0a5535d91446b8f41313a34ac5
invariant-mono-sum.wav 60cb238f013b8539fb8e3845e751f495ccf6c5a189201f8a16070df7e8bf3ed7
```

No listening trial, physical playback, full repository CI or independent review claimed.
