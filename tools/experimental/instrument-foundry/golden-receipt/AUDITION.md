# Golden Receipt 0.1.0 — owner audition

Qualified binary source `eb78ea3b7a08a646910e66235724f259aeeb8190` (PR #447, issue #446). Origin: research #428 / draft #429 at `07fb2f67a5a2cf26312699410f00152033cae843`; direct timing-fingerprint realization with creative sine-pulse timbre, no human-perception claim.

Windows x64: extract the inner release ZIP and copy the entire `MHACGoldenReceipt.vst3` folder to `C:\Program Files\Common Files\VST3\`. Rescan your DAW and insert MHAC Golden Receipt on an instrument track. It uses host-native parameters. Start with the default patch, conservative monitoring levels, and a 120 BPM project. Import one MIDI file at a time; do not change its timing or quantize it. Render audio with no downstream effects. The following are proposed DAW checks, not executed host tests.

| File | Suggested check |
|---|---|
| 01-collision-witness | Default span/width/gain; Golden shape; compare First vs Third, and Second vs Fourth. The direct core produces identical audio within each pair. Compare Equal gaps First vs Second as a negative control. Reset transport/plugin between renders and align them before a polarity-inverted null test. |
| 02-velocity-ladder | Five identical pitches with increasing velocity; compare isolated pulse amplitudes. |
| 03-staggered-chord | Six overlapping voices, independent pitches and motif timing. |
| 04-early-release | First note ends after 125 ms; later full-length reference note. Check early silence and absence of stuck voices. |
| 05-voice-capacity | Seventeen simultaneous distinct notes with 16 slots; the excess note is dropped (the exact dropped pitch depends on host event order). Check later isolated note sounds after the earlier group ends. |

Default span 0.72 s and width 47.5 ms; longer spans may intentionally be truncated by note-off. MIDI fixtures use format 0, PPQ 480, 120 BPM, channel 1, no host-specific automation. The script needs Python 3 only. `python make_audition.py midi` regenerates fixtures; `python -m unittest -v test_audition` checks independent decoding, deterministic generation and rejection of invalid inputs. Local run: four test methods PASS, all five fixtures decoded, seven negative cases rejected. AI-assisted same-agent software checks, not independent review.

Exact-head Windows workflow 45537942765 and research integrity 45537942596 succeeded. Artifact 14987637390 contains an inner portable ZIP; SHA-256 outer `299400212aff8213b99131474d8092be5a396658197727621245ca4a7a94e9c3`, inner `ce074aff2bbfd9d8b10e90e4e2d246fbef43f0d36a7da14592ab03153e39cccf`, plugin PE x64 `b30e6715fb9772dbc2aa896ada542a3f67c5880a4565b3496f93e0a6197d281c`. Both archives passed CRC checks. Build source and SDK receipt match pinned source and SDK `9fad9770f2ae8542ab1a548a68c1ad1ac690abe0`; seven recorded SDK gitlinks, license notices, VST 3.8.0 instrument module metadata and official validator transcript present. Validator transcript reports 47 passed, 0 failed and all 12 sample rates, including previous failures. The separate validator artifact 14988465702 also passed CRC and digest verification. The packaged historical README has prequalification wording; the completed workflow and transcript supersede it. Physical DAW audition, independent review and Linux/macOS plugin qualification remain outstanding. No DSP or adapter changed in this follow-on; original qualified SHA preserved.
