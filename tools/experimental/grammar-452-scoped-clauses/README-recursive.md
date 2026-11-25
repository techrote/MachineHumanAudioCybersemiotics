# Recursive acoustic clauses — Grammars Run 002

Refs #452 / Draft PR #453. Additive independent codec beside the unchanged fixed-frame GF(7) lab at 29a5ebd195e8d943236f532cf289feb9061fb8ad. Based on the scope distinction in that prototype; Interaction PR #457 at 6f0b7c1e536b9d11cc8841b28c3b3d9b1c11b590 exposes symbolic receipt metadata, not a waveform decoder (PR description inspected). No claim of accepted research, novelty of prefix or bracket syntax, or human comprehension. Synthetic only; no real device control. One GPT-6.2 agent, no subagents.

## Contract

AST is a nested array: [operator, ...children]. Four atoms, seven unary operators (including distinct quotation, question, negation and attributed report), two ordered binary operators (and, if). This is a syntactic representation; no truth evaluation, reference resolution or operational effect. An operator's arguments are ordered; not(quote(fault)) differs from quote(not(fault)). Prefix encoding is self-delimiting on clean complete frames given known arities. Closed encoding emits an explicit END tone after each compound. Decoder accepts only exactly one whole tree; unknown/erased tokens, trailing symbols and missing closes refuse. Bounds: 128 slots, 64 nodes, depth 12 (root depth zero). No automatic error correction.

Each token has a separate frequency from 400–1700 Hz, 80 ms slots, 60 ms active, 16 kHz mono PCM, digital peak 4096/32768. Phase-invariant sine/cosine projections over 40 ms inner windows (integer cycles), minimum energy, score and runner-up thresholds. Exact slot/frame alignment required. No synchronization, unknown frequency drift, real noise or human perception qualification. Silence = erasure, not a valid word. Tone phase is arbitrary constant per generated frame in this test, not a channel model for all distortions.

## Executed experiment

Exhaustive ordered trees of 1–4 nodes: 4, 28, 228, 2044; total 2304. All clean trees decode uniquely in both grammars. Enumerate one unknown-position token deletion (remove slot and concatenate; not silence), every one-token substitution in the common 14-symbol alphabet, and known-position erasures (null). Same AST population and alphabet; closed adds a tone per compound, so aggregate slot counts and nominal energy are higher, not matched. No statistical sampling or listener learning is asserted. Substitution counts include END in both modes (invalid in prefix). A deletion census weights longer messages by their number of slots. Do not interpret the raw case fractions as a channel probability without that distribution.

| Mode | Slots | Single deletions wrongly accepted | Single deletions refused | Single substitutions wrongly accepted | Single substitutions refused |
|---|---:|---:|---:|---:|---:|
| Prefix | 8920 | 5208 | 3712 | 40976 | 74984 |
| Closed | 14832 | 0 | 14832 | 40976 | 151840 |

For the closed grammar, let L be leaves, U unary compounds, B binary compounds. Any valid tree has L=B+1. Deleting a leaf or binary opener violates that identity; deleting a unary opener leaves a surplus END; deleting an END violates the equality of compound openers and END. Thus no single token deletion can yield a valid closed tree, independent of the tested depth. This is rejection, not recovery, assuming complete frame boundaries and otherwise perfect tokens. Substitutions between equal-arity operators can silently change meaning; deleting both the unary opener and its END can also change meaning undetected. See retained witnesses. Explicit close is not a substitute for redundancy or integrity checks.

PCM: 120 frames over six examples, two modes, five phase values, clean and erased; all expected outcomes. 48107 assertions per V8 execution; two identical receipts. Substitution enumeration records outcomes, not an assertion that all substitutions are detected. Native Node CLI/filesystem, listening, external channels, whole repository validation and independent review not established.

## Reproduce

Node.js 18+ standard library: `node recursive.cjs output-recursive`. Generates the JSON receipt, 12 original WAV recipes rendered as WAVs and SHA-256 manifest. CLI wrapper not exercised in V8; no claimed generated on-disk WAVs until run. Call `encode(tree, mode)`, `decode(tokens, mode)`, `render(tokens, phase)`, `receive(pcm)`, `wav(pcm)` or `qualify()` for Observatory adapters. The committed receipt is from the computational core executed directly in V8. Compare against it; cross-engine floating-point ties may affect PCM.

Next: frame synchronization, per-token phase and frequency variation, matched latency/energy comparator (padded prefix with integrity check), scoped reference binding and explicit corruption/abstention traces. Retain Draft/HOLD; original Run 001 remains unchanged.
