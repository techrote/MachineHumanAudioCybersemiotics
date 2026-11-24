# Seven Pulses Before a Decision

Original artistic score; not a listening experiment. Three generated recordings are illustrations, not mandated realizations.

**I. Common material.** At quarter-second intervals, play seven soft, identical 440 Hz pulses, adding a 220 Hz component to pulse four only. Stop. Do not announce a meter. The player may have felt a meter already; the score withholds the subsequent evidence.

**II. The nearest future.** Repeat the opening verbatim, but continue with low accents on pulses 8, 12, 16, 20, 24. In a deliberately simple annotation of four-pulse meter, pulse seven is the pickup immediately before the next accent.

**III. A more distant future.** Repeat the opening verbatim, then accent pulses 9, 14, 19, 24. In a five-pulse annotation, pulse eight instead becomes the immediate pickup; pulse seven no longer has that assigned function. Do not tell listeners that their experience must agree with the annotation.

**IV. The clerk of beginnings (live, unrendered).** Player A produces regular pulses. Player B is permitted to place a new accent after a wait chosen at the last possible moment. Player C marks a paper copy of previous pulses as continuation, pickup, or unknown, with a second ink colour for revisions. A fourth performer sonifies only changes of annotation, never the original pulses. Preserve earlier annotations without claiming them correct. If no coherent meter emerges, leave blank spaces.

**V. Refusal (unrendered).** Play the seven common pulses again, then end. Let the classification remain undecided. The lack of an eighth pulse is the ending of this performance, not missing evidence from some other performance.

## Fiction: The Office of Beginnings

The city had a department whose business was to certify that a bell had begun an event. Its officers were not allowed to listen to the next bell, because that would make the certification retrospective.

A bell rang. The officer wrote BEGINNING. Another bell rang, and a third. The bells continued to arrive in a pattern that made the first sound seem to belong to the previous evening.

The office amended its form. It retained the date at which the bell had sounded, but added another date for the recognition of its role. The city complained that the forms were now twice as long.

A musician borrowed the new form and made a score out of the second column. She played only the changes in the clerk's mind.

The last bell was never certified. It remained in the concert.

## Mechanical ledger

Render with Python 3: `python render.py`. Generated audio is not committed; no external samples. Mono 24 kHz, PCM16, 6000 samples per pulse. Expected hashes from the local run:

```
08d371b12c7653eb731c3ff18e04f83c9c1e41bdd499293d64894f1cda393beb  audio/01-undecided.wav
f44671cd11eed284700a6760f5a75b7d1f8b44a528ecffe94b660e26d99186df  audio/02-four.wav
bbe19863b2b3bc3252bfefdce54b5c865592c555e5fa9df6a440a32448253260  audio/03-five.wav
```

These receipts identify the executed local outputs; floating-point library variation across platforms is possible. The renderer verifies payload identity, prefix equality, divergence at pulse eight, peak bounds and repeat generation. No listener data.
