"""Fail closed on incomplete Orbit Lantern SDK replay receipts (INST-011X)."""
import itertools
import math
import re
import sys
from pathlib import Path

ROW = re.compile(r'SDK_REPLAY rate=(\d+) sustain=(\d+) channels=(\d+) identity=(\d+) format=(\d+) block=(\d+) frames=(\d+) max_error=(\S+)')
SUMMARIES = ('SDK_CONTROLLER_PASS encodings=4 parameters=7',
             'SDK_REPLAY_PASS cases=144', 'SDK_EXPRESSIVE_REPLAY_PASS cases=48')
RATES = (44100, 48000, 96000)
EXPECTED = set(itertools.product(RATES, (0, 1), (1, 2), (0, 1, 2), (0, 1), (127, 1024)))
EXPECTED |= set(itertools.product(RATES, (1,), (1, 2), (3, 4), (0, 1), (127, 1024)))


def verify(text):
    lines = text.splitlines()
    for summary in SUMMARIES:
        if lines.count(summary) != 1:
            raise ValueError('missing or duplicate summary: ' + summary)
    seen = set()
    for line in lines:
        if not line.startswith('SDK_REPLAY '):
            continue
        match = ROW.fullmatch(line)
        if not match:
            raise ValueError('malformed replay row: ' + line)
        rate, sustain, channels, identity, fmt, block, frames = map(int, match.groups()[:7])
        key = (rate, sustain, channels, identity, fmt, block)
        if key not in EXPECTED or key in seen:
            raise ValueError('unexpected or duplicate case: ' + str(key))
        expected_frames = 5 * rate if identity >= 3 else 17 + 8 * 3072 + rate + 2048
        error = float(match.group(8))
        if frames != expected_frames or not math.isfinite(error) or not 0 <= error < (2e-6 if fmt == 0 else 1e-10):
            raise ValueError('invalid render receipt: ' + line)
        seen.add(key)
    if seen != EXPECTED:
        raise ValueError('missing cases: ' + str(sorted(EXPECTED - seen)))
    return len(seen)


def self_test():
    rows = []
    for rate, sustain, channels, identity, fmt, block in sorted(EXPECTED):
        frames = 5 * rate if identity >= 3 else 17 + 8 * 3072 + rate + 2048
        rows.append(f'SDK_REPLAY rate={rate} sustain={sustain} channels={channels} identity={identity} format={fmt} block={block} frames={frames} max_error=0')
    def joined(items):
        return '\n'.join([*SUMMARIES, *items])
    assert verify(joined(rows)) == 192
    bad = [joined(rows[1:]), joined(rows + rows[:1]),
           joined(rows + [rows[0].replace('max_error=0', 'max_error=1e-12')]),
           joined([rows[0].replace('channels=1', 'channels=9'), *rows[1:]]),
           joined([rows[0].replace('max_error=0', 'max_error=nan'), *rows[1:]]),
           joined([rows[0].replace('max_error=0', 'max_error=1'), *rows[1:]]),
           joined([rows[0].replace('frames=70741', 'frames=1'), *rows[1:]]),
           joined(rows).replace(SUMMARIES[0], ''), joined(rows) + '\n' + SUMMARIES[1]]
    for candidate in bad:
        try:
            verify(candidate)
        except ValueError:
            continue
        raise AssertionError('accepted invalid receipt')
    print(f'ORBIT_REPLAY_GATE_SELF_TEST_PASS positive=1 negative={len(bad)}')


if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        self_test()
    elif len(sys.argv) == 2:
        print(f'ORBIT_REPLAY_GATE_PASS cases={verify(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))}')
    else:
        raise SystemExit('usage: verify_replay.py --self-test | sdk-replay.txt')
