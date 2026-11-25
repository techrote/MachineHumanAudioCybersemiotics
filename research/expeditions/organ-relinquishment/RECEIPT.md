# Native synthetic execution receipt

2026-11-25; one GPT-6.2 assistant; native Python 3.13.5. Command: python laboratory.py. Source Git blob in local environment: 1f76c88ac9684ca83397a4f837d3256823032729.

Reachable states, valid/invalid transition checks: (64, 903, 2232). Frontier states are deduplicated at each depth; counts are transition attempts over seven frontier expansions, not distinct histories. Checks: nonincrease of machine seats, single-seat locality, terminal vacancy, guest release only, refusal restoration and complete state coverage. The allowed-transition table is also the validation reference; this is self-qualification, not an independent oracle. 

Each WAV: mono PCM16, 16 kHz, 40,000 frames, 2.5 seconds.

| Scene | States | SHA-256 |
|---|---|---|
| invitation | MMM OMM MMM MOM MMM | f1b98caf92d2e68990534549ff8391ddcd739f42a78e9c88fea09e2bdccbdc8d |
| handoff | MMM OMM GMM GOM GGM | a8c99304751ab21a2fdebc2e48f8a767042e55b2065ed0c4da5dd123ce618e26 |
| vacancy | MMM VMM VVM VVO VVM | 32e7d7079d72bc4ea1fb6f26166f7bc0d5baaa96316f8689b2e1e23083aff6ff |
| release | MMM OMM GMM VMM VVM | f5d2d9fefb75377771268c60f86693ec0c7adf2d8ffc36975da9ed8e0775a60a |

PASS: repeated rendering, bounds, WAV header and payload readback, first invitation block equality, handoff/vacancy difference. No human listener, physical installation or plugin qualification. Audio generated locally, not committed; regenerate with laboratory.py. Cross-platform byte-identical rendering not established. Full repository validator and exact-head CI not run locally; hold for mergedown.
