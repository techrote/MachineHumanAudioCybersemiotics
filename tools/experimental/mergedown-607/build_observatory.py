"""Refs #607/#443: assemble a bounded frozen Observatory package, no network."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import wave

REF = '5a1e3a857389ce8f6763c66847c9522179dcbf59'
PINS = {
    'core.js': '47938c769604ae56a1f8cb92e5d4ccc3e20f8d59',
    'index.html': '5ee12f884479425acf8d3137a1974ff6df9c8cb4',
    'phase.html': 'c8f8631a9e76318a271d811e471af75e5c372acf',
    'legacy-workbench.cjs': '71766ee6194f36f16aca6459fcf64966105844ce',
    'selective-transfer.cjs': 'ea1b41bda016082a4ff4754beb8da9b062a2736d',
    'phase-fit.cjs': 'fd0fbca5bc784fadb9227baa628fb290506b841c',
    'matched-fp.cjs': 'e2c5e29240844a643ba966e5a261909d39f07862',
}
JOBS = {'legacy': 'legacy-workbench.cjs', 'selective': 'selective-transfer.cjs'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'Symlink not permitted: {p}')
        if p.is_file():
            result[p.relative_to(root).as_posix()] = sha(p.read_bytes())
    return result


def verify_export(root, script, source, pins):
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    actual = inventory(root)
    del actual['manifest.json']
    if actual != manifest['files']:
        raise ValueError(f'Export inventory/hash mismatch: {root.name}')
    if manifest['sourceSHA256'] != sha((source / script).read_bytes()):
        raise ValueError(f'Export source mismatch: {script}')
    if not manifest['pins'] or any(pins.get(k) != v for k, v in manifest['pins'].items()):
        raise ValueError(f'Export dependency mismatch: {script}')
    if not {'index.html', 'receipt.json'} <= actual.keys():
        raise ValueError(f'Missing required output: {root.name}')
    audio = {}
    for name in actual:
        if name.endswith('.wav'):
            with wave.open(str(root / name), 'rb') as w:
                if w.getsampwidth() != 2 or w.getnchannels() != 1:
                    raise ValueError(f'Unexpected WAV format: {name}')
                frames = w.getnframes()
                pcm = w.readframes(frames)
                if len(pcm) != frames * 2 or not frames:
                    raise ValueError(f'Incomplete WAV: {name}')
                peak = max(abs(int.from_bytes(pcm[i:i+2], 'little', signed=True))
                           for i in range(0, len(pcm), 2))
                audio[name] = {'rateHz': w.getframerate(), 'frames': frames,
                               'peakPCM16': peak, 'peakFractionFS': peak / 32768}
    return audio


def build(snapshot, output, node='node', *, pins=None, jobs=None):
    pins = PINS if pins is None else pins
    jobs = JOBS if jobs is None else jobs
    snapshot, output = Path(snapshot).resolve(), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    raw = {}
    for name, expected in pins.items():
        raw[name] = (snapshot / name).read_bytes()
        if blob(raw[name]) != expected:
            raise ValueError(f'Frozen source mismatch: {name}; use byte-preserving checkout')
    version = subprocess.check_output([node, '--version'], text=True).strip()
    with tempfile.TemporaryDirectory(prefix='.observatory-', dir=output.parent) as temp:
        stage = Path(temp) / 'package'
        source = stage / 'source'
        source.mkdir(parents=True)
        for name, data in raw.items():
            (source / name).write_bytes(data)
        audio = {}
        for name, script in jobs.items():
            dest = stage / name
            subprocess.run([node, str(source / script), str(dest)], check=True,
                           cwd=source, timeout=600, stdout=subprocess.DEVNULL)
            audio[name] = verify_export(dest, script, source, pins)
        if inventory(source) != {k: sha(v) for k, v in raw.items()}:
            raise ValueError('Source changed during native execution')
        links = ''.join(f'<li><a href="{name}/index.html">{name}</a></li>' for name in jobs)
        (stage / 'index.html').write_text(
            '<!doctype html><meta charset="utf-8"><title>MHAC Observatory</title>'
            '<h1>MHAC Observatory — frozen experimental package</h1>'
            '<p>Synthetic only. Playback opt-in; start at low hardware volume. '
            'Digital peaks are not calibrated SPL. Comparisons do not establish human perception.</p>'
            '<ul><li><a href="source/index.html">Affine inspector</a></li>'
            '<li><a href="source/phase.html">Sampling phase inspector</a></li>' + links +
            '<li><a href="package-manifest.json">Package manifest</a></li></ul>', encoding='utf-8')
        manifest = {'schema': 'mhac-607-observatory-package-v1', 'frozenRef': REF,
                    'sourcePins': pins, 'nodeVersion': version, 'audio': audio,
                    'files': inventory(stage)}
        (stage / 'package-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        if output.exists() or output.is_symlink():
            raise FileExistsError(output)
        stage.rename(output)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new directory with existing parent')
    parser.add_argument('--node', default='node')
    args = parser.parse_args()
    result = build(Path(__file__).resolve().parent / 'affine-snapshot', args.output, args.node)
    print(json.dumps({'status': 'PASS', 'files': len(result['files']), 'audio': result['audio']}, indent=2))
