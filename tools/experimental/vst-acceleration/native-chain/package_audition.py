"""Assemble the exact ACCEL-037 Windows owner audition set, offline."""
import argparse
import hashlib
import io
import json
import re
import struct
import wave
import zipfile
from pathlib import Path, PurePosixPath

SDK = '9fad9770f2ae8542ab1a548a68c1ad1ac690abe0'
SOURCE = 'd996a0b8c457630e3d18a4b2a06393640f8d3fbf'
HOST_SHA = 'e9300c376c22bc937899d2eed1e5045cf3be8b922c0c08cd88d202d69bc2c6d9'
TRACE = dict(source=SOURCE, sdk=SDK, outer_sha256='fa74dd77708ab33537b0f69037ecc92f8236297ffc3f09580860d71fe82595c9', inner_sha256='c36408772286a89314373a3126a878521df51b50dfa8e0a5e3fc8e70012ec327', binary_sha256='f2bc429bc1df60bb0c05e67ce2b05bbf675cecd19901173a546c09f0950187a5', cid='A6740DA9EA17442B9B283CF2584E908C')
NAMES = {'afterimage': 'MHACAfterimage', 'winters': 'MHACThreeWinters', 'receipt': 'MHACReceiptFold', 'trace': 'MHACTraceBell'}
IDS = {'afterimage': 15148180211, 'winters': 15156181930, 'receipt': 15145497011, 'trace': 15195705883}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [n for n in z.namelist() if not n.endswith('/')]
        require(len(names) == len(set(n.casefold() for n in names)), 'duplicate archive path')
        for n in names:
            p = PurePosixPath(n)
            require(not p.is_absolute() and '..' not in p.parts and '\\' not in n and ':' not in n, 'unsafe path')
        require(z.testzip() is None, 'archive CRC')
        return {n: z.read(n) for n in names}


def wav(data):
    with wave.open(io.BytesIO(data)) as w:
        require((w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2, 2, 48000, 576000), 'session WAV shape')
        return [x[0] for x in struct.iter_unpack('<h', w.readframes(w.getnframes()))]


def assemble(paths, host, out):
    host_bytes = host.read_bytes()
    require(digest(host_bytes) == HOST_SHA, 'host artifact digest')
    files = archive(host_bytes)
    session = json.loads(files['session/session.json'])
    require(session['complete'] and len(session['cases']) == 14, 'session receipt')
    require(all(c['restore_error'] == 0 and c.get('partition_error', 0) == 0 for c in session['cases']), 'session state/partition')
    stems = [wav(files['session/Stems/' + n + '.wav']) for n in ('Afterimage', 'Winter-Latch', 'Winter-Pause', 'Winter-Snapshot')]
    dry = wav(files['session/Comparisons/Dry.wav'])
    error = max(abs(sum(s) - d) for s, d in zip(zip(*stems), dry))
    require(error <= 1, 'stem alignment')
    for n in ('Balanced', 'Legacy'):
        require(wav(files['session/Comparisons/' + n + '.wav']) != dry, 'wet contrast')
    delivery = {'Session/' + n[len('session/'):]: b for n, b in files.items() if n.startswith('session/')}
    manifest = {'host_artifact': 15194909235, 'host_sha256': HOST_SHA, 'stem_sum_lsb_error': error, 'plugins': {}}
    class_ids = set()
    for k, name in NAMES.items():
        meta = TRACE if k == 'trace' else session[k]
        raw = paths[k].read_bytes()
        require(digest(raw) == meta['outer_sha256'], k + ' outer digest')
        outer = archive(raw)
        require(len(outer) == 1, k + ' outer layout')
        inner = next(iter(outer.values()))
        require(digest(inner) == meta['inner_sha256'], k + ' inner digest')
        entries = archive(inner)
        binary = entries[f'{name}.vst3/Contents/x86_64-win/{name}.vst3']
        pe = struct.unpack_from('<I', binary, 60)[0]
        require(binary[:2] == b'MZ' and binary[pe:pe+6] == b'PE\0\0\x64\x86', k + ' AMD64')
        require(digest(binary) == meta['binary_sha256'], k + ' binary digest')
        source = dict(x.split('=', 1) for x in entries['BUILD-SOURCE.txt'].decode().splitlines())
        require(source == {'source': meta['source'], 'sdk': SDK}, k + ' source pin')
        info = entries[f'{name}.vst3/Contents/Resources/moduleinfo.json'].decode()
        ids = re.findall(r'"CID"\s*:\s*"([0-9A-Fa-f]{32})"', info)
        require(len(ids) == 2 and len(set(ids)) == 2 and not class_ids.intersection(ids) and meta.get('cid', meta.get('processor_cid')) in ids, k + ' class IDs')
        class_ids.update(ids)
        require('VST 3.8.0' in info, k + ' SDK version')
        for n, b in entries.items():
            target = ('VST3/' if n.startswith(name + '.vst3/') else 'Evidence/' + name + '/') + n
            if k == 'trace' and n.startswith(('Presets/', 'PresetAuditions/')):
                target = 'TraceBell/' + n
            delivery[target] = b
        manifest['plugins'][k] = dict(meta, artifact_id=IDS[k], name=name)
    delivery['MANIFEST.json'] = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    delivery['README.txt'] = ("MHAC Windows x64 owner audition — Draft/HOLD\n"
        "Copy complete VST3/*.vst3 directories into your DAW's VST3 scan path; rescan.\n"
        "Avoid duplicate copies of earlier versions with the same class IDs. Use a disposable session.\n"
        "Session: 48 kHz, 12 seconds. Import four Stems at the same zero start, unity gains.\n"
        "Their sum matches Comparisons/Dry.wav within one PCM16 LSB. Solo each comparison.\n"
        "For live reconstruction, import four MIDI tracks at zero, use Afterimage on its track\n"
        "and Three Winters on the other three, loading the matching Session/Presets. Route all\n"
        "to a stereo group with gains 0.5/0.125/0.125/0.125 respectively; insert Receipt Fold\n"
        "and compare Balanced, Legacy, Bypass. Stems already include gains; do not apply twice.\n"
        "Trace Bell is a separately qualified optional group effect, not part of those reference mixes.\n"
        "TraceBell contains eight presets and audition WAVs; start at low monitoring levels.\n"
        "Original per-plugin documentation, licences and qualification evidence are preserved.\n"
        "No combined DAW scan, listening judgement, owner approval or research adoption is claimed.\n").encode()
    delivery['SHA256SUMS.txt'] = ''.join(f'{digest(b)}  {n}\n' for n,b in sorted(delivery.items())).encode()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for n,b in sorted(delivery.items()):
            item = zipfile.ZipInfo(n, (2026,11,27,0,0,0))
            item.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(item,b)
    require(archive(out.read_bytes()) == delivery, 'delivery readback')
    print(f'PASS {len(delivery)} files; 4 AMD64 plugins; 8 unique class IDs; stem error {error} LSB; SHA256 {digest(out.read_bytes())}')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for k in (*NAMES, 'host', 'out'):
        p.add_argument('--' + k, required=True, type=Path)
    a = p.parse_args()
    assemble({k: getattr(a,k) for k in NAMES}, a.host, a.out)
