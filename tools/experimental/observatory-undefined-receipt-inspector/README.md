# Observatory — affine receipt quantisation inspector

Refs #undefined, #428, [draft #429 at pinned source](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/07fb2f67a5a2cf26312699410f00152033cae843/research/expeditions/missing-beat/README.md). Base main `495a98ca12bae467a507031f04931aa4254b1866`. Synthetic-only apparatus, AI-assisted single-agent implementation and computation, 2026-11-25; no human study, independent review or accepted empirical evidence.

## Run

Download this directory (or check out the draft branch), open `index.html` locally with `core.js` beside it. No network, install or server required. Select gap pair, sampling rate, nominal span and frame. The four deletion receipts show exact normalized triple ratio, sample indices, partition, Bayes index accuracy under uniform deletions, conditional entropy in bits and original WAV playback/export. Playback is opt-in; set hardware volume low. Digital peak bounded by 9000/32768 even if all three pulses overlap; no SPL calibration or safe human exposure claim. Browser execution and listening not performed in this run. All core functions, including the renderer and SHA-256, executed in the connector V8 isolate. CLI alternative with Node: `node core.js` writes receipt.json in cwd and prints assertions; Node invocation itself not executed here. Use an empty scratch folder for CLI output.

## Model and baseline

No jitter, no insertions, uniform one-deletion index, known nominal motif (0,p,p+q,2p+q), exact positive integer gaps. Receipt-relative mode maps the surviving endpoints to the nominal duration; fixed mode assumes a known external frame mapping original endpoints, including deleted endpoints. Both use exact integer half-up rounding, 100 ms lead and equal total duration, 20 ms integer triangular carrier/taper (500 Hz, different waveform from source), same PCM16 level. Exact ratio is measured separately from sampled receipt. Group by ordered sample vector; for equally likely deletion indices, optimal index accuracy = number of groups/4; H(D|receipt) = sum over groups (size/4) log2(size). Fixed frame adds timing information and is not an apples-to-apples decoder improvement. No stochastic inference, error bars or participant interpretation. No RNG (finite factorial).

## Executed receipt

- 1036 assertions passed, including SHA-256 known-answer vectors, literal WAV equality, sample indices, partitions, header/peak and invalid input checks. JS core executed directly in V8, not Node/browser. Full factorial: 288 conditions (16 gap pairs × 3 sample rates × 3 spans × 2 frames).
- Receipt-relative: 66/144 ambiguous; 57 with 1 bit conditional entropy; mean optimal index accuracy 0.7864583333333334. Fixed: 0/144 ambiguous, mean 1. These are finite design summaries, not population estimates.
- Source witness p=144 q=89, 8000 Hz, span 800 ms: deletion 2 and 4 both [800,4755,7200] despite distinct exact ratios; literal PCM/WAV equality and equal SHA-256 reproduced with independent renderer. Fixed clock separates all four at this condition. The retained waveform is not the source waveform; only the index/equality result is reproduced.
- `qualification.json` retains complete replay trace, conditions, source pin, specimen hashes and assertion result. Not every factorial row has an audio hash; selected conditions generate hashes on demand; full trace is not an archived audio corpus.

## Remaining limitations

No actual onset detection from noisy audio, frame estimation, jitter, sample-phase variation, perceptual data or independent cross-runtime test. Fixed frame can be lost in real systems; quantisation may depend on sample phase. Browser/Node qualification and full repository checks pending. Future useful extension: expose phase-offset sweep and robust onset detection; retain exact distinction from psychoacoustic effects. No shared manifests, canonical evidence, license, study gates or other branches changed.
