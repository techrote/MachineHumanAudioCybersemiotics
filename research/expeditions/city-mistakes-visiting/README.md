# The City That Mistakes Passing Through for Visiting

**Exploratory humanities / artistic research, 2026-11-26. Refs #742. Draft/HOLD.** Not a finding of the frozen MHAC research protocol. AI-assisted source reading, original interpretation, synthetic mathematical verification and composition by ChatGPT; no human participants or independent review.

## A city that has composed its visitor

A municipal synthesizer contains six rooms: a central interchange and five peripheral workshops. Every workshop has an equally intricate sound. You may leave a workshop only through the interchange. The curator turns on an unbiased random navigator: at every junction, give all available exits the same chance.

After a long visit the curator discovers that half the piece is the interchange. She decides that the interchange must have the most compelling sound.

The architect protests: the composition was made by the doors, not by the visitors' preferences.

An equal chance at every local choice does not imply an equal share of global experience. Even a completely indifferent navigator can create a highly repetitive composition. A musician could therefore compose the arrangement of doors independently of the sounds behind them.

A second curator changes the clock. The visitor spends five times as long in each workshop as in the interchange. Now the six rooms receive equal time, but the route still passes through the interchange between every pair of workshops. The same place can be musically dominant under one measure and ordinary under another.

A third curator exports only changes of room. The new equality vanishes from the recording. Nothing about the route has changed: the editor removed the time spent remaining.

## Source-located encounters

* **Guy Debord**, [Theory of the Dérive](https://theanarchistlibrary.org/library/guy-debord-theory-of-the-derive), originally November 1956, reprinted 1958, Ken Knabb translation. Passage-level reading: opening paragraphs through the discussion of surrealist wandering and tadpoles. Debord distinguishes playful drifting from ordinary strolling and explicitly argues that chance can restore habit instead of liberating movement. He situates attractions and barriers in a social and spatial terrain. The source is a translated online transcription, not an inspected original French edition. No empirical validation of psychogeography is inferred. The star graph below is an analogy, not a model of his political programme.
* **Max Neuhaus**, [LISTEN, artist's retrospective text, archive 1988–1990](https://www.max-neuhaus.estate/en/bibliography/publications/max-neuhaus-listen-1990), paragraphs beginning with the account of the first independent work, the first performance, and the lecture demonstrations. Neuhaus explains his dissatisfaction with importing everyday sound into concert spaces and describes taking an audience outside instead. The initial walk deliberately followed an itinerary; the exercise was not random wandering. The artist's recollections of audience responses are autobiographical testimony, not a controlled listening study. Estate-hosted HTML read at passage level; no recording auditioned.
* **Hildegard Westerkamp**, [Soundwalking](https://archives.locusonus.org/dropbox/coordination/txts_docs/divers_phonographie_soundscapes/Westercamp/Westerkamp_Soundwalking.pdf), Sound Heritage III(4), 1974, revised 2001; opening passage through the instruction to attend to bodily sounds. The revised PDF's extracted opening text was read; page-image retrieval failed, so no visual verification claimed. Westerkamp permits a soundwalk to concentrate on a small area or even a single place. Her practice supplies a counterargument to equating movement with exploration. Her general physiological statements are not adopted as scientific evidence, and her historical practical suggestions are not presented as contemporary safety guidance.
* **Elias Koutsoupias**, [Probability and Computing, Oxford 2016–17](https://www.cs.ox.ac.uk/people/elias.koutsoupias/pc2016-17/lectures.html#random-walks-on-undirected-graphs), lecture 14, sections Stationary Distributions and Random walks on undirected graphs. The theorem and proof of the degree-proportional stationary distribution were read, along with the preceding discussion of periodicity. Mathematical prior art: this is established elementary Markov-chain theory, not an original theorem of psychogeography.

**Interpretation:** Debord asks why some routes recur even when practical destinations are suspended. Neuhaus asks what happens when the site of listening changes. Westerkamp gives a reason to stay in a place rather than cover more distance. Their activities are not reducible to a sampling algorithm. Nevertheless, the three questions make an interesting musical instrument possible: its primary parameters might be passage, duration and attention instead of pitch, envelope and timbre.

There is also a political caution. A graph of a real city can omit inaccessible routes, housing costs, surveillance, histories of exclusion and bodily effort. A uniform stochastic policy does not make the city just. An artist can use topology as material without adopting mathematical equality as a normative description of civic life.

## Synthetic laboratory: two clocks of a star

Take a star with hub H and k leaves. On leaving H, choose one leaf uniformly. From a leaf, return to H with probability q per tick and otherwise stay. Assume k >= 2 and 0 < q <= 1. This is a finite irreducible chain; q=1 is periodic, so distinguish stationary occupation and long-run time averages from pointwise convergence.

Detailed balance: each leaf has stationary mass pi_L satisfying pi_H/k = q pi_L. Normalization gives

    pi_H = q/(1+q)
    pi_L = 1/[k(1+q)]
    P(move at a stationary tick) = 2q/(1+q).

At q=1, H takes half of all time, each leaf 1/(2k). At q=1/k, all k+1 states have equal time occupation, and only 2/(k+1) of ticks contain changes of room in stationarity.

Crucially, the jump chain (retain only changes of state) is identical for every q. Its arrivals are half hub, half leaves collectively. This follows because a leaf can only return to H, while each H departure selects a uniform leaf. The stationary distribution of arrival destinations is therefore (1/2, 1/(2k), ..., 1/(2k)), irrespective of the holding parameter.

There is a sharp constraint even without assuming symmetric transition probabilities: on the star, stationarity implies incoming and outgoing hub movement rates agree; with uniform occupation the hub can leave at most 1/(k+1) per tick. Every non-self movement has exactly one hub endpoint, so total movement rate cannot exceed 2/(k+1). The above symmetric policy attains that bound. It is a stationary bound, not a finite-path bound with arbitrary endpoints. Uniform time cannot be purchased with uninterrupted motion on this graph (k>1).

The proof does not say that a long finite random run will contain exact proportions; nor does equal dwell imply equal perceptual salience.

## Original composition: Three Tours of an Interchange

Let H have 110 Hz, the five workshops 165, 220, 277, 330, 415 Hz. Each tick is an independently enveloped quarter-second tone with a third harmonic. The fixed cyclic paths below are deterministic illustrations, NOT sampled Markov trajectories.

* Transit: H A H B H C H D H E. Five hub ticks, one for each workshop; 2.5 seconds.
* Dwelling: H A A A A A H B B B B B ... H E E E E E. Five ticks for each of the six rooms; 7.5 seconds. Each repeated note is a new tick of a continuing stay, not a new arrival.
* Collapsed: remove consecutive duplicate room labels from Dwelling, then render one tick for each retained label. Byte-identical to Transit by construction. This is a destructive editing operation; do not describe the result as an unedited time recording.

Performance score: play Transit, then Dwelling, then Collapsed. On the fourth tour use the graph merely as a suggestion; interrupt a return, linger without counting, or invent a connecting door. The fourth tour has no supplied rendering. Its point is to escape the model rather than optimize it.

[Laboratory source](laboratory.py): run with Python 3.11+ and no dependencies. It writes three WAVs and a JSON receipt into a local audio directory. The WAVs are deliberately not committed to the repository. Qualification executed twice using Python 3.13.5: 2,040 exact rational parameter cases (k 2–16, q positive fractions with denominator 1–16 including repeated rational values), explicit row stochasticity, normalization, stationary matrix multiplication, movement fraction, uniformity criterion and conditional hub-arrival fraction. The deterministic scores check exact counts and collapsed equality. WAV headers, frames, complete PCM readback, amplitude bounds and within-run deterministic rendering pass. Transit and Collapsed hash 15f51a3ff5393be27ad6ce64a09b20c7de8e680da5c0688ab88cf29c48574918; Dwelling hash 4ad239221d69116592734dcad053caf7522a2c3562347735fe38c6d63013d4b0. Same-runtime numerical rendering is tested, not cross-platform bitwise reproducibility. No microphone, human listening or real urban data.

## The instrument: Dérive Organ

A graph of synthesis regions, separate buses for occupation and entry, and separately controllable route and dwell clocks. The route bus strikes short sounds when crossing a threshold. The occupation bus sustains a local evolving voice. A third bus performs the disagreement between long-run arrival frequency and elapsed time.

The musician can paint a door instead of painting a note. An edge can introduce a bridge oscillator without altering the region's own patch. A newly opened door is potentially a change to the entire composition, even when nobody has walked through it yet.

A CYD implementation could place territories on a small touchscreen: tap to inspect a region, draw a permitted connection, hold to alter the dwell clock. Provide an explicit distinction between an actual movement and a preview; permit stopping and saving. A VSTi can represent region identities as patches, advance a clock with sample-accurate event scheduling, expose separate route and occupation MIDI outputs, and keep a persistent visit ledger. A VSTfx could route explicitly provided stems according to a graph; it must not claim to infer source identities from arbitrary mixed audio.

A further speculative extension is a landscape of competing explorers. One follows attraction, another seeks unfamiliar rooms, another remains in place until a long envelope completes. Their paths interact musically, but their distinct purposes must not be collapsed into one optimization target. A room that is not visited may still generate material. Route, world evolution and monitoring are separate processes (cf. the Carrier Bag Organ, #731).

## Operational boundary and proposed experiment

A machine interface that reports frequent entry into a subsystem may conceal that little time was spent inspecting it. Conversely, a long-lasting display state need not establish repeated independent checks. Distinguish entry, elapsed occupation, active inspection and actual task completion. None can be inferred from the others without an explicit contract.

Synthetic evaluation: use matched star and regular cycle graphs, fixed and stochastic dwell clocks, and tasks asking about route counts, elapsed time, completed inspections and pending obligations. Compare plain textual visit/time ledgers, transition-only summaries, and dual-bus audio with the same accessible ledger. Include a coalesced-event negative control and a short finite-run condition. Record correct operational decisions, mistaken inference between counts and time, latency, abstention and workload independently. No acoustic advantage is claimed; a simple table may suffice. Accessibility and participation require real authorized evaluation, not the model.

## A city that does not want to be explored

The strongest objection is that the laboratory is an impoverished soundwalk. Its rooms never change because a listener is paying attention. It equates time with ticks and contact with a state change. An artist might instead need thresholds that disappear, uncertain boundaries, inaccessible regions, or a visitor who listens to the echo of a place from another place. These would require explicit new models rather than claims that the star is already a theory of lived space.

*The surveyor drew five doors on a plan. The organist played the corridor five times. The mayor ordered more workshops. The organist played the corridor six times. A child opened a door between two workshops. The surveyor had to begin again.*

## Reconciliation and handoff

Read live AGENTS, RAG, programme, runbook, integrity and validation authorities; inspected 40 recent PR titles and 30 active issue titles. Targeted searches for psychogeography, Debord, situationist, flâneur, random walk and drift navigation found no direct matching expedition (search indexing is incomplete). Other explored directions were abandoned because of existing clinamen (#494), chiasmus (#188), anacoluthon (#366), parergon (#628) and metalepsis (#594). This contribution is not the earlier encounter-coverage experiment (#701) or the observation-window instrument (#731): it holds the jump policy invariant while changing elapsed occupation, and tests a destructive export that removes dwell information.

Base main at inspection: 495a98ca12bae467a507031f04931aa4254b1866. Fresh branch mhac-x742/city-mistakes-visiting. Scope only this directory, no manifests or frozen protocol, no human recruitment, no license decisions. The full repository validator and exact-head CI are separate from local laboratory qualification. Existing mergedown integrator owns landing; keep Draft/HOLD until its checks and review requirements are satisfied.
