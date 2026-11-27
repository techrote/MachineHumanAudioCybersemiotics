# The Choir Whose Answer Depends on Your Seat

**Expedition #769 · 27 November 2026 · Exploratory humanities/art and synthetic mathematics · Draft/HOLD**

## A fictitious liturgy

Three choirs address a congregation stretched along a corridor. The central choir begins. The western choir speaks next, and the eastern choir last. At the western end a witness insists the western choir spoke first. At the eastern end another witness insists the eastern choir did. Neither needs to have misremembered.

The archivist wants to designate one recording as the true sequence. The architect instead draws the places at which a pair of utterances exchange order.

A fourth choir, which contains no singers, is introduced. Its score consists solely of those places. The congregation performs it by walking.

This is an original speculative scene. The proposal is to compose the geography of reception, including its temporal relationships, without necessarily changing the emission score. It is not an historical reconstruction.

## Source-located encounters

- **Masataka Yoshioka, _Singing the Republic: Polychoral Culture at San Marco in Venice (1550–1615)_ (PhD dissertation, University of North Texas, 2010), [institutional record, extended Description](https://digital.library.unt.edu/ark:/67531/metadc33220/), DOI 10.12794/metadc33220.** Complete extended abstract and bibliographical metadata read on 27 November 2026; dissertation chapters not read. Yoshioka interprets the rhetorical interaction of Venetian choirs as an expression of civic ideology: distinct groups are presented as belonging to a harmonious political whole. He treats the alternation and eventual convergence of choirs as meaningful rhetorical structures. This is his musicological argument, not a demonstrated universal political meaning of polychorality. No historical placement or performance practice is inferred beyond the access available.
- **University of Cambridge, Centre for Acoustic and Musical Experiments in Renaissance Architecture (CAMERA), [project account](https://www.hoart.cam.ac.uk/research/past-projects/camera), Architecture and Music in Renaissance Venice section.** Indexed project text consulted; direct retrieval returned 403. Howard and Moretti's team describes acoustic measurements, situated choral performances and audience questionnaires. This is a discovery-level methodological precedent, not a close reading of their book or results. It motivates an empirical alternative to merely imagining a Renaissance church's acoustic field.
- **Albrecht Moritz, [Stockhausen: GRUPPEN (1955–57)](https://stockhausen-essays.org/gruppen.htm), 2000, edited 2005, opening paragraphs through the composer's attributed explanation of spatial arrangement.** Full relevant HTML passages read. The account describes three orchestras disposed around listeners; the attributed composer passage connects separate tempi with the development of spatial composition. The underlying booklet and performance score were not independently examined; no recording was auditioned. Spatial composition is an established artistic precedent, not this expedition's invention.
- **National Arts Centre, [Storgårds, Beethoven & Dvořák programme notes](https://nac-cna.ca/en/event/notes/40423), discussion of Ives's _The Unanswered Question_.** Indexed passage consulted; direct retrieval returned 503. The programme describes the separated instrumental groups and Ives's contrasting narrative roles. The primary score was not examined. This is a provisional comparison, not evidence about which group audiences actually hear first.
- **Andrew D. Brown et al., “Evidence for a neural source of the precedence effect in sound localization,” _Journal of Neurophysiology_ 114(5), 2991–3001 (2015), [DOI](https://doi.org/10.1152/jn.00243.2015), [NLM metadata](https://pubmed.ncbi.nlm.nih.gov/26400253/).** Indexed publisher abstract and introductory definition of fusion/localization dominance read; direct publisher retrieval returned 403. The authors report results for simulated source–echo stimuli; no full methods appraisal or data extraction undertaken. This is a counterweight to the proposed construction: arrival time, perceived number of auditory objects, localization and perceived temporal order cannot be equated. In particular, findings about similar lead–lag sounds do not automatically apply to distinct pitched bursts here.

All source access and interpretation are AI-assisted, not independent human review; no source has been admitted to the frozen evidence corpus. No restricted source text is reproduced.

## Interpretation: the political acoustics of a privileged seat

Yoshioka's interpretation suggests a question worth reversing. Rather than making separated groups culminate in a representational unity, an artist might distribute different temporal relations among the listeners. One spectator receives a question followed by something that can be heard as a reply; another receives a nominally identical performance with the apparent reply first. Neither recording exhausts the event.

The political reading is deliberately speculative: a privileged seat could acquire the status of a privileged history. An acoustic difference is not in itself proof of a political hierarchy. The point is that an archive must decide which observations to preserve and which it has made interchangeable.

The comparison with Stockhausen is not a claim that his practice implements this formula. The particular construction here edits the positions of pairwise arrival reversals, treating coincidence loci as composable constraints.

## Exact direct-arrival model

In a virtual one-dimensional medium, measure distance in travel-time units. Let source i at coordinate x_i emit one labelled event at t_i. A receiver at p receives its ideal direct onset at a_i(p)=t_i+|p-x_i|. Fixed propagation speed is absorbed into units; no reflections, attenuation, Doppler, head-related response, source detection, listener motion during an event or clock error.

For x_i<x_j, an interior reversal exists exactly when |t_j-t_i|<x_j-x_i. The boundary is

    b_ij=(x_i+x_j+t_j-t_i)/2.

Between the sources, the arrival difference a_i-a_j grows with slope two; outside it is constant. Therefore i arrives before j exactly when p<b_ij in the strict case. At equality of the emission-time separation and source distance, equality persists on an exterior ray; it is not a unique interior crossing. Beyond that bound no reversal is possible.

For three ordered sources A,B,C:

    b_AB+b_BC-b_AC=x_B.

The boundary desires are therefore not independent. A composer specifying all three must satisfy this identity, and each boundary must lie strictly between its pair of sources. These conditions are also sufficient: set t_A=0, t_B=2b_AB-x_A-x_B, t_C=t_B+2b_BC-x_B-x_C. The third desired boundary follows from the identity.

Moreover b_AB<x_B<b_BC, hence b_AB<b_AC<b_BC. All strict cases visit exactly four distinct strict arrival permutations, always ABC, BAC, BCA, CBA as the receiver travels left to right. A single straight corridor cannot produce all six permutations of three mutually reversible single events, regardless of their valid emission offsets. Tie positions are excluded from the permutation count.

For n ordered sources in the strict regime, each pair reverses at most once; there are at most n(n-1)/2+1 strict arrival orders. This is sharp when choosing positions freely: let x_i=2^i and all t_i=0. Binary uniqueness makes every pair midpoint distinct; crossing each changes a pairwise order that will never reverse again. The result concerns a line of static point receivers, not arbitrary 2D or 3D movement.

The general inverse problem: prescribe interior boundaries on selected edges. Convert each to a desired time difference d_ij=2b_ij-x_i-x_j. A common emission schedule exists precisely when the signed differences sum to zero around every cycle of the prescribed graph. Within a connected component, choose one reference time and integrate along a spanning tree; consistency makes all other edges agree. Disconnected components retain independent time origins. This is elementary potential consistency, not a claim of mathematical priority. It says nothing about unprescribed edges, which may not reverse. The general graph criterion is derived, not separately exhaustively tested here.

Another consequence: |(a_j-a_i)-(t_j-t_i)|<=|x_j-x_i| by the reverse triangle inequality. If the received gap exceeds the known travel-time separation, its sign certifies the emission order in this ideal model. Inside the bound, without receiver position or additional information, order alone cannot certify emission order. Even correct emission order does not certify causal dependency, scope or acknowledgement.

## Executed laboratory and original score

Run `python laboratory.py audio` from this directory. Standard library only. Python 3.13.5 was executed twice locally; the two output directories compared byte for byte. A failed early test revealed a supposedly inconsistent boundary triple (4,16,24) was actually consistent; the corrected negative witness (4,17,24), ordered AB,AC,BC, is inconsistent for x_B=12. Preserve this correction as a useful example of artistic intentions needing mathematical checks.

The finite census covers x=(0,b,c), 1<=b<c<=8, t=(0,u,v), -8<=u,v<=8, filtering to all three strict pair conditions. All 532 admissible triples exhibited exactly four strict arrival orders. 6,384 pair comparisons at exact rational interval representatives passed; pair equalities, interior positions and the triangle constraint were checked separately. Seven simultaneous-emission constructions for n=2..8 attained the general count bound. Equality and beyond-bound crossing requests are refused, not represented as arbitrary single boundaries.

The sound piece _Four Seats and a Hinge_ fixes x=(0,12,31), t=(3,0,5), pitches=(220,330,495) Hz. A tick is 10 ms; positions are expressed in propagation-time ticks. The crossings are 4.5,16.5,24 for AB,AC,BC. Four repetitions occur every 700 ms; 70 ms Hann-like squared-sine bursts have fixed amplitude 4200 PCM units before mixing. Each export is 3 s, mono signed 16-bit PCM, 16 kHz; no normalization or room model.

| Virtual seat | First repetition scheduled arrivals A,B,C (ms) | Strict order |
|---|---|---|
| 0 | 30,120,360 | ABC |
| 10 | 130,20,260 | BAC |
| 20 | 230,80,160 | BCA |
| 31 | 340,190,50 | CBA |
| 4.5 | 75,75,315 | A=B then C |

The receipt's ABC label for the tie is only index tie-breaking in the sort, not a strict order. Sample offsets designate scheduled burst starts, not measured perceptual onsets. All five hashes differ; headers, PCM readback, headroom and same-runtime rerender equality passed. No human listening test or calibration took place. Playback is a synthetic timing illustration, not a binaural or realistic architectural recording.

Original performance instructions: Listen at each of the four seats in order. Imagine an identical public announcement being issued by the same three people each time. In a fifth movement take the hinge seat. Refuse to decide who spoke first where their attacks coincide. In a sixth, unwritten movement, move the architectural boundary instead of the voices. No inference about an actual listener's experience is required.

## Exaptation and a second rabbit hole: compositional jurisdiction

Make a **Choir Atlas VSTi** with separately editable emission gestures, a one-dimensional virtual receiver, bounded per-source delays and independently selectable listening perspectives. The sound generator and the room score need not share a clock editor. A boundary editor should report inconsistent constraints rather than silently move a requested boundary. A future VSTfx could accept explicitly tagged input stems and render several perspectives, with bounded delay lines and independent latency reporting; no arbitrary source separation is assumed. A CYD version could use horizontal touch to move a virtual receiver, vertical touch to vary an explicitly fictional propagation scale, and show three arrival traces. An FM-1 experiment could use relative arrival intervals to modulate envelopes or FM indices without claiming physical acoustics.

A further musical thought: each listener could inhabit a different contractual definition of concurrence. One receives the direct order, another quantizes arrival into a common beat, a third receives a deliberately synchronized version. The disagreements become control signals. An artist can introduce fictional replies, but a machine claiming to report operational events must identify them as fictional.

The second rabbit hole is the inverse designer. Ask a composer to mark locations for every intended coincidence. Some designs are impossible because the boundary constraints conflict. Instead of an opaque least-squares repair, present the inconsistent cycle and offer an explicit choice of which boundary to move. The residual becomes an additional artistic material rather than merely an error message. Future work could examine optimization under weighted boundary priorities, 2D hyperbolic loci, uncertain clocks, reflected arrivals and mobile receivers. None are implemented here.

## Implications and objections

The narrow MHAC implication is that local reception chronology cannot automatically stand in for source chronology. Neither chronology implies causality or successful operation. Preserve event identity, source time and its clock scope, receiver time, and dependency receipts separately. Compare a conventional typed event ledger against arrival-order displays and optional acoustic representations under controlled synthetic delays, offset uncertainty, mis-scoped acknowledgements, and missing events. Human evaluation remains gated; proposed outcomes include correct source-order judgment, causal misattribution, abstention, action correctness and latency. A textual event ledger may solve the entire engineering problem; no acoustic advantage is claimed.

This is an impoverished polychoral performance. Its static sources ignore the ways musicians adapt to one another, architecture affects the spectrum, and audiences share a socially situated event. Fusion and masking can make the labelled onsets inaccessible. A real score may demand audible togetherness rather than differentiated perspectives. A deliberately seat-dependent installation can also become inaccessible to people who cannot move. Provide independently selectable perspectives rather than equating bodily mobility with access. No mathematical model here proves Yoshioka's historical interpretation or explains the entirety of spatial musical experience.

## Reconciliation and checkpoint

Live main inspected at 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, README, RAG, programme, runbook, research integrity and validation. Reviewed forty recent PR titles, thirty active issue titles and targeted overlap queries; #41 received-channel stress test read in full. It concerns feature survival under transforms, whereas this expedition concerns exact direct-arrival reversal loci and their artistic inverse constraints; no duplication of its qualification or authority is claimed. Searches for antiphonal, Gabrieli, propagation delay and spatial synchrony returned no exact matching expedition; searches are not a comprehensive novelty audit. Hocket (#540), tuning drift (#286), heterophony (#586), and estrangement (#430) were avoided as primary topics. The newly created #769 had no comments at inspection. Scope is an explicitly authorized independent exploratory expedition, not advancement of R005–R020. No shared manifests, canonical evidence, protocol, other branches or production components touched. Draft/HOLD for independent mergedown and exact-head CI; native execution is not repository CI or scientific acceptance. No human action required for this bounded handoff.
