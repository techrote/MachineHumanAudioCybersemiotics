# Native execution receipt — 2026-11-26

Scope: synthetic artistic construction; software self-check only. Python 3.13.5, standard library, actual native container execution. Command: `python laboratory.py audio` (executed with absolute paths in the working container; default output is audio/). Exit 0.

Source SHA-256: `1d6c2b2eef69add7da5167f0e6369a0f53fa5beacf52bb60865206afb51790ec`.
Git blob: `07a8e67d2044710bd997248f6be82848dd2261c5`; repository readback matched native source.

- 64 positive count families (b,c each 1–8), 48,602 distinct words across those families. For every word: independent contiguous unigram/bigram tally equals fixed target, triple-switch equality; analytical histogram checked across every switch count for each family.
- Balanced family b=c=8, 12,870 words. Switch-count histogram for t=1..15: 2, 14, 98, 294, 882, 1470, 2450, 2450, 2450, 1470, 882, 294, 98, 14, 2.
- Complete five-node undirected pentagon: 528 rooted oriented Euler walks; fixed directed tournament: 22 rooted walks. Each checked for exact edge usage and uniqueness; directed family has a single bigram inventory.
- Negative control: changing excursion inventory to seven B and nine C changes the bigram ledger. Three selected performances have three different triple inventories and three different WAV hashes.
- Each output: mono PCM16, 16 kHz, 105,600 frames, 6.6 s; repeated PCM render, amplitude bounds, WAV header and complete payload readback passed.

| WAV | Switches | SHA-256 |
|---|---:|---|
| blocks.wav | 1 | e2f47d9905e1e6686ceb3b96a5fc35efb378b1c0f6c0415624966518bc4a3821 |
| pairs.wav | 7 | b9daacbbbd7d51b34a4ff4ebd2a453f5b0b1fcf7fe43fe87b23465d52d2dced7 |
| alternation.wav | 15 | cdcf9eabe4be0c2ac1c77587760a3604b95a61ce6d45a700c5b5ec89f4e11f37 |

WAV and JSON receipt outputs are generated locally, not committed. Hash equality across platforms is not guaranteed for floating-point libm synthesis. No perceptual test, general Eulerian sampler, real-time plugin, independent review or full repository suite executed in this native experiment. Exact-head repository CI and integration review remain separate. No claim of empirical evidence or novelty.
