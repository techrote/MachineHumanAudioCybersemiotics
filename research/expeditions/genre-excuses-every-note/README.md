# The Genre That Excuses Every Note

*An expedition in aesthetic categories, musical expectation and retrospective explanation.*

**Status:** original exploratory essay and finite synthetic model, 2026-11-24. Refs #310. AI-assisted research and self-review; no independent human review, no empirical listener data, no priority claim. This is not a Track E extraction or accepted Track G synthesis.

## 1. A critic with a switch

A machine plays the same note six times. One critic hears the persistence of a drone; another hears a failed melody. A third hears a ritual in which the expected change has been withheld. The acoustic object does not settle the disagreement. But neither does the disagreement imply that every description is equally instructive.

Imagine an unusually obliging critic who switches aesthetic categories immediately before every difficult note, having already heard the entire performance. Every deviation becomes exemplary of some other practice. A work that initially appeared full of transgressions is transformed into a succession of perfectly conventional events. The critic has not necessarily discovered a new unity; they may have spent the entire explanatory budget manufacturing exceptions.

I propose **category counterpoint**: the composition of competing frames of intelligibility alongside a fixed sequence of sounds. A frame can be as much a part of the score as its notes, but a frame announced before an event is a different kind of commitment from one supplied afterwards.

The qualification matters. Art does not owe us statistical prediction. Retrospective interpretation can be insightful, historically warranted and structurally revealing. The following finite experiment concerns the narrower claim that a collection of retrospectively selected probability models is not automatically a probability model.

## 2. Source encounters and resistant readings

**Danto, Arthur C. (1964), “The Artworld,” Journal of Philosophy 61(19), 571–584.** [Stable bibliographic record](https://www.jstor.org/stable/2022937); [accessible text](https://www.academia.edu/31026000/The_Artworld_Danto). Read the opening argument, printed pp. 571–573, not a comprehensive reconstruction of the article. Danto argues that an artistic theory may do more than identify objects already recognized as art: it may make new artistic practices intelligible. His examples of conceptual change complicate the assumption that looking harder at the object alone will suffice. My interpretation: an instrument can expose the rules by which a gesture becomes intelligible, rather than merely exhibit the gesture. Counterpoint: an arbitrary post-hoc label is not equivalent to a historically established art practice.

**Walton, Kendall L. (1970), “Categories of Art,” Philosophical Review 79(3), 334–367.** [Author's university bibliography](https://lsa.umich.edu/philosophy/people/emeritus-faculty/klwalton/Categories-of-Art.html), [secondary discussion, SEP, §2.1 Aesthetic Objects (discussion of formalism)](https://plato.stanford.edu/archives/sum2017/entries/aesthetic-concept/). Bibliography verified; primary full text not established. The SEP discussion locates Walton's thought experiment about Guernica at p. 347: the same surface could be encountered under a different artistic category in which flatness has a different significance. It also distinguishes his claims about perceived qualities from questions about appropriate categorization. Do not infer from this that rarity is the definition of a contra-standard property, or that artistic categories are freely interchangeable. The toy model below is explicitly narrower than Walton's aesthetic account.

**Pearce, Marcus T. (2018), “Statistical learning and probabilistic prediction in music cognition: mechanisms of stylistic enculturation,” Annals of the New York Academy of Sciences 1423(1), 378–395.** [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849749/), DOI 10.1111/nyas.13654. Read abstract, Introduction, Statistical learning and predictive processing, and IDyOM opening paragraphs. Pearce proposes that exposure to musical styles supports learned probabilistic expectations and discusses variable-order models of musical events. This is a theory and review of modelling work, not direct validation of our artificial listener. IDyOM is richer than the two fixed Bernoulli laws below; the latter contain no human training, memory or neural mechanism. A useful resistance: uncertainty over what a listener expects is not the same as uncertainty within a single stipulated model.

**Liu, Ziyi, Idan Attias and Daniel M. Roy (2024), “Sequential Probability Assignment with Contexts: Minimax Regret, Contextual Shtarkov Sums, and Contextual Normalized Maximum Likelihood,” NeurIPS 37.** [Conference abstract](https://proceedings.neurips.cc/paper_files/paper/2024/hash/19a94fdf9e1c5b387830e4c4fef6972a-Abstract-Conference.html), DOI 10.52202/079017-0448. Abstract only. Establishes the relevant literature connection to Shtarkov's earlier minimax-regret result and contextual extensions. Our elementary finite proof below is independent of those more general results; no claim of novelty for NML.

**Brisson, Romain and Renzo Bianchi (2021 online; volume 50, issue 4), “Perception of the usability of music-genre labels for the assessment of musical tastes.”** [Article](https://doi.org/10.1177/03057356211046660). Read abstract and Discussion; their exploratory student survey concerns the usability of genre labels for taste reporting. This supplies a reason to distrust casually assigned genre categories, not evidence of effects of labels on auditory perception. No extracted empirical estimate is imported into MHAC's corpus.

These positions should not be collapsed. Danto's concern with the constitution of art, Walton's concern with category-relative aesthetic properties and Pearce's probabilistic account of expectation are not interchangeable. A historian can object to a statistically excellent but anachronistic reading; a listener can be surprised by an historically conventional passage; and an artwork can deliberately cultivate both effects.

## 3. Exact synthetic model: the price of a perfect excuse

Start on note A. Each subsequent event is either a repetition (0) or a change to the other note (1). The transition word determines the whole acoustic score, given the initial note.

Grammar R assigns probability 3/4 to repetition and 1/4 to change; grammar C reverses these. Both assign positive probability to every word. A path g of n grammar choices is declared in advance to specify a normalized probability distribution P_g(w). At most k switches between adjacent positions are allowed. A switch costs nothing in the likelihood; it is instead restricted by the model class.

For a word w, let d_k(w) be the minimum Hamming distance to a grammar path with at most k switches (R encoded 0, C encoded 1). Then the best retrospective likelihood is M_k(w)=3^(n-d_k(w))/4^n. A dynamic program maintains the minimum mismatch count for each final grammar and allowed switch budget. At each event either retain the previous grammar or change it using one unit of budget. Induction on the prefix length proves exactness.

Two transition words 00001111 and 01010101 have identical repetition/change counts. The first is fitted perfectly with one switch, the second requires seven. With a single fixed grammar both incur four mismatches. A retrospective interpretation can therefore differ substantially without any change in the aggregate event histogram.

However, M_k is not generally normalized. Put Z_k=sum_w M_k(w). If Q is any normalized distribution over words and all ratios M_k(w)/Q(w) were strictly less than Z_k, summation would imply sum Q>1. The distribution Q*(w)=M_k(w)/Z_k attains the bound at every word. Thus the exact worst-case pointwise log-loss regret against the retrospective oracle is log2 Z_k. This is the finite normalized maximum likelihood (NML) construction, not a psychological theory. The block distribution can be factored into prefix conditionals for a known horizon; this does not grant a real-time listener access to the future word.

For k=0, Z_0=4^(-n) sum_j binom(n,j)3^max(j,n-j), lying between 1 and 2. As n grows, the two iid laws concentrate on opposite sides of n/2, so Z_0 approaches 2; the cost of allowing one unknown fixed grammar approaches one bit. For k=n-1, every event can be fitted to its preferred grammar and Z=(3/2)^n, so regret is n log2(3/2). Intermediate budgets are enumerated in [RESULTS.md](RESULTS.md). A union bound gives Z<=2 sum_{j=0}^k binom(n-1,j) because the maximum is no larger than the sum over paths. Z is nondecreasing in k.

At length 12 the fixed-category regret is 0.949606 bits; permitting one retrospective switch increases it to 3.054377 bits; unrestricted switching raises it to 7.019550 bits. The latter makes Q* uniform: the perfectly accommodating critic has achieved the same best-fit likelihood on every possible score, thereby losing all discrimination between them.

The executable [lab.js](lab.js) enumerates all 8,190 nonempty binary words up to length 12; a direct enumeration of grammar paths cross-checks 510 words up to length 8. It verifies reversal/complement symmetries, integer mismatch bounds, exact fit thresholds, fixed and unlimited normalizers and class-size bounds. 303,714 assertions passed in the authoring isolate; the uploaded source text was retrieved and compared exactly. This is synthetic mathematical qualification only. The same agent wrote and checked the model.

## 4. Where the analogy should break

A low-probability event can be entirely appropriate within a genre. A high-probability event can be beautiful, tedious, ominous, or unnoticed. Walton's categories include conventions and histories not reducible to marginal frequencies. A new category need not have been stated before the work existed. An art practice that insists on prior declaration of every interpretive innovation may merely turn criticism into bureaucracy.

In the model, the grammar switch is a change in a stochastic law. In the essay, a frame may also be an invitation, a remembered association, a social convention, a fictional instruction, a historical attribution or an ethical judgment. It would be a category error to identify all those things with the switches of a Bernoulli model.

Nor does the regret number measure aesthetic worth. A critic can have excellent reasons for switching categories seven times. The calculation simply states the normalization cost if their retrospective likelihood is presented as if it were a single predictive probability distribution.

The stronger aesthetic idea is not that explanations should be cheap. It is that **explanations should reveal what they have committed themselves to, what they have revised, and what they have declined to explain.**

## 5. Exaptation: the Category Counterpoint instrument

Build a two-lane instrument: a raw score (MIDI, grains, CV events) and an independently editable grammar lane. The grammar lane supplies a predictive distribution and an explicit time stamp for when each declaration was made. A monitor calculates surprise from the declared model, not from an invisible retrospective optimizer. A separate retrospective audition exposes alternative segmentations and their switch budgets. A third lane may sonify disagreement among candidate models, never presented as a direct measurement of a human listener's feelings.

The raw score is invariant when the analyst edits the interpretation lanes. A sound bank can deliberately be composed against two opposed conventions; the conductor selects which frame is currently announced while a second performer supplies deviations. For a more ambitious implementation, learn style models from consensually selected material, permit nonbinary alternatives and expose both within-model entropy and disagreement across models. Avoid opaque genre labels; display operational model constraints, training scope and confidence separately.

MHAC transfer: a diagnostic alert scored as probable under a maintenance model and improbable under a normal-operation model should expose which baseline was declared, when it changed and whether the model was selected before or after the event. A context switch may be fully justified; logging it makes revision auditable. Do not interpret low probability as danger or high probability as safety. Test design (unexecuted): synthetic paired histories with identical sound, one genuine predeclared context change and one retrospective reclassification. Measure whether explicit model-version and effective-time cues help distinguish forecast from retrospective explanation, controlling workload, training and base rates. Actual participants remain gated.

See the original [performance score](SCORE.md). No production synth, browser rendering, participant experiment, external review or empirical claim is delivered.

---

**Checkpoint.** Live main inspected at 495a98ca12bae467a507031f04931aa4254b1866, plus AGENTS, RAG, programme, runbook, research integrity, validation, frozen protocol record and amendments index. Reviewed 70 recent PR titles and 50 open issue titles for overlap: the Refrain That Exhausts Itself treats recurrence; the Clock That Borrows a Memory treats temporal dependence; the Licensed Glitch treats protected class variation. This expedition addresses category-relative explanation and the explicit cost of retrospective model selection instead. Branch mhac-310/genre-excuses-every-note, new issue #310 (no comments at creation). Four additive files only; no canonical registry or protocol edits. Branch left for exact-head integrity and independent review; no claim of completed programme acceptance.
