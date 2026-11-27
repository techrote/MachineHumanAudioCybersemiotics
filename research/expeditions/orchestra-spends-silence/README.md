# The Orchestra That Spends Its Silence

**2026-11-27 | exploratory humanities/art expedition | Refs #799 | Draft/HOLD.** This is an original conceptual construction and synthetic engineering rehearsal, not a canonical source extraction, empirical result or finding about listeners. AI-assisted research, calculation, writing and rendering by ChatGPT; no independent human review.

## The patron's accountant (fiction)

A patron commissions four electronic musicians to play a single melodic line. The first pays two musicians to play it in unison. The second pays three to play and one to subtract. The third pays two to double the tune and one to undo half the result. The recorder receives the same melody. The accountant announces that each concert involved the same amount of music.

The musicians request a second concert, in which the public is allowed to listen to the individual channels. What had been classified as surplus now becomes the composition. A fourth patron requests that even this second concert remain unperformed: no archive, no performance statistics, no recovered value. This last instruction is deliberately beyond the experiment below.

## Source encounters and their disagreement

- Georges Bataille, *The Notion of Expenditure* (1933), in *Visions of Excess: Selected Writings, 1927–1939*, ed. Allan Stoekl, trans. Stoekl with Carl R. Lovitt and Donald M. Leslie Jr., University of Minnesota Press, 1985, §II, printed pp. 118–120. [Accessible scan](https://cominsitu.wordpress.com/wp-content/uploads/2021/02/visions-of-excess-selected-writings-1927-1939-by-georges-bataille-z-lib.org_-1.pdf). Read the extracted opening of §II and artistic-production passage; visually checked printed pp. 118–119 (PDF zero-based 143–144). Bataille distinguishes consumption required for production from activities whose meaning is constituted through loss, including art. He is not describing signal cancellation or proposing inefficient software. The scan's rights status is unverified; no source pages are redistributed. The original French and full essay were not independently read.
- Lauro Eusébio, *The emergence of expenditure: on Georges Bataille's first economic essay*, Nova Economia, [article](https://www.scielo.br/j/neco/a/s3fJrTY7Xq8x86xbs5Vm6gr/?format=html&ilang=en&lang=en). Abstract, selected passages in introduction and discussion, and conclusion read. Eusébio connects the 1933 essay to Bataille's earlier critique of standardized experience and to his Marxist intellectual setting, challenging a simple consumer-society reading. This complicates the proposed artistic appropriation: expenditure is a historically situated critique, not a generic permission to consume more resources. The article's reconstruction was not independently adjudicated.
- MoMA, Jean Tinguely, [*Homage to New York* exhibition record](https://www.moma.org/calendar/exhibitions/3369), and [*Fragment from Homage to New York*, 1960, object 227.1968](https://www.moma.org/collection/works/81174), gallery labels 2023 and 2019–20. The exhibition record dates the event March 17, 1960; the object label says March 18. MoMA's [photographic record](https://www.moma.org/slideshows/216/2797) supports March 17. Retain the discrepancy rather than treating both dates as corroboration. Read the online labels and captions, not the primary film or engineer's report. The kinetic work was designed to destroy itself rather than maximize durable output. Its remnants became collectible objects nonetheless. Our proposal is software-only; no destructive physical construction is proposed.
 
**Interpretation:** Bataille's critique and Tinguely's practice invite us to ask whether an instrument can have an internally meaningful activity which the principal output does not valorize. But our hidden stems can be auditioned and reused, so they are not genuinely lost. The contradiction is fertile: the engineer retrieves what the artist intended to spend. Do not turn expenditure into a numerical measure of aesthetic worth.

## Exact construction: a fixed-sum mixer

Let n >= 2, q >= 1 be integers. Each signed gain x_i belongs to [-q,q] intersect the integers, and the shared bus coefficient is s = sum x_i. Define A = sum x_i^2, a dimensionless gain-activity index. This is not joules, CPU time, acoustic intensity or an estimate of musical value.

Write s = n*a+r with 0 <= r < n. The minimum A is (n-r)*a^2 + r*(a+1)^2. If two coefficients differ by at least 2, transferring one unit from the larger to the smaller strictly decreases A and stays within bounds. Repeating produces coefficients differing by at most 1. They are admissible for |s| <= n*q.

Write s+n*q = 2*q*k+t with 0 <= t < 2*q. The maximum is n*q^2 when t=0, otherwise (n-1)*q^2+(t-q)^2. If two coefficients are strictly interior, move one unit from the smaller toward -q and one from the larger toward +q. This strictly increases A, preserves s and is feasible until one reaches a boundary. Thus a maximum has at most one interior coordinate. The remainder t uniquely determines that coordinate.

A must have the same parity as s since x_i^2-x_i is even, but that necessary condition is insufficient. For n=2, q=2, s=0, the possible activities are {0,2,8}; the parity-compatible values 4 and 6 are impossible. A control that offers every integer between its extrema is therefore not an exact realizability inspector.

For four voices, q=2, s=2, consider:
 
| Realization | Signed gains | A |
| --- | --- | ---: |
| Frugal | 0,0,1,1 | 2 |
| Ornate | -1,1,1,1 | 4 |
| Extravagant | -2,0,2,2 | 12 |

The extravagant realization uses six times the summed squared stem amplitude of the frugal one on the same carrier, but its output is exactly unchanged. This is coherent signed mixing, not independent random sources. General real-valued identity: sum x_i^2 = s^2/n + sum (x_i-s/n)^2. The second term is the squared norm of a nullspace component. It vanishes at equal real-valued allocation, which is not always admissible on the integer grid. This decomposition is standard elementary geometry; no priority is claimed.

## Original sound studies and executed checks

Run `python laboratory.py OUTPUT_DIRECTORY` (Python 3.11+ standard library). The census enumerates all coefficient vectors for n=2..6 and q=1..3, groups by fixed sum, and compares actual extrema with the analytical formula.

Native execution, twice with identical receipts: 157,863 vectors, 255 sum classes, 354 missing parity-compatible activity values summed across those classes. All extrema and parity checks passed. The explicit two-voice hole witness passed. These are finite census counts, not sampling estimates.

The renderer makes a four-second, sixteen-note original phrase using integer-rounded sinusoidal tiles with smooth envelopes. Each realization cyclically rotates its gain assignments on successive notes, creating four independently inspectable stem sequences. Each note has the same master coefficient of two. Nine WAV files: three mono masters, three four-channel stem files, three stereo monitors (left=master; right=stem 1). All are 16 kHz signed 16-bit PCM, 64,000 frames. Masters are byte-identical: SHA-256 63da74bee1b2232b5faf0dde0e6c11ccea04fe5620dd31cdf7a3de74a3c554d9. The three monitors have distinct hashes. Full PCM readback, bounds, metadata, fixed-sum identity and the sixfold activity ratio are checked by the script; two runs yielded identical receipts. This is offline synthesis; cross-runtime bit identity and physical reproduction are not established.

Performance score: first listen to the three masters without labels. Next use the stereo monitors to hear the same principal line and three different subordinate counterpoints. Finally route the four stems independently in a digital mixer, attenuating to safe levels and avoiding physical phase-cancellation claims. Do not assume the four-channel file is rendered with correct speaker mapping by a player. No human listening experiment occurred.

## Second rabbit hole: the right not to recover

An orchestra may contain a compositional activity that exists only in a nullspace. It can be transformed without altering its master. A player selects a protected bus and edits another degree of freedom. This resembles contrapuntal composition with a constraint, not a proof that an inaudible signal is art. A more provocative performance prohibits re-audition of the discarded component; its unrecorded existence cannot later be reconstructed from the master. This is an artistic option, not a permission to destroy required operational evidence.

A digital nullspace is not acoustic disappearance: spatial speaker separation, phase mismatch, clipping, nonlinear processors and different resampling can expose supposedly cancelled material. The same file also says nothing about whether a gain vector was actually evaluated. A computational optimizer could remove the entire nullspace calculation. This is one reason the activity index cannot stand in for actual energy consumption.

## Instrument and research exaptation

- **Expenditure Organ (VSTi):** protected principal bus, integer or continuous nullspace controls, morph among admissible coefficient allocations, independent solo audition. Use preallocated voice storage and explicit headroom. Preserve the protected bus before nonlinear FX, or visibly release the invariant.
- **Surplus Choir (VSTfx):** for explicitly supplied stems, extract the orthogonal residual of a declared linear routing map; permit transformations in its kernel. No arbitrary source separation claim. Recompute the residual after map changes and use negative controls for clipping, delay and quantization.
- **Null Atlas (CYD):** XY controls select protected sum and activity target, snapping to an actually attainable pair; tap a voice to transfer a unit to another. Keep the unallocated residual and actual allowed gain vector visible. The artistic screen may conceal the inspector; a separate diagnostic screen remains available.
- **Counter-carrier (FM-1):** explore signed modulation pairs only under a verified linear summing architecture. Ordinary nonlinear FM is not guaranteed to preserve the master; treat it as a separate proposed experiment.
- **Procedural field:** graph-incidence routing permits circulation around loops without changing node divergence. A landscape can hold independent loop music and a protected boundary delivery. This is a speculative generalization, not implemented or qualified here.

MHAC engineering question: can an interface expose actual resource use independently of its emitted signal and distinguish measured telemetry from a deliberately fictional sonification? Conventional typed execution and resource receipts are the comparator. Independently vary resource use, nullspace activity and audible output. Outcomes: correct resource attribution, task decisions, abstention and workload; separately evaluate artistic preference. A counterexample is the compiler eliding cancelled terms, yielding the same simulated trace but different computation. An acoustic advantage is unestablished. No participant recruitment, external review or production deployment is proposed.

## Checkpoint

Live AGENTS.md, RAG.md, README.md, programme, runbook, integrity and validation rules consulted (long documents selected ranges); 40 recent PR titles and 25 active issue results reviewed. Targeted issue searches for Bataille, expenditure, potlatch, cancellation, clinamen, Warburg, undo and related terms distinguished this from #494 collateral exceptions, #672 faceted classification, #568 coherent cubic cancellation, #666 hidden-schedule cancellation, and the recent #795 cutting expedition. Title/keyword search cannot establish exhaustive novelty. Base 495a98ca12bae467a507031f04931aa4254b1866; #799 freshly opened, body and empty comments fetched. Only this expedition's two files are proposed; canonical records, frozen protocol, generated aggregates and shared manifests remain untouched. Local laboratory qualification passed, full repository CI and independent mergedown qualification pending. No license grant or human gate bypass.

*The patron paid for the concert. The accountant counted the sound. The musicians asked whether the silence had a budget. The recorder had already stopped.*
