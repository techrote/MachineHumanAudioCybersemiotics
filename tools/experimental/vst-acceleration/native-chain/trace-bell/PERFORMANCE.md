# Trace Bell performance and state — ACCEL-029

Refs #632; base d30879240d268c3ae470b13b798e76687a477b1c; main 495a98ca12bae467a507031f04931aa4254b1866. Additive wrapper only; original TraceBell core unchanged (blob ec7d6deb7a72a7f2d0f854af34625063530e81db). Creative exaptation, no scientific or perception claims.

## Parameter and state contract

Candidate stable normalized IDs: 0 pitch (80–500 Hz linear), 1 decay (0.03–1.2 s linear), 2 contrast, 3 mix, 4 spread (each 0–1), 5 bypass (threshold 0.5). Reject nonfinite/out-of-range normalized values and unknown IDs. No VST class IDs assigned. Single audio owner dispatches changes at sample boundaries; no host event queue implemented here.

TB01: exactly 32 bytes. Bytes 0–3 ASCII TB01, byte 4 version 1, bytes 5–7 zero. Bytes 8–27 five little-endian IEEE754 binary32 physical parameters in ID order, byte 28 bypass (0 or 1), bytes 29–31 zero. Strict exact-length/version/range validation before commit; no checksum or claim to detect arbitrary in-range corruption. Patch only, not history. Restore preserves live memory; reset after restore for deterministic fresh-instance playback.

Bypass crossfades dry/wet in ceil(10 ms * sample rate) samples from current fade position; exact bounded dry at endpoint. Core continues processing during bypass so memory evolves. Rapid reversal retargets from current position. No allocation or I/O by inspection; no measured real-time deadline claim. Pitch/decay/spread remain immediate coefficient updates; mix/contrast retain the original smoothing. No SDK linked, no plugin ABI/validator or Windows-specific tests in this increment.

## Reproduction and receipts (2026-11-27)

    g++ -std=c++17 -O2 -Wall -Wextra -Werror trace_bell_state_test.cpp -o state_gcc
    ./state_gcc
    clang++ -std=c++17 -O1 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer trace_bell_state_test.cpp -o state_clang
    ./state_clang

GCC 14.2 and Clang 17 ASan/UBSan both: 606 state round trips; 55 negative controls; 820300 exact partition comparisons; six-rate fade oracle; sizeof 240 PASS. Six rates 8–192 kHz, partitions 1/257/1024, golden default bytes, fresh-instance output equality, interrupted fade and bounded output checks. Same-agent native tests. Previous exact ACCEL-028 host run 45930773768 and integrity 45930773687 both success; those workflows do not qualify this new wrapper. Local git checkout DNS failed. Next smooth tuning and implement thin VST3 adapter with pinned SDK, validator and real host checks. Draft/HOLD; no merge.
