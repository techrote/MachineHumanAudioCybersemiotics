# The Splitter That Needs a Delay

Refs #416. Synthetic mathematical expedition; not a human or hardware experiment.
Base reconciled: 495a98ca12bae467a507031f04931aa4254b1866. No frozen files edited.
Live issue/PR discovery included paraunitary, filter bank, lifting, lossless and group delay; #336 is adjacent cyclotomic work but addresses monotone transitions, not lossless mixing.

## Model and arithmetic obstruction

Let H(z) be a real two-by-two causal FIR matrix of degree D, coefficients in Z[1/2], satisfying H(z^-1)^T H(z)=I. z denotes a delay. An equal power split of input 1 means |H_11(z)|^2=1/2 at a specified unit-circle point. This is neither equal acoustic loudness nor a claim of perceptual equivalence.

Any two dyadic rationals x,y with x^2+y^2=1 must be a signed coordinate vector: clear the common denominator 2^b, and if b>0 both integer numerators must be even by reduction modulo four. Iterate. Thus H(1) and H(-1) are signed permutations. Constant dyadic 3-port matrices are also signed permutations by the same mod-four argument (three squares); four ports permit a normalized 4-by-4 Hadamard matrix with entries +/-1/2. This is a dimension trade-off, not a two-port equal-split solution.

Write the first column as (a(z),b(z))/M with M=2^s, a,b integral. Set F(z)=z^D(2a(z)a(z^-1)-M^2). This is an integral polynomial of degree at most 2D, F(1)=+/-M^2, F(-1)=+/-M^2. At a primitive q-th root equal power is equivalent to Phi_q dividing F, by irreducibility. This is an exact certificate, not a floating threshold. F is nonzero by its DC value.

For q=p^k (p odd prime), Phi_q(1)=p by the geometric sum. For q=2p^k, Phi_q(-1)=p by Phi_2n(z)=Phi_n(-z) for odd n>1. Divisibility would make p divide M^2, impossible. Orders 1 and 2 are already forbidden by the signed-permutation argument. The obstruction holds for every degree and bit depth. It is not claimed for all odd composite orders.

## Minimum delay bounds and construction

Since F is nonzero, 2D >= phi(q) (Euler totient). A sharper bound applies when Phi_q(1)=1 and q>2. If 2D=phi(q), divisibility implies F=+/-M^2 Phi_q. But its leading coefficient is 2a_0 a_D. Losslessness at lag D gives a_0 a_D = -b_0 b_D; the zero-lag sum of squares is M^2. By 2|xy|<=x^2+y^2, 4|a_0 a_D|<=M^2. The required leading coefficient magnitude M^2 contradicts this. Hence D>=phi(q)/2+1 for these orders.

Define P as the orthogonal projector onto (1,1). E_d(z)=I-P+z^d P, or the matrix with diagonal (1+z^d)/2 and off-diagonal (z^d-1)/2. P^2=P=P^T, P(I-P)=0 imply E_d is paraunitary. First output power fraction is cos^2(pi d/q) at z=exp(-2pi i/q), second sin^2(pi d/q). If 4 divides q, d=q/4 gives exact equal split. When q=2^k, k>=2, the degree bound matches d. The sharpened bound also matches d for q=4p with p odd prime. Examples: q=12 needs degree 3, q=20 needs degree 5. q=24 is bounded 5..6, unresolved by these proofs. q=15 is unresolved, not refused as impossible.

At fixed coefficient denominator M=2^s, s>=1, the real algebraic integer alpha=M^2/2*(2|a(z)/M|^2-1) has all conjugates bounded in magnitude by M^2/2 by losslessness. If alpha is nonzero its norm in the real cyclotomic field is a nonzero integer. For q>2 this proves |2|H_11|^2-1| >= (M^2/2)^(-phi(q)/2). This weak separation bound is not asserted sharp.

## A finite alphabet of degree-one stages

Normalize a degree-one H by left multiplication with H(1)^T, so H=I-P+zP. Orthogonality of coefficients implies P=P^TP, hence P symmetric idempotent. For rank one, write P=[[u,v],[v,1-u]]; (2u-1)^2+(2v)^2=1. Dyadic rigidity above restricts P to two axes and two diagonals. Rank zero and two give I and zI. The compiler uses four rank-one stages A,B,+,-; a product remains lossless. It does not assert that every higher-degree dyadic paraunitary admits a dyadic stage factorization.

splitter.py compiles an exact first column, checks its autocorrelation sum, and supplies polynomial remainder and order bounds. A full two-port completion for a column of degree <=D is [[a,-z^D b(z^-1)],[b,z^D a(z^-1)]]/M. This is paraunitary by direct multiplication. The actual stage product is another valid full completion. No per-sample fixed-point rounding is part of the theorem.

## Qualification

Native Python 3: execute python splitter.py. The census retains distinct integer column pairs at each of depths 1..8 (same denominator within depth), not independent full matrices. Counts 4,13,40,121,364,1093,3280,9841. All 438725 eligible polynomial remainder checks completed; each retained column passed losslessness and DC/Nyquist assertions. First witnesses through order 60 were q=4,8,...,32 at d=q/4, all repeated + stages. This is an exhaustive restricted alphabet census, not proof that other FIR matrices cannot improve a bound. Separately, the main script verified witnesses for all 64 multiples of 4 through 256. An exploratory SymPy polynomial oracle independently generated the cyclotomic divisors and reproduced the same first-witness census; stage recurrence is shared mathematically.

python audio.py generates stereo PCM at 48 kHz for q=64 and 81, both d=16. Input integer samples are even so half sums are exact. Circular input, zero second input, inverse uses circular advance; reconstruction equals input exactly and second reconstructed channel is zero. Total sample-square energy is exactly conserved, no clipping. q64 produces equal sample-square energies, q81 left fraction 0.6618669707034835. Two repeated renders match hashes. Quantized sine is not exactly a single Fourier mode; its ideal power fraction is separately reported. No streaming latency/overflow/hardware or perceptual claims. A causal inverse would add latency, not advance real time.

Negative cases: arbitrary irrational coefficients admit a constant Hadamard rotation; three dyadic channels cannot circumvent static mixing rigidity; four channels permit mixing but change the physical contract. Ordinary rounding may break energy conservation. A single output does not retain the full input. Unresolved orders and bounded minimum-degree cases are explicitly marked. Native repository clone failed DNS; standalone runs only. No reviewer or scientific acceptance claimed.

## Provenance and exaptation

Established paraunitary framework: Julius O. Smith, Spectral Audio Signal Processing, Lossless Filters, equations 12.79–12.81, https://www.dsprelated.com/freebooks/SASP/Lossless_Filters.html (web text consulted). Established lossless lattice factorization context: The Design of Matched Balanced Orthogonal Multiwavelets, 2021, section Parameterizing Lossless FIR Polyphase Filters, theorem 3.1, https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2021.785803/full (web excerpt consulted). Cyclotomic prime-power formula and irreducibility are standard; self-contained divisibility application above. No priority claimed for the mathematics. AI-generated derivations and implementation; no independent human review.

Potential transfer: exact-arithmetic spectral splitter diagnostics, frequency-selective stereo routing with reversible signed delay stages, constrained DSP compiler, numerical-vocabulary counterexamples, and explicit trade-offs between delay, coefficient precision and channel count. These are design hypotheses, not evidence of human communication effects.
