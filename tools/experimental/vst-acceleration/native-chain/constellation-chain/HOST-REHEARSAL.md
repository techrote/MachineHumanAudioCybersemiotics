# ACCEL-048 — pinned Windows host performance rehearsal

Refs #632. Creative performance chain follow-up to ACCEL-047, not independent distribution qualification. Uses only original artifact IDs 15249403545, 15251347207 and 15248002499 (no source substitutions). Outer and PE digests, nested CRC, build source, SDK 3.8.0 root/seven gitlinks and audio class CID/version checked before use. The Bank archive has top-level module version 0.2.0 while both classes report 0.3.0; retain the finding and do not silently rewrite the package. This is a diagnostic exception for an exact pinned audition, not release approval.

Run on Windows x64 with Python 3.12, pedalboard==0.9.23 and numpy==2.3.5:

    python constellation_host.py --orbit orbit.zip --bank bank.zip --shuttle shuttle.zip --out fresh-output

Provide original outer Actions ZIPs, not their inner ZIPs. Add --preflight-only to inspect without loading. Output must not already exist. Receipt distinguishes preflight-only, fail and pass. Host uses 7-bit MIDI velocities (102/127 and 89/127) and boundary-separated parameter calls with reset=False, not direct SDK sample-offset queue qualification. Full matrix is five modes, 44.1/48/96 kHz, 257/1024 buffer sizes; checks complete state readback, finite bounds, release, persistent versus full erasure, stereo stagger contrast and stage partition tolerance. At 48 kHz WAVs use half-gain export. Actual host behaviour remains unqualified until receipt passes. A failed or truncated case is not PASS.

Linux execution: exact three original downloaded archives passed preflight, native CMake CTest 1/1 repeated. Windows PE load attempted locally and failed with unsupported plugin format; no Windows execution claimed. A pure segmentation mock exercised the one-sample trigger and preset parser rejected truncated/bad magic examples. Preserve previous individual artifact identities and all negative receipts. No desktop DAW or listening claim.
