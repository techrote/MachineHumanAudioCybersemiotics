"""Fixed six-reference batch F profile; all scientific boundaries remain separate."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-DOI-F-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-F-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-F-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-F-20261106.json',
 'aid': 'AID-R006-REFERENCE-F-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-f-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; fresh hash-matched PDF retrieval, pypdf/Poppler bibliography inspection '
                   'and retained-export comparison'},
 'cases': {'HIT-R005-RLFRAPDF-006': ['RL-FRAPDF', 'fra-baldwin'],
           'HIT-R005-RLNL-020': ['RL-NL', 'nees-haas'],
           'HIT-R005-RLNL-039': ['RL-NL', 'nees-moskovitch'],
           'HIT-R005-RLNLAM-020': ['RL-NLAM', 'nees-haas'],
           'HIT-R005-RLNLAM-039': ['RL-NLAM', 'nees-moskovitch'],
           'HIT-R005R-C9RUSKIN-00019': ['ruskin', 'ruskin-brewster']},
 'base': 'bc6a506a1c884fd563791c8c0c6b30bb875fe803',
 'task': 'Verify six deferred batch F bibliography occurrence identities through three freshly '
         'retrieved same-byte PDFs and four visually checked citation witnesses.',
 'steps': ['All three PDFs returned HTTP 200 and match retained original SHA-256 exactly.',
           'Rendered/inspected Nees AM file/printed 45,48; FRA file 34 (printed 26); Ruskin 57. '
           'Inspection limited to four selected bibliography citations.',
           'Checked original export hashes, ordinals, explicit DOI, full title or two abbreviated '
           'prefixes, source/page provenance and existing representatives. Coordinate-bearing '
           'Ruskin citation export and original line/box locators remain intact.'],
 'limitations': 'No cited target article or whole review/report read; all four target source '
                'records remain metadata_only. Two model-rendered short titles receive '
                'publication-identity corroboration only. Source PDFs/renders not committed. No '
                'independent human verification, eligibility, version alias, study/sample identity '
                'or corpus acceptance.',
 'counts': {'occurrences': 6,
            'duplicate_occurrences': 6,
            'existing_target_publications': 4,
            'source_pdf_retrievals': 3,
            'visually_checked_citation_witnesses': 4,
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
