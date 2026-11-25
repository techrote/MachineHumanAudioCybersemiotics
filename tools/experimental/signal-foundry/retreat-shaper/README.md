# MHAC Retreat Shaper 0.1.0

Experimental VSTfx / reusable C++17 DSP. **Source candidate; native DSP tested on Linux; plugin qualification pending.** Based on [#364 / PR #365, Result B](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/8054d306ce926b7102ba36ebbbc05d874c8188c6/research/expeditions/dial-remembers-retreat/README.md). Direct realization of the two finite, nonnegative relay ensembles at m=8, creative mapping of ON mass to attenuation. Not a magnetic material model, research novelty assertion or human perception result.

Each channel uses independent relay histories. Upper thresholds are 9..16. Bank A lower thresholds are 7,6,5,4,3,2,1,8; Bank B 8,7,6,5,4,3,2,1. Ascending and descending saturation sweeps agree exactly; the nested input 0,15,1,14,2,13,3,12,4,11,5,10,6,9,7 ends at mass 7/8 vs 0. Both banks evolve continuously, including in bypass; changing coupling crossfades their current masses, not their state. Detector level = floor(16*min(1,abs(input)*drive)), with drive 1..16x. Target gain = 1-depth*mix*(1-mass), bounded 0..1, 5 ms full-scale slew. No added signal, latency, audio tail, allocation or external service. Saturation or a zero detector level erases memory; silence resets relays, not stored parameters. Instantaneous magnitude, not an envelope follower; ordinary sinusoidal zero crossings erase memory, so try biased envelopes, square/pulse signals or slow asymmetric waveforms. No anti-aliasing/oversampling; nonlinearity can create harmonics and aliasing. No claim of magnetic realism.

| Parameter ID | Name | Normalized mapping |
|---|---|---|
|100|Drive|2^(4p), 1..16x|
|101|Coupling A-B|linear interpolation of both ON masses|
|102|Depth|attenuation 0..100%|
|103|Mix|wet contribution 0..100%|
|104|Bypass|slewed unity gain; history continues|

Preset recipes (Drive, Coupling, Depth, Mix, Bypass): Research A (0,0,1,1,0), Research B (0,1,1,1,0), Hybrid (0.5,0.5,0.65,0.75,0), Dry (0,0,0,0,0). Parameters only, M H R S version 1 little-endian millionths, no relay or gain history in preset. Host-native parameter editor; no custom GUI. Sample-offset events applied as steps, gain slew smooths changes. Mono/stereo, float/double; channel-independent dynamics can alter stereo image. Inputs outside finite range are sanitized only for nonfinite/denormal values; attenuation never exceeds the input magnitude, so use normal DAW gain staging.

## Native build and demos

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure

Create an output folder and run retreat_test with that path. It writes three 48 kHz mono signed little-endian PCM files (72000 samples each). Convert with Python standard library wave module or import as raw audio, 16-bit little-endian, 48 kHz, mono. 500 Hz square wave follows 15 levels for 100 ms each. A/B use full depth and mix; third file is dry. Rendering scales by 16000 before int16 rounding; same scaling for all. Reference test and render are original synthetic data. No listening test.

## VST3 build and owner delivery

SDK pin: official v3.8.0_build_66, root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. Clone exact tag, verify root, recursively initialize gitlinks and keep SDK clean. The build rejects any different root, uninitialized/mismatched submodule or dirty checkout.

    cmake -S . -B build-vst -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/path/to/vst3sdk
    cmake --build build-vst --config Release

The scoped Windows workflow uses the same proven SDK setup as Freeze Socket #439, official validator and portable ZIP with source identity and SDK notices. Do not claim an installable binary until that exact-head workflow passes. Once qualified, copy the entire MHACRetreatShaper.vst3 bundle into C:\Program Files\Common Files\VST3 and rescan. Linux/macOS plugin compilation remains intended, not validated. VSTGUI is disabled. See QUALIFICATION.md.

SDK gitlinks observed in previously qualified Freeze Socket package (this plugin's actual checkout must reverify):
- base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206
- cmake de6e54eeaaab35b7145f5c32c279b5e892146e04
- doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4
- pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c
- public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95
- tutorials 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34
- vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c
