"""Fixed reference profiles preserve old outputs and reject misleading witnesses."""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json, dumps
from research.registry.identity.scripts import build_r006_reference_batch_b as batch
from research.registry.identity.scripts import build_r006_reference_tranche as engine

ROOT=Path(__file__).resolve().parents[1]


class ReferenceBatchBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/batch.LEDGER)
        cls.at=cls.ledger['resolved_at']
        cls.records,cls.expected=batch.build(ROOT,cls.at)

    @contextmanager
    def receipt(self,change):
        receipt=read_json(ROOT/batch.RECEIPT);change(receipt)
        profile=copy.deepcopy(batch.PROFILE)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-receipt.json';path.write_text(dumps(receipt))
            profile['receipt']=str(path)
            yield profile

    def build(self,profile):
        return engine.build(ROOT,self.at,profile=profile)

    def test_batch_and_original_default_reproduce_exactly(self):
        self.assertEqual(self.expected,self.ledger)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)
        old=read_json(ROOT/engine.LEDGER)
        records,ledger=engine.build(ROOT,old['resolved_at'])
        self.assertEqual(ledger,old)
        for path,expected in records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_nine_duplicates_five_publications_and_no_source_state_changes(self):
        self.assertEqual(len(self.ledger['occurrences']),9)
        self.assertEqual(len({o['source_ref']['id'] for o in self.ledger['occurrences']}),5)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*9+['assistance'])
        for o in self.ledger['occurrences']:
            self.assertEqual(self.records[o['path']]['revisions'][1]['data']['status'],'duplicate')
            source=read_json(ROOT/f"research/registry/identity/records/{o['source_ref']['id']}.json")
            self.assertEqual(len(source['revisions']),1)
            self.assertEqual(source['revisions'][0]['data']['access_status'],'metadata_only')

    def test_all_original_fields_except_resolution_are_retained(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(engine.digest(original),o['input_revision_sha256'])
            self.assertEqual(engine.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_four_abbreviations_remain_corroboration_only(self):
        rendered=[o for o in self.ledger['occurrences'] if o['hit_id'].startswith('HIT-R005-RLNL-')]
        self.assertEqual(len(rendered),4)
        for o in rendered:
            self.assertIn('No claim of faithful original-preprint transcription',o['verification_extent'])
            self.assertEqual(o['export_locator']['corroborating_reference_list'],'RL-NLAM')
        case=next(o for o in self.ledger['occurrences'] if o['hit_id']=='HIT-R005-RLNLAM-010')
        self.assertIn('https://doi.org/https://doi.org/',self.records[case['path']]['revisions'][0]['data']['raw_metadata'])

    def test_repeated_receipt_keys_are_rejected_before_mapping(self):
        for key in ('retrievals','witnesses'):
            with self.subTest(key=key),self.receipt(lambda r:r[key].append(copy.deepcopy(r[key][0]))) as profile:
                with self.assertRaisesRegex(ValueError,'Repeated receipt identity'):self.build(profile)

    def test_failed_or_changed_pdf_cannot_support_identity(self):
        for change in ({'http_status':403},{'sha256':'0'*64},{'hash_matches':False}):
            with self.subTest(change=change),self.receipt(lambda r:r['retrievals'][0].update(change)) as profile:
                with self.assertRaisesRegex(ValueError,'Same-byte source PDF receipt failed'):self.build(profile)

    def test_witness_identity_and_page_disagreements_fail(self):
        for change in ({'checked_doi':'10.1234/fictional'}, {'file_pages_1based':[999]}):
            with self.subTest(change=change),self.receipt(lambda r:r['witnesses'][0].update(change)) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_missing_witness_cannot_shrink_declared_scope(self):
        with self.receipt(lambda r:r['witnesses'].pop()) as profile:
            with self.assertRaisesRegex(ValueError,'Receipt scope disagreement'):self.build(profile)

    def test_repeated_deferred_occurrence_cannot_hide_in_scope_set(self):
        plan=read_json(ROOT/batch.PROFILE['plan'])
        plan['deferred'].append(copy.deepcopy(plan['deferred'][0]))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-repeated-plan.json';path.write_text(dumps(plan))
            profile=copy.deepcopy(batch.PROFILE);profile['plan']=str(path)
            with self.assertRaisesRegex(ValueError,'Fixed deferred scope disagreement'):self.build(profile)

    def test_count_or_narrative_cannot_be_inherited_for_new_profile(self):
        profile=copy.deepcopy(batch.PROFILE);profile['counts']['occurrences']=8
        with self.assertRaisesRegex(ValueError,'Fixed profile count disagreement'):self.build(profile)
        profile=copy.deepcopy(batch.PROFILE);del profile['steps']
        with self.assertRaisesRegex(ValueError,'complete fixed scope and verification narrative'):self.build(profile)

    def test_profile_does_not_mutate_default_configuration(self):
        old=read_json(ROOT/engine.LEDGER);before=engine.build(ROOT,old['resolved_at'])
        profile=copy.deepcopy(batch.PROFILE);self.build(profile)
        self.assertEqual(profile,batch.PROFILE)
        self.assertEqual(engine.build(ROOT,old['resolved_at']),before)

    def test_changed_original_abbreviation_is_not_silently_repaired(self):
        def reader(path):
            value=read_json(path)
            if str(path).endswith('HIT-R005-RLNL-002.json'):
                value['revisions'][0]['data']['raw_metadata']='Fictional altered reference'
            return value
        with patch.object(engine,'read_json',reader):
            with self.assertRaisesRegex(ValueError,'Original reference export disagreement'):batch.build(ROOT,self.at)

    def test_frozen_ledger_drift_prevents_any_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=8
        with patch.object(engine,'build',return_value=(self.records,changed)),patch.object(engine,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):engine.main(root=ROOT,profile=batch.PROFILE)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
