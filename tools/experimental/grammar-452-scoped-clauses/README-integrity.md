# Matched-budget integrity framing — Grammars Run 003

Refs #452 / Draft PR #453. Synthetic-only extension of recursive.cjs at 4bed9abcb2343129c265cbfeb7d5cd0341eeaf6b; accepted main 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity, experiments, human gates, foundation, protocol and amendment indexes, issue/comments, prior grammar implementation and Interaction #457 README at 85ca2185a0481512c903b08d55c4e5dd6ed738e9 (symbolic receipt metadata, not acoustic serialization). No concurrent source imported. One GPT-6.2 agent, no subagents; no human evidence, novelty, operational safety or production claim. No canonical record edits.

## Contract

Both modes transmit exactly eight 80 ms slots (640 ms), same 17-tone alphabet (400–2000 Hz in 100 Hz steps), same envelope, amplitude and bandwidth; no silent padding. All 2304 ordered trees of 1–4 nodes are legal. Closed comparator: one length symbol (length minus one), closed AST, END padding to seven body slots. Protected: length, compact prefix AST, END padding to five body slots, two GF(17) check tones. The check frame satisfies sum(x)=sum((i+1)x_i)=0 mod 17. Distinct columns (1,i+1) imply no nonzero codeword of weight <=2. Thus any one or two substitutions with no erasures is detected; any two known erasures can be corrected. Receiver does not correct unknown substitutions. More than two erasures refuse. Unknown-position deletion removes a slot and fails length in both modes; no resynchronization is asserted. Padding and length are checked after reconstruction. Syntax is not truth or authentication.

The comparator deliberately spends its redundancy on explicit closure and padding; it is not a claim of optimality of either encoding. Both have same transmitted duration, alphabet, active duty and nominal amplitude. Actual clean PCM sample-energy extrema are recorded for the example set and four phases; small rounding/envelope differences remain, not calibrated SPL or human loudness. Receiver requires exact frame/slot alignment; sine/cosine template scores, no noise or drift tests. Symbolic tests are exhaustive over declared corruption positions, not independent statistical samples or estimated channel probabilities.

## Results

    {
      "metrics": {
        "closed": {
          "clean": 2304,
          "deletion": {
            "correct": 0,
            "wrong": 0,
            "refused": 18432
          },
          "singleSub": {
            "correct": 0,
            "wrong": 40976,
            "refused": 253936
          },
          "singleErase": {
            "correct": 0,
            "wrong": 0,
            "refused": 18432
          },
          "doubleErase": {
            "correct": 0,
            "wrong": 0,
            "refused": 64512
          }
        },
        "protected": {
          "clean": 2304,
          "deletion": {
            "correct": 0,
            "wrong": 0,
            "refused": 18432
          },
          "singleSub": {
            "correct": 0,
            "wrong": 0,
            "refused": 294912
          },
          "singleErase": {
            "correct": 18432,
            "wrong": 0,
            "refused": 0
          },
          "doubleErase": {
            "correct": 64512,
            "wrong": 0,
            "refused": 0
          }
        }
      },
      "distance": {
        "closed": {
          "hist": [
            0,
            20488,
            137832,
            462032,
            857488,
            911792,
            263424,
            0,
            0
          ],
          "closest": {
            "d": 1,
            "i": 0,
            "j": 1
          }
        },
        "protected": {
          "hist": [
            0,
            0,
            0,
            45166,
            252712,
            830500,
            1161640,
            363038,
            0
          ],
          "closest": {
            "d": 3,
            "i": 0,
            "j": 1
          }
        }
      },
      "pcm": {
        "cases": 96,
        "energy": {
          "closed": {
            "min": 57190941211,
            "max": 57207064518
          },
          "protected": {
            "min": 57189149432,
            "max": 57210974587
          }
        },
        "peak": 4096
      },
      "assertions": 502472
    }

The pair census independently verifies minimum distance on the finite catalogue. A protected frame at distance three from another legal frame can be transformed by two substitutions plus one known erasure into a falsely accepted meaning; retained in qualification. No claim of robustness beyond stipulated budget. The fixed length makes unknown deletion detection trivial and is a framing assumption, not a superiority result. Explicit END can still be useful for variable length syntax and segmentation; this experiment deliberately fixes the frame budget.

## Reproduce

Node 18+ from this directory: `node integrity.cjs output-integrity`. Generates receipt, 13 original PCM16 WAV specimens and SHA-256 manifest. Exported functions encode, decode, render, receive, qualify, vocab, synd; qualification JSON contains exact conditions, pair histograms, example frames and corruption witnesses. V8 core executed twice with identical receipts. Native CLI/filesystem not executed (container cannot resolve github.com), actual listening, synchronization, drift/noise, independent review and final-head CI pending. Keep digital playback low; no physical calibration. Next: frame synchronization with explicit acquisition/false-alarm tests, then reference binding to independently faulted dialogue metadata. Retain Draft/HOLD.
