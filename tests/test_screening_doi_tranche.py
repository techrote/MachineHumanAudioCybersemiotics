"""Metadata-only identity adjudication, history and adverse-input checks."""
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from tools.record_io import read_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r006_doi_tranche', ROOT / 'research/registry/identity/scripts/build_r006_doi_tranche.py')
TRANCHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRANCHE)


class DoiTrancheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = read_json(ROOT / TRANCHE.LEDGER)
        cls.records, cls.rebuilt = TRANCHE.build(ROOT, cls.ledger['resolved_at'])

    def changed_reader(self, suffix, change):
        def reader(path):
            value = read_json(path)
            if str(path).endswith(suffix):
                change(value)
            return value
        return reader

    def test_frozen_ledger_and_prefixes_reproduce(self):
        self.assertEqual(self.ledger, self.rebuilt)
        for path, expected in self.records.items():
            actual = read_json(ROOT / path)
            self.assertEqual({**actual, 'revisions': actual['revisions'][:len(expected['revisions'])]}, expected)

    def test_only_identity_fields_change_and_originals_remain_hash_pinned(self):
        allowed = {'status', 'source_ref', 'duplicate_of', 'resolution_reason'}
        for item in self.ledger['occurrences']:
            original, revision = self.records[item['path']]['revisions']
            self.assertEqual(TRANCHE.digest(original), item['input_revision_sha256'])
            self.assertEqual(TRANCHE.digest(revision), item['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
            self.assertIn(item['input_ref'], revision['basis'])
            self.assertIn(item['duplicate_of'], revision['basis'])
            representative = next((ROOT / 'research/searches/related/records/hits').glob(item['duplicate_of']['id']+'.json'))
            self.assertEqual(read_json(representative)['revisions'][0]['data']['source_ref'], item['source_ref'])

    def test_twelve_duplicates_three_existing_sources_no_scientific_entities(self):
        self.assertEqual(len(self.ledger['occurrences']), 12)
        self.assertEqual(len({x['source_ref']['id'] for x in self.ledger['occurrences']}), 3)
        self.assertCountEqual([r['kind'] for r in self.records.values()], ['search_hit']*12+['assistance'])
        for item in self.ledger['occurrences']:
            self.assertEqual(self.records[item['path']]['revisions'][1]['data']['status'], 'duplicate')
        for field in ('new_source_records','screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][field], 0)

    def test_unverified_source_identifier_cannot_support_resolution(self):
        def change(row):
            for item in row['revisions'][0]['data']['identifiers']:
                item['status'] = 'candidate'
        with patch.object(TRANCHE, 'read_json', self.changed_reader('SRC-REL-BLATTNER-1989.json', change)):
            with self.assertRaisesRegex(ValueError, 'one verified DOI'):
                TRANCHE.build(ROOT, self.ledger['resolved_at'])

    def test_title_mismatch_is_not_overridden_by_matching_doi(self):
        def change(row):
            row['revisions'][0]['data']['title'] += ' [different]'
        with patch.object(TRANCHE, 'read_json', self.changed_reader('SRC-REL-BLATTNER-1989.json', change)):
            with self.assertRaisesRegex(ValueError, 'DOI/title disagreement'):
                TRANCHE.build(ROOT, self.ledger['resolved_at'])

    def test_wrong_returned_doi_is_rejected(self):
        def change(row):
            row['revisions'][0]['data']['returned_identifiers'] = [{'scheme':'doi','value':'10.1234/fictional-wrong'}]
        hid = self.ledger['occurrences'][0]['hit_id']
        with patch.object(TRANCHE, 'read_json', self.changed_reader(hid+'.json', change)):
            with self.assertRaisesRegex(ValueError, 'DOI/status mismatch'):
                TRANCHE.build(ROOT, self.ledger['resolved_at'])

    def test_representative_must_already_resolve_same_source(self):
        def change(row):
            row['revisions'][0]['data']['source_ref'] = {'id':'SRC-FICTIONAL-WRONG','rev':1}
        with patch.object(TRANCHE, 'read_json', self.changed_reader('HIT-R004-LK-BLATTNER-1989-01.json', change)):
            with self.assertRaisesRegex(ValueError, 'Representative source disagreement'):
                TRANCHE.build(ROOT, self.ledger['resolved_at'])

    def test_evidence_hash_mismatch_rejected(self):
        def change(manifest):
            manifest['lookups']['BLATTNER-1989']['sha256'] = '0'*64
        with patch.object(TRANCHE, 'read_json', self.changed_reader('lookups/MANIFEST.json', change)):
            with self.assertRaisesRegex(ValueError, 'artifact hash mismatch'):
                TRANCHE.build(ROOT, self.ledger['resolved_at'])

    def test_frozen_count_drift_prevents_any_write(self):
        changed = copy.deepcopy(self.ledger)
        changed['counts']['occurrences'] = 13
        with patch.object(TRANCHE, 'build', return_value=(self.records,changed)), patch.object(TRANCHE, 'write_generated_records') as writer, patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit, 'ledger drift'):
                TRANCHE.main()
            writer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
