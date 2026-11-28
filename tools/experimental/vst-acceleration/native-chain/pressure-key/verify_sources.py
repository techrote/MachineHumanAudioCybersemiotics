"""Verify pinned upstream native Git blobs without a network connection."""
import hashlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
lock = pathlib.Path(__file__).with_name('DEPENDENCIES.txt')
count = 0
for row in lock.read_text(encoding='utf-8').splitlines():
    if not row or row.startswith('#'):
        continue
    name, expected = row.split()
    data = (root / name).read_bytes()
    actual = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    if actual != expected:
        sys.exit(f'{name}: expected {expected}, got {actual}')
    count += 1
if count != 14:
    sys.exit('Unexpected dependency count')
print(f'PRESSURE_KEY_SOURCE_PASS headers={count}')
