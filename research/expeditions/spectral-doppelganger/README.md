# The Spectral Doppelgänger

Refs #199. Exploratory, synthetic mathematical and artistic work; not human evidence.

## Question and relation to existing work

Can distinct event sequences share an apparently informative signal fingerprint, even after adding higher-order correlations? This expedition treats descriptor collisions rather than signal-channel separability (#41), temporal causation (#183), joint witnesses (#195), or continuous identity drift (#197). Live main at reconciliation: 495a98ca12bae467a507031f04931aa4254b1866. All changes remain in this directory.

## Formal model

A pattern S is a subset of the cyclic group Z/nZ, represented by a binary vector f. Its second-order descriptor P(a)=sum_x f(x)f(x+a) is the ordered difference multiset, including repetitions at zero. Its discrete Fourier transform equals the squared magnitude of the DFT of f: expand the product F(k)conj(F(k)) and collect terms by difference. Thus equality of P implies exactly equal circular power spectra, regardless of numerical FFT error. Translation and reflection preserve P. The canonical bracelet is the lexicographically least tuple among these transformations. Distinct bracelets establish collisions even after quotienting by these symmetries.

A higher-order descriptor T(a,b)=sum_x f(x)f(x+a)f(x+b) counts anchored triples; repeated positions are intentional. Reflection transforms T(a,b) into T(-a,-b), so take the lexicographically smaller entire array, not the componentwise minimum. Fourth-order counts extend the same construction. Descriptors are integer arrays, not approximate hashes. Lower-order counts can be recovered by repeated offsets.

The classic 12-slot pair {0,1,4,6} and {0,1,3,7} has common pair descriptor (4,1,1,1,1,1,2,1,1,1,1,1). It is separated by the triple descriptor. Exhaustive bracelet enumeration for n=3 through 16 finds 539 ambiguous pair classes; none remain ambiguous after triple refinement in that bounded domain. This is not a general reconstruction theorem.

## Deliberately adversarial search

Restrict to even n=2m and sets containing exactly one of every antipodal pair. Then f(x+m)=1-f(x), |S|=m. Apply the half-turn to the sum defining T:

T(a,b) = sum_x (1-f(x))(1-f(x+a))(1-f(x+b))
       = n-3m+P(a)+P(b)+P(b-a)-T(a,b).

Therefore 2T(a,b)=P(a)+P(b)+P(b-a)-m. On this subfamily, third-order correlation contains no extra distinguishing information beyond second-order correlation. This is an exact identity, not an empirical observation.

Enumerating the restricted subfamily at n=8,10,...,24 produces six pair-collision classes at n=24 and none at the smaller surveyed sizes. This is not a minimum over all unrestricted patterns. Two discovered representatives are:

X = {0,1,2,3,4,5,6,8,10,11,19,21}
Y = {0,1,2,3,4,6,7,8,9,11,17,22}.

These are different bracelets, with identical ordered pair and triple arrays even before normalizing reflection. The reflection-normalized fourth-order arrays differ in 3168 of 13824 entries. This is a specific rescue, not a proof that fourth order always suffices.

## Results

Full binary survey: 131064 patterns across lengths 3–16; 5094 bracelet representatives; 539 second-order ambiguity classes. Counts by length:

| n | bracelets | ambiguous pair classes | unresolved triple classes |
|---:|---:|---:|---:|
|3|4|0|0|
|4|6|0|0|
|5|8|0|0|
|6|13|0|0|
|7|18|0|0|
|8|30|1|0|
|9|46|0|0|
|10|78|3|0|
|11|126|0|0|
|12|224|23|0|
|13|380|6|0|
|14|687|72|0|
|15|1224|80|0|
|16|2250|354|0|

Restricted antipodal search: 8176 patterns across lengths 8–24; at n=24, 102 bracelets and six ambiguous pair classes. All such collisions also collide in third order by the identity above.

## The instrument and its possible exaptations

Each rhythm is upsampled to a grid of 1800 samples per slot, convolved circularly with the same integer bipolar triangular click kernel. This construction has no overlapping clicks or clipping. Upsampling and circular convolution preserve equality of circular power spectra: the upsampled difference counts occupy integer multiples of the slot duration, and the common kernel multiplies each complex Fourier coefficient by the same factor. Both channels are written as 12 kHz signed 16-bit PCM with four repetitions (7.2 seconds for the 12-slot pair; 14.4 seconds for the 24-slot pair). The output is an original comparison score: one rhythm in each channel, not a psychophysical experiment. Each channel can be listened to separately. Four repeated complete periods also have equal circular power by the same periodic extension argument. Arbitrary cropping, windowing, cross-channel interference, nonlinear processing and unequal kernels do not inherit that guarantee.

Potential transfer: adversarial unit tests for phase-blind music retrieval, rhythm codebook design, synthetic telemetry descriptor audits, texture/structure generation constrained to shared pair statistics. Do not automatically upgrade feature collisions to semantic or perceptual equivalence. In a real task, define what distinctions matter before choosing a quotient; phase and direction may be essential. An explicit anchor or raw sequence comparison may be preferable to expensive high-order statistics. This work does not claim a universally adequate feature set, a new homometry theorem, a listening outcome, or suitability for operational alerts.

## Provenance and execution

Background sources inspected at abstract/summary level only, 2026-11-23:
- Grimm and Baake, *Homometric Point Sets and Inverse Problems* (2008), https://arxiv.org/abs/0808.0094 (abstract: equal autocorrelation and nonunique inverse problem).
- Jaming and Kolountzakis, *Reconstruction of functions from their triple correlations* (2002 preprint), https://arxiv.org/abs/math/0207051 (abstract: translated triple counts).
- Keleti and Kolountzakis, *On the determination of sets by their triple correlation in finite cyclic groups* (2006), https://arxiv.org/abs/math/0603415 (abstract: cyclic reconstruction problem and second-order insufficiency). No full-text theorem attribution or priority claim.
- *Reconstructing Colourings of Finite Groups*, RWTH Aachen repository https://publications.rwth-aachen.de/record/698365 (repository abstract and indexed section 3 summary: self-complementary subsets as sources of 3-deck failures). The antipodal identity above is independently derived and tested here; this is a rediscovery-oriented expedition, not a claim of novelty in the mathematics.

AI-assisted implementation and self-review. No human or independent reviewer. Local Python standard-library commands:
    python -m unittest -v
    python doppelganger.py --max-n 16 --out run

Eight tests passed, including direct correlation cross-check over every binary pattern at lengths 3–8, orbit invariance, negative controls, exact integer circular PCM correlation on a smaller grid, and all 576 triple offsets for each antipodal witness. The survey and audio generator completed. Local tested Git blob hashes:
- doppelganger.py e5a50b8498e0f97bc67da008969d3976c02e10e6
- test_doppelganger.py 945e2da0d0577cb7f9a3ef63eaa28e9e58d007f2

Generated WAV SHA-256:
- pair.wav ae557d1fa6d5fb58340ba0a36810c6c008441340082a64fe4e989bbc3632e869
- third-order-collision.wav c48f746e406155829ee8082a70214e1725e5a1cb1f7fffe772e25e45189cf079

The executable regenerates the complete survey JSON and WAVs; binary outputs need not be committed. Remaining: independent review, repository CI, clean-checkout hash comparison. No claims of human testing. Public source provenance is URL/abstract-level only; no source copies or licenses asserted.
