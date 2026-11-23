# MHAC-X005 — network audio already has a negative-space problem

The closest practical audio precedent found during X005 is not an alarm system. It is RTP voice transport.

## Packet silence is ambiguous

RFC 3551 explains an encoding-independent problem for packet audio:

- silence suppression is desirable;
- packets may also be absent because they were lost;
- therefore the RTP header carries sequence numbers and timestamps so a receiver can distinguish periods when no data was transmitted from packet loss.

This is already an X005-style distinction:

    no media packet arrived

is not a sufficient semantic state.

The receiver needs protocol metadata.

RFC 3550 adds an especially useful limit: after the **last packet actually received**, the receiver cannot know whether later packets were lost solely from sequence-number accounting, because there is no later sequence number yet to expose the gap.

That is a real protocol instance of the finite-prefix problem.

## Silence suppression without pretending nothing happened

RFC 3389 defines an RTP payload for Comfort Noise (CN).

A voice activity detector may identify an inactive speech interval. Instead of transmitting ordinary voice packets continuously, a sender can transmit a CN/SID description so the receiver can synthesize suitable background noise.

The RFC states that a CN packet can be sent at the beginning of an inactive voice segment and updated according to implementation policy.

This is not merely decorative comfort. Structurally, it gives the receiver an **explicit positive artifact associated with an interval in which ordinary speech media is suppressed**.

The receiver is not required to treat total packet disappearance as a self-explanatory acoustic fact.

## Sequence number versus timestamp

RFC 3389 describes another elegant distinction.

After silence suppression, the next normal packet can have:

- a sequence number that increments only by one, because no intervening RTP data packets were sent;
- a timestamp that jumps forward across the suppressed media time.

Thus two clocks/coordinates encode different things:

- packet sequence counts transmitted packets;
- RTP timestamp tracks media sampling time.

Their disagreement makes the quiet interval observable in retrospect.

This is a strong example of a recurring MHAC motif: **do not collapse two quantities merely because one scalar would be convenient**.

## Comfort noise is not semantic resolution

The analogy stops sharply here.

A Comfort Noise payload says something about audio generation during speech inactivity.

It does not say:

- an alarm condition resolved;
- a task completed;
- a source crashed;
- no event occurred;
- the network is healthy.

The protocol metadata disambiguates *media transport behavior*, not arbitrary application meaning.

An MHAC renderer still needs application-level lifecycle semantics.

## AMR frame types make the distinction even more explicit

RFC 4867's RTP payload format for AMR/AMR-WB includes frame types for:

- speech coding modes;
- SID/comfort-noise modes;
- SPEECH_LOST in AMR-WB;
- NO_DATA.

The RFC notes that NO_DATA can have more than one reason, including no encoder data or no data carried in the current payload.

This is another warning against treating a name such as “NO_DATA” as a fully diagnosed hidden cause.

Even explicit negative-space symbols may need subtyping or context.

## Exaptation for machine–human state audio

A future machine-state audio protocol could borrow the **shape** of the RTP solution without borrowing its codec:

- keep event/lifecycle identity separate from sample-time continuity;
- make deliberate suppression distinguishable from transport failure where necessary;
- use explicit low-bandwidth markers for long quiet states if downstream interpretation depends on knowing why the channel is quiet;
- retain sequence/version information so later packets can reveal gaps;
- avoid forcing the acoustic waveform to carry transport, semantic and epistemic status simultaneously.

This is a design hypothesis, not an accepted MHAC architecture.

## The important asymmetry

RTP can often recognize a suppressed interval **after a later packet arrives**, because timestamp and sequence-number relationships become available.

Before that future packet arrives, the receiver may still face a finite-prefix ambiguity.

So the real protocol does not refute X005's theorem.

It demonstrates a practical way of accumulating enough later evidence to break the ambiguity.

That is a better result than a universal slogan about silence.
