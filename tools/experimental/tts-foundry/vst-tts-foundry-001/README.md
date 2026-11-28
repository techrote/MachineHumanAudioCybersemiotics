# MHAC VST-TTS Foundry 001 — LOGOS + ARTICULUM

Draft/HOLD experimental VST3 speech instruments. This subtree is additive and is based on the VST mainline-consolidation candidate, without changing frozen MHAC research records or promoting a scientific claim.

## LOGOS 0.1.0

A bounded procedural phonetic/formant instrument. A non-real-time grapheme-to-phone planner compiles text into a fixed 96-phone plan. The audio engine uses a deterministic harmonic excitation model with three moving formant targets, voiced/unvoiced balance, whispering, articulation, rate, formant shift and MIDI pitch. The VST exposes eight precompiled phrase programs so phrase changes on the audio thread do not run arbitrary text normalization. The standalone renderer accepts free-form text and is the current audition path for arbitrary phrases.

Class IDs:
- processor `E3B14C6F32DA44F1A221D9836F4AC587`
- controller `8D4750C2B91E4F36A3F7C0125EDE2B9A`

Parameter IDs: 2100–2106.

## ARTICULUM 0.1.0

A genuinely separate articulatory architecture. A 24-section bidirectional scattering tract is driven by a glottal pulse plus aspiration. Tongue front/back, tongue height and lip rounding continuously reshape section areas; a bounded nasal branch adds coupling. This is an experimental simplified waveguide/articulatory model, not a calibrated human vocal-tract simulation.

Class IDs:
- processor `5F86D4A1C7284A91B8C12F7DE09A6354`
- controller `D21A8E9063CF4B109A287E5B4471C2DF`

Parameter IDs: 2200–2206.

## Real-time contract

No allocation, dictionary lookup, arbitrary text normalization, filesystem work or unbounded host interaction occurs in either audio loop. LOGOS arbitrary text compilation is a bounded fixed-size operation but is still treated as control/non-real-time work. A fixed SPSC phrase mailbox transfers precompiled plans at block boundaries. VST state exchange uses the existing mainline triple-buffer bridge so UI state calls do not directly mutate audio-owned DSP state.

## Qualification in this revision

Native tests cover 44.1/48/96 kHz, block sizes 1/64/511, deterministic rerendering, malformed text fallback, live phrase replacement, state serialization, concurrent phrase transfer and a 384 kHz long-run tract stability witness. The render target produces original LOGOS spoken/melodic and ARTICULUM tract WAV specimens.

The CI workflow additionally pins VST3 SDK 3.8.0 build 66 and all recorded gitlinks, builds on Windows x64 and Linux, runs Steinberg validator, performs an actual SDK-host MIDI render/state round trip, packages the two bundles and specimens, extracts that package, then repeats validator and host checks against the extracted copies. Sanitizer-native qualification runs separately on Linux.

## Explicitly incomplete

The mission is not closed by 0.1.0. The following remain required before any Ready/merge recommendation:

- custom editor text entry and editable phoneme timeline for LOGOS;
- controller→processor message transport for arbitrary compiled phrases, with cancellation/versioning;
- richer English G2P/dictionary strategy and explicit unsupported-language policy;
- polyphonic/layered voice architecture and voice stealing tests;
- ARTICULUM text-derived articulation planning, plosive/fricative tract gestures and a graphical tract editor;
- DAW tempo-derived phrase timing and transport-aware phrase scheduling;
- preset banks and owner-audition material beyond the generated smoke specimens;
- independent review of CI evidence and owner-authorized promotion into the consolidated catalogue.

No listening result, intelligibility result, perceptual-semantic mapping or validated psychological interpretation is claimed.
