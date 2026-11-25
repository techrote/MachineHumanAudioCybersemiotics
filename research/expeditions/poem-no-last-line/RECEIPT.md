# Native audio qualification

Executed the original standard-library Python renderer on 25 November 2026. Five 6-second WAVs: 16 kHz, signed 16-bit, 96,000 frames each. Carrier mono, four offset demonstrations stereo. A's 880 Hz marker is left, B's 1320 Hz marker is right; each channel includes the same carrier. No claim that the whole mixes are invariant. Exact subtraction of each marker recovers the same carrier. Bounds, header/payload readback, deterministic re-render, and distinct-file checks passed. No listening trial. WAVs generated on demand with python render.py; no binary files in repo.

SHA-256 of executed outputs:

carrier.wav e376800765b2a1024ac6a6ab9e444cf0196607d9afdd1a966a3c698685e46bca
offset-0.wav 7a6f37c8b6d0ecb6019daf2bbd476f54bd27fa5bbcab74e11bf72294a5eb27e9
offset-1.wav 55a2707f1b935d81c140b63786b3126ff790722e3e8025e105509f609e6c2d2f
offset-2.wav 8d0ac1c42a175a9970d0f5ca26ced4e1ca6b8461d326a237d9976ac0ade53ba2
offset-3.wav eb9406e7d3d437954b0083339fd3e409a6dc3a9e71b4ddaefee8a059cacb919e

The mathematical oracle is separately qualified in the JavaScript execution environment, not by this audio receipt. No full CI or human review asserted. Reproduction hashes refer to this run, not guaranteed bitwise portability of platform math libraries.
