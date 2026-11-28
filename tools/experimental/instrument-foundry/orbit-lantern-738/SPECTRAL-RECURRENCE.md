# INST-011L — Spectral carrier recurrence and Windows recovery

Refs #738; creative synthesis interpretation of draft #265 at 56c107f8f4147316a588484c47be28bc8f840fbb. Parent 648a2b6760e5aeaf83caf23342793004a37582f5. Reuse the dominant Fourier recurrence phasor in the spectral carrier instead of evaluating a second cosine/sine pair per active spectral voice per sample. The legacy non-spectral path retains the same summation order. No change to VST3 parameter IDs, state, class IDs or plugin adapter. Spectral depth remains native-only.

Windows run 45971543290 job 140412915492 failed before SDK checkout: MSVC C4701 (l,r,u,v potentially uninitialized), promoted to C2220. Initialize the regression locals without disabling warnings or assertions. Windows recovery needs new-head CI; no new binary claimed.

GCC 14.2 Release CTest 7/7 PASS; Clang 17 ASan/UBSan spectral probe PASS. 4,097 phase samples times 35 cutoff positions: Fourier sums exactly equal, dominant phasor within 1e-12 of direct trigonometry, zero carrier if cutoff excludes dominant. 503,144 checks including renders/benchmark per invocation. Both original spectral WAVs and 22 prior preset/audio files reproduced byte-identically. No listening assessment.

Alternating baseline/candidate GCC O3 benchmark at 96 kHz, 32 frames, eight releasing voices: means (us) 44.4905/42.8546, 46.2157/45.4128, 45.1922/43.1944; misses 6/6, 9/4, 3/7 of 4000 blocks respectively. Candidate maxima 1226.59, 1994.66, 2036.79 us. Sanitized candidate 51.832 us mean, 669.142 us max, 9/4000 misses. Modest observed mean reduction, no hard real-time or statistically established speedup claim. Modulation sidebands remain unqualified.

SDK official tag v3.8.0_build_66 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; seven exact root gitlinks and full recursive trees verified via API, none truncated or containing nested gitlinks. Local git ls-remote fails DNS resolution; no SDK consumed, no substitute. Use existing exact SDK build instructions and notices. Draft/HOLD, no independent review or merge.
