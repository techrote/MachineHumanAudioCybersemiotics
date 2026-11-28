"""Synthetic negative fixtures; optionally run against the real frozen archive manifest."""
import copy
import io
import json
import struct
import unittest
import zipfile
from preflight import SDK, PINS, audit, catalogue, module_json, sha

BUNDLE = 'Test.vst3'
CLASSES = {'Audio Module Class': '1' * 32, 'Component Controller Class': '2' * 32}


def archive(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, value in files.items():
            z.writestr(name, value)
    return out.getvalue()


def fixture():
    binary = bytearray(512)
    binary[:2] = b'MZ'
    struct.pack_into('<I', binary, 60, 64)
    binary[64:68] = b'PE\0\0'
    struct.pack_into('<H', binary, 68, 0x8664)
    struct.pack_into('<HHH', binary, 84, 240, 0x2000, 0x20b)
    files = {'BUILD-SOURCE.txt': f'source={"a"*40}\nsdk={SDK}\n',
             'SDK-GITLINKS.txt': ''.join(f' {v} {k}\n' for k, v in PINS.items()),
             'Steinberg-SDK-LICENSE.txt': 'synthetic fixture; not an SDK license',
             'validator.txt': 'Result: 47 tests passed, 0 tests failed\n',
             BUNDLE + '/Contents/x86_64-win/' + BUNDLE: bytes(binary),
             BUNDLE + '/Contents/Resources/moduleinfo.json': json.dumps({
                 'Name': 'Test', 'Version': '0.1.0', 'Classes': [
                     {'Category': k, 'CID': v, 'Version': '0.1.0', 'SDKVersion': 'VST 3.8.0'}
                     for k, v in CLASSES.items()]})}
    expected = {'source': 'a'*40, 'bundle': BUNDLE, 'version': '0.1.0', 'classes': CLASSES}
    return files, expected


class PreflightTests(unittest.TestCase):
    def check(self, files, expected, wrapped=False):
        data = archive(files)
        if wrapped:
            data = archive({'delivery.zip': data})
        return audit(data, dict(expected, sha256=sha(data)))

    def test_direct_and_nested(self):
        f, e = fixture()
        self.assertEqual(self.check(f,e)['binary_sha256'], self.check(f,e,True)['binary_sha256'])

    def test_trailing_comma_and_duplicate_key(self):
        self.assertEqual(module_json('{"x":"comma,}",}'), {'x':'comma,}'})
        with self.assertRaises(ValueError):
            module_json('{"x":1,"x":2,}')

    def test_mutations(self):
        f,e = fixture()
        binary = BUNDLE + '/Contents/x86_64-win/' + BUNDLE
        meta = BUNDLE + '/Contents/Resources/moduleinfo.json'
        wrong_machine = bytearray(f[binary]); struct.pack_into('<H', wrong_machine, 68, 0x14c)
        cases = [('../escape', b'x'), ('CON.txt', b'x'), ('test.vst3/contents/x86_64-win/test.vst3', b'x'),
                 ('test.vst3', b'x'), ('x:y', b'x'), ('a/./b', b'x'),
                 ('BUILD-SOURCE.txt', f'source={"b"*40}\nsdk={SDK}\n'),
                 ('SDK-GITLINKS.txt', f['SDK-GITLINKS.txt'].replace(' base', ' bogus')),
                 ('SDK-GITLINKS.txt', '+' + f['SDK-GITLINKS.txt'][1:]),
                 ('validator.txt', f['validator.txt'] + 'ERROR: false green\n'),
                 ('validator.txt', 'Result: 47 tests passed, 1 tests failed'),
                 ('validator.txt', f['validator.txt']*2),
                 ('Steinberg-SDK-LICENSE.txt', ''), (binary, bytes(wrong_machine)),
                 (binary, b'MZ'), (meta, f[meta].replace('VST 3.8.0','VST 3.8.1')),
                 (meta, f[meta].replace('1'*32,'2'*32)), (meta, f[meta].replace('0.1.0','0.2.0'))]
        for name, value in cases:
            with self.subTest(name=name, value=str(value)[:50]), self.assertRaises(ValueError):
                self.check(dict(f, **{name:value}), e)

    def test_digest(self):
        f,e = fixture()
        with self.assertRaisesRegex(ValueError, 'digest'):
            audit(archive(f), dict(e, sha256='0'*64))

    def test_catalogue_collisions(self):
        f,e = fixture(); row = self.check(f,e)
        with self.assertRaisesRegex(ValueError, 'install name'):
            catalogue([row, dict(row, bundle='test.vst3')])
        with self.assertRaisesRegex(ValueError, 'factory CID'):
            catalogue([row, dict(row, bundle='Other.vst3')])


if __name__ == '__main__':
    unittest.main()
