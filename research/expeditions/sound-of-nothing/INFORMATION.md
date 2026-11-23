# MHAC-X005 — information note: when identical silence carries zero world identity

The silence quartet is deliberately artificial enough to support one exact information-theoretic statement.

## Hidden variable

Let W be the hidden scene identity:

- explicit resolution;
- channel failure;
- delayed alert;
- intentional rest.

For the simplest calculation, assign each scene prior probability 1/4.

Then:

    H(W) = -4 * (1/4) log2(1/4) = 2 bits.

## Observation variable

Let S be only the raw PCM content of the shared 1.0–2.5 second interval.

The generator enforces:

    S = SAME_DIGITAL_ZERO_WINDOW

in every hidden scene.

Therefore S is a constant random variable.

For every scene w:

    P(S = zero | W = w) = 1.

The marginal also satisfies:

    P(S = zero) = 1.

## Mutual information

Mutual information is

    I(W;S)
      = sum_w sum_s P(w,s)
        log2( P(w,s) / [P(w)P(s)] ).

Here the only observation value has probability 1 and

    P(w, zero) = P(w).

So every logarithmic ratio is

    P(w) / [P(w)*1] = 1,

whose logarithm is zero.

Therefore:

    I(W;S) = 0 bits.

The silent samples themselves do not change the prior distribution over the four constructed scene identities.

This remains true for a non-uniform prior: a constant observation cannot distinguish the hidden worlds.

## Distinguishing observations

If a later observation uniquely identifies each of four equally likely scenes, then the observation can carry the full 2 bits of scene identity.

Intermediate channels can carry values strictly between 0 and 2 bits.

The code includes a generic finite-channel mutual-information calculation and tests:

- identical silence -> 0 bits;
- four unique deterministic observations -> 2 bits under uniform prior;
- a partially distinguishing two-world channel -> strictly between 0 and 1 bit.

## Why this is not a semantic theory

Shannon's framework deliberately abstracts from semantic meaning.

The result therefore does **not** say:

- silence has no meaning;
- a listener learns nothing during the interval;
- the listener lacks prior context;
- silence is aesthetically empty;
- all four scenes are physically identical outside the interval;
- semantic information is exhausted by mutual information.

It says something more exact and narrower:

> In the authored four-scene channel, the chosen raw silent-window observation variable is statistically independent of the authored hidden scene identity.

The larger trace is not independent. The scene labels, prior protocol, pre-silence events and post-silence events can all carry information.

## A useful decomposition

For interface design, it can be helpful to ask which random variable is being measured.

Possible variables include:

- instantaneous acoustic samples;
- event history;
- message identity;
- source state;
- channel health;
- semantic lifecycle;
- listener interpretation.

A signal can have zero information about one of these and substantial information about another.

For example, the shared zero window carries zero information about **which of the four authored scenes** is active, but trivially reveals that the acoustic sample in that window is zero.

This prevents a common rhetorical mistake: “zero information” always requires specifying **about what**.

## Artistic reading

John Cage's 4′33″ is a useful anti-example to “silence has no information.”

The work's lack of intentional performer sound redirects attention to ambient events and the performance situation. X005's PCM interval is instead forcibly set to digital zero.

They are almost opposite constructions:

- Cage removes intended performer sound so environmental sound becomes salient.
- X005 removes all waveform variation in the selected interval so contextual history becomes the only source of scene identity.

The comparison is artistic, not a claim that Cage was doing Shannon theory.

## Engineering reading

If a status UI renders four semantically different states as the exact same observable output, that output cannot discriminate those states.

This does not automatically mean the UI is bad. The distinctions may be irrelevant at that moment or available elsewhere.

But if the user must act differently across those hidden states, the system has created an identification problem that no downstream decoder of that output alone can solve.

That is the same observation-fibre structure inherited from X001, now restated probabilistically.
