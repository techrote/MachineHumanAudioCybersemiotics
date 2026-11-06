"""Publisher identity defeats a mixed discovery DOI without creating study independence."""
from contextlib import contextmanager
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_batch_e_final as F

ROOT=Path(__file__).resolve().parents[1]


class BatchEFinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=read_json(ROOT/F.PLAN);cls.ledger=read_json(ROOT/F.LEDGER);cls.at=cls.ledger['resolved_at']
        cls.records,cls.expected=F.build(ROOT,cls.at)

    @contextmanager
    def changed_plan(self,change):
        value=copy.deepcopy(self.plan);change(value)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'fictional-adverse-plan.json';p.write_text(dumps(value))
            with patch.object(F,'PLAN',str(p)):yield

    @contextmanager
    def changed_capture(self,field,change):
        value=read_json(ROOT/self.plan[field]['path']);change(value);plan=copy.deepcopy(self.plan)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'fictional-adverse-capture.json';p.write_text(dumps(value))
            plan[field]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            pp=Path(directory)/'fictional-adverse-plan.json';pp.write_text(dumps(plan))
            with patch.object(F,'PLAN',str(pp)):yield

    def test_frozen_ledger_and_canonical_prefixes_reproduce(self):
        self.assertEqual(self.expected,self.ledger)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_one_journal_source_two_hits_and_no_scientific_entities(self):
        self.assertCountEqual([r['kind'] for r in self.records.values()],['source','search_hit','search_hit','assistance'])
        self.assertEqual(self.ledger['counts']['resolved_representatives'],1)
        self.assertEqual(self.ledger['counts']['duplicate_occurrences'],1)
        for k in ['screening_decisions_created','study_records_created','sample_records_created']:
            self.assertEqual(self.ledger['counts'][k],0)
        s=self.records[self.ledger['source']['path']]['revisions'][0]['data']
        self.assertEqual(s['access_status'],'abstract_only');self.assertEqual(s['manifestations'],[])
        self.assertEqual(s['family_links'],[]);self.assertEqual(s['rights']['status'],'unknown')

    def test_conference_source_and_original_representative_are_unchanged(self):
        p=F.AREA+'/records/'+F.CONFERENCE+'.json';r=read_json(ROOT/p)
        self.assertNotIn(p,self.records)
        self.assertEqual(F.E.digest(r['revisions'][0]),self.ledger['conference_source_unchanged']['revision_sha256'])
        self.assertEqual(r['revisions'][0]['data']['publication_date']['value'],'2010-04-10')
        self.assertEqual(r['revisions'][0]['data']['access_status'],'metadata_only')

    def test_rejected_conference_doi_is_not_transferred_to_journal(self):
        s=self.records[self.ledger['source']['path']]['revisions'][0]['data']
        self.assertEqual(s['identifiers'],[{'scheme':'url','value':F.AES_URL,'status':'verified',
            'provenance':self.plan['publisher']['path']+' HTTP 200, publisher citation metadata; AES item 16362'}])
        for o in self.ledger['occurrences']:
            b=self.records[o['path']]['revisions'][1]['data']
            self.assertEqual(b['source_ref'],F.E.pin(F.JOURNAL));self.assertEqual(o['rejected_discovery_doi'],F.DOI)
            self.assertIn(F.DOI,[i['value'] for i in b['returned_identifiers'] if i['scheme']=='doi'])
            self.assertIn('separate CHI EA 2010',b['resolution_reason'])

    def test_publisher_and_discovery_dates_and_types_stay_separate(self):
        s=self.records[self.ledger['source']['path']]['revisions'][0]['data']
        self.assertEqual(s['publication_date']['value'],'2012-07-06');self.assertEqual(s['source_type'],'article')
        self.assertIn('60(7/8); 505-518',s['edition']['value'])
        for o in self.ledger['occurrences']:
            b=self.records[o['path']]['revisions'][1]['data'];self.assertIn('2012-08-27 | conference-paper',b['raw_metadata'])
            self.assertEqual(o['export_locator']['reported_biblio']['first_page'],'505')

    def test_original_discovery_and_hashes_are_preserved(self):
        allowed={'status','resolution_reason','source_ref','duplicate_of'}
        for o in self.ledger['occurrences']:
            old,new=self.records[o['path']]['revisions']
            self.assertEqual(F.E.digest(old),o['input_revision_sha256']);self.assertEqual(F.E.digest(new),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in old['data'].items() if k not in allowed},
                             {k:v for k,v in new['data'].items() if k not in allowed})

    def test_wrong_publisher_pages_or_doi_are_rejected(self):
        for change in (lambda c:c['metadata'].update(citation_firstpage=['3319']),
                       lambda c:c['metadata'].update(citation_doi=[F.DOI]),
                       lambda c:c.update(http_status=403)):
            with self.changed_capture('publisher',change):
                with self.assertRaisesRegex(ValueError,'Journal publisher bibliographic disagreement'):F.build(ROOT,self.at)

    def test_changed_subtitle_and_nonmatching_raw_response_are_rejected(self):
        for change in (lambda c:c['record'].update(subtitle=['Fictional unrelated title']),
                       lambda c:c.update(raw_response_sha256='0'*64)):
            with self.changed_capture('fresh_crossref',change):
                with self.assertRaisesRegex(ValueError,'Subtitle capture provenance disagreement'):F.build(ROOT,self.at)

    def test_same_doi_and_title_cannot_override_mixed_venue_disagreement(self):
        original_loads=json.loads
        def altered(raw,*a,**kw):
            value=original_loads(raw,*a,**kw)
            if isinstance(value,dict):
                for row in value.get('results',[]):
                    if row.get('id')==self.plan['retained_work_id']:row['biblio']['first_page']='3319'
            return value
        with patch.object(F.json,'loads',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'Retained mixed-identity provenance disagreement'):F.build(ROOT,self.at)

    def test_missing_parent_case_or_changed_capture_hash_is_rejected(self):
        with self.changed_plan(lambda p:p['selected'].pop()):
            with self.assertRaisesRegex(ValueError,'Fixed residual scope disagreement'):F.build(ROOT,self.at)
        with self.changed_plan(lambda p:p['publisher'].update(sha256='0'*64)):
            with self.assertRaisesRegex(ValueError,'Artifact hash mismatch'):F.build(ROOT,self.at)

    def test_frozen_ledger_drift_blocks_all_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=3
        with patch.object(F,'build',return_value=(self.records,changed)),patch.object(F,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):F.main()
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
