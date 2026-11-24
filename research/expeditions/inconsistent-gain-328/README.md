# The Gain That Cannot Agree With Itself

**Scope:** #328, synthetic mathematical expedition, 2026-11-24. Base 495a98ca12bae467a507031f04931aa4254b1866. No change to the frozen protocol, registry or main programme. AI-generated mathematics/code, self-reviewed and cross-checked by different algorithms, not independently human-reviewed.

## Problem

An instrument reports intervals for ratios of positive gains, but absolute calibration is absent or irrelevant. Use log-level coordinates x (e.g. dB for amplitude ratios). Measurements impose inclusive integer-tick bounds l <= x[j]-x[i] <= h. This is a deterministic uncertainty set, not a probability distribution. An estimator y must be one coherent vector of log levels, not unrelated estimates of each ratio. Error is oscillation seminorm ||x-y||_osc = max(x-y)-min(x-y), i.e. maximum absolute error over all pairwise log ratios. Common offsets are immaterial.

A local pairwise midpoint can minimize each interval's individual worst error, yet the whole collection may be impossible to realize simultaneously. This is not about perceptual loudness or a claim that an actual device produces these intervals.

## Tight bounds and constructive certificates

Represent each interval by arcs i->j of weight h and j->i of weight -l. Shortest path closure d[i][j] yields the tight upper bound on x[j]-x[i]. A negative cycle means infeasible, because summing the constraints gives 0 < 0. Conversely no negative cycle permits shortest-path potentials from a super-source, giving a feasible x. For connected input, every bound is attained by x[k]=d[i][k], by triangle inequalities and d[i][i]=0. Disconnected feasible components admit arbitrary relative offsets, so the global minimax radius is unbounded. Componentwise relative reconstruction is possible but not implemented as a separate interface.

The exact diameter D of the feasible set in oscillation distance is max_ij (d[i][j]+d[j][i]): upper bound by the interval widths; equality by the two shortest-path witnesses for a maximizing pair.

For any estimate y, its worst-case loss is max_ij(d[i][j]-y[j]+y[i]). To enforce loss <= R requires y[j]-y[i] <= R-d[j][i]. Such a difference-constraint system is feasible exactly when every directed cycle of these weights has nonnegative total. Reversing orientation gives the exact minimax radius

    R* = max_C sum_{(i,j) in C} d[i][j] / |C|.

Only simple cycles are necessary (closed walks decompose into cycles). The maximizer is a lower-bound certificate independent of the candidate center. Shortest-path potentials at R* are an upper-bound certificate. The implementation searches closed walks of length at most n by dynamic programming from each start, retaining an attaining walk. It returns a rational radius and a rational center with common denominator.

A coherent optimum can also be chosen within the original feasible set: project any optimal y using P(y)[j] = min_i(y[i]+d[i][j]). Triangle inequalities make P(y) feasible and P(x)=x for feasible x. If a <= y[i]-x[i] <= b for all i, then a <= P(y)[j]-P(x)[j] <= b for all j, so the projection cannot increase oscillation error. The solver therefore includes the original bounds while computing the center. This property avoids returning a calibration estimate that violates measured constraints.

## Sharp separation from independent interval estimates

The largest individual optimal midpoint error is D/2. The coherent radius satisfies

    D/2 <= R* <= (n-1)D/n.

For a cycle of k>=2 edges, let F be the sum of forward d weights and B the sum of reverse weights. Each forward edge can be bounded by the other k-1 reverse edges by the triangle inequality, so F <= (k-1)B. Also F+B <= kD. Thus F/k <= (k-1)D/k <= (n-1)D/n. Self-loops have zero weight. Lower bound follows from a two-edge cycle attaining D. This is a specialized normed-space radius/diameter inequality, not a claimed new general Jung theorem.

Sharp family: 0=x[0] <= x[1] <= ... <= x[n-1] <= 1. For i<j, d[i][j]=1 and d[j][i]=0. Diameter is 1; the increasing cycle and its closing reverse edge attain (n-1)/n. A center is y[i]=i/n. Every directed pair midpoint for i<j is 1/2, impossible to realize simultaneously when n>=3 since two successive differences sum to 1, not 1/2. The ratio of coherent radius to independent midpoint bound is 2(n-1)/n, approaching 2. No unbounded separation is claimed.

For n=3 and a 12 dB interval width, the individual midpoint bound is 6 dB; coherent optimum is 8 dB. Naively taking midpoint estimates relative to coordinate zero gives y=(0,6,6), whose worst relative error is 12 dB. Minimax y=(0,4,8) achieves 8 dB on all three vertices (0,0,0), (0,0,12), (0,12,12). The minimax center deliberately accepts more error at some states to reduce the worst.

A useful negative control: if every pair's tight interval is centered around a common feasible vector (e.g. symmetric uncertainty about the true calibration), the midpoint system is consistent and the radius is exactly D/2. Asymmetry is essential for the gap, though not sufficient.

## Reproduction and qualification

- gain.mjs: standard JS, n=1..32, integer bounds abs <=1e6; intermediate exact integer arithmetic within IEEE safe integer range. Negative-cycle detection before closure avoids growth on invalid inputs. Infinity is internal only. Cycle search uses O(n^4) arithmetic operations plus witness copying overhead; not a large-scale optimized solver.
- verify.mjs: run with Node, compare stdout with results.synthetic.txt. The 729 labelled three-coordinate configurations take six independent lower/upper magnitudes from {0,1,2}, so every input admits zero. All are bounded. Direct enumeration of integer feasible points checks all nine tight bounds per case (the extrema have integer witnesses). Enumerating coherent centers on a 1/6-tick lattice over [-2,2]^2 verifies the radius independently of the cycle algorithm: a center exists in the original set and its denominator is at most 3. Direct enumeration of simple cycles, primal and dual certificates, and radius/diameter inequalities also checked. 152 strict gaps and 356 inconsistent collections of pairwise midpoints; these are not interchangeable properties. Family n=2..12, shifted negative bounds, disconnected and inconsistent cases included.
- check_audio.py: Python standard library, direct integer feasible-point enumeration and exact Fraction two/three-cycle formulas independently reproduce all census counts and histogram. No graph closure reused. Run to regenerate WAV and verification JSON in run/. 
- Audio: three equal-reference partials (250, 500, 750 Hz); each stereo channel uses the actual relative residual gains of a different calibration estimate. Common-mode error is removed by centering each log-error vector at its midrange, then exponentiating with amplitude dB convention. Left is anchor midpoint, right minimax. The three blocks correspond to the three simplex vertices. Spans in dB are left 6,12,6 and right 8,8,8. 1.8 seconds, 16 kHz, PCM16 stereo; repeated local execution identical bytes, SHA-256 fd8697ea87dea2c8778a915a474f6b95bc4d3f59c8d924af36a86f9b7b9ca36f. Common scale and short block fades; no clipping. This is a deterministic synthetic coefficient demonstration, not hardware or listener evidence.
- Local Python 3.13.5 run passed, local Git checkout blocked by DNS (github.com could not resolve); JS computational tests executed in V8 before commit. Repository-wide CI and independent review are separate gates.

## Provenance and limits

Prior art is directly relevant: Barnhill, Yoshida and Miura, *Maximum Inscribed and Minimum Enclosing Tropical Balls of Tropical Polytopes and Applications to Volume Estimation and Uniform Sampling* (2023), https://arxiv.org/abs/2303.02539 (abstract inspected 2026-11-24, describes LP minimum enclosing tropical balls); Krivulin, *Application of tropical optimization for solving multicriteria problems of pairwise comparisons using log-Chebyshev approximation* (2022), https://arxiv.org/abs/2205.10969 (abstract inspected, ratio constraints and log-Chebyshev optimization). These are background overlap, not claims of priority or full-text review. The derivations above are self-contained. The cycle-mean/shortest-path method and oscillation geometry are established mathematics. The particular calibration framing, executable qualification and synthetic instrument are this expedition's contribution. No empirical evidence is promoted.

The exact interval model assumes simultaneous, consistent bounds on log ratios, positive amplitudes, no phase cancellation, and no unmodelled calibration drift. Zero amplitude cannot be logged. No stochastic inference, outlier removal, actual hearing or loudness model. Inconsistent observations are refused rather than automatically repaired. No claim that the minimax choice is best under a different objective, prior, or perceptual metric.

## Exaptation

Use this as a small robust calibration compiler for oscillator banks, relative sensor levels, or multiplicative procedural controls. Tight intervals can diagnose missing calibration links; a critical cycle identifies which ratio observations obstruct a tighter coherent answer. A constrained synthesizer could expose asymmetry and ambiguity as compositional controls, rather than interpreting the interval midpoint as a necessarily realizable patch. For an agentic communication analogy, mutually plausible pairwise interpretations need not assemble into a single internally consistent explanation; this formal result does not establish such effects in people or agents.
