"""Deterministic, bounded T007 table/manifest generator and exact-byte checker."""
import argparse
import hashlib
import json
from pathlib import Path
try:
    from .model import run_all
except ImportError:
    from model import run_all

OUT = Path(__file__).resolve().parent/'generated'/'SUMMARY.json'


def summary():
    full = run_all()
    compact = {
        'schema': 'mhac-t007-summary-v1',
        'scope': 'synthetic engineering diagnostics, NOT perceptual or behavioral results',
        'inputs_sha256': full['inputs_sha256'],
        'cue_count': len(full['runs']['identity']),
        'transform_count': len(full['runs']),
        'case_count': len(json.loads((OUT.parent.parent/'CASES.json').read_text())['cases']),
        'diagnostics': {},
    }
    for t, records in full['runs'].items():
        pairs=full['pairwise'][t]
        compact['diagnostics'][t] = {
            'pulse_pair_count_difference': pairs['P_FAST|P_SLOW']['pulse_groups_proxy'],
            'spectral_pair_contrast_db': pairs['F_LOW|F_HIGH']['high_low_projection_db'],
            'spatial_pair_ild_difference_db': pairs['S_LEFT|S_RIGHT']['interaural_level_db'],
            'alternate_pulse_groups': records['P_ALT']['features']['pulse_groups_proxy'],
            'alternate_tail_rms': records['P_ALT']['features']['tail_rms'],
            'left_waveform_sha256': records['S_LEFT']['waveform_sha256'],
            'right_waveform_sha256': records['S_RIGHT']['waveform_sha256'],
        }
    return compact


def generate(check=False):
    value=json.dumps(summary(), sort_keys=True, indent=2, ensure_ascii=False)+'\n'
    if check:
        if not OUT.is_file() or OUT.read_text(encoding='utf-8')!=value:
            raise SystemExit('T007 generated summary stale; rerun generate.py')
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(value,encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    generate(parser.parse_args().check)
