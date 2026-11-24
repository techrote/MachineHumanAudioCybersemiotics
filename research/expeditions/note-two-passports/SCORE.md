# Customs counterpoint — original score for two authorities and one oscillator

This is a text score for performers or a computer realization. No claim of perceptual equivalence or cultural authenticity. The names of the offices are fictional, not representations of any real community.

## I. The passport office

Start at 220 Hz. One voice sounds that reference every event. Another voice multiplies its pitch by three, then repeatedly halves it until it lies in [220,440) Hz. After each multiplication and each halving, a different official stamps a sheet of paper. One official is permitted to say "same under the tritave"; the other "same under the octave." Both officials may say "different physical frequency." They never say only "same."

After twelve folded steps, stop. Sound the residual with the reference. Do not tune away the difference.

## II. The closed border

Repeat I with a twelve-step octave grid, using seven steps modulo twelve in place of the exact folded ratio. The last note returns exactly. The officials record that the operation is now approximate. They are not permitted to treat a mathematical closure in a quantized system as evidence of the accuracy of its approximations.

## III. The ministry of sameness

At each event, a third official takes all earlier stamps as a single transitive relation. The official announces only the number of surviving classes. The original oscillator continues independently. In the twelve-step version the final single class contains every pitch. The announcement need not be sung in unison with the oscillator; indeed the point of the movement is the contrast.

## IV. The reverse of the paper

Restore the issuing authority on each stamp. Permit two different answers about the same pair of frequencies. Perform the exact folded sequence for fifty-three steps, then stop, leaving the reference and the last pitch as two separately labelled voices. The return is closer than in I but not exact. The concert may end on this note or before it. There is no mandated correct ending.

For an unpitched performance, replace frequencies with two sets of context-sensitive object labels and explicitly choose which substitutions are permitted; the quantitative theorem need not transfer.

## Executed audio realization

The [renderer](render.py) realizes a restricted, wordless subset of I, II and IV. The left channel is an enveloped sine oscillator, the right the fixed reference. Each event is 300 ms with identical 15 ms attack/release ramps; phase restarts. 16 kHz, stereo PCM16; peak amplitude at most 6000 per channel. It does not render the officials or movement III. No production voice synthesis, acoustic calibration, listening experiment, or claim of perceptual discriminability.

Run python3 render.py. It writes three local WAVs (not committed) and SHA256SUMS. Local Python qualification rendered each PCM stream twice, checked exact rational final states, verified exact grid closure and twelve distinct grid pitches, reopened all WAVs for headers and bytes, and checked the identical right-channel block at every event. Float sine rounding may differ across libraries.

| WAV | Events | Frames | Final left Hz |
|---|---:|---:|---:|
| 01-tempered | 13 | 62400 | 220 |
| 02-rational | 13 | 62400 | 223.0015182495 |
| 03-long-return | 54 | 259200 | 220.4598690890 |

Local SHA-256:
- 01-tempered.wav: 5c1bdf62cbb6a250cb9fcad54cb14774254022c8275729c856ee639153bdae3e
- 02-rational.wav: 1178fca74b04d9289b9aee19c5e2b3e31bb66abdc8054aa7deb37139ad62e1dc
- 03-long-return.wav: 89d51042bbe34afc7be9dd3cd740b5110a22bd8e4376d8d85c2a8d585dba3779

The listener may prefer the close-but-open ending, the closed ending or the longer wandering. This is not a preference study.
