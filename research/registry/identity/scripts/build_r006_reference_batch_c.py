"""Fixed batch C bibliography subplan; the ICAD venue case remains deferred."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_reference_tranche as engine

PROFILE={'plan': 'research/registry/identity/R006-REFERENCE-C-PLAN-20261106.json',
 'previous': 'research/registry/identity/R006-DOI-C-20261106.json',
 'receipt': 'research/registry/identity/R006-REFERENCE-C-WITNESSES-20261106.json',
 'ledger': 'research/registry/identity/R006-REFERENCE-C-20261106.json',
 'aid': 'AID-R006-REFERENCE-C-20261106',
 'actor': {'kind': 'agent',
           'id': 'codex-r006-reference-c-20261106',
           'model': 'GPT-6',
           'tool': 'Codex; urllib hash-matched PDF retrieval, pypdf/Poppler bibliography '
                   'inspection and retained-export comparison'},
 'cases': {'HIT-R005-RLFRAPDF-037': ['RL-FRAPDF', 'fra-graham'],
           'HIT-R005-RLFRAPDF-086': ['RL-FRAPDF', 'fra-nees'],
           'HIT-R005-RLNL-003': ['RL-NL', 'nees-amer'],
           'HIT-R005-RLNL-019': ['RL-NL', 'nees-graham'],
           'HIT-R005-RLNL-044': ['RL-NL', 'nees-nees'],
           'HIT-R005-RLNL-059': ['RL-NL', 'nees-tislar'],
           'HIT-R005-RLNLAM-003': ['RL-NLAM', 'nees-amer'],
           'HIT-R005-RLNLAM-019': ['RL-NLAM', 'nees-graham'],
           'HIT-R005-RLNLAM-044': ['RL-NLAM', 'nees-nees'],
           'HIT-R005-RLNLAM-059': ['RL-NLAM', 'nees-tislar'],
           'HIT-R005R-C9NLGENERAL-00002': ['general', 'nees-amer-general'],
           'HIT-R005R-C9TOTLAND-00002': ['totland', 'totland-bellettiere']},
 'base': '993f3cb85a547da366e2d8bf7d76718162e7ba21',
 'task': 'Verify twelve batch C bibliography occurrence identities using three freshly retrieved '
         'hash-matched PDFs and eight visually checked citation witnesses. Keep the venue case and '
         'six HTML-title cases unresolved.',
 'steps': ['Nees AM, FRA review and Totland thesis PDFs returned HTTP 200 and match retained '
           'SHA-256 exactly. Expired Totland alias 404 was resolved through the stable public '
           'OpenFile endpoint; no access bypass.',
           'Rendered/inspected eight citation pages: Nees AM 33,43,45,49,51; FRA file 36,40 '
           '(printed 28,32); Totland file/printed 42. No target-article or whole-report/thesis '
           'reading.',
           'Checked original export/hash/ordinal, full titles or four explicitly abbreviated title '
           'prefixes, explicit DOI, source/page provenance and existing representatives. Preserved '
           'Totland citation line/box locators and literal discovery text.',
           'Pinned parent plan and required the twelve checked plus one remaining venue occurrence '
           'to partition its thirteen deferred entries without omissions/duplicates. The six '
           'Wilcox title-representation cases remain unadmitted in that parent.'],
 'limitations': 'No target article or whole report/thesis read; target source records remain '
                'metadata_only. Four model-rendered abbreviations receive identity corroboration '
                'only. One agent; no independent human review, eligibility, sample identity, '
                'version alias or corpus acceptance. Source PDFs/renders not committed; stable '
                'URLs/hashes and page locators retained.',
 'counts': {'occurrences': 12,
            'duplicate_occurrences': 12,
            'existing_target_publications': 5,
            'source_pdf_retrievals': 3,
            'visually_checked_citation_witnesses': 8,
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
