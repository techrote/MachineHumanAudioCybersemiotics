"""Fixed nineteen-source metadata identity batch G; bibliography cases stay deferred."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research.registry.identity.scripts import build_r006_new_publications as engine

PLAN=engine.AREA+'/R006-DOI-G-PLAN-20261106.json'
LEDGER=engine.AREA+'/R006-DOI-G-20261106.json'
AID='AID-R006-DOI-G-20261106'
OPTIONS={
    'plan_path':PLAN,'ledger_path':LEDGER,'assistance_id':AID,
    'actor':{'kind':'agent','id':'codex-r006-doi-g-20261106','model':'GPT-6',
             'tool':'Codex; sequential Crossref bibliographic metadata and retained-export identity comparison'},
    'expected_counts':(19,51,6),
    'task':'Verify nineteen metadata-only publication identities and resolve 51 fixed DOI/full-title occurrences, deferring six bibliography cases and holding three correction-related occurrences.',
    'verification_steps':[
        'Twenty sequential Crossref single-work requests returned HTTP 200; retained selected bibliographic derivatives and original-response hashes. Abstracts, chapters and articles not read.',
        'Checked original export/page hashes, payloads, ordinals/work IDs, explicit DOI and full title under case/whitespace normalization only. No competing existing DOI assertions or exact normalized source titles found.',
        'Preserved original discovery dates and separate print/online/issued metadata. Five proceedings articles retain conference-paper type; original OpenAlex type labels remain unchanged.',
        'Six bibliography occurrences remain explicitly deferred; three Ferreira occurrences are not admitted because registration lists a correction relation. The admission engine rejects nonempty relation/update metadata for separate review. Captures retain deposited subtitle fields when present; no title expansion or fuzzy matching applied. No source alias, eligibility, study/sample or corpus decision introduced.',
    ],
}


def build(root,at):
    return engine.build(root,at,**OPTIONS)


if __name__=='__main__':
    engine.main(root=ROOT,build_options=OPTIONS)
