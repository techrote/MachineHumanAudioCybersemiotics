"""Fixed six-reference batch G profile; correction-related cases remain separate."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-DOI-G-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-G-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-G-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-G-20261106.json',
 'aid': 'AID-R006-REFERENCE-G-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-g-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; fresh hash-matched PDF retrieval, pypdf/Poppler bibliography inspection '
                   'and retained-export comparison'},
 'cases': {'HIT-R005-RLFRAPDF-032': ['RL-FRAPDF', 'fra-fagerlonn'],
           'HIT-R005-RLFRAPDF-052': ['RL-FRAPDF', 'fra-jeon'],
           'HIT-R005-RLNL-022': ['RL-NL', 'nees-hutchinson'],
           'HIT-R005-RLNLAM-022': ['RL-NLAM', 'nees-hutchinson'],
           'HIT-R005R-C9NLGENERAL-00006': ['general', 'nees-bennett'],
           'HIT-R005R-C9NLGENERAL-00021': ['general', 'nees-davidson']},
 'base': '39d6635a5897d30b5c85fe0f03526712898e2e9c',
 'task': 'Verify six deferred batch G bibliography identities through two freshly retrieved '
         'same-byte PDFs and five visually checked citation witnesses.',
 'steps': ['Both PDFs returned HTTP 200 and match retained original SHA-256 exactly.',
           'Rendered/inspected Nees AM general references at file/printed 33,35 and included list '
           '46; FRA file 36,37 (printed 28,29). Inspection limited to five selected citations.',
           'Checked original export hashes, ordinals, explicit DOI, full titles or one abbreviated '
           'prefix, source/page provenance and existing representatives. Preserved literal '
           'general-reference wording, Fagerlonn subtitle, Hutchinson outcome letter and Jeon '
           'citation page assertion.',
           'Resolved only the complete six-case deferred bibliography scope; the three Ferreira '
           'correction-related occurrences remain untouched and unadmitted.'],
 'limitations': 'No cited target article or whole review/report read; all five target source '
                'records remain metadata_only. One model-rendered short title receives '
                'publication-identity corroboration only. Source PDFs/renders not committed. No '
                'independent human verification, eligibility, version alias, study/sample '
                'identity, correction adjudication or corpus acceptance.',
 'counts': {'occurrences': 6,
            'duplicate_occurrences': 6,
            'existing_target_publications': 5,
            'source_pdf_retrievals': 2,
            'visually_checked_citation_witnesses': 5,
            'corroborated_model_abbreviations': 1,
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
