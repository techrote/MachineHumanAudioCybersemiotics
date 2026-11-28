# Orbit Lantern — Expressive automation study (INST-011W)

Refs #738. Creative synthesis interpretation of #265 at 56c107f8f4147316a588484c47be28bc8f840fbb; not human evidence. Uses the existing 0.4.0 interface without changing the binary contract, DSP, state encodings or parameter IDs. Predecessor #739 at 646d1f4dadd4ded55b3c4f681e94856923611445.

Build with the existing CMake instructions (native, SDK option OFF by default). Run `orbit_expressive_performance <output-directory>` to generate two original five-second 48 kHz PCM16 stereo WAVs, two sample-indexed normalized VST3 automation CSVs and a note event CSV. No arguments runs the same regression without writing output. No third-party runtime is required.

| Note | On / off (ms) | Blend | Release duration | Sustain depth / cycle | Release mode / spectral depth |
|---|---|---|---|---|---|
| C3 | 0 / 1800 | 18% | 650 ms | 90% / 1400 ms | Phase / 70% |
| G3 | 500 / 2300 | 70% | 900 ms | 100% / 6000 ms | Fixed / 25% |
| E4 | 1000 / 2800 | 55% | 180 ms | 80% / 320 ms | Phase / 80% |
| A4 | 2000 / 3400 | 35% | 500 ms | 50% / 780 ms | Linear / 0% |

Use a 48 kHz stereo instrument track with the previously qualified 0.4.0 plugin. Enter notes from notes.csv and step (not ramp) automation from the chosen CSV; parameter IDs 1810..1816 are the existing VST3 controller IDs. Parameters precede notes at identical sample offsets in the adapter. Set initial points before playback if the DAW cannot deliver sample-zero automation; a host may interpolate or reorder automation and note delivery, so the offline renders are references, not DAW captures. The fixed comparison has the same score with blend 18%, release 650 ms, tuning -12 cents, phase release, spectral depth 70%, sustain disabled. The expressive score deliberately changes sustain depth and cycle mid-note at 750 ms; the two held voices must retain their onset settings. Release mode/depth are sampled at note-off, not onset.

The executable drives a polyphonic native Live instance through the normalized parameter API and compares every sample against the sum of four separately configured Live instances. This is a voice-isolation and latch witness, not an independent oscillator implementation. 1, 257-frame loop partitions at 44.1/48/96 kHz, both modes: GCC Release and Clang ASan/UBSan each PASS with 1,881,000 paired stereo frames, zero maximum solo-sum error, final exact digital silence, bounded finite output, distinct fixed/expressive renders, and all voices released. Both WAVs and three CSVs reproduce byte-identically across compilers. Full native Linux Release CTest 12/12 PASS. No listening, actual VST3 replay of this score, Windows candidate build or independent review performed locally. Existing 22-preset inventory unchanged. Official 3.8.0 pin and seven prior actual checkout revisions retained, local SDK Git DNS blocked; no SDK substitution.
