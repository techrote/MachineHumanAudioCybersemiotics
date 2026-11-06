"""Fixed nine-reference batch B profile; source observations remain explicitly bounded."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-DOI-B-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-B-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-B-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-B-20261106.json',
 'aid': 'AID-R006-REFERENCE-B-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-b-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; urllib same-byte PDF retrieval, pypdf/Poppler bibliography inspection '
                   'and retained-export comparison'},
 'cases': {'HIT-R005-RLNL-002': ['RL-NL', 'nees-alseid'],
           'HIT-R005-RLNL-010': ['RL-NL', 'nees-edworthy'],
           'HIT-R005-RLNL-021': ['RL-NL', 'nees-hofmann'],
           'HIT-R005-RLNL-056': ['RL-NL', 'nees-suh'],
           'HIT-R005-RLNLAM-002': ['RL-NLAM', 'nees-alseid'],
           'HIT-R005-RLNLAM-010': ['RL-NLAM', 'nees-edworthy'],
           'HIT-R005-RLNLAM-021': ['RL-NLAM', 'nees-hofmann'],
           'HIT-R005-RLNLAM-056': ['RL-NLAM', 'nees-suh'],
           'HIT-R005R-C9NLGENERAL-00068': ['general', 'nees-petocz']},
 'base': '2b6128a133363c0e395743ea6952c1b026dd24d7',
 'task': 'Verify nine deferred batch B bibliography occurrence identities using one freshly '
         'retrieved hash-matched Nees accepted-manuscript PDF and five visually checked citation '
         'witnesses.',
 'steps': ['Fresh Nees AM retrieval returned HTTP 200 and matches the retained original SHA-256 '
           'exactly.',
           'Rendered and inspected Nees AM file pages 40,43,44,46,50; printed page numbers '
           'coincide. Inspection limited to five selected bibliography citations, not target '
           'articles or chapter.',
           'Checked original export hashes/ordinals, full titles or four explicitly abbreviated '
           'title prefixes, explicit DOI and existing resolved representatives. Four old '
           'model-rendered short entries receive corroboration only. The duplicated DOI URL prefix '
           'in the Edworthy citation is preserved.'],
 'counts': {'occurrences': 9,
            'duplicate_occurrences': 9,
            'existing_target_publications': 5,
            'source_pdf_retrievals': 1,
            'visually_checked_citation_witnesses': 5,
            'corroborated_model_abbreviations': 4,
            'new_source_records': 0,
            'screening_decisions_created': 0,
            'study_records_created': 0,
            'sample_records_created': 0},
 'limitations': 'No cited target article or chapter was retrieved/read; all five target source '
                'records remain metadata_only. Only selected Nees AM bibliography citations were '
                'checked. Four model-rendered abbreviations receive corroboration, not '
                'original-preprint transcription or review-version acceptance. One agent; no '
                'independent human verification, source alias, sample identity, eligibility or '
                'corpus acceptance. PDF/renders not committed; exact receipt URL/hash and page '
                'locators retained.'}
LEDGER=PROFILE['ledger']
RECEIPT=PROFILE['receipt']

def build(root,at):
    return engine.build(root,at,profile=PROFILE)

if __name__=='__main__':
    engine.main(root=ROOT,profile=PROFILE)
