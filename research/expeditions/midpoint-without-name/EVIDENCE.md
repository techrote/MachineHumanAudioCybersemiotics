# Execution receipt — 2026-11-24

Issue #254; branch mhac-254/midpoint-without-name, base 495a98ca12bae467a507031f04931aa4254b1866. GPT-6.2 self-execution, not independent human review. Local Python 3.13.5. Source and tests uploaded and fetched back: Git blob IDs match local SHA-1 Git blob computations:

- midpoint_lab.py: dbbb7de7affa6a72d8a0d81db8232cf8374468f3
- test_midpoint_lab.py: 0118a24e1827d653d2e4c2a7516eb03b6642e06a
- tests/test_expedition_midpoint_254.py: 82c3bec610ca0cd4524c445e4191b6150ad9b32e

Actual runs: five test methods passed (constructive sharpness, invalid inputs, affine/rank controls, grid census, audio). The constructive test evaluates 3 slope pairs × 2 anchor sets × 65 target values × 3 candidate locations = 1,170 witnesses, with interpolation and all segment slopes checked. An isolated temporary tree containing the exact bridge and an additional dummy test passed six tests via unittest discover -s tests. This is not a run of the full repository suite.

Grid: 65,536 increment vectors inspected, 3,823 normalized charts, 961 centered-anchor charts and 440 displaced-anchor charts. All 51 target/anchor combinations contained in continuous intervals, 39 attained both bounds. At t=1/2: no intermediate anchor [1/4,3/4]; centered anchor [1/2,1/2]; anchor (1/2,3/8) [9/16,3/4]. Discrete failure to reach both bounds in 12 settings is retained in generated results.json, not silently discarded.

A separate local verification used four-fold polynomial coefficient convolution (rather than enumerating 8-tuples) and multiplied paired coefficients for the anchor filters. Counts matched 3823,961,440. It also checked maximum-width formula at 2,970 target/segment combinations across 90 admissible segments, including equality at each segment's ordinate midpoint. Those checks reuse the bounds implementation for comparison; this is a distinct calculation, not a separate author. For reproducibility the core convolution is:

    from collections import Counter
    a=Counter({0:1})
    for _ in range(4):
        b=Counter()
        for x,n in a.items():
            for j in range(1,5): b[x+j]+=n
        a=b
    assert sum(a[s]*a[16-s] for s in a)==3823
    assert a[8]*a[8]==961 and a[6]*a[10]==440

Audio: generated and inspected all 3 original WAVs. Actual 16-bit mono, 16 kHz, 28,800 frames per file. Samples within ±7000, 27 blocks independently inspected for rising zero-crossings consistent with frequencies to within one crossing per 0.2 second block. First and last blocks byte-identical across all 3 files; all complete files distinct.

| File | Frequencies (Hz) | SHA-256 |
|---|---|---|
| identity.wav | 200,300,400,500,600,700,800,900,1000 | 1f081c55a45fd65de1a5ec766fc9f66dc49ebd3b0f81930071271506a81f06ae |
| early.wav | 200,250,300,350,400,550,700,850,1000 | 22ab3613e663f0fe759e92a7c0addfbd7e27ce0bcd1e57b838bbeb5482cd7c7b |
| late.wav | 200,350,500,650,800,850,900,950,1000 | 57acd70160e898a79a8f29fac4f1568712e2c394daea7c592e521143388d152a |

Reproduction: run midpoint_lab.py with output directory, then python -m unittest discover -s research/expeditions/midpoint-without-name -v. The generated binary audio is not committed; the source and hashes suffice to regenerate.

Repository-wide integrity CI not yet observed at time of this receipt. PR and final-head check state to be reported separately; no claim of merge or post-merge acceptance. Human gate: none for synthetic calculations; no human study or source corpus admission authorized.
