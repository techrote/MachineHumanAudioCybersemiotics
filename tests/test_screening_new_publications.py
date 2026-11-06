"""Metadata-only source admission, exact DOI/title and discovery-history controls."""
import copy
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('new_publications',ROOT/'research/registry/identity/scripts/build_r006_new_publications.py')
TRANCHE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(TRANCHE)


class NewPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/TRANCHE.LEDGER)
        cls.records,cls.expected=TRANCHE.build(ROOT,cls.ledger['resolved_at'])

    def reader(self,suffix,change):
        def read(path):
            value=read_json(path)
            if str(path).endswith(suffix):change(value)
            return value
        return read

    @contextmanager
    def changed_plan(self,change):
        plan=read_json(ROOT/TRANCHE.PLAN)
        change(plan)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-plan.json';path.write_text(json.dumps(plan))
            with patch.object(TRANCHE,'PLAN',str(path)):yield

    def test_frozen_ledger_and_all_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_five_sources_29_occurrences_and_seven_deferred(self):
        kinds=[r['kind'] for r in self.records.values()]
        self.assertCountEqual(kinds,['source']*5+['search_hit']*29+['assistance'])
        self.assertEqual(len(self.ledger['deferred']),7)
        self.assertEqual(sum(o['status']=='resolved' for o in self.ledger['occurrences']),5)
        self.assertEqual(sum(o['status']=='duplicate' for o in self.ledger['occurrences']),24)
        self.assertTrue({o['hit_ref']['id'] for o in self.ledger['deferred']}.isdisjoint(o['hit_id'] for o in self.ledger['occurrences']))

    def test_metadata_verification_does_not_promote_access_reading_or_rights(self):
        for row in self.records.values():
            if row['kind']!='source':continue
            body=row['revisions'][0]['data']
            self.assertEqual(body['metadata_status'],'verified')
            self.assertEqual(body['access_status'],'metadata_only')
            self.assertEqual(body['manifestations'],[])
            self.assertEqual(body['family_links'],[])
            self.assertEqual(body['rights']['status'],'unknown')
            self.assertNotIn('alias_of',body)
        for field in ('screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][field],0)

    def test_abstract_only_doi_remains_distinct_from_full_article(self):
        row=next(r for r in self.records.values() if r['id']=='SRC-R006-BLATTNER-1989-ABSTRACT')
        body=row['revisions'][0]['data']
        self.assertIn('(Abstract only)',body['title'])
        self.assertEqual(body['identifiers'][0]['value'],'10.1145/67880.1046599')
        self.assertNotEqual(body['identifiers'][0]['value'],'10.1207/s15327051hci0401_1')

    def test_print_and_online_dates_are_retained_separately(self):
        row=next(r for r in self.records.values() if r['id']=='SRC-R006-WALKER-2013-SPEARCONS')
        self.assertEqual(row['revisions'][0]['data']['publication_date']['value'],'2013-02')
        ledger=next(s for s in self.ledger['sources'] if s['source_ref']['id']==row['id'])
        self.assertEqual(ledger['reported_dates']['published-online']['date-parts'][0],[2012,7,2])
        self.assertEqual(ledger['reported_dates']['published-print']['date-parts'][0],[2013,2])
        self.assertEqual(ledger['selected_publication_date_field'],'published-print')

    def test_original_discovery_revisions_and_metadata_are_unchanged(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for item in self.ledger['occurrences']:
            original,revision=self.records[item['path']]['revisions']
            self.assertEqual(TRANCHE.digest(original),item['input_revision_sha256'])
            self.assertEqual(TRANCHE.digest(revision),item['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
            self.assertIn(item['input_ref'],revision['basis'])

    def test_wrong_capture_hash_is_rejected(self):
        with self.changed_plan(lambda p:p['sources'][0]['capture'].update(sha256='0'*64)):
            with self.assertRaisesRegex(ValueError,'Artifact hash mismatch'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_wrong_crossref_doi_cannot_be_admitted(self):
        with self.changed_plan(lambda p:p['sources'][0].update(doi='10.1234/fictional-wrong')):
            with self.assertRaisesRegex(ValueError,'Crossref identity disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_failed_http_capture_cannot_support_source_verification(self):
        plan=read_json(ROOT/TRANCHE.PLAN);capture=plan['sources'][0]['capture'];metadata=read_json(ROOT/capture['path']);metadata['http_status']=403
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-failed-capture.json';raw=json.dumps(metadata).encode();path.write_bytes(raw)
            def change(p):p['sources'][0]['capture']={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest()}
            with self.changed_plan(change):
                with self.assertRaisesRegex(ValueError,'Crossref identity disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_wrong_occurrence_doi_is_rejected(self):
        hid=self.ledger['occurrences'][0]['hit_id']
        def change(row):row['revisions'][0]['data']['returned_identifiers']=[{'scheme':'doi','value':'10.1234/fictional-wrong'}]
        with patch.object(TRANCHE,'read_json',self.reader(hid+'.json',change)):
            with self.assertRaisesRegex(ValueError,'Original DOI disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_different_full_title_is_not_overridden_by_matching_doi(self):
        hid=self.ledger['occurrences'][0]['hit_id']
        def change(row):row['revisions'][0]['data']['raw_metadata']='Fictional mismatched title'
        with patch.object(TRANCHE,'read_json',self.reader(hid+'.json',change)):
            with self.assertRaisesRegex(ValueError,'Web export disagreement|full-title disagreement'):TRANCHE.build(ROOT,self.ledger['resolved_at'])

    def test_frozen_ledger_count_drift_prevents_any_write(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['new_source_records']=6
        with patch.object(TRANCHE,'build',return_value=(self.records,changed)),patch.object(TRANCHE,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):TRANCHE.main()
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
