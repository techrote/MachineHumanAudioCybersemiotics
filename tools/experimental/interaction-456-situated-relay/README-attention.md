# Acoustic Attention Economy — Situated Relay extension (#456)

Exploratory synthetic-only Draft/HOLD, AI-assisted single worker, no human studies or real devices. Main at 495a98ca12bae467a507031f04931aa4254b1866; parent candidate 6f0b7c1e536b9d11cc8841b28c3b3d9b1c11b590. Read AGENTS, RAG, programme/runbook, foundations, integrity, validation, experiments, human gates, target issue/comment, prior core/README and recent PR inventory. Prior #457 exact-head repository-integrity passed. This is a separate additive scheduler model addressing the prior core's explicitly recorded starvation limitation, not a replacement for its dialogue reducer or an adoption of another lane's grammar. The user authorizes exploratory apparatus only; original protocol remains unchanged.

## Operate

Open attention.html with attention.js beside it. Select one of five deterministic arrival scenarios and three policies; step, run, publish a new independent observation from any agent, change policy to replay the same input prefix, listen explicitly, and export WAV/JSON. A manual publish advances one tick; selecting a different scenario resets. Node CLI: `node attention.js attention-output` generates three policy WAV/JSON traces and the qualification receipt. Browser and native Node were not run in this environment; source/core execution and inline script syntax were checked in V8. No external runtime dependencies.

## Contract

Three fictional agents independently generate periodic observations; no actual fault, urgency, action, human or device. One tick = 250 ms; each packet requires two consecutive ticks. A new queued observation coalesces the older queued observation of the same agent; it does not invalidate an already playing packet. This models periodic independent updates, not revisions or receipt acknowledgement. Queue bound: one pending per agent plus active packet. Deadline is latest permitted completion boundary. Expire impossible packets before service; outstanding at horizon remain pending, not successes. Each input is replayable from config, policy, until and extra. Trace contains offer/start/interrupted/complete/coalesced/expired events; segments show actual occupied ticks. Completion is scheduler evidence, not actual acoustic recognition. Preempt uses strict priority and restart; priority uses the same ranking without preemption; aging is nonpreemptive with score 4 * priority + age in ticks. Equal scores favor earlier arrival, then deadline and ID. The age scale is an exploratory design decision, not fitted. No universal starvation bound is claimed because deadlines and coalescing can prevent service. Same arrivals, packet duration and rendering for each policy; total energy varies with occupancy and interrupted packets. Original PCM16 mono 8 kHz motifs, tapered envelopes, peak bound 0.08 FS, initial browser playback volume 0.15; no calibrated SPL or listening validation. No waveform decoding. Metrics partition all offered messages; completed-only latency explicitly excludes noncompletions. Occupied minus useful ticks includes partial-at-horizon ticks, not just waste.

## Executed results

11197 assertions, 180 factorial stress executions plus 15 named scenarios, deterministic repeated receipt, source replay; previous 479 assertions and receipt preserved. All scenarios and policies are in attention-qualification.json. Synthetic saturated workload (80 ticks), per-agent counts [complete/offered]:

| Policy | Pump | Fan | Relay | Used / useful ticks |
|---|---:|---:|---:|---:|
| preempt | 0/1 | 39/40 | 0/1 | 80/78 |
| priority | 0/1 | 39/40 | 1/1 | 80/80 |
| aging | 1/1 | 38/40 | 1/1 | 80/80 |

Tight fan deadline deliberately exposes a fairness/urgency cost; expired fan observations: preempt 0, priority 2, aging 2. No implication of operational safety. These are finite constructed scenarios, not estimates of human attention or performance. No policy dominates by construction. Preserve exact receipts and compare future deadline-aware scheduler, identity-bound responses and waveform-derived observations; native DOM/audio and CLI qualification and independent review outstanding.
