"""Fixed title presentation, ICAD provenance and truthful access observations."""
from contextlib import contextmanager
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_batch_c_final as F

ROOT=Path(__file__).resolve().parents[1]


class BatchCFinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=read_json(ROOT/F.PLAN);cls.ledger=read_json(ROOT/F.LEDGER);cls.at=cls.ledger['resolved_at']
        cls.records,cls.expected=F.build(ROOT,cls.at)

    @contextmanager
    def changed_artifact(self,key,change):
        plan=copy.deepcopy(self.plan);value=read_json(ROOT/plan[key]['path']);change(value)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-capture.json';path.write_text(dumps(value))
            plan[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            pp=Path(directory)/'fictional-plan.json';pp.write_text(dumps(plan))
            with patch.object(F,'PLAN',str(pp)):yield

    def test_frozen_ledger_and_all_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_seven_resolutions_one_new_publication_one_observation(self):
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*7+['source']*2+['assistance'])
        c=self.ledger['counts'];self.assertEqual(c['occurrences'],7);self.assertEqual(c['new_source_records'],1)
        self.assertEqual(c['resolved_representatives'],1);self.assertEqual(c['duplicate_occurrences'],6)
        self.assertEqual(c['source_access_observations'],1)
        for key in ('screening_decisions_created','study_records_created','sample_records_created'):self.assertEqual(c[key],0)

    def test_original_discovery_metadata_and_hashes_are_preserved(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(F.E.digest(original),o['input_revision_sha256']);self.assertEqual(F.E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_actual_line_feed_and_exact_title_mapping_are_explicit(self):
        raw=read_json(ROOT/self.plan['raw_crossref']['path'])['record']['title'][0]
        self.assertIn(chr(10),raw);self.assertNotIn(chr(92)+'n',raw)
        self.assertEqual(raw,F.RAW_TITLE)
        source=self.records[F.AREA+'/records/'+F.WILCOX+'.json']['revisions'][0]['data']
        self.assertEqual(source['title'],F.DISPLAY_TITLE);self.assertIn('Perspective :',source['title'])
        self.assertEqual(source['publication_date']['value'],'2011-07')

    def test_unreviewed_tags_or_literal_slash_n_are_not_accepted(self):
        for title in (F.RAW_TITLE.replace('<i>','<b>'),F.RAW_TITLE.replace(chr(10),chr(92)+'n')):
            with self.subTest(title=title),self.changed_artifact('raw_crossref',lambda r:r['record'].update(title=[title])):
                with self.assertRaisesRegex(ValueError,'Fixed raw title/DOI disagreement'):F.build(ROOT,self.at)

    def test_changed_pubmed_doi_is_rejected_even_with_valid_capture_hash(self):
        with self.changed_artifact('pubmed',lambda p:p['record']['identifiers'].update(doi='10.1234/fictional')):
            with self.assertRaisesRegex(ValueError,'PubMed bibliographic disagreement'):F.build(ROOT,self.at)

    def test_fresh_venue_uuid_or_doi_disagreement_is_rejected(self):
        changes=[lambda c:c['record'].update(uuid='fictional-wrong-item'),lambda c:c['metadata']['dc.identifier.doi'][0].update(value='10.1234/fictional')]
        for change in changes:
            with self.subTest(change=change),self.changed_artifact('gatech',change):
                with self.assertRaisesRegex(ValueError,'Fresh venue identity disagreement'):F.build(ROOT,self.at)

    def test_exact_original_venue_text_is_required(self):
        def reader(path):
            value=read_json(path)
            if str(path).endswith(F.VENUE+'.json'):value['revisions'][0]['data']['raw_metadata']='Fictional changed venue label'
            return value
        with patch.object(F,'read_json',reader):
            with self.assertRaisesRegex(ValueError,'Venue discovery text disagreement'):F.build(ROOT,self.at)

    def test_original_venue_doi_assertion_is_required(self):
        def reader(path):
            value=read_json(path)
            if str(path).endswith(F.VENUE+'.json'):value['revisions'][0]['data']['returned_identifiers']=[{'scheme':'doi','value':'10.1234/fictional'}]
            return value
        with patch.object(F,'read_json',reader):
            with self.assertRaisesRegex(ValueError,'Venue original DOI disagreement'):F.build(ROOT,self.at)

    def test_parent_residue_cannot_be_silently_shrunk(self):
        plan=copy.deepcopy(self.plan);plan['selected'].pop()
        with patch.object(F,'read_json',side_effect=lambda p:copy.deepcopy(plan) if str(p).endswith(F.PLAN) else read_json(p)):
            with self.assertRaisesRegex(ValueError,'Fixed residual scope disagreement'):F.build(ROOT,self.at)

    def test_source_access_exposure_does_not_become_full_reading(self):
        wilcox=self.records[F.AREA+'/records/'+F.WILCOX+'.json']['revisions'][0]['data']
        tislar=self.records[F.AREA+'/records/'+F.TISLAR+'.json']['revisions'][1]['data']
        self.assertEqual(wilcox['access_status'],'partial_text');self.assertEqual(tislar['access_status'],'abstract_only')
        for b in (wilcox,tislar):self.assertEqual(b['manifestations'],[]);self.assertEqual(b['rights']['status'],'unknown')
        aid=self.records[F.AREA+'/records/'+F.AID+'.json']['revisions'][0]['data']
        self.assertEqual(aid['subtype'],'assistance');self.assertIn('No full-paper reading',aid['limitations'])
        self.assertEqual(len(aid['input_refs']),len({(r['id'],r['rev']) for r in aid['input_refs']}))

    def test_tislar_observation_preserves_material_identity(self):
        original,current=self.records[F.AREA+'/records/'+F.TISLAR+'.json']['revisions']
        changed={'access_status','access_at','access_reason','metadata_evidence'}
        self.assertEqual({k:v for k,v in original['data'].items() if k not in changed},
                         {k:v for k,v in current['data'].items() if k not in changed})
        self.assertEqual(original,read_json(ROOT/(F.AREA+'/records/'+F.TISLAR+'.json'))['revisions'][0])

    def test_venue_locator_and_representative_are_not_title_only(self):
        o=next(o for o in self.ledger['occurrences'] if o['hit_id']==F.VENUE)
        self.assertEqual(o['export_locator']['repository_item_id'],F.UUID)
        self.assertEqual(o['export_locator']['manifest_ordinal'],1072)
        self.assertIn('/objects/80/',o['export_locator']['json_pointer'])
        self.assertIsNotNone(o['duplicate_of']);self.assertEqual(o['source_ref'],F.E.pin(F.TISLAR))

    def test_frozen_ledger_drift_prevents_any_canonical_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=8
        with patch.object(F,'build',return_value=(self.records,changed)),patch.object(F,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):F.main()
            writer.assert_not_called()

    def test_existing_identity_and_reference_ledgers_still_reproduce(self):
        from research.registry.identity.scripts import build_r006_doi_batch_c as C
        from research.registry.identity.scripts import build_r006_reference_batch_c as R
        for module in (C,R):
            ledger=read_json(ROOT/module.LEDGER);self.assertEqual(module.build(ROOT,ledger['resolved_at'])[1],ledger)


if __name__=='__main__':unittest.main()
