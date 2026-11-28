# Palimpsest Shuttle VST3 0.1.0 candidate — ACCEL-040

Refs #632. Draft/HOLD; creative exaptation, not research evidence. Parent a832d89601154c404aa1570244d5d790ab8e1243.
Adapter derived from acceleration-owned Trace Bell (same pinned parent); no third-party source vendored.
Stereo float32, immediate dry path (zero reported latency), conservative 30-second tail,
PS01 13-byte component state, IDs 0 Mix, 1 Reverse, 2 Feedback, 3 Cross, 4 Bypass.
Four controls quantized to 1001 positions; bypass threshold 0.5.
No custom editor; host generic parameters. Restore at block boundary using existing
lock-free audio-side state bridge; lifecycle reset separate from start/stop.
Processor CID 58F3C28ABA5142D1AF75DF83173B962E; controller 7D191A63804C4BF0A02BFE689B7D1C24.

Build from the sibling Trace Bell vst3 CMake project with exact clean SDK
v3.8.0_build_66, root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and seven pinned
gitlinks. Reuses the same build tree and validator; no extra job or checkout.
Build target MHACPalimpsestShuttle, shuttle_sdk_probe, shuttle_control_test, shuttle_regression.
Run official validator and direct SDK probe against the bundle, then
shuttle_host.py --module <inner module> --out <directory>.
After actual qualified delivery, copy the entire .vst3 directory to
C:/Program Files/Common Files/VST3 and rescan in the DAW; audition at attenuated gain.
Five presets and five host-rendered WAVs planned.

Local GCC 14.2 Release CMake/CTest 1/1 and Clang 17 ASan/UBSan native DSP
661484 checks PASS each. New mapping test GCC optimized and Clang ASan/UBSan
4027 mapping/state checks PASS each. Original DSP Git blob
5995cd5e092cc740b55c4592d6891f961edd881d matches the recovered archive.
Mapping/test blobs 56e9dc8690da8074e5a52703bec23b0f8306fca3 and
f0f1d1a112416b76144a1ca1fb5618e6ccc71c62. Local SDK git DNS unavailable;
actual adapter compilation, validator, direct SDK concurrency/automation, host render
and binary packaging remain CI gates. No subjective listening or independent review.

## ACCEL-041 — rate admission recovery (2026-11-27)

Parent fa3ae1695e3a6f5d55349bb92f092cee0b3ad7e5; Windows run 46019178132 job 140574040845 compiled the module and native tests, then failed the explicit validator error gate despite a 47/0 summary. Five setup failures at 384000, 1234.568, 12345.678, 123456.780, 1234567.800 Hz. Diagnostic artifact 15206679605 retained. No qualified 0.1.0 binary from that run. Earlier Trace Bell step passed.

DesktopShuttle now reserves 160000 grain samples (2.56 MB per instance on tested Linux ABI), uses a finite 1000–2000000 Hz double-valued setup contract, and computes the nearest even length to 80 ms (ties upward). Existing integer prepare and small embedded capacities retain their prior limits. No change to PS01, parameter/class IDs, sample processing recurrence, or feedback ceiling. Heap-resident processor and heap-resident SDK oracle avoid Windows stack expansion. Unsupported rates rejected before base setup/state mutation. No sample-rate clamping, bypass simulation, or validator gate relaxation. Existing standard-rate audio is unchanged in tested fixtures.

GCC 14.2 -std=c++17 -O2 -Wall -Wextra -Werror and Clang 17 -O1 -g -fsanitize=address,undefined: new native rate test 4,103,382 checks PASS each; independent original-vs-expanded engine comparison 131,872 exact stereo frames per compiler. Rate fixtures cover all five failed rates and boundaries; forward/reverse oracle, invalid-rate transactional rejection, capacity and legacy path. Tested source blobs 64d0005b306b1830f811529cc27eda3a9f6e29ff and a9397a3e82adbebe0297866df178c482fa6b24f9. SDK probe now additionally exercises 10 paired-block extended-rate automation cases (including wet output at high rates), rejects invalid setup, and checks rate-dependent tail. These adapter and host changes remain unexecuted locally; SDK checkout failed DNS. Exact SDK root and seven recursive checkout revisions rechecked in prior hosted logs; no dependency changes. Existing workflow and strict validator gate unchanged. New exact-head Windows build, validator, SDK probe, Pedalboard host and package remain required. No independent review or listening claim.

## ACCEL-043 — complete SDK receipt gate (2026-11-27)

The recovered Windows run 46030439105 (head ca1ed99b0c8632a2ed977289fa9d49929273be70) showed all 16 direct SDK automation cases in job 140612568815, but the retained Shuttle artifact 15213579147 contains only the six standard-rate rows and a different state-stress receipt. Preserve the original package and the failed earlier qualification; do not infer the extended result from the old archive alone. This is an evidence/packaging defect, not a newly demonstrated audio regression.

The probe now prints exact three-decimal fixture rates, with full precision for error. `shuttle_receipt.py` requires the complete ordered 16-case matrix, exact frame counts, finite nonnegative error below the existing 2e-5 bound, ten-case extended marker, 20,000-write state stress with positive reads and at least 256 blocks, and the original six-case marker. The existing dedicated Windows job self-tests the checker, rejects stale staging, validates the live transcript, binds it by SHA-256 across host rendering/packaging and checks its exact bytes and archive CRC before upload. No new job, DSP change, SDK pin change, Trace Bell change or gate relaxation. Local Python self-test: 3 positive, 17 negative; historical six-case receipt rejected. Fresh Windows SDK execution and package inspection still required. Existing qualified candidate is retained.

## ACCEL-044 — isolate SDK notices from plugin evidence (2026-11-27)

Exact predecessor 7def30b39d2fed240155005e945bec0f5c91622a failed Windows run 46067860106, job 140737438122, at the new transcript hash gate after all 16 SDK cases and 30 host renders passed. Mergedown independently found the Windows case-insensitive SDK-* wildcard copied Trace Bell's sdk-probe.txt over Shuttle's validated transcript (issue #632 comment 7228889719). Preserve both negative evidence artifacts 15232021185 and 15232116079. Replace the wildcard and three copy commands with a case-sensitive provenance allowlist, known SDK part/notice families only, required root license/gitlinks/build-source files, preflight case-fold collision rejection and exclusive creation. No changes to native DSP, plugin IDs, dependency pins, Trace Bell or the existing hash/ZIP/validator gates. The same Windows job runs portable copy regressions before build. Windows rerun and actual archive inspection are required; do not claim a fresh qualified binary yet.
