# The Clock Inside the Grain

**2026-11-27 — Exploratory humanities/art expedition, #807.** Draft/HOLD; AI-assisted original essay and synthetic laboratory by one GPT-6.2 agent. No participant data, no independent human review, no canonical evidence promotion. This is not a new finding of the frozen MHAC protocol.

## The miniature that demands its own conductor (original fiction)

A clockmaker constructs a musical city which lasts exactly twenty-one ticks. It contains two districts, each divided into two streets, each divided into two houses, each divided into two rooms. A melody moves through its sixteen rooms.

The mayor orders all divisions to be as equal as indivisible ticks permit. Every district receives an independently authorized clockmaker. The finished city passes every local inspection. Yet a visitor following the city clock arrives at a particular room more than a tick before the music does.

A second city preserves the exact same total duration, number of rooms and inventory of short and long rooms. It appoints a single surveyor to determine every boundary from the original plan. Its clocks agree much more closely with the mayor's ideal.

The first city asks whether it must surrender its interior rhythms in order to be considered correct. The second asks whether a visitor should be obliged to learn sixteen different histories of time.

Neither city is an argument for political centralization. The fictional administrative architecture serves to distinguish two mathematical constraints and to dramatize their consequences.

## Source encounters and interpretation

**Source S1: Gaston Bachelard, The Poetics of Space, Maria Jolas translation (Beacon Press edition with John R. Stilgoe foreword, 1994), chapter 7, Miniature.** [University-hosted PDF](https://sites.evergreen.edu/wp-content/uploads/sites/88/2015/05/Gaston-Bachelard-the-Poetics-of-Space.pdf). Printed pp. 155, 161 (PDF zero-index pages 190, 196) visually inspected; text passages around pp. 163–167 also read. Not a full-book reading or a comparison with the French. Access: public university-hosted copy, no source bytes redistributed; no claim of redistribution license. Checked by this agent on the expedition date.

Bachelard's magnifying glass is an invitation to enter a newly significant world (p. 155), not merely a mechanism for increasing apparent size. On p. 161 he describes the comfort of miniature worlds in terms of mastery, and on p. 163 resists treating the poetic miniature as simple relativity of dimensions. The Petit Poucet discussion (pp. 165–166) moves from scale to command: a tiny voice positioned within a horse's ear directs a much larger body. Bachelard attends to the ambiguity of listening as hearing and obeying. These are literary-philosophical passages, not experimental observations of auditory attention.

**Interpretation:** A zoomable synthesizer might contain places that have a life of their own rather than showing a succession of enlarged pictures of the same object. A tiny detail might govern a much larger structure. Equally, a miniature can be an instrument of domination: a surveyor can overlook the local time of inhabitants. We should not uncritically adopt the metaphor of mastery.

**Source S2: Susan Stewart, On Longing: Narratives of the Miniature, the Gigantic, the Souvenir, the Collection.** [Duke University Press](https://www.dukeupress.edu/On-Longing), publisher description, paragraphs beginning with the inventory of cultural forms and the original publication history; DOI [10.1215/9780822378563](https://doi.org/10.1215/9780822378563). The 1992 Duke edition is described as a reissue of the 1984 Johns Hopkins publication. Only the publisher description and bibliographic details read; no chapter-level claim is made.

The publisher identifies miniature with interiority and relates the book to the body, scale, narrative and experience. It provides a useful contrasting frame for the laboratory: a miniature might establish an interior rather than merely preserve proportions. The book itself remains a reading lead, not fully evaluated evidence.

**Source S3: Kyle Gann, Survey of works by Conlon Nancarrow, IRCAM, updated 15 September 2010.** [IRCAM English work survey](https://brahms.ircam.fr/en/composer/conlon-nancarrow/workcourse). Read the paragraphs on structural convergence points, tempo switches, studies 24, 31, 36, 21 and 27, and synchronization limitations in studies 41/48. Secondary expert account; no score, original rolls, or recordings inspected in this run.

Gann describes multiple voices whose different tempi govern shrinking or expanding temporal echo distances, and Study 21 as a crossing of acceleration and deceleration. In his account of Study 48, precise convergence between two player pianos presents a performance problem. The historical point is not that Nancarrow used the integer rounding system below; that would be unsupported. It is that relationships between clocks already constitute a rich musical domain, and a notated temporal relationship need not translate straightforwardly into a particular performance medium.

**Synthesis proposition, unvalidated:** Zoom should be separated into magnification (no change in score), traversal (choose another internal time domain), and retiming (change an actual schedule). A fourth gesture, delegation, assigns authority over subdivision to a selected region. This turns the apparent error of unequal quantization into a deliberately editable feature. Do not automatically transfer these artistic conventions into operational timing.

## Exact construction: the two clockmakers

Let M = 2^d be the number of leaves in an ordered perfect binary tree and let N >= M integer ticks be distributed among them. Each leaf is allocated a positive integer duration. Each internal node passes its budget to two children whose budgets differ by at most one. Call this *local balance*. The clock is exact at the end of the root, not necessarily at internal boundaries.

Let b_i be the cumulative duration up to leaf i; the ideal reference is iN/M. Define signed prefix error e_i = b_i - iN/M. It is an explicit schedule discrepancy, not an estimate of subjective rhythm or of physical clock instability.

A globally aligned clock can take b_i = floor(iN/M + 1/2). Each boundary is a nearest integer, so |e_i| <= 1/2. Each child interval of a given parent spans the same number of ideal ticks x. For any real u, floor(u+x+1/2)-floor(u+1/2) is either floor(x) or ceil(x). Thus the two child lengths differ by at most one; the global schedule is also locally balanced at every depth. Because each individual boundary is nearest to its ideal location, it minimizes maximum absolute prefix error over all integer schedules. This is an elementary construction, not a priority claim.

But local balance alone does not guarantee that global half-tick bound. At M=16, N=21, a witness is

- Global: 1 2 1 1 | 2 1 1 2 | 1 1 1 2 | 1 1 2 1
- Local: 1 2 1 2 | 2 1 1 1 | 1 1 1 2 | 1 1 1 2

Both sum to 21, use eleven single-tick and five double-tick cells, and satisfy all fifteen split constraints. After five leaves, the local cumulative time is 8 ticks, versus ideal 105/16 = 6.5625 ticks. Error = 23/16 = 1.4375 ticks. Its reflected schedule exchanges the sign of the corresponding errors. The global schedule's maximum absolute error is 8/16.

A general loose bound follows from midpoint rounding: for any internal boundary, its error is the mean of its parent endpoint errors plus a residual in {-1/2, 0, +1/2}. At depth j the absolute error is at most j/2 by induction. This is not asserted sharp. No need to claim unbounded drift on the basis of four tested depths.

The exact number of locally balanced words follows from C(N,1)=1 and C(N,M)=sum C(k,M/2)C(N-k,M/2), over distinct k in {floor(N/2),ceil(N/2)}. It counts distinct ordered leaf allocations, not distinct labeling histories that produce the same durations. For N>=M, all leaves remain positive.

## Executed census and sound art

Standalone Python 3.13.5 laboratory (standard library). Run from this directory with python laboratory.py /tmp/miniature-audio (or another writable output directory). The script exhaustively filters every vector with leaf durations 1 or 2 for depths 1 through 4, groups by total, independently checks counts via recursive allocation, and verifies global rounding against the actual minimum max absolute error for every total. Reflection closure makes maximal positive error equal to the maximal absolute error over each complete depth census.

| Depth | Vectors screened | Locally balanced | Largest absolute prefix error (ticks) |
|---|---:|---:|---:|
| 1 | 4 | 4 | 1/2 |
| 2 | 16 | 14 | 3/4 |
| 3 | 256 | 130 | 9/8 |
| 4 | 65536 | 7586 | 23/16 |

Total 65,812 vectors, 7,734 balanced. 34 distinct depth/total cases (3+5+9+17) checked. The explicitly unbalanced vector (2,2,1,1) is rejected. Enumeration covers totals M through 2M; no larger exhaustive claim. Standalone native execution and repeat receipt comparison passed; not a full repository validation.

**Three rooms for an indivisible clock (original sound art).** Three 3.36-second stereo WAVs, 53,760 frames each, signed PCM16 at 16 kHz. Left channel always performs the global clock; right performs global, local extreme or its reversal. Eight pitches cycle through the sixteen events, with the same note order in every edition. The unit of 40 ms (640 samples) deliberately magnifies symbolic timing. This does not represent the audibility of single-sample errors at normal sample rates. At the fifth boundary the local right channel is one full 40 ms tick behind the left, and 57.5 ms later than the unrendered ideal. All three end at the same root boundary on each of four repetitions. Complete WAV readback, sample bounds, identical left channel hashes and three distinct full-file hashes passed. Rerendered receipt byte-identical within the same runtime. No listening test or subjective judgment is claimed.

- Global: both channels synchronized.
- Local: right channel follows the selected maximal-error local allocation.
- Reflected: right channel follows the reversed duration word, not a reversal of the pitch sequence.

Perform the global edition, then the local one. Imagine the left channel as an aerial view and the right as the time experienced inside a room. Reverse this interpretation: perhaps the left is a clock that has refused to enter any room. For an unwritten fourth movement, give each room an independent motif that develops at its own rate. Refuse to describe the result as a tempo error unless the score actually required common phase.

## Instrument consequences (proposals)

**Grain Clock VSTi:** a recursive sequencer; a region has integer duration, tempo ratio, motif and rounding contract. Separate global boundary compilation from local parent-budget allocation. A selectable residue bus performs signed prefix error as a pitched or percussive gesture. Do not run enumeration or allocate memory in a real-time callback; compile bounded snapshots on a control thread and atomically publish at a declared boundary.

**Microscope VSTfx:** explicitly segmented input stems, with overview and local retiming auditions. Preserve exact parent extent, identify interpolation/resampling policies separately from event retiming, expose discontinuities and boundary receipts. No arbitrary source separation or pitch-preserving DSP has been implemented.

**CYD Grain Atlas:** 320x240 hierarchy view, touch selects a node; horizontal gesture changes split allocation, vertical gesture navigates depth. Provide global/local policy, local budget, prefix error and a residue audition. Avoid conflating a rendered zoom with a change to the musical model. A simple 16-leaf bounded implementation requires no exhaustive enumeration during performance.

**FM-1 Microcosm:** nested FM parameter gestures with independent local timing and fixed parent duration. A control-rate sequencer may use integer tick rounding; independently test parameter discontinuities, bounded gain and actual jitter on hardware. Exact waveform invariance is neither promised nor expected.

The more speculative instrument has persistent oscillator territories inside other territories. A parent delegates a time budget rather than micromanaging the descendants. A musician can enter a territory's clock and hear what was previously a detail as an entire composition. This is not a demand that every musical world be self-similar. A child may have an entirely alien grammar.

## Operational implication, counterargument and limits

A valid aggregate duration, correct local splits and a globally aligned event schedule are three distinct claims. An operational receipt should name the clock domain, exact boundaries or interval bounds, rounding policy and cumulative discrepancy; local conformance alone is insufficient for a global deadline. Do not interpret the fictional authority of an oscillator as authorization of an external action.

A future synthetic experiment could compare a typed event ledger with hierarchical visualization and optional acoustic residue cues. Hold total duration and local balance constant, vary prefix discrepancy, compare correct deadline judgments, false action, abstention, workload and preference separately. Include a negative control where the audio is absent or deliberately misleading while the ledger remains correct. A conventional ledger may provide the complete engineering solution. No human study, acoustic advantage, or canonical empirical result established.

The miniature is not a dyadic tree. Bachelard explicitly rejects a merely geometrical understanding of the poetic image, and his miniature's interiority cannot be established by the integer census. The mathematical construction contradicts the ideal of an independent world insofar as every descendant remains constrained by the root's budget. An artist could deliberately remove that restriction; an operational timing system cannot silently do so.

## Checkpoint

Base 495a98ca12bae467a507031f04931aa4254b1866. Reconciled live AGENTS, RAG, programme, runbook, research integrity, validation and frozen-protocol index; 40 recent PR results and 25 updated open issue results; targeted issue searches including Bachelard, miniature, Nancarrow, dyadic, hierarchy/rounding, zoom, and nearby artistic approaches. Read #721 and its comments and companion PR description: that investigation concerns hierarchical observation ambiguity and musical mass, not local allocation versus globally aligned phase. Search is bounded, not a comprehensive novelty audit.

Only this directory is changed. Single AI agent, no subagents or human review. Standalone execution passed twice; executed source blob d01d4ccf4d3f07d93f6ef7c624d7030c4a0efd78 matched committed source readback. No protocol, corpus, manifest or shared registry changes. Independent mergedown, exact-head CI and review remain gates. No human action required for this bounded exploratory work.

*The clockmaker measured the room. The musician entered it. The clockmaker asked how long she would stay. She said that inside, she had found another clock.*
