# Phase Cycle Prism — FX-006A

Refs #568, #296/#297 (research draft pinned c66c128ae550aadd16a46ddc7559406dbbc65be9). Isolated creative spectral effect and direct coefficient-level realization of the two-sign cubic cancellation mechanism. Not a general nonlinear receiver, human experiment, or production plug-in. Original source and generated demos only. No new license granted.

## Operation

Stereo is treated as complex I/Q (L = real, R = imaginary); conventional stereo is an intentional creative interpretation. The four bin indices 5,6,9,10 correspond to 400,480,720,800 Hz at 48 kHz. Each N=round(sample_rate/80) input samples are projected against the four complex carriers. A cubic coefficient convolution produces a raw vector. The second virtual sign frame negates carrier 10, recomputes the cubic, and demodulates carrier 10 by negating it again. Their complex average cancels all nontrivial equal-sum collisions on this grid; diagonal gain remains. This is a simulation of both phase frames from one captured coefficient vector, not an acoustic transmission or a decoder of an arbitrary already-distorted signal. In particular it cannot erase a 400 Hz component already present in the input. Only four output bins are synthesized in the wet path; other products and off-grid material are not faithfully reproduced.

Drive [-1,1], cancellation [0,1], wet [0,1], wet gain [0,1]. Drive and cancellation are captured at each completed analysis frame; wet and gain slew over up to 5 ms. Each new coefficient vector is interpolated over the following frame. The dry path is delayed N samples; full-wet stationary output settles after two frames. Time-varying wet signals have an additional interpolation history, not a pure N-sample delay. Tail bound 3N samples. At 48 kHz: N=600 (12.5 ms), tail bound 1800 samples (37.5 ms). At rates not divisible by 80 the actual grid is sample_rate/N times each bin. Stereo double core, fixed storage, no allocation, locks or I/O in step(); setup precomputes basis. Input and output components bounded +/-1 FS, nonfinite and extremely small values mapped to zero. Protection clipping can invalidate the formal result. No callback profiling or allocation instrumentation yet. Range 8–192 kHz; no other layout claimed.

## Build and audition

CMake 3.16+, C++17, no dependencies.
    
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    ./build/prism_demo

For multi-config generators run build/Release/prism_demo.exe. The demo generates dry.wav, raw.wav and corrected.wav, all original 2-second stereo PCM16 at 48 kHz, same three .18 FS carriers at 480/720/800 Hz, first 1.5 s active, no loudness normalization. Dry is latency-aligned; both wet renders use gain .7. Begin at low listening volume. No listening assessment performed.

Standalone file processor accepts headerless interleaved stereo signed PCM16 little-endian, not a WAV header:

    prism_process input.s16le output.s16le 48000 1 1 1 0.7

Arguments after rate are drive, cancel, wet, gain. It appends the full 3N tail, refuses an existing output path, returns 2 for invalid arguments and 3 for truncated input/output failure (partial output possible). Example optional conversion with independently installed FFmpeg:

    ffmpeg -i input.wav -ac 2 -ar 48000 -f s16le input.s16le
    ffmpeg -f s16le -ar 48000 -ac 2 -i output.s16le output.wav

Do not pass WAV containers directly. Example patches (drive/cancel/wet/gain): Raw witness 1/0/1/.7; Clean witness 1/1/1/.7; Half witness 1/.5/1/.7; Spectral glaze -.3/1/.35/.7; protected delayed dry 0/1/0/1. No VST parameter IDs, state codec, DAW host adapter or installable Prism binary exists yet.

## Qualification receipt — 2026-11-25

GNU 14.2 Linux x64, C++17 Release with -Wall -Wextra -Werror: CTest 1/1 PASS. Native test also passed address and undefined-behavior sanitizers. 625 complex amplitude words, 2500 comparisons to independent diagonal expression, 5 rates x 3 cancellation settings (8,44.1,48,96,192 kHz), dry impulse latency, reset, finite tail, nonfinite/extreme input and analytical off-grid negative control. Maximum settled corrected target residual 2.01457e-16 FS; maximum raw-target error 2.40942e-16 FS. Predicted raw manufactured coefficient .011664 at unity wet gain; half cancellation .005832; full cancellation zero within floating-point error.

Actual PCM16 demo coherent projection at 400 Hz over samples 12000..59999: dry 1.38234e-7 FS, raw .00816523611 FS, corrected 5.64447e-8 FS. Corrected PCM floor is not exact zero; clipping, off-grid signals, varying coefficients, non-cubic distortion and unmodeled channel memory are outside the ideal claim. The 440 Hz off-grid analytical negative control has projection magnitude >.1 FS from a .2 FS carrier. It is not an external hardware measurement. Demo peaks .54/.447401/.439236 FS. All three WAVs byte-identical on regeneration; SHA256 corrected 701dc403324eed4fd6329835123f4bdf4e8a7dd757ade039be0e11003d1655e5, dry 473bbaa1dae0496e63cdba7a77527525cb9607903f0e3b30fa507aefddfd7620, raw 85c26d80209948447338648dea9ec48b11a242914f9114a35ab9328cb5939d6c. File processor valid raw render 384000 input bytes -> 391200 output bytes; malformed one-byte file returns 3; existing output returns 2. Same agent implemented and tested; no independent review or scientific acceptance.

## SDK and next gate

Prism core does not use the SDK. Future adapter must use official https://github.com/steinbergmedia/vst3sdk tag v3.8.0_build_66, root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. Clone with git clone --branch v3.8.0_build_66 --recurse-submodules https://github.com/steinbergmedia/vst3sdk.git; verify git rev-parse HEAD and git submodule status --recursive against SDK-GITLINKS.txt (no missing, modified or conflicted gitlinks). Retain upstream notices/licenses with any eventual bundle. Root tag and all seven dependency commits resolved via GitHub read access; git clone/ls-remote from local shell remains DNS-blocked. Gitlink list recovered from exact-source Witness Forge 0.2.0 qualified Windows artifact; no SDK files redistributed here. No substitution, no native Prism VST3 build. Windows x64 and macOS intended only. Next: stable class and parameter IDs, state codec, adapter lifecycle, host automation and latency reporting, callback deadline tests, Windows SDK validator and independent review. Main base 495a98ca12bae467a507031f04931aa4254b1866; AGENTS/RAG/programme/runbook/research integrity/validation and origin issue/PR read, sibling lane checked; no shared workflows or manifests edited. Draft/HOLD.
