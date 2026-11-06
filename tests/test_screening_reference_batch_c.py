"""Bibliography subplan partition, Totland coordinates and unchanged old batches."""
from contextlib import contextmanager
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_reference_batch_c as C

ROOT=Path(__file__).resolve().parents[1]
E=C.engine


class ReferenceBatchCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=read_json(ROOT/C.LEDGER);cls.at=cls.ledger['resolved_at']
        cls.records,cls.expected=C.build(ROOT,cls.at)
        cls.plan=read_json(ROOT/C.PROFILE['plan'])

    @contextmanager
    def changed(self,field,change):
        value=read_json(ROOT/C.PROFILE[field]);change(value)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fictional-adverse-input.json';path.write_text(dumps(value))
            profile=copy.deepcopy(C.PROFILE);profile[field]=str(path)
            yield profile

    def build(self,profile):return E.build(ROOT,self.at,profile=profile)

    def test_frozen_ledger_and_record_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_twelve_duplicates_five_targets_and_no_scientific_entities(self):
        self.assertEqual(len(self.ledger['occurrences']),12)
        self.assertEqual(len({o['source_ref']['id'] for o in self.ledger['occurrences']}),5)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*12+['assistance'])
        for o in self.ledger['occurrences']:
            self.assertEqual(self.records[o['path']]['revisions'][1]['data']['status'],'duplicate')
            s=read_json(ROOT/f"research/registry/identity/records/{o['source_ref']['id']}.json")
            # This batch pins source revision 1; later access observations are allowed.
            self.assertEqual(s['revisions'][0]['data']['access_status'],'metadata_only')

    def test_every_original_discovery_field_and_hash_is_preserved(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})

    def test_four_short_titles_are_corroborated_without_transcription_claim(self):
        rows=[o for o in self.ledger['occurrences'] if o['hit_id'].startswith('HIT-R005-RLNL-')]
        self.assertEqual(len(rows),4)
        for o in rows:self.assertIn('No claim of faithful original-preprint transcription',o['verification_extent'])

    def test_totland_retains_exact_occurrence_and_page_provenance(self):
        o=next(o for o in self.ledger['occurrences'] if 'TOTLAND' in o['hit_id'])
        self.assertEqual(o['export_locator']['occurrence_id'],'C9-TOTLAND-2021-REF002')
        self.assertEqual(o['export_locator']['pdf_pages'],[42])
        self.assertEqual(o['source_pdf_sha256'],'caf75fd9f71016b869d1c27aa238c56a8f302a4ae2ce4459647203432e8d600d')
        export=read_json(ROOT/o['export_locator']['path']);row=export['references'][1]
        self.assertEqual(row['printed_pages'],['42']);self.assertTrue(all('bbox_pdf_points' in line for line in row['citation_lines']))

    def test_fra_file_and_printed_pages_stay_separate(self):
        receipt=read_json(ROOT/C.RECEIPT)
        pairs={(w['file_pages_1based'][0],w['printed_pages'][0]) for w in receipt['witnesses'] if w['pdf_key']=='fra'}
        self.assertEqual(pairs,{(36,'28'),(40,'32')})

    def test_remaining_venue_and_six_html_title_cases_stay_unresolved(self):
        parent=read_json(ROOT/self.plan['parent_plan']['path'])
        refs=[i['hit_ref'] for i in self.plan['remaining_deferred']]+parent['not_admitted'][0]['hit_refs']
        self.assertEqual(len(refs),7)
        for ref in refs:
            path=f"research/searches/auditory/records/hits/{ref['id']}.json";r=read_json(ROOT/path)
            self.assertNotIn(path,self.records)
            self.assertEqual(r['revisions'][0]['data']['status'],'unresolved')

    def test_missing_parent_case_is_rejected(self):
        with self.changed('plan',lambda p:p['remaining_deferred'].clear()) as profile:
            with self.assertRaisesRegex(ValueError,'Parent deferred scope disagreement'):self.build(profile)

    def test_duplicated_parent_case_is_rejected(self):
        with self.changed('plan',lambda p:p['remaining_deferred'].append(copy.deepcopy(p['deferred'][0]))) as profile:
            with self.assertRaisesRegex(ValueError,'Parent deferred scope disagreement'):self.build(profile)

    def test_changed_parent_plan_hash_is_rejected(self):
        with self.changed('plan',lambda p:p['parent_plan'].update(sha256='0'*64)) as profile:
            with self.assertRaisesRegex(ValueError,'Artifact hash mismatch'):self.build(profile)

    def test_failed_pdf_and_fake_hash_cannot_support_totland(self):
        for change in ({'http_status':404},{'sha256':'0'*64,'expected_sha256':'0'*64}):
            with self.subTest(change=change),self.changed('receipt',lambda r:next(p for p in r['retrievals'] if p['key']=='totland').update(change)) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_unreviewed_export_label_does_not_fall_through(self):
        profile=copy.deepcopy(C.PROFILE);profile['cases']['HIT-R005R-C9TOTLAND-00002'][0]='fictional-unreviewed'
        with self.assertRaisesRegex(ValueError,'Unreviewed reference export format'):self.build(profile)

    def test_prior_reference_batches_reproduce_exactly(self):
        from research.registry.identity.scripts import build_r006_reference_batch_b as B
        old=read_json(ROOT/E.LEDGER);self.assertEqual(E.build(ROOT,old['resolved_at'])[1],old)
        b=read_json(ROOT/B.LEDGER);self.assertEqual(B.build(ROOT,b['resolved_at'])[1],b)

    def test_frozen_ledger_drift_stops_all_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=13
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,profile=C.PROFILE)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
