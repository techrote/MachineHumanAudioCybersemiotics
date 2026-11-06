"""Fixed nine-reference batch H with explicit deposited-subtitle corroboration."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-DOI-H-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-H-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-H-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-H-20261106.json',
 'aid': 'AID-R006-REFERENCE-H-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-h-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; fresh hash-matched PDF retrieval, pypdf/Poppler bibliography inspection '
                   'and retained-export comparison'},
 'cases': {'HIT-R005-RLNL-023': ['RL-NL', 'nees-isherwood'],
           'HIT-R005-RLNL-045': ['RL-NL', 'nees-neurauter'],
           'HIT-R005-RLNL-052': ['RL-NL', 'nees-understanding'],
           'HIT-R005-RLNL-053': ['RL-NL', 'nees-recognition'],
           'HIT-R005-RLNLAM-023': ['RL-NLAM', 'nees-isherwood'],
           'HIT-R005-RLNLAM-045': ['RL-NLAM', 'nees-neurauter'],
           'HIT-R005-RLNLAM-052': ['RL-NLAM', 'nees-understanding'],
           'HIT-R005-RLNLAM-053': ['RL-NLAM', 'nees-recognition'],
           'HIT-R005R-C9RUSKIN-00073': ['ruskin', 'ruskin-hickling']},
 'base': 'b638b537ea17301db9e86ec112ee2234fb2e4199',
 'task': 'Verify all nine deferred batch H bibliography identities through two freshly retrieved '
         'same-byte PDFs and five visually checked citation witnesses, with an explicit hash-bound '
         'deposited-subtitle comparison.',
 'steps': ['Both PDFs returned HTTP 200 and match retained original SHA-256 exactly.',
           'Rendered/inspected Nees AM included references at file/printed 46,49,50 and Ruskin '
           'file/printed 64. Inspection limited to five selected citations.',
           'Checked original export hashes, ordinals, explicit DOI, full titles or four '
           'abbreviated prefixes, source/page provenance, outcome letters and existing '
           'representatives. Original discovery text preserved.',
           'Sabic recognition has an explicit opt-in comparison against the title and single '
           'subtitle in its accepted hash-bound DOI capture. The shortened model title is an exact '
           'word-boundary prefix of the combined citation title; the AM witness carries the '
           'complete citation form. No fuzzy match, source title rewrite or review-version alias.',
           'Resolved only the complete nine-case deferred bibliography scope; no eligibility, '
           'access, study/sample or corpus acceptance change.'],
 'limitations': 'No cited target article or whole review/report read; all five target source '
                'records remain metadata_only. Four model-rendered titles receive '
                'publication-identity corroboration only, including one exact word-boundary prefix '
                'of the registered main-title-plus-subtitle citation form. Source PDFs/renders not '
                'committed. No independent human verification, eligibility, version alias, '
                'study/sample identity or corpus acceptance.',
 'counts': {'occurrences': 9,
            'duplicate_occurrences': 9,
            'existing_target_publications': 5,
            'source_pdf_retrievals': 2,
            'visually_checked_citation_witnesses': 5,
            'corroborated_model_abbreviations': 4,
            'new_source_records': 0,
            'screening_decisions_created': 0,
            'study_records_created': 0,
            'sample_records_created': 0}}
LEDGER=PROFILE['ledger']
RECEIPT=PROFILE['receipt']

def build(root,at):
    return engine.build(root,at,profile=PROFILE)

if __name__=='__main__':
    engine.main(root=ROOT,profile=PROFILE)
