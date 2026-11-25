# Freeze Socket compensated clock — #466

Parent #439 exact source fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2; qualified Windows run 45534581573 and integrity run 45534581388 both success, unchanged. Origin #422 / #423, direct control contracts with creative attenuation mapping. Separate stacked PR protects the delivered parent artifact. No ABI, IDs, preset format, SDK pin, gain formula, plugin adapter, license, shared workflow, canonical research or human claims changed.

## Defect and correction

Repeated double addition loses enough phase at slow rates to miss the expected integer sample boundary even with the former 1e-12 tolerance. Original exact header Git blob 510fb2ab09690754c21f3c6bea0d3e9c48fd72d6, reproduced locally: 48 kHz, 0.25 steps/s, sample 192000, slot 0 instead of 1. First-boundary probe across nine integer sample rates and seven power-of-two step rates found 14 late cases. Compensated addition retains low-order error across wraps, with a boundary tolerance of eight double epsilons (not a guarantee of exact real arithmetic at arbitrary parameter values). Tiny signed residual is not clamped; paused clock preserves both accumulator terms. No allocation or extra transcendental calls per frame. Assumes normal floating point semantics; do not compile with reassociative fast-math.

## Executed local evidence

Linux x86_64 GNU 14.2.0, C++17, -O3 -Wall -Wextra -Wpedantic: new clock_test passed 119668098 frame/assertion checks (overlapping, not independent experiments), 0 fractional near-tie frames excluded. Wall time 0.724 s on this environment; not a real-time DAW CPU budget. Same test against exact parent header fails at the rational oracle above. -O1 AddressSanitizer + UndefinedBehaviorSanitizer passed same count. Rational oracle covers 63 sample-rate/step-rate pairs, three boundaries each; automated rate changes and pause use exact integer units; fractional reference uses long double and excludes within 1e-8 of an integer. Windows long double precision differs; its run is outstanding.

Native local modified header blob 1a14e951a686cdfa445f51f06e698a06cd325311; clock_test.cpp blob e2c760223e3ec86e768c5ceaaad89124c9444792. Existing test.cpp demo render loop copied into a temporary standalone executable (same source carrier, same parameters, no third-party audio). Corrected 48 kHz renders preserve all three published SHA-256 hashes:
- latch: 5d91efa4d7780f3475a0494c69773bad18c1bcf3c9f0b0c8c531ae29de03a6e3
- pause: 1b878cec88a96a2877eff2a2fd3f6cbc2c108d0526ef492e05dddf296b562f51
- snapshot: 443f910bcb91a231922895df2f30402657830ea519907b369cd7f624d766d170

## Open gates

Native Git checkout still fails DNS. No full native checkout or local VST SDK/adapter build; original full test.cpp suite not replayed in this local run. CTest registration added for existing Windows workflow to execute both suites. Parent pin remains official v3.8.0_build_66 at 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; recursive gitlink and clean-tree guards unchanged. Parent SDK qualification is not child qualification. No new binary, independent review, listening or owner DAW test. Draft/HOLD until corrected exact-head Windows CTest/validator/package and integration review. Same-agent implementation and testing, no human validation.
