"""Negative controls on the frozen synthetic corpus; no human data."""
import copy, hashlib, json, pathlib, shutil, tempfile, unittest
import check_interaction as check

ROOT=pathlib.Path(__file__).resolve().parent

class NegativeControls(unittest.TestCase):
    def test_mutations(self):
        r=json.loads((ROOT/'run1/receipt.json').read_text())
        cases=[('clean','send',{'kind':'ACT'},{'delay':2}),
               ('clean','apply',{}, {'seq':7}),
               ('clean','receipt',{}, {'ack':7}),
               ('forward-restored','status-accept',{}, {'nonce':999})]
        for regime,event,match,change in cases:
            with self.subTest(event=event):
                trace=copy.deepcopy(r['witnesses'][regime+'/bound'])
                next(x for x in trace if x['event']==event and all(x.get(k)==v for k,v in match.items())).update(change)
                with self.assertRaises(ValueError): check.audit(trace,regime,'bound')

    def test_rehashed_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            for n in check.BLOBS: shutil.copyfile(ROOT/n,root/n)
            shutil.copytree(ROOT/'run1',root/'run1')
            wav=next((root/'run1').glob('*.wav')); data=bytearray(wav.read_bytes()); data[-1]^=1; wav.write_bytes(data)
            p=root/'run1/manifest.json'; m=json.loads(p.read_text()); m[wav.name]=hashlib.sha256(data).hexdigest(); p.write_text(json.dumps(m,sort_keys=True)+'\n')
            with self.assertRaisesRegex(ValueError,'frozen manifest mismatch'): check.main(root)

if __name__=='__main__': unittest.main()
