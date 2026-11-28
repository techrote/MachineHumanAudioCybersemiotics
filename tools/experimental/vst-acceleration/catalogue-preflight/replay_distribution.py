#!/usr/bin/env python3
"""Rebuild five frozen MHAC owner distributions from original Actions ZIPs.

No network, host loading, installation or modification of input archives.
Run from a clean output path with Python 3.13.5 for byte-identical output.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import zlib

SOURCES = {
    'assemble.py': '6ed1e382e91d2b4af575c1de6b632fd46de2c565f3c7d2f4da472d6563a17872',
    'extend.py': '3d12f0b1973f6ecfa657a59880801f6ab3473fb4f82229455cc0a77f110885be',
    'refresh.py': '55c24b05144c8fe238f5a0b254e107aa3eb98191ea8ddae497f0ccbcd25a8523',
    'refresh_signal.py': 'bac2d06616dab939d933600d6114a191d44b4e4c57d7ba6f4e86fc5e13021377',
    'refresh_shuttle.py': '7f2a1cba947f371fde0af7f92903e36579896dba5fcffadf78d32458aece82a2',
}
# Aliases are the original assembly scripts' input filenames, not new artifacts.
INPUTS = {
    15210786073: ('orbit.zip', '7773d5aa091ebc34087563d8812f3048f97e6f0b3ca989dcf51f1d4525df60b1'),
    15207530972: ('counterfactual.zip', '0469c67bea5be1ad3d03ce0dbae866d886c82143f0e82cdbfc22011b0f3b38b6'),
    15207451185: ('harmonic.zip', '56bd85930d4df21462c22d5ab4348fd9a67af459a1032e0179e9dd9d7002f3c6'),
    15195705883: ('tracebell.zip', 'fa74dd77708ab33537b0f69037ecc92f8236297ffc3f09580860d71fe82595c9'),
    15213334539: ('tracebell-15213334539.zip', '438bd442336a041e873f7044cdd768549764c5613a807281aa7ab81a013a5dff'),
    15213579147: ('shuttle-15213579147.zip', '078c4060ea83e14fd8a067df269cc9034bd301de0bd5989a83956ccce0561b3a'),
    15213519440: ('host-15213519440.zip', '693419854d3d7141234f95a64e2d98f1feb050ec276ccdd187f47b64bfe84e7e'),
    15194909235: (None, 'e9300c376c22bc937899d2eed1e5045cf3be8b922c0c08cd88d202d69bc2c6d9'),
    15148180211: (None, 'ff3ee494ff663515347000342c5ac9eeccbd7754b595d0d35fa2c64fb9273502'),
    15156181930: (None, 'f47449a0a9bbf626cbdebb0acd68713acc01e4130815697ee4ab92f14581c8b9'),
    15145497011: (None, '74ff70c9c5704fe13a1a0ee88ceaada4cc3e7076fa14e9e6d57e1da6ffabca94'),
    15222539017: (None, 'f6039ee0bcf9cd6952611387479dd96b42a64feb8f3fb249b313f6a01085a4e4'),
    15228973006: (None, '33fd869fb32c620008e0a23d49710489fbb0e10970b8325a75c5fca75a8efe86'),
    15228688642: (None, 'b821fdd41052afc8c47674195fe644eb392cf722fbbd2acc2adc6550ca38690c'),
    15233734011: (None, '2bdd984ca696964779bf3228e09b6e80502a51c14c7d321777ae11874f5fa017'),
    15233868488: (None, '8cbd5e26692aae3b19784ab58794f920c16c1d68b89bdbaeca6fce10567ede50'),
}
STAGES = [
    ('assemble.py', 'MHAC-VST-catalogue-increment-20261127.zip', 'd58faf344111f0eb3882aa47f58e2e28baac84517f74e65b2f5e8df68c86ae29'),
    ('extend.py', 'MHAC-VST-five-plugin-owner-review.zip', 'b0cc07827ad5efea7796254314038d0cabf855e249bb424c4240d5e0f03a45fe'),
    ('refresh.py', 'MHAC-VST-eight-plugin-owner-review.zip', '5592de05b6e2e46c00a9b2a247e2e8c5c64b4e5a23286fb1be72ee241a0c9bc1'),
    ('refresh_signal.py', 'MHAC-VST-eight-plugin-signal-refresh.zip', '7800d5084eca08d5939ec7348faa5d9c57f0c828df92787d7cccabffe3842106'),
    ('refresh_shuttle.py', 'MHAC-VST-eight-plugin-shuttle-refresh.zip', 'bc7aba293dfdd2c7840b50a8cc2bef085cfd94be7fa97c770a4a564ecb05db8c'),
]


def verify(path, expected):
    with path.open('rb') as stream:
        got = hashlib.file_digest(stream, 'sha256').hexdigest()
    if got != expected:
        raise ValueError(f'digest mismatch: {path.name}: {got}')
    return got


def replay(inputs, output):
    root = pathlib.Path(__file__).resolve().parent
    inputs, output = inputs.resolve(), output.absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    for name, digest in SOURCES.items():
        verify(root / name, digest)
    for artifact, (_, digest) in INPUTS.items():
        verify(inputs / f'github-actions-artifact-{artifact}.zip', digest)
    output.mkdir(parents=False, exist_ok=False)
    for artifact, (alias, digest) in INPUTS.items():
        name = f'github-actions-artifact-{artifact}.zip'
        target = output / (alias or name)
        shutil.copyfile(inputs / name, target)
        verify(target, digest)
    stages = []
    for script, name, digest in STAGES:
        target = output / name
        result = subprocess.run([sys.executable, '-I', '-B', '-c',
            'import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); '
            'sys.argv.pop(0); runpy.run_path(sys.argv[0],run_name="__main__")',
            str(root), str(root / script), str(output), str(target)],
            check=True, capture_output=True, text=True)
        verify(target, digest)
        stages.append({'script': script, 'archive': name, 'sha256': digest,
                       'assembly_stdout': result.stdout})
    report = {'scope': 'native offline archive reconstruction; no new VST host execution',
              'python': sys.version.split()[0], 'zlib': zlib.ZLIB_RUNTIME_VERSION,
              'input_count': len(INPUTS), 'source_count': len(SOURCES), 'stages': stages}
    (output / 'replay-receipt.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: python replay_distribution.py INPUT_DIRECTORY NEW_OUTPUT_DIRECTORY')
    print(json.dumps(replay(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])), indent=2))
