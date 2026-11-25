# Winter With the Wrong Properties
*An original score for two or three performers, four pitch tokens and a word.*

Duration: approximately 4–8 minutes at the performers' discretion. No physical cold, live feedback, strenuous action, recording or network connection is required. Tokens may be voiced, played on ordinary instruments, displayed visually, or tapped. Any performer may stop.

## I — The label shop

Choose four distinguishable, comfortable pitches or other tokens. Write them in a bank, initially 0,1,2,3. Place a counter on slot 0. One performer is the clock and editor, another is the instrument. A third, if present, is the announcer.

The clock advances the counter only on TICK. The editor increments slot 1 modulo four on EDIT. Emit the current token once following each event, including the first HOLD and RELEASE; this is discrete symbolic repetition, not a demand to sustain a waveform.

Perform the event sequence HOLD, TICK, RELEASE three times, resetting all state between takes. The announcer says the same word, FREEZE, on each HOLD. Apply these contracts in turn:

- Output latch: capture current token on HOLD and repeat it until RELEASE, while the clock and edits proceed normally.
- Transport pause: do not advance the counter while held; the live bank remains editable.
- Bank snapshot: copy the bank on HOLD and use that copy until RELEASE; the counter and edits continue.

The exact token traces, including the initial token, are 0001, 0000 and 0011. Play them slowly enough to hear the difference. There is no need for a listener to guess the contract.

## II — The work behind the ice

Reset. Repeat each mode with HOLD, EDIT, TICK, RELEASE. The expected traces are 00002, 00000, 00012. The editor can announce the live bank or remain silent; use the same choice in all three takes.

Next, choose an all-zero bank. Repeat the first movement. The differences have not been removed from the mechanism, but the chosen material no longer exhibits them. Make one authorized edit to slot 1 before holding and repeat. A changing piece can serve as a test of an instrument, though it need not be composed for that purpose.

## III — The cup without wine

Each performer invents a musical metaphor, then names a characteristic they wish to exclude. Offer only one precise rule, with a reset and a simple example. The others may suggest a different operational reading.

Perform the resulting two incompatible rules in succession using a short shared gesture. Announce their literal behavior before performing it. Do not silently change the meaning of an existing control midway through another performer's action.

Optional counterpoint: one voice composes clock behavior, another composes bank edits, a third selects which of the existing contracts governs each voice. Do not permit unbounded loudness or force. Use any comfortable sonic or visual realization.

## IV — A drawer without a switch

Each performer may submit one metaphor that will not be implemented. Place it beside the instrument. Read it, keep it private, or leave it unread. No rule, oscillator or sound is owed in return.

The work ends when the participants decide that the unbuilt drawer is complete. Silence is a valid ending.

---

This is a performable text score, not evidence of actual performance, a human trial, or a validated universal interpretation of the word freeze. The laboratory formalizes only the first two movements' explicit operations.
