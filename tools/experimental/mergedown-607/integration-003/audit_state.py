"""Independent, fixture-scoped semantic replay; not a PCM decoder or general v33 reducer."""
import argparse
import collections
import copy
import json
from pathlib import Path


def check(ok, message):
    if not ok:
        raise ValueError(message)


def ident(p, g):
    return f'{p["source"]}:{g}'


def replay(records):
    # v40 uses only distinct ordered indices 1/2 and event occurrences.
    ordered, status, effects, tape, events = {}, {}, [], [], []
    floor = 0
    for rec in records:
        p, g = rec['p'], rec['g']
        k = ident(p, g)
        check(p['kind'] == 0 and p['version'] == 1 and p['actor'] == 9 and p['source'] in (1, 2), 'packet scope')
        verb, (value,) = p['tree']
        check(value in ('open', 'stopped', 'fault', 'overload'), 'value scope')
        if p['event'] == 8 and verb == 'pump-reports':
            events.append(dict(id=k, value=value))
            status[k] = 'applied'
            effects.append(k)
        else:
            i = p['seq']
            check(p['event'] == 7 and p['source'] == 1 and verb == 'verify' and i in (1, 2) and i not in ordered, 'ordered fixture scope')
            ordered[i] = (k, value)
            status[k] = 'buffered'
            while floor + 1 in ordered:
                floor += 1
                a, v = ordered[floor]
                tape.append(dict(index=floor, value=v))
                status[a] = 'applied'
                effects.append(a)
    return dict(world=dict(state=None, tape=tape, events=events, floor=floor, blocked=False), status=status, effects=effects)


def audit(data):
    counts = collections.Counter()
    for row in data['rows']:
        records = []
        for t in row['trace']:
            a, job = t['decoded'], t['job'] or {}
            if job.get('role') == 'data':
                if a['status'] != 'receipt-candidate':
                    expected = dict(decision='no-receipt', ack=False, semantic=None)
                else:
                    p, g = a['packet'], a['generation']
                    check(a['epoch'] == 0 and a['role'] == 0 and 0 <= g <= 255, 'admission scope')
                    if row['bits']:
                        check(a['authenticated'] is True, 'authentication flag')
                    k = ident(p, g)
                    old = next((r for r in records if ident(r['p'], r['g']) == k), None)
                    if old:
                        same = old['p'] == p
                        expected = dict(decision='duplicate' if same else 'occurrence-conflict', ack=same, semantic=replay(records)['status'][k] if same else None)
                    else:
                        check(len(records) < 4 and g >= max((r['g'] for r in records if r['p']['source'] == p['source']), default=-1)-2, 'capacity/stale scope')
                        records.append(dict(p=p, g=g))
                        expected = dict(decision='new', ack=True, semantic=replay(records)['status'][k])
                check(t['decision'] == expected, 'admission decision')
                counts[expected['decision']] += 1
            else:
                counts['non_data_slots'] += 1
            expected_state = dict(schema='mhac-semantic-v33', policy='typed', records=records, semantic=replay(records))
            check(t['state'] == expected_state, 'semantic snapshot')
            counts['snapshots'] += 1
    check(counts['snapshots'] == 196 and counts['new'] == 48 and counts['no-receipt'] == 2 and counts['occurrence-conflict'] == 1, 'fixture accounting')
    return dict(counts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('receipts', nargs=2, type=Path)
    args = p.parse_args()
    result = []
    for path in args.receipts:
        data = json.loads(path.read_bytes())
        counts = audit(data)
        bad = copy.deepcopy(data)
        bad['rows'][0]['trace'][0]['state']['semantic']['effects'].append('fabricated')
        try:
            audit(bad)
        except ValueError as e:
            check(str(e) == 'semantic snapshot', 'wrong negative refusal')
        else:
            raise ValueError('fabricated effect accepted')
        bad = copy.deepcopy(data)
        t = next(t for r in bad['rows'] for t in r['trace'] if isinstance(t['decision'], dict) and t['decision']['decision'] == 'new')
        t['decision']['ack'] = False
        try:
            audit(bad)
        except ValueError as e:
            check(str(e) == 'admission decision', 'wrong negative refusal')
        else:
            raise ValueError('modified admission accepted')
        result.append(dict(receipt=str(path), counts=counts, negative_refusals=2))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
