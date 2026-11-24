# Execution receipt — 2026-11-24

Same-agent local Python execution, two independent output directories. Both runs completed without assertion failure. Byte comparisons matched every WAV and the JSON receipt. All WAVs: mono PCM16, 16000 Hz, 192000 samples (12 seconds). The last 96000 samples match across all four arms. Peak bounds and sample readback checked.

Renderer Git blob SHA-1 from locally executed bytes: 163b3dce210b390357188e65d0afa37b3b914f8b.

| WAV | SHA-256 |
| --- | --- |
| room.wav | 0c608bbdcf31db9e50748161b0536b50f620f11566cc602badfa62c4dcb38ecb |
| in-phase.wav | da4b66a8932e4b316e44b7d377672e9de2ee6ad1b836d97f6d1865068900d2e8 |
| disjoint.wav | f3e03f9513adcdd3eed1e06d403a8fd4f2f48c46a41b17b6c8ef6368d013fc54 |
| opposite-phase.wav | 3d77fecec3273039eb52294ed534352196c13e1440cb633bc61106a3c9a97729 |

Regenerate with render.py; hashes characterize the executed environment, not a cross-platform libm identity guarantee. No participant responses, no physical speaker output measured, no auditory masking threshold, no safety claim. Repository-wide CI is separately qualified on the final PR head, not inferred from this run.
