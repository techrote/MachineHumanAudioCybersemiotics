# Execution receipt — #230

- Authoring tool JavaScript isolate executed the same function definitions serialized to veil_lab.cjs at commit b19fc1088d490dd7535f6567420fe87d513e9d7f: **341 assertions passed**. This is function-level execution, not execution of the Node CLI wrapper.
- Explicit candidate-set minimax independently enumerated for even n=2,4,6,8; recurrence validated for all a,b in 0..12. Count/pair comparisons through n=16. All 35 anchored balanced eight-slot partitions passed exact mixture, energy and byte equality tests.
- Independent Python reproduction executed separately: **93 assertions passed**, matching allocation counts, pair counts, minimax n<=8, 25,600 samples, squared energy 78,754,641,280 per stem, 157,509,282,560 per mix.
- Python generated actual six WAVs; grouped and alternating mono share SHA-256 29a5b2b824dc4a77cd3e78dac3a4770371e877476e4a3b9ffeccac7910823398. Grouped/alternating stereo differ (73fbdf2206d12e61bcc6eab74227119624946ed48cc6234208e1872d328eb7eb / c709ae41c1fbcb0c7e02d73e112b7a38d064a01b5877d5e6aba126d60bbf2122). Python solo A hashes 420c22709ac64e09c9203be4f9764072f082c35de2464920ce77e196cec2ecef / 5e776d43fbc3b7d27c15939d2004ed0578ed35d4b339d33b3367e56b64ac4b65.
- Python output is independent cross-check, not an independent reviewer. Exact PR-head repository CI requires separate qualification; Node CLI qualification follows below. No listening, participant, or field experiment.
- Reconciliation: current AGENTS.md, RAG.md, PROGRAMME.md, AGENT_RUNBOOK.md and newest issue/PR listings consulted; nearest related scope compared in README. Fresh branch from main. No shared paths edited.

## Exact source execution

Fetched both source blobs from PR head 90575e430a6005c8aad82f65b49331db7fe2ebf7 and verified local Git blob hashes: JavaScript 43858a870662867fac1f9bd1c91bf34a02bbcb98; Python fa291b9cfc53fc7bd1fcfa3d01ab0400554006db. Executed Node 22.16.0 CLI: all 341 assertions passed. The separate Python execution passed 93 assertions. Both implementations produced identical rows, sample counts, energy and SHA-256 fields; all six WAV files compared directly byte-for-byte equal across implementations. This resolves the earlier CLI checkpoint. Exact final documentation-head repository CI remains to be verified. No scientific validation is claimed.
