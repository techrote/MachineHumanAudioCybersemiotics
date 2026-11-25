# The Avalanche That Writes a Receipt

Refs #498 · 25 November 2026 · isolated mathematical and artistic expedition, not Track E/G evidence or an accepted interface requirement.

## Model and result

Take n sites on a path, numbered 1 through n, with absorbing ends 0 and M=n+1. Stable heights are 0 or 1. Each legal firing of a site holding at least 2 sends one grain to each neighbour, losing grains that reach either absorbing end. Begin in the all-ones configuration (h=0), or with exactly one hole at site h (1<=h<=n). Add one grain at i, then fully stabilize. Receipts record total firings T and optional left/right sink counts. Each action changes the underlying state; a second probe is NOT a repeated measurement of the original configuration.

For this family:

- The final hole is h'=(h-i) mod M, using 0 for all ones.
- T=(M-i)(i-h) for h<i; T=i(h-i) for h>=i.
- Every count has at most two candidates. There are exactly gcd(M,i)-1 ambiguous counts; count-only identification is universal iff gcd(M,i)=1.
- A count plus either one of the two endpoint-loss bits uniquely identifies h.
- If a first count is ambiguous, precisely one further count-only probe is necessary and sufficient, allowing a choice of injection site. Repeating i works unless i is the exact centre; at the centre every repeated centre-only count preserves reflection ambiguity indefinitely. An injection at site 1 resolves it.

## Derivation

For an all-ones segment between absorbing boundaries L and R, with L<i<R, topple i then propagate outward through every interior site once. After this wave the two ends have lost one grain, and the interior has its original heights except for the added grain at i. If i remains unstable, the next wave occupies the interval with each endpoint advanced inward by one; the previously emptied endpoints receive a grain and are restored. Repeat until i is an endpoint of the active interior (or the only site). This is a legal sequence: start each wave at the unstable i and propagate outward, firing each active site once. The last wave leaves a single zero at L+R-i (if the last active interval is a singleton, that site is the zero). The number of nested waves including site j is

    u_j=max(0,min(j-L,R-j,i-L,R-i)).

This also proves termination for this construction. Stabilization is order-independent by the standard Abelian sandpile property [S1]; the firing vector is unique since the reduced path Laplacian is invertible (its homogeneous equation is zero second difference with zero endpoints).

If h>i use L=0,R=h: the original hole absorbs exactly one grain (the boundary-adjacent site fires once), cannot topple, and becomes full. For 0<h<i use L=h,R=M. If h=0 use the full interval; if h=i no toppling occurs. Thus h' follows the stated formula. The sum of the nested trapezoid is (i-L)(R-i): counting each wave's interior length gives sum_{k=0}^{min(i-L,R-i)-1}(R-L-1-2k). Substitution yields T. Sink counts are L_loss=1 iff h=0 or h>i, R_loss=1 iff h<i; for n=1 the sole site sends one grain to each end.

## Exact inverse and active diagnosis

The two monotone branches of T meet at zero and cannot collide internally. Write g=gcd(M,i). A nonzero collision consists of h_a=i-i*k/g and h_b=i+(M-i)*k/g for k=1,...,g-1: equality of the two branch products forces both branch offsets to be integer multiples of the respective coprime reduced factors. k=g is excluded because h_b=M is not a site. Both hypotheses have opposite endpoint-loss bits. The closed-form decoder tests at most two candidates using divisibility; it can also reject inconsistent observations. Time and space for a single count decode are constant in the number of sites (ordinary integer arithmetic). Odometer output takes O(n) operations and storage.

For a colliding pair set q=k/g. After the first action their new holes are A=M-i*q and B=(M-i)*q, with A>B. If both lie on the same count branch, strict monotonicity distinguishes them. If they straddle i, equality would require (M-i)*(i-B)=i*(A-i), hence q*((M-i)^2-i^2)=0. Since q>0, this is possible only at the centre i=M/2. At that centre, reflection h->M-h preserves all counts and commutes with the state shift by i modulo M, so unlimited repeated centre measurements cannot resolve a colliding pair. Site 1 is coprime to M and gives an injective count on the changed state. This proves the adaptive plan's minimum additional probe count (0 when unique, 1 when ambiguous; inconsistent inputs have no feasible plan).

Example n=11, i=4: h=2 and h=8 each yield 16 firings. They lose a grain at the right and left sinks respectively. Their new holes are 10 and 4; a second injection at site 4 yields counts 24 and 0. At i=6, h=3 and h=9 instead have identical centre counts forever. These are deterministic counterexamples, not a noise model.

## Reproducible apparatus

From this directory:

    python verify.py --out build

The standard-library Python oracle directly executes individual legal topplings with left-first and right-first priorities. It does not use the closed-form odometer to generate its trajectories. It enumerates every n=1..28, i=1..n and h=0..n, then groups exact count classes, tests each endpoint bit, checks adaptive second probes and tests invalid inputs. Native Python 3.13.5 results: 8,120 input states, 16,240 legal schedule replays, 7,761 count classes, 359 ambiguous pairs including 91 centre pairs. All assertions passed. There are 16,240 single-bit recovery comparisons (both sink choices for each state). The separate formulation is not independent human review.

The local WAV generated by the verifier, same-count.wav, contains 16 sequential 75 ms integer triangle pulses per channel, one per actual firing in the direct left-first schedule. Pitch depends on site; matched pulse counts and peaks do not imply equal energy or perceptual equivalence. PCM16 stereo, 16 kHz, 1.2 seconds, peak magnitudes 7000. Two consecutive renders gave identical hashes. The committed results.synthetic.json records SHA-256, event sequence, odometers, and counts. Audio bytes are generated on demand, not committed. This is an original artistic convention, not a listening study or a physical sandpile recording.

## Transfer, falsifiers and provenance

A possible instrument would let a performer inject grains and hear both the size and location of a cascade, optionally using endpoint loss as a separate binary accent. Count-only sonification can deliberately hide a latent state; a subsequent probe can disclose it by perturbing that state. The same apparatus may provide exact regression fixtures for discrete procedural simulation and actively probed machine communication. The CyberSand transfer is prospective; no integration or equivalence to its chemistry, pressure solver or physical dynamics is claimed.

Negative case: starting outside the family, [0,0,1] and [0,1,1] both produce zero firings and zero sink losses after adding at site 1; final configurations differ. This defeats the unrestricted one-bit theorem. The model also excludes arbitrary multi-grain bursts, uncertain injection sites, noisy/lost receipts, asynchronous injection before stabilization, arbitrary graph topology and acoustic classification. The theorem establishes exact symbolic distinguishability, not human decoding, and does not assert robustness to count errors. The audible schedule is a selected legal ordering; only the odometer is guaranteed invariant.

[S1] David Perkinson, *Abelian Sandpile Model*, SageMath Thematic Tutorials, version 10.10 as displayed, https://doc.sagemath.org/html/en/thematic_tutorials/sandpile.html#stabilization ; Stabilization and Laplacian sections (web text around lines 112–115, 215–225 inspected 2026-11-25). Secondary mathematical tutorial for the established model and order independence. The path-specific calculations above are locally derived; no priority claim or exhaustive literature search. No source text or data copied into fixtures.

AI-assisted derivation, implementation, native execution and scope review by one agent. Main reconciled at 495a98ca12bae467a507031f04931aa4254b1866, recent issues/PRs inspected, searches for sandpile/avalanche/toppling found no matches at intake; existing homometry work was avoided. This does not prove novelty. Native checkout blocked by GitHub DNS resolution; source/receipt Git blob comparison is performed separately. Repository-wide tests and external review remain pending. Only new files in this issue-scoped folder; no frozen records, central manifests or other branches changed. Draft disposition.
