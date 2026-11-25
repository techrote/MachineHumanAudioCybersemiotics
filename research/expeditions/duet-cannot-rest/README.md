# The Duet That Cannot Rest

Hocket, handoff, and the composition of uninterrupted silence. 25 November 2026. Exploratory humanities/art expedition, not a registered empirical study or an amendment to MHAC's frozen protocol. AI-assisted research, writing, code and self-check by a single ChatGPT agent; no independent reviewer or participants.

## 1. Equal time, unequal possibility

Two identical synthesizers divide a continuous twelve-note melody evenly. The first pair alternates every note; the second plays six notes each before handing over. Their combined recording can be exactly identical. Yet one performer in the first pair cannot put down the instrument for six consecutive slots, whereas one in the second can. Equal entitlement to sounding time is not equal access to uninterrupted non-sounding time.

There is a further difficulty: a non-sounding performer might still be listening, counting, preparing a fingering, monitoring the other performer, or worrying about a missed entrance. Calling these slots "rest" is an artistic provocation, not a physiological measurement. A score might distribute opportunities for relief without actually producing relief. Conversely a musician might enjoy a demanding alternating passage more than a long tacet.

The artistic proposal is to compose the temporal shape of an obligation separately from the notes it produces. The sound of a collectively sustained line can hide where the work of sustaining it resides. The piece need not be an allegory about exploitation; a precisely interlocked duet can be an expression of mutual pleasure. We should not prescribe the correct political or emotional reading of the resulting music.

## 2. Source encounters and limits

All links accessed 2026-11-25. Locators indicate the actual extent read; no complete article reading or new empirical extraction is claimed.

- Sean Curran (2017), [Hockets broken and integrated in early mensural theory and an early motet](https://doi.org/10.1017/S0261127917000055), Early Music History 36, 31–104. Publisher abstract, especially paragraphs 1–3, read. Curran's historical reconstruction challenges the familiar exclusively multi-voice definition: earlier mensural theory can describe fragmentation within one voice. More strikingly, he describes a tension between the fragmentation of sound and the integrated planning that makes it possible, and reports that St. Emmeram's account gives attentive integrative listening moral significance. This is Curran's account, not our reading of the medieval texts. Our narrow two-voice model therefore cannot define historical hocket in general.
- ECM Records, [Facing North](https://ecmrecords.com/product/facing-north-meredith-monk-w-robert-een/), original release 1992-10-01, track 8 and featured-artist metadata read. This establishes Meredith Monk and Robert Een's recording context for Hocket. No transcription or audition of that recording was performed.
- Britt Robson (2017-03-20), [Meredith Monk](https://web03125.microsites03.redbull.com/2017/03/meredith-monk-feature/), passages on The Soul's Messenger and Hocket read. The reported performance with Katie Geissinger emphasizes the difficulty and trust involved in exchanging brief vocal fragments. Treat this as journalism and artist testimony, not controlled evidence. Interpretation: an absence of vocal output may be precisely the period when the co-performer must be most available.
- Harvey Sacks, Emanuel Schegloff and Gail Jefferson (1974), [A simplest systematics for the organization of turn-taking for conversation](https://doi.org/10.2307/412243), Language 50(4), 696–735. Publisher abstract only; original publication 1974, online publisher listing 2026. Their model makes conversational turn allocation locally administered and sensitive to recipients. In contrast our machine uses a globally precomputed slot schedule. Its exclusive allocation cannot capture the ordinary flexibility of conversation or decide whether an interruption is welcome.
- Peter Keller, Giacomo Novembre, Michael Hove (2014), [Rhythm in joint action](https://doi.org/10.1098/rstb.2013.0394), Phil. Trans. R. Soc. B 369:20130394, abstract and opening of section 2 as retrieved in indexed text; direct PMC open encountered a browser challenge. The review describes anticipation, attention and adaptation as key to ensemble coordination. This is a source claim about human joint action, not evidence that longer gaps are easier or more restorative. It supplies the principal rival interpretation of our toy metric: remaining silent may require active coordination.

The difference between a silent note, an idle process and an agent actually relieved of responsibility deserves its own authoring representation. Silence is an acoustic property; availability is a relationship; recovery is a possible outcome. They should not share an unqualified Boolean flag.

## 3. Exact construction (synthetic)

Take a marked cyclic word of length N=a+b, a,b>0, with exactly a slots owned by A and b by B. Exactly one owner per slot; equal slot durations; no overlapping tails in the formal model. Include the wrap-around handoff. Rotations are distinct unless they are identical marked words. There are r positive-length A runs and r B runs, hence 2r handoffs.

Let C(t,r,L,U) count ordered r-part integer compositions of t with every part in [L,U]. A's sounding bursts are exactly B's uninterrupted non-sounding windows, and conversely. Thus A-run lower/upper bounds may express B's minimum gap and A's maximum burst; B-run bounds express the reverse. The number of schedules is

    N/r * C(a,r,LA,UA) * C(b,r,LB,UB).

Proof: count pairs (word, marked A-run start). Each word has r possible marks. Conversely choose one of N positions for the mark, choose ordered A and B run lengths, and interleave them clockwise. This bijection is valid even for periodic words because the index of the mark is retained. With unrestricted positive parts, C(t,r,1,t)=binom(t-1,r-1), by placing r-1 cuts between t unit slots.

Feasibility is exactly r LA <= a <= r UA and r LB <= b <= r UB for positive valid bounds: start each part at L and distribute the excess up to capacity r(U-L). Therefore for symmetric a=b=m, minimum non-sounding window R and maximum sounding burst B (R<=B), the feasible r satisfy ceil(m/B)<=r<=floor(m/R), with 1<=r<=m. If no integer exists the scheduler must report infeasibility; it cannot rescue the contract by making a sound louder.

For m=6, unrestricted counts at r=1,2,3,4,5,6 are 12,150,400,300,60,2 (sum 924). With every run exactly two, r=3 yields four marked words. The total quota and handoff count alone do not establish the required window: AABBAABBAABB has both minimum windows 2, whereas ABAAAABBBABB has both minima 1 and the same six handoffs. In fact the largest achievable minimum of all runs is floor(m/r) and the smallest achievable maximum is ceil(m/r), simultaneously attained by balanced integer compositions. This is not a cognitive-load optimum.

Native laboratory.py enumerates marked words for a,b=1..7 and all positive interval bounds for each feasible r; dynamic programming independently counts bounded compositions. It checks count identities, infeasible combinations, and audio invariants. See RECEIPT.md. Elementary combinatorics, no mathematical priority.

## 4. Exaptation: the Rest Window Sequencer

Use an immutable event lane and independently editable ownership lane. A scheduler can choose handoff density, each agent's burst limit and minimum non-sounding window, and audition its separate stems against the invariant composite. A third lane specifies whether a silent agent is still monitoring, can precompute locally, or has been explicitly relieved of obligations. This third lane is not derived from silence.

The first instrument could allocate phase-continuous wavetable voices or sample events between two synthesizer agents, with a preview of ownership, contiguous windows and boundary handoffs. In the proof-of-concept renderer the voices are intentionally identical and notes retrigger with a fixed envelope; phase continuity is a future feature, not implemented. A monitor mode can play the ownership lane as stereo positions or timbre differences. That intentionally breaks the invariant mono mix and exposes the hidden arrangement.

A second instrument might deliberately complicate the assignment: a silent voice's filter state evolves during its gap, or the next owner takes over the previous owner's envelope. This lets a composer investigate whether a quiet interval is material for another voice rather than mere vacancy. Conventional sequencing, voice allocation, bounded run-length coding and scheduling already provide the machinery; the novel claim is at most a proposed authoring vocabulary, pending prior-art review.

A potential MHAC synthetic experiment compares equal event quotas under different contiguous gaps in an optional, low-consequence two-channel task. Conditions should include direct visual scheduling and no extra cue, measure interruption predictions and task performance, and distinguish designated off-duty time from non-sounding monitoring. Longer windows could worsen anticipation or disengagement. Urgent information must not be deferred merely to maintain this artistic contract. No human trial is authorized or performed.

## 5. The rest that belongs to somebody else (speculation)

The factory commissioned two identical music boxes. Each was paid for half the tune. The inspector recorded equality. A box asked to be taken out of the room while the other played. The inspector replied that it already spent half its time silent. The box requested a score with the silence in a single piece.

The musician did not correct the inspector's arithmetic. She wrote another arrangement and let the inspector hear it. He heard no difference.

For the next concert she added a third part, whose sole instruction was not to count. It was not clear whether anyone could perform it. The musician left the chair empty.

See [the original score](SCORE.md), [laboratory](laboratory.py) and [execution receipt](RECEIPT.md).

## Checkpoint and boundaries

Base 495a98ca12bae467a507031f04931aa4254b1866; issue #540. Read AGENTS, README, RAG, programme, runbook, integrity, validation and research workspace; reviewed 60 recent PRs and 40 open issue results, targeted hocket, rehearsal, silence, handoff, rest-window and adjacent topics. Issue #390 concerns optional participation and turn rights, not this fixed-quota bounded-run problem; #530/#531 concerns temporal identity assignment, not allocation of contiguous non-sounding windows. These bounded searches do not establish global novelty. This work is disjoint from accepted corpus, protocol, registers, shared manifests and instrument workers. Draft for integration review; no external peer review, human outcomes or Brier endorsement claimed.
