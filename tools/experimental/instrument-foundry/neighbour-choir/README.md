# MHAC Neighbour Choir 0.1.0

Experimental eight-voice, sixteen-node complex graph resonator instrument. Refs #526, #388 and draft #389 at 661e4898ac42b2a44f6808f9d7c0e85434b07f1f. The graph and common-neighbour witness directly realize the source arithmetic; complex phase propagation, damping, note envelopes and timed reinjection are creative synthesis extensions. This is not an acoustic room model or evidence of human perception.

Both the rook and Shrikhande graph obey A²=4I+2J, with eigenvalues -2,2,6. Each sample advances the complex field by d exp(i omega) exp(i theta A). The exact polynomial coefficients are a=cos(2 theta), b=i sin(2 theta)/2, j=(exp(i6theta)-a-6b)/16. The undamped operator is unitary. The root receives an initial unit impulse. At 100 ms, if enabled and the note is still held, compute the two-adjacent-anchor common-neighbour selector c and inject 0.5 c*(Ac) at the selected internal nodes. On rook this adds two half impulses; on Shrikhande it adds none. The root itself receives no discontinuous impulse at that time. Linear returns agree mathematically; floating-point arithmetic introduces small numerical differences. The coupling control sets frequency splitting of the three modes relative to the fundamental.

| Control | Normalized | Behaviour |
|---|---|---|
| Topology | 0 rook / 1 Shrikhande | per-note latched |
| Internal intervention | 0 off / 1 on | per-note latched |
| Phase coupling | 0..1 | 0..0.35 of pitch, per-note latched |
| Decay | 0..1 | 0.12..1.5 s amplitude time constant, per-note latched |
| Gain | 0..1 | live, 5 ms full-scale slew |

Eight independent note slots, drop new notes when full (no stealing), velocity and note tuning, 5 ms attack/40 ms release, no transport sync, mono or dual mono, float32/64 adapter, zero latency, conservative 41 ms post-release tail. No automatic voice reclamation before note-off; reset clears all voices. Notes shorter than 100 ms suppress the intervention; at zero coupling the internal injection cannot reach the root. High modes near Nyquist are faded out. State NC01 stores parameters only, not active notes. Normalized parameter IDs 500–504. No real-time allocation or I/O in the core. Conservative hard output bound ±0.5 FS, not a limiter for external processing.

## Build and audition

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
mkdir -p demos
./build/neighbour_test demos
```

On multi-config Windows use build/Release/neighbour_test.exe. Four original 48 kHz mono PCM16 fixtures: MIDI note 57, velocity 0.8, 450 ms hold, 600 ms total. Default gain is deliberately conservative. Compare linear R/S, then enable internal intervention on both; the two graphs only differ after the witness propagates. For a musical patch use topology rook, intervention on, coupling .45, decay .65, gain .7. Try a slow three-note chord with decay .9 and coupling .2. Shrikhande with otherwise identical parameters is the control. No listening judgement asserted.

For VST3:
```sh
git clone --branch v3.8.0_build_66 --recursive https://github.com/steinbergmedia/vst3sdk.git sdk380
cmake -S . -B build-vst -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/path/to/sdk380
cmake --build build-vst --config Release --target MHACNeighbourChoir validator
```
Exact root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. The CMake gate requires clean root and recursive gitlinks. Windows CI pins the tag/root, records recursive status, copies SDK notices and runs the official validator. No SDK vendoring or new license. When a qualified artifact exists, extract the complete MHACNeighbourChoir.vst3 directory into C:\Program Files\Common Files\VST3 and rescan an instrument track. Native SDK compilation and DAW use are not claimed by the initial DSP checkpoint. Linux/macOS plugin support intended, not validated. Read QUALIFICATION.md for exact limits.
