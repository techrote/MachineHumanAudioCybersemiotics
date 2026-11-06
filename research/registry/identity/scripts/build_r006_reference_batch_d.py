"""Fixed eight-reference batch D profile; all scientific boundaries remain separate."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-DOI-D-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-D-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-D-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-D-20261106.json',
 'aid': 'AID-R006-REFERENCE-D-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-d-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; fresh hash-matched PDF retrieval, pypdf/Poppler bibliography inspection '
                   'and retained-export comparison'},
 'cases': {'HIT-R005-RLFRAPDF-011': ['RL-FRAPDF', 'fra-belz'],
           'HIT-R005-RLFRAPDF-053': ['RL-FRAPDF', 'fra-jeon'],
           'HIT-R005-RLNL-008': ['RL-NL', 'nees-brewster'],
           'HIT-R005-RLNL-025': ['RL-NL', 'nees-jeon'],
           'HIT-R005-RLNLAM-008': ['RL-NLAM', 'nees-brewster'],
           'HIT-R005-RLNLAM-025': ['RL-NLAM', 'nees-jeon'],
           'HIT-R005R-C9RUSKIN-00018': ['ruskin', 'ruskin-brewster'],
           'HIT-R005R-C9TOTLAND-00003': ['totland', 'totland-belz']},
 'base': '6984dff4c55da9e8f4d03dd63b774eaead37c36f',
 'task': 'Verify eight deferred batch D bibliography occurrence identities through four freshly '
         'retrieved same-byte PDFs and six visually checked citation witnesses.',
 'steps': ['All four PDFs returned HTTP 200 and match retained original SHA-256 exactly. Totland '
           'used the stable public OpenFile endpoint and a newly issued anonymous alias; route '
           'times/status retained, alias omitted.',
           'Rendered/inspected Nees AM file/printed 44,46; FRA file 34,38 (printed 26,30); Ruskin '
           '57; Totland 42. Inspection limited to selected bibliography citations.',
           'Checked original export hashes, ordinals, explicit DOI, full title or two abbreviated '
           'prefixes, source/page provenance and existing representatives. Coordinate-bearing '
           'Ruskin/Totland citation exports and original line/box locators remain intact.'],
 'limitations': 'No cited target article or whole review/report/thesis read; all three target '
                'source records remain metadata_only. Two model-rendered short titles receive '
                'publication-identity corroboration only. Source PDFs/renders not committed. No '
                'independent human verification, eligibility, version alias, study/sample identity '
                'or corpus acceptance.',
 'counts': {'occurrences': 8,
            'duplicate_occurrences': 8,
            'existing_target_publications': 3,
            'source_pdf_retrievals': 4,
            'visually_checked_citation_witnesses': 6,
            'corroborated_model_abbreviations': 2,
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
