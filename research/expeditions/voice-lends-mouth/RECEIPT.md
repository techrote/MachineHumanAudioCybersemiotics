# Follow-up native execution receipt

25 November 2026. This supplements the earlier pure-JS execution described in README.md; the exact committed laboratory was subsequently reproduced byte for byte in a local runtime. Git blob SHA-1: c294c8629ed0a17aa134c4c49763f211d6116f1b (local git hash-object matches remote fetch).

Node v22.16.0, command: node laboratory.cjs audio. Exit 0. All 293,861 assertions passed; 5,460 histories, 2,604 inherited-policy disagreements, four recordings, 32,000 frames each, 16,000 shared prefix frames. Separate Python standard-library wave read confirmed 2 channels, 2-byte samples, 16,000 Hz, 32,000 frames for each export.

SHA-256:
- adopt.wav and cite+adopt.wav: 0087b9b6b533833aae36623811de02779c4a96b65e8ab7bcb152e714f4761701
- cite.wav and replay.wav: 2e1631db9665579fb8706b44c07d4610648d0e4a69cbe1755f8c92bdfa29b4d4

The outputs are deterministic within this runtime; floating-point sine portability across platforms is not guaranteed. No physical playback, listener data, independent review, canonical research validation or full offline repository suite claimed. One AI agent performed both executions. Generated WAVs are distributed separately from the source branch.
