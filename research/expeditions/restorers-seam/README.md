# The Restorer's Seam

*An archive that sings the holes in its own history.*

Refs #222. Exploratory humanities, finite mathematics and original synthetic sound art; no Track E/G advancement or empirical listener results. AI-assisted expedition, 2026-11-23. Base: 495a98ca12bae467a507031f04931aa4254b1866.

## The smoothness of a lie

A conservator acquires five bars of a damaged mechanical score. Three interior bars are gone. The two survivors sound the same note. The restoration software repeats that note across the gap. This is a defensible act of composition: economical, symmetrical, and pleasant in its structural regularity. It is not a defensible statement that the missing historical musician played three identical notes. Perhaps the very interest of the original was a violent interruption.

This is the subject of this expedition: not simply how much information has been lost, but how the aesthetics of repair acquire a falsely documentary authority. We distinguish **material survival, admissible completion, regularization, and historical warrant**. In the synthetic model these are separate operations. In the arts their boundaries are negotiable; in an evidentiary archive the distinction is consequential.

The 1964 Venice Charter presents a particularly fruitful tension. Article 3 puts the artwork and its historical evidentiary function together. Article 9 limits conjectural restoration; Article 12 asks that missing replacements fit the whole without becoming indistinguishable from originals. Article 11 also rejects stylistic unity as restoration's governing end. This is a conservation position about monuments, not a universal algorithm for sound. But it offers a surprisingly usable analogy: a smooth waveform can be an aesthetic success and a documentary failure simultaneously. IASA's ethical principles §2.2.2 provide a more directly pertinent archival precedent: preserve the unmodified transfer, apply subjective enhancement to a copy, and document interventions. See [SOURCES.md](SOURCES.md).

Auditory perception introduces a contrary demand. Warren's chapter 6 summary describes contextually appropriate perceptual completion where an intervening masker obliterates parts of a sound. The listener may experience continuity despite an absence of the relevant signal. Perception is not archival misconduct; it has no obligation to give an evidence receipt for every percept. Yet the machine that exports a repaired recording has an institutional choice the ear does not: it can preserve the missingness mask, and it can refuse to represent its inference as measurement.

What happens if we make that distinction itself into an instrument?

## Exact finite model: two optimalities and a missing history

Let each event be a symbol in {0,1,2}; the record is (1, ?, ?, ?, 1). Here '?' is missingness and never means a rest or zero-valued symbol. A completion must preserve every observed coordinate. With no additional grammar, k independent missing coordinates give 3^k compatible sequences. For this case k=3, hence 27 possibilities. This is a combinatorial fact, not a probability distribution.

Define smoothness energy E(x) as the sum of squared differences of adjacent symbols. The unique minimum is the constant sequence (1,1,1,1,1), because energy zero requires equality at every adjacent pair and both anchors equal 1. The compatible rival (1,0,2,0,1) has energy 10. If a historical process generated that rival, the smooth reconstruction would make three symbol errors. Both satisfy the exact same observed data. A unique optimizer is not a uniquely identified historical sequence.

A second question: suppose we wish to minimize worst-case reconstruction error, not merely smoothness. We consider all compatible truths and restrict predictions to compatible sequences.

- Under Hamming loss, for any prediction an adversary may choose a different symbol independently at each missing coordinate, so worst-case loss equals k. Every completion ties.
- Under squared symbol loss the worst-case cost at a missing coordinate is max((a-0)^2,(a-2)^2). This is 4 for a=0 or 2, and 1 for a=1. The coordinates are independent, so the minimax prediction inserts 1 everywhere and has worst-case cost k. This is a unique risk optimizer, but it is still not an observation.
- Thus the constant completion in this example wins both smoothness and squared minimax criteria. Neither confers identification. Under Hamming loss even its relative advantage disappears.

Squared symbol loss is a declared ordinal coding choice, not a psychoacoustic distance. Remapping symbols or choosing a different loss can change the result. A minimax action can be useful even when every proposed history remains uncertain. No probability or human hearing data have been introduced.

**Countercases:** With observed sequence (0,?,2), imposing the known grammar |x[i+1]-x[i]| ≤ 1 leaves exactly (0,1,2). Without that grammar there are three options. A cap of zero yields no compatible history, a model/data inconsistency, not a license to manufacture one. When no coordinates are missing, the model already identifies the sequence and worst-case error is zero. The sidecar conservatively calls even grammar-identified but unobserved samples conjectural: a future version should separate logical entailment under a named grammar from direct acquisition.

This last point matters beyond music: an observation and an inference can have the same value but different provenance. If the step-cap assumption came from a damaged instruction manual rather than the mechanism, apparent uniqueness may merely express an erroneous premise. Do not use the finite result as a universal claim that restoration is impossible.

## A score for uncertain restoration

The generator produces five original stereo PCM16 recordings, each 1.25 seconds, 16 kHz. Discrete symbols drive integer triangle oscillators (160, 200, 250 Hz nominal). Every event has an independent short linear envelope, so they are repeated attacks, not a continuous-tone illusion stimulus. There is no calibrated masking or perceptual evaluation.

| Recording | Purpose |
|---|---|
| 01_gap | Preserve missingness as silent placeholder; receipt distinguishes gap from actual rest |
| 02_noise_placeholder | Replace missing intervals with arithmetic pseudo-noise, not measured original audio |
| 03_smooth_conjecture | Minimum smoothness / squared-risk completion |
| 04_rival_conjecture | A compatible but aesthetically discontinuous alternative |
| 05_audit_insert_only_right | Full proposed completion left; only newly inserted events right |

The last recording is not a proposed universal audible provenance convention. The point is the possibility of a parallel audit bus. Since the same event can sound different depending on its provenance, or identical despite different provenance, the artist must decide whether to make the seam heard or keep it inspectable elsewhere.

Run from repository root:

    python research/expeditions/restorers-seam/seam_lab.py --out build/restorers-seam
    python -m unittest discover -s research/expeditions/restorers-seam -v

The generator creates disposable files plus a JSON receipt with compatible-world counts, risk minimizers, per-event provenance labels, and SHA-256 for every WAV. No copyrighted recordings are embedded. The code is intended for tiny finite models only; pairwise minimax evaluation is quadratic in number of completions and enumeration exponential in missing coordinates.

## Exaptation: a palimpsest workstation

An audio editor could offer three views which are independent, rather than three competing versions of the truth.

1. **Acquisition**: immutable transfer, timestamped missingness mask, carrier/recording metadata and source hash. A mask is not inferred from a string of zeros without additional evidence.
2. **Conjecture**: nondestructive alternative layers; each records its algorithm, parameters, conditioning evidence, cost function, assumptions and predecessor. Store multiple plausible fills, not only the winner.
3. **Audition**: compose a mix for listening, with toggleable source, candidate, candidate-difference and insertion-only buses. A seam may be beautiful, jarring, concealed or rhythmic; no one sound automatically conveys warranted confidence.

The artistic opportunity is to compose with the difference between admissible histories. A single score becomes a bundle of performances, and the missing region becomes a constrained generator rather than a place to hide damage. A deliberately unfilled interval might be a new musical voice. A composition can migrate from archaeology to improvisation without claiming that the improvisation recovers the past.

For MHAC interfaces, a repaired telemetry segment, guessed transcription, or interpolated state should carry its own provenance even when it happens to coincide with a later verified observation. A future experiment could cross auditory seam salience with independently disclosed provenance and measure source attribution, task accuracy and aesthetic preference separately. A clean auditory seam might help recognition; a prominent seam could also distract. Neither conjecture has been tested here. No production requirement follows.

## Contrary readings and future trails

- A monument has layered material histories and living social uses; a digital waveform is a sequence of numbers. Conservation cannot be reduced to a coordinate mask. IASA offers the more direct institutional comparison, but neither source settles creative synthesis ethics.
- A reconstructed passage may have good historical warrant from an independent copy, score, witness, or documented grammar. The model explicitly admits that case; do not privilege roughness or treat all repair as forgery.
- Plausibility is not necessarily suspect. Sound restoration legitimately improves access. The objection concerns falsely attributed provenance, not high-quality enhancement.
- Audible seams alone are fallible labels. Listeners may overlook them, hear them as a musical event, or mistake authentic damage for a generated insert. A persistent sidecar and separate disclosure mechanism are stronger candidates for future evaluation.
- The formal result uses observation fibres already explored in #178 and #187; its distinct contribution is the conflict between two optimization criteria, exact error bounds, and archival/aesthetic policy. #203 studies loss incurred in observation; here the mask is already given. #197 concerns drift under incremental resemblance, not selection among alternative pasts. These are bounded comparisons, not proof of literature novelty.
- An actual archive would need immutable source objects, sample-range masks, edit reversibility, validation of provenance assertions, explicit uncertainty and lawful rights; this toy implements only event-level sidecar labels.

A useful next rabbit hole is a *conservation counterpoint*: competing restorations from different historical periods can be performed in separate channels while the surviving source appears at the centre. But the resulting spatial arrangement is itself a curatorial claim, not a discovered dimension of history.

See [AFTERWORD.md](AFTERWORD.md) for the original fictional continuation and [EVIDENCE.md](EVIDENCE.md) for executed checks.
