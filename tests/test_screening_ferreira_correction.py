"""Correction-aware identity scope, distinct readings and immutable discovery provenance."""
from contextlib import contextmanager
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_ferreira_correction as C
ROOT=Path(__file__).resolve().parents[1]


class FerreiraCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/C.LEDGER);cls.at=cls.ledger['resolved_at']
        cls.records,cls.expected=C.build(ROOT,cls.at)
        cls.plan=read_json(ROOT/C.PLAN)

    @contextmanager
    def changed(self,kind,change):
        with tempfile.TemporaryDirectory() as directory:
            plan=copy.deepcopy(self.plan);options={}
            if kind=='receipt':
                value=read_json(ROOT/C.RECEIPT);change(value)
                path=Path(directory)/'fictional-receipt.json';path.write_text(dumps(value));options['receipt_path']=str(path)
            else:
                if kind=='plan':change(plan)
                else:
                    key={'original':'original_capture','notice':'notice_capture','parent':'parent_plan'}[kind]
                    value=read_json(ROOT/plan[key]['path']);change(value)
                    path=Path(directory)/'fictional-artifact.json';path.write_text(dumps(value))
                    plan[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                path=Path(directory)/'fictional-plan.json';path.write_text(dumps(plan));options['plan_path']=str(path)
            yield options

    def source(self,rid):return self.records[C.AREA+'/records/'+rid+'.json']['revisions'][0]['data']

    def test_frozen_ledger_and_canonical_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_original_and_notice_are_distinct_publications_without_study_creation(self):
        self.assertCountEqual([r['kind'] for r in self.records.values()],['source']*2+['search_hit']*4+['assistance']*2)
        original,notice=self.source(C.ORIGINAL),self.source(C.NOTICE)
        self.assertEqual(original['validity'],'corrected');self.assertEqual(notice['validity'],'active')
        self.assertEqual(notice['source_type'],'correction')
        self.assertEqual(notice['family_links'][0]['relation'],'correction_of')
        self.assertEqual(notice['family_links'][0]['source_ref'],C.pin(C.ORIGINAL))
        self.assertNotIn('alias_of',original);self.assertNotIn('alias_of',notice)
        for name in ['screening_decisions_created','study_records_created','sample_records_created']:
            self.assertEqual(self.ledger['counts'][name],0)

    def test_full_notice_reading_and_rights_never_transfer_to_original(self):
        original,notice=self.source(C.ORIGINAL),self.source(C.NOTICE)
        self.assertEqual(original['access_status'],'metadata_only');self.assertEqual(original['manifestations'],[])
        self.assertEqual(original['rights']['status'],'unknown')
        self.assertEqual(notice['access_status'],'full_text_available');self.assertEqual(notice['manifestations'][0]['extent'],1)
        reading=self.records[C.AREA+'/records/'+C.READING+'.json']['revisions'][0]['data']
        self.assertEqual(reading['source_ref'],C.pin(C.NOTICE));self.assertEqual(reading['ranges'],[[1,1]])
        self.assertEqual(reading['reading_status'],'full_item_read')
        self.assertEqual(self.ledger['counts']['original_article_readings'],0)

    def test_original_discovery_fields_and_revision_hashes_stay_immutable(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            before,after=self.records[o['path']]['revisions']
            self.assertEqual(C.digest(before),o['input_revision_sha256']);self.assertEqual(C.digest(after),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in before['data'].items() if k not in allowed},{k:v for k,v in after['data'].items() if k not in allowed})

    def test_three_original_hits_and_one_notice_hit_keep_distinct_targets(self):
        self.assertEqual({o['hit_id'] for o in self.ledger['occurrences']},C.HITS|{C.NOTICE_HIT})
        self.assertEqual(sum(o['status']=='resolved' for o in self.ledger['occurrences']),2)
        self.assertEqual(sum(o['status']=='duplicate' for o in self.ledger['occurrences']),2)
        originals=[o for o in self.ledger['occurrences'] if o['hit_id'] in C.HITS]
        self.assertEqual(len(originals),3);self.assertTrue(all(o['source_ref']==C.pin(C.ORIGINAL) for o in originals))
        notice=next(o for o in self.ledger['occurrences'] if o['hit_id']==C.NOTICE_HIT)
        self.assertEqual(notice['source_ref'],C.pin(C.NOTICE));self.assertEqual(notice['status'],'resolved');self.assertIsNone(notice['duplicate_of'])

    def test_dates_and_deposited_name_splitting_remain_distinct(self):
        original,notice=self.source(C.ORIGINAL),self.source(C.NOTICE)
        self.assertEqual(original['publication_date']['value'],'2023-02-16')
        self.assertEqual(notice['publication_date']['value'],'2023-12-07')
        self.assertEqual(original['authors'],notice['authors']);self.assertEqual(len(original['authors']),8)
        self.assertEqual(original['authors'][0]['name'],'Vasco Ribeiro Ferreira')
        om=read_json(ROOT/self.plan['original_capture']['path'])['record']['author'][0]
        nm=read_json(ROOT/self.plan['notice_capture']['path'])['record']['author'][0]
        self.assertNotEqual(om['family'],nm['family'])

    def test_parent_scope_cannot_duplicate_or_drop_a_held_occurrence(self):
        changes=[lambda p:p['held_occurrences'].pop(),lambda p:p['held_occurrences'].__setitem__(1,copy.deepcopy(p['held_occurrences'][0]))]
        for change in changes:
            with self.changed('plan',change) as options:
                with self.assertRaisesRegex(ValueError,'Fixed held occurrence scope disagreement'):C.build(ROOT,self.at,**options)

    def test_wrong_or_extra_original_correction_relation_is_rejected(self):
        changes=[lambda v:v['record']['relation']['correction'][0].update(id='10.0000/fictional'),
                 lambda v:v['record']['relation'].update(unreviewed=[{}])]
        for change in changes:
            with self.changed('original',change) as options:
                with self.assertRaisesRegex(ValueError,'Original correction relation disagreement'):C.build(ROOT,self.at,**options)

    def test_wrong_or_retraction_notice_target_is_rejected(self):
        for change in [{'DOI':'10.0000/fictional'},{'type':'retraction'}]:
            with self.changed('notice',lambda v:v['record']['update-to'][0].update(change)) as options:
                with self.assertRaisesRegex(ValueError,'Notice correction target disagreement'):C.build(ROOT,self.at,**options)

    def test_fake_or_failed_publisher_pdf_cannot_support_resolution(self):
        for change in [{'http_status':404},{'sha256':'0'*64},{'page_count':2}]:
            with self.changed('receipt',lambda v:v['retrieval'].update(change)) as options:
                with self.assertRaisesRegex(ValueError,'Publisher PDF receipt disagreement'):C.build(ROOT,self.at,**options)

    def test_changed_publisher_identity_witness_is_rejected(self):
        with self.changed('receipt',lambda v:v.update(checked_original_doi='10.0000/fictional')) as options:
            with self.assertRaisesRegex(ValueError,'Publisher notice identity witness disagreement'):C.build(ROOT,self.at,**options)

    def test_notice_reading_cannot_be_promoted_to_original_results_reading(self):
        for change in [{'original_article_read':True},{'file_pages_1based':[2]},{'results_effect_assessment':'unchanged'}]:
            with self.changed('receipt',lambda v:v.update(change)) as options:
                with self.assertRaisesRegex(ValueError,'Notice reading/scope boundary disagreement'):C.build(ROOT,self.at,**options)

    def test_changed_capture_hash_or_parent_hold_is_rejected(self):
        with self.changed('plan',lambda v:v['original_capture'].update(sha256='0'*64)) as options:
            with self.assertRaisesRegex(ValueError,'Artifact hash mismatch'):C.build(ROOT,self.at,**options)
        with self.changed('parent',lambda v:v['not_admitted'][0]['hit_refs'].pop()) as options:
            with self.assertRaisesRegex(ValueError,'Parent held scope disagreement'):C.build(ROOT,self.at,**options)

    def test_retained_full_title_disagreement_prevents_linking(self):
        hid=sorted(C.HITS)[0]
        def reader(path):
            value=read_json(path)
            if str(path).endswith(hid+'.json'):value['revisions'][0]['data']['raw_metadata']='Fictional different title'
            return value
        with patch.object(C,'read_json',reader):
            with self.assertRaisesRegex(ValueError,'Retained DOI/full-title/work-ID disagreement'):C.build(ROOT,self.at)

    def test_extra_notice_relation_and_wrong_registration_doi_are_rejected(self):
        with self.changed('notice',lambda v:v['record'].update(relation={'unreviewed':[{}]})) as options:
            with self.assertRaisesRegex(ValueError,'Notice correction target disagreement'):C.build(ROOT,self.at,**options)
        with self.changed('original',lambda v:v['record'].update(DOI='10.0000/fictional')) as options:
            with self.assertRaisesRegex(ValueError,'Registration/request identity disagreement'):C.build(ROOT,self.at,**options)

    def test_notice_retained_erratum_label_date_and_work_id_stay_literal(self):
        o=next(o for o in self.ledger['occurrences'] if o['hit_id']==C.NOTICE_HIT)
        text=self.records[o['path']]['revisions'][1]['data']['raw_metadata']
        self.assertIn('2023-12-07 | erratum | https://openalex.org/W4389429591',text)
        self.assertEqual(o['export_locator']['work_id'],'https://openalex.org/W4389429591')
        self.assertEqual(o['export_locator']['ordinal'],705)

    def test_notice_occurrence_scope_cannot_be_replaced_by_original(self):
        with self.changed('plan',lambda p:p.update(notice_occurrence=copy.deepcopy(p['held_occurrences'][0]))) as options:
            with self.assertRaisesRegex(ValueError,'Fixed notice occurrence scope disagreement'):C.build(ROOT,self.at,**options)

    def test_frozen_ledger_drift_prevents_all_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=5
        with patch.object(C,'build',return_value=(self.records,changed)),patch.object(C,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):C.main(root=ROOT)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
