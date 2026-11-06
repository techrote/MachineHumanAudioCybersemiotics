"""Larger fixed identity batch, conservative title mismatch and provenance limits."""
import copy
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch
from tools.record_io import read_json
from research.registry.identity.scripts import build_r006_doi_batch_c as C

ROOT=Path(__file__).resolve().parents[1]
E=C.engine


class DoiBatchCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=read_json(ROOT/C.PLAN);cls.ledger=read_json(ROOT/C.LEDGER)
        cls.at=cls.ledger['resolved_at'];cls.records,cls.expected=C.build(ROOT,cls.at)

    def test_frozen_ledger_and_all_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_nine_publications_38_occurrences_13_deferred_no_scientific_entities(self):
        self.assertCountEqual([r['kind'] for r in self.records.values()],['source']*9+['search_hit']*38+['assistance'])
        self.assertEqual(len(self.ledger['deferred']),13)
        self.assertEqual(sum(o['status']=='resolved' for o in self.ledger['occurrences']),9)
        self.assertEqual(sum(o['status']=='duplicate' for o in self.ledger['occurrences']),29)
        for key in ('screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][key],0)

    def test_sources_remain_metadata_only_and_chapters_stay_chapters(self):
        sources=[r for r in self.records.values() if r['kind']=='source']
        for source in sources:
            b=source['revisions'][0]['data']
            self.assertEqual(b['access_status'],'metadata_only');self.assertEqual(b['manifestations'],[])
            self.assertEqual(b['rights']['status'],'unknown');self.assertEqual(b['family_links'],[])
        self.assertEqual({s['id'] for s in sources if s['revisions'][0]['data']['source_type']=='chapter'},
                         {'SRC-R006-BREWSTER-1997-TELEPHONE','SRC-R006-GYGI-2010-ENVIRONMENTAL'})

    def test_original_discovery_fields_and_revision_hashes_are_retained(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_unadmitted_html_title_is_retained_and_six_hits_are_unresolved(self):
        item,=self.plan['not_admitted'];capture=read_json(ROOT/item['capture']['path'])
        self.assertEqual(hashlib.sha256((ROOT/item['capture']['path']).read_bytes()).hexdigest(),item['capture']['sha256'])
        self.assertEqual(capture['record']['title'][0],item['reported_title']);self.assertIn('<i>',item['reported_title'])
        self.assertEqual(len(item['hit_refs']),6)
        for ref in item['hit_refs']:
            path=ROOT/f"research/searches/auditory/records/hits/{ref['id']}.json"
            record=read_json(path);self.assertEqual(len(record['revisions']),1)
            self.assertEqual(record['revisions'][0]['data']['status'],'unresolved')
            self.assertNotIn(str(path.relative_to(ROOT)),self.records)
        self.assertNotIn(item['doi'],{i['doi'] for i in self.plan['sources']})

    def test_deferred_reference_and_venue_occurrences_are_not_silently_linked(self):
        venue=[i for i in self.plan['deferred'] if 'C5SERIES' in i['hit_ref']['id']]
        self.assertEqual(len(venue),1);self.assertIn('ICAD-series',venue[0]['defer_reason'])
        for item in self.plan['deferred']:
            path=f"research/searches/auditory/records/hits/{item['hit_ref']['id']}.json"
            self.assertNotIn(path,self.records)
            record=read_json(ROOT/path);self.assertEqual(len(record['revisions']),1)
            self.assertEqual(record['revisions'][0]['data']['status'],'unresolved')

    def test_date_assertions_and_discovery_dates_are_not_harmonized(self):
        source=self.records['research/registry/identity/records/SRC-R006-SANDERSON-2009-ANESTHESIOLOGY.json']['revisions'][0]['data']
        self.assertEqual(source['publication_date']['value'],'2009-12')
        cases=[o for o in self.ledger['occurrences'] if o['source_ref']['id']=='SRC-R006-SANDERSON-2009-ANESTHESIOLOGY']
        self.assertTrue(any(o['export_locator'].get('reported_publication_date')=='2009-10-31' for o in cases))
        self.assertTrue(all('2009-10-31' in self.records[o['path']]['revisions'][1]['data']['raw_metadata'] for o in cases))

    def test_retained_title_disagreement_prevents_source_linking(self):
        hid=self.plan['selected'][0]['hit_ref']['id']
        def reader(path):
            value=read_json(path)
            if str(path).endswith(hid+'.json'):value['revisions'][0]['data']['raw_metadata']='Fictional inconsistent title'
            return value
        with patch.object(E,'read_json',reader):
            with self.assertRaisesRegex(ValueError,'Retained DOI/full-title disagreement'):C.build(ROOT,self.at)

    def test_unadmitted_capture_hash_is_checked_before_build(self):
        plan=copy.deepcopy(self.plan);plan['not_admitted'][0]['capture']['sha256']='0'*64
        with patch.object(C,'read_json',return_value=plan):
            with self.assertRaisesRegex(ValueError,'ARTIFACT_HASH'):C.build(ROOT,self.at)

    def test_frozen_ledger_drift_stops_canonical_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=39
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,build_options=C.OPTIONS)
            writer.assert_not_called()

    def test_original_and_batch_b_outputs_still_reproduce(self):
        from research.registry.identity.scripts import build_r006_doi_batch_b as B
        old=read_json(ROOT/E.LEDGER);self.assertEqual(E.build(ROOT,old['resolved_at'])[1],old)
        b=read_json(ROOT/B.LEDGER);self.assertEqual(B.build(ROOT,b['resolved_at'])[1],b)


if __name__=='__main__':unittest.main()
