# Exact bounded quadratic receiver (adversarial run 003)

Refs #448, #428; additive continuation of Draft #449, adversarial lane. Accepted main at intake 495a98ca12bae467a507031f04931aa4254b1866; parent e9c7dc8a1d7e9c1dae54b767bc6efd96f5147d0a, previous integrity workflow 45538382068 success. No new codebook optimization or human evidence. Single ChatGPT agent; repeated execution and separate algorithm cross-check are not independent review. Synthetic apparatus outside canonical evidence/protocol records. Original codebooks and run 002 receipt retained unchanged.

## Observation contract

Sorted, distinct exact 8 kHz onset sample indices, not waveform features. Three genuine of four onsets retained; optionally one false onset. Scale s in [0.6,1] seconds, translation free in receiver (generator samples [0.1,0.2] seconds), quadratic warp 4 b x(1-x), b in [-D,D], independent timestamp error at most J and nearest sample quantization. Use integer half-sample ticks (16000 ticks/sec), E=J*16000+1. For each deletion triple and observation subset enforce y_i-E <= o+s*x_i+4*b*x_i*(1-x_i) <= y_i+E. Closed bounds admit rounding ties. Stronger receiver also requires unmatched onset prequantized timestamp in [o,o+s] with only half-sample quantization, not independent jitter. Neither receiver assumes generator's translation prior. Exact refers to this closed feasible-set model, not maximum-likelihood inference or physical timing generally.

## Solver

Normalize integer coordinates p by L, multiply inequalities by L squared. Eliminate translation by requiring each lower bound on o to be no greater than each upper bound: integer half-planes A*s+B*b<=C. Insertion-bound variant includes o>=f-1-s and o<=f+1. Eliminate s with every lower/upper scale bound pair, intersect rational one-dimensional bounds for b. Rational cross-products checked safe integers. Separate BigInt vertex enumeration cross-checks sampled calls; signed warp boundary and insertion-bound known-answer tests included. Monotone warp/order holds (s>=9600 ticks, |b|<=240 ticks). Envelope prefilter uses 1e-7 tick slack; run 002 counts checked exactly. At D=0 exact triple sets must equal envelope. Exact triple subset of envelope; insertion-bound subset of exact triple; all retain truth. Duplicate-index observations remain invalid in denominators. Not a general-purpose solver for unbounded coordinates.

## Evaluation

Replay all 36 run 002 cells, 55,296 trials, identical generator/seeds and envelope outcomes; reanalysis, not independent evaluation. New seeds 3011,4027,5009, eight repeats per seed/word/deletion, same factorial, 27,648 trials. No tuning on either set. Exact counts for synthetic draws, no human/population inference. Same codebooks and underlying pulse budgets; no new acoustic clock side channel. Insertion-bound receiver has stronger information than triple receiver if false onset placement is otherwise unknown.

Selected results (2 ms jitter, 15 ms warp; uniquely correct, invalid retained in denominators):

| Dataset | Codebook | False onset | Trials | Envelope | Exact triple | Exact + insertion bound |
|---|---|---|---:|---:|---:|---:|
 | replay | source8 | false | 1536 | 254 | 819 | 819 | 
 | replay | source8 | true | 1536 | 39 | 329 | 474 | 
 | replay | source8_searched | false | 1536 | 540 | 1427 | 1427 | 
 | replay | source8_searched | true | 1536 | 36 | 431 | 600 | 
 | replay | robust8 | false | 1536 | 406 | 1436 | 1436 | 
 | replay | robust8 | true | 1536 | 40 | 477 | 655 | 
 | heldout | source8 | false | 768 | 123 | 423 | 423 | 
 | heldout | source8 | true | 768 | 12 | 169 | 241 | 
 | heldout | source8_searched | false | 768 | 272 | 703 | 703 | 
 | heldout | source8_searched | true | 768 | 28 | 220 | 315 | 
 | heldout | robust8 | false | 768 | 184 | 716 | 716 | 
 | heldout | robust8 | true | 768 | 10 | 239 | 338 | 

All three receivers had zero wrong accepts and zero truth omissions among valid trials. Abstentions in JSON. Residual ambiguity may be reducible under richer models (translation prior, signal identity, statistical priors, longer words); no claim robust8 dominates. Retained first rescued cases reproducible via seeds and traces. Prior literal PCM replacement examples preserved, not regenerated here.

## Reproduction

Run node quadratic.cjs OUTPUT_DIRECTORY next to false-onset-receipt.json. CLI writes quadratic-receipt.json and prints checks. Core executed twice in connector V8, identical JSON; 194149 checks per run including 371 separate-algorithm vertex comparisons; 291032 exact feasibility calls. Native Node CLI/filesystem, waveform detection, listening, full local repo validation and independent review not yet performed. Draft/HOLD. Next: matched-energy, matched-duration additional pulse labels or longer words against replacement obstruction; unreliable pulse identity classification.
