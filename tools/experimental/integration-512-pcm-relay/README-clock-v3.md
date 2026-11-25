# Clock-aware relay receiver (v3 receiver, unchanged v2 wire)

Refs #512, Draft PR #513; synthetic apparatus, 2026-11-25. One GPT-6.2 agent, no subagents or independent review. Main 495a98ca12bae467a507031f04931aa4254b1866; parent 4d2d0b2c067924305675e92eabd2b9cc28676842 (Research integrity succeeded). Read AGENTS/RAG, programme/runbook, foundations, experiments/human gates, integrity/validation and both issue comments. The explicit experimental remit supersedes the foundational no-production restriction only for synthetic apparatus. No canonical research edits, license grant, merge or firmware writes.

## Mechanism and scope

Responds to the timing finding in #449 (389f1662fa0abaa21753d8982731cb7e80b6e46d, relay-clock-audit.cjs) and #453 (c2eb5783dfd9b3272512ef17ea08986d44e29228, local-clock.cjs). Independently reproduced the #449 120 timing fixtures, including 15 ms guard-only contractions that preserve exact PCM energy. No new markers or transmitter changes. Search ordered 2300/2700 Hz preamble at 13 scales from .985 to 1.015 in .0025 steps; 16-sample onset stride. Keep best onset per scale, retain all detected onset extrema. Demodulate centred 320-sample windows at scale-adjusted frequencies, check energy, purity and separation. Recover GF(17) erasures, parse canonical tree, verify complete v2 binding tag. Abstain if onset span exceeds 320 samples, no valid interpretation or different valid interpretations. This is a finite single-frame model, NOT a general synchronizer. The minimum completeness bound tolerates a short missing terminal guard; it does not prove every sample arrived. No probability calibration or claim against arbitrary interference. Shorter demodulation windows trade noise integration for timing tolerance.

#443 measurement README at bfb5d207125e3d654756b8a9a1b8f1aba2cbd16d separates exact timing from sampled receipt; #457 return-window README at fefeb1713d538c5c3b8553da0f0d2f954fd7ed98 separates ready ACK and channel cost, but uses oracle metadata. Both are draft. Foundry issues surveyed, no DSP imported. FM-1-MHAC and FM-1-CYDaux README read for downstream boundaries, no hardware operation. No upstream source vendored or external license assumed; main LICENSE absent. Existing v2 wire implementation blobs relay.cjs 3ba457f85f496e4d57d9789a2dc3b7d68fe2c071 and bound-v2.cjs 2aa2905d4f4d756276814d5ca941c02c51e63f97 verified in prior owner package against current exact parent.

## Run and audition

Use Node 22 or compatible, C++17 host compiler and Python 3. From this directory in a scratch checkout:

    node clock-v3.cjs clock-v3-output
    g++ -std=c++17 -O2 -Wall -Wextra -Werror clock-v3-host.cpp -o clock-v3-host
    python verify-clock-v3.py clock-v3-output ./clock-v3-host
    node schedule-clock-v3.cjs scheduled-clock-v3-output
    node verify-schedule-clock-v3.cjs scheduled-clock-v3-output

Open schedule-inspector.html and select manifest.json plus matching WAV/JSON pairs from one output directory at a time. Start with drift-ack-first, delayed-ack-first, forged-reserve. Compare the existing fixed-clock scheduled-v2-output against the new clock-aware output in separate viewer tabs. The viewer reports recorded evidence, not live decoding; play at low device volume. clock-v3-output contains individual matched-input comparisons (same PCM supplied to both receivers); read receipt.json for word hypotheses and exact SHA-256. All stimuli original synthetic PCM16 mono 16 kHz. Scheduled outputs use the same 20 s budget, but actual signals diverge after protocol decisions. No measured SPL or human evidence.

## Native qualification

Linux x86_64, Node 22.16.0, g++ 14.2.0, Python. 233 assertions, 176 matched single-window fixtures (107 fixed expected-decision matches, 176 new). The 120 audit reproduction rows: fixed 86 intended recoveries, new 120; specifically 72 uniform scale cases 40 -> 72, 48 guard edits 46 -> 48. Another 48 clean/guard/drift rows 14 -> 48. Remaining eight controls include loss, truncation, original splice, missing tag and changed tag refusal; competing preamble now refused where fixed receiver accepted intended packet. Known checksum collision and matching forged ACK still accepted, intentionally retained counterexamples. These are predetermined finite fixtures, not estimated rates. No independent proof of correctness.

Native independent C++ Goertzel DSP adapter compared against JS direct correlations on all 176 exported WAVs: 805 hypotheses, identical starts, scales, symbols/erasures, completeness flags and onset span; maximum quality difference 1.255e-14. All WAV hashes, sample counts, format and peak <=4096 verified. C++ result struct 640 bytes on tested ABI; caller PCM cap 76,800 bytes; no heap in DSP core, host CLI allocates. This is an acquisition adapter only; semantic/checksum/authority verification still required by host, not embedded RAM or real-time certification. 13-scale scan can be expensive. No portable Windows binary or device test.

Scheduler: explicit receiver injection preserves default v2 continuous scan. New receiver receives known 2 s slot boundaries (out-of-band timing, not intent); 273 assertions over 45 sessions, 450 exported slots replayed byte-for-byte in decoder evidence. All three drift scenarios remove one retry while retaining two genuine confirmations; aggregate genuine counts unchanged 23/25/23, retries 14/9/14 -> 13/8/13; one false confirmation per policy retained. No unsegmented v3 re-acquisition claim. Native headless Chromium 144.0.7559.96 file:// and localhost navigation blocked by administrator; set_content fallback tested file selection, 10-slot timeline, 3 policy rows, 20 s muted playhead and JSON export/reread without page errors. Physical playback, ordinary launch and Windows outstanding. Full repo clone blocked by DNS. CI and independent review required before any promotion.

## Next action and limitations

Do not shorten the binding tag merely to rescue clock failures. First build a bounded streaming preamble association layer and measure held-out mixed drift/noise/overlap, false-onset and timing ambiguity. Current 13 hypotheses search a declared scale grid, not an exhaustive physical uncertainty set; acceptance of one interpretation does not prove unique physical origin. The matching-forgery and collision controls remain failures of identity/authority, not clock errors. Compact framing is a separate design comparison, with preserved v2 baseline and matched channel budget. No real-time, human comprehension, hardware or production reliability claims.
