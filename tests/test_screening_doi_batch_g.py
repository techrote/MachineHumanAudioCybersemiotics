"""Twenty-source batch G: immutable discovery, dates, exact scope and failure gates."""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_doi_batch_g as D

ROOT=Path(__file__).resolve().parents[1]
E=D.engine


class DoiBatchGTests(unittest.TestCase):
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

    def test_fixed_source_and_occurrence_counts_do_not_create_scientific_entities(self):
        ns,nh,nd=D.OPTIONS['expected_counts']
        self.assertCountEqual([r['kind'] for r in self.records.values()],['source']*ns+['search_hit']*nh+['assistance'])
        self.assertEqual(sum(o['status']=='resolved' for o in self.ledger['occurrences']),ns)
        self.assertEqual(sum(o['status']=='duplicate' for o in self.ledger['occurrences']),nh-ns)
        sources=[r for r in self.records.values() if r['kind']=='source']
        for source in sources:
            b=source['revisions'][0]['data'];self.assertEqual(b['access_status'],'metadata_only')
            self.assertEqual(b['rights']['status'],'unknown');self.assertEqual(b['manifestations'],[]);self.assertEqual(b['family_links'],[])
        self.assertEqual({r['id'] for r in sources if r['revisions'][0]['data']['source_type']=='conference_paper'},
            {'SRC-R006-G-JEON-DUALTASK','SRC-R006-G-BIKAKI-AGGREGATOR','SRC-R006-G-FAGERLONN-GRADED','SRC-R006-G-POLITIS-TACTONS','SRC-R006-G-HUTCHINSON-CODE'})
        for k in ('screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][k],0)

    def test_original_discovery_fields_and_revision_hashes_are_retained(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_all_sixty_fixed_occurrences_are_accounted_for(self):
        selected={o['hit_id'] for o in self.ledger['occurrences']};deferred={i['hit_ref']['id'] for i in self.plan['deferred']}
        held={i['id'] for group in self.plan['not_admitted'] for i in group['hit_refs']}
        self.assertEqual(len(selected|deferred|held),60)
        self.assertFalse(selected&deferred);self.assertFalse(selected&held);self.assertFalse(deferred&held)
        for item in self.plan['deferred']:
            path=f"research/searches/auditory/records/hits/{item['hit_ref']['id']}.json"
            self.assertNotIn(path,self.records)
            self.assertEqual(read_json(ROOT/path)['revisions'][0]['data']['status'],'unresolved')

    def test_davidson_print_and_discovery_dates_are_not_harmonized(self):
        b=self.records[E.AREA+'/records/SRC-R006-G-DAVIDSON-LINGUISTIC.json']['revisions'][0]['data']
        self.assertEqual(b['publication_date']['value'],'2019-11')
        hits=[o for o in self.ledger['occurrences'] if o['source_ref']['id']=='SRC-R006-G-DAVIDSON-LINGUISTIC']
        self.assertEqual(len(hits),2)
        self.assertTrue(all(o['export_locator']['reported_publication_date']=='2019-08-14' for o in hits))
        self.assertTrue(all('2019-08-14' in self.records[o['path']]['revisions'][1]['data']['raw_metadata'] for o in hits))

    def test_fagerlonn_subtitle_is_retained_without_expanding_the_source_title(self):
        spec=next(s for s in self.plan['sources'] if s['source_id']=='SRC-R006-G-FAGERLONN-GRADED')
        capture=read_json(ROOT/spec['capture']['path'])
        self.assertEqual(capture['record']['subtitle'],['using sound to guide drivers without additional noise'])
        b=self.records[E.AREA+'/records/SRC-R006-G-FAGERLONN-GRADED.json']['revisions'][0]['data']
        self.assertEqual(b['title'],'Graded auditory warnings during in-vehicle use')
        self.assertNotIn('abstract',capture['record'])

    def test_every_capture_retains_only_declared_bibliographic_fields(self):
        for spec in self.plan['sources']:
            capture=read_json(ROOT/spec['capture']['path'])
            self.assertEqual(capture['http_status'],200)
            self.assertLessEqual(set(capture['record']),set(capture['retained_fields']))
            self.assertNotIn('abstract',capture['retained_fields'])

    def test_ferreira_correction_relation_is_held_without_source_or_hit_writes(self):
        held=self.plan['not_admitted'];self.assertEqual(len(held),1)
        item=held[0];self.assertEqual(item['doi'],'10.1371/journal.pone.0281680')
        capture=read_json(ROOT/item['capture']['path'])
        self.assertEqual(capture['record']['relation']['correction'][0]['id'],'10.1371/journal.pone.0295826')
        self.assertEqual(len(item['hit_refs']),3)
        self.assertNotIn(E.AREA+'/records/SRC-R006-G-FERREIRA-ERP.json',self.records)
        for ref in item['hit_refs']:
            path='research/searches/auditory/records/hits/'+ref['id']+'.json'
            self.assertNotIn(path,self.records)
            self.assertEqual(read_json(ROOT/path)['revisions'][0]['data']['status'],'unresolved')

    def test_relation_or_update_cannot_be_admitted_even_with_matching_artifact_hash(self):
        for field,value in [('relation',{'correction':[{'id':'10.0000/fictional-correction'}]}),
                            ('update-to',[{'DOI':'10.0000/fictional-original','type':'correction'}])]:
            plan=copy.deepcopy(self.plan);spec=plan['sources'][0]
            capture=read_json(ROOT/spec['capture']['path']);capture['record'][field]=value
            with self.subTest(field=field),tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'fictional-capture.json';path.write_text(dumps(capture))
                import hashlib
                spec['capture']={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                p=Path(directory)/'fictional-plan.json';p.write_text(dumps(plan))
                with self.assertRaisesRegex(ValueError,'Correction/relation metadata requires explicit identity review'):
                    E.build(ROOT,self.at,**{**D.OPTIONS,'plan_path':str(p)})

    def test_duplicate_occurrence_cannot_replace_a_different_case(self):
        with self.changed_plan(lambda p:p['selected'].__setitem__(1,copy.deepcopy(p['selected'][0]))) as options:
            with self.assertRaisesRegex(ValueError,'Duplicate or overlapping fixed-plan identities'):E.build(ROOT,self.at,**options)

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
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=61
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,build_options=D.OPTIONS)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
