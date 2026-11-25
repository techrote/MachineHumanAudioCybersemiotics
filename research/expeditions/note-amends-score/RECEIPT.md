# Execution receipt — 2026-11-25

One ChatGPT agent; no independent reviewer or participant. Synthetic only.

- laboratory.cjs function body executed in JavaScript tool runtime before publication: 3,413 tables, 16,739 start/table combinations, 1,541 trajectory classes, 208,966 passing assertions. Native Node execution not checked.
- render.py executed with Python 3.13.5, standard library only. Local executed file Git blob e13b89168929e526a0e2a200076d030e571512fc matches committed fetch_file blob and contents. Seven original WAVs generated, 16 kHz mono signed PCM16, 64,000 frames each. Repeated render equality, sample bounds, header and payload readback, identical same-start WAVs, distinct intervention WAVs and exactly silent empty audition all passed. Silence is labelled externally; it is not self-interpreting. The recordings are available in the run's downloadable ZIP, not committed; reproduce with python render.py.
- SHA-256 of each WAV:

```
prospective-cycle 8c9da13a0aed257e3d67c1e347667daea0d08d66318e7c2361a0e36a4fd985d0
law-a-start-0 258cad9860c60055b71012cdf7f10bbce44508ad153b7f5c89c4b81b1036b86d
law-b-start-0 258cad9860c60055b71012cdf7f10bbce44508ad153b7f5c89c4b81b1036b86d
law-a-start-2 9a0089542915386d158c5c01d454a95c3ab44b62bc9db36839197d3f67a632f4
law-b-start-2 b92e025e3d9b912c2fda4ec8b4bba44b27b612f36d978d5ab409a4385ce94608
audition-a 29753b302699410018150b67fecabee99d4df45a3bb1cbf4e859a045993dd61f
audition-b-empty f751fd7094be088dc785125e4a1a0222a17c2bd20469aa31728ca5e515ed5809
```

No physical listening trial, human performance, browser qualification, native Node run or full repo validation. No claim of empirical support or mathematical priority. See PR for exact-head CI state. All changes additive under the issue-owned directory.
