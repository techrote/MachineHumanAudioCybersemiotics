# Exact synthetic execution receipt

Executed the same function definitions in a JavaScript runtime on 2026-11-23 (no Node-specific APIs). All 4,096 graph cases verified by separate Bellman–Ford feasibility search, plus controls. Output below; run `node oracle.js` to reproduce. No local Node invocation or repository CI claimed by this receipt.

```json
{
  "census": {
    "all": {
      "cases": 4096,
      "positiveDebt": 3056,
      "ordinalCycle": 488,
      "positiveWithoutOrdinalCycle": 2568,
      "triangleUnderstates": 576,
      "triangleZeroButDebt": 186,
      "debtHistogram": {
        "0/1": 1040,
        "1/3": 1128,
        "2/3": 888,
        "1/1": 488,
        "1/4": 96,
        "1/2": 240,
        "3/4": 216
      }
    },
    "complete": {
      "cases": 729,
      "positiveDebt": 714,
      "ordinalCycle": 186,
      "positiveWithoutOrdinalCycle": 528,
      "triangleUnderstates": 162,
      "triangleZeroButDebt": 0,
      "debtHistogram": {
        "1/2": 60,
        "1/3": 144,
        "2/3": 228,
        "1/1": 186,
        "3/4": 96,
        "0/1": 15
      }
    },
    "checks": 4096
  },
  "controls": {
    "square": {
      "num": 1,
      "den": 1,
      "potential": [
        0,
        0,
        0,
        0
      ],
      "witness": [
        0,
        1,
        2,
        3,
        0
      ],
      "witnessSum": 4,
      "witnessLength": 4,
      "triangleNum": 0,
      "triangleDen": 1,
      "ordinalCycle": true
    },
    "tree": {
      "num": 0,
      "den": 1,
      "potential": [
        2,
        7,
        0,
        2
      ],
      "witness": [],
      "witnessSum": 0,
      "witnessLength": 0,
      "triangleNum": 0,
      "triangleDen": 1,
      "ordinalCycle": false
    },
    "disconnected": {
      "num": 2,
      "den": 1,
      "potential": [
        0,
        0,
        0,
        0,
        97
      ],
      "witness": [
        0,
        1,
        2,
        0
      ],
      "witnessSum": 6,
      "witnessLength": 3,
      "triangleNum": 6,
      "triangleDen": 3,
      "ordinalCycle": true
    },
    "exact": {
      "num": 0,
      "den": 1,
      "potential": [
        0,
        2,
        5
      ],
      "witness": [],
      "witnessSum": 0,
      "witnessLength": 0,
      "triangleNum": 0,
      "triangleDen": 1,
      "ordinalCycle": false
    },
    "examples": [
      {
        "n": 3,
        "unanimous": {
          "num": 1,
          "den": 1,
          "potential": [
            4,
            2,
            0
          ],
          "witness": [
            0,
            2,
            1,
            0
          ],
          "witnessSum": 3,
          "witnessLength": 3,
          "triangleNum": 3,
          "triangleDen": 3,
          "ordinalCycle": false
        },
        "rotations": {
          "num": 1,
          "den": 1,
          "potential": [
            0,
            0,
            0
          ],
          "witness": [
            0,
            2,
            1,
            0
          ],
          "witnessSum": 3,
          "witnessLength": 3,
          "triangleNum": 3,
          "triangleDen": 3,
          "ordinalCycle": true
        }
      },
      {
        "n": 4,
        "unanimous": {
          "num": 2,
          "den": 1,
          "potential": [
            6,
            4,
            2,
            0
          ],
          "witness": [
            0,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 8,
          "witnessLength": 4,
          "triangleNum": 4,
          "triangleDen": 3,
          "ordinalCycle": false
        },
        "rotations": {
          "num": 2,
          "den": 1,
          "potential": [
            0,
            0,
            0,
            0
          ],
          "witness": [
            0,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 8,
          "witnessLength": 4,
          "triangleNum": 4,
          "triangleDen": 3,
          "ordinalCycle": true
        }
      },
      {
        "n": 5,
        "unanimous": {
          "num": 3,
          "den": 1,
          "potential": [
            8,
            6,
            4,
            2,
            0
          ],
          "witness": [
            0,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 15,
          "witnessLength": 5,
          "triangleNum": 5,
          "triangleDen": 3,
          "ordinalCycle": false
        },
        "rotations": {
          "num": 3,
          "den": 1,
          "potential": [
            0,
            0,
            0,
            0,
            0
          ],
          "witness": [
            0,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 15,
          "witnessLength": 5,
          "triangleNum": 5,
          "triangleDen": 3,
          "ordinalCycle": true
        }
      },
      {
        "n": 6,
        "unanimous": {
          "num": 4,
          "den": 1,
          "potential": [
            10,
            8,
            6,
            4,
            2,
            0
          ],
          "witness": [
            0,
            5,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 24,
          "witnessLength": 6,
          "triangleNum": 6,
          "triangleDen": 3,
          "ordinalCycle": false
        },
        "rotations": {
          "num": 4,
          "den": 1,
          "potential": [
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "witness": [
            0,
            5,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 24,
          "witnessLength": 6,
          "triangleNum": 6,
          "triangleDen": 3,
          "ordinalCycle": true
        }
      },
      {
        "n": 7,
        "unanimous": {
          "num": 5,
          "den": 1,
          "potential": [
            12,
            10,
            8,
            6,
            4,
            2,
            0
          ],
          "witness": [
            0,
            6,
            5,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 35,
          "witnessLength": 7,
          "triangleNum": 7,
          "triangleDen": 3,
          "ordinalCycle": false
        },
        "rotations": {
          "num": 5,
          "den": 1,
          "potential": [
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "witness": [
            0,
            6,
            5,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 35,
          "witnessLength": 7,
          "triangleNum": 7,
          "triangleDen": 3,
          "ordinalCycle": true
        }
      },
      {
        "n": 8,
        "unanimous": {
          "num": 6,
          "den": 1,
          "potential": [
            14,
            12,
            10,
            8,
            6,
            4,
            2,
            0
          ],
          "witness": [
            0,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 48,
          "witnessLength": 8,
          "triangleNum": 8,
          "triangleDen": 3,
          "ordinalCycle": false
        },
        "rotations": {
          "num": 6,
          "den": 1,
          "potential": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
          ],
          "witness": [
            0,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
            0
          ],
          "witnessSum": 48,
          "witnessLength": 8,
          "triangleNum": 8,
          "triangleDen": 3,
          "ordinalCycle": true
        }
      }
    ]
  }
}
```
