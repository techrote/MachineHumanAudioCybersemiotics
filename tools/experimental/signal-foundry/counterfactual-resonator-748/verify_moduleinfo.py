"""Fail closed on module/class identity drift; supports SDK trailing commas."""
import argparse
import json
import re
import unittest
import zipfile
from pathlib import Path

PINS = {
    'MHACCounterfactualResonator': ('0.2.0', 'FBC2EF81CA534C7A8B3BC61D9929C901', 'A1C2780816014C3A8AC0E00B6D775BD5'),
    'MHACHarmonicMemoryBank': ('0.3.0', 'AE00577BADF94D9C8F2FB9D04991475C', 'B82C6F98A6D847E9B6084DF9834F4B45'),
}
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|,\s*(?=[}\]])')


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def verify(raw, name):
    version, processor, controller = PINS[name]
    info = json.loads(TOKEN.sub(lambda m: m[0] if m[0].startswith('"') else '',
                               raw.decode('utf-8-sig')), object_pairs_hook=unique)
    if info['Version'] != version:
        raise ValueError(f'{name}: module version {info["Version"]!r}, expected {version}')
    classes = info['Classes']
    expected = {processor: 'Audio Module Class', controller: 'Component Controller Class'}
    if len(classes) != len(expected):
        raise ValueError(f'{name}: unexpected class count')
    for cls in classes:
        cid = cls['CID']
        if expected.pop(cid, None) != cls['Category'] or cls['Version'] != version or cls['SDKVersion'] != 'VST 3.8.0':
            raise ValueError(f'{name}: class identity/version/SDK mismatch: {cid}')
    if expected:
        raise ValueError(f'{name}: missing classes')


def read_metadata(path, name):
    rel = name + '.vst3/Contents/Resources/moduleinfo.json'
    if path.is_dir():
        if path.name != name + '.vst3':
            raise ValueError('Unexpected bundle directory name')
        return (path / 'Contents/Resources/moduleinfo.json').read_bytes()
    with zipfile.ZipFile(path) as archive:
        if archive.namelist().count(rel) != 1 or archive.testzip() is not None:
            raise ValueError('Missing/duplicate moduleinfo or corrupt archive')
        return archive.read(rel)


class MetadataTests(unittest.TestCase):
    def fixture(self, name):
        version, processor, controller = PINS[name]
        return {'Version': version, 'Classes': [
            {'CID': cid, 'Category': cat, 'Version': version, 'SDKVersion': 'VST 3.8.0'}
            for cid, cat in [(processor, 'Audio Module Class'), (controller, 'Component Controller Class')]]}

    def test_valid(self):
        for name in PINS:
            data = self.fixture(name)
            data['Name'] = 'literal ,} and ,] inside string'
            raw = json.dumps(data).replace('}]', '},]').encode()
            verify(raw, name)

    def test_negative(self):
        name = 'MHACHarmonicMemoryBank'
        for field, value in [('Version', '0.2.0'), ('CID', 'bad'), ('SDKVersion', 'VST 3.8.1'), ('Category', 'wrong')]:
            data = self.fixture(name)
            data['Classes'][0][field] = value
            with self.assertRaises(ValueError):
                verify(json.dumps(data).encode(), name)
        for mutation in ('module', 'duplicate_class', 'missing_class'):
            data = self.fixture(name)
            if mutation == 'module': data['Version'] = '0.2.0'
            elif mutation == 'duplicate_class': data['Classes'][1] = data['Classes'][0]
            else: data['Classes'].pop()
            with self.assertRaises(ValueError):
                verify(json.dumps(data).encode(), name)
        with self.assertRaises(ValueError):
            verify(b'{"Version":"0.2.0","Version":"0.3.0"}', name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('name', nargs='?', choices=PINS)
    parser.add_argument('path', nargs='?', type=Path)
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=[__file__])
    elif args.name and args.path:
        verify(read_metadata(args.path, args.name), args.name)
        print(f'MODULEINFO_PASS {args.name} {PINS[args.name][0]} classes=2')
    else:
        parser.error('provide name and bundle/ZIP path or --self-test')
