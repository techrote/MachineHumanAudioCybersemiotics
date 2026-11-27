# Integration 004 — native process interruption and full corpus (HOLD)

Refs #607 / #512. Supplements README.md without changing the original frozen source pins or the earlier logical-cut evidence. The additional original generator source/test-journal-v42.cjs is archived byte-identically from 3637529f313949d31e55d66d04bb119547c1e29a, blob ddd1cfc16ae87049ff8602fe9a8169edb7a12450. This expands the closure to 25 exact upstream source files; subsequent versions remain excluded.

Native Linux Node 22.16.0: each seed 71/113 produced 14 sessions, 126 upstream assertions, 32 original decoder WAV rescans. Python independently checked 28 WAV SHA-256 hashes, mono PCM16 at 16000 Hz, sample counts, trace slot accounting and complete seed inventory. The locally generated receipt SHA-256 pins are in audit_corpus.py; these are consolidation-side pins, not a comparison with an upstream archived receipt.

Reproduce from this directory:
    SEED=71 node source/test-journal-v42.cjs seed71
    SEED=113 node source/test-journal-v42.cjs seed113
    python -B audit_corpus.py
    node check_process_cut.cjs > process-cut-receipt.json

The latter checker terminates isolated child Node processes with actual SIGKILL at four instrumented filesystem-call boundaries across both seeds. Original runtime modules unchanged. The parent checks actual signal status, local/stage/witness commit values and witness hash prior to recovery, then retries the same authenticated PCM and verifies one retained event. Before stage and after stage retry new; after witness recovers candidate and retries duplicate; after publication recovers current and retries duplicate. Two runs produced identical receipt SHA-256 371db05a28bdf6ada45041dad6c58213f174c865624791edb24394eec9363131.

Instrumentation wraps real fs.openSync/fs.fsyncSync calls in the child only; it does not replace the filesystem or inject a logical exception. This tests process death while the OS and filesystem continue running, not kernel crash, power loss, arbitrary interruption inside a syscall, a real external witness, concurrent writers or physical audition. Prior joint rollback failures remain. The upstream rescan uses the original decoder, not an independent decoder. Native Windows, hosted native CI, actual browser viewing and independent review remain outstanding. No scientific acceptance, no human gates changed.
