# The Silent Coauthor

*An instrument whose contributors cannot be counted by listening to them individually.*

**Status:** exploratory humanities / original finite mathematics / sound art. Not a Track E or G finding, human evaluation, or production design. Issue [#238](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/238).

## The author as a position in the machine

Suppose four people stand before four keys of an organ. None can play alone. Every group of three can sound a note, as can the full quartet. One person is appointed indispensable because they have never been heard in isolation. Another is declared dispensable because the organ still sounds when they leave. Both arguments fail even as engineering accounts of the instrument.

Two organ mechanisms are possible. In the first, two-player music is possible only when A is present. In the second, two-player music is possible only when A is absent. Their solo auditions, full ensemble recordings, and every leave-one-out audition are identical. This is not a dispute about vague timbral similarity. Under the specified synthesis rule the complete digital recordings are identical. What differs is the counterfactual architecture of cooperation.

The idea grew from reading the accessible English excerpt of Foucault's 1969 “What is an Author?” (1977 translation, pp. 124–127 as identified by the host; [source](https://foucault.info/documents/foucault.authorFunction.en/)). The first three features discussed there concern appropriation, historical variability in the assignment of authors, and procedures that construct an author from a body of discourse. His third feature is particularly provocative: a constructed author can be made to account for coherence across disparate works. The excerpt is not a treatise on synthesizers, AI authorship, or cooperative games. Its historical generalizations should not be imported as established facts; the author himself qualifies one of them. The original lecture as a whole was not read in this expedition.

A possible interpretation is that an attribution system partly constructs its own object. When a music label, a DAW, an AI evaluation or a research archive identifies a contributor, its choice of what counts as a contribution helps determine what it will subsequently recognize. A name may designate a physical performer, an institutional role, a person responsible for a decision, an originator of an idea, an owner, or an allocation recipient. These are not synonyms.

The quantitative model below deliberately narrows the problem to a value function. It has no account of artistic intention, historical labor, consent or economic rights. This limitation is productive: it makes it possible to exhibit how little even a fully specified, exact attribution rule can establish about the institution that surrounds it.

## The four-key instrument: exact finite result

Let N = {A,B,C,D}; a coalition S is the set of enabled controls. For every coalition of size 0 or 1, define v(S)=0. For every coalition of size 3 or 4, define v(S)=1. Each of the six unordered pairs independently has value 0 or 1. Thus there are exactly 2^6=64 distinct monotone Boolean games, represented by a simple graph whose edges are the sounding pairs.

All 64 agree on the ten non-pair coalitions. In particular the full-ensemble removal score v(N)-v(N minus {i}) is zero for each i, as is every solo score. Every complete ordinary solo / master / leave-one-out audit therefore gives exactly the same result. The combined audio is a fixed original gated pulse, not a sum of performer stems.

Choose the conventional Shapley allocation: the uniform average of the incremental value added by a player over the 24 possible joining permutations. This is an explicit allocation convention, not a theory of legal or moral desert. Shapley's 1952 RAND paper landing page [P-295](https://www.rand.org/pubs/papers/P295.html) confirms the axiomatic historical precursor; the 1953 chapter [publisher record](https://doi.org/10.1515/9781400881970-018) confirms the publication, but its full text was not available. The permutation definition used here is stated explicitly in this report and in accessible teaching expositions; we do not claim to have read the original proof or reinvented the value.

For player i let d_i be its graph degree and m the total number of edges. Only two sizes of predecessor coalition contribute: a single other player, for which the marginal is one if the resulting pair is an edge; or a pair not containing i, for which the marginal is one if that pair is not an edge. Each particular predecessor set of either size occurs in 2 of the 24 permutations (2!1! or 1!2!). There are d_i successful pairs containing i and 3-(m-d_i) nonsounding pairs outside i. Therefore

    phi_i = (3 + 2*d_i - m)/12.

The formula is exact. Each of the six conditions contributes either zero or 1/12. The sharp range for any fixed player is [0,1/2]; its maximum occurs in the three-edge star centered on that player, its minimum in the complementary triangle not containing it. The allocations for A-centered star and triangle are respectively (1/2,1/6,1/6,1/6) and (0,1/3,1/3,1/3). In the triangle A is a dummy in the precise game sense, not a person whose artistic work is necessarily worthless. In the star A is not a veto player: the three others together still produce sound. No player is indispensable to the grand coalition.

A stronger result concerns identifying the allocation. Suppose an exact deterministic interrogator can query v(S) for one coalition at a time. Each unqueried pair can be independently flipped while holding every response given so far fixed; its flip changes each player's allocation by either plus or minus 1/12. Consequently the entire credit vector is not determined until all six pair values are known, even if the interrogator chooses questions adaptively. Query all six and the formula supplies the vector: six is necessary and sufficient. This does not cover arbitrary group queries, probabilistic estimation, or extra structural priors.

### The allocation itself forgets

Let x = e_AB - e_CD, y = e_AC - e_BD, z = e_AD - e_BC. Here each e is a Boolean edge indicator. In coordinate order A,B,C,D the allocation is the uniform quarter plus

    (x*(1,1,-1,-1) + y*(1,-1,1,-1) + z*(1,-1,-1,1))/12.

The three vectors are orthogonal, so the triple (x,y,z) uniquely determines the allocation, and the allocation determines the triple. Each difference independently has three possible values (-1,0,1). There are precisely 27 possible allocation vectors. For any difference of zero there are two indistinguishable underlying pair assignments, while a nonzero difference has one. A vector with k zero differences therefore has 2^k distinct underlying graphs. The resulting class counts are eight singleton classes, twelve classes of size two, six classes of size four, and one class of size eight.

That last class is the uniform allocation. It includes the empty graph (no duet works), complete graph (every duet works), three perfect matchings and three four-cycles. Eight instruments receive the same apparently equitable four shares while differing in the possible relations between performers. Even a fully verified value allocation is not an invertible account of the mechanisms that generated it.

## The composition: permission before sound

This score turns the six possible relationships into compositional parameters. A conventional patch changes oscillator shape, frequency or amplitude. Here the waveform is fixed. The mutable object is the set of coalitions permitted to sound it.

The original WAV score consists of two audition movements for each graph: ten routine coalitions (empty, four solos, four trios, ensemble) and six pair coalitions in AB AC AD BC BD CD order. Each slot comprises an enveloped 400 Hz square pulse or zero samples, followed by 50 ms silence. The routine scores are byte-identical for star and triangle; the pair scores are complementary. This is a demonstration of the declared gate, not a simulation of physical instrument mechanics, perceived contribution, or a human listening experiment.

An alternative musical lens is Philip Thomas, “Understanding Indeterminate Music through Performance: Cage's Solo for Piano” (2013, [publisher abstract](https://doi.org/10.1017/S1478572212000424), pp. 91–113 metadata). Thomas describes how performers' realization of indeterminate scores can produce a kind of understanding different from that of non-performers. Only the abstract was accessed; no claim about particular Tudor performance techniques follows. The relevance is conceptual: our instrument allows a player to discover its interaction grammar by playing, not only by reading a score or auditioning a recording. Unlike Cage's work, the gate is deterministic and finite. It is not an attempted realization of Cage.

A further artistic exercise would give players private access to keys but not the graph. They could negotiate which pairs work, change a graph edge, or deliberately refuse to disclose a working pair. The new composition would be the evolving social protocol around the note. This is a proposed artistic research task, not evidence of any participant's subjective experience.

## Exaptation: the coalition patch bay

Rather than only providing independent audio channels, a modular instrument might expose a six-edge editable interaction graph. Each edge gates a duet; three or four held keys always sound. A single tone then becomes a probe of cooperation. An inspector displays both the intervention table and the chosen allocation, including alternative graph witnesses consistent with the available probes.

For a general four-control patch, the user should select an objective before computing allocations: note-on, pitch error, RMS energy, spectral centroid, target-distance reduction, latency, etc. They may produce inconsistent rankings for the same sound. Baseline and mute semantics must be specified; an effect bypass is not necessarily a physical intervention removing a performer or their work. Interactions can be negative, and real nonlinear patches can violate monotonicity. This toy does not license transferring its sharp bounds to arbitrary DSP.

Possible MHAC applications include testing whether one-variable ablation hides dependencies among alert fields, or whether a responsibility display is silently using the wrong objective. A reproducible model of all coalitions may justify a particular allocation under its explicit assumptions. It cannot establish decision authorization, causal responsibility, copyright ownership or deserved acknowledgement. An allocation UI ought to expose its question, model, intervention and loss of information.

A useful contrary case: for an additive value v(S)=sum of w_i for i in S, every marginal is exactly w_i; solo auditions then suffice and the leave-one-out differences agree. The present failure requires an interaction structure outside that additive class. Likewise, if one knows in advance that all pairs sound, there is no six-question identification problem. The hypothesis is not that attribution is always impossible.

The immediate next artistic experiment is a pair-controlled patch with a continuous output function and separate effect morphs for different edges. The immediate methodological extension is interval-valued allocations when only some coalition outcomes are known; in this toy the bounds can be computed without assuming a distribution on unobserved pair bits. The observed graph itself is not an author.

## Speculative afterword: The Fourth Hand

The municipal organ had been commissioned by four citizens, although none of the surviving programmes specified which citizens had done the commissioning.

Every anniversary four hands descended on its keys. The note was immaculate. Each citizen was asked to leave the stage in turn, and the note did not change. Each was subsequently asked to perform alone, and the organ was mute.

The city abolished the names of the performers from the programme. This was judged a victory for mathematical equality.

A child approached the abandoned organ after the ceremony. She pressed one key and asked her sister to press another. The instrument sounded. They changed keys and it fell silent. When the custodian arrived, both were crouched under the console writing down the names of pairs, rather than the names of people.

The city held an inquiry. It found that the names had been removed from the programme correctly, according to the agreed algorithm. It found no error in the recordings and no error in the arithmetic. It was impossible, however, to repair the omissions without asking questions the programme had never authorized.

A second organ was installed the following year. All its pairs worked. Its attribution plaque was identical to that of an organ whose pairs never worked. Both were registered as equally cooperative.

The child became the city's first composer of permissions. Her scores were sheets of blank paper on which she had written the circumstances under which someone else might be permitted to make a mark. She signed none of them. The city's archivist recorded her absence as a contribution of zero.

The archivist was not unkind. He had been given a number and told it was a name.

---

Sources and execution details are in [EVIDENCE.md](EVIDENCE.md). The runnable laboratory is [lab.py](lab.py). The present report and audio are original AI-assisted exploratory artifacts; no new research participants, external review, canonical evidence, empirical synthesis or license grant is asserted.
