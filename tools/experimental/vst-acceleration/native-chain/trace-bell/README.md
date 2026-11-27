# Trace Bell — ACCEL-028 (Refs #632)

Original C++17 host-independent stereo resonance module, not a VST3 bundle. Creative MHAC analogy: short/long envelope contrast modulates excitation of four damped quadrature modes per channel (ratios 1, 1.5, 2.125, 3.25), leaving a pitched trace of preceding gestures. Not a decoder, formal scientific model, or perceptual result. No upstream code copied, no SDK dependency; existing qualified plugins unchanged. Base 9ef7275b398c038842563d0ceef8f20aabd6e719; main 495a98ca12bae467a507031f04931aa4254b1866. Draft/HOLD.

Parameter contract: pitch 80–500 Hz, decay 0.03–1.2 s (amplitude time constant), contrast and mix and spread 0–1. Stereo spread ±1.2% at maximum. All calls single owner. Prepare clears state; configure rejects invalid patches and preserves resonance state; mix and contrast smooth over a 10 ms time constant. Pitch/decay/spread update at explicit boundaries, not smoothed. Bypass emits exact sanitized dry and advances memory; hard toggles may click. No allocations in core, no lookahead, no fixed algorithmic delay; tails depend on decay and excitation. Each quadrature pair limited by max magnitude 0.5, wet sum bounded to 1; denormal guard and finite input clamp. No persisted state version or VST parameter/class IDs assigned yet. Do not use fast-math; no physical or real-time deadline claims.

## Reproduce

From this directory (assertions enabled):

    g++ -std=c++17 -O2 -Wall -Wextra -Werror trace_bell_test.cpp -o test_gcc
    ./test_gcc
    clang++ -std=c++17 -O1 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer trace_bell_test.cpp -o test_clang
    ./test_clang
    g++ -std=c++17 -O2 -Wall -Wextra -Werror trace_bell_render.cpp -o render_gcc

GCC 14.2 and Clang 17 ASan/UBSan both PASS 1,640,600 exact stereo-frame comparisons per compiler across 8/22.05/44.1/48/96/192 kHz, partitions 1/257/1024, sample-indexed changes, exact bounded dry bypass, impulse decay/channel isolation, invalid configuration/rate transaction, nonfinite input, reset and 480,000 extreme frames. Native object 196 bytes on x86_64; extreme peak .659829378 FS. No allocation instrumentation, VST ABI, Windows compilation, subjective audition, deadline or embedded performance test.

## Offline audition

Use the original Session-026/Comparisons/Dry.wav from the ACCEL-027 package (archive SHA256 5063db0c5369b891d30f300592633b034e1e27b24aedb0b715a7db6dba9a2bba, input WAV SHA256 561da1ad404f1154aabe670b13ebe169437c61571d411adf4d3670f802f8558d). Extract PCM16 little-endian stereo at 48 kHz via Python wave. Run render_gcc INPUT.raw OUTPUT.raw glass (or bronze/haze), using separate new output paths. Wrap output in matching WAV format. Renderer adds 3 seconds of zero input; 15 s total. No normalization. GCC and Clang sanitizer PCM bytes identical for each setting. Peak FS glass .1741333, bronze .19958496, haze .0953064. This is actual core processing of a previously qualified host mix, NOT a new VST host render.

Previous ACCEL-027 Windows host run 45924687243 and integrity run 45924687211 succeeded. Original SDK 3.8.0 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 MIT license and seven submodule declarations reread; no SDK linked or rebuilt here.

Next: evaluate sonic usefulness, add a versioned parameter/state contract, smooth tuning and bypass transition, dedicated thin VST3 adapter with stable IDs, validator/host tests, and assess fixed-budget embedded portability only after measurement. Do not merge without independent review and owner approval.
