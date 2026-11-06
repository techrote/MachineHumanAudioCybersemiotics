"""Verify the fixed metadata-only DOI batch and reject adverse provenance."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from tools.record_io import read_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('remaining_dois', ROOT/'research/registry/identity/scripts/build_r006_remaining_dois.py')
TRANCHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRANCHE)


class RemainingDoiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = read_json(ROOT/TRANCHE.LEDGER)
        cls.records,cls.expected = TRANCHE.build(ROOT,cls.ledger['resolved_at'])

    def reader(self,suffix,change):
        def read(path):
            value = read_json(path)
            if str(path).endswith(suffix):
                change(value)
            return value
        return read

    def test_frozen_ledger_and_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual = read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_ten_occurrences_five_sources_two_representatives_eight_duplicates(self):
        rows = self.ledger['occurrences']
        self.assertEqual(len(rows),10)
        self.assertEqual(len({o['source_ref']['id'] for o in rows}),5)
        self.assertEqual(sum(o['status']=='resolved' for o in rows),2)
        self.assertEqual(sum(o['status']=='duplicate' for o in rows),8)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*10+['assistance'])
        for item in rows:
            if item['duplicate_of'] and item['duplicate_of']['rev']==2:
                target = next(o for o in rows if o['output_ref']==item['duplicate_of'])
                self.assertEqual(target['status'],'resolved')
                self.assertEqual(target['source_ref'],item['source_ref'])

    def test_original_metadata_dates_and_discovery_paths_are_unchanged(self):
        allowed = {'status','source_ref','duplicate_of','resolution_reason'}
        for item in self.ledger['occurrences']:
            original,revision = self.records[item['path']]['revisions']
            self.assertEqual(TRANCHE.digest(original),item['input_revision_sha256'])
            self.assertEqual(TRANCHE.digest(revision),item['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
            self.assertIn(item['input_ref'],revision['basis'])
        for field in ('new_source_records','screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][field],0)

    def test_published_review_is_not_aliased_to_accepted_manuscript(self):
        nees = [o for o in self.ledger['occurrences'] if o['source_ref']['id']=='SRC-NOV-NEES-LIEBMAN-2023']
        self.assertEqual(len(nees),4)
        for item in nees:
            self.assertEqual(item['duplicate_of'],{'id':'HIT-R002-PA6-02','rev':1})
        self.assertFalse(any(r['kind']=='source' for r in self.records.values()))

    def test_title_normalization_preserves_semantic_punctuation(self):
        self.assertEqual(TRANCHE.text_key('Medical audible alarms: A   review'),TRANCHE.text_key('medical audible alarms: a review'))
        self.assertNotEqual(TRANCHE.text_key('sound?'),TRANCHE.text_key('sound!'))
        self.assertNotEqual(TRANCHE.text_key('not safe'),TRANCHE.text_key('safe'))

    def test_unverified_source_cannot_support_resolution(self):
        def change(row):
            row['revisions'][0]['data']['metadata_status']='candidate'
        with patch.object(TRANCHE,'read_json',self.reader('SRC-NOV-NEES-LIEBMAN-2023.json',change)):
            with self.assertRaisesRegex(ValueError,'verified identity'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_mismatched_occurrence_doi_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['returned_identifiers']=[{'scheme':'doi','value':'10.1234/fictional-wrong'}]
        hid = self.ledger['occurrences'][0]['hit_id']
        with patch.object(TRANCHE,'read_json',self.reader(hid+'.json',change)):
            with self.assertRaisesRegex(ValueError,'DOI/status disagreement'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_wrong_representative_source_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['source_ref']={'id':'SRC-FICTIONAL-WRONG','rev':1}
        with patch.object(TRANCHE,'read_json',self.reader('HIT-R002-PA6-02.json',change)):
            with self.assertRaisesRegex(ValueError,'Representative source disagreement'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_export_hash_mismatch_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['export']['value']['sha256']='0'*64
        hid = self.ledger['occurrences'][0]['search_ref']['id']
        with patch.object(TRANCHE,'read_json',self.reader(hid+'.json',change)):
            with self.assertRaisesRegex(ValueError,'artifact hash mismatch'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_frozen_count_drift_prevents_writes(self):
        changed = copy.deepcopy(self.ledger)
        changed['counts']['occurrences']=11
        with patch.object(TRANCHE,'build',return_value=(self.records,changed)), patch.object(TRANCHE,'write_generated_records') as writer, patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):
                TRANCHE.main()
            writer.assert_not_called()


if __name__=='__main__':
    unittest.main()
