# Session-window laboratory (Measurement Run 071, Refs #442)

Draft/HOLD, exploratory synthetic engineering. Parent cf8ed0b6dea0cfc4865ad10a57fbcebd3339fe36; accepted main 495a98ca12bae467a507031f04931aa4254b1866. Adversarial checkpoint 56272fdf8c81661a37b92cc1488baacf8f68e373 retained. Pinned acquisition and transport sources are checked by SHA256 in the executable. No canonical records or human gates changed.

Run with Python 3.13.5 / NumPy 2.3.5:
```sh
OPENBLAS_NUM_THREADS=1 python session-window.py acquisition-rank.py selective-transport.py NEW_OUT
```
Seed 4427101. 16 kHz, 13 slots of 20 ms, pilot plus 16-bit session, byte sequence, byte semantic rank and CRC8. Continuous white noise 1000 counts RMS and 1600 nominal tone peak. Known capture and externally trusted session. Four acquisition candidates. Twenty-four episodes of fourteen events, 264 newly generated PCM captures plus 72 literal waveform replays; 1344 decisions. All policies see identical bytes. Four policies: session alone, retained strict monotonic sequence, volatile eight-position window, retained eight-position window.

| Event (24 each) | Session only | Monotonic | Volatile window | Retained window |
|---|---|---|---|---|
| Legitimate reorder | 24 correct | 24 withheld | 24 correct | 24 correct |
| Duplicate | 24 wrong | 24 withheld | 24 withheld | 24 withheld |
| Expired unseen sequence | 24 wrong | 24 withheld | 24 withheld | 24 withheld |
| Replay after modeled restart | 24 wrong | 24 withheld | 24 wrong | 24 withheld |
| Old session | 24 withheld | 24 withheld | 24 withheld | 24 withheld |
| Same-session unseen stale sequence | 24 wrong | 24 withheld | 24 wrong | 24 wrong |
| Subsequent legitimate same sequence | 24 correct | 24 withheld | 24 withheld | 24 withheld |

All ordinary in-order transmissions recovered, noise withheld. State and observation recount with separate set representation: 1344 decisions, 336 matched event hashes, 56 aggregate groups; two native runs byte-identical. Six WAV exports (one duplicate pair), common quarter scaling peak 1236 counts; JS syntax passed. Source SHA256 df8012b03846eab1ff620e1a8cdec0ec5e28df2bd65692d14a544c3300e18b04.

This is not real persistent storage, session negotiation, authentication, sequence wrap handling, continuous acquisition, physical or human evidence. A previously unseen but stale in-window codeword is indistinguishable from legitimate reordering; admitting it also consumes the legitimate sequence. Expiration is sequence distance, not wall time. Monotonic baseline is modeled retained. No independent acceptance, no merge. Next Measurement: integrity-triggered full replacement on freshly rendered grammatical bodies; evaluate atomic persistence/rollback and non-reuse separately. Adversarial next: held-out decoy geometry and bounded suspension on longer bodies.
