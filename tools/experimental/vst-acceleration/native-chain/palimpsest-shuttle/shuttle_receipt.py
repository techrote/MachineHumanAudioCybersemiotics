"""Fail-closed Palimpsest Shuttle SDK replay receipt gate (no SDK required)."""
import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import zipfile

RATES = ('44100', '48000', '96000', '384000', '1234.568', '12345.678',
         '123456.780', '1234567.800')
EXPECTED = [(Decimal(r), b, n) for r, n in zip(RATES,
            (20000, 20000, 20000, 92160, 20000, 20000, 20000, 296298))
            for b in (127, 1024)]
EXT = 'SDK_EXTENDED_RATE_PASS automation_cases=10'
END = 'SDK_PROBE_PASS automation_cases=6 stereo_frames=120000'
CASE = re.compile(r'SDK_AUTOMATION rate=(\S+) block=(\d+) frames=(\d+) max_error=(\S+)')
STATE = re.compile(r'SDK_STATE_PASS writes=20000 reads=([1-9]\d*) blocks=([1-9]\d*)')


def validate(data):
    lines = [s.strip() for s in data.decode('utf-8-sig').splitlines() if s.strip()]
    if len(lines) != 19 or lines[16] != EXT or lines[18] != END:
        raise ValueError('expected 16 ordered cases, extended marker, state stress and final marker')
    state = STATE.fullmatch(lines[17])
    if not state or int(state[2]) < 256:
        raise ValueError('missing or incomplete state stress')
    for line, expected in zip(lines[:16], EXPECTED):
        m = CASE.fullmatch(line)
        if not m:
            raise ValueError('malformed automation case: ' + line)
        try:
            rate, error = Decimal(m[1]), Decimal(m[4])
        except InvalidOperation as exc:
            raise ValueError('invalid numeric case: ' + line) from exc
        if (not rate.is_finite() or (rate, int(m[2]), int(m[3])) != expected
                or not error.is_finite() or not Decimal(0) <= error < Decimal('0.00002')):
            raise ValueError('wrong case identity, frame count or error: ' + line)


def verify_zip(data, path):
    with zipfile.ZipFile(path) as z:
        if z.namelist().count('sdk-probe.txt') != 1 or z.read('sdk-probe.txt') != data:
            raise ValueError('packaged SDK transcript differs from the validated file')
        if z.testzip() is not None:
            raise ValueError('package CRC failure')


def self_test():
    import tempfile
    lines = [f'SDK_AUTOMATION rate={r} block={b} frames={n} max_error=0'
             for r, b, n in EXPECTED]
    lines += [EXT, 'SDK_STATE_PASS writes=20000 reads=1 blocks=256', END]
    encode = lambda rows: ('\n'.join(rows) + '\n').encode()
    data = encode(lines)
    validate(data)
    validate(b'\xef\xbb\xbf' + data.replace(b'\n', b'\r\n'))
    bad = [lines[:6] + lines[17:], lines[:-1], lines[:16] + lines[17:],
           lines[:17] + lines[18:], lines[:1] + lines[:1] + lines[2:],
           lines[:6] + [lines[6].replace('92160', '20000')] + lines[7:],
           lines[:8] + [lines[8].replace('1234.568', '1234.57')] + lines[9:],
           lines[:17] + [lines[17].replace('blocks=256', 'blocks=255')] + lines[18:],
           lines[:17] + [lines[17].replace('writes=20000', 'writes=19999')] + lines[18:],
           lines + ['SDK_PROBE_FAIL unexpected']]
    for err in ('nan', 'inf', '-1', '0.00002', '1', 'bad'):
        bad.append([lines[0].replace('max_error=0', 'max_error='+err)] + lines[1:])
    for case in bad:
        try:
            validate(encode(case))
        except ValueError:
            continue
        raise AssertionError('invalid receipt admitted')
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'fixture.zip'
        for payload in (data, encode(lines[:6] + lines[17:])):
            with zipfile.ZipFile(p, 'w') as z:
                z.writestr('sdk-probe.txt', payload)
            if payload == data:
                verify_zip(data, p)
            else:
                try:
                    verify_zip(data, p)
                except ValueError:
                    pass
                else:
                    raise AssertionError('stale package admitted')
    print(f'SHUTTLE_RECEIPT_SELFTEST_PASS positive=3 negative={len(bad)+1}')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('receipt', type=Path, nargs='?')
    p.add_argument('--zip', type=Path)
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.receipt is None:
        p.error('receipt required')
    else:
        data = a.receipt.read_bytes()
        validate(data)
        if a.zip:
            verify_zip(data, a.zip)
        print('SHUTTLE_RECEIPT_PASS cases=16 extended=10 state=1')
