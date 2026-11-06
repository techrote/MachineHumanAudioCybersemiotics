"""Fixed URL adjudication, original web provenance and rejection controls."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from tools.record_io import read_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('url_tranche',ROOT/'research/registry/identity/scripts/build_r006_url_tranche.py')
TRANCHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRANCHE)


class UrlTrancheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = read_json(ROOT/TRANCHE.LEDGER)
        cls.records,cls.expected = TRANCHE.build(ROOT,cls.ledger['resolved_at'])

    def reader(self,suffix,change):
        def read(path):
            row = read_json(path)
            if str(path).endswith(suffix):
                change(row)
            return row
        return read

    def test_frozen_ledger_and_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual = read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_eight_occurrences_four_sources_one_representative_seven_duplicates(self):
        rows = self.ledger['occurrences']
        self.assertEqual(len(rows),8)
        self.assertEqual(len({r['source_ref']['id'] for r in rows}),4)
        self.assertEqual(sum(r['status']=='resolved' for r in rows),1)
        self.assertEqual(sum(r['status']=='duplicate' for r in rows),7)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*8+['assistance'])
        ruskin = [r for r in rows if r['source_ref']['id']=='SRC-R005R-RUSKIN-2020']
        self.assertEqual(ruskin[0]['status'],'resolved')
        for duplicate in ruskin[1:]:
            self.assertEqual(duplicate['duplicate_of'],ruskin[0]['output_ref'])

    def test_original_discovery_pilot_status_and_domain_labels_are_preserved(self):
        allowed = {'status','source_ref','duplicate_of','resolution_reason'}
        for item in self.ledger['occurrences']:
            original,revision = self.records[item['path']]['revisions']
            self.assertEqual(TRANCHE.digest(original),item['input_revision_sha256'])
            self.assertEqual(TRANCHE.digest(revision),item['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
            self.assertEqual(original['data']['raw_metadata'],item['original_result_label']+' | '+item['verified_resource'])
        pilot = next(o for o in self.ledger['occurrences'] if o['hit_id']=='HIT-R002-PA6-03')
        self.assertEqual(pilot['original_result_label'],'pmc.ncbi.nlm.nih.gov')
        # Search/source records are not rewritten, including mode/access/reading.
        self.assertFalse(any(r['kind'] in {'search_run','source'} for r in self.records.values()))
        for field in ('new_source_records','screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][field],0)

    def test_same_host_different_resource_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['returned_identifiers'][0]['value']='https://pmc.ncbi.nlm.nih.gov/articles/PMC9999999/'
        with patch.object(TRANCHE,'read_json',self.reader('HIT-R002-PA6-03.json',change)):
            with self.assertRaisesRegex(ValueError,'Original resource/status disagreement'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_unverified_source_url_is_rejected(self):
        def change(row):
            for item in row['revisions'][0]['data']['identifiers']:
                if item['scheme']=='url':
                    item['status']='candidate'
        with patch.object(TRANCHE,'read_json',self.reader('SRC-BRIER-2011-SIGNS.json',change)):
            with self.assertRaisesRegex(ValueError,'exact verified resource'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_wrong_representative_source_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['source_ref']={'id':'SRC-FICTIONAL-WRONG','rev':1}
        with patch.object(TRANCHE,'read_json',self.reader('HIT-R003-B04-06.json',change)):
            with self.assertRaisesRegex(ValueError,'Representative source disagreement'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_wrong_original_ordinal_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['ordinal']=2
        with patch.object(TRANCHE,'read_json',self.reader('HIT-R002-PA6-03.json',change)):
            with self.assertRaisesRegex(ValueError,'Retained result/ordinal disagreement'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_export_hash_mismatch_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['export']['value']['sha256']='0'*64
        with patch.object(TRANCHE,'read_json',self.reader('SRCH-R002-PA6.json',change)):
            with self.assertRaisesRegex(ValueError,'artifact hash mismatch'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_changed_search_query_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['query']='fictional changed query'
        with patch.object(TRANCHE,'read_json',self.reader('SRCH-R002-PA6.json',change)):
            with self.assertRaisesRegex(ValueError,'Search query/export disagreement'):
                TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_frozen_count_drift_prevents_writes(self):
        changed = copy.deepcopy(self.ledger)
        changed['counts']['occurrences']=9
        with patch.object(TRANCHE,'build',return_value=(self.records,changed)),patch.object(TRANCHE,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):
                TRANCHE.main()
            writer.assert_not_called()


if __name__=='__main__':
    unittest.main()
