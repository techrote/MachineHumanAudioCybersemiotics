"""Fixed batch C identity profile; HTML-marked candidate remains unadmitted."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_new_publications as engine
from tools.record_io import read_json, verify_artifact

PLAN=engine.AREA+'/R006-DOI-C-PLAN-20261106.json'
LEDGER=engine.AREA+'/R006-DOI-C-20261106.json'
AID='AID-R006-DOI-C-20261106'
OPTIONS={
    'plan_path':PLAN,'ledger_path':LEDGER,'assistance_id':AID,
    'actor':{'kind':'agent','id':'codex-r006-doi-c-20261106','model':'GPT-6',
             'tool':'Codex; sequential Crossref bibliography and retained-export identity comparison'},
    'expected_counts':(9,38,13),
    'task':'Verify nine batch C publication identities and resolve 38 fixed DOI/full-title occurrences. Defer 13 bibliography/venue occurrences and leave six Wilcox occurrences unadmitted because of HTML-marked metadata-title disagreement.',
    'verification_steps':[
        'Retrieved ten sequential HTTP 200 Crossref single-work bibliographic derivatives; nine publication identities have qualified full-title occurrences. No abstract or target text read.',
        'Checked original export/page hashes, ordinals/work IDs, DOI and full title under case/whitespace normalization only. No competing existing DOI assertions or exact normalized source titles found.',
        'Preserved print/online/issued assertions, original discovery and two book-chapter types. Twelve bibliography entries and one ICAD-series entry deferred for separate provenance checks.',
        'The tenth capture (Wilcox) has an HTML-marked title. All six plain discovery titles disagree under the current comparison: no tag stripping, source creation or hit resolution. Capture/hash, original hit pins and reason remain in the plan.',
    ],
}


def verify_unadmitted(root):
    # This retained tenth capture supports a deferral, not a canonical source.
    for item in read_json(root/PLAN)['not_admitted']:
        verify_artifact(root,item['capture'])


def build(root,at):
    verify_unadmitted(root)
    return engine.build(root,at,**OPTIONS)


if __name__=='__main__':
    verify_unadmitted(ROOT)
    engine.main(root=ROOT,build_options=OPTIONS)
