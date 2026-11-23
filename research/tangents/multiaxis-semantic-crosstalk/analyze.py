"""MHAC-T009: deterministic symbolic/instrumental cue-mapping falsifier.

Not an acoustic renderer, listener model, or evidence about perceptual independence.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ('certainty', 'hazard', 'urgency')


def load():
    return (json.loads((ROOT / 'CASES.json').read_text(encoding='utf-8')),
            json.loads((ROOT / 'MAPPINGS.json').read_text(encoding='utf-8')))


def validate_cases(cases):
    assert len(cases) >= 24
    ids = [case['id'] for case in cases]
    assert len(set(ids)) == len(ids)
    combinations_seen = set()
    for case in cases:
        truth = case['truth']
        assert case['kind'] in ('factorial', 'unknown')
        assert truth['requested_action'] == 'inspect'
        assert truth['addressee'] == 'operator-A'
        for field in FIELDS:
            assert truth[field] in (None, 0, 1, 2)
        if case['kind'] == 'factorial':
            assert all(truth[f] is not None for f in FIELDS)
            combinations_seen.add(tuple(truth[f] for f in FIELDS))
    assert len(combinations_seen) == 27, 'Require independently labelled full 3x3x3 truth factorial'
    assert sum(c['kind'] == 'unknown' for c in cases) >= 3


def validate_mappings(policies):
    assert set(policies) == {'fused', 'naive', 'engineered', 'serial'}
    for name, policy in policies.items():
        assert policy['mode'] in ('fused_sum', 'component', 'serial_fields')
        if policy['mode'] == 'component':
            keys = [policy['dimensions'][f]['parameter'] for f in FIELDS]
            assert len(set(keys)) == 3, 'Not physically distinct descriptors'
            for field in FIELDS:
                scale = policy['dimensions'][field]['levels']
                assert len(scale) == 3
                assert all(isinstance(x, (int, float)) for x in scale)
                assert scale[0] < scale[1] < scale[2], f'{name}/{field}: polarity reversal or saturation'


def encode(truth, policy):
    mode = policy['mode']
    if mode == 'fused_sum':
        return ('unknown-state',) if any(truth[f] is None for f in FIELDS) else (sum(truth[f] for f in FIELDS),)
    if mode == 'component':
        return tuple((policy['dimensions'][f]['parameter'],
                      'UNKNOWN' if truth[f] is None else policy['dimensions'][f]['levels'][truth[f]])
                     for f in FIELDS)
    if mode == 'serial_fields':
        return tuple((f, 'UNKNOWN' if truth[f] is None else truth[f]) for f in FIELDS) + (
            ('requested_action', truth['requested_action']), ('addressee', truth['addressee']))
    raise ValueError(mode)


def audit(cases, policies):
    validate_cases(cases)
    validate_mappings(policies)
    result = {}
    for name, policy in policies.items():
        groups = {}
        for case in cases:
            key = repr(encode(case['truth'], policy))
            groups.setdefault(key, []).append(case['id'])
        collisions = [ids for ids in groups.values() if len(ids) > 1]
        result[name] = {
            'cases': len(cases), 'unique_codes': len(groups),
            'extra_cases_in_collision_groups': sum(len(g) - 1 for g in collisions),
            'collision_groups': len(collisions),
            'field_addressable': policy['mode'] != 'fused_sum',
            'human_decoding_tested': False,
        }
    return result


def main():
    cases, policies = load()
    print(json.dumps(audit(cases, policies), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
