# Native execution receipt — 2026-11-26

Command: python laboratory.py /mnt/data/MHAC-Line/audio (stdout redirected to receipt.json). Python 3.13.5, standard library. One GPT-6.2 agent; no independent review or real listener.

Source SHA-256: 770cf6fb4314f9820719151f8711cec27f1498ba3a8e560f580c9f8d0ec05e86
Local Git blob: 89079ea0868dd80f9ae08922bb71d384465ab98e

PASS: exact integer geometry at seven levels, normalized endpoints and retained parent vertices, direction counts, rational length, 35 weighted direction comparisons, four rejected invalid inputs. All five rendered WAVs are deterministic on rerender, distinct by hash, bounded at gain 0.30 and passed header and complete PCM readback. All 16 kHz mono PCM16.

| Depth | Edges | Horizontal | Vertical | Length |
|---:|---:|---:|---:|---:|
|0|1|1|0|1|
|1|5|3|2|5/3|
|2|25|13|12|25/9|
|3|125|63|62|125/27|
|4|625|313|312|625/81|
|5|3125|1563|1562|3125/243|
|6|15625|7813|7812|15625/729|

| WAV | Frames | PCM peak | SHA-256 |
|---|---:|---:|---|
|d0-duration.wav|32000|9829|1a6cdeab0b3992a3c4bd43919cb705aa64f8213a193945b6623706ac1e368149|
|d1-duration.wav|32000|9829|a3f8c36bae521533510b67bbec3b0b1187a836f63a8a649db94d7812c39dd492|
|d2-duration.wav|32000|9825|bbf6a3d67984610fd4fa9c3bf79ce4e0072c9fa7de7842e8ce2db64fbc01e2cc|
|d3-duration.wav|32000|9827|830063b23df89b85bb948468f7a2338dd4f2fd92ff6577e0c799db6afe74f5ea|
|d3-speed.wav|148148|9830|884ff931634a61a6215df77235c05b27d704140a2d03f2b93276758ecc3af5f7|

The fifth file is 9.25925 seconds by PCM count, rounded from 250/27 s. Audio outputs provided separately; reproduce using laboratory.py. No binary data, registered source or shared manifest added. Structural repo CI and independent review not established by this receipt. No cross-platform bit-identical floating-point guarantee, human listening, participant data or real-time DSP qualification.
