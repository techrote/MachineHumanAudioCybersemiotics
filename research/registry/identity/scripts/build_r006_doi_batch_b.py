"""Fixed batch B profile for the shared publication-identity builder."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_new_publications as engine

PLAN=engine.AREA+'/R006-DOI-B-PLAN-20261106.json'
LEDGER=engine.AREA+'/R006-DOI-B-20261106.json'
AID='AID-R006-DOI-B-20261106'
OPTIONS={
    'plan_path':PLAN,'ledger_path':LEDGER,'assistance_id':AID,
    'actor':{'kind':'agent','id':'codex-r006-doi-b-20261106','model':'GPT-6',
             'tool':'Codex; fresh Crossref bibliography and fixed retained-export identity comparison'},
    'expected_counts':(5,23,9),
    'task':'Verify five batch B publication identities and resolve 23 fixed DOI/full-title occurrences, deferring nine reference-list provenance cases.',
    'verification_steps':[
        'Retrieved five successful HTTP 200 Crossref single-work metadata derivatives; initial Alseid 429 and missing captures were followed by sequential retries after local builder work.',
        'Checked retained original export/page hashes, ordinals/work IDs, explicit DOI and full title before source linking. Abstracts and article texts were not read.',
        'Preserved print/online/issued dates and original discovery; correctly recorded the Hofmann book chapter. Nine reference-list occurrences remain explicitly deferred.',
    ],
}


def build(root,at):
    return engine.build(root,at,**OPTIONS)


if __name__=='__main__':
    engine.main(root=ROOT,build_options=OPTIONS)
