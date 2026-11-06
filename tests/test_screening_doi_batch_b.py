"""Reusable identity builder: frozen old outputs, isolated new profile and rejection gates."""
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json
from research.registry.identity.scripts import build_r006_doi_batch_b as B

ROOT=Path(__file__).resolve().parents[1]
E=B.engine


class DoiBatchBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/B.LEDGER);cls.records,cls.expected=B.build(ROOT,cls.ledger['resolved_at'])

    @contextmanager
    def changed_plan(self,change):
        plan=read_json(ROOT/B.PLAN);change(plan)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-plan.json';path.write_text(json.dumps(plan))
            options={**B.OPTIONS,'plan_path':str(path)}
            yield options

    def test_frozen_batch_b_ledger_and_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_old_batch_ledger_still_reproduces_exactly_with_default_options(self):
        old=read_json(ROOT/E.LEDGER);records,ledger=E.build(ROOT,old['resolved_at'])
        self.assertEqual(old,ledger)
        for path,expected in records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_new_profile_does_not_mutate_default_global_configuration(self):
        old=copy.deepcopy((E.PLAN,E.LEDGER,E.AID,E.ACTOR))
        B.build(ROOT,self.ledger['resolved_at'])
        self.assertEqual(old,(E.PLAN,E.LEDGER,E.AID,E.ACTOR))

    def test_five_metadata_only_sources_23_occurrences_nine_deferred(self):
        self.assertCountEqual([r['kind'] for r in self.records.values()],['source']*5+['search_hit']*23+['assistance'])
        self.assertEqual(len(self.ledger['deferred']),9)
        self.assertEqual(sum(o['status']=='resolved' for o in self.ledger['occurrences']),5)
        self.assertEqual(sum(o['status']=='duplicate' for o in self.ledger['occurrences']),18)
        for r in self.records.values():
            if r['kind']=='source':
                b=r['revisions'][0]['data'];self.assertEqual(b['access_status'],'metadata_only');self.assertEqual(b['manifestations'],[]);self.assertEqual(b['rights']['status'],'unknown')
        chapter=next(r for r in self.records.values() if r['id']=='SRC-R006-HOFMANN-2016-INCAR')
        self.assertEqual(chapter['revisions'][0]['data']['source_type'],'chapter')

    def test_original_discovery_metadata_and_history_are_preserved(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
        self.assertTrue({d['hit_ref']['id'] for d in self.ledger['deferred']}.isdisjoint(o['hit_id'] for o in self.ledger['occurrences']))

    def test_duplicate_source_id_is_rejected(self):
        with self.changed_plan(lambda p:p['sources'][1].update(source_id=p['sources'][0]['source_id'])) as options:
            with self.assertRaisesRegex(ValueError,'Duplicate or overlapping'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_selected_and_deferred_overlap_is_rejected(self):
        with self.changed_plan(lambda p:p['deferred'][0].update(hit_ref=p['selected'][0]['hit_ref'])) as options:
            with self.assertRaisesRegex(ValueError,'Duplicate or overlapping'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_duplicate_deferred_occurrence_cannot_inflate_the_count(self):
        with self.changed_plan(lambda p:p['deferred'][1].update(hit_ref=p['deferred'][0]['hit_ref'])) as options:
            with self.assertRaisesRegex(ValueError,'Duplicate or overlapping'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_source_without_qualified_occurrence_is_rejected(self):
        def change(p):
            old=p['sources'][0]['source_id'];new=p['sources'][1]['source_id']
            for item in p['selected']:
                if item['source_id']==old:item['source_id']=new
        with self.changed_plan(change) as options:
            with self.assertRaisesRegex(ValueError,'qualified occurrence evidence'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_custom_batch_cannot_inherit_another_batch_narrative(self):
        options={**B.OPTIONS,'task':None}
        with self.assertRaisesRegex(ValueError,'own task and verification narrative'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_fixed_count_change_is_rejected(self):
        with self.changed_plan(lambda p:p['selected'].pop()) as options:
            with self.assertRaisesRegex(ValueError,'scope/count disagreement'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_metadata_capture_hash_change_is_rejected(self):
        with self.changed_plan(lambda p:p['sources'][0]['capture'].update(sha256='0'*64)) as options:
            with self.assertRaisesRegex(ValueError,'Artifact hash mismatch'):E.build(ROOT,self.ledger['resolved_at'],**options)

    def test_frozen_new_ledger_drift_prevents_any_write(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=24
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,build_options=B.OPTIONS)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
