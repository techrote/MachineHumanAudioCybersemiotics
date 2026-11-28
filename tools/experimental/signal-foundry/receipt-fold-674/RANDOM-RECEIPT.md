# FX-009I — balanced receipt traversal laboratory (26 November 2026)

Refs #674; [#339 section 4](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64/research/expeditions/undo-needs-forecast/README.md). Main 495a98ca12bae467a507031f04931aa4254b1866; predecessor f84484207c07d67cedeb627738cd8a1ea6923b78. Direct restricted finite-law realization plus creative audio interpretation. Single AI implementer/self-test; no scientific or human validation.

## Mechanism

For N=2^bits (3–8 bits) and M=2^budget, a nonzero multiplier a in GF(N) permutes N states. The low budget bits of a*x define a balanced tag. For distinct endpoints u,v, a*(u XOR v) runs through all nonzero elements, so exactly N/M-1 multipliers collide. Enumerating every multiplier with both tie decisions yields endpoint error (N/M-1)/(2*(N-1)), equal to the pinned theorem for these power-of-two alphabets. This is a smaller sufficient family than all balanced colourings. The kernel recover() is an optimized finite oracle using the original index internally; it is not an externally connected encoder/decoder or transport implementation.

Schedule uses a seed-derived offset and coprime stride to permute the 2*(N-1) multiplier/tie pairs each cycle. Every pair appears once, with a different seeded order on each cycle (orders may recur). This is exact cycle stratification, not IID draws or cryptographic randomness. Tie choices alternate within a cycle; partial cycles can be biased. The theorem assumes the world precedes the random draw; audio input need not satisfy that assumption. Fixed comparison uses the identity multiplier with the same fair-in-cycle tie schedule, not the original RF03 lower-endpoint tie policy. Intermediate smoothed samples and continuous amplitude error are not discrete minimax outcomes.

## Native interface

random_receipt.hpp extends the existing resolution library without changing any legacy plugin source, IDs or RF01/RF02/RF03 formats. Config fields: bits, lo, hi, budget, epoch_ms (5–1000), seed (uint32), balanced, bypass, wet [0,1]. Default dry; RR01 is a separate 24-byte little-endian patch format, not a VST3 state format. Clock/phase is transient. prepare accepts finite 1 kHz–2 MHz and resets clock and wet; apply is audio-thread-owned and rejects invalid settings. Bits, seed or epoch changes restart schedule; other law changes preserve clock. Pass distinct stereo scalars to frame once per sample (for mono use a separate scratch scalar). Apply configuration at the caller's event offset; no host automation layer added. Shared stereo draw intentionally couples state choices, not channel amplitudes. Transfer-table and wet changes slew over 5 ms; no sample delay or audio tail, clean silence, finite clamped output [-1,1]. All callback storage fixed, no I/O or locks; table rebuild 256 entries, bounded stride search <=510 iterations. Public finite helpers require valid config, bits, multiplier and index.

Example configurations: 3 bits, endpoints 1/5, budget 1, epoch 25 ms, seed 42, wet .8 (coarse); 8 bits, endpoints 96/176, budget 4, epoch 20 ms, seed 77, wet .65 (fine selective); same with budget 8 (zero discrete reconstruction error control). Compare balanced true/false.

## Reproduction and evidence

In this directory:
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    ./build/receipt_fold_random_test fixed.wav balanced.wav

The last executable may be under build/Release on multi-config generators. The render uses a 4-second stereo original oscillator score with matching input and timing, 3/4/5/6-bit epochs in successive seconds, 25 ms tag epochs, seed 42, wet .8. GCC 14.2 Release CTest 9/9; Clang 17 ASan/UBSan new test PASS. 2,996,508 endpoint worlds (XOR difference representatives), all multiplier permutations and class sizes, four seeds/four cycles per resolution, 175,000 paired float64 frames across seven sample rates (plus extra float32 probes), 48,000 partition-invariant float32 frames, 48,000 zero-tail frames. Invalid state and invalid epoch rejection, bypass, reset and nonfinite inputs tested. Dense automation 480,000 stereo frames took 0.190582 s on local Linux (aggregate, not a worst callback deadline). Repeated WAV bytes identical; fixed peak .443749 FS/RMS .268792; balanced peak .443749 FS/RMS .280345; PCM16 RMS difference .093858 FS; both final 50 ms exact silence. SHA-256 fixed f91850d4f725ded9bf945d7443cb7fa6a3066c9be8e6966cfa1fd052a8d97f47; balanced 02f24fbb1dfeff14a2ec9f38d4cc1993a173f7c5746661f168919489148c509f. No listening or DAW validation performed for this development.

SDK tag v3.8.0_build_66 resolved to locked root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; all seven gitlinks in SDK-PIN.txt match official root tree and all seven recursive dependency trees were untruncated with no nested gitlinks. Local git fetch fails DNS resolution; no substitute SDK used. Predecessor Windows run 45860902739 and integrity 45860902665 both success. New work is native-only: existing VST3 0.2.0 remains unchanged, no new binary claimed. Existing isolated Windows workflow reused for regression; no shared changes. Draft/HOLD; adapter, sample-offset host integration and actual host performance still outstanding.
