"""MHAC-R004 candidate list: key -> (cluster, tier, lookup route, query, why sampled).

Tiers follow protocol v1 §7.1 (T2 Brier dependencies, T3 comparators, T4 reception and criticism,
T5 semiotics of auditory display). Each query is a bibliographic lookup string, not a claim about
the source; identity is decided only from the retained lookup responses.
"""
CANDIDATES = {
    # T2: dependencies Brier cites in his own reference lists (IR 2013, SK 2015, GL 2015 AM).
    "PEIRCE-CP": ("peirce", "T2", "openlibrary", "Collected papers of Charles Sanders Peirce", "Cited by Brier as the Intelex CD-ROM reproduction of CP 1931-1958"),
    "PEIRCE-EP2": ("peirce", "T2", "openlibrary", "The essential Peirce selected philosophical writings volume 2 1893-1913", "Cited by Brier (SK 2015, GL 2015)"),
    "PEIRCE-W": ("peirce", "T2", "openlibrary", "Writings of Charles S. Peirce a chronological edition", "Cited by Brier (SK 2015, GL 2015)"),
    "SHORT-2007": ("peirce", "T2", "crossref", "Peirce's Theory of Signs Short 2007 Cambridge University Press", "Secondary account of sign, object and interpretant cited by Brier"),
    "ATKIN-SEP": ("peirce", "T2", "web", "Peirce's Theory of Signs Stanford Encyclopedia of Philosophy Atkin", "Open reference account of interpretant typology; not cited by Brier"),
    "LUHMANN-1995": ("autopoiesis", "T2", "openlibrary", "Social systems Luhmann Stanford University Press 1995", "Cited by Brier for communication as autopoietic social system"),
    "MATURANA-VARELA-1980": ("autopoiesis", "T2", "crossref", "Autopoiesis and Cognition: The Realization of the Living Maturana Varela 1980", "Cited by Brier for autopoiesis and the observer"),
    "MATURANA-1988": ("autopoiesis", "T2", "crossref", "Ontology of observing: the biological foundations of self-consciousness Maturana 1988 Irish Journal of Psychology", "Cited by Brier (1988a)"),
    "BATESON-1972": ("cybernetics", "T2", "openlibrary", "Steps to an ecology of mind Bateson", "Cited by Brier: difference that makes a difference"),
    "FOERSTER-1984": ("cybernetics", "T2", "openlibrary", "Observing systems von Foerster 1984", "Cited by Brier (SK 2015)"),
    "FOERSTER-2003": ("cybernetics", "T2", "crossref", "Understanding Understanding: Essays on Cybernetics and Cognition von Foerster 2003", "Later collection of von Foerster's essays; checks Brier's citation family"),
    "WIENER-1961": ("cybernetics", "T2", "openlibrary", "Cybernetics or control and communication in the animal and the machine Wiener second edition", "Cited by Brier (1963 printing)"),
    "SPENCER-BROWN-1969": ("cybernetics", "T2", "openlibrary", "Laws of form Spencer-Brown", "Cited by Brier for distinction and re-entry"),
    "SHANNON-1948": ("information", "T2", "crossref", "A Mathematical Theory of Communication Shannon 1948 Bell System Technical Journal", "Original Shannon paper; Brier cites the 1949 book version"),
    "SHANNON-WEAVER-1949": ("information", "T2", "openlibrary", "The mathematical theory of communication Shannon Weaver 1949", "Cited by Brier (SK 2015, GL 2015) including Weaver's levels"),
    "HOFFMEYER-1996": ("biosemiotics", "T2", "openlibrary", "Signs of meaning in the universe Hoffmeyer", "Cited by Brier"),
    "KULL-2009": ("biosemiotics", "T2", "crossref", "Theses on Biosemiotics: Prolegomena to a Theoretical Biology Kull Deacon Emmeche Hoffmeyer Stjernfelt", "Cited by Brier"),
    "BARBIERI-2008": ("biosemiotics", "T4", "crossref", "Biosemiotics: a new understanding of life Barbieri 2008 Naturwissenschaften", "Rival code-biology position Brier cites and argues against"),
    # T3: comparator accounts.
    "DESOUZA-1993": ("semiotic-engineering", "T3", "crossref", "The semiotic engineering of user interface languages de Souza 1993", "Original semiotic engineering formulation"),
    "PRATES-2000": ("semiotic-engineering", "T3", "crossref", "A method for evaluating the communicability of user interfaces Prates de Souza Barbosa 2000", "Communicability evaluation method"),
    "DESOUZA-LEITAO-2009": ("semiotic-engineering", "T3", "crossref", "Semiotic Engineering Methods for Scientific Research in HCI de Souza Leitao", "Methods book; checks how semiotic engineering is applied"),
    "CLARK-BRENNAN-1991": ("grounding", "T3", "crossref", "Grounding in communication Clark Brennan 1991", "Grounding criterion and costs by medium"),
    "CLARK-SCHAEFER-1989": ("grounding", "T3", "crossref", "Contributing to discourse Clark Schaefer 1989 Cognitive Science", "Contribution model: presentation and acceptance phases"),
    "CLARK-1996": ("grounding", "T3", "crossref", "Using Language Clark 1996 Cambridge University Press", "Joint action account of language use"),
    "SCHEGLOFF-1977": ("grounding", "T3", "crossref", "The preference for self-correction in the organization of repair in conversation Schegloff Jefferson Sacks", "Repair organisation"),
    "BRENNAN-HULTEEN-1995": ("grounding", "T3", "crossref", "Interaction and feedback in a spoken language system: a theoretical framework Brennan Hulteen", "Grounding applied to machine speech feedback"),
    "HARNAD-1990": ("grounding", "T3", "crossref", "The symbol grounding problem Harnad 1990 Physica D", "Intrinsic meaning versus interpretable symbols"),
    "TADDEO-FLORIDI-2005": ("grounding", "T4", "crossref", "Solving the symbol grounding problem: a critical review of fifteen years of research", "Critical review of grounding proposals"),
    "FLORIDI-2005": ("information", "T3", "crossref", "Is Semantic Information Meaningful Data? Floridi 2005", "Semantic information as well-formed, meaningful and truthful data"),
    "KOLCHINSKY-WOLPERT-2018": ("information", "T3", "crossref", "Semantic information, autonomous agency and non-equilibrium statistical physics Kolchinsky Wolpert", "Formal semantic information tied to a system's viability"),
    "EDWORTHY-1991": ("human-factors", "T3", "crossref", "Improving auditory warning design: relationship between warning sound parameters and perceived urgency Edworthy Loxley Dennis", "Urgency as designable acoustic mapping"),
    "HELLIER-1993": ("human-factors", "T3", "crossref", "Improving auditory warning design: quantifying and predicting the effects of different warning parameters on perceived urgency Hellier Edworthy Dennis", "Psychophysical urgency scaling"),
    "EDWORTHY-HELLIER-2006": ("human-factors", "T3", "crossref", "Alarms and human behaviour: implications for medical alarms Edworthy Hellier", "Alarm design account from human factors"),
    "VICENTE-RASMUSSEN-1992": ("human-factors", "T3", "crossref", "Ecological interface design: theoretical foundations Vicente Rasmussen", "Ecological alternative: making constraints perceivable"),
    "WICKENS-2002": ("human-factors", "T3", "crossref", "Multiple resources and performance prediction Wickens 2002", "Cognitive resource account of auditory versus visual load"),
    "GAVER-1986": ("human-factors", "T3", "crossref", "Auditory icons: using sound in computer interfaces Gaver 1986", "Ecological mapping account of auditory icons"),
    "GAVER-1993": ("human-factors", "T3", "crossref", "What in the world do we hear? An ecological approach to auditory event perception Gaver", "Everyday listening"),
    "BLATTNER-1989": ("human-factors", "T3", "crossref", "Earcons and icons: their structure and common design principles Blattner Sumikawa Greenberg", "Abstract structured sounds"),
    "IJDESIGN-ALARM-FRAMEWORK": ("human-factors", "T3", "crossref", "Design Framework for Audible Alarms: A Multidisciplinary and Integrated Approach", "Integrated alarm framework found in R005 (overlap N06)"),
    "NASS-1994": ("anthropomorphism", "T3", "crossref", "Computers are social actors Nass Steuer Tauber 1994", "Social responses to machines"),
    "NASS-BRAVE-2005": ("anthropomorphism", "T3", "crossref", "Wired for speech: how voice activates and advances the human-computer relationship Nass Brave", "Voice interface social responses"),
    "EPLEY-2007": ("anthropomorphism", "T3", "crossref", "On seeing human: a three-factor theory of anthropomorphism Epley Waytz Cacioppo", "Determinants of anthropomorphism"),
    "MORI-2012": ("anthropomorphism", "T3", "crossref", "The Uncanny Valley Mori MacDorman Kageki 2012 IEEE Robotics Automation Magazine", "Human likeness and affinity"),
    "SEABORN-2021": ("anthropomorphism", "T3", "crossref", "Voice in Human-Agent Interaction: A Survey Seaborn", "Survey of voice research (overlap N07)"),
    "CLARK-FISCHER-2023": ("anthropomorphism", "T3", "crossref", "Social robots as depictions of social agents Clark Fischer", "Depiction account of social machines"),
    "MOORE-2017": ("anthropomorphism", "T4", "crossref", "Appropriate voices for artefacts: some key insights Moore", "Argument for appropriate rather than human-like machine voices"),
    "KUHNE-2020": ("anthropomorphism", "T4", "crossref", "The human takes it all: humanlike synthesized voices are perceived as less eerie and more likable Kuhne", "Contrary evidence favouring human-like voices"),
    "VARELA-1991": ("embodiment", "T3", "openlibrary", "The embodied mind cognitive science and human experience Varela Thompson Rosch", "Enactive alternative sharing autopoietic roots"),
    "PICARD-1997": ("embodiment", "T3", "openlibrary", "Affective computing Picard 1997", "Affective machines as a design programme"),
    # T4: reception and criticism of T2/T3 positions.
    "MINGERS-2002": ("autopoiesis", "T4", "crossref", "Can social systems be autopoietic? Assessing Luhmann's social theory Mingers", "Critique of transferring autopoiesis to social systems"),
    "SCOTT-2004": ("cybernetics", "T4", "crossref", "Second-order cybernetics: an historical introduction Scott 2004 Kybernetes", "Historical and critical framing of second-order cybernetics"),
    # T5: semiotics of auditory display.
    "NSAS-ICAD": ("auditory-semiotics", "T5", "crossref", "Non-Speech Audio-Semiotics: A Review and Revision of Auditory Icon and Earcon Theory", "Semiotic review of auditory icons and earcons (overlap N08)"),
    "REVIEW-AUDITORY-SIGNS-ICAD": ("auditory-semiotics", "T5", "crossref", "A review-based conceptual analysis of auditory signs and their design", "Conceptual analysis of auditory signs (overlap N08)"),
    "JEKOSCH-2005": ("auditory-semiotics", "T5", "crossref", "Assigning meaning to sounds: semiotics in the context of product-sound design Jekosch", "Semiotics of product sound"),
    "TUURI-EEROLA-2012": ("auditory-semiotics", "T5", "crossref", "Formulating a revised taxonomy for modes of listening Tuuri Eerola", "Modes of listening"),
    "HERMANN-2008": ("auditory-semiotics", "T5", "crossref", "Taxonomy and definitions for sonification and auditory display Hermann", "Definitions boundary for sonification"),
    "OZCAN-2008": ("auditory-semiotics", "T5", "crossref", "Basic semantics of product sounds Ozcan van Egmond", "Product sound semantics"),
}

# Second-round lookups: field-scoped Open Library queries ("title|author") for books the free-text
# query missed, and Crossref queries refined after the first round.
ROUND2 = {
    "LUHMANN-1995": ("openlibrary-ta", "Social systems|Niklas Luhmann"),
    "FOERSTER-1984": ("openlibrary-ta", "Observing systems|Heinz von Foerster"),
    "PICARD-1997": ("openlibrary-ta", "Affective computing|Rosalind Picard"),
    "SPENCER-BROWN-1969": ("openlibrary-ta", "Laws of form|Spencer-Brown"),
    "SHANNON-WEAVER-1949": ("openlibrary-ta", "The mathematical theory of communication|Claude Shannon"),
    "VARELA-1991": ("openlibrary-ta", "The embodied mind|Francisco Varela"),
    "NASS-BRAVE-2005": ("openlibrary-ta", "Wired for speech|Clifford Nass"),
    "CLARK-1996": ("openlibrary-ta", "Using language|Herbert H. Clark"),
    "SHORT-2007": ("openlibrary-ta", "Peirce's theory of signs|T. L. Short"),
    "MOORE-2017": ("crossref", "The right kind of unnatural: designing a robot voice"),
}

# Round 3: identity checks for counter-position and neighbouring items surfaced by the Track G
# negative-case and access searches (run labels in RELATED-WEBSEARCH-2026-10-13.json).
ROUND3 = {
    "VOICE-NATURALNESS-TRUST": ("crossref", "Influence of Robots' Voice Naturalness on Trust and Compliance"),
    "VOICE-REPAIR-TRUST": ("crossref", "The effect of voice and repair strategy on trust formation and repair in human-robot interaction"),
    "THIRD-ORDER-CYBERNETICS": ("crossref", "There's nothing like the real thing: revisiting the need for a third-order cybernetics"),
    "WHICH-SGP": ("crossref", "Which symbol grounding problem should we try to solve?"),
    "CODE-BIOLOGY-OPERATIONAL": ("crossref", "Biosemiotics, code biology, and operational interpretation"),
    "CODES-NOT-SUFFICIENT": ("crossref", "Codes: necessary, but not sufficient for meaning-making"),
    "PEIRCEAN-LISTENING": ("crossref", "Listening and interpretation: a Peircean semiotic model for the analysis of listening"),
    "NSS-USE-SCENARIO": ("crossref", "Non-speech sounds as elements of a use scenario: a semiotic perspective"),
    "SOUND-DRIVEN-DESIGN": ("crossref", "Guiding design students to sound-driven design from the base camp of semiotics"),
    "HAC-CHALLENGES": ("arxiv", "2412.10380"),
    "CUI-ETHICAL-CAVEATS": ("arxiv", "2401.14746"),
    "ANTHRO-LLM-ETHICS": ("arxiv", "2601.09869"),
}

# Round 4: identity checks for items surfaced by the second batch of negative-case searches.
ROUND4 = {
    "SEMIOTICA-2009-070": ("crossref-doi", "10.1515/semi.2009.070"),
    "MEANING-AND-MACHINE": ("crossref", "Meaning and the machine: toward a semiotics of interaction"),
    "AUTOPOIETIC-ENACTIVISM": ("crossref", "Autopoietic enactivism, phenomenology and the deep continuity between life and mind"),
}

# Third round: Crossref work records for adjudicated DOIs, fetched to read publisher-deposited abstracts.
ABSTRACT_DOIS = {
    "DESOUZA-1993": "10.1006/imms.1993.1082",
    "PRATES-2000": "10.1145/328595.328608",
    "BRENNAN-HULTEEN-1995": "10.1016/0950-7051(95)98376-h",
    "CLARK-SCHAEFER-1989": "10.1207/s15516709cog1302_7",
    "EDWORTHY-1991": "10.1177/001872089103300206",
    "HELLIER-1993": "10.1177/001872089303500408",
    "EDWORTHY-HELLIER-2006": "10.1093/bja/ael114",
    "VICENTE-RASMUSSEN-1992": "10.1109/21.156574",
    "WICKENS-2002": "10.1080/14639220210123806",
    "GAVER-1986": "10.1207/s15327051hci0202_3",
    "GAVER-1993": "10.1207/s15326969eco0501_1",
    "BLATTNER-1989": "10.1207/s15327051hci0401_1",
    "SEABORN-2021": "10.1145/3386867",
    "CLARK-FISCHER-2023": "10.1017/s0140525x22000668",
    "EPLEY-2007": "10.1037/0033-295x.114.4.864",
    "MORI-2012": "10.1109/mra.2012.2192811",
    "NASS-1994": "10.1145/191666.191703",
    "MINGERS-2002": "10.1111/1467-954x.00367",
    "SCOTT-2004": "10.1108/03684920410556007",
    "TADDEO-FLORIDI-2005": "10.1080/09528130500284053",
    "FLORIDI-2005": "10.1111/j.1933-1592.2005.tb00531.x",
    "BARBIERI-2008": "10.1007/s00114-008-0368-x",
    "KULL-2009": "10.1162/biot.2009.4.2.167",
    "TUURI-EEROLA-2012": "10.1080/09298215.2011.614951",
    "JEKOSCH-2005": "10.1007/3-540-27437-5_8",
    "SCHEGLOFF-1977": "10.2307/413107",
    "AYLETT-2019": "10.1145/3342775.3342806",
    # Added after the round-3 identity checks.
    "BECKER-2025": "10.1145/3706066",
    "ROMEO-2025": "10.1145/3711938",
    "ROMEO-2023": "10.1109/ro-man57019.2023.10309631",
    "MULLER-2015": "10.1080/0952813x.2014.940143",
    "ZHOU-2025": "10.1515/css-2025-2003",
    "MURPHY-2006": "10.1007/11821731_12",
    "SANZSEGURA-2024": "10.21606/drs.2024.855",
}
