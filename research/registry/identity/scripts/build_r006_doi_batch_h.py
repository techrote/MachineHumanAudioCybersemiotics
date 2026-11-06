"""Fixed twelve-source metadata identity batch H; bibliography cases stay deferred."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_new_publications as engine

PLAN=engine.AREA+'/R006-DOI-H-PLAN-20261106.json'
LEDGER=engine.AREA+'/R006-DOI-H-20261106.json'
AID='AID-R006-DOI-H-20261106'
OPTIONS={
    'plan_path':PLAN,'ledger_path':LEDGER,'assistance_id':AID,
    'actor':{'kind':'agent','id':'codex-r006-doi-h-20261106','model':'GPT-6',
             'tool':'Codex; sequential Crossref bibliographic metadata and retained-export identity comparison'},
    'expected_counts':(12,25,9),
    'task':'Verify twelve metadata-only publication identities and resolve 25 fixed DOI/full-title occurrences, deferring nine bibliography cases for separate provenance checks.',
    'verification_steps':[
        'Twelve sequential Crossref single-work requests returned HTTP 200; retained selected bibliographic derivatives and original-response hashes. Abstracts, chapters and articles not read.',
        'Checked original export/page hashes, payloads, ordinals/work IDs, explicit DOI and full title under case/whitespace normalization only. No competing existing DOI assertions or exact normalized source titles found.',
        'Preserved original discovery dates and separate print/online/issued metadata. Two book chapters retain that publication type; original OpenAlex type labels remain unchanged.',
        'Two R004 lookup occurrences for the returned Edworthy 1994 chapter retain the original 1991/1993 query labels; no discovery-field or date harmonization.',
        'Nine bibliography occurrences remain explicitly deferred. Captures retain deposited subtitle fields when present; no title expansion or fuzzy matching applied. No source alias, eligibility, study/sample or corpus decision introduced.',
    ],
}


def build(root,at):
    return engine.build(root,at,**OPTIONS)


if __name__=='__main__':
    engine.main(root=ROOT,build_options=OPTIONS)
