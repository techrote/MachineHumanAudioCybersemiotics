# ACCEL-015 — Afterimage Choir → Receipt Fold (Refs #632)

Native DSP chain only, not VST3 execution, DAW validation or listening. Original score: D4 0.1–0.8 s, C4 1.0–1.7 s, C4/E4/G4 1.9–2.6 s, velocity .8. Afterimage pair (2,6), memory .8, minimum 80 ms; compare fixed parity with preview. Receipt Fold pair (2,4), wet .65; absent, parity, preview, full and bypass.

Recover these three headers into a temporary deps/ directory; check git hash-object before compiling. No vendored copies:
- tools/experimental/instrument-foundry/afterimage-choir-680/afterimage.hpp @ b9f2381cc3d90aecf9c9f4fb17634ce3dce613eb, blob dc45ae5b71f9db76c39236b5736d595b9cc1164b.
- tools/experimental/signal-foundry/receipt-fold-674/receipt_fold.hpp @ b0e7f818fb7cd1a79d99453c408e208adda01334, blob 06d120ebb1fe8deaa696c7eda3a921e65beae0b3.
- tools/experimental/signal-foundry/receipt-fold-674/receipt_live.hpp @ same commit, blob 188a22dc53b7b60e2c2e0aaa73cd21a3e56eaa39.

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Werror -Ideps afterimage_receipt_chain.cpp -o chain
./chain render
clang++ -std=c++17 -O1 -g -fsanitize=address,undefined -Wall -Wextra -Werror -Ideps afterimage_receipt_chain.cpp -o chain-san
./chain-san
```

Both executions passed 60 partition-paired cases, 11,286,000 exact float frames per compiler, 44.1/48/96 kHz, blocks 257/1024, input gains 1 and 3. Checked finite/bounded outputs, exact stereo equality, exact bypass, pre-note/final silence, history and receipt equivalences. Fixed parity and absent are exactly equal for this effect pair; preview and full are exactly equal, not continuous input reconstruction. Source blob 875800313ee17960778be229f287efd22727ba14 verified against commit 5a489c2a57bd23f7628fbbf34efe73f69b4aff62. No host callbacks or deadline measurements.

At 48 kHz and unity drive, unfiltered fixed-memory instrument chain active-window mean (0.1–2.7 s): absent/fixed effect -0.0684780 FS; preview/full +0.00004543; bypass +0.000001455. Peak .121875/.075081/.098446 respectively. The asymmetric quantization introduces DC in the collapse mode; not a perception claim or a general plugin failure. Recommend a normal 20 Hz high-pass after Receipt Fold and conservative output attenuation for audition, especially prolonged listening. The owner audition archive contains six distinct rendered WAVs with identical 20 Hz one-pole DC blocker and .5 postgain, unfiltered measurements, source and checksums. Archive SHA256 f56b413797e155eaac50f6e8e37f524cee708f1e788f9041cfc0b73b6a1efa0f. No actual listening. To recreate in a DAW: Afterimage Choir instrument, Receipt Fold insert, high-pass and -6 dB gain; use fresh instance per comparison. Instrument pair rank 16, effect rank 14. DAW steps untested. Creative interoperability example; no new research acceptance.

Previous exact acceleration head 294607e51542d6917ddfbbbbbd0e813bf6a865ac, Windows run 45822868105: official SDK direct diagnostic success, 36 mixed activation cases, six conformant offline cases, six source-derived disabled-bus cases rejected across 369 blocks, 18 timbre cases/108 witnesses passed. Pedalboard original gate remains red. Integrity 45822868140 passed. Artifact 15118777098 published SHA256 625cdd6fbe9231a23b06adb2fb40ec575bba4b38d8286f360f562ff755629b49 (metadata only). Foundry #597 still 91dc53aca2076665693cbef9f0c61fd913b28745 at inspection. Narrow inactive-bus compatibility fix remains a foundry handoff, not implemented here. #681 and #675 are distinct candidates; both SDK locks agree on official 3.8.0 build 66 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and all seven dependencies; root MIT notice re-read. No SDK build in this native increment; local Git DNS failed. No foundry, main, shared workflow or frozen research changes, no new CI jobs or paid resources. Draft/HOLD.
