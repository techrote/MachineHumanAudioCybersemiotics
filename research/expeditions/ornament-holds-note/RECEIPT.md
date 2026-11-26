# Native execution receipt — 26 November 2026

One AI agent, Python 3.13.5, command `python laboratory.py --out audio` (assertions enabled), exit 0. Executed source Git blob 383014bd7fb081f18e5d0e8d10a17c415c1831e3 matches repository readback. 1,005 direct matrix/elimination comparisons; maximum absolute complex amplitude error 1.2080532582046505e-14 (tolerance 1e-9). Two tuned targets exactly zero on primary, branch nonzero; three invalid-input/singularity controls rejected. Detuning and branch-loss controls nonzero at original targets. Repeat rendering byte-equal, WAV headers and decoded payload verified, coupled primary slots 2/4 all zero, diagnostic left zero/right nonzero at both. Common gain 0.05226962487879539.

| WAV | Channels | Frames | Peak integer PCM | SHA-256 |
|---|---:|---:|---:|---|
| bare.wav | 1 | 40000 | 6851 | fbd0aff0284d4147cc09c6c628fc51a133e0a6fdd805853ed584fb3ce356cdfa |
| coupled.wav | 1 | 40000 | 4663 | 6c71110a64979bdf0cec43a05ae0e84a8b1f760743d58d6ae52916f70374cc5c |
| detuned.wav | 1 | 40000 | 6162 | ba70b95311b1255d8a45a1517022ec9fbcaa260160485c0d1418dfbc70dc5f01 |
| lossy.wav | 1 | 40000 | 4215 | 234a71abab6e7d14c338d1076d3f1bc534bb0b8419a5dd4709b2a1abf51f07f1 |
| witness.wav | 2 | 40000 | 19470 | e2c6a2518438ba1c759944908c04fb1856ef125231c4273045111cf9875f1bff |

Primary amplitude (nondimensional, unscaled), computed by the same source:

| Hz | Bare | Coupled | Detuned | Lossy |
|---:|---:|---:|---:|---:|
| 160 | 2.42821 | 2.72274 | 3.59809 | 2.46109 |
| 200 | 4.00000 | 0 | 0.53546 | 0.59469 |
| 240 | 1.87779 | 1.44843 | 1.43116 | 0.77938 |
| 300 | 0.76626 | 0 | 0.19033 | 0.19890 |
| 340 | 0.51621 | 0.89575 | 0.23494 | 0.50277 |

The oracle and renderer share parameter construction; matrix elimination is a distinct numerical route, not independent scholarly review. No full checkout validation, participant trial, hardware, time-domain solver or real-time plugin qualification. Audio regenerates locally; binary WAVs not committed. Exact-head CI and integration review remain gated.
