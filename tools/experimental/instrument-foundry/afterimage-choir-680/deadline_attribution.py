"""Offline attribution of Afterimage deadline-probe CSV; never used by process()."""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

FIELDS = 'rate,block,phase,start,count,onsets,wall_us,cpu_us,budget_us,peak'.split(',')


def rows(path):
    """Validate chronology and event count, then classify onset/fade overlap."""
    ends = {}
    with Path(path).open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != FIELDS:
            raise ValueError('unexpected deadline-probe header')
        for line, row in enumerate(reader, 2):
            try:
                rate, block, phase, start, count, onsets = [int(row[k]) for k in FIELDS[:6]]
                wall, cpu, budget, peak = [float(row[k]) for k in FIELDS[6:]]
                key = (rate, block, phase)
                if not (1000 <= rate <= 2000000 and block > 0 and 0 <= phase <= 3
                        and 0 < count <= block and start == ends.get(key, 0)
                        and start % block == 0 and all(map(math.isfinite, (wall, cpu, budget, peak)))
                        and wall >= 0 and cpu >= 0 and budget > 0 and 0 <= peak <= .520000001
                        and abs(budget - count * 1e6 / rate) <= 1e-5):
                    raise ValueError('invalid timing row')
                interval = rate * 6 // 1000
                first = ((start + interval - 1) // interval) * interval
                last = start + count - 1
                bursts = 0 if first > last else 1 + (last - first) // interval
                if onsets != 8 * bursts:
                    raise ValueError('onset count disagrees with sample clock')
                # This labels the *nominal* forced fade window, not measured voice state.
                since = start % interval
                fade = math.ceil(.005 * rate)
                label = 'onset' if bursts else 'post-onset' if since < fade else 'settled'
                ends[key] = start + count
                yield key, label, count < block, wall / budget, cpu / budget
            except (ValueError, TypeError, KeyError, OverflowError) as exc:
                raise ValueError(f'{path}:{line}: {exc}') from exc
    if not ends:
        raise ValueError('no timing rows')


def summarize(values):
    wall = sorted(x[0] for x in values)
    cpu = sorted(x[1] for x in values)
    n = len(values)
    p99 = math.ceil(.99 * n) - 1
    both = sum(w > 1 and c > 1 for w, c in values)
    return dict(blocks=n, wall_misses=sum(w > 1 for w in wall),
                cpu_misses=sum(c > 1 for c in cpu), both=both,
                wall_only=sum(w > 1 >= c for w, c in values),
                cpu_only=sum(c > 1 >= w for w, c in values),
                wall_p50=median(wall), cpu_p50=median(cpu),
                wall_p99=wall[p99], cpu_p99=cpu[p99],
                wall_max=wall[-1], cpu_max=cpu[-1])


def analyze(path):
    groups = defaultdict(list)
    strata = defaultdict(list)
    for key, label, partial, wall, cpu in rows(path):
        size = 'partial' if partial else 'full'
        groups[(label, size)].append((wall, cpu))
        strata[(*key, label, size)].append((wall, cpu))
    return dict(file=Path(path).name,
                pooled={':'.join(k): summarize(v) for k, v in sorted(groups.items())},
                strata={':'.join(map(str, k)): summarize(v) for k, v in sorted(strata.items())})


def self_test():
    import tempfile
    v = summarize([(0.5, 0.3), (1.1, 0.8), (1.2, 1.1), (.9, 1.01)])
    assert (v['wall_misses'], v['cpu_misses'], v['both'], v['wall_only'], v['cpu_only']) == (2, 2, 1, 1, 1)
    # 1 kHz: burst every six samples; nominal fade lasts five samples.
    header = ','.join(FIELDS) + '\n'
    good = '1000,1,0,0,1,8,100,90,1000,.1\n'
    good += ''.join(f'1000,1,0,{i},1,{8 if i == 6 else 0},100,90,1000,.1\n' for i in range(1, 7))
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'test.csv'
        path.write_text(header + good, encoding='utf-8')
        result = analyze(path)['pooled']
        assert [result[k + ':full']['blocks'] for k in ('onset', 'post-onset', 'settled')] == [2, 4, 1]
        for bad in (good.replace(',8,100,', ',0,100,', 1), good.replace(',90,', ',nan,', 1),
                    good.replace(',1000,.1', ',900,.1', 1), good.replace(',1,0,1,1,', ',1,0,2,1,', 1), ''):
            path.write_text(header + bad, encoding='utf-8')
            try:
                analyze(path)
            except ValueError:
                continue
            raise AssertionError('accepted invalid trace')
    print('PASS: event strata, deadline categories, five invalid trace controls')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', nargs='*')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.csv:
        print(json.dumps([analyze(path) for path in args.csv], indent=2, allow_nan=False))
    if not args.self_test and not args.csv:
        parser.error('provide CSV files or --self-test')
