# The Gift That Returns as a Stranger

*Circulation, reciprocity and the latitude of transfer — 25 November 2026.*

Exploratory humanities/art research and synthetic computation, not canonical Track G/E evidence or human validation. AI-assisted source reading, derivation, implementation and self-review by the executing ChatGPT agent. No independent human review.

## The gift that changes the giver

Three musicians each possess a melody. A gives one to B, B gives one to C, C gives one to A. The ledger records three transfers and closes with each participant holding one melody. Yet the melodies might all have returned to their owners, two might have exchanged owners, or all three might have moved. The ledger is complete at its chosen level of description, but incomplete as a score.

The artist must decide which question the composition inhabits. Is its material the melody, the handoff, the relationship with a prior owner, the option to pass something onward, or the obligation to do so?

### Six source encounters

- Marcel Mauss, *Essai sur le don* (1923–1924), chapter I §III, electronic edition by Jean-Marie Tremblay (2002), electronic p. 18 onward. [French text](https://www.academia.edu/35383336/Essai_sur_le_don); [institutional edition index](https://classiques.uqam.ca/classiques/mauss_marcel/socio_et_anthropo/2_essai_sur_le_don/essai_sur_le_don_tdm.html). Read opening paragraphs in extracted text. Mauss treats giving and receiving as obligations alongside returning. This historical comparative argument does not establish a universal theory of gifts.
- Bronisław Malinowski, *Argonauts of the Western Pacific* (1922), chapter III, Sinaketa example and geographical directions of Kula valuables. [Online transcription](https://ridero.eu/pl/books/wl_argonauts_of_the_western_pacific/freeText), web lines 848–857 read. He describes oppositely directed circulation of shell necklaces and arm-shells and temporary possession. Our circuit is NOT a model of Kula: it has one token class, homogeneous agents, exactly one transfer per edge and no ethnographic context. Early anthropology's colonial categories cannot be treated as unproblematic accounts of contemporary Indigenous lives.
- Marshall Sahlins, *Stone Age Economics*, 2004 edition, chapter 'On the Sociology of Primitive Exchange', subsection on the spectrum of reciprocities. [Transcription](https://www.thetedkarchive.com/library/marshall-sahlins-stone-age-economics), paragraphs defining generalized and balanced reciprocity (web lines 1849–1855) read. He distinguishes indefinitely deferred or absent return from closely stipulated equivalent return. This complicates the idea of closing a gift ledger.
- Marcel Hénaff, *The Philosophers’ Gift: Reexamining Reciprocity* (English edition 2019), chapter 1, pp. 11–29, [publisher abstract](https://doi.org/10.5422/fordham/9780823286478.003.0002). Abstract only; full chapter unavailable. Hénaff describes Derrida's argument that the return or debt implied by a recognized gift compromises its purity. Secondary account, not direct reading of *Given Time*. This challenges the fiction that all observed transfers count as gifts.
- Christopher Small, 'Musicking — the meanings of performing and listening. A lecture', *Music Education Research* 1(1), 9–22 (1999), [publisher abstract](https://doi.org/10.1080/1461380990010102). Abstract only. Small locates musical meaning in relationships enacted through participation. The instrument below makes some narrow relationships configurable; it cannot reduce his social account to token exchange.
- Meredith Evans, 'Making care audible: Musical gifts and affective reciprocity in the clinic', *Feminist Anthropology* 7(1), e70038, 9 March 2026, [publisher HTML](https://doi.org/10.1002/fea2.70038). Abstract, introduction and conclusion consulted, not full ethnographic appraisal. Evans describes musical offerings in clinical care as invitations rather than compulsory reciprocation, and attends to forms of reciprocity that escape normative expectations of recognition. This is a counterweight to an apparatus forcing a response. No patient data copied, no clinical inference; this reading is outside the frozen review.

### Interpretation

Sound can be copied. The restriction that a motif belongs to exactly one site is a fictional compositional resource constraint, not an intrinsic property of information. Ownership here means exclusive rendering authority over a synthetic motif, not legal title. An instrument that makes every gift visible, accounted for and reciprocated may make the word gift inappropriate. A recipient must have the artistic option to refuse the apparatus. No combinatorial invariant adjudicates these philosophical positions.

## Exact synthetic construction

Let n >= 2 labelled seats form a directed cycle. Each initially holds its own distinguishable motif. Each directed edge i -> (i+1) mod n fires exactly once in a fixed permutation. Each firing transfers exactly one token; no copying or deletion. A seat can send its original or forward an already received token. If its outgoing edge fires before its incoming edge it must send its original. Every seat ends with one token.

Let F be the set of seats whose outgoing edge fires before their incoming edge. Both F and its complement are nonempty by strict cyclic ordering. Let K include F and any subset of its complement, representing seats sending originals. The rest forward the received token and retain their own.

**Proposition:** the number of distinct final labelled assignments for a fixed schedule is exactly 2^(n-|F|).

Proof: each flexible seat has its own token and exactly one arrival when it sends, so its binary options are independently feasible. Each original of a seat in K ultimately reaches the next seat of K along the cycle; seats outside K retain their own. For |K| >= 2 the non-fixed points of the terminal permutation identify K. For |K| = 1 the assignment is identity, and at most one singleton is admissible since F is nonempty. Distinct K therefore give distinct assignments. The bounds 2 and 2^(n-1) are attained by reverse and forward spatial sweeps respectively (coincident bounds at n=2). No claim about repeated transfers or arbitrary graphs.

The cardinality is not Shannon entropy absent a probability law. Given the schedule, n-|F| is the exact fixed-width bit count needed to identify a terminal assignment. This is elementary combinatorics, no priority claim.

For n=3 and schedule A->B, B->C, C->A, the final seat orders are abc, cba, bac, cab. With A->B, C->A, B->C only B has an option. Both schedules have identical aggregate directed transfer counts and initial/final quantities. The ordered edge ledger distinguishes schedules but not choices within them. Timing controls the availability of choice before sound is authored.

## Laboratory and score

Run python laboratory.py (standard library; executed Python 3.13.5). Enumerates all schedules n=2..7, direct token simulation versus next-K prediction, rejects impossible forwarding before arrival. Four original four-second stereo recordings share the same first-second transfer pulses, followed by original motifs and fixed seat-dependent gains (3,1), (2,2), (1,3). Integer samples conserve the unnormalized L+R signal exactly, because each motif has summed gain four regardless of seat. This is not acoustic energy conservation. Stereo signals differ; physical-room mixes and perception are not guaranteed invariant. No listening study.

See [laboratory.py](laboratory.py), [SCORE.md](SCORE.md), [RECEIPT.md](RECEIPT.md). Audio generated locally, not committed as binaries.

## Exaptation: The Circulation Organ

Design persistent motif tokens and relay sites, each with renderer, arrival buffer and policy (pass arrival, send local, offer and wait, decline). The edge scheduler controls which transfers can occur and when. Display independently the inventory, transfer events and provenance: fixed timing strip for receipts, spatial bus for actual motifs, optional timbre identifying transferred tokens. An artist can lock the first strip while editing the other two. Extend to a grid of agents, each with its own relay policy; do not assume the one-shot cycle proof still holds.

The most interesting extension breaks the model: an agent may decline an offer, leave a token silent or copy it. Refusal need not be failure. In human performance no compulsory response or participation; add independent audition, stop, amplitude bounds and lifecycle controls.

MHAC hypothesis: generic transfer acknowledgements may communicate movement without identity, or invite unwarranted inferences of acceptance. Compare synthetic receipt-only, identity-bearing audio and ordinary visual-list baseline; measure terminal identity reconstruction, false inference of acceptance, latency, inspection burden. Counterhypothesis: conventional explicit identifiers and status labels suffice. Distinguish offer, receipt, acceptance, custody and authorization. No claim that cybersemiotics improves on event sourcing is established.

## Checkpoint

Read live AGENTS, RAG, PROGRAMME, AGENT_RUNBOOK, RESEARCH_INTEGRITY, VALIDATION, protocol freeze and amendment index. Base 495a98ca12bae467a507031f04931aa4254b1866. Reviewed 65 recent PR titles and 50 open issue titles; searched sorites/family resemblance (overlap #197, abandoned), Condorcet (overlap #228, abandoned), Mauss, gift exchange, reciprocity (no issue matches returned), and adjacent themes. Distinct from #530 trajectory identity, #540 handoff windows, #516 deletion scars, #524 traversal: this is about relay latitude and object redistribution. Bounded search, not novelty proof. Fresh branch mhac-578/gift-returns-stranger. No shared files changed. Draft/HOLD for integration review and exact-head CI; full repository validation and human review not claimed.
