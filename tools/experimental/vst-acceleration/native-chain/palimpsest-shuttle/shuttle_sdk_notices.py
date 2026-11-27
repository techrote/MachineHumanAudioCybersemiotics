"""Copy only SDK provenance into Shuttle staging, never another plugin's logs."""
import argparse
from pathlib import Path
import re

PARTS = ('base', 'cmake', 'doc', 'pluginterfaces', 'public.sdk', 'tutorials', 'vstgui4')
REQUIRED = {'SDK-GITLINKS.txt', 'Steinberg-SDK-LICENSE.txt', 'BUILD-SOURCE.txt'}
NOTICE = re.compile(r'SDK-(?:' + '|'.join(map(re.escape, PARTS)) +
                    r')-(?i:LICENSE|NOTICE|COPYING)(?:[.-][^/\\]+)?')


def copy_notices(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('source and destination must differ')
    selected = sorted(p for p in source.iterdir()
                      if p.name in REQUIRED or NOTICE.fullmatch(p.name))
    if not REQUIRED <= {p.name for p in selected}:
        raise ValueError('missing required SDK provenance')
    occupied = {p.name.casefold() for p in destination.iterdir()}
    for p in selected:
        if p.is_symlink() or not p.is_file() or p.stat().st_size == 0:
            raise ValueError('invalid SDK provenance: ' + p.name)
        if p.name.casefold() in occupied:
            raise ValueError('SDK provenance collision: ' + p.name)
        occupied.add(p.name.casefold())
    for p in selected:
        with (destination / p.name).open('xb') as out:
            out.write(p.read_bytes())
    return len(selected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(f'SHUTTLE_SDK_NOTICES_PASS files={copy_notices(args.source, args.destination)}')
