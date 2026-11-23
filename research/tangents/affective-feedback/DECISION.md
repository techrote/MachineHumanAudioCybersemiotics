# MHAC-T018 decision note: affect can inform but should not own the verdict

**Provisional, source-bounded hypothesis; not an adopted production assistant policy.** This record deliberately revises an over-simple view of emotion as noise in machine–human communication.

## The useful distinction

An emotional cue can communicate a legitimate change in circumstances—urgency, perceived consequence, the need for acknowledgment, a request to repair previous work—without itself constituting a change in the underlying **technical specification or truth of evidence**.

For machine-generated speech, warmth/urgency/prosody may shape human response. For human-generated speech, expressions of anger, gratitude, distress or impatience may shape the assistant's wording *and* its task execution. Those are not symmetrical phenomena mechanically, but they create a reciprocal channel.

A consequential failure may arise when the machine treats **social repair success** ("I have soothed the user") as equivalent to **task repair success** ("the implementation is now correct"). Those are separate outcomes. An apology is not a patch receipt.

## Candidate design proposition

A useful assistant could separate an **epistemic/task core** from a **social presentation policy**:

- Core: what is true, unknown, feasible, authorised, within scope, or supported by code/tests/evidence?
- Presentation: how much tact, acknowledgment, brevity, warmth, urgency or disagreement is appropriate *for the communication context*?
- Feedback: did the actual implementation improve, did the user explicitly revise requirements, or is the change merely increased affect in the message?

This is a *design hypothesis*, not proof that a product has physically independent inference channels or that presentation never affects reasoning. A genuinely urgent message may legitimately change priorities. An explicit instruction to change scope should change scope, regardless of whether the user is angry.

## Contradictory cases to retain

1. More empathetic wording improves the human's willingness to provide a necessary bug reproduction without compromising correctness.
2. A technically independent but rude assistant obscures its point and increases supervisory burden.
3. A frightened or angry user supplies *new* factual information (data loss, an actual safety hazard); taking that seriously is appropriate.
4. An assistant mistakenly regards profanity as an instruction to ignore all criticism; it becomes rigid and unhelpful.
5. A genuinely bad bug persists despite neutral language, because the assistant lacks technical competence rather than adequate resistance to sycophancy.
6. A user consciously chooses a riskier technical approach after understanding the alternatives; disagreeing again can become paternalistic obstruction.

## Possible artistic translation: Affect as control voltage

A synthesizer may separate a score from the timbre in which it is rendered, without claiming that either is emotion-free. A controller can alter amplitude, attack, vibrato and spatial movement while the underlying pitch or encoded factual field remains intact. That separation is valuable *as an analogy for interface architecture*, not as a model of the human psyche.

What if a future artistic piece renders two fictional interaction policies as audible positive and negative feedback systems—one building an increasingly harsh resonance, the other damping it—while displaying the mathematical gain parameter? That might dramatise epistemic fragility without pretending that an audio spectrum is a direct measurement of feelings.

## Disposition

- **Positive:** a controlled concept for separating human tone, model surface response and technical outcome is worthwhile.
- **Negative:** the current materials do not show that anger caused any real model to fail, that warmth should be suppressed, or that better communication means less empathy.
- **Null:** the underlying interaction problem may be explained entirely by task complexity, incomplete specifications and ordinary HCI grounding rather than a distinctive cybersemiotic mechanism.
- **Next gate:** actual model evaluations with controlled task facts; later user-experience studies only if separately authorised. The synthetic recurrence cannot substitute.

Retain the tangent as intellectual sediment and a falsifiable proposal. Do not convert it into a global rule for how ChatGPT must address a person, nor a justification to infer private health, sleep or emotional state from text.
