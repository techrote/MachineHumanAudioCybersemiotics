# Six lamps, two skeletons

An original score for a note performer, two bracket editors and an optional witness. Duration flexible; the audio studies are illustrations, not performances of these social roles. Use ordinary instruments, a sequencer or silent counters. Any performer can stop.

## I. A score before its joints

Six notes, equally spaced: A3, E4, B3, G4, D4, A4. Repeat eight times. Place one unit of transferable emphasis at the first event and none at the others. Give every event a small baseline amplitude unrelated to its emphasis. Do not reassign timing or pitch.

Two editors each write three paired event IDs on separate cards. Editor P: (1,2), (3,4), (5,6). Editor Q: (2,3), (4,5), (6,1). Keep the cards hidden during the first rendering. There is no obligation for a witness to guess the grouping.

## II. Two perfectly innocent editors

Both editors use the same operation: replace each pair's emphasis by its arithmetic mean, all pairs simultaneously. Reset to the original score. P acts, then Q acts. Play the result. Reset again. Q acts, then P acts. Play that result. Do not edit a live sounding note retroactively; calculate each version before performing it.

    Event            1    2    3    4    5    6
    Initial          1    0    0    0    0    0
    P then Q         1/4  1/4  1/4  0    0    1/4
    Q then P         1/4  1/4  0    0    1/4  1/4

Reveal both cards. Ask which *changes* belong together, not which performance was correct. If the witness disagrees with both groupings, leave that disagreement unresolved.

## III. The museum's request for agreement

Repeat the two edits alternately without adding emphasis. After each round play one repetition. Eventually the six gains approach the same value. The editors may stop before this happens.

Negative control: use only four events and cards (1,2)(3,4) and (2,3)(4,1). Both orders already agree after two edits. This is an intended contrast, not a failed composition.

## IV. The joint that does not close

A performer can replace one skeleton with a new pairing, refuse the next edit, or reintroduce emphasis. No obligation to reconcile the two cards. Finish with the last state selected by the performers, or with silence.

## Rendered studies (local qualification)

Python 3 standard library renderer, 24 kHz, 16-bit mono, 288,000 frames each, 12 seconds. Eight repeats of six 250-ms slots; same frequencies and envelope, explicit emphasis-to-amplitude mapping. These are original synthetic sounds; not a clinical, psychoacoustic or bistability stimulus calibration.

SHA-256 receipts from one execution on 2026-11-25 (platform libm differences may affect last-bit output on other systems):

    38e4e864e09c524a6882b9bb844253eb010528cf916f0f7b8f547d3b75bedbf0  01-original.wav
    7c80a058c88ed832f2f705e8870e25461deb5a2e3707f8aa383ab620ea773355  02-P-then-Q.wav
    5da4d374ce6f5f000c42beb723ef6e55d926187c04721dacda31df8638f06f7e  03-Q-then-P.wav

Repeated generation, WAV header/payload roundtrip, amplitude bounds and first-phrase slot comparisons passed: slots 3 and 5 differ, other corresponding slots are byte-identical between the two orders. No human audition or perceptual outcome was assessed.
