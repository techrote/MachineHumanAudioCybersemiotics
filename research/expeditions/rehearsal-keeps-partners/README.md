# The Rehearsal That Exchanges Every Mask but Keeps Its Partners

**2026-11-27 | MHAC exploratory humanities/art research | [Issue #803](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/803) | Draft/HOLD**

## A play for six actors (fiction)

A director announces a democratic rehearsal. Every actor will play every part. The principal speaker will become the respondent; the respondent will become the principal speaker; the witnesses will become the people they once observed.

At the end, the actors receive identical certificates. Each has occupied all six positions for an identical length of time.

Two actors discover that whenever either was asked a question, the other was the questioner. A different rehearsal of the same play sent the question around all six actors. The certificates cannot tell these rehearsals apart.

One actor proposes that the director rehearse a relationship rather than a role. Another asks who appointed the director.

The instrument imagined here is a theatre whose casting is a score, not a setup operation.

## Source encounters and bounded readings

**Bertolt Brecht, A Short Organum for the Theatre (1948), §§57–62**, especially §§58–61 on printed p. 12 of the [English PDF transcription](https://www.german-dutch.com/139-Brecht_A_Short_Organum_for_the_Theatre.pdf). The relevant sections were read; page images 10–11 (zero-based) were visually checked. This copy has uncertain edition metadata; the German original and complete essay were not independently read. In §57 he asks an actor to retain alternative utterances and initial reservations rather than disappear into the finished characterization. In §§58–59 the development of characters depends on one another; exchanging roles in rehearsal can reveal how supporting performances create the apparent qualities of the dominant part. In §§60–61 the relation to other characters is constitutive of gest, which encompasses complex and sometimes contradictory attitudes. This is not a prescription for equal-frequency casting, a quantitative measure of social power, or evidence for the effect of our instrument.

**Carrie J. Preston, [A class on Bertolt Brecht's Der Jasager/Der Neinsager](https://sites.bu.edu/learningtokneel/activities/a-class-on-bertolt-brechts-der-jasagerder-neinsager/)**, Procedures, Free-Writing Exercise and Results (web page, full sequence read; author established by [site home](https://sites.bu.edu/learningtokneel/)). The teacher and boy exchange parts across versions, explicitly to make the distribution of authority through casting available to reflection. The exercise itself then changes the prompt, until no writing is requested, yet Preston reports students tending to repeat the earlier argumentative format. This is the most interesting correction to our initial idea: changing declared roles does not erase the institutional situation in which they are performed. The reported classroom response is a teacher's account, not a controlled experiment or independent evaluation. The related book chapter and full plays were not read; do not reduce the Japanese noh source tradition to its European adaptations.

**Kurt Weill, [Gestus in Music](https://doi.org/10.2307/1125003)**, translated by Erich Albrecht, Tulane Drama Review 6(1), September 1961, 28–32. The Cambridge publisher's opening extract, metadata and translator/editorial footnote were read; the rest of the text was not accessible. Weill asks what makes music appropriate to the theatrical situation. The footnote explicitly cautions against translating Gestus as mere physical gesture. No detailed Weill compositional prescription is derived from the inaccessible remainder. No historical music is copied or reproduced.

**Joy H. Calico, [The Operatic Roots of Gestus in The Mother and Round Heads and Pointed Heads](https://doi.org/10.1525/california/9780520254824.003.0003)**, Brecht at the Opera (2008), ch. 2, pp. 43–75. Publisher abstract only. Calico situates Brecht's changing practice in changing collaborators, audiences, performers and political circumstances. This complicates any idea of a universally fixed Brechtian technical method. Full chapter unavailable; this is a reading lead, not a completed close reading.

## Interpretation: the actor is not the role

A conventional synthesizer assigns a timbre to a part. A gestic instrument could instead distinguish a persistent performer, a temporarily occupied part, and the relationship currently being staged between performers. A performer may change the part without changing its partners. Or it may change partners while retaining its part. Those are not the same musical transformations.

A scene can be played twice with the same score and cast but with different allocations of listening, response, interruption and silence. The composer might write a role for an oscillator that normally emits the first note of each phrase, then move that role to another oscillator without resetting either one's phase or timbral memory. The new allocation changes which history occupies the role.

The technical reduction below is intentionally severe. It treats every actor as interchangeable in capacity, every role as equally long, and one directed relation as selected for inspection. It cannot measure the experience of a role or the power to refuse it. Its point is to demonstrate an exact obstruction to interpreting equal role exposure as complete relational rehearsal.

## Synthetic construction: the casting organ

Let n distinct performers occupy n distinct roles in each of n rehearsals. A casting block is an n-by-n Latin square: each row is a permutation of performers, and each column is also a permutation. A fixed row gives the cast for one rehearsal. A fixed column gives the complete roster for one role.

Select two roles, caller and respondent (columns 0 and 1). Normalize row order by the identity of the caller. The two columns then read identity and p, where p is a permutation without fixed points: a performer cannot occupy both roles in the same scene.

**Proposition 1. Every derangement can occur as the caller-to-respondent map of a complete casting block.** The remaining entries can always be completed. After k columns are chosen, form a bipartite graph with rows on the left and performers on the right. Join a row to each performer not yet used in that row. Both sides have degree n-k, since each previous column used every performer once. When k<n, every subset S of rows sends (n-k)|S| edges to its neighbours, each of which can receive at most n-k such edges. Thus |N(S)|>=|S|. Hall's marriage theorem gives a perfect matching, which can be the next column. Repeat until all columns are filled. This uses the established finite Hall criterion; it is not a new theorem of combinatorics. The reference formulation was checked at [Hall's marriage theorem, graph-theoretic formulation](https://en.wikipedia.org/wiki/Hall%27s_marriage_theorem), not Hall's original paper.

**Proposition 2. For complete exposure to every ordered distinct performer pair in these two particular roles, exactly n-1 balanced blocks are necessary and sufficient.** Each block covers n directed pairs, whereas there are n(n-1) desired pairs. To attain the bound, index actors modulo n; for block d=1,...,n-1 use row i with caller i and respondent i+d modulo n, and fill the other columns with the remaining distinct offsets. Each block is Latin and every ordered pair occurs once in the collection. This does NOT assert that the same construction simultaneously balances every other ordered role pair. That is a different design problem.

**Proposition 3. Equal role counts do not even identify the cycle decomposition of p.** At n=6 the derangements have cycle types (2,2,2), (2,4), (3,3), or (6). Each has the identical role histogram: every performer appears once in every role. Under an independently authored rule that passes a motif from caller to respondent repeatedly, the number of applications required to return to a performer is its cycle length. That return process is a proposed additional score, not the literal rehearsal chronology.

The number of derangements of n is the inclusion-exclusion count sum over k=0,...,n of (-1)^k n!/k!. The count of a cycle type with m_j cycles of length j is n! divided by the product of j^(m_j) m_j!; order within a cycle is cyclic and cycles of equal length are unordered. For n=6 this gives 15,90,40,120 in the order above.

### Executed census

The companion [laboratory.py](laboratory.py) constructs and validates one block for every derangement from n=2 through 7, independently counts all 576 labeled order-four Latin squares by enumerating complete rows, and verifies the sharp pair-coverage construction for each population.

| n | derangements |
|---:|---:|
| 2 | 1 |
| 3 | 2 |
| 4 | 9 |
| 5 | 44 |
| 6 | 265 |
| 7 | 1854 |

All 2,175 derangements extended successfully. At n=4 exactly 288 of the 576 complete Latin squares have two reciprocal pairs in the selected relation; the other 288 have a single directed four-cycle. Three malformed maps are rejected. This is an exhaustive finite census under stated rules, not an estimate of the prevalence of social structures.

The extension implementation uses a deliberately small brute-force perfect-matching search; do not place it inside an audio callback or extrapolate its speed to large ensembles.

## Original artistic score: Three Rehearsals of the Same Play

The six role identities have frequencies 180,270,360,450,540,630 Hz; the six performer identities have frequencies 240,305,370,435,500,565 Hz. Each rehearsal plays all six roles in their fixed order. Each slot lasts 200 ms with a sine-squared envelope. The left channel plays the role, the right plays the performer assigned to it. Every performance has six rehearsals and 36 slots (7.2 seconds).

- Pairs: p=(1,0,3,2,5,4), three reciprocal dyads.
- Triangles: p=(1,2,0,4,5,3), two three-person circuits.
- Ring: p=(1,2,3,4,5,0), a single six-person circuit.

The full casting arrays and WAV hashes are emitted to audio/receipt.json when running the script. The three stereo WAVs are distinct; the role channel has the same raw PCM SHA-256 f0bb3800350736d5b6c57104f1134bec2616fe0d39597fde6a4162cc7f68fa16 in every edition. PCM is signed 16-bit, 16 kHz; 115,200 stereo frames per recording. Native execution twice produced identical file and receipt hashes; header and full frame readback assertions passed. The bounded oscillator amplitudes are at most 8,000 PCM units per channel. The audio is original and synthetic, not a recreation of a Brecht/Weill work.

Performance instructions (original): first audition the left channel only. Then audition the right channel. In each scene, imagine that the second performer must answer the first. Now replay just the first two slots of every scene and read the caller/respondent map. Try passing a note around the resulting graph, starting with A; stop on returning to A. Finally, let a performer decline its assigned part, and write an extra scene rather than force the certificate to remain balanced. The last two instructions are not implemented in the renderer. No listener trial occurred.

## Exaptation: compose casting as an instrument parameter

A VSTi could preserve six oscillator states independent of six role-specific modulation graphs. An atomic routing change at a phrase boundary reassigns roles without invalidating the identity or internal history of an oscillator. Keep a role bus, actor bus, and optional relationship bus; avoid automatic gain compensation that hides routing changes. The existing renderer does not implement continuous state inheritance, host transport, real-time automation, or MIDI.

A CYD Cast Atlas could display the casting grid on the left and the selected partner graph on the right. The horizontal gesture changes rehearsal; vertical movement selects an actor. A separate brush chooses a relationship (e.g. call/response, modulation source/destination, foreground/accompaniment), not a global importance score. Preview a whole block on a worker or control thread; publish a prevalidated immutable routing snapshot. Refuse edits that violate protected routing constraints, unless the performer explicitly switches to a free score.

An FM-1 sketch could assign algorithmic carriers and modulators as temporary roles of persistent voice identities. Whether the hardware supports such a mapping is unverified. Nonlinear FM will not generally preserve the role waveform; the exact PCM invariant is limited to this renderer.

In a procedural oscillator city, inhabitants could move between workspaces without changing the neighbourhood relationships that govern their activity. The city can announce perfect rotation while retaining a fixed network. A different brush changes the network itself. The relationship selected for inspection becomes a second visual composition, rather than an intrinsic truth about the population.

## Counterargument and possible research

A Latin square is not a just institution. Rotation into a role does not imply equal ability to perform it, equal choice, equal risk or equal influence. A scene with a refusal is not a malformed scene. It may be the most important event of the work. The director who determines the grid still has a role that the grid does not distribute. Preston's exercise is a reminder that rearranging an explicit task can preserve a hidden authority. The appropriate artistic response may be to abolish the cast inspector, or add the power to rewrite the theatre, rather than optimize its coverage.

Operational MHAC distinction: identity, assigned role, event target, authorized scope, observed response and independent verification are separate. A count of appearances in a role cannot establish that a relationship was exercised. A target-specific receipt cannot be replaced by an aggregate count of replies. This is a model-derived design hypothesis only. Compare a typed actor-role-target event ledger (strong baseline) against a learned acoustic relation motif on synthetic cases with equal marginals but changed partners, missing target fields, stale roles and asymmetric authority. Measure correct binding, false attribution, appropriate abstention, latency and workload separately; artistic preference is not correctness. No acoustic advantage is established.

## Checkpoint

Live AGENTS, RAG, programme, runbook, research-integrity, validation and protocol freeze were consulted on 2026-11-27; base main 495a98ca12bae467a507031f04931aa4254b1866. Recent issue and PR results (45 each) plus targeted searches checked overlap. #238 concerns nonlinear coalition attribution; #262 rule amendments; #390 turn opportunities and uptake; #578 transfer timing on circuits; #274 temporal privacy; #512 PCM-bound receipt integration. This expedition instead isolates complete role rotation with incomplete partner coverage. No claim of exhaustive novelty. New issue #803, isolated additive branch, no shared manifests or canonical Track E/G changes. All notes, code and audio are AI-assisted by ChatGPT (GPT-6.2); self-check, not independent human review. Local Python execution and exact Git blob comparison are the bounded qualification. Repository CI and substantive integration remain separate. No human gate was satisfied, no license granted, no participant data collected.
