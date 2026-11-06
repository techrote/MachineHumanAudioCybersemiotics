"""Fixed eight-citation batch E subplan with two separate title cases."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-REFERENCE-E-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-E-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-E-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-E-20261106.json',
 'aid': 'AID-R006-REFERENCE-E-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-e-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; fresh hash-matched PDF retrieval, pypdf/Poppler bibliography inspection '
                   'and retained-export comparison'},
 'cases': {'HIT-R005-RLNL-007': ['RL-NL', 'nees-bonebright'],
           'HIT-R005-RLNL-027': ['RL-NL', 'nees-spindex'],
           'HIT-R005-RLNL-057': ['RL-NL', 'nees-sun'],
           'HIT-R005-RLNL-063': ['RL-NL', 'nees-walker'],
           'HIT-R005-RLNLAM-007': ['RL-NLAM', 'nees-bonebright'],
           'HIT-R005-RLNLAM-027': ['RL-NLAM', 'nees-spindex'],
           'HIT-R005-RLNLAM-057': ['RL-NLAM', 'nees-sun'],
           'HIT-R005-RLNLAM-063': ['RL-NLAM', 'nees-walker']},
 'base': '0b088db1aa83149fea94d98c0a7aac0601970c88',
 'task': 'Verify eight deferred batch E bibliography occurrences through one freshly retrieved '
         'same-byte PDF and four visual citation witnesses.',
 'steps': ['Nees accepted manuscript returned HTTP 200 and matches retained original SHA-256 '
           'exactly.',
           'Rendered and inspected four selected citations at file/printed pages 44,46,50,51. No '
           'target-article or whole-review reading.',
           'Checked original export/hash/ordinal, full title or original model-rendered prefix, '
           'explicit DOI and existing representative. Preserved doubled DOI resolver prefix, '
           'outcome letters and all discovery fields.',
           'Eight bibliography cases plus two remaining title cases exactly partition the '
           'hash-bound parent deferred scope.'],
 'limitations': 'Four cited target publications remain metadata_only. Four RL-NL model-rendered '
                'entries receive identity corroboration only (three truncated titles, one full '
                'title); no faithful preprint transcription or review-version equivalence. '
                'PDF/renders not committed; no independent human verification, eligibility, '
                'study/sample identity or corpus acceptance.',
 'counts': {'occurrences': 8,
            'duplicate_occurrences': 8,
            'existing_target_publications': 4,
            'source_pdf_retrievals': 1,
            'visually_checked_citation_witnesses': 4,
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
