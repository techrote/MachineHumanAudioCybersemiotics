"""Offline audit for the first Orbit Lantern 0.1.0 Windows delivery (Refs #738).
Not a host test. Supply independently obtained GitHub artifact digest and source SHA.
"""
import argparse
import hashlib
import io
import json
import re
import struct
import wave
import zipfile

ROOT = '9fad9770f2ae8542ab1a548a68c1ad1ac690abe0'
PINS = dict(base='3d2e82f8e6bff59c1d8b7a27491a29c2286b5206',
            cmake='de6e54eeaaab35b7145f5c32c279b5e892146e04',
            doc='6d4737c9e70750056e731d88d49aa06eefc8a1a4',
            pluginterfaces='31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c',
            tutorials='33b73dfbb87f3fde3bce8c0a10cae934dc66ad34',
            vstgui4='76823bdbe286e4bdb9f79ab8986af5ce7202336c')
PINS['public.sdk'] = 'a3911a4615dabbfdfd9d181ee26b05c70c289a95'
CID = '24C15B793B8C4F4B98275F233EE969C4'
CONTROLLER = 'A501C96DF0EC48C88BA63D11B860D74F'
BUNDLE = 'MHACOrbitLantern.vst3'
BINARY = BUNDLE + '/Contents/x86_64-win/' + BUNDLE


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [n for n in z.namelist() if not n.endswith('/')]
        require(len(set(n.casefold() for n in names)) == len(names), 'duplicate paths')
        require(all(not n.startswith('/') and '\\' not in n and ':' not in n and
                    all(p not in ('', '.', '..') for p in n.split('/')) for n in names), 'unsafe path')
        require(z.testzip() is None, 'ZIP CRC')
        return {n: z.read(n) for n in names}


def audit(outer, expected_digest, source, native):
    require(digest(outer) == expected_digest.lower(), 'artifact SHA256')
    wrapper = archive(outer)
    require(set(wrapper) == {'MHACOrbitLantern-Windows-x64.zip'}, 'outer layout')
    inner = wrapper['MHACOrbitLantern-Windows-x64.zip']
    f = archive(inner)
    require(dict(line.split('=', 1) for line in f['BUILD-SOURCE.txt'].decode('utf-8-sig').splitlines()) ==
            {'sdk': ROOT, 'source': source}, 'source/SDK receipt')
    links = {}
    for line in f['SDK-GITLINKS.txt'].decode('utf-8-sig').splitlines():
        m = re.fullmatch(r' ([0-9a-f]{40}) (\S+)(?: \(.*\))?', line)
        require(m is not None and m[2] not in links, 'dirty or duplicate gitlink')
        links[m[2]] = m[1]
    require(links == PINS, 'recursive gitlink pins')
    log = f['validator.txt'].decode('utf-8-sig')
    require('Result: 47 tests passed, 0 tests failed' in log and not re.search(r'ERROR:', log, re.I), 'validator gate')
    for rate in ('1234.5678', '1234567.8'):
        require(log.count(rate + ' Hz - processed successfully!') == 2, 'fractional-rate witness ' + rate)
    meta = json.loads(re.sub(r',\s*([}\]])', r'\1', f[BUNDLE + '/Contents/Resources/moduleinfo.json'].decode()))
    classes = meta['Classes']
    require(meta['Version'] == '0.1.0' and len(classes) == 2 and
            [(c['CID'], c['Category']) for c in classes] == [(CID, 'Audio Module Class'), (CONTROLLER, 'Component Controller Class')] and
            all(c['SDKVersion'] == 'VST 3.8.0' and c['Version'] == '0.1.0' for c in classes), 'factory metadata')
    b = f[BINARY]
    offset = struct.unpack_from('<I', b, 60)[0]
    require(b[:2] == b'MZ' and b[offset:offset+6] == b'PE\0\0\x64\x86' and
            struct.unpack_from('<H', b, offset+24)[0] == 0x20b and
            struct.unpack_from('<H', b, offset+22)[0] & 0x2000, 'AMD64 PE32+ DLL')
    for n in ('Steinberg-SDK-LICENSE.txt', 'SDK-base-LICENSE.txt', 'SDK-cmake-LICENSE.txt',
              'SDK-pluginterfaces-LICENSE.txt', 'SDK-public.sdk-LICENSE.txt', BUNDLE + '/Contents/Resources/LICENSE.txt'):
        require(bool(f[n].strip()), 'missing notice ' + n)
    presets = sorted(n for n in f if n.startswith('Presets/'))
    audio = sorted(n for n in f if n.startswith('Audio/'))
    require(len(presets) == len(audio) == 8 and
            {n[8:-10] for n in presets} == {n[6:-4] for n in audio}, 'preset/audio pairing')
    for n in presets:
        p = f[n]
        require(len(p) == 86 and p[:4] == b'VST3' and p[8:40] == CID.encode() and
                struct.unpack_from('<IQ', p, 4)[0] == 1 and struct.unpack_from('<Q', p, 40)[0] == 58 and
                p[48:52] == b'OL01' and p[58:66] == b'List\x01\0\0\0' and p[66:70] == b'Comp' and
                struct.unpack_from('<QQ', p, 70) == (48, 10), 'preset layout ' + n)
        blend, release, cents = struct.unpack_from('<HHH', p, 52)
        require(blend <= 1000 and 10 <= release <= 1000 and cents <= 200, 'patch range')
    for n in audio:
        with wave.open(io.BytesIO(f[n]), 'rb') as w:
            require((w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) ==
                    (2, 2, 48000, 144000), 'WAV format ' + n)
            pcm = w.readframes(w.getnframes())
            require(len(pcm) == 576000 and pcm[-9600:] == bytes(9600) and
                    0 < max(abs(v[0]) for v in struct.iter_unpack('<h', pcm)) <= 17040, 'WAV bounds/silence ' + n)
    require(all(f[n] == native[n] for n in presets + audio), 'native/Windows content mismatch')
    return dict(source=source, sdk=ROOT, outer_sha256=digest(outer), inner_sha256=digest(inner),
                binary_sha256=digest(b), class_ids=[CID, CONTROLLER], validator='47 passed, 0 failed',
                files=len(f), presets=len(presets), audio=len(audio), native_exact=16)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('artifact'); p.add_argument('digest'); p.add_argument('source'); p.add_argument('native')
    a = p.parse_args()
    with open(a.artifact, 'rb') as f, open(a.native, 'rb') as n:
        print(json.dumps(audit(f.read(), a.digest, a.source, archive(n.read())), indent=2))


if __name__ == '__main__':
    main()
