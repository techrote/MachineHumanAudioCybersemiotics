# FX-002 qualification receipt — 2026-11-25

AI-assisted implementation and self-check, not independent critique. Base main 495a98ca12bae467a507031f04931aa4254b1866. Source #365 pinned 8054d306ce926b7102ba36ebbbc05d874c8188c6, read model and Results A-D, synthetic/negative boundaries. Prior #467 exact head 0c2deeca933d95a0ccb215d79ce9b662d87f00b3 Windows and integrity workflows confirmed success; corrected artifact listed but not downloaded. Instrument #447/#473 inspected read-only. No duplicate Retreat Shaper PR found. Only new scoped paths. SDK upstream connector resolved v3.8.0_build_66 to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; prior qualified package gitlinks read, current checkout not performed.

Actual Linux x64 GNU 14.2.0 / CMake 3.31.6 core-only build and CTest passed; 742264 assertions, 742270 including render, ASan/UBSan build and execution passed. 17^4 = 83521 four-level histories compared to a separately represented literal bool relay oracle (same author), major loop 34 samples, nested gap 7/8, eight sample rates 1000 to 2000000 Hz including fractional validator rates, float/double finite and bounded output, bypass settling, channel isolation, reset, state version/range rejection and nonfinite/denormal sanitation. Assertions overlap. CTest ran in ~0.02s here, not a DAW CPU measurement. Native CMake used identical core-only target definitions; plugin SDK block not executed. Native GitHub DNS blocked; no plugin compilation, official validator, adapter event/bus/flush validation, real-time benchmark, full repo suite or physical DAW test executed locally.

Exact locally tested git blob SHA: retreat.hpp 5a788758119841147dc216d418bea56421ab1e7e; test.cpp 2bb13a58d1be5b6b987a3a5825e052ff797e220a. Fetched committed blobs matched both. The VST adapter and workflow derive from qualified #439 but are new uncompiled source, not validated by parent CI.

Three 72000-sample raw PCM renders repeated byte-identically. WAV wrapper: standard library wave, 1 channel, 2 byte sample, 48000 Hz. Peak FS A/B .400543212890625, dry .457763671875; final 2400 samples RMS A .186920166015625, B 0, dry .213623046875. No clipping, no listening claim. SHA-256 of WAVs:
- A 0fc660db7f9bcfde2d4c152e070623a7e56c924c3b01ef2a483051e197dfb602
- B e65a8c08960bd1dac3c409ab4467b7cf3695177dcf84ba2192e068b5a447807c
- Dry bc3f9dba69e135743a10962a1b836a5303f9b5e7352d9aaff2f0febe3a68f4d7

Outstanding: exact-head Windows build and validator, package inspection, integrity CI, independent critique, actual host audition, native Linux/macOS SDK builds. Adapter-level validation and expanded CPU and aliasing characterization not claimed. Draft/HOLD.
