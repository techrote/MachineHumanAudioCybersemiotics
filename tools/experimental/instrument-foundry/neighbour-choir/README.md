# MHAC Neighbour Choir 0.2.0

Experimental eight-voice, sixteen-node complex graph resonator instrument. Refs #526, #388 and draft #389 at 661e4898ac42b2a44f6808f9d7c0e85434b07f1f. The graph and common-neighbour witness directly realize the source arithmetic; complex phase propagation, damping, note envelopes and timed reinjection are creative synthesis extensions. This is not an acoustic room model or evidence of human perception.

Both the rook and Shrikhande graph obey A²=4I+2J, with eigenvalues -2,2,6. Each sample advances the complex field by d exp(i omega) exp(i theta A). The exact polynomial coefficients are a=cos(2 theta), b=i sin(2 theta)/2, j=(exp(i6theta)-a-6b)/16. The undamped operator is unitary. The root receives an initial unit impulse. At the selected time (default 100 ms), if enabled and the note is still held, compute the two-anchor common-neighbour selector c and inject strength × c*(Ac) (default strength 0.5) at the selected internal nodes. On rook this adds two half impulses; on Shrikhande it adds none. The root itself receives no discontinuous impulse at that time. Linear returns agree mathematically; floating-point arithmetic introduces small numerical differences. The coupling control sets frequency splitting of the three modes relative to the fundamental.

| Control | Normalized | Behaviour |
|---|---|---|
| Topology | 0 rook / 1 Shrikhande | per-note latched |
| Internal intervention | 0 off / 1 on | per-note latched |
| Phase coupling | 0..1 | 0..0.35 of pitch, per-note latched |
| Decay | 0..1 | 0.12..1.5 s amplitude time constant, per-note latched |
| Gain | 0..1 | live, 5 ms full-scale slew |
| Root anchor (505) | 0..15 | normalized index/15, per-note latched |
| Second anchor (506) | 0..15 | normalized index/15, per-note latched |
| Intervention time (507) | 0..2 s | normalized seconds/2, per-note latched |
| Intervention strength (508) | 0..1 | per-note latched |

Coincident anchors deterministically use (root+1) modulo 16 for the second anchor, without rewriting the saved parameter. Eight independent note slots, drop new notes when full (no stealing), velocity and note tuning, 5 ms attack/40 ms release, no transport sync, mono or dual mono, float32/64 adapter, zero latency, conservative 41 ms post-release tail. No automatic voice reclamation before note-off; reset clears all voices. Notes released before the selected intervention suppress it; at zero coupling the internal injection cannot reach the root. High modes near Nyquist are faded out. State NC02 stores nine parameters only, not active notes. NC01 (24 bytes) is migrated by the processor and controller, retaining IDs 500–504 and defaulting the new controls. NC02 is 40 bytes. IDs 505–508 are appended. Older plugin versions cannot read NC02. No real-time allocation or I/O in the core. Conservative hard output bound ±0.5 FS, not a limiter for external processing.

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
Exact root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. The CMake gate requires clean root and recursive gitlinks. Windows CI pins the tag/root, records recursive status, copies SDK notices and runs the official validator. No SDK vendoring or new license. When a qualified artifact exists, extract the complete MHACNeighbourChoir.vst3 directory into C:\Program Files\Common Files\VST3 and rescan an instrument track. The 0.2.0 SDK build and DAW use remain unqualified at the initial DSP checkpoint; the predecessor 0.1.0 qualified separately. Linux/macOS plugin support intended, not validated. Read QUALIFICATION.md for the predecessor and LIVE-QUALIFICATION.md for the 0.2.0 limits.

## New anchor presets

All use note 57, velocity .8, coupling .45, decay .65, gain .7, intervention enabled. Hold at least .5 s. Adjacent Rook (root 0, second 1, .1 s, strength .5) produces an internal witness; matched Shrikhande does not. Nonadjacent Shrikhande (0,6) produces a witness; Rook (0,5) does not. Late witness: Rook (0,1), .3 s, .75 strength; compare strength zero. Automation changes affect subsequent notes, not existing voices. Run neighbour_live_test demos (create directory first) for three stereo comparisons; no listening or DAW render claimed.
