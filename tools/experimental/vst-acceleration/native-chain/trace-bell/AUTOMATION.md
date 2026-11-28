# Trace Bell — polar retuning and sample-offset block bridge (ACCEL-030)

Refs #632; base b476856b255a5a012191e4d1b418d1deb2f94122; main 495a98ca12bae467a507031f04931aa4254b1866. Creative DSP exaptation, not a scientific or perception claim. Draft/HOLD.

The performance wrapper now enables 10 ms pole ramps. Interpolate phase and log radius using a double-precision complex multiplier computed only at a tuning event; advance by multiplication while active, snap to exact target at the last sample, and retarget from the current position. Unlike a Cartesian chord, this does not impose an unintended large intermediate radius loss. Mix/contrast retain their original smoothing. Legacy direct core defaults to immediate tuning; prepare/reset settle to the target. TB01 parameter bytes and IDs unchanged. Repeated identical targets do not restart a ramp.

The native planar stereo block bridge validates sorted normalized events before processing, applies simultaneous changes as one patch (last duplicate wins), supports matching in-place buffers and zero-frame parameter flush. Count bounded by six times max(1,frames); malformed block does not advance state or write output. Caller guarantees valid array extents and no cross-channel buffer overlap. No allocation/locks/I/O by inspection in the processing path; dense automation still performs transcendental coefficient setup at event boundaries, and no deadline is claimed. SDK adapter, class IDs, SDK queue translation, host state concurrency, validator, native Windows build and DAW testing remain outstanding.

## Executed native tests (2026-11-27)

For each of trace_bell_test, trace_bell_state_test, trace_bell_pole_test and trace_bell_block_test:

    g++ -std=c++17 -O2 -Wall -Wextra -Werror TEST.cpp -o TEST_gcc
    ./TEST_gcc
    clang++ -std=c++17 -O1 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer TEST.cpp -o TEST_clang
    ./TEST_clang

GCC 14.2 and Clang 17: both pass 426544 analytic complex-pole comparisons (max error 3.98828947e-08, all radii below unity), 2460900 exact stereo-frame block comparisons (six rates 8–192 kHz, partitions 1/31/257/1024/65536 and in-place), 54 transactional rejects, zero-frame flush, 1640600 existing core comparisons, 820300 wrapper comparisons, 606 state round trips and 55 prior negative controls. Core/wrapper size now 584/632 B on this host. All three prior static audition WAVs reproduced byte-identically via existing render_wav.py. Same-agent tests; no independent human review.

## Audio comparison

Compile trace_bell_sweep.cpp with the same flags (substitute renderer name). Input: 15s 48kHz stereo PCM16 little endian raw extracted from ACCEL-028 padded Dry.wav (WAV SHA256 3e5b69016dbbb6626d27c2bde7b8a2cf1f203631ad6abe0a2f3fd65466f1bb80). Execute renderer INPUT.raw OUTPUT.raw instant and polar, wrap outputs as 48kHz stereo PCM16 WAV. Both renders include 23 timed tuning events and three seconds of tail, fixed -6.02 dB output attenuation. Exact cross-compiler PCM for both; first half-second identical, 1383023 differing PCM words after events. Peak 0.0987243652 / 0.1015319824 FS; RMS 0.0177940871 / 0.0174714710 FS. No listening claim or general click-free guarantee.

Prior exact ACCEL-029 Windows host and integrity runs 45936738941/45936738983 succeeded (not specific qualification of this new DSP). Local git checkout still DNS-blocked; SDK root MIT license and seven submodule declarations reread at pinned 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0, not linked. No workflow, Foundry or frozen research edits. Next: actual SDK adapter with dedicated native/validator qualification, not further native-only feature accumulation.
