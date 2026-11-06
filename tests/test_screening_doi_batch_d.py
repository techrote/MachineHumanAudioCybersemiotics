"""Fifteen-source fixed batch: immutable discovery, types, dates and failure gates."""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_doi_batch_d as D

ROOT=Path(__file__).resolve().parents[1]
E=D.engine


class DoiBatchDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=read_json(ROOT/D.PLAN);cls.ledger=read_json(ROOT/D.LEDGER)
        cls.at=cls.ledger['resolved_at'];cls.records,cls.expected=D.build(ROOT,cls.at)

    @contextmanager
    def changed_plan(self,change):
        value=copy.deepcopy(self.plan);change(value)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-plan.json';path.write_text(dumps(value))
            yield {**D.OPTIONS,'plan_path':str(path)}

    def test_ledger_and_all_canonical_prefixes_reproduce(self):
        self.assertEqual(self.expected,self.ledger)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_fifteen_metadata_only_sources_67_occurrences_and_three_chapters(self):
        self.assertCountEqual([r['kind'] for r in self.records.values()],['source']*15+['search_hit']*67+['assistance'])
        self.assertEqual(sum(o['status']=='resolved' for o in self.ledger['occurrences']),15)
        self.assertEqual(sum(o['status']=='duplicate' for o in self.ledger['occurrences']),52)
        sources=[r for r in self.records.values() if r['kind']=='source']
        for source in sources:
            b=source['revisions'][0]['data'];self.assertEqual(b['access_status'],'metadata_only')
            self.assertEqual(b['rights']['status'],'unknown');self.assertEqual(b['manifestations'],[]);self.assertEqual(b['family_links'],[])
        self.assertEqual({r['id'] for r in sources if r['revisions'][0]['data']['source_type']=='chapter'},
            {'SRC-R006-D-LEIMANN-EARCONS','SRC-R006-D-NAKATANI-GUIDELINES','SRC-R006-D-MCINTYRE-OPERATING'})
        for k in ('screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][k],0)

    def test_original_discovery_fields_and_revision_hashes_are_retained(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_75_occurrence_scope_keeps_eight_bibliography_cases_deferred(self):
        selected={o['hit_id'] for o in self.ledger['occurrences']};deferred={i['hit_ref']['id'] for i in self.plan['deferred']}
        self.assertEqual(len(selected|deferred),75);self.assertEqual(len(deferred),8);self.assertFalse(selected&deferred)
        for item in self.plan['deferred']:
            path=f"research/searches/auditory/records/hits/{item['hit_ref']['id']}.json"
            self.assertNotIn(path,self.records)
            self.assertEqual(read_json(ROOT/path)['revisions'][0]['data']['status'],'unresolved')

    def test_jeon_dates_and_nakatani_original_type_are_not_harmonized(self):
        b=self.records[E.AREA+'/records/SRC-R006-D-JEON-MENUS.json']['revisions'][0]['data']
        self.assertEqual(b['publication_date']['value'],'2015-01-02')
        source=next(s for s in self.ledger['sources'] if s['source_ref']['id']=='SRC-R006-D-JEON-MENUS')
        self.assertEqual(source['reported_dates']['published-online']['date-parts'],[[2014,10,22]])
        hits=[o for o in self.ledger['occurrences'] if o['source_ref']['id']=='SRC-R006-D-JEON-MENUS']
        self.assertTrue(all(o['export_locator']['reported_publication_date']=='2014-05-30' for o in hits))
        self.assertTrue(all('2014-05-30' in self.records[o['path']]['revisions'][1]['data']['raw_metadata'] for o in hits))
        n=next(o for o in self.ledger['occurrences'] if o['source_ref']['id']=='SRC-R006-D-NAKATANI-GUIDELINES')
        self.assertIn('conference-paper',self.records[n['path']]['revisions'][1]['data']['raw_metadata'])

    def test_wrong_capture_hash_is_rejected(self):
        with self.changed_plan(lambda p:p['sources'][0]['capture'].update(sha256='0'*64)) as options:
            with self.assertRaisesRegex(ValueError,'Artifact hash mismatch'):E.build(ROOT,self.at,**options)

    def test_retained_title_disagreement_prevents_linking(self):
        hid=self.plan['selected'][0]['hit_ref']['id']
        def reader(path):
            value=read_json(path)
            if str(path).endswith(hid+'.json'):value['revisions'][0]['data']['raw_metadata']='Fictional changed full title'
            return value
        with patch.object(E,'read_json',reader):
            with self.assertRaisesRegex(ValueError,'Retained DOI/full-title disagreement'):D.build(ROOT,self.at)

    def test_fixed_scope_cannot_silently_shrink(self):
        with self.changed_plan(lambda p:p['selected'].pop()) as options:
            with self.assertRaisesRegex(ValueError,'scope/count disagreement'):E.build(ROOT,self.at,**options)

    def test_frozen_ledger_drift_prevents_all_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=68
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,build_options=D.OPTIONS)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
