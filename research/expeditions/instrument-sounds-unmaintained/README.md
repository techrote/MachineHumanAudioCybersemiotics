# The Instrument That Sounds Unmaintained
*Maintenance art, the silence of successful correction, and service counterpoint.*

Exploratory humanities expedition, 24 November 2026. Refs #374. AI-assisted original interpretation and synthetic construction, not a frozen Track E/G extraction, empirical finding, or production design. One GPT-6.2 assistant performed source reading, construction, mechanical checks and self-review; no independent reviewer or participant.

## I. The third performer

A machine that has never needed repair and a machine that has been repaired every morning can give exactly the same concert. If the repair is good enough, the audience may have no means of distinguishing them. The second machine is not necessarily less reliable; its reliability may be an accomplishment rather than an intrinsic property.

The third performer, omitted from the programme, is the person who tuned the machine before the concert. In a digital instrument the third performer might also be an automated controller. These are not morally interchangeable: the controller has no entitlement to human wages, rest or recognition. The distinction matters precisely because we are borrowing a concept from the history of human labour.

An instrument is sometimes said to possess a character because it is difficult to maintain. This can romanticize the expense incurred by other people. The thought experiment here instead asks what it means for something to have a history of care whose result is an absence of perceptible history.

## II. Four encounters, and a disagreement

**S1 — Mierle Laderman Ukeles, Manifesto for Maintenance Art (1969), excerpt and curatorial context.** [Arnolfini, Maintenance Art Works 1969–1980](https://arnolfini.org.uk/whatson/mierle-laderman-ukeles-maintenance-art-works-1969-1980/), paragraphs beginning “The work of Mierle Laderman Ukeles” and the following attributed manifesto excerpt. Read the exhibition prose and reproduced excerpt, not the entire manifesto. The exhibition frames Ukeles's work around the neglected status of domestic and low-paid labour and her challenge to boundaries between art and daily life. In the reproduced passage she proposes exhibiting everyday acts of care as art. This is a feminist intervention in the organization of work, not merely a metaphor about correcting oscillator frequency. My interpretation: a concert might incorporate the tuning process as a work in its own right rather than treating it as a failed portion of the concert.

**S2 — Steven J. Jackson, “Rethinking Repair” (2014), chapter 11, pp. 221–240, DOI [10.7551/mitpress/9780262525374.003.0011](https://doi.org/10.7551/mitpress/9780262525374.003.0011).** [Publisher abstract](https://academic.oup.com/mit-press-scholarship-online/book/14976/chapter-abstract/169335302). Abstract exposed by search and read; direct retrieval subsequently failed. No full-chapter claim. Jackson's stated argument centres breakdown, maintenance and care in technical experience rather than privileging the creation of new artefacts. Interpretation: the history of a device is not exhausted by its release notes; an unchanged interface can represent considerable ongoing technical activity. A release log is an unreliable proxy for this activity.

**S3 — Variable Media Network, [statement of approach](https://variablemedia.net/e/index.html).** Read the web sections on medium-independent behaviours, performed works, the four preservation strategies and the third-generation questionnaire. Its examples include curators gathering branches to install Meg Webster's Stick Spiral; the installation procedure is something to preserve, not merely an obstacle to reproducing its appearance. Its discussion of reinterpretation explicitly warns against unauthorized transformations. The later questionnaire consults people beyond the named artist, including assistants and conservators. Interpretation: record the kinds of intervention an instrument is allowed to undergo, the people entitled to perform them, and whether those interventions are constitutive of the work. An executable patch alone is an inadequate specification for certain artworks.

**S4 — Kunstmuseum Den Haag, [Musical instruments collection](https://www.kunstmuseum.nl/en/collections/musical-instruments).** Read the collection-history paragraphs before “Provenance research,” particularly the two beginning “Under the first curator” and “An exception.” The museum explains that playing its collection was later restricted for conservation reasons, with exceptions for some instruments, including synthesizers. This is the institution's stated policy, not a universal conservation rule. It complicates an easy celebration of use: preserving a practice, preserving an object, and permitting an object to incur wear are different decisions.

These positions are not a single doctrine. Ukeles's political/artistic intervention is not equivalent to Jackson's research programme; the variable media framework is not a permission slip to replace every component; and an institution protecting rare objects need not be hostile to living music. S3 also supplies a contrary approach to preserving original material: approved migration or emulation may be preferable in particular cases. Neither preserving performance nor preserving components has automatic priority.

Access: public web excerpts and institutional statements retrieved 2026-11-24, English. No third-party source text or images retained. This is a small purposive reading, not an exhaustive search. S1 and S2 are not full primary-text readings; do not extend claims beyond the specified passages.

## III. The perfectly maintained sound

An original finite construction: at each tick an abstract raw offset r changes by -1, 0, or +1. An independent compensator c may choose any integer in [-B,B] after seeing the new r. The audible error is e=r+c. A distinct idealized intervention, repair, resets r and c to zero before sounding. This is a toy state transition, not a physical theory of wear, cost, repairability or reliability.

Three machines perform the same eight-note melody. The first has no disturbance. The second receives [1,1,1,0,0,0,-1,1] and compensates at every attack. The third receives the same disturbance and resets the raw offset each tick. For B=4 the three PCM outputs match exactly. A fourth machine, without service, detunes by 9 Hz per unit of raw offset. The two audit versions add a separate optional channel for nonzero compensator movement (880 Hz) or nonzero repair magnitude (440 Hz); the melody channel remains identical. These codes are arbitrary artistic conventions.

The counterexample is stronger than the observation that many causes yield one sound: at the last tick the compensated machine has r=3, c=-3 and error zero, while the repaired machine has r=c=0. The two states have different capacity for future compensation without further repair. A listener with a perfect recording of the entire concert cannot recover this difference from the recording alone.

For a starting offset r in [-B,B], assume repair is unavailable for the next h ticks, drift steps have absolute size at most 1, and compensation can choose a new value freely each tick. Perfect correction is guaranteed for all allowed continuations exactly when h <= B-|r|. Sufficiency: every prefix has absolute offset at most |r|+h. Necessity: take successive unit steps outward (either direction at zero). After B-|r|+1 ticks the offset exceeds the compensation range. This is an elementary model-specific robust horizon, not a probability of failure or a claim that real equipment obeys the model. No rate constraint, noise, delay, measurement uncertainty or repair cost is included.

The sample compensated instrument thus has guaranteed reserve of one tick; the repaired one has four. Their identical acoustic state at the checkpoint does not make their maintenance situations equivalent.

A ledger of correction movement and reset magnitude is included for synthetic arithmetic only. Neither magnitude measures human work, skill, wages or effort. In fact the repaired machine and compensator execute differently costly operations, and the model explicitly refuses to compare these costs.

## IV. An interface for the labour of remaining unchanged

Proposed instrument: a **Service Counterpoint Bus**, not a simulated defective oscillator sold as vintage authenticity. It separates a playable voice, a latent condition model, compensation, authorized repair, and an independent optional sonification of the work necessary to maintain the voice. A performer can choose which transformations belong to the sound and which remain in the service ledger.

Imagine a modular patch whose timbre remains fixed while its service lane grows increasingly elaborate. A second performer composes the disturbances; a third maintains the timbre. A fourth chooses when the audience can hear the maintenance lane. The artistic question is whether the stationary voice can be heard as an achievement rather than an absence of composition.

A further possibility is *maintenance improvisation*: the maintainer is given a fixed reserve, a collection of permitted restoration operations, and a right to refuse further work. Their improvisation is not the introduction of a new melody but the negotiation of an existing one's persistence. A different piece could intentionally disable compensation and turn a hypothetical fault into musical material. Keep this inside a fictional/synthetic instrument; no permission to manufacture failures in real devices.

A practical interface should distinguish condition (raw deviation), correction already applied, residual error, remaining reserve, whether inspection actually occurred, and authority to intervene. The ledger should explicitly identify missing observations. A normal residual is not a guarantee of a healthy component. A compensation reserve is not a hazard estimate or a countdown to inevitable failure.

The ethical counterargument: making maintenance visible can become surveillance. A worker should not have to demonstrate constant struggle to deserve payment, and a quiet service log should not become evidence of idleness. Recording every intimate detail of care can destroy the autonomy of the person providing it. The proposed score lets the maintainer withhold or summarize the optional artistic lane; it never permits suppression of operationally required disclosures. An audit tone should never claim that human labour occurred when only an automated operation was observed.

## V. A question for MHAC

In an authorized synthetic evaluation, compare (A) output-only status, (B) explicit residual plus compensation reserve, and (C) B plus a selectively available maintenance ledger. Give all three the same correct currently rendered state; vary future disturbances and whether repair remains available. Include stable and genuinely unserviced controls, false-positive costs, missing or stale diagnostic readings, and a text equivalent. Ask for correct decisions about whether to inspect, continue, or request more information, not just confidence ratings. Measure comprehension, response time, false reassurance and notification burden; do not equate simulated reserve with real hazard.

Reject or narrow the proposal if additional disclosure produces confusion, false alarms, privacy loss or no useful action improvement. No participants recruited; no evidence of interface advantage asserted.

## Reproducibility and boundaries

Run `python lab.py audio` with Python 3.11+ (executed here on Python 3.13.5). It creates six 16-bit stereo 16-kHz WAVs of 3.2 seconds and a JSON state/receipt ledger. The exact finite check enumerated 38,255 continuations across 245 (B,r,h) configurations, including zero horizon; an explicit fifth outward step defeats B=4 compensation but not ideal repair. All local assertions passed: repeated synthesis, matching full PCM for the three perfect-output cases, distinct no-service and audit controls, invariant left-channel samples, sample peak and WAV headers/payloads. The committed lab blob was compared with the locally executed Git blob: 512b040541227968795bb4c886d9849c16c638b8.

WAV SHA-256 receipts (local run; identical hashes are intentional):

| Files | SHA-256 |
|---|---|
| 01-stable, 02-compensated, 03-repaired | 3255be9fabfc38add2a552df265a861e71e3868c7764ebce7227ef5a5e45042e |
| 04-unserviced | 4e61e23abcf8e2068d8eb901b9428d6c1128c4fc4b985957686628a5ad5e35b7 |
| 05-compensation-audit | ba5a18e832e102e7f48a5932a784a4a16f954545550d530585be8937223bbf43 |
| 06-repair-audit | cea5af52c54a5125e1c33cd25821d48fcb8a40e76227e9ecd6eb06cb2be00ae6 |

The PCM test is digital, not perceptual. Hashes are receipts for the stated runtime, not a promise about every platform's floating point library. No claim of mathematical priority. No independent source review, real-world sensor, physical maintenance, human listening or economic inference.

Reconciliation: read live main README, AGENTS, RAG, programme, runbook, integrity, validation and project foundations; inspected 100 recent PR titles, 70 open issue titles and targeted maintenance/Restorer's Seam/Remembers Your Hands search results. #222 concerns conjectural restoration after loss; #270 concerns appropriation and gesture compatibility. This expedition studies ongoing correction that prevents an audible defect. #374 was created and its full body and empty comments read. Branch from main 495a98ca12bae467a507031f04931aa4254b1866. Only this directory is added; no canonical registry or protocol change. Repository-wide exact-head checks and independent review are separate from local checks.

[Original performance score](SCORE.md).
