# Evidence, contrary cases and execution receipt

Date: 24 November 2026. AI-assisted expedition; one ChatGPT agent authored the report, original code, experiments, and self-review. No independent human review, participant observations, or claim of scholarly priority.

## Source ledger

| Source and exact locator | Access and reading extent | Supports / does not support |
|---|---|---|
| Michel Foucault, 1969 lecture, Bouchard and Simon translation in *Language, Counter-Memory, Practice* (1977), pp. 124–127 as identified by [the excerpt host](https://foucault.info/documents/foucault.authorFunction.en/) | Read visible excerpt from introduction through third feature, ending in ellipsis. Not a complete lecture or checked print edition. | Author-function as historically variable and constructed by interpretive operations. Does not support equivalence to an allocation rule, nor establish universal history. |
| Lloyd S. Shapley, [RAND P-295](https://www.rand.org/pubs/papers/P295.html), 1952, description and document details; 1953 [chapter DOI](https://doi.org/10.1515/9781400881970-018), publisher metadata pp. 307–318 | Read landing page and chapter metadata; full original chapter unavailable in accessed view. No claim of primary theorem reconstruction. | Historical provenance of the value and axiomatic approach only. |
| Stéphane Airiau, [Cooperative Games, Lecture 7](https://www.lamsade.dauphine.fr/~airiau/Teaching/CoopGames/2012/coopgames-7%5B8up%5D.pdf), slides 3–8, PDF page index 0 | Inspected extracted equations and page image including slides 3, 4, 6, 8. Teaching material, not original proof. | Marginal contributions, uniform permutation definition and equivalent subset weights. Slide 5 gives a contrary example where the Shapley value is not in the core. |
| Philip Thomas, [Understanding Indeterminate Music through Performance](https://doi.org/10.1017/S1478572212000424), 2013, publisher abstract, pp. 91–113 metadata | Read abstract, not the full article. | Performer realization as a route to musical understanding. No attribution metric or findings on this instrument. |

All source notes are original paraphrases. No third-party texts, recordings or source images are redistributed. No new license selected. The interpretation that attribution systems construct their objects is the expedition's own reading, not a mathematical consequence of Foucault or a claim that the sources are mutually equivalent.

## Extended result: incomplete audits

An exact inspector is implemented in [partial.py](partial.py). Six inputs are 0, 1 or unknown, with one input per pair. The unknowns are unrestricted independently within the stated game family. If k pairs remain unqueried, there are exactly 2^k possible graphs.

For each pair of opposite graph edges, its difference can take one, two or three values, obtained by subtracting the two allowed bit sets. Taking the Cartesian product of those three difference sets, then applying the report's orthogonal-vector map, gives the **exact joint set** of possible Shapley allocations. No prior on the unknown bits is needed.

Each individual share's sharp interval has width k/12: every unknown edge changes that share by exactly plus or minus 1/12, so independent favorable or unfavorable completions attain its extrema. The extrema for different people need not be simultaneously attainable. Reporting four independent intervals as though every combination were feasible is another information loss.

Example in AB AC AD BC BD CD order: (1, unknown, 1, unknown, 0, unknown). Eight graph completions and eight possible vectors. Marginal intervals in twelfths are A=[3,6], B=C=D=[1,4]. The exact set contains (3,3,3,3) and (6,2,2,2), but not the vector (3,1,4,4), despite all its coordinates satisfying the intervals and summing to 12. An instrument may thus preserve the joint set rather than merely the uncertainty bars.

Contrary controls: zero unknown edges gives a unique allocation; all six unknown gives 64 graphs and 27 vectors; equal vector does not imply equal graph; the empty and complete graph make that fact especially clear.

## Executed checks

Local environment Python 3.13.5. Commands from the expedition directory:

    python lab.py --out audio
    python partial.py

Observed 12,741 assertion evaluations in the main verification (64 games, all comparable coalitions, all single-bit graph neighbors, formula vs permutation checks, exact PCM witness comparison and extremes). Partial audit verification: 2,921 assertion/rejection checks covering all 729 ternary audit configurations against enumerated compatible games, plus malformed input rejection. The two algorithms are independent calculations in the same authored codebase, not independent researchers. Total 15,662 counted checks. Exact local Git blobs verified against repository fetch: lab.py f66f5bc6da93f5822bf69893410ece4da8617194; partial.py 3f48de31e6fbe9bb42c0f62950e757d531954582.

Observed distribution: 64 graphs, 27 distinct credit vectors; class sizes 1:8, 2:12, 4:6, 8:1; equal-share graph IDs 0,12,18,30,33,45,51,63. Graph IDs use the six pair bits in AB AC AD BC BD CD order, with AB least significant. Sharp bounds 0 and 1/2 attained. Routine WAVs identical.

| Original PCM WAV, 16 kHz mono signed 16-bit | SHA-256 |
|---|---|
| star-routine.wav | 28fc511d2f753a7244594b73b3072aa6b9ca9c8232ca07fbb11f25b5ed582abc |
| triangle-routine.wav | 28fc511d2f753a7244594b73b3072aa6b9ca9c8232ca07fbb11f25b5ed582abc |
| star-pairs.wav | 8d433230a0ef271188665ae8a70ab73a081223e7d319c3a45aa1295f27cfa350 |
| triangle-pairs.wav | df17a7737f4642897fe1ce1cfc8ad9a3ee26c83bb975b35e1f27dfb8bc3c88bf |

The deterministic generator emits WAVs and results.json to a caller-selected directory; generated binaries are not committed. The repository test bridge runs the two scripts as subprocesses. Exact-head CI and any required reviews must be checked before claiming landing.

## Reconciliation and limits

Base observed: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS.md, RAG.md, programme, runbook, integrity and validation docs; surveyed current issues and open PRs, and read #230 and #236 scopes. #230 investigates additive source attribution; this work concerns nonlinear coalition interaction and allocation. #236 investigates stochastic decision channels; this work does not compare channels. Other worktrees and shared manifests were not edited. No changes to frozen protocol, canonical registries, empirical synthesis, or human gates. Full repo qualification and scholarly critique are distinct from the local arithmetic and PCM checks.
