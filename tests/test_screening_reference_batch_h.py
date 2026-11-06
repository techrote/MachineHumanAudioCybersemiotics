"""Nine fixed bibliography cases and fail-closed deposited-subtitle corroboration."""
from contextlib import contextmanager
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.record_io import read_json,dumps
from research.registry.identity.scripts import build_r006_reference_batch_h as C

ROOT=Path(__file__).resolve().parents[1]
E=C.engine
RECOGNITION='SRC-R006-H-SABIC-RECOGNITION'


class ReferenceBatchHTests(unittest.TestCase):
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

    @contextmanager
    def changed_capture(self,change):
        previous=read_json(ROOT/C.PROFILE['previous']);receipt=read_json(ROOT/C.RECEIPT)
        source=next(s for s in previous['sources'] if s['source_ref']['id']==RECOGNITION)
        capture=read_json(ROOT/source['capture']['path']);change(capture)
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);cp=directory/'fictional-capture.json';cp.write_text(dumps(capture))
            source['capture']={'path':str(cp),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest()}
            next(w for w in receipt['witnesses'] if w['key']=='nees-recognition')['title_subtitle_capture']=source['capture']
            profile=copy.deepcopy(C.PROFILE)
            for key,value in [('previous',previous),('receipt',receipt)]:
                p=directory/(key+'.json');p.write_text(dumps(value));profile[key]=str(p)
            yield profile

    @contextmanager
    def changed_export(self,change):
        relative='research/searches/auditory/exports/AUDITORY-WEBSEARCH-2026-10-13.json'
        export=read_json(ROOT/relative);change(export)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'fictional-export.json';p.write_text(dumps(export))
            pin={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            def reader(path):
                value=read_json(path)
                for rev in value.get('revisions',[]):
                    body=rev['data']
                    if value['kind']=='search_run' and body.get('export',{}).get('value',{}).get('path')==relative:
                        body['export']['value']=pin
                    if value['id']=='HIT-R005-RLNL-053':
                        body['raw_metadata']=next(s for s in export['reference_lists'] if s['label']=='RL-NL')['entries'][52]['text']
                return value
            with patch.object(E,'read_json',reader):yield

    def test_frozen_ledger_and_canonical_prefixes_reproduce(self):
        self.assertEqual(self.ledger,self.expected)
        for path,expected in self.records.items():
            actual=read_json(ROOT/path)
            self.assertEqual({**actual,'revisions':actual['revisions'][:len(expected['revisions'])]},expected)

    def test_nine_duplicates_five_existing_targets_no_scientific_entities(self):
        self.assertEqual(len(self.ledger['occurrences']),9)
        self.assertEqual(len({o['source_ref']['id'] for o in self.ledger['occurrences']}),5)
        self.assertCountEqual([r['kind'] for r in self.records.values()],['search_hit']*9+['assistance'])
        for o in self.ledger['occurrences']:
            self.assertEqual(self.records[o['path']]['revisions'][1]['data']['status'],'duplicate')
            source=read_json(ROOT/f"research/registry/identity/records/{o['source_ref']['id']}.json")
            self.assertEqual(source['revisions'][0]['data']['access_status'],'metadata_only')
        for k in ('new_source_records','screening_decisions_created','study_records_created','sample_records_created'):
            self.assertEqual(self.ledger['counts'][k],0)

    def test_original_discovery_fields_hashes_and_outcome_letters_are_preserved(self):
        allowed={'status','source_ref','duplicate_of','resolution_reason'}
        for o in self.ledger['occurrences']:
            original,revision=self.records[o['path']]['revisions']
            self.assertEqual(E.digest(original),o['input_revision_sha256']);self.assertEqual(E.digest(revision),o['output_revision_sha256'])
            self.assertEqual({k:v for k,v in original['data'].items() if k not in allowed},
                             {k:v for k,v in revision['data'].items() if k not in allowed})
        path='research/searches/auditory/records/hits/HIT-R005-RLNLAM-053.json'
        self.assertTrue(self.records[path]['revisions'][1]['data']['raw_metadata'].startswith('[a,b] '))

    def test_complete_deferred_scope_and_five_witnesses_are_accounted_for(self):
        self.assertEqual({i['hit_ref']['id'] for i in self.plan['deferred']},{o['hit_id'] for o in self.ledger['occurrences']})
        receipt=read_json(ROOT/C.RECEIPT)
        self.assertEqual(len(receipt['retrievals']),2);self.assertEqual(len(receipt['witnesses']),5)
        self.assertEqual({(w['pdf_key'],tuple(w['file_pages_1based'])) for w in receipt['witnesses']},
                         {('nees-am',(46,)),('nees-am',(49,)),('nees-am',(50,)),('ruskin',(64,))})

    def test_four_short_titles_receive_identity_corroboration_only(self):
        rows=[o for o in self.ledger['occurrences'] if o['hit_id'].startswith('HIT-R005-RLNL-')]
        self.assertEqual(len(rows),4)
        for o in rows:self.assertIn('No claim of faithful original-preprint transcription',o['verification_extent'])

    def test_main_title_remains_separate_and_subtitle_capture_is_hash_bound(self):
        rows=[o for o in self.ledger['occurrences'] if o['source_ref']['id']==RECOGNITION]
        self.assertEqual(len(rows),2)
        for o in rows:self.assertIn('Deposited main title and subtitle checked separately',o['verification_extent'])
        body=read_json(ROOT/f'research/registry/identity/records/{RECOGNITION}.json')['revisions'][0]['data']
        self.assertEqual(body['title'],'Recognition of Car Warnings')
        self.assertTrue(any(a['path'].endswith('20261106-h-sabic-recognition.json') for a in self.ledger['input_artifacts']))
        short=self.records['research/searches/auditory/records/hits/HIT-R005-RLNL-053.json']['revisions'][1]['data']['raw_metadata']
        self.assertIn('Various Alert";',short);self.assertNotIn('Various Alert Types";',short)

    def test_ruskin_page_and_reference_ordinal_remain_literal(self):
        o=next(o for o in self.ledger['occurrences'] if 'C9RUSKIN' in o['hit_id'])
        self.assertEqual(o['export_locator']['item'],73);self.assertEqual(o['file_pages_1based'],[64])
        self.assertIn('C9-RUSKIN-2020-REF073',self.records[o['path']]['revisions'][1]['data']['raw_metadata'])

    def test_missing_subtitle_opt_in_cannot_expand_primary_title_matching(self):
        with self.changed('receipt',lambda r:next(w for w in r['witnesses'] if w['key']=='nees-recognition').pop('title_subtitle_capture')) as profile:
            with self.assertRaisesRegex(ValueError,'Abbreviated title disagreement'):self.build(profile)

    def test_substituted_capture_pin_is_rejected(self):
        with self.changed('receipt',lambda r:next(w for w in r['witnesses'] if w['key']=='nees-recognition')['title_subtitle_capture'].update(sha256='0'*64)) as profile:
            with self.assertRaisesRegex(ValueError,'capture pin disagreement'):self.build(profile)

    def test_missing_or_ambiguous_deposited_subtitle_is_rejected(self):
        for subtitle in ([],['One','Two'],'X',['']):
            with self.subTest(subtitle=subtitle),self.changed_capture(lambda c:c['record'].update(subtitle=subtitle)) as profile:
                with self.assertRaisesRegex(ValueError,'title/subtitle identity disagreement'):self.build(profile)

    def test_changed_registered_doi_title_or_correction_metadata_is_rejected(self):
        for fields in ({'DOI':'10.0000/fictional'},{'title':['Fictional other title']},{'relation':{'is-correction-of':['fictional']}},{'update-to':[{'DOI':'10.0000/fictional'}]}):
            with self.subTest(fields=fields),self.changed_capture(lambda c:c['record'].update(fields)) as profile:
                with self.assertRaisesRegex(ValueError,'title/subtitle identity disagreement'):self.build(profile)

    def test_fabricated_subtitle_requires_full_citation_agreement(self):
        with self.changed_capture(lambda c:c['record'].update(subtitle=['An Analysis of Various Alert Findings'])) as profile:
            with self.assertRaisesRegex(ValueError,'lacks matching full citation corroboration'):self.build(profile)

    def test_nonprefix_and_partial_word_discovery_titles_are_rejected(self):
        for ending in ('Various Al','Various Other Alerts'):
            def change(export):
                row=next(s for s in export['reference_lists'] if s['label']=='RL-NL')['entries'][52]
                row['text']=row['text'].replace('Various Alert"',''+ending+'"')
            with self.subTest(ending=ending),self.changed_export(change):
                with self.assertRaisesRegex(ValueError,'title/subtitle prefix disagreement'):C.build(ROOT,self.at)

    def test_pdf_hash_or_failed_retrieval_cannot_support_identity(self):
        for fields in ({'http_status':403},{'sha256':'0'*64}):
            with self.subTest(fields=fields),self.changed('receipt',lambda r:r['retrievals'][0].update(fields)) as profile:
                with self.assertRaisesRegex(ValueError,'Same-byte source PDF'):self.build(profile)

    def test_missing_or_changed_witness_and_impossible_page_are_rejected(self):
        for change in (lambda r:r['witnesses'].pop(),lambda r:r['witnesses'][0].update(checked_doi='10.0000/fictional'),lambda r:r['witnesses'][0].update(file_pages_1based=[999])):
            with self.changed('receipt',change) as profile:
                with self.assertRaises(ValueError):self.build(profile)

    def test_frozen_ledger_drift_prevents_writes(self):
        changed=copy.deepcopy(self.ledger);changed['counts']['occurrences']=10
        with patch.object(E,'build',return_value=(self.records,changed)),patch.object(E,'write_generated_records') as writer,patch('sys.argv',['builder']):
            with self.assertRaisesRegex(SystemExit,'ledger drift'):E.main(root=ROOT,profile=C.PROFILE)
            writer.assert_not_called()


if __name__=='__main__':unittest.main()
