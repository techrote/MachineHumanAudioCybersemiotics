# The Constitution of the Instrument
*An instrument in which a vote changes what a vote can do.*

Independent exploratory humanities, artistic research and finite mathematics; 24 November 2026; AI-assisted original writing and synthetic software. Not a Track E or G result, evidence of listener response, normative political recommendation, or production control mechanism.

## The organ before the organ

A pipe organ has stops that change which pipes respond to a key. Imagine a second keyboard whose stops determine who is entitled to decide whether a key should sound. A third keyboard would determine who is entitled to change those entitlements. At what point does the organ cease being a device for producing music and become an institution that happens to produce music?

One can learn the first keyboard by practising. The second requires negotiation. The third requires a history: why is this rule in effect, and by what rule was it brought into effect? The musician who knows all the pitches but cannot answer that question knows the instrument acoustically but not constitutionally.

This is an interpretive construction, not a universal definition of music. A soloist with a violin need not consult a constitution. Nor is every social interaction a formal vote. The organ is an artificial object designed to make a neglected distinction palpable.

## Four disagreements, not one synthesis

Austin's lectures on performative utterances provide a starting point: a formula is not sufficient for a successful conventional act. His ninth lecture also differentiates several ways in which an illocution relates to effects. [A1–A2] A successful vote, audible confirmation and subsequent compliance need not be a single event. It would be a mistake to equate every emitted sound with a speech act; our vote is stipulated to have a procedural consequence, whereas the accompanying tone is an optional manifestation of that consequence.

Bourdieu's analysis presses from another direction. In the opening of his 1975 article, he challenges an account that would locate the efficacy of authorized discourse inside the utterance, detached from social use. [B1] In our imaginary organ, the question is not just whether the gate computes correctly but who got to place the gate there, whose participation is recognized and whether the ensemble accepts its authority. This does not mean Austin ignored circumstances. It means Bourdieu's sociological question cannot be answered solely by enumerating Austinian procedural conditions.

Derrida's intervention is different again. In his discussion of Austin's exclusions, he argues that citability is not simply an accidental threat to a normally pure performative; repeatability is integral to the possibility of recognizable acts. [D1] A recording of our fictional assembly could therefore become material for a new artwork or even an authorized new act under a different convention. This is not a proof that a software system cannot distinguish a live command from a recording. It is an objection to reducing the entire context of a sign to a single authentic origin. A replay restriction can be appropriate for a command and deeply inappropriate for an artwork.

Finally, Ono's instruction-based practice supplies a counterweight to an obsession with enforcement. A MoMA account of Grapefruit describes works that can be realized in imagination and beyond a conventional exhibition setting. [O1] The institution that makes a musical event possible can also be the institution that denies someone the right to experience it. An instruction might be an invitation to make something else, not an obligation to produce a specified material effect. Our explicit score must leave room for a listener to decline the game and still engage with the piece.

These positions do not resolve each other. A correctly implemented gate can be socially illegitimate; a meaningful replay can be institutionally invalid; an unexecuted instruction can be artistically realized. This is why the score offers three procedural conventions rather than appointing one as the correct theory of language.

## Nomic and musical amendment

Peter Suber's Nomic is a direct antecedent, not an analogy invented here. The appendix to The Paradox of Self-Amendment explicitly makes rule changes moves, permits changes to rules that authorize changes, and discusses the special character of voluntary games relative to law. [N1] The present work is a much smaller and deliberately less reflexive adaptation: the choice of ratification convention is fixed outside each session, while two thresholds may change inside it. It does not implement Nomic, solve the paradox of self-amendment, or claim priority for mutable rules.

The novelty sought here is artistic: make the distribution of rule-changing power an audible compositional medium. Musicians can play a concerto of coalitions without assigning a pitch to a political party. Their fundamental material is which procedural act makes a future tone possible.

A conventional synthesizer usually distinguishes a signal path from a modulation path. This organ adds a jurisdiction path. A control might select a pitch, modulate a filter, grant a player access to the filter, or change the procedure for granting access. The last two operate on the instrument's control grammar, not merely its audio parameters. A programmer can implement those operations as ordinary state updates; the interesting difference is what the participants agree those updates mean.

## An exact but deliberately tiny constitution

Let n be the fixed positive number of voters. Each voter may approve or not approve; all ballots are identified and synchronous, the identities do not change, and no adversarial delivery or strategic response is modeled. Let s and q in {1,...,n} be the current thresholds for sounding and amending. A sound ballot with c approvals produces a tone exactly when c >= s. An amendment proposes a new pair (s',r) and has c approvals. Rejecting leaves the pair unchanged; accepting changes both simultaneously.

We compare three *stipulated* meta-rules:

| Convention | Amendment accepted when |
|---|---|
| Incumbent / old | c >= q |
| Candidate / proposed | c >= r |
| Dual | c >= max(q,r) |

The candidate rule is an intentionally provocative fictional convention; it is not a recommended authorization system. The outer convention authorizes its use, so there is no logical paradox in this model. In particular, a proposal cannot change the convention itself. That is the hidden ceiling on all three constitutions.

**Witness 1: a single approval adopts a proposal (s',r)=(1,1) under the candidate rule from (s,q)=(2,2), but not under the other two.** Thus a proposal that fails the incumbent threshold can authorize itself under this convention. Sound now requires a single approval. The same ballot would have been silent beforehand.

**Witness 2: two approvals adopt a proposal (s',r)=(3,3) from (2,2) under the incumbent rule but not the other two.** If exactly those two continue to approve, they cannot undo their accepted amendment. This is a self-lock relative to a fixed coalition, not a claim of irreversible lock under every future vote: a third approval changes the situation.

**Witness 3: dual ratification is not a fairness cure.** A two-person majority in a three-person ensemble can change s to 1 while keeping q=2, even under dual ratification. The majority can also set s=3, enabling any one member to block a subsequent tone. The meta-rule constrains changes to amendment thresholds; it does not protect against every objectionable ordinary rule.

### A finite census and its derivation

For every ordered pair (q,r) of thresholds and every labelled binary ballot, there are n^2 * 2^n configurations. We intentionally include q=r and no-op amendments. For one ballot with c approvals, there are c(n-c) threshold pairs accepted only by the old rule and the same number accepted only by the candidate rule. There are c^2 accepted by both and (n-c)^2 rejected by both.

Summing over all ballots, each voter appears in half the ballots and each ordered pair of distinct voters appears together in a quarter. Thus the old-only and candidate-only counts are each n(n-1)2^(n-2), while both-accept and both-reject each equal n(n+1)2^(n-2). These expressions also evaluate correctly at n=1. Under uniform weighting over configurations (not a prediction about people), the two single-rule conventions disagree on fraction (n-1)/(2n), approaching one-half as n increases.

The two conventions have the same aggregate acceptance rate, one-half, under this symmetric census. Equal rates hide exactly the disagreement we care about. Dual accepts fraction (n+1)/(4n); rejecting more proposals is not necessarily better governance.

### Reachability with a fixed coalition

Fix c throughout the session, with all outsiders voting no and every threshold proposal available. Consider just q, the amendment threshold; the sound threshold can be included freely in any accepted proposal.

- Incumbent: from q<=c, all n amendment thresholds are reachable in one step. Each q>c is absorbing relative to this coalition.
- Candidate: from any initial q, all r<=c are reachable in one step; the initial state itself is reachable by doing nothing. No new threshold above c is reachable.
- Dual: if q<=c, precisely the thresholds r<=c are reachable; if q>c, the only reachable state is the initial one.

Proof: read the transition condition for each mode. The stated sets contain their initial state and are closed under the respective transitions; each additional listed state has a direct accepted edge. This gives both directions without induction over unbounded proposal sequences. The executable oracle independently uses breadth-first traversal for each n<=8, q, c and mode; see RESULTS.md.

Dual prevents both specific mechanisms (self-ratification by a coalition initially below q and the fixed coalition's voluntarily raising q above its own strength), but it also prevents a majority from deliberately entrenching future consensus requirements in the latter way. The ability to bind oneself is not always a flaw. The model refuses to choose a normative objective.

## An original performance: constitutional counterpoint

Three performers with voting tokens, one timekeeper, one tone generator. All can stop at any time, without penalty; no actual permission outside the artwork is granted or revoked. The instrument's free-standing browser realization is in instrument.html. A paper performance requires only three people, a ledger and a quiet instrument.

First perform the same eight vote events in three separate sessions (one per meta-rule). Start at (2,2). A alone proposes (1,1); A alone requests a tone; A and B propose (3,3); A and B request a tone; A and B propose (1,1); A requests a tone; all three propose (2,2); B and C request a tone. At each round allow time for the vote, record before/after thresholds and whether the vote was accepted, and render only sound votes as a tone or rest. The amendments are inaudible by convention. Now perform the ledger aloud after the music has ended.

In the second movement, give performers the right to propose their own ballot sequences. Ask them to preserve a disliked rule long enough to learn what it affords another performer. Then allow the same group to compare the three meta-rules, choose one, or abandon the instrument. This invitation is deliberately outside the implemented finite model.

A third movement could use two rooms with the same score but different ratification conventions. After the first six rounds, exchange the ledgers without exchanging the recordings. Play a final sequence in a way that quotes the other room's acts. A quoted refusal can be musically productive without having the original procedural force.

The piece makes a distinction between constitutional counterpoint (relations among authorized futures) and acoustic counterpoint (relations among sounding events). The former is a proposed artistic term for this project, not an established musicological category.

## Objections and useful failures

Why turn democratic procedures into music? Because a machine's permissions are often buried in a config panel, whereas its results are immediately audible. Art can make the missing mediation available for inspection. But this argument risks instrumentalizing democratic practice as entertainment, so the toy must not stand in for real participation, citizenship, coercion, legitimacy, disability access or collective action. A fixed electorate with equal numerical ballots abstracts almost everything about those subjects. It can even conceal unequal influence over which amendments reach a vote.

A note that sounds need not signal assent. A tone might be an alarm about an unjust result; the same silence might be welcome, imposed or a technical failure. In the score, a failed sound generator does not undo a ballot. In a real interface, authorization must not be conferred by acoustic resemblance. These are engineering constraints, not listener-study findings.

The experiment itself has a pointed institutional problem. The three labelled voters in a single browser are controlled by one user. The browser does not enact a collective decision; it permits rehearsal of one stipulated procedure. Paper performance by actual people would be artwork, not an experiment producing empirical evidence without the programme's gates.

## Exaptation: jurisdiction as a modulation source

A future musical environment might contain three separate editors: a DSP graph; a control/affordance graph; and an amendment graph defining who can change the control graph and when. Changes to the latter could be logged and auditioned as first-class events. A reversible rehearsal branch would let an ensemble hear the consequence of an amendment before deciding whether to adopt it. The branch is not the adopted constitution.

For MHAC, consider a machine saying "approved" after a calculation. The message should distinguish a proposal, a recorded ratification, its governing rule version, the effective time of the change and an observed consequence. An authoritative decision can exist without a confirmation tone, and a perfectly intelligible tone can occur without a decision. The design candidate is a version-bound procedural receipt, not a claim that all listeners benefit from additional narration. In a nonconsequential setting a simple cue may suffice. Test the added cost of verbosity against actual action and comprehension only under an authorized protocol.

The most interesting extension is a score in which participants can change the very meaning of an instrument control, but the musicians retain a route to contest the new mapping. In software, this suggests versioned, inspectable interaction contracts rather than unannounced reassignment. In art it suggests an instrument whose characteristic sound is not its timbre but the history of its negotiated possibilities.

## Source locators, access and boundaries

All consulted on 24 November 2026 by a ChatGPT agent; no human or independent scholarly review. The following are bounded readings and discovery, not canonical source records. No original source text has been copied into the repository.

- **A1:** J. L. Austin, *How To Do Things With Words*, second edition (1975), Lecture II, pp. 12–24, [publisher abstract](https://doi.org/10.1093/acprof:oso/9780198245537.003.0002). Abstract retrieved in search response; direct chapter retrieval returned HTTP 500. No full chapter claimed. Secondary cross-check: [SEP, Speech Acts, §2.2](https://plato.stanford.edu/entries/speech-acts/#CanSayMakItSo) (2020 revision); section read in search result. Austin's theory is not reduced to its early performative/constative distinction.
- **A2:** Austin, same edition, Lecture IX, pp. 109–120, [publisher abstract](https://doi.org/10.1093/acprof:oso/9780198245537.003.0009). Abstract retrieved; direct fetch failed. The distinctions are reported only at abstract-level resolution.
- **B1:** Pierre Bourdieu, "Le langage autorisé: Note sur les conditions sociales de l'efficacité du discours rituel", *Actes de la recherche en sciences sociales* 1(5–6), 1975, pp. 183–190, [Persée](https://www.persee.fr/doc/arss_0335-5322_1975_num_1_5_2488), DOI 10.3406/arss.1975.2488. Opening printed p. 183, paragraphs following the Austin epigraph, read in French HTML OCR; epigraph OCR damaged and not quoted. [Bibliographic summary](https://bourdieu.name/fr/node/653) also consulted; full article not read. Interpretive English paraphrase, not translation quotation.
- **D1:** Jacques Derrida, "Signature Event Context", in *Margins of Philosophy*, Alan Bass trans., pp. 307–330. [Stanford-hosted transcription](https://web.stanford.edu/class/history34q/readings/Derrida/Derrida_Signature_Event.html), printed pp. 324–326, passage from Austin's theatrical exclusion through the argument about the repeatable formulation of a performative. Read passage-level HTML with OCR noise; no full-volume claim. This is a critical position, not an empirical security result.
- **O1:** Whitney Rose Graham, [MoMA, "Happy (Belated) Birthday to Yoko Ono's Grapefruit"](https://www.moma.org/explore/inside_out/2015/07/15/happy-belated-birthday-to-yoko-onos-grapefruit/), 15 July 2015, body paragraphs beginning with the 1964 self-publication and the discussion of distribution. Museum commentary read, not the whole 1964 book. Museum's empowerment interpretation is not independently verified participant experience.
- **N1:** Peter Suber, [Nomic: A Game of Self-Amendment](https://constitution.org/2-LawRev/psuber/nomic.htm), appendix 3 of *The Paradox of Self-Amendment* (1990), Introduction, particularly the discussion of legal tiers, self-application and the contrast between games and law; Initial Set rules 103, 114–116. Relevant passages read in HTML mirror. No copying of the game rules; the two-threshold score is an original constrained adaptation. The toy's fixed meta-rule is an explicit departure.

## Reconciliation and execution

Main inspected at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity and validation. Latest PR and open-issue searches show concurrent expeditions on time geometry, audit randomization, causal filters, ordinal calibration and others. Searches for speech act, authority, replay and branch names were checked. Related issue bodies #43, #56, #62, #205, #238, #242 distinguish existing action authority, retraction, claim warrant, choice and coalition relationships, and strategic signalling respectively. This expedition asks how amendment of future decision rules is authorized, in an explicitly voluntary artwork. Nonduplication is scoped to the inspected results, not an exhaustive novelty audit. Target issue #262 read after creation; no comments at inspection. No changes to shared files or accepted claims.

Local finite function execution is recorded in RESULTS.md; browser UI/audio hardware untested. The model is deterministic and synthetic. A dedicated independent implementation, repository CI and review remain separate from the mathematical argument and the work's aesthetic value.
