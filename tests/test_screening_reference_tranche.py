"""Bibliography identity, same-byte PDF receipts and original-render provenance."""
from contextlib import contextmanager
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('reference_tranche',ROOT/'research/registry/identity/scripts/build_r006_reference_tranche.py')
TRANCHE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(TRANCHE)


class ReferenceTrancheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/TRANCHE.LEDGER);cls.records,cls.expected=TRANCHE.build(ROOT,cls.ledger['resolved_at'])

    @contextmanager
    def changed_receipt(self,change):
        receipt=read_json(ROOT/TRANCHE.RECEIPT);change(receipt)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-receipt.json';path.write_text(json.dumps(receipt))
            with patch.object(TRANCHE,'RECEIPT',str(path)):yield

    def reader(self,suffix,change):
        def read(path):
            value=read_json(path)
            if str(path).endswith(suffix):change(value)
            return value
        return read

    def test_frozen_ledger_and_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_seven_duplicates_three_targets_no_scientific_entities(self):
        self.assertEqual(len(self.ledger['occurrences']),7)
        self.assertEqual(len({o['source_ref']['id'] for o in self.ledger['occurrences']}),3)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*7+['assistance'])
        for o in self.ledger['occurrences']:
            self.assertEqual(self.records[o['path']]['revisions'][1]['data']['status'],'duplicate')
        for field in ('new_source_records','screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][field],0)

    def test_original_abbreviations_outcome_letters_and_discovery_are_unchanged(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(TRANCHE.digest(original),o['input_revision_sha256'])
            self.assertEqual(TRANCHE.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
        rendered=[o for o in self.ledger['occurrences'] if o['hit_id'].startswith('HIT-R005-RLNL-')]
        self.assertEqual(len(rendered),2)
        for o in rendered:
            self.assertIn('No claim of faithful original-preprint transcription',o['verification_extent'])
            self.assertIn('corroborating_reference_list',o['export_locator'])
        # No search-run or source reading/access states are silently upgraded.
        self.assertFalse(any(r['kind'] in {'source','search_run'} for r in self.records.values()))

    def test_fra_citation_keeps_both_pages_across_page_break(self):
        case=next(o for o in self.ledger['occurrences'] if o['hit_id']=='HIT-R005-RLFRAPDF-103')
        self.assertEqual(case['file_pages_1based'],[41,42])
        self.assertEqual(case['source_pdf_sha256'],'6f652a858994170816f1535405387fadf3ce417ce3642eedb594240f3d9bb0e6')

    def test_changed_pdf_bytes_cannot_support_identity(self):
        with self.changed_receipt(lambda r:r['retrievals'][0].update(sha256='0'*64)):
            with self.assertRaisesRegex(ValueError,'Same-byte source PDF receipt failed'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_failed_retrieval_cannot_support_identity(self):
        with self.changed_receipt(lambda r:r['retrievals'][0].update(http_status=403)):
            with self.assertRaisesRegex(ValueError,'Same-byte source PDF receipt failed'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_witness_doi_disagreement_is_rejected(self):
        with self.changed_receipt(lambda r:r['witnesses'][0].update(checked_doi='10.1234/fictional-wrong')):
            with self.assertRaisesRegex(ValueError,'PDF witness identity disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_impossible_witness_page_is_rejected(self):
        with self.changed_receipt(lambda r:r['witnesses'][0].update(file_pages_1based=[999])):
            with self.assertRaisesRegex(ValueError,'PDF witness page bounds disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_changed_original_abbreviation_cannot_be_silently_repaired(self):
        def change(row):row['revisions'][0]['data']['raw_metadata']='Fictional altered rendering'
        with patch.object(TRANCHE,'read_json',self.reader('HIT-R005-RLNL-047.json',change)):
            with self.assertRaisesRegex(ValueError,'Original reference export disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_frozen_count_drift_prevents_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=8
        with patch.object(TRANCHE,'build',return_value=(self.records,changed)),patch.object(TRANCHE,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):TRANCHE.main()
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
