"""Build and run the pinned DSP chain without vendoring the foundry headers."""
import argparse
import hashlib
import pathlib
import subprocess
import tempfile

PINS = {
    'engine.hpp': ('eb78ea3b7a08a646910e66235724f259aeeb8190',
                   'tools/experimental/instrument-foundry/golden-receipt/engine.hpp',
                   '482ffd924042f201c513a5e68c1b3e6a95c54999'),
    'freeze.hpp': ('fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2',
                   'tools/experimental/signal-foundry/freeze-socket/freeze.hpp',
                   '510fb2ab09690754c21f3c6bea0d3e9c48fd72d6'),
}


def git_blob(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=pathlib.Path, default=pathlib.Path.cwd())
    p.add_argument('--headers', type=pathlib.Path, help='locally recovered exact upstream files')
    p.add_argument('--cxx', default='g++', help='GCC/Clang-compatible C++ compiler')
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--out', type=pathlib.Path, required=True, help='new or empty output directory')
    args = p.parse_args()
    if args.out.exists() and (not args.out.is_dir() or any(args.out.iterdir())):
        p.error('--out must be a new or empty directory')
    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mhac-chain-') as tmp:
        work = pathlib.Path(tmp)
        for name, (commit, path, expected) in PINS.items():
            data = (args.headers / name).read_bytes() if args.headers else subprocess.check_output(
                ['git', '-C', str(args.repo), 'show', f'{commit}:{path}'])
            if git_blob(data) != expected:
                raise ValueError(f'upstream blob mismatch: {name}')
            (work / name).write_bytes(data)
        source = work / 'chain.cpp'
        source.write_bytes(pathlib.Path(__file__).with_name('chain.cpp').read_bytes())
        exe = work / 'chain.exe'
        flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if args.sanitize else ['-O2']
        subprocess.run([args.cxx, '-std=c++17', '-Wall', '-Wextra', '-Werror', *flags,
                        '-I', str(work), str(source),
                        '-o', str(exe)], check=True)
        subprocess.run([str(exe), str(args.out.resolve())], check=True)
    for path in sorted(args.out.glob('*.wav')):
        print(hashlib.sha256(path.read_bytes()).hexdigest(), path.name)


if __name__ == '__main__':
    main()
