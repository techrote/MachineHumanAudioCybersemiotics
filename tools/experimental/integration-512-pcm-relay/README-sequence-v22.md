# Sequence-qualified compact references (v22)

Refs #512, cumulative Draft/HOLD #513. Synthetic-only, 2026-11-26; one AI-assisted agent, no independent review. Main 495a98ca12bae467a507031f04931aa4254b1866; parent 94796a6a766e4299f1c83e577366ba3551342a4d. Eleven inherited executable Git blob IDs match parent. Parent exact-head Research integrity run 45750081020 succeeded. No frozen research, shared manifests or other workers' branches changed.

## Contract

A compact request now carries the six existing public DATA-tag digits, source and existing sequence (1..16), then two GF(17) parity digits. Distinct reversed preamble (3500 then 3100 Hz); 640-sample preamble, 10 x 640-sample symbols = 7040 samples (440 ms), vs 5760 (360 ms) v20 and 31360 (1960 ms) full-frame request. PCM16 16 kHz mono, peak 4096. DATA/ACK format unchanged; labels on legitimate requests are derived from actually decoded diagnostic DATA, not expected transmitter identity. The receiver scans within host-supplied 33600-sample slots, with no onset or identity oracle. A known gap anywhere in the capture slot prevents acceptance of a detected request. Two separated onsets abstain. Fixed clock, 16-sample scan grid and association outside the supplied slot unqualified. Bank 97280 bytes, at most 67200 bytes of caller PCM, at most two onset clusters retained; JS runtime and inherited receiver excluded. This is not an embedded qualification.

The existing source/sequence fields are not an independent persistent generation number. The scheduler has the same 19 x 2.1 s channel horizon, two DATA attempts per record, first-attempt request lease and no quarantine in either new comparator. The new namespace is incompatible with v20 controls. Neither policy gives a diagnostic interpretation authority to acknowledge. The channel records original request provenance for evaluation only; the resolver does not consult it. Forgery is a synthetic public-frame negative control, not a deployment threat assessment.

## Native results

`node test-sequence-v22.cjs sequence-v22-output` (Node 22.16.0 Linux): 530 assertions; 410 exact symbolic checks of two erasures and single substitutions for the two collision tokens; 18 standalone acoustic controls (two phases) and 12 end-to-end sessions (seed 71). All 24 DATA/ACK exchanges confirmed with a preceding strict receipt, 12/12 alternate-chunk full PCM and compact rescans exact. Four common legacy waveform hashes, full evidence and controls reproduce archived v21 singleton results. Independent Python verifies all 30 WAV hashes, headers, lengths and maximum peak 4096. Elapsed 23.60 s, maximum RSS 75668 KiB. Native Chromium 144.0.7559.96 file input, muted media playhead and exact JSON export passed; ordinary file navigation blocked by administrator, tested via set_content in fresh page. No Windows, physical audition, whole-checkout validation or hardware evidence (git DNS blocked).

| Scenario | Legacy wrong repair | Qualified wrong repair | D confirmation legacy / qualified (s) |
|---|---:|---:|---:|
| bounded replay | 1 | 0 | 25.126375 / 31.426375 |
| expired replay | 1 | 0 | 33.526375 / 39.826375 |
| honest current | 0 | 0 | 33.526375 / 33.526375 |
| no replay | 0 | 0 | 31.426375 / 31.426375 |
| reused sequence and identical packet | 1 | 1 | 25.126375 / 25.126375 |
| forged current | 0 | 0 | 25.126375 / 25.126375 |

Both policies honor one matching current forgery. Old request C tag [11,14,16,1,6,1] equals D tag; qualified C ends [1,15], D ends [1,16]. Stale C is refused for distinct D even beyond v21 quarantine. D admitted at 16.8 s in bounded replay and no replay (v21 quarantine 23.1 s), and no-replay confirmation 31.426375 s vs v21 quarantine 37.726375 s. Different waveforms per policy, paired initial scenarios, same full DATA and ACK framing; slot remainder not reclaimed. Extra request cost 1280 samples / 80 ms; saves 1520 ms vs full frame. In reused-sequence witness D is a new logical offer of the exact same packet as C; no on-wire distinction exists. New evidence cannot establish occurrence identity under arbitrary reuse. Refusing distinct labels restores timeout, not faster repair. No false confirmation test added in this run; inherited weaknesses remain. 

## Source reconciliation

Principal experimental heads refreshed: #443 51de5ccf34186c5f7d64eb994a63ee83152ef90f (affine receipt inspector README); #449 8c5717ca36feb6c83602a4a3ca56b0541b339190 (false-onset README); #453 7eed95ec03c998439e1be061a07d2f924a46ca17 (transaction-leases.cjs, inspected relevant allocator/release and workload portions); #457 8f0e3120b990d77b247dbeaff3a9fa5d1aa67f4f (service-debt README). All four exact-head structural workflows passed, not accepted findings. Grammar address-scoped lease concept relevant; no upstream implementation imported. No repo-wide license found at LICENSE or LICENSE.md; no third-party reuse or new license grant. Read FM-1-MHAC and FM-1-CYDaux main README read-only; no firmware changes. Foundry PR titles inventoried, no DSP imported. AGENTS/RAG and core programme/runbook/experiment/human gates/integrity/validation authorities inspected. No claims about human interpretation or reliability.

## Run and next action

Extract ZIP and open Open Inspector.cmd or sequence-v22-inspector.html; load sequence-v22-output/receipt.json and matching WAVs. Start optional audio at low device volume. Standalone control WAVs are independently playable; inspector compares session pairs. Node has no third-party dependencies. Next: independently transmitted non-reused transaction generation with explicit admission, durable pre-exposure reservation, crash/rollback and finite namespace saturation; test DATA/ACK association too. Distinguish freshness from authentic origin. Keep v21 quarantine as a complementary policy; do not promote v22 as universally safe.
