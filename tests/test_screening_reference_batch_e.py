"""Batch E bibliography partition, four witnesses and preserved model-rendered entries."""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_reference_batch_e as C

ROOT=Path(__file__).resolve().parents[1]
E=C.engine


class ReferenceBatchETests(unittest.TestCase):
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

    def test_eight_duplicates_four_targets_and_no_scientific_entities(self):
        self.assertEqual(len(self.ledger['occurrences']),8)
        self.assertEqual(len({o['source_ref']['id'] for o in self.ledger['occurrences']}),4)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*8+['assistance'])
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

    def test_four_model_rendered_entries_are_corroborated_without_transcription_claim(self):
        rows=[o for o in self.ledger['occurrences'] if o['hit_id'].startswith('HIT-R005-RLNL-')]
        self.assertEqual(len(rows),4)
        for o in rows:self.assertIn('No claim of faithful original-preprint transcription',o['verification_extent'])

    def test_four_selected_pages_match_printed_labels(self):
        receipt=read_json(ROOT/C.RECEIPT)
        self.assertEqual(len(receipt['retrievals']),1)
        self.assertEqual({(w['file_pages_1based'][0],w['printed_pages'][0]) for w in receipt['witnesses']},
                         {(44,'44'),(46,'46'),(50,'50'),(51,'51')})

    def test_two_mixed_cases_remain_outside_bibliography_scope(self):
        self.assertEqual(len(self.plan['remaining_deferred']),2)
        for i in self.plan['remaining_deferred']:
            path='research/searches/auditory/records/hits/'+i['hit_ref']['id']+'.json'
            self.assertNotIn(path,self.records)
            self.assertEqual(read_json(ROOT/path)['revisions'][0]['data']['status'],'unresolved')

    def test_parent_partition_cannot_silently_drop_title_case(self):
        with self.changed('plan',lambda p:p['remaining_deferred'].pop()) as profile:
            with self.assertRaisesRegex(ValueError,'Parent deferred scope disagreement'):self.build(profile)

    def test_missing_or_changed_identity_witness_is_rejected(self):
        for change in (lambda r:r['witnesses'].pop(),
                       lambda r:r['witnesses'][0].update(checked_doi='10.0000/fictional')):
            with self.changed('receipt',change) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_failed_pdf_and_fake_hash_cannot_support_bibliography(self):
        for change in ({'http_status':404},{'sha256':'0'*64,'expected_sha256':'0'*64}):
            with self.subTest(change=change),self.changed('receipt',lambda r:next(p for p in r['retrievals'] if p['key']=='nees-am').update(change)) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_frozen_ledger_drift_stops_all_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=9
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,profile=C.PROFILE)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
