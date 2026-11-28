"""Exercise audit against actual receipt, then repacked corrupted fixtures."""
import io, sys, zipfile
from pathlib import Path
from audit_orbit_delivery import audit, archive, digest, BINARY, BUNDLE

outer = Path(sys.argv[1]).read_bytes()
native = archive(Path(sys.argv[2]).read_bytes())
source = 'e548c3166723b76cee25f30fbc93b7dd82b47b26'
assert audit(outer, digest(outer), source, native)['native_exact'] == 16
wrapper = archive(outer)
name = next(iter(wrapper))
files = archive(wrapper[name])


def pack(items):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in items.items():
            z.writestr(k, v)
    return out.getvalue()


preset = next(n for n in files if n.startswith('Presets/'))
audio = next(n for n in files if n.startswith('Audio/'))
cases = [('BUILD-SOURCE.txt', b'wrong', 'source/SDK receipt'),
         ('SDK-GITLINKS.txt', b'+' + files['SDK-GITLINKS.txt'][1:], 'dirty or duplicate gitlink'),
         ('validator.txt', files['validator.txt'] + b'\nERROR: injected', 'validator gate'),
         ('validator.txt', files['validator.txt'].replace(b'1234.5678', b'1234.0000'), 'fractional-rate witness'),
         (BINARY, b'XX' + files[BINARY][2:], 'AMD64 PE32+ DLL'),
         (BUNDLE + '/Contents/Resources/LICENSE.txt', b'', 'missing notice'),
         (preset, b'XXXX' + files[preset][4:], 'preset layout'),
         (audio, files[audio][:-2] + b'\x01\x00', 'WAV bounds/silence'),
         (preset, files[preset][:52] + b'\xff\xff' + files[preset][54:], 'patch range'),
         (preset, files[preset][:52] + b'\x01\x00' + files[preset][54:], 'native/Windows content mismatch'),
         ('../escape', b'unsafe', 'unsafe path'),
         (preset.upper(), files[preset], 'duplicate paths')]
# Incorrect source receipt uses a well-formed receipt with a different source.
cases[0] = ('BUILD-SOURCE.txt', files['BUILD-SOURCE.txt'].replace(source.encode(), b'0'*40), 'source/SDK receipt')
for key, value, expected in cases:
    mutant = pack({name: pack(dict(files, **{key: value}))})
    try:
        audit(mutant, digest(mutant), source, native)
    except ValueError as e:
        assert expected in str(e), (key, expected, e)
    else:
        raise AssertionError(key)
try:
    audit(outer, '0'*64, source, native)
except ValueError as e:
    assert 'artifact SHA256' in str(e)
else:
    raise AssertionError('digest')
print(f'PASS: actual artifact and {len(cases)+1} negative controls')
