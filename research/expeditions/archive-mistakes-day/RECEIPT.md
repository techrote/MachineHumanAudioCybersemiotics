# Execution receipt — 2026-11-25

The original `laboratory` function was executed in the JavaScript tool isolate before committing its exact function body. This is not a native Node process or repository-wide CI run. Reproduce with `node laboratory.cjs`. No human data, real recording or physical experiment. Agent: ChatGPT GPT-6.2, sole author and checker; no independent review.

```json
{
  "episodes": [
    [
      "hum",
      12
    ],
    [
      "tap",
      1
    ],
    [
      "gap",
      1
    ],
    [
      "tap",
      1
    ],
    [
      "gap",
      1
    ],
    [
      "tap",
      1
    ],
    [
      "gap",
      1
    ],
    [
      "chime",
      2
    ]
  ],
  "time": {
    "N": 20,
    "k": 3,
    "total": 1140,
    "inclusion": {
      "hum": 1084,
      "tap": 460,
      "gap": 460,
      "chime": 324
    },
    "counts": {
      "hum": 2052,
      "tap": 513,
      "gap": 513,
      "chime": 342
    }
  },
  "episode": {
    "N": 8,
    "k": 3,
    "total": 56,
    "inclusion": {
      "hum": 21,
      "tap": 46,
      "gap": 46,
      "chime": 21
    },
    "counts": {
      "hum": 21,
      "tap": 63,
      "gap": 63,
      "chime": 21
    }
  },
  "category": {
    "N": 4,
    "k": 3,
    "total": 4,
    "inclusion": {
      "hum": 3,
      "tap": 3,
      "gap": 3,
      "chime": 3
    },
    "counts": {
      "hum": 3,
      "tap": 3,
      "gap": 3,
      "chime": 3
    }
  },
  "refinements": 4096,
  "humEpisodeInclusionRange": [
    0.3333333333333333,
    0.9638802889576883
  ],
  "assertions": 45097
}
```

## Subsequent native confirmation

Reconstructed the exact committed source from GitHub readback; `git hash-object laboratory.cjs` returned `8678bcfb1796bd08704ee944580e413bccefcf40`, matching the committed blob. Native Node v22.16.0 executed `node laboratory.cjs` successfully (exit 0), reproducing every numerical field above, including 45,097 assertions, 4,096 refinements and both extremal probabilities. This qualifies the finite oracle only. Repository-wide checks and independent review remain separate.
