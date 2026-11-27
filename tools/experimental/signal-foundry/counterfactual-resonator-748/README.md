# Counterfactual Resonator — FX-011A

Refs #748; creative DSP extension of #264 and [draft #265, exact model and unbounded construction](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/56c107f8f4147316a588484c47be28bc8f840fbb/research/expeditions/quantized-decay/README.md). Base main 495a98ca12bae467a507031f04931aa4254b1866. Native C++17 stereo effect laboratory, not a VST3 binary, empirical evidence, or physical shutdown guarantee. One AI implementer; no independent review or listening assessment.

## Processing contract

A causal sample clock advances at four times the selected nominal pitch. At each tick, average the input samples since the previous tick, round 12 times that average to an integer drive, and inject it into the x coordinate. Both paths receive the same drive. The discrete path applies the q=9, a=0, b=8 quarter turn with nearest integer rounding (or magnitude truncation on an intervention), then clips each coordinate to [-16,16]. The continuous reference uses the same rational rotation, drive, and coordinate clipping, but no feedback rounding; tiny values below 1e-15 are zeroed. Interpolated x coordinates produce the audio; y is internal. The dry path is undelayed. Both stereo channels have independent states, with a shared tick clock and controls. This is a deliberately coarse, driven, clipped extension of the source's undriven, unbounded model, not a general minimum-intervention solver. Boxcar drive and linear interpolation are not an ideal anti-alias filter; weak drives can quantize to zero and intentional distortion/aliasing may occur. Frequency is nominal quarter-turn pitch, not a guaranteed spectral peak for arbitrary excitation.

Within the square |x|,|y|<=4, with zero drive, nearest rounding is an exact quarter turn. A single truncation update decreases the maximum magnitude by exactly one until zero. Outside the square the bounded discrete system can have transient states; continuous truncation with zero drive extinguishes every bounded state in at most 16 ticks, plus interpolation settling. With excitation still present, neither mode guarantees silence. Nearest mode has potentially infinite tail; no VST3 tail or latency report is implemented yet. Reset clears the state and pending intervention. Preparing a new valid sample rate resets rather than preserving phase or tail.

## Controls and use

- Frequency 40–6000 Hz, effective cap sample_rate/16; supported rates 8–384 kHz. Frequency changes preserve clock phase and apply from the next sample.
- Wet and gain 0–1000 (per mille), linear full-scale slew of 5 ms; bypass targets zero wet with the same slew and preserves state evolution. Settled bypass is exact for finite normalized inputs. Nonfinite, tiny and out-of-range inputs are sanitized to zero or clipped to [-1,1]. Wet output and total output are bounded to [-1,1].
- Monitor 0 reference, 1 discrete, 2 half difference. Convex one-pole transition with approximately 5 ms time constant (not a 5 ms fixed crossfade); snaps to exact target near convergence. Half difference has the same bound.
- Erase applies magnitude truncation on every tick. requestIntervention() requests one truncation on the next tick; repeated requests before a tick coalesce. The pulse is not a persistent parameter. Controls and pulse are audio-thread/event-owner APIs, not thread-safe host mailboxes.
- CR01 is a 12-byte little-endian native configuration (magic, frequency, wet, gain, monitor, erase/bypass flags). It does not serialize live audio state, pulse or sample-clock phase. A future adapter needs stable class/parameter IDs and thread-safe state transport.

Default is 220 Hz, 70% wet, 80% wet gain, discrete monitor, no erase/bypass. Persistent resonances can continue after transport stops unless reset or erased; audition at low monitoring volume. For a short input pulse, compare continuous reference with discrete persistence, then select residual to isolate the difference. A single pulse in the invariant square shrinks the orbit; sustained erase extinguishes it.

## Build and reproduce

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
mkdir -p Audio Presets
./build/counterfactual_lab --render .
./build/counterfactual_lab --bench
```

For MSVC multi-config builds use `build/Release/counterfactual_lab.exe` and create the output directories before rendering. No SDK source is required for this laboratory. SDK-PIN.txt records the official release and all recursive gitlinks; future adapter builds must verify the actual checkout and retain notices. Do not substitute another SDK. No changes to shared workflows or manifests. Windows/macOS are intended, not compiled or validated in this iteration.

The four original stereo 48 kHz PCM16 examples use 250 Hz, full wet, 80% gain; left receives 48 samples at +0.5 starting at frame 0, right 48 samples at -0.75 starting at frame 96. Reference, persistent and half-difference change only the monitor. Intervention uses the persistent configuration, requests one T at frame 48000, and enables continuous erase at frame 96000. Its CR01 starting patch is intentionally identical to persistent; the event score is in lab.cpp, not encoded in CR01. The reference and intervention recordings end in exact silence; persistent and residual intentionally do not. No subjective listening or DAW import test.

## Verification and remaining gates

GCC 14.2 Release and Clang 17 ASan/UBSan Debug CTest each passed 1/1 (1,125,660 assertions per invocation). Enumerated 1,089 lattice states and all 25 supported integer drives in both rounding modes, exact invariant-square cycles, zero-drive truncation descent, coalesced intervention, output bounds, invalid config/state, 324 patch cases, six sample rates, three monitors, float32/64 agreement, variable partitions and stereo isolation. Mixed-control deterministic replay uses hostile input and reset. Four WAVs and four starting patches regenerate byte-identically on the same Release build. Two offline 96k/32-frame mixed automation probes (4,000 blocks each): median 0.561/0.552 us, p99 1.014/0.697 us, maximum 211.546/135.32 us, 0/8000 observed deadline misses. These are uncontrolled wall-clock measurements, not actual host or real-time qualification. No callback allocation/blocking code is present in the native core; no allocator interposition test yet.

Remaining: independent source review, VST3 adapter and coherent state mailbox, stable IDs, bus negotiation and event handling, actual exact SDK checkout/build/official validator, native Windows/macOS, host state/automation/tail verification, standard VST3 presets and desktop DAW audition. Local SDK git retrieval failed DNS; no substitute was used. Draft/HOLD, no merge.
