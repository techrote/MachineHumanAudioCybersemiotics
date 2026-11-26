"""Native packaging contract tests; fixture JS is not upstream MHAC apparatus."""
import json
from pathlib import Path
import tempfile
import unittest
from build_observatory import build, blob, inventory

SCRIPT = '''const fs=require('node:fs'),p=require('node:path'),c=require('node:crypto');
const out=process.argv[2];fs.mkdirSync(out);const h=b=>c.createHash('sha256').update(b).digest('hex');
const core=fs.readFileSync(p.join(__dirname,'core.js'));
const pin=c.createHash('sha1').update('blob '+core.length+'\\0').update(core).digest('hex');
const wav=Buffer.alloc(48);wav.write('RIFF');wav.writeUInt32LE(40,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(8000,24);wav.writeUInt32LE(16000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(4,40);wav.writeInt16LE(-2048,44);wav.writeInt16LE(1024,46);
const files={'index.html':'<html>fixture</html>','receipt.json':'{}','specimen.wav':wav};
for(const [n,b] of Object.entries(files))fs.writeFileSync(p.join(out,n),b);
fs.writeFileSync(p.join(out,'manifest.json'),JSON.stringify({pins:{'core.js':pin},sourceSHA256:h(fs.readFileSync(__filename)),files:Object.fromEntries(Object.entries(files).map(([n,b])=>[n,h(b)]))}));
'''

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.jobs = {'legacy': 'fixture.cjs', 'selective': 'fixture.cjs'}
        self.write(SCRIPT)

    def write(self, script):
        files = {'core.js': b'// fixture\n', 'index.html': b'<html>fixture</html>',
                 'phase.html': b'<html>fixture</html>', 'fixture.cjs': script.encode()}
        self.pins = {n: blob(b) for n,b in files.items()}
        for n,b in files.items():
            (self.source/n).write_bytes(b)

    def run_build(self, name='out'):
        return build(self.source, self.root/name, pins=self.pins, jobs=self.jobs)

    def test_native_and_repeat(self):
        m = self.run_build()
        self.assertEqual(m, self.run_build('again'))
        self.assertEqual(inventory(self.root/'out'), inventory(self.root/'again'))
        self.assertEqual(len(m['files']), 13)
        self.assertEqual(m['audio']['legacy']['specimen.wav']['peakPCM16'], 2048)
        self.assertEqual(json.loads((self.root/'out/package-manifest.json').read_text()), m)

    def test_source_mismatch(self):
        (self.source/'core.js').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Frozen source mismatch'):
            self.run_build()
        self.assertFalse((self.root/'out').exists())

    def test_existing_output(self):
        self.run_build()
        with self.assertRaises(FileExistsError):
            self.run_build()

    def test_bad_manifest(self):
        self.write(SCRIPT+"fs.writeFileSync(p.join(out,'receipt.json'),'bad');\n")
        with self.assertRaisesRegex(ValueError, 'inventory/hash mismatch'):
            self.run_build()
        self.assertFalse((self.root/'out').exists())

    def test_undeclared_file(self):
        self.write(SCRIPT+"fs.writeFileSync(p.join(out,'extra'),'bad');\n")
        with self.assertRaisesRegex(ValueError, 'inventory/hash mismatch'):
            self.run_build()
        self.assertFalse((self.root/'out').exists())

    def test_source_mutation(self):
        self.write(SCRIPT+"fs.appendFileSync(p.join(__dirname,'core.js'),'bad');\n")
        # The second job detects the changed core's pin before publication.
        with self.assertRaisesRegex(ValueError, 'dependency mismatch'):
            self.run_build()
        self.assertFalse((self.root/'out').exists())

if __name__ == '__main__':
    unittest.main()
