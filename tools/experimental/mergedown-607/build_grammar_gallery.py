"""Refs #607: offline gallery for the frozen Grammar batch; synthetic PCM only."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import struct
import wave

PIN = '9e45f77a11c637c03f7e1ac50b6b6802ffc97cfc'
PINS = {
    'prefix-disjoint.py': 'f9dd2ae4d62c91584c9c3beeac6fe25daf2d6942',
    'frame-length-commit.py': '1538e258e53b62fc62315ca11eb9ba34496c5919',
    'version-bound-payload.py': '7ef6881cefa9c34355d024aeea671d021b674a55',
    'version-bridge.py': '6400cf4c1b42fbe958b0265da43ef657bb355401',
    'control-namespace.py': '8e27fe89f2734a0b5fd666bb2018b0d379736493',
    'migration-namespace.py': 'b3562781a974c47b41cbe066ceb755288a51b6b1',
    'distributed-profile.py': 'a780404e8c76820976ad6fb407429ec895a6313f',
}
GROUPS = {'prefix1': 'Interrupted frames', 'bridge-reproduced': 'Version bridge',
          'bound-reproduced': 'Version-bound payload'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect(root):
    for name, pin in PINS.items():
        p = root / name
        require(p.is_file() and not p.is_symlink(), 'source path ' + name)
        b = p.read_bytes()
        require(hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest() == pin, 'source pin ' + name)
    specimens = []
    count = 0
    for group in GROUPS:
        folder = root / group
        require(folder.is_dir() and not folder.is_symlink(), 'group path ' + group)
        require(all(p.is_file() and not p.is_symlink() for p in folder.iterdir()), 'unexpected group entry ' + group)
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        require(set(manifest) == {p.name for p in folder.iterdir()} - {'manifest.json'}, 'inventory ' + group)
        for name, expected in sorted(manifest.items()):
            p = folder / name
            require(digest(p.read_bytes()) == expected, 'artifact hash ' + group + '/' + name)
            count += 1
            if p.suffix != '.wav':
                continue
            with wave.open(str(p), 'rb') as w:
                require((w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getcomptype()) == (1, 2, 16000, 'NONE'), 'PCM format ' + name)
                n = w.getnframes()
                require(0 < n <= 32000, 'duration ' + name)
                raw = w.readframes(n)
            require(len(raw) == 2*n, 'PCM length ' + name)
            samples = struct.unpack(f'<{n}h', raw)
            peak = max(map(abs, samples))
            require(peak <= 2048, 'peak bound ' + name)
            specimens.append({'path': group + '/' + name, 'samples': n, 'peakPCM16': peak,
                              'rmsPCM16': round(math.sqrt(sum(s*s for s in samples)/n), 6),
                              'pcmSHA256': digest(raw)})
    require(len(specimens) == 24 and all(sum(x['path'].startswith(g+'/') for x in specimens) == 8 for g in GROUPS), 'specimen coverage')
    lookup = {x['path']: x for x in specimens}
    a = lookup['bound-reproduced/marker-erased.wav']
    b = lookup['bound-reproduced/polynomial-erased.wav']
    require(a['pcmSHA256'] == b['pcmSHA256'], 'erased alias witness differs')
    return {'schema': 'mhac-grammar-gallery-1', 'sourceRef': PIN, 'sourceBlobs': PINS,
            'manifestEntries': count, 'specimens': specimens, 'erasedAliasPCMEqual': True,
            'scope': 'Frozen synthetic artifacts; digital PCM, not loudness, listening or human evidence.'}


def render(report):
    rows = []
    for group, title in GROUPS.items():
        rows.append(f'<h2>{html.escape(title)}</h2><p><a href="{group}/index.html">Original gallery and receipt</a></p><table><tr><th>Specimen</th><th>Duration (s)</th><th>RMS (PCM16)</th></tr>')
        for s in report['specimens']:
            if not s['path'].startswith(group+'/'):
                continue
            path = html.escape(s['path'], quote=True)
            name = html.escape(Path(s['path']).name)
            rows.append(f'<tr><td><button type="button" data-src="{path}">{name}</button></td><td>{s["samples"]/16000:.2f}</td><td>{s["rmsPCM16"]:.2f}</td></tr>')
        rows.append('</table>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MHAC Grammar laboratory</title><style>body{max-width:850px;margin:2rem auto;padding:0 1rem;font:16px system-ui;color:#172534;background:#fafafa}header{border-bottom:1px solid #abb6c1}section{position:sticky;top:0;background:#fff;padding:1rem;border:1px solid #abb6c1}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:.45rem;border-bottom:1px solid #ddd}button{font:inherit;text-align:left;cursor:pointer}audio{width:100%}</style><header><h1>MHAC Grammar laboratory</h1><p>Frozen synthetic experiments. Select a specimen, then press Play. Start at low hardware volume. Gain is digital, not SPL or matched loudness.</p><p>Erased marker and polynomial examples contain identical PCM despite incompatible contextual interpretations. <a href="grammar-gallery.json">Measurement receipt</a></p></header><section><label>Selected: <strong id="selection">None</strong></label><audio id="player" controls preload="none"></audio><label>Digital gain: <input id="gain" type="range" min="0" max="0.2" step="0.01" value="0.2"> <output id="level">20%</output></label></section>''' + ''.join(rows) + '''<script>const player=document.querySelector('#player'),gain=document.querySelector('#gain');function setGain(){player.volume=Number(gain.value);document.querySelector('#level').textContent=Math.round(player.volume*100)+'%'}setGain();gain.addEventListener('input',setGain);document.querySelectorAll('button[data-src]').forEach(b=>b.addEventListener('click',()=>{player.pause();player.src=b.dataset.src;document.querySelector('#selection').textContent=b.textContent;setGain()}));</script></html>\n'''


def build(root):
    report = inspect(root)
    paths = [root/'index.html', root/'grammar-gallery.json']
    require(not any(p.exists() or p.is_symlink() for p in paths), 'output already exists')
    paths[0].write_bytes(render(report).encode('utf-8'))
    paths[1].write_bytes((json.dumps(report, indent=2, sort_keys=True)+'\n').encode('utf-8'))
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    args = p.parse_args()
    print(json.dumps(build(args.root), indent=2, sort_keys=True))
