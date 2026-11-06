"""Offline real-Git snapshots and adverse batch framing; no live research records."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from schemas import ValidationError
from tests.test_record_loading import live_gate_sentinel,state
from tools import records
from tools.record_io import dumps


class BatchedSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.git('init','-q','-b','main')

    def git(self,*args):
        r=subprocess.run(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
            '-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null',*args],cwd=self.root,
            capture_output=True,text=True,timeout=15)
        self.assertEqual(r.returncode,0,r.stderr);return r.stdout.strip()

    def write(self,path,value):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(dumps(value),encoding='utf-8');return p

    def commit(self):
        self.git('add','--all');self.git('commit','-q','-m','Explicitly synthetic history fixture');return self.git('rev-parse','HEAD')

    def test_multiple_batches_preserve_committed_records_and_bound_git_processes(self):
        self.write(records.STATE_PATH,state());expected=[]
        for n in range(5):
            row=live_gate_sentinel();row['id']=f'HG-BATCH-{n}';row['revisions'][0]['data']['reason']='Café π: line one\nline two'
            self.write('research/registry/records/'+row['id']+'.json',row);expected.append(row)
        ref=self.commit()
        self.write('research/registry/records/HG-BATCH-0.json',{'rewritten':'worktree bytes'})
        with patch.object(records,'_HISTORY_BATCH_SIZE',2),patch.object(records.subprocess,'run',wraps=subprocess.run) as run:
            snapshot=records.snapshot_from_git(self.root,ref)
        self.assertEqual(snapshot['records'],expected)
        calls=[c.args[0] for c in run.call_args_list]
        self.assertEqual(len(calls),6)  # Three setup reads plus ceil(5 / 2) blob batches.
        self.assertEqual(sum(c[-2:]==['cat-file','--batch'] for c in calls),3)
        self.assertEqual(sum('show' in c for c in calls),1)  # Registry state only.
        records.assert_append_only(snapshot,snapshot)

    def test_quoted_unicode_cr_tab_newline_record_root_is_not_skipped(self):
        root='research/sources/évidence set\rpart\tmore\nrows';manifest=state();manifest['record_roots']=[root]
        self.write(records.STATE_PATH,manifest);row=live_gate_sentinel();self.write(root+'/'+row['id']+'.json',row)
        self.assertEqual(records.snapshot_from_git(self.root,self.commit())['records'],[row])

    def test_quoted_bootstrap_record_cannot_hide_missing_registry(self):
        self.write('research/gates/évidence\tpart\nrows/HG-LOADER-TEST.json',live_gate_sentinel())
        with self.assertRaisesRegex(ValidationError,'^HISTORY_STATE:'):records.snapshot_from_git(self.root,self.commit())

    def test_historical_symlink_and_executable_json_still_fail(self):
        self.write(records.STATE_PATH,state());p=self.write('research/registry/records/HG-LOADER-TEST.json',live_gate_sentinel())
        for mode in ['100755','120000']:
            self.git('add','--all');oid=self.git('hash-object','-w',str(p))
            self.git('update-index','--cacheinfo',mode,oid,'research/registry/records/HG-LOADER-TEST.json')
            self.git('commit','-q','-m','Synthetic invalid-mode fixture');ref=self.git('rev-parse','HEAD')
            with self.subTest(mode=mode),self.assertRaisesRegex(ValidationError,'^HISTORY_PATH:'):
                records.snapshot_from_git(self.root,ref)

    def test_historical_filename_id_disagreement_still_fails(self):
        self.write(records.STATE_PATH,state());self.write('research/registry/records/HG-WRONG.json',live_gate_sentinel())
        with self.assertRaisesRegex(ValidationError,'^RECORD_FILENAME:'):records.snapshot_from_git(self.root,self.commit())

    def test_repeated_blob_ids_preserve_each_path_and_multibyte_json(self):
        row={'fixture':'é π\nsecond line'};p=self.write('fixture.json',row);oid=self.git('hash-object','-w',str(p))
        self.assertEqual(list(records._git_json_blobs(self.root,[('first',oid),('second',oid)])),[('first',row),('second',row)])


class BatchProtocolTests(unittest.TestCase):
    def frame(self,payload=b'{}',oid=None,kind=b'blob',size=None):
        oid=oid or hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
        return oid,oid.encode()+b' '+kind+b' '+str(len(payload) if size is None else size).encode()+b'\n'+payload+b'\n'

    def parse(self,raw,oid,returncode=0):
        result=subprocess.CompletedProcess(['git'],returncode,stdout=raw,stderr=b'fixture Git failure')
        with patch.object(records.subprocess,'run',return_value=result):
            return list(records._git_json_blobs(Path('/fictional-fixture'),[('fixture.json',oid)]))

    def test_empty_selection_starts_no_git_process(self):
        with patch.object(records.subprocess,'run') as run:
            self.assertEqual(list(records._git_json_blobs(Path('/fictional-fixture'),[])),[])
            run.assert_not_called()

    def test_wrong_identity_type_and_missing_object_fail_closed(self):
        oid,raw=self.frame()
        variants=[raw.replace(oid.encode(),b'0'*40,1),self.frame(kind=b'tree')[1],oid.encode()+b' missing\n',b'']
        for value in variants:
            with self.subTest(raw=value),self.assertRaisesRegex(ValidationError,'^HISTORY_OBJECT:'):self.parse(value,oid)

    def test_invalid_or_excessive_size_header_fails_closed(self):
        oid,_=self.frame()
        for size in ['-1','1x','01','9'*200]:
            raw=oid.encode()+b' blob '+size.encode()+b'\n{}\n'
            with self.subTest(size=size),self.assertRaisesRegex(ValidationError,'^HISTORY_OBJECT:'):self.parse(raw,oid)

    def test_truncated_payload_or_missing_delimiter_fails_closed(self):
        oid,raw=self.frame(b'{"fixture":1}')
        for value in [raw[:-1],raw[:-3],raw[:-1]+b'x',self.frame(size=99999)[1]]:
            with self.subTest(raw=value),self.assertRaisesRegex(ValidationError,'^HISTORY_OBJECT:'):self.parse(value,oid)

    def test_trailing_output_is_not_ignored(self):
        oid,raw=self.frame()
        with self.assertRaisesRegex(ValidationError,'^HISTORY_OBJECT:'):self.parse(raw+b'additional object\n',oid)

    def test_non_utf8_blob_fails_with_validation_error(self):
        oid,raw=self.frame(b'{"fixture":"\xff"}')
        with self.assertRaisesRegex(ValidationError,'^HISTORY_OBJECT:'):self.parse(raw,oid)

    def test_duplicate_keys_and_nonfinite_json_remain_rejected(self):
        for body,code in [(b'{"id":1,"id":2}','JSON_DUPLICATE_KEY'),(b'{"x":NaN}','JSON_NONFINITE')]:
            oid,raw=self.frame(body)
            with self.subTest(body=body),self.assertRaisesRegex(ValidationError,'^'+code+':'):self.parse(raw,oid)

    def test_git_error_is_not_an_empty_or_partial_snapshot(self):
        oid,raw=self.frame()
        with self.assertRaisesRegex(ValidationError,'^HISTORY_REF:'):self.parse(raw,oid,returncode=1)

    def test_sha256_object_name_and_exact_utf8_byte_size_are_supported(self):
        payload=dumps({'fixture':'é π'}).encode();oid=hashlib.sha256(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
        _,raw=self.frame(payload,oid=oid)
        self.assertEqual(self.parse(raw,oid),[('fixture.json',{'fixture':'é π'})])


if __name__=='__main__':unittest.main()
