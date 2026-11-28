"""Refs #607: assemble frozen Grammar batch without modifying upstream sources."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from build_grammar_gallery import PIN, PINS, build, require

JOBS = {'prefix-disjoint.py': 'prefix1', 'version-bridge.py': 'bridge-reproduced',
        'version-bound-payload.py': 'bound-reproduced'}
# Canonical JSON hashes include original PCM hashes. Native text line endings
# are allowed; semantic changes, including different PCM, fail closed.
RECEIPTS = {
    'prefix1': 'ce193c701dfe7e29f22135f43f5192cd8b58b14c0a0c2517911cc96b26853856',
    'bridge-reproduced': '580d4944533e74fc6d859ed54fb6568e7da26afaaba8ae22dba1246ef5cba79c',
    'bound-reproduced': 'f0127ec8be4190e6a95f1458def1975d3ade15463f8cb11c03c539bc30d4512b',
}
TRACE = 'b2930057574bba65fb9d8e9f9d0f020a9ed6ec5d0bdbd09075ee683f3d6ddfbb'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def check_frozen(root):
    for group, expected in RECEIPTS.items():
        receipt = json.loads((root/group/'receipt.json').read_text(encoding='utf-8'))
        require(sha(canonical(receipt)) == expected, 'frozen receipt ' + group)
    require(sha((root/'prefix1/traces.jsonl').read_text(encoding='utf-8').encode('utf-8')) == TRACE, 'frozen trace')


def run(source, target):
    require(not target.exists() and not target.is_symlink(), 'target exists')
    target = target.absolute()
    require(target.parent.is_dir(), 'target parent missing')
    here = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=target.parent, prefix='.grammar-') as td:
        root = Path(td)/'package'
        root.mkdir()
        for name, pin in PINS.items():
            b = (source/name).read_bytes()
            require(hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest() == pin, 'source pin ' + name)
            (root/name).write_bytes(b)
        for name in ('check_prefix_disjoint.py', 'check_version_bound.py', 'build_grammar_gallery.py', 'build_grammar_release.py'):
            shutil.copyfile(here/name, root/name)
        for name, group in JOBS.items():
            subprocess.run([sys.executable, '-B', str(root/name), str(root), str(root/group)], check=True)
        check_frozen(root)
        report = build(root)
        commands = [('check_prefix_disjoint.py', 'prefix-audit.json', [str(root/'prefix1')]),
                    ('check_version_bound.py', 'version-audit.json', [str(root/'bridge-reproduced/receipt.json'), str(root/'bound-reproduced/receipt.json')])]
        for name, output, args in commands:
            receipt = subprocess.check_output([sys.executable, '-B', str(root/name), str(root), *args])
            json.loads(receipt)
            (root/output).write_bytes(receipt)
        (root/'README.txt').write_bytes((f'MHAC #607 frozen Grammar snapshot {PIN}\nOpen index.html offline. Start at low hardware volume; no autoplay.\nOriginal synthetic PCM, not human evidence. Source bytes preserved; no new license.\nPython and NumPy needed only for regeneration. Independent audits included.\n').encode('utf-8'))
        manifest = {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}
        (root/'release-manifest.json').write_bytes((json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode('utf-8'))
        require(not target.exists(), 'target appeared during build')
        root.rename(target)
        return {'sourceRef': PIN, 'files': len(manifest)+1, 'gallery': len(report['specimens']), 'frozenReceipts': len(RECEIPTS), 'frozenTrace': True, 'manifestSHA256': sha((target/'release-manifest.json').read_bytes())}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('target', type=Path)
    args = p.parse_args()
    print(json.dumps(run(args.source, args.target), indent=2))
