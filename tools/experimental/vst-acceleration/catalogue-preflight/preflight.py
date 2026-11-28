"""Read-only preflight for MHAC Windows x64 VST3 delivery archives (Python 3.11+)."""
import argparse
import hashlib
import io
import json
import re
import stat
import struct
import sys
import zipfile
from pathlib import Path

SDK = '9fad9770f2ae8542ab1a548a68c1ad1ac690abe0'
PINS = dict(line.split() for line in '''base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206
cmake de6e54eeaaab35b7145f5c32c279b5e892146e04
doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4
pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c
public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95
tutorials 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34
vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c'''.splitlines())
LIMIT = 64 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON key: ' + k)
        result[k] = v
    return result


def module_json(text):
    # Steinberg's generator emits trailing commas. Preserve quoted strings.
    text = re.sub(r'"(?:\\.|[^"\\])*"|,(?=\s*[}\]])',
                  lambda m: '' if m.group() == ',' else m.group(), text)
    return json.loads(text, object_pairs_hook=unique_pairs)


def members(z):
    infos = z.infolist()
    require(len(infos) <= 1024 and sum(i.file_size for i in infos) <= LIMIT,
            'archive exceeds entry/expanded-byte budget')
    seen = {}
    for i in infos:
        name = i.filename.rstrip('/')
        parts = name.split('/')
        require(all(p and p not in ('.', '..') and not p.endswith((' ', '.'))
                    and not re.search(r'[\\:<>"|?*\x00-\x1f]', p)
                    and not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])', p.split('.')[0])
                    for p in parts), 'unsafe Windows path: ' + repr(i.filename))
        require(i.orig_filename == i.filename and not i.flag_bits & 1 and
                stat.S_IFMT(i.external_attr >> 16) in (0, stat.S_IFREG, stat.S_IFDIR),
                'unsafe entry: ' + repr(i.filename))
        key = name.casefold()
        require(key not in seen, 'duplicate Windows path: ' + name)
        seen[key] = i.is_dir()
    for key in seen:
        parts = key.split('/')
        require(all(seen.get('/'.join(parts[:j]), True) for j in range(1, len(parts))),
                'file is parent of another entry: ' + key)
    require(z.testzip() is None, 'ZIP CRC failure')
    return [i.filename for i in infos if not i.is_dir()]


def audit(data, expected):
    require(len(data) <= LIMIT and sha(data) == expected['sha256'], 'archive digest mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        names = members(outer)
        if len(names) == 1 and names[0].lower().endswith('.zip'):
            inner = outer.read(names[0])
        else:
            inner = data
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        names = members(z)
        def read(name):
            require(name in names, 'missing member: ' + name)
            return z.read(name)
        def text(name):
            return read(name).decode('utf-8-sig')
        receipt = unique_pairs([line.split('=', 1) for line in text('BUILD-SOURCE.txt').splitlines()])
        require(receipt == {'source': expected['source'], 'sdk': SDK}, 'source/SDK receipt mismatch')
        links = []
        for line in text('SDK-GITLINKS.txt').splitlines():
            m = re.fullmatch(r' ([0-9a-f]{40}) ([^ ]+)(?: \(.*\))?', line)
            require(m, 'unclean or malformed SDK gitlink: ' + line)
            links.append((m[2], m[1]))
        require(unique_pairs(links) == PINS, 'SDK gitlink mismatch')
        require(bool(read('Steinberg-SDK-LICENSE.txt').strip()), 'empty SDK license')
        log = text('validator.txt')
        summaries = re.findall(r'Result:\s+([1-9][0-9]*) tests passed, (\d+) tests failed', log)
        require(len(summaries) == 1 and summaries[0][1] == '0' and 'ERROR:' not in log,
                'validator transcript not clean')
        bundle = expected['bundle']
        require({n.split('/')[0] for n in names if n.split('/')[0].lower().endswith('.vst3')} == {bundle},
                'unexpected bundle root')
        binary = read(bundle + '/Contents/x86_64-win/' + bundle)
        require(len(binary) >= 64 and binary[:2] == b'MZ', 'not a PE file')
        pe = struct.unpack_from('<I', binary, 60)[0]
        require(64 <= pe <= len(binary)-26 and binary[pe:pe+4] == b'PE\0\0', 'invalid PE signature')
        machine, = struct.unpack_from('<H', binary, pe+4)
        optional_size, flags, magic = struct.unpack_from('<HHH', binary, pe+20)
        require(machine == 0x8664 and flags & 0x2000 and magic == 0x20b and
                112 <= optional_size <= len(binary)-pe-24, 'not an AMD64 PE32+ DLL')
        meta = module_json(text(bundle + '/Contents/Resources/moduleinfo.json'))
        require(meta['Name'] == bundle[:-5] and meta['Version'] == expected['version'], 'module name/version mismatch')
        classes = meta['Classes']
        require(isinstance(classes, list) and len(classes) == 2, 'expected two factory classes')
        ids = unique_pairs([(c['Category'], c['CID'].upper()) for c in classes])
        require(ids == expected['classes'] and len(set(ids.values())) == 2 and
                all(re.fullmatch(r'[0-9A-F]{32}', v) for v in ids.values()) and
                all(c['SDKVersion'] == 'VST 3.8.0' and c['Version'] == expected['version'] for c in classes),
                'factory ID/version mismatch')
        return dict(bundle=bundle, source=receipt['source'], version=meta['Version'],
                    classes=ids, validator_passed=int(summaries[0][0]), archive_sha256=sha(data),
                    delivery_sha256=sha(inner), binary_sha256=sha(binary))


def catalogue(rows):
    names, ids = set(), set()
    for row in rows:
        name = row['bundle'].casefold()
        require(name not in names, 'duplicate install name: ' + name)
        names.add(name)
        for cid in row['classes'].values():
            require(cid not in ids, 'duplicate factory CID: ' + cid)
            ids.add(cid)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path)
    p.add_argument('directory', type=Path)
    args = p.parse_args()
    try:
        entries = json.loads(args.manifest.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)
        require(isinstance(entries, list) and entries, 'empty/invalid manifest')
        rows = []
        for entry in entries:
            filename = entry['file']
            require(re.fullmatch(r'[A-Za-z0-9._-]+\.zip', filename), 'invalid manifest filename')
            path = args.directory / filename
            require(path.is_file() and path.stat().st_size <= LIMIT, 'missing/oversized archive: ' + filename)
            rows.append(audit(path.read_bytes(), entry))
        print(json.dumps({'result': 'PASS', 'packages': catalogue(rows), 'scope': 'static package preflight only'}, indent=2))
    except (ValueError, KeyError, TypeError, AttributeError, OSError, RuntimeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'result': 'FAIL', 'error': str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
