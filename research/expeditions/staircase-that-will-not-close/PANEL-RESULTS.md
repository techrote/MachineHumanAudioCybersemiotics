# Executed same-panel and audio receipt

2026-11-23: the exact function definitions of panel_and_audio.js executed in a JavaScript runtime. The PCM byte arrays were actually constructed in memory; the optional Node filesystem adapter was not run. FNV-1a is a noncryptographic regression checksum, not a provenance/security hash. Every case is synthetic.

```json
{
  "panels": {
    "count": 17550,
    "cycles": 6,
    "maxDebt": 210,
    "maxDebtNoCycle": 204,
    "maxDebtCycle": 6,
    "zeroDebt": 1068,
    "histogram": {
      "0": {
        "acyclic": 1068,
        "cyclic": 0
      },
      "8": {
        "acyclic": 6912,
        "cyclic": 0
      },
      "12": {
        "acyclic": 2400,
        "cyclic": 0
      },
      "16": {
        "acyclic": 5040,
        "cyclic": 0
      },
      "18": {
        "acyclic": 1920,
        "cyclic": 0
      },
      "24": {
        "acyclic": 204,
        "cyclic": 6
      }
    },
    "unit": "1/48 of normalized margin"
  },
  "instruments": {
    "rotations": {
      "left": [
        400,
        440,
        480,
        520,
        560
      ],
      "right": [
        400,
        400,
        400,
        400,
        400
      ],
      "bytes": 64044,
      "fnv1a32": "f7f8e9de"
    },
    "unanimous": {
      "left": [
        400,
        320,
        400,
        480,
        560
      ],
      "right": [
        400,
        280,
        320,
        360,
        400
      ],
      "bytes": 64044,
      "fnv1a32": "d50677ab"
    }
  }
}
```
