"""Batch G bibliography identity, source witnesses and preserved discovery provenance."""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_reference_batch_g as C

ROOT=Path(__file__).resolve().parents[1]
E=C.engine


class ReferenceBatchGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/C.LEDGER);cls.at=cls.ledger['resolved_at']
        cls.records,cls.expected=C.build(ROOT,cls.at)
        cls.plan=read_json(ROOT/C.PROFILE['plan'])

    @contextmanager
    def changed(self,field,change):
        value=read_json(ROOT/C.PROFILE[field]);change(value)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-input.json';path.write_text(dumps(value))
            profile=copy.deepcopy(C.PROFILE);profile[field]=str(path)
            yield profile

    def build(self,profile):return E.build(ROOT,self.at,profile=profile)

    def test_frozen_ledger_and_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_six_duplicates_five_targets_and_no_scientific_entities(self):
        self.assertEqual(len(self.ledger['occurrences']),6)
        self.assertEqual(len({o['source_ref']['id'] for o in self.ledger['occurrences']}),5)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*6+['assistance'])
        for o in self.ledger['occurrences']:
            self.assertEqual(self.records[o['path']]['revisions'][1]['data']['status'],'duplicate')
            s=read_json(ROOT/f"research/registry/identity/records/{o['source_ref']['id']}.json")
            # This batch pins source revision 1; later access observations are allowed.
            self.assertEqual(s['revisions'][0]['data']['access_status'],'metadata_only')

    def test_every_original_discovery_field_and_hash_is_preserved(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_one_short_title_is_corroborated_without_transcription_claim(self):
        rows=[o for o in self.ledger['occurrences'] if o['hit_id'].startswith('HIT-R005-RLNL-')]
        self.assertEqual(len(rows),1)
        for o in rows:self.assertIn('No claim of faithful original-preprint transcription',o['verification_extent'])

    def test_fixed_plan_is_exhausted_and_witness_scope_matches(self):
        self.assertEqual({i['hit_ref']['id'] for i in self.plan['deferred']},
                         {o['hit_id'] for o in self.ledger['occurrences']})
        receipt=read_json(ROOT/C.RECEIPT)
        self.assertEqual(len(receipt['retrievals']),2)
        self.assertEqual(len(receipt['witnesses']),5)
        nees={w['file_pages_1based'][0] for w in receipt['witnesses'] if w['pdf_key']=='nees-am'}
        self.assertEqual(nees,{33,35,46})

    def test_fra_file_and_printed_pages_stay_separate(self):
        receipt=read_json(ROOT/C.RECEIPT)
        pairs={(w['file_pages_1based'][0],w['printed_pages'][0]) for w in receipt['witnesses'] if w['pdf_key']=='fra'}
        self.assertEqual(pairs,{(36,'28'),(37,'29')})

    def test_general_references_keep_their_original_ordinals_and_pages(self):
        rows=[o for o in self.ledger['occurrences'] if 'C9NLGENERAL' in o['hit_id']]
        self.assertEqual(len(rows),2)
        for o in rows:
            ordinal,page=(6,33) if '00006' in o['hit_id'] else (21,35)
            self.assertEqual(o['export_locator']['item'],ordinal)
            self.assertEqual(o['file_pages_1based'],[page])
            before,after=self.records[o['path']]['revisions']
            self.assertIn(f'source PDF pp.{page}–{page}, reference {ordinal}',after['data']['raw_metadata'])
            self.assertEqual(before['data']['raw_metadata'],after['data']['raw_metadata'])

    def test_fagerlonn_full_subtitle_and_jeon_page_assertion_remain_literal(self):
        f=next(o for o in self.ledger['occurrences'] if o['hit_id']=='HIT-R005-RLFRAPDF-032')
        text=self.records[f['path']]['revisions'][1]['data']['raw_metadata']
        self.assertIn('using sound to guide drivers without additional noise',text)
        j=next(o for o in self.ledger['occurrences'] if o['hit_id']=='HIT-R005-RLFRAPDF-052')
        text=self.records[j['path']]['revisions'][1]['data']['raw_metadata']
        self.assertIn('AutomotiveUI 2009, 91.',text)

    def test_correction_related_occurrences_are_outside_all_output_writes(self):
        held=self.plan['not_admitted'];self.assertEqual(len(held),1)
        self.assertEqual(held[0]['doi'],'10.1371/journal.pone.0281680')
        self.assertEqual(len(held[0]['hit_refs']),3)
        for ref in held[0]['hit_refs']:
            path='research/searches/auditory/records/hits/'+ref['id']+'.json'
            self.assertNotIn(path,self.records)
            self.assertEqual(read_json(ROOT/path)['revisions'][0]['data']['status'],'unresolved')

    def test_missing_or_changed_identity_witness_is_rejected(self):
        for change in (lambda r:r['witnesses'].pop(),
                       lambda r:r['witnesses'][0].update(checked_doi='10.0000/fictional')):
            with self.changed('receipt',change) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_failed_pdf_and_fake_hash_cannot_support_fra(self):
        for change in ({'http_status':404},{'sha256':'0'*64,'expected_sha256':'0'*64}):
            with self.subTest(change=change),self.changed('receipt',lambda r:next(p for p in r['retrievals'] if p['key']=='fra').update(change)) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_frozen_ledger_drift_stops_all_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=7
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,profile=C.PROFILE)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
