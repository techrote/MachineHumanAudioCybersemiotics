# Related theory and counter-positions — MHAC-R004

[Protocol §7](../../protocol/PROTOCOL-v1.md#7-track-g-theoretical-sampling-and-concept-revision) · [Concept register](../../protocol/CONCEPT_REGISTER.md) · [Source map CSV](SOURCE-MAP-R004.csv) · [Concept map CSV](CONCEPT-MAP-R004.csv) · [Search lane](../../searches/related/README.md) · [Access ledger](../../searches/related/exports/ACCESS-LEDGER-R004-2026-10-13.csv) · [Overlap matrix](../../novelty/OVERLAP_MATRIX.md)

**A bounded comparison corpus, mostly unread.** R004 identifies, verifies and positions 75 new sources (plus four R002 records) for the Track G comparison in #8. Seven sources were read at passage level, 16 at abstract level, and 51 not at all; role statements for unread sources are orientations to be source-checked, not findings. No philosophical convergence or incompatibility is asserted here: the [concept map](#6-concept-and-source-map-for-8) flags apparent equivalences as hypotheses for #8.

## Contents

| § | Section | One-line summary |
|---|---|---|
| 1 | [Method actually used](#1-method-actually-used) | Candidate list from protocol §7.1, Brier's reference lists, identity lookups, 31 web searches, lawful fetches. |
| 2 | [Corpus at a glance](#2-corpus-at-a-glance) | Counts by tier, cluster, identity status, access and reading. |
| 3 | [T2 tracing from Brier's reference lists](#3-t2-tracing-from-briers-reference-lists) | What Brier actually cites, which T2 works are recorded, and conflicts in his citations. |
| 4 | [Sources and their roles](#4-sources-and-their-roles) | Every source with its role, access and reading extent, by tier. |
| 5 | [Negative cases (§7.3)](#5-negative-cases-73) | One or more disconfirmation searches per cluster, what they found and what changed. |
| 6 | [Concept and source map for #8](#6-concept-and-source-map-for-8) | Grounding, feedback, situated interpretation, system boundaries, non-human audio and more; equivalences flagged. |
| 7 | [Theoretical sampling log and stopping rationale](#7-theoretical-sampling-log-and-stopping-rationale) | How the sample grew, why R004 stops here, kept apart from Track E completeness. |
| 8 | [Unavailable texts and secondary reliance](#8-unavailable-texts-and-secondary-reliance) | What could not be obtained and where a secondary account stands in for a primary text. |
| 9 | [Hand-offs](#9-hand-offs) | What #5, #6, #7 and #8 receive, including corrections to earlier records. |
| 10 | [Files and reproduction](#10-files-and-reproduction) | Scripts, exports, derived files and validation commands. |
| 11 | [Limits and independence](#11-limits-and-independence) | What this work package cannot support. |

## 1. Method actually used

All network steps ran on 2026-10-13 between 06:38 and 07:11 UTC in one agent session, under the frozen [protocol v1](../../protocol/PROTOCOL-v1.md) §7 (Track G theoretical sampling). No bibliographic database was used (gate `HG-R002-DATABASE-ACCESS`), and no forward citation tracing was possible.

| Step | What was done | Records and files |
|---|---|---|
| Candidate list | 57 candidates drawn from the §7.1 tiers, the R002 seeds and the RQ1–RQ6 dependencies | [`candidates_r004.py`](scripts/candidates_r004.py) |
| T2 tracing | Downloaded three Brier articles from their open-access locations, hashed them and parsed every reference-list entry (150 + 77 + 64) | `SRCH-R004-BRLIR2013`, `-BRLSK2015`, `-BRLGL2015AM`; [`BRIER-REFLISTS-R004.json`](../../searches/related/exports/BRIER-REFLISTS-R004.json) |
| Identity lookups | 81 known-item queries kept byte-for-byte: 56 first-round (Crossref or Open Library), 10 field-scoped, 12 for counter-position finds (Crossref, arXiv API) and 3 for the second negative batch | `SRCH-R004-LK*`; [lookup manifest](../../searches/related/exports/lookups/MANIFEST.json) |
| Abstract reading | 34 single-DOI Crossref work records fetched to read deposited abstracts; 11 carried one. Files are not committed because abstracts belong to publishers; hashes are | Lookup manifest, `work_records` |
| Web searches | 31 runs: 14 negative-case, 9 discovery, 8 access; titles and URLs kept in returned order | `SRCH-R004-G01`…`G31`; [web log](../../searches/related/exports/RELATED-WEBSEARCH-2026-10-13.json) |
| Fetches | Open copies fetched where the host or licence made that lawful; refusals and bot protection were not bypassed; third-party copies and proxy mirrors were not opened | [Access ledger](../../searches/related/exports/ACCESS-LEDGER-R004-2026-10-13.csv), 38 rows |
| Adjudication | Lookup results and web occurrences matched to source records by title, author, year or stable identifier; 167 of 818 occurrences resolved | `HIT-R004-*`; [`build_r004_records.py`](scripts/build_r004_records.py) |

Identifiers were taken from retained responses or the fetched files, never typed from memory. That check caught two DOIs remembered wrongly before the lookups (Hellier et al. 1993; Edworthy and Hellier 2006).

## 2. Corpus at a glance

| Tier | New records | Clusters |
|---|---|---|
| T2 works Brier cites (candidate dependencies) | 18 | Peirce 5, cybernetics 5, autopoiesis 4, information 2, biosemiotics 2 |
| T3 comparators | 31 (+2 R002) | human factors 9, grounding 7, anthropomorphism 6, semiotic engineering 4 (+2), information 3, embodiment 2 |
| T4 reception, criticism, contrary evidence | 17 | anthropomorphism 8, grounding 3, biosemiotics 2, autopoiesis, cybernetics, Peirce, embodiment 1 each |
| T5 auditory-display semiotics | 9 (+2 R002) | auditory semiotics |

| Property | Counts (75 new records) |
|---|---|
| Identity | 63 verified, 7 candidate, 5 conflict |
| Access | 47 metadata only, 16 abstract only, 8 full text available, 3 not attempted, 1 unavailable |
| Reading | 7 passage-level, 16 abstract, 1 read through its preprint record, 51 not read |
| Rights | 6 with an open licence verified (CC BY or CC BY-NC-SA), 69 unknown; no source bytes are committed |

Passage-level reading, with locators in each record: Atkin's encyclopedia entry on Peirce's theory of signs (§§1.3, 4.2, 4.3), Clark and Brennan (1991), Kolchinsky and Wolpert (arXiv v3), Sanz-Segura et al. (2022), Hermann (2008), Kühne et al. (2020) and Traum's paper on the contribution model.

## 3. T2 tracing from Brier's reference lists

Brier's lists were parsed from hashed files: *Integral Review* 2013 (`SRC-BRIER-2013-IR`, 150 entries), *Studia kulturoznawcze* 2015 (`SRC-NOV-BRIER-2015`, 77) and the *Green Letters* 2015 accepted manuscript (`SRC-BRIER-2015-GL-AM`, 64). Entry splitting is heuristic: a few entries are merged and some running heads remain.

**Recorded T2 works and how often Brier's lists name them** (resolved occurrences): Peirce, *Collected Papers* via the 1994 Intelex reproduction (5); Shannon and Weaver 1949 including Weaver's essay (4); Maturana and Varela 1980 (3); Maturana 1988a and 1988b (3 each); Luhmann 1995 (3); Short 2007 (3); *Essential Peirce* vol. 2 (2); Peirce's *Writings* (2); Bateson (2); Hoffmeyer 1996 (2); Kull et al. (2); Spencer-Brown (2); Wiener (2); von Foerster 1984 (1); Barbieri 2008 (1).

**Most-cited first authors** ([derived tally](BRIER-CITED-AUTHORS-R004.csv), self-citations included): Brier 31, Maturana 14, Peirce 11, Sebeok 9 (IR 2013 only), Hoffmeyer 8, Popper 7, Luhmann 6, Bhaskar 5, Prigogine 5. A block of Peirce scholars — Boler, Brent, Colapietro, Corrington, Deledalle, Esposito, Fisch, Hookway, Liszka, Savan and Short — appears once in each of the three lists.

**Cited but not recorded in R004:** Sebeok, Deely, Nöth, Popper, Bhaskar, Prigogine, Eigen, Küppers, Lorenz, Whitehead and the Peirce scholars other than Short. §7.1 admits a T2 work by "actual citation dependency in T1 passages read"; citation alone does not show that an argument depends on a work, and the T1 passages are #7's to read. #7 should add any of these whose passages carry a premise.

**Conflicts kept, not resolved** (each in its source record):

| Record | Conflict |
|---|---|
| `SRC-REL-MATURANA-1988A` | Brier gives *Irish Journal of Psychology* 9(1):25–82 for both 1988a ("Ontology of observing") and 1988b ("Reality"); Crossref shows only "Reality" at those pages and no record with the 1988a title. |
| `SRC-REL-BATESON-1972` | The same Paladin edition is dated 1972 in the IR 2013 list and 1973 in the GL 2015 manuscript. |
| `SRC-REL-FOERSTER-1984` | Brier cites 1984; Open Library gives first publication 1981; the printing Brier used is not identified. |
| `SRC-REL-KULL-2009` | The IR 2013 list dates the *Biological Theory* theses 2010 while giving 4(2) 2009; Crossref has 2009. |
| `SRC-REL-VARELA-1991` | *The Embodied Mind* is commonly dated 1991; Open Library's English work records give 1992 and 2016. |

## 4. Sources and their roles

Each row's search provenance, rights and translation status are in the [source map CSV](SOURCE-MAP-R004.csv) (`search_provenance`, `rights`, `language_and_translation`). Where the reading column says "Not read", the role is an orientation drawn from the title, catalogue data or background knowledge (`role_basis`) and must be checked against the source before it supports any extraction.

### T2 — works Brier cites (candidate dependencies)

| Record | Work | Cluster | Role in the comparison | Access · reading |
|---|---|---|---|---|
| `SRC-REL-PEIRCE-CP` | Peirce (1931), *Collected Papers of Charles Sanders Peirce* | peirce | Primary source for sign, object, interpretant and the categories; the edition Brier cites (Intelex CD-ROM reproduction). | metadata only · Not read |
| `SRC-REL-PEIRCE-EP2` | Peirce (1998), *The Essential Peirce: Selected Philosophical Writings, Volume 2 (1893-1913)* | peirce | Late sign theory, including the emotional/energetic/logical interpretants (EP2:409 as quoted in ATKIN-SEP section 4.3). | metadata only · Not read; locator known only through ATKIN-SEP |
| `SRC-REL-PEIRCE-W` | Peirce (1982), *Writings of Charles S. Peirce: A Chronological Edition* | peirce | Critical edition for early sign theory (e.g. the 1867 New List). | metadata only · Not read |
| `SRC-REL-SHORT-2007` | Short (2007), *Peirce's Theory of Signs* | peirce | Secondary reconstruction of Peirce's semeiotic, cited in all three Brier lists; reading aid for #7. | metadata only · Not read |
| `SRC-REL-ATKIN-SEP` | Atkin (2006), *Peirce's Theory of Signs* | peirce | Open reference account of interpretant divisions used to check how 'interpretant' is used by Brier and the project. | full text available · Sections 1.3, 4.2 and 4.3 (paragraphs 9-11 and 43-67 of 73, with the block quotations inside them) |
| `SRC-REL-LUHMANN-1995` | Luhmann (1995), *Social Systems* | autopoiesis | Communication as an autopoietic social system; the layer Brier combines with Peirce. | metadata only · Not read |
| `SRC-REL-MATURANA-VARELA-1980` | Maturana & Varela (1980), *Autopoiesis and Cognition: The Realization of the Living* | autopoiesis | Autopoiesis and the observer; cited in all three Brier lists, so a likely source of the closure concepts #7 must trace. | metadata only · Not read |
| `SRC-REL-MATURANA-1988B` | Maturana (1988), *Reality: The Search for Objectivity or the Quest for a Compelling Argument* | autopoiesis | Maturana's observer-dependent account of reality cited by Brier (1988b). | metadata only · Not read |
| `SRC-REL-MATURANA-1988A` | Maturana (1988), *Ontology of Observing: The Biological Foundations of Self-Consciousness and the Physical Domain of Existence* | autopoiesis | Brier-cited Maturana text; its bibliographic identity must be resolved before #7 relies on it. | not attempted · Not read |
| `SRC-REL-BATESON-1972` | Bateson (1972), *Steps to an Ecology of Mind* | cybernetics | 'Difference that makes a difference' account of information; cited in two Brier lists. | metadata only · Not read |
| `SRC-REL-FOERSTER-1984` | von Foerster (1981), *Observing Systems* | cybernetics | Second-order cybernetics: cybernetics of observing systems. | metadata only · Not read |
| `SRC-REL-FOERSTER-2003` | von Foerster (2003), *Understanding Understanding: Essays on Cybernetics and Cognition* | cybernetics | Accessible collection of von Foerster's essays; checks Brier's citation family. | metadata only · Not read |
| `SRC-REL-WIENER-1948` | Wiener (1948), *Cybernetics: Or Control and Communication in the Animal and the Machine* | cybernetics | First-order cybernetics: control and communication. | metadata only · Not read |
| `SRC-REL-SPENCER-BROWN-1969` | Spencer-Brown (1969), *Laws of Form* | cybernetics | Calculus of distinction and re-entry used by Luhmann and Brier. | metadata only · Not read |
| `SRC-REL-SHANNON-1948` | Shannon (1948), *A Mathematical Theory of Communication* | information | Syntactic information on its own terms: the engineering problem that excludes meaning. | metadata only · Not read |
| `SRC-REL-SHANNON-WEAVER-1949` | Shannon & Weaver (1949), *The Mathematical Theory of Communication* | information | Book version Brier cites, with Weaver's essay (its levels of communication problems are commonly summarised as technical, semantic and effectiveness; not read here). | metadata only · Not read |
| `SRC-REL-HOFFMEYER-1996` | Hoffmeyer (1996), *Signs of Meaning in the Universe* | biosemiotics | Peircean biosemiotics; cited in two Brier lists. | metadata only · Not read |
| `SRC-REL-KULL-2009` | Kull et al. (2009), *Theses on Biosemiotics: Prolegomena to a Theoretical Biology* | biosemiotics | Programmatic statement of biosemiotics cited by Brier. | metadata only · Not read |

### T3 — comparator accounts

| Record | Work | Cluster | Role in the comparison | Access · reading |
|---|---|---|---|---|
| `SRC-REL-DESOUZA-1993` | de Souza (1993), *The semiotic engineering of user interface languages* | semiotic-engineering | Founding statement of semiotic engineering (interface as designer-to-user message). | metadata only · Not read |
| `SRC-REL-PRATES-2000` | Prates et al. (2000), *Methods and tools: a method for evaluating the communicability of user interfaces* | semiotic-engineering | Communicability evaluation method; nearest existing evaluation contract for RQ6. | metadata only · Not read |
| `SRC-REL-DESOUZA-LEITAO-2009` | de Souza & Leitão (2009), *Semiotic Engineering Methods for Scientific Research in HCI* | semiotic-engineering | Methods (SIM, CEM) for semiotic-engineering research; checks overlap N09. | metadata only · Not read |
| `SRC-REL-CLARK-BRENNAN-1991` | Clark & Brennan (1991), *Grounding in communication* | grounding | Grounding criterion, least collaborative effort and medium constraints (incl. audibility, reviewability) as the comparator for 'feedback' and 'persistence'. | full text available · PDF pp. 1-2, 5, 8-9 and the closing paragraph on PDF p. 12 (two printed pages per PDF page; constraints list on printed p. 141) |
| `SRC-REL-CLARK-SCHAEFER-1989` | Clark & Schaefer (1989), *Contributing to Discourse* | grounding | Contribution model: presentation and acceptance phases ending in mutual belief of understanding. | abstract only · Abstract |
| `SRC-REL-CLARK-1996` | Clark (1996), *Using Language* | grounding | Language use as joint action; extended account of common ground. | metadata only · Not read |
| `SRC-REL-SCHEGLOFF-1977` | Schegloff et al. (1977), *The Preference for Self-Correction in the Organization of Repair in Conversation* | grounding | Repair organisation; comparator for how a machine message could be corrected or acknowledged. | abstract only · Abstract |
| `SRC-REL-BRENNAN-HULTEEN-1995` | Brennan & Hulteen (1995), *Interaction and feedback in a spoken language system: a theoretical framework* | grounding | Grounding applied to spoken system feedback; closest theory-to-design bridge for machine speech. | metadata only · Not read |
| `SRC-REL-HARNAD-1990` | Harnad (1990), *The symbol grounding problem* | grounding | Intrinsic meaning for a symbol system versus meaning 'parasitic on the meanings in our heads'; contrasts with interactional grounding. | abstract only · Abstract |
| `SRC-REL-FLORIDI-2005` | Floridi (2005), *Is Semantic Information Meaningful Data?* | information | Philosophy-of-information account of semantic information (comparator to Brier's semiotic account of information). | metadata only · Not read |
| `SRC-REL-KOLCHINSKY-WOLPERT-2018` | Kolchinsky & Wolpert (2018), *Semantic information, autonomous agency and non-equilibrium statistical physics* | information | Formal semantic information defined by causal necessity for a system's self-maintenance. | metadata only · See the preprint record |
| `SRC-REL-KOLCHINSKY-WOLPERT-2018-ARXIV` | Kolchinsky & Wolpert (2018), *Semantic information, autonomous agency, and nonequilibrium statistical physics* | information | Readable version used for the definition of semantic information. | full text available · Abstract and introduction, PDF p. 1 |
| `SRC-REL-EDWORTHY-1991` | Edworthy et al. (1991), *Improving Auditory Warning Design: Relationship between Warning Sound Parameters and Perceived Urgency* | human-factors | Urgency as a designable function of acoustic parameters (urgency mapping, overlap N04). | abstract only · Abstract |
| `SRC-REL-HELLIER-1993` | Hellier et al. (1993), *Improving Auditory Warning Design: Quantifying and Predicting the Effects of Different Warning Parameters on Perceived Urgency* | human-factors | Psychophysical scaling of urgency per parameter (overlap N04). | abstract only · Abstract |
| `SRC-REL-EDWORTHY-HELLIER-2006` | Edworthy & Hellier (2006), *Alarms and human behaviour: implications for medical alarms* | human-factors | Human-factors account of alarm problems in medicine; candidate review for N04. | metadata only · Not read |
| `SRC-REL-VICENTE-RASMUSSEN-1992` | Vicente & Rasmussen (1992), *Ecological interface design: theoretical foundations* | human-factors | Ecological alternative: interfaces that make work-domain constraints perceivable. | metadata only · Not read |
| `SRC-REL-WICKENS-2002` | Wickens (2002), *Multiple resources and performance prediction* | human-factors | Cognitive-resource account predicting auditory versus visual time-sharing costs. | metadata only · Not read |
| `SRC-REL-GAVER-1986` | Gaver (1986), *Auditory Icons: Using Sound in Computer Interfaces* | human-factors | Auditory icons: mapping by everyday-sound resemblance (ecological account). | metadata only · Not read |
| `SRC-REL-GAVER-1993` | Gaver (1993), *What in the World Do We Hear? An Ecological Approach to Auditory Event Perception* | human-factors | Everyday versus musical listening; perceptual basis for source attribution. | metadata only · Not read |
| `SRC-REL-BLATTNER-1989` | Blattner et al. (1989), *Earcons and Icons: Their Structure and Common Design Principles* | human-factors | Earcons: abstract, learned, structured sound messages. | metadata only · Not read |
| `SRC-REL-SANZSEGURA-2022` | Sanz-Segura et al. (2022), *Design Framework for Audible Alarms: A Multidisciplinary and Integrated Approach* | human-factors | Integrated alarm design framework (event-alarm-action, criticality, priority-to-urgency); comparator for overlap N06. | full text available · Abstract (PDF p. 1), interview quotations on silencing (PDF p. 11) and framework passages (PDF pp. 13-14); term search over all pages |
| `SRC-REL-NASS-1994` | Nass et al. (1994), *Computers are social actors* | anthropomorphism | Social responses to computers regardless of believed nature. | metadata only · Not read |
| `SRC-REL-NASS-BRAVE-2005` | Nass & Brave (2005), *Wired for Speech: How Voice Activates and Advances the Human-Computer Relationship* | anthropomorphism | Voice interfaces evoke social responses (gender, personality, emotion); principal pro-social-voice comparator. | metadata only · Not read |
| `SRC-REL-EPLEY-2007` | Epley et al. (2007), *On seeing human: A three-factor theory of anthropomorphism* | anthropomorphism | When people anthropomorphise; separates listener tendency from machine features. | metadata only · Not read |
| `SRC-REL-MORI-2012` | Mori (2012), *The Uncanny Valley* | anthropomorphism | Human likeness and affinity are non-monotonic; tested in voices by KUHNE-2020. | metadata only · Not read |
| `SRC-REL-SEABORN-2021` | Seaborn et al. (2021), *Voice in Human-Agent Interaction: A Survey* | anthropomorphism | Survey of agent voice research; principal overlap check for N07. | abstract only · Abstract |
| `SRC-REL-CLARK-FISCHER-2022` | Clark & Fischer (2022), *Social robots as depictions of social agents* | anthropomorphism | Depiction account: people treat social robots as depictions of agents (base scene, depiction proper, scene depicted). | abstract only · Abstract |
| `SRC-REL-VARELA-1991` | Varela et al. (1991), *The Embodied Mind: Cognitive Science and Human Experience* | embodiment | Enactive account developed from autopoietic theory, which Brier also cites (Maturana and Varela 1980 in all three lists). | metadata only · Not read |
| `SRC-REL-PICARD-1997` | Picard (1997), *Affective Computing* | embodiment | Programme for machines that recognise and express emotion; opposing design stance to the project preference. | metadata only · Not read |
| `SRC-REL-BRANDT-1994` | Brandt (1994), *Meaning and the machine: Toward a semiotics of interaction* | semiotic-engineering | Early semiotics of human-computer interaction outside de Souza's school; comparator for interface meaning. | metadata only · Not read |
| `SRC-REL-BANSAL-2024` | Bansal et al. (2024), *Challenges in Human-Agent Communication* | grounding | Applies a communication-grounding perspective to generative AI agents and lists twelve communication challenges in both directions (abstract). | abstract only · Abstract |
| `SRC-NOV-DESOUZA-2005` | de Souza (2005), *The Semiotic Engineering of Human-Computer Interaction* | semiotic-engineering | Core semiotic engineering monograph (R002 record; metadata only). | metadata only · see record |
| `SRC-NOV-VALENTE-2009` | Valente et al. (2009), *Turn off the graphics: designing non-visual interfaces for mobile phone games* | semiotic-engineering | Semiotic engineering applied to non-visual (aural/tactile) mobile interfaces (R002 record; abstract only). | abstract only · see record |

### T4 — reception, criticism and contrary evidence

| Record | Work | Cluster | Role in the comparison | Access · reading |
|---|---|---|---|---|
| `SRC-REL-BARBIERI-2008` | Barbieri (2008), *Biosemiotics: a new understanding of life* | biosemiotics | Rival code-biology account of biological meaning; cited in Brier's IR 2013 list (Brier's own stance to be read in #7). | metadata only · Not read |
| `SRC-REL-MINGERS-2002` | Mingers (2002), *Can Social Systems Be Autopoietic? Assessing Luhmann's Social Theory* | autopoiesis | Critique of extending autopoiesis from living to social systems; relevant because Brier draws on Luhmann's social-systems theory. | abstract only · Abstract |
| `SRC-REL-SCOTT-2004` | Scott (2004), *Second-order cybernetics: an historical introduction* | cybernetics | Historical framing of the first/second-order distinction; context for judging Brier's use of it. | abstract only · Abstract |
| `SRC-REL-TADDEO-FLORIDI-2005` | Taddeo & Floridi (2005), *Solving the symbol grounding problem: a critical review of fifteen years of research* | grounding | Critical review of proposed solutions to symbol grounding. | metadata only · Not read |
| `SRC-REL-KUHNE-2020` | Kühne et al. (2020), *The Human Takes It All: Humanlike Synthesized Voices Are Perceived as Less Eerie and More Likable. Evidence From a Subjective Ratings Study* | anthropomorphism | Contrary evidence: listeners rated humanlike voices less eerie and more likable (negative case for the project's preference). | full text available · Abstract and results summary, PDF p. 1 |
| `SRC-REL-AYLETT-2019` | Aylett et al. (2019), *The right kind of unnatural: designing a robot voice* | anthropomorphism | Design position for deliberately non-human robot voices; ally of the project preference to test against KUHNE-2020. | metadata only · Not read |
| `SRC-REL-MOORE-2019` | Moore (2019), *A 'Canny' Approach to Spoken Language Interfaces* | anthropomorphism | Argues for aligning a device's visual, vocal, behavioural and cognitive affordances (the 'habitability gap'), not for maximal human likeness. | abstract only · Abstract |
| `SRC-REL-BECKER-2025` | Becker et al. (2025), *Influence of Robots’ Voice Naturalness on Trust and Compliance* | anthropomorphism | Contrary evidence: a natural robot voice was perceived as safer and increased reliance on repeated incorrect advice, with no direct trust effect (abstract). Empirical study: candidate for Track E screening in #6. | abstract only · Abstract |
| `SRC-REL-ROMEO-2025` | Romeo et al. (2025), *The Effect of Voice and Repair Strategy on Trust Formation and Repair in Human-Robot Interaction* | anthropomorphism | Contrary and mixed evidence: in-game behaviour showed more trust in a state-of-the-art synthetic voice than in the default robot voice while questionnaires indicated the opposite; human repair strategies also worked (abstract). Track E candidate for #6. | abstract only · Abstract |
| `SRC-REL-ROMEO-2023` | Romeo et al. (2023), *Putting Robots in Context: Challenging the Influence of Voice and Empathic Behaviour on Trust* | anthropomorphism | Further voice-and-trust study by the same group; title signals a challenge to voice effects on trust. Track E candidate for #6. | metadata only · Not read |
| `SRC-REL-MULLER-2014` | Müller (2014), *Which symbol grounding problem should we try to solve?* | grounding | Objection to the framing of symbol grounding; tests whether Harnad's problem is the right one for machine communication. | metadata only · Not read |
| `SRC-REL-ZHOU-2025` | Zhou (2025), *Biosemiotics, code biology, and operational interpretation* | biosemiotics | Takes the code-biology critiques of biosemiotics as reasonable and proposes 'operational interpretation' to reconcile them (abstract); tests Brier's claims about interpretation below the human level. | abstract only · Abstract |
| `SRC-REL-TRAUM-CONTRIB` | Traum (n.d.), *On Clark and Schaefer’s Contribution Model and its applicability to Human-Computer Collaboration* | grounding | Criticism of the contribution model as a design model: not an on-line model, no way to tell a contribution's current state, graded evidence poorly ordered (PDF pp. 2-4). | full text available · PDF pp. 1-4 (abstract, sections 1-4); references not read |
| `SRC-REL-PARMENTIER-2009` | Parmentier (2009), *Troubles with trichotomies: Reflections on the utility of Peirce's sign trichotomies for social analysis* | peirce | Reflections on how useful Peirce's sign trichotomies are for social analysis (title); tests fixed sign-class assignments (concept K07). | metadata only · Not read |
| `SRC-REL-DEJESUS-2015` | De Jesus (2015), *Autopoietic enactivism, phenomenology and the deep continuity between life and mind* | embodiment | Examines the life-mind continuity thesis of autopoietic enactivism; relevant to Brier's use of autopoiesis, to be read in #7. | metadata only · Not read |
| `SRC-REL-MILDNER-2024` | Mildner et al. (2024), *Listening to the Voices: Describing Ethical Caveats of Conversational User Interfaces According to Experts and Frequent Users* | anthropomorphism | Interview study of ethical caveats in conversational user interfaces (risks that exploit trust); ethics comparator for human-like machine speech. | abstract only · Abstract |
| `SRC-REL-FERRARIO-2026` | Ferrario et al. (2026), *A Scoping Review of the Ethical Perspectives on Anthropomorphising Large Language Model-Based Conversational Agents* | anthropomorphism | Scoping review: ethical concerns (deception, overreliance) and claimed benefits of anthropomorphic agents; reports divergent operationalisations (abstract). | abstract only · Abstract |

### T5 — semiotics of auditory display

| Record | Work | Cluster | Role in the comparison | Access · reading |
|---|---|---|---|---|
| `SRC-REL-OSWALD-2012` | Oswald (2012), *Non-Speech Audio-Semiotics: A Review and Revision of Auditory Icon and Earcon Theory* | auditory-semiotics | Prior semiotic review of auditory icons and earcons; overlap check N08. | unavailable · Not read |
| `SRC-REL-AUDITORY-SIGNS-REVIEW` | Unknown author (n.d.), *A review-based conceptual analysis of auditory signs and their design* | auditory-semiotics | Second semiotic review of auditory signs; overlap check N08. | not attempted · Not read |
| `SRC-REL-JEKOSCH-2005` | Jekosch (2005), *Assigning Meaning to Sounds — Semiotics in the Context of Product-Sound Design* | auditory-semiotics | Semiotic account of meaning in product sound. | metadata only · Not read |
| `SRC-REL-TUURI-EEROLA-2012` | Tuuri & Eerola (2012), *Formulating a Revised Taxonomy for Modes of Listening* | auditory-semiotics | Modes of listening (causal, semantic, reduced and revisions) for situated interpretation of sound. | metadata only · Not read |
| `SRC-REL-HERMANN-2008` | Hermann (2008), *Taxonomy and Definitions for Sonification and Auditory Display* | auditory-semiotics | Boundary definition of sonification versus other auditory display (system-boundary concept). | full text available · Abstract, introduction and the definition with conditions C1-C3, PDF pp. 1-2 |
| `SRC-REL-OZCAN-2012` | Özcan & van Egmond (2012), *Basic Semantics of Product Sounds* | auditory-semiotics | Semantic categories listeners assign to product sounds. | full text available · Not read |
| `SRC-REL-MURPHY-2006` | Murphy et al. (2006), *A Semiotic Approach to the Design of Non-speech Sounds* | auditory-semiotics | Semiotic design approach for non-speech interface sounds; overlap check N08. | metadata only · Not read |
| `SRC-REL-SANZSEGURA-2024` | Sanz-Segura & Manchado-Pérez (2024), *Guiding design students to sound-driven design from the base camp of semiotics* | auditory-semiotics | Semiotics as a basis for teaching sound-driven design, by two authors of SANZSEGURA-2022; overlap check N06/N08. | metadata only · Not read |
| `SRC-REL-NSS-USE-SCENARIO` | Unknown author (n.d.), *Non-speech sounds as elements of a use scenario: A semiotic perspective* | auditory-semiotics | Third semiotic treatment of interface sounds found in the ICAD collection; overlap check N08. | not attempted · Not read |
| `SRC-NOV-NAM-2010` | Nam (2010), *A semiotic analysis of sounds in personal computers: Toward a semiotic model of human-computer interaction* | auditory-semiotics | Peircean classification of interface sounds (R002 record; abstract only). | abstract only · see record |
| `SRC-NOV-VRIEND-2025` | Vriend et al. (2025), *Two Empirical Studies on Audiovisual Semiotics of Uncertainty* | auditory-semiotics | Audiovisual semiotics of uncertainty (R002 record; tool-mediated full text). | full text available · see record |

## 5. Negative cases (§7.3)

Protocol §7.3 requires at least one disconfirming or rival search per concept cluster and a record of what changed. Every cluster used in this corpus has one.

| Run | Cluster (register) | Query target | What was found | Effect on the interpretation |
|---|---|---|---|---|
| G-01 | Semiotic engineering (K02, K04) | Critiques of semiotic engineering | Methods chapters, applications and theses; no substantive critique | None. The N09 redundancy risk stands untested. |
| G-02 | Autopoiesis (K03) | Critique of transferring autopoiesis to social systems | Mingers (2002), abstract read | Keeps the transfer question open for #8: whether social or technical systems can be autopoietic at all. |
| G-03 | Grounding (K02) | Critical reviews of symbol grounding | Taddeo and Floridi (2005); Müller (2014) | Symbol grounding separated from interactional grounding (CM01, CM02). |
| G-15 | Grounding (K04, K06) | Asymmetry of common ground between people and machines | Bansal et al. (2024), abstract; Traum, read | Traum argues that the contribution model cannot tell a contribution's state on-line (PDF p. 3). This constrains any state model that relies on acknowledgement (CM03, CM11). |
| G-06 | Anthropomorphism (K08) | Evidence that human-like voices raise trust or compliance | Becker et al. (2025) and Romeo et al. (2025), abstracts | Contrary and mixed evidence recorded. N07 moves from `unknown` to `partly_covered`. The studies go to #6 as Track E candidates. |
| G-16 | Anthropomorphism (K08) | Ethics of deceptive anthropomorphism | Mildner et al. (2024), Ferrario et al. (2026), abstracts | Ethics comparators recorded. The scoping review reports both risks and claimed benefits, so the project's preference is not presumed safer. |
| G-07 | Biosemiotics (K02, K03) | Code biology against Peircean biosemiotics | Zhou (2025), abstract; Brier (2015, R003 record) | Zhou treats the code-biology critiques as reasonable. #7 must test Brier's claims about interpretation below the human level against them. |
| G-13 | Cybernetics (K03) | Objections to second-order cybernetics | A third-order cybernetics paper that Crossref could not find, mailing-list threads | Executed but no verifiable counter-position recorded. This is a scope gap (§7). |
| G-14 | Information (K01) | Critiques of Weaver's levels and of meaning in Shannon's theory | Engineering "semantic communication" preprints | Not added: the engineering sense of "semantic" is a terminology hazard for #8, not a rival account of meaning. |
| G-27 | Peirce (K02, K07) | Objections to applying Peirce's semiotics to machines | Parmentier (2009), Brandt (1994), metadata | Fixed sign-class assignments remain contested (register P4). Atkin §4.3 adds that Peirce's late typology is itself unsettled. |
| G-28 | Embodiment (K05) | Critiques of enactivism and autopoietic cognition | De Jesus (2015), metadata; other records unverified | Limited. The life–mind continuity thesis is flagged for #8. |
| G-29 | Auditory semiotics (K07) | Evidence comparing auditory icons and earcons | Empirical learnability and memory studies | These are Track E studies; flagged for #6 (several already appear in R005's searches). |
| G-30 | Human factors (K09) | Speech versus tonal warnings | Empirical response-time studies and reports | Track E hand-off; no Track G change. |
| G-31 | Auditory semiotics (K07) | Critiques of semiotic classification of interface sounds | Oswald (2012) again, Parmentier (2009), Nam (2010) | No explicit critique of Peircean sound classes beyond Parmentier's general one. N08 stands. |

## 6. Concept and source map for #8

The [concept map](CONCEPT-MAP-R004.csv) has 12 rows. Each names the project concept and its register ID, the comparator concept, the sources, exactly what was read, the apparent relation, and the question #8 must settle. **Every relation below is a hypothesis.** "Analogous", "incompatible" and "equivalent" are flags for #8, not conclusions.

| Map | Project concept | Apparent relation flagged for #8 |
|---|---|---|
| CM01–CM02 | Grounding | One word for two problems: interactional grounding (Clark and Brennan PDF p. 2; Clark and Schaefer abstract) and symbol grounding (Harnad abstract). Treat them as homonyms, not equivalents. |
| CM03 | Feedback | Cybernetic control, conversational evidence of understanding, and closed-loop sonification (Hermann PDF p. 1) are analogous at most. Traum's on-line state critique bears on G13. |
| CM04 | Situated interpretation | Peirce's immediate, dynamic and final interpretants (Atkin ¶¶49–56), Clark's "well enough for current purposes" and K06 are partial analogies. None is an equivalent of another. |
| CM05 | System boundaries | Operational closure of a self-producing system against the scope of an engineered signal chain (Hermann's conditions C1–C3, PDF p. 2; Sanz-Segura et al. PDF p. 14): probably incompatible senses. |
| CM06 | Non-human audio design | A tension: Kühne et al. (PDF p. 1), Becker et al. and Romeo et al. (abstracts) report advantages for human-like or natural voices against the project's preference. |
| CM07 | Interpretant | Atkin quotes Peirce (EP2:409) that every interpretant includes feeling. If that holds, listener affect is not optional on a Peircean reading. Nothing here is a claim about Brier's own position. |
| CM08 | Information | Kolchinsky and Wolpert define semantic information for a system without an interpretant (PDF p. 1). This may be incompatible with treating information as an aspect of semiosis; #7 must verify Brier's account. |
| CM09 | Urgency | Close analogue: Sanz-Segura et al. chain event criticality, informing, warning, alarming and urging sounds, and compliance with response-time bands (PDF p. 14). |
| CM10 | Human-likeness | "Human-likeness" bundles voice naturalness, attributed agency and the depicted character. Clark and Fischer's depiction account (abstract) is a third option. |
| CM11 | Persistence and lifecycle | Clark and Brennan's reviewability (PDF p. 8) concerns the message in a medium, not the state it reports. Sanz-Segura et al. show lifecycle problems only in interview quotations (PDF p. 11). |
| CM12 | Designer-to-user message | The project's message model may be a special case of semiotic engineering's metacommunication (N09). Only metadata has been read. |

Five concept-register revisions follow from this map, all nonmaterial to Track E. They are logged in the [register](../../protocol/CONCEPT_REGISTER.md#post-freeze-revision-log).

## 7. Theoretical sampling log and stopping rationale

**Separate from Track E.** Nothing in this section describes empirical search completeness, which belongs to #5 and the frozen Track E rules. Track G sampling is purposive. Its provenance is reproducible; its interpretive products are not claimed to be.

| Step | Time (UTC) | Sampling change | Why |
|---|---|---|---|
| S1 | before 06:38 | 57 candidates across T2–T5 | Protocol §7.1 tiers, R002 seeds, RQ1–RQ6 |
| S2 | 06:38–06:39 | Brier's three reference lists parsed; T2 confirmed against actual citations | §7.1 requires citation dependency, not assumed influence |
| S3 | 06:40–06:41 | R1: 18 discovery and negative-case searches across the clusters | §7.3 negative cases; filling clusters |
| S4 | 06:41–06:45 | First and second identity rounds; conflicts recorded (§3) | Verify identity before roles are written |
| S5 | 06:45–06:49 | R2–R3: access searches; open copies fetched; Oswald (2012) found unavailable | Lawful access to comparators that #8 must read |
| S6 | 06:51–06:53 | Deposited abstracts read for 27 adjudicated DOIs | Lowest-cost reading for role statements |
| S7 | 07:05–07:08 | 12 additions from the negative and access finds (Becker, Romeo ×2, Müller, Zhou, Traum, Bansal, Mildner, Ferrario, Murphy, Sanz-Segura 2024, a candidate ICAD paper) | Each tests a concept: grounding, anthropomorphism, biosemiotics or auditory semiotics |
| S8 | 07:09–07:10 | R4: negative cases for clusters without one; Parmentier, Brandt and De Jesus added | §7.3 coverage for Peirce, embodiment, K07 and K09 |

**Stopping (§7.4).** No cluster meets the stopping rule, and none is claimed to:

- **(a) is not met.** It needs every core T1 text read or covered by an access-gap record. That reading is #7's.
- **(b) cannot be judged.** It asks whether the last two additions brought a new construct. Most additions are unread, so this cannot be assessed.
- **(c) is met.** Every cluster has a logged negative-case search (§5).
- **(d) is met.** The scope statement is this memo, with the not-sampled list in §3 and §8.

R004 stops sampling at this point because a corpus large enough to frame #8 exists, the identity work is done, and further additions would be unread titles. Sampling resumes in #7 and #8 under the same log conventions as passages are read; each new addition must again record why, which concept it tests and how it was found.

**Not sampled, and why.** No Danish- or German-language literature. No standards documents were sought; alarm standards are usually sold, and none was obtained. No full HCI semiotics beyond the items listed. The engineering "semantic communication" line is a terminology issue (G-14). Track E empirical studies belong to #5/#6.

## 8. Unavailable texts and secondary reliance

| Item | Status | Consequence |
|---|---|---|
| Oswald (2012), ICAD review of auditory-icon and earcon theory | Unavailable: the author's PDF host does not resolve; ICAD 2012 page HTTP 500; Georgia Tech repository API HTTP 500 (ledger rows 28, 29, 33) | N08 overlap cannot be judged; owner access or a working repository route needed |
| *Review-based conceptual analysis of auditory signs*; *Non-speech sounds as elements of a use scenario* | Titles only, from the Georgia Tech repository (script-rendered; API refused) | Identity unverified (candidate) |
| de Souza (1993, 2005), Prates et al. (2000), de Souza and Leitão (2009) | Metadata only; the ACM archive page refused (ledger 26); no open copy located | N09 cannot be judged; the core chapters are a priority for #8 |
| Brennan and Hulteen (1995) | Metadata only; portal page script-rendered | The closest grounding-for-speech comparator is unread |
| Seaborn et al. (2021) | Abstract only; repository file HTTP 500 (ledger 21) | N07 relies on the abstract |
| Becker et al. (2025), Romeo et al. (2025) | Abstracts only; ACM PDFs refused with HTTP 403 (ledger 36) although both carry open licences | Contrary evidence is abstract-level |
| Mingers (2002) | Abstract only; repository holds no file (ledger 24) | Critique known only by abstract |
| Harnad (1990) | Abstract only; arXiv PDF HTTP 404 (ledger 18) | — |
| Peirce primary texts (CP, EP2, W) | Not consulted | **Secondary reliance:** interpretant divisions come from Atkin's encyclopedia entry (§§1.3, 4.2–4.3), which quotes EP2 and CP. Per §7.1 this does not substitute for the primary text; #7/#8 must check EP2:409 and the CP passages Atkin cites. |
| Luhmann, Maturana and Varela, von Foerster, Bateson, Wiener, Spencer-Brown, Shannon | Catalogue metadata only | The T2 roles are orientations. Brier's use of each must be read in #7 before comparison. |
| Short (2007) | Metadata only; Atkin reports Short's view that the two interpretant trichotomies are distinct (¶65) | Secondary report of a secondary source. Not usable as evidence of Short's argument. |

## 9. Hand-offs

**To #6 and #5 (Track E):** Becker et al. (2025), Romeo et al. (2025), Romeo et al. (2023) and Kühne et al. (2020) are empirical studies of voice naturalness, trust, compliance and eeriness. Nineteen web occurrences on urgency, icon/earcon learnability and speech-versus-tone warnings are marked in their hit records as possible Track E studies. Eligibility is #6's decision under the frozen rules; R004 does not include or exclude them.

**To #7 (Brier):**
- **Hashed copies now exist.** Once network access opened, the workspace could download Brier files that R003 could only read through a summarising tool (see `HG-R003-BRIER-FULLTEXT`). IR 2013 (44 pp.), SK 2015 (21 pp.), GL 2015 AM (18 pp.), TJES 2019 (13 pp.) and Cobley (2010; 39 pp.) are hashed in ledger rows 3–6 and 8. The bytes are outside the repository. #7 should record them as manifestations through the amendment process, because adding a manifestation changes a source record materially.
- **Page-count correction.** `SRC-BRIER-2015-GL-AM` records "16 pages" from a tool-mediated fetch, but the hashed file has 18 PDF pages. The correction belongs with the manifestation amendment.
- **Maturana 1988a/1988b.** The citation conflict (§3) must be settled before #7 relies on either text.

**To #8:** the concept map (§6) and the source table (§4), with reading priorities: de Souza (2005) core chapters; Clark and Brennan (rest of the chapter); Brennan and Hulteen; Sanz-Segura et al. (whole framework); Kühne et al. (methods and results); EP2:409 and the CP passages Atkin cites; Mingers (2002); Oswald (2012) if access is obtained.

**To the novelty audit:** N04, N06, N07, N08, N09 and N12 were re-judged in the [overlap matrix](../../novelty/OVERLAP_MATRIX.md#revision-log).

## 10. Files and reproduction

| File | Content |
|---|---|
| [`scripts/candidates_r004.py`](scripts/candidates_r004.py) | Candidate list, lookup rounds and DOIs for abstract reading |
| [`scripts/lookup_r004.py`](scripts/lookup_r004.py) | Network lookups (`--round2`, `--round3`, `--round4`, `--abstracts`); writes responses and the manifest |
| [`scripts/build_r004_records.py`](scripts/build_r004_records.py) | Offline. Writes all `SRC-REL-*`, `SRCH-R004-*`, `HIT-R004-*` and `AID-R004-RELATED-CORPUS` records and the two derived CSVs; checks lookup hashes and web adjudications |
| [`SOURCE-MAP-R004.csv`](SOURCE-MAP-R004.csv) | Derived: tier, cluster, role, identity, access, reading, rights, translation, Brier-list count, search provenance |
| [`BRIER-CITED-AUTHORS-R004.csv`](BRIER-CITED-AUTHORS-R004.csv) | Derived: first-author tally of Brier's three lists (heuristic parse) |
| [`CONCEPT-MAP-R004.csv`](CONCEPT-MAP-R004.csv) | Hand-written interpretation (researcher_interpretation), with locators |

Rebuild and check:

```bash
python3 research/sources/related/scripts/build_r004_records.py
python3 tools/validate.py --write-exports
python3 tools/validate.py
python3 -m unittest discover -s tests
```

The build script fetches nothing. Rerunning the lookups would replace the retained responses and change their hashes, so only rerun them deliberately.

## 11. Limits and independence

- **One agent, no second check.** The work was done by one agent with no human check and no independent second screening. The source map and concept map are the agent's adjudications.
- **Discovery, not coverage.** Web searches are discovery only: US-only results, one page, no stated index coverage.
- **Unread sources.** Unread sources (51) support nothing beyond their identity. Abstract-level sources support only what their abstracts say.
- **No claims about Brier.** Nothing here states what Brier holds beyond what his reference lists show he cites. In particular, nothing implies that Brier endorsed emotion-free machine speech.
- **Coverage still depends on the database gate.** Without a citation database, neither reception nor criticism could be traced forward, and the `HG-R002-DATABASE-ACCESS` gate still limits coverage.
