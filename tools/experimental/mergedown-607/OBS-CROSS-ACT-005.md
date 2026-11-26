# OBS-CROSS-ACT-005 — independent qualification (2026-11-26)

Refs #607, #442, #443, #452, #453. AI-assisted consolidation, no independent human review. Source and evidence stay upstream; this batch adds only the separate oracle and ledger. Main observed at 495a98ca12bae467a507031f04931aa4254b1866. The user's explicit no-merge instruction overrides the normal landing runbook. No protocol, canonical records, rights or human gates changed.

## Reproduce offline

From a checkout containing the frozen Git object  ed648880b0588b2852a0b691a8f603a2a0a49a13, extract the original standalone Python script without text conversion (Git Bash, Linux/macOS):

```sh
git show ed648880b0588b2852a0b691a8f603a2a0a49a13:tools/experimental/observatory-442-receipt-inspector/cross-act-audit.py > cross-act-audit.py
git hash-object cross-act-audit.py
python cross-act-audit.py audit-output
python tools/experimental/mergedown-607/check_cross_act.py > independent.json
```

Expected source Git blob 6788b2a9d3df49eea24737062d414a19e95bb29b. On Windows use Git Bash, or a byte-preserving checkout of the exact commit (avoid PowerShell text redirection or CRLF conversions). Upstream uses standard-library Python only; independent harness tested with Python 3.13.5 and NumPy 2.3.5. Do not use Python -O (assertions enabled). Use a new output directory. Open audit-output/index.html manually; audio is opt-in, start at low hardware volume. The gallery contains three WAV examples, receipt and manifest. This is a reproducible gallery recipe, not a delivered Windows-qualified archive. Generated files not committed; expected hashes in ledger.

## Qualification

Original source transferred from connector, exact Git blob verified; two native executions, six files identical, manifest 5/5, three 16kHz mono PCM16 640ms WAV format/hash/peak checks passed. Independent oracle constructs the complete polynomial family by coefficient enumeration rather than interpolation and directly enumerates 215,040,000 actual symbol replacements rather than grouping unchanged triples. Both 4×4 matrices match native upstream exactly. The 70 individual surviving-position masks each contain 3,072,000 faults; incorrect acceptance varies from 1,699,610 (positions 2,3,4,6) to 2,627,172 (0,1,4,5). Same-address incorrect acceptance ranges from 906 (0,2,4,5) to 968,708 (0,1,4,5). Positions zero-based. This suggests unequal protection evaluation must distinguish mask distributions. Perfect address/class filtering is side information, not free. Counts are finite enumeration, not physical error probabilities.

The original grammar encoder and one decoder witness reproduced in connector V8 only, not native Node DSP. Independent Python oracle repeated byte-identically (SHA-256 89d68f2786591c5eb3bd4e694549b1e6a09267b828cc5f2a35c57ee5a62bde7e). Upstream receipt SHA-256 5914839f5c15b24f699be97a177bcf6269b74743c7c82a96b2cfb72ab98ea118. WAV peak 2048/32768 digital full scale, no RMS or SPL match claim.

## Disposition

HOLD overall. Native numerical and filesystem scope passes; Chromium file navigation timed out (exit 124, missing D-Bus sockets, zero DOM bytes), no physical audition, Windows or external review. Git DNS still fails (exit 128), full native selective/legacy wrapper remains unresolved. All frozen prior source pins preserved; later Measurement delta is five additive files, not automatically included. No duplication of source or generated receipts; provenance and upstream license status preserved (no new rights granted). Next complete native legacy/selective dependency transfer, then owner-ready package; no merge authorization inferred.
