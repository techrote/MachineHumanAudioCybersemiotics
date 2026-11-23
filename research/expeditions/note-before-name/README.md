# The Note Before Its Name

**Scope:** issue #224, synthetic formal expedition, AI-assisted self-review only, 23 November 2026. Base 495a98ca12bae467a507031f04931aa4254b1866. No change to Track E/G, frozen registries, human gates, or canonical design requirements.

## Question and exact model

A variable-length sonic alphabet assigns distinct nonempty binary words to tokens. Assume noiseless synchronized bit cells, a known starting boundary, and arbitrary infinite token streams over a fixed finite codebook C. There is no guaranteed terminator in the live setting. For finite messages separately assume an observed end of message. How long can two streams disagree about their first token but agree on every received bit?

Do not collapse unique finite-message decoding, prefix freedom, bounded first-token identification, acoustic bit recognition, or semantic understanding.

## A three-way falsifier with identical length budget

| Codebook | Finite unique decoding | Live first-token identification |
|---|---|---|
| 0, 10, 11 | Yes, prefix-free | At most 2 bits |
| 0, 01, 11 | Yes, suffix-free | No uniform finite horizon |
| 0, 01, 10 | No | Not guaranteed even with end marker |
| 0, 01 | Yes, nonprefix | At most 2 bits |
| 0, 01, 110 | Yes, nonprefix | At most 4 bits |

The first three share lengths 1,2,2 and Kraft sum 1. For the second code, finite unique decoding follows from suffix freedom: decode from the right edge. But the infinite stream 011111... has two tokenizations, 0|11|11|... and 01|11|11|.... For the third, 010 = 0|10 = 01|0, even with a known end. A checksum or finite-message roundtrip is not by itself a deadline guarantee. The fourth code is a negative control: nonprefix does not entail infinite delay.

## Exact graph and proof

A state (u,v) stores the nonempty unconsumed suffixes of the two currently selected words. Start with every unordered distinct pair of first words. If their leading bits differ, no synchronized continuation exists. If equal, consume one bit from both sides. A side reaching a word boundary selects any codeword as its next suffix; otherwise it retains its remaining suffix. All transitions consume exactly one shared bit.

By induction, each path from a start represents two token streams with distinct first words and an identical received prefix of length equal to the edge count. Conversely all equal prefixes of such streams induce paths. Every finite path extends separately to two infinite streams (not necessarily a common continuation). The graph is finite: its states are drawn from the Cartesian square of the set of nonempty word suffixes.

A synchronized transition finishing both words yields a finite collision. Conversely any finite collision can have its common initial token sequence cancelled, so a collision is reachable from one of the distinct first pairs. Breadth-first traversal produces a minimum-bit-length collision witness; a pair of possible first words plus a common finite bitstring is independently checked by a dynamic-programming parser.

A reachable directed cycle yields an arbitrarily long common prefix and a repeatable infinite lasso (all edges emit one bit). Conversely a finite graph with arbitrarily long paths contains a reachable cycle. In the acyclic case the longest path length H is the maximum ambiguous prefix length. With at least two codewords, H+1 bits suffice to identify the first token in an infinite stream, and some prefix of H bits does not. This is an absolute first-token observation horizon, not the standard codeword-count delay or a delay measured after the end of a particular codeword. A one-word alphabet is trivial and needs zero bits.

If S is the number of distinct nonempty suffixes, the graph has at most S squared states; finite H is at most S squared minus 1. This is a coarse bound, not a sharp complexity theorem. The implementation explicitly explores graph edges and uses recursive DFS, so very large inputs may exceed runtime limits; no real-time guarantee.

## Constructive family and census

For m >= 1, take C_m = {0, 01^m, 1^(m+1)0}. It is suffix-free: neither of the first two words is a proper suffix of the third or of each other. Only first words 0 and 01^m can initially agree. If the short word is followed by a word starting 0, the common prefix stops at length 1. Otherwise it is followed by the third word, which contributes m+1 ones. The longer first word finishes after m ones and can select the third word to match one further 1. On the next bit the first stream emits 0 while the second still emits 1. Thus H=m+2 exactly. A matching prefix is 01^(m+1). Every family member is uniquely decodable and finitely identifiable, yet no horizon independent of m suffices. This is an elementary construction, not a priority claim.

Exhaustive census of all 4,060 unordered three-word subsets of the 30 nonempty binary words of lengths 1–4: 2,462 prefix-free, 800 nonprefix UD with bounded horizon, 186 UD with unbounded horizon, 612 non-UD. The maximum finite H among the nonprefix UD cases is 10, attained for {011,0110,1101}, with common prefix 0110110111. This is an exact finite census, not a sample of deployed protocols.

The executable experiment compares all 4,060 finite UD classifications against an independently written Sardinas–Patterson residual closure, validates 612 finite collision strings with dynamic-programming parsing, checks five repetitions of each of 798 cycle prefixes (including non-UD), compares 364 short codebooks with direct bitstring enumeration through length 10, and evaluates C_m for m=1..32. The direct prefix oracle is horizon-limited; it does not by itself prove the unbounded cases. The cycle proof supplies that implication. Results are from the same JavaScript functions serialized into decoder.mjs, executed in the tool's V8 runtime. Node clean-checkout reproduction and full repository CI remain separate gates. No external human reviewer or subagent.

## Acoustic experiment and reuse

Original stereo render maps each bit independently to 440 Hz (0) or 660 Hz (1), with identical deterministic envelopes and 3,300 samples per bit at 22,050 Hz. The left and right finite streams for the unbounded example contain 29 and 30 bits; their first 95,700 PCM sample pairs are identical. The first unequal sample is at index 95,701 (zero based). The endpoint is the only difference in this rendition; both tokenizations remain compatible with the shared prefix if there is no known EOF. This is not a claim about hearing or perceptual equality under different rendering. The finite-delay control uses 01100 and 01110, two valid finite streams for {0,01,110}; first unequal sample at 9,901.

Potential reusable machine: a codebook preflight that reports finite collision or lasso certificates and exact worst-case live observation horizon, rather than scoring only average word length. For synthesis, audition word-boundary ambiguity as an intentionally delayed resolution, while avoiding claims that a listener reconstructs hidden boundaries. For embedded protocols, event transports and symbolic agents, check a stated finite alphabet under known bit timing before accepting a decode deadline. An explicit terminator, reserved separator or bounded frame can repair some ambiguity, but incurs overhead and changes assumptions. No fault, packet loss, timing jitter, semantic confusion, privacy, or safety evaluation is included.

## Sources and boundaries

- Jean Berstel, Dominique Perrin and Christophe Reutenauer, *Codes and Automata*, chapter 5, “Deciphering delay”, pp. 199–224, DOI 10.1017/CBO9781139195768.006. [Publisher chapter summary](https://doi.org/10.1017/CBO9781139195768.006), read 23 November 2026: distinguishes finite lookahead counted in letters and codewords. Summary only, not full chapter or proof reading.
- Cover and Thomas, *Elements of Information Theory*, 1991, chapter 5 problems, printed p. 123, problem 24. Search-visible text of this problem was inspected via a digitized copy; it explicitly raises the distinction and lists the examples 0/01/11 and 0/01/10. Original publisher text was not acquired. These examples are established pedagogical examples, not original discoveries.
- Sardinas and Patterson, “A necessary and sufficient condition for unique decomposition of coded messages” (1953): original not retrieved. The name and residual algorithm were cross-checked via secondary overview ([Sardinas–Patterson algorithm](https://en.wikipedia.org/wiki/Sardinas%E2%80%93Patterson_algorithm), algorithm and termination sections). The product-graph argument above is self-contained and does not claim novelty over coding/automata theory.

Crosswalk: #209 addresses future-context coding; #211 known-period streams under missing/corrupt observations; #187 silence; #199 feature collisions. Here no corruption, no context change, no feature reduction: the bitstream itself can fail to determine an early token. This also differs from #218 joint disclosure: observation is a single serialized stream.

## Reproduce

Run from this directory with Node.js and Python 3.11+ (standard library):

    node run.mjs > /tmp/note-before-name-results.txt
    diff -u results.synthetic.txt /tmp/note-before-name-results.txt
    python3 render.py

Local Python execution generated both audio files (not committed; original deterministic generator supplied). WAV SHA-256 in this execution:

- end-of-message.wav: dd43ca4b92eff23813713626fab55b046942d3dc2838c85f1f6f897f3151e621 (99,000 frames)
- finite-delay.wav: dba62ed081144af53886254836804d297e8d44a48d032bebf8431078ed7633d1 (16,500 frames)

Floating-point libm rounding across platforms is not guaranteed byte-identical. The bit-level proof does not depend on the audio waveform.
