# Three Winters 0.1.0 — live instrument adapter (INST-007B)

Refs #596, #597, #422, #423. Native predecessor 0ff3f440e7fb64051d39ab2f50a22dee3fe8b0c8. [Pinned research §§3–4](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/03e3f121fbb2362d76db4d6cd597d27ae087ea8b/research/expeditions/metaphor-becomes-socket/README.md). The discrete freeze contracts are formal realizations; clocked pitch counterpoint is a creative interpretation, not human evidence.

## Performance

Play normal MIDI notes. Three lanes share a four-slot bank with token intervals 0, 3, 7, 10 semitones. HOLD gates the three different contracts; while held, try edits and ticks. Manual tick is a rising edge (return it to zero before retriggering). Internal clock runs continuously during rendered samples, including silence; it starts with a full interval, retains fractional phase on rate changes, and resets on mode changes. It is not host-tempo synchronized. Manual ticks can supplement the internal clock. Parameter points at the same sample are applied in ascending ID order, then notes, then automatic clock and audio. Continuous lane gains use a bounded 5 ms slew. No custom UI. Note tuning is accepted in cents, capped at +/-1200; high pitches are capped at 0.45 sample rate. Four slots, no stealing; duplicate note IDs (including same channel/pitch fallback while releasing) are rejected.

| ID | Parameter | Normalized default / mapping |
|---|---|---|
| 1000–1003 | Bank slots 1–4 | 0, 1/3, 2/3, 1; discrete four tokens |
| 1004 | Hold | 0; gate |
| 1005 | Tick | 0; rising edge |
| 1006 | Internal clock | 0; manual |
| 1007 | Clock speed | .2; 0.5 + 7.5*x Hz |
| 1008–1010 | Latch/Pause/Snapshot gain | 1 each |

Main stereo is latch + half pause / snapshot + half pause, mono is their half-sum. Optional inactive-by-default mono auxiliary buses are Latch, Pause and Snapshot. Main is always a monitor; mute it in a DAW mixer when separately mixing the three stems. Zero algorithmic latency; note release <=40 ms, reported tail ceil(.041*sampleRate); main bounded +/-0.3 FS, each stem +/-0.2 FS. No waveform freeze.

TW01 state: 48 bytes, magic then eleven little-endian float32 normalized values. Hold/tick are transient and always encoded as zero; score position, capture, voices, oscillator and clock phase are not serialized. Restore starts a silent reset with the bank and clock/gain patch restored. Activation/reset releases gates; re-send control values after restart. State/lifecycle operations require serialized access with audio processing; simultaneous state restore/callback has not been qualified. No prior plugin state version exists. Stable new class IDs D1195E6E-292C442C-B550AE83-4977E4CD and 992821A7-B1114FB3-8B69B059-EC25C81C (SDK FUID word notation). Host bus negotiation, sample-offset mapping and state paths are implemented but not locally compiled or host-tested.

## Patches / build / audition

Normalized parameters 1000–1010:
- Manual Winters: 0, .3333333, .6666667, 1, 0, 0, 0, .2, 1, 1, 1.
- Auto Counterpoint: 0, .3333333, .6666667, 1, 0, 0, 1, .2, 1, 1, 1.
- Clocked minor thirds: 0, .3333333, 0, .3333333, 0, 0, 1, .6, 1, .6, .8.

Native: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run winters_live_test with any argument in an empty working directory for winters-clock.wav and winters-stems.wav, 6s/48kHz stereo and 3-channel PCM16. Notes 48 and 55 (+7 cents), 2 Hz clock, hold 1s, slot 2 edit 1.5s, slot 3 edit 2s, release 3s, note-offs 4s. No listening claim.

SDK: clone official v3.8.0_build_66 recursively, verify exact root and all dependency commits in SDK-LOCK.txt. CMake -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=<clean SDK checkout> with CMake 3.25+; build MHACThreeWinters and validator. The scoped Windows workflow reuses the qualified Offcut workflow structure; requires clean official validator summary with no ERROR lines, archives licenses, gitlinks, source SHA and bundle. Install entire MHACThreeWinters.vst3 in C:/Program Files/Common Files/VST3 and rescan. Linux/macOS plugin targets intended, not verified.

## Native receipt 2026-11-25

Linux x64 GCC 14.2, warning-as-error Release CTest 2/2; new test ASan/UBSan PASS. Original 256 bank witnesses retained. New manual edge, snapshot/release witness, TW01 state corruption rejection, automatic clock at ten rates (1 kHz–2 MHz), voice rejection/release, +1200 cent pitch count, mono Float32 vs Float64 main and optional stems, 231300 paired sample frames. Two native demo regenerations matched (SHA256 e4f42aa3df1ec950c648ebcfdea979fa6bde569e08851ab578f0409645058121 and 8450840e76f676512ce349847bfa16d73543ef2b41943bae7bea825e80ba656c); stereo peak .123753 FS, silence from 4.05s. Offline 10s/4-note benchmark .079–.084s. No real-time deadline certification. Native tested blob IDs: live.hpp 563ff4be1b133e1d270b1aa248c13baaf5ba7944; live_test.cpp 0155ccba407bc3db5379ca7fcb244d2b714794d0; winters.hpp d38325619c619ac621d9aacfaa2ae77b93639b25. The native CMake was tested before adding the inherited optional SDK section; exact final build-file qualification remains CI work.

Official tag resolves upstream to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; all seven inherited dependency commit identities freshly resolved in official upstream repositories. Root .gitmodules matches the seven dependency paths. Local git retrieval fails DNS; no SDK substitute. New adapter transformed from qualified Offcut #589 at 03fc88a6f9c5bb3928a5fbaa5ede9c6490c23643; no sibling dependency. No Windows binary or validator claim at this checkpoint. AI-assisted single-agent implementation and tests, no independent review, host audition or empirical claims. No shared manifest or frozen record edits.


## INST-007C — 0.1.1 release-tail re-articulation (2026-11-25)

The above 0.1.0 duplicate-ID policy is superseded for a matching **releasing** voice. A new note-on using the same ID may re-articulate that slot without resetting oscillator phase, instantaneous frequency, envelope or velocity. Pitch (including tuning) glides to the new target; velocity slews at a full-range 5 ms rate. Active non-releasing duplicate IDs and new IDs at capacity still reject; no arbitrary voice stealing. This addresses ordinary same-pitch/channel fallback note IDs during fast repeated passages. The four-note capacity and TW01 state, FUIDs and parameter IDs are unchanged. Distinct new IDs at capacity and overlapping same-key notes without distinct host IDs remain limitations.

Prior exact 0.1.0 head f4c98a667c87ff7d521157a028dbf85cf2acba56 qualified on Windows run [45682340971](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45682340971), official validator 47/47, integrity PASS. Artifact inner SHA256 5a53197e252bb80bc63c8848cf5d22012e215ad898909387b69b44b430dff81d. This result does not qualify 0.1.1.

Baseline regression reproduces rejection at the first release-tail retrigger. Revised Linux GCC 14.2 C++17 warning-clean Release CTest 3/3, new retrigger ASan/UBSan PASS. Thirty saturated-polyphony cases at ten rates, three velocities, phase/envelope/increment/velocity continuity, output bound and complete silence after release. Existing clock/stem WAVs regenerate byte-identically against the 0.1.0 receipts above. Run `winters_retrigger_demo retrigger.wav` for a two-second stereo passage with 24 same-key note-ons, 30 ms gate, 20 ms gap, varying velocity, internal clock and HOLD/EDIT/RELEASE. Compile the same renderer against the pinned 0.1.0 headers for comparison: old 12/24 accepted; new 24/24 accepted. New WAV repeats byte-identically, SHA256 0c3c62eb42855ab60cd5d5805beada9a2d83cc59b38fbf1adef4aa21cca813fe; legacy WAV 1ee9c06166c3d33de0e38ec5dd92fdc83070ae86fd391464e83f7dd9c926daf7. No listening or DAW claim.

SDK root/tag and seven direct gitlinks reverified against official GitHub data; all seven pinned commits resolved. Local git DNS blocked, so use unchanged scoped exact SDK Windows qualification workflow for the new head. Concurrent state access, host automation, auxiliary routing and independent review remain outstanding. AI-assisted engineering repair, no empirical research claim. Refs #596.


## 0.2.0 — independent timbre automation (INST-007E, 2026-11-25)

Refs #596, #422/#423, pinned 03e3f121fbb2362d76db4d6cd597d27ae087ea8b README §§3–4. The continuous socket is a creative harmonic synthesis extension of the formal freeze contracts. Existing pitch controls 1000–1010 remain unchanged. New normalized parameters:

| ID | Control | Default |
|---|---|---|
| 1011–1014 | Timbre bank slots (continuous harmonic crossfade) | 0 |
| 1015 | Independent timbre HOLD | 0 |
| 1016 | Independent timbre TICK rising edge | 0 |
| 1017 | Independent internal timbre clock | 0 (manual) |
| 1018 | Timbre speed (0.5 + 7.5 × normalized Hz) | 0.2 (2 Hz) |

TW02 is 80 bytes (four-byte tag, 19 little-endian float32 values). TW01 48-byte states migrate with neutral timbre. Both HOLD/TICK pairs are transient and zeroed on restoration; cursors and phases are reset, not serialized. Four shared notes, twelve oscillator lanes, zero latency, unchanged monitor and three optional mono outputs. Full timbre amount can suppress the fundamental, producing octave motion; high-note guard is inherited, not a universal antialias guarantee. Clocks are independent and free-running, not DAW synchronized. Parameter queues retain sample-offset step semantics; simultaneous edits are applied in ascending parameter ID order before note events and clocks. No new SDK dependency, class IDs, shared workflows or manifests.

Example: pitch clock 2 Hz; timbre clock 3.2 Hz; timbre bank [0,.85,.3,1]. HOLD timbre at 1s, edit slot 3 at 1.5s, HOLD pitch at 2s, edit timbre slot 1 at 2.5s, release timbre at 3s and pitch at 4s. Render original MIDI pitches 48 and 55 at velocities .8 and .7, release at 5s. Neutral A/B uses identical timing and all-zero timbre bank. Reproduce with `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release`, `cmake --build build --config Release`, `ctest --test-dir build -C Release --output-on-failure`, and `winters_integrated_demo neutral.wav neutral` / `winters_integrated_demo expressive.wav expressive` (Windows executable under Release). Copy the complete qualified MHACThreeWinters.vst3 directory into the standard VST3 directory and rescan. Do not treat source ZIP as plugin binary.

Native GCC 14.2 Release warnings-as-errors CTest 5/5, new integrated test ASan/UBSan PASS, 28,672 exact migrated legacy frames at seven rates; independent clock/edge semantics, nonfinite control rejection, state truncation rejection, bounded output and release silence. Two 6s 48kHz native stereo WAVs reproduced byte-identically; both peak 0.112487793 FS; RMS neutral 0.046093571, expressive 0.045227569; both silent after 5.05s. These are same-agent engineering tests, not listening or human evidence. Previous head 057a07ee2ed2bd11fc3d400b13e8ef1a4c5b40ed Windows run 45700976326 passed four native suites and 47 official validator tests; adapter there is still 0.1.1. New 0.2.0 Windows SDK compile, validator, DAW, independent review and concurrent state access still outstanding. Local SDK checkout DNS blocked; official tag freshly resolved to locked 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; retain exact seven gitlinks and license packaging. No substitution.
