"""Trace Bell TB01 Windows audition bank and optional actual-host witness."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import wave

CID = b'A6740DA9EA17442B9B283CF2584E908C'
HEADER = struct.Struct('<4si32sq')
LIST = struct.Struct('<4si')
ENTRY = struct.Struct('<4sqq')
STATE = struct.Struct('<4sI5fB3x')
# Pitch Hz, decay seconds, contrast, mix, spread, bypass.
BANK = (
    ('01 Trace Bell', (220, .35, .8, .3, .5, 0)),
    ('02 Iron Footsteps', (110, .09, .95, .5, .2, 0)),
    ('03 Glass Rain', (440, .18, .9, .65, .85, 0)),
    ('04 Distant Foundry', (82.5, 1.1, .65, .7, .95, 0)),
    ('05 Quiet Halo', (165, .65, .15, .18, .6, 0)),
    ('06 Metallic Breath', (330, .85, .05, .55, .35, 0)),
    ('07 Narrow Chime', (293.665, .25, .75, .75, 0, 0)),
    ('08 Dry Reference', (220, .35, .8, .3, .5, 1)),
)


def state(values):
    if len(values) != 6 or values[5] not in (0, 1):
        raise ValueError('invalid patch')
    bounds = ((80, 500), (.03, 1.2), (0, 1), (0, 1), (0, 1))
    if any(not math.isfinite(x) or not lo <= x <= hi
           for x, (lo, hi) in zip(values, bounds)):
        raise ValueError('invalid parameter')
    return STATE.pack(b'TB01', 1, *values)


def preset(values):
    body = state(values)
    return (HEADER.pack(b'VST3', 1, CID, HEADER.size + len(body)) + body
            + LIST.pack(b'List', 1) + ENTRY.pack(b'Comp', HEADER.size, len(body)))


def component(raw):
    sig, version, cid, offset = HEADER.unpack_from(raw)
    if (sig, version, cid) != (b'VST3', 1, CID) or not HEADER.size <= offset <= len(raw)-LIST.size:
        raise ValueError('invalid header')
    tag, count = LIST.unpack_from(raw, offset)
    if tag != b'List' or not 1 <= count <= 32 or offset+LIST.size+count*ENTRY.size != len(raw):
        raise ValueError('invalid list')
    chunks = {}
    for i in range(count):
        key, start, size = ENTRY.unpack_from(raw, offset+LIST.size+i*ENTRY.size)
        if key in chunks or start < HEADER.size or size < 0 or start+size > offset:
            raise ValueError('invalid chunk')
        chunks[key] = raw[start:start+size]
    body = chunks.get(b'Comp', b'')
    if len(body) != STATE.size or body[:8] != b'TB01\x01\x00\x00\x00' or body[28] > 1 or any(body[29:]):
        raise ValueError('invalid component')
    return body


def generate(out):
    dest = out/'Presets'
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, values in BANK:
        raw = preset(values)
        assert component(raw) == state(values)
        (dest/(name+'.vstpreset')).write_bytes(raw)
        rows.append({'name': name, 'parameters': values, 'sha256': hashlib.sha256(raw).hexdigest()})
    (dest/'bank.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    return rows


def self_test():
    raw = preset(BANK[0][1])
    assert len(raw) == 108 and len(component(raw)) == 32
    assert len({preset(v) for _, v in BANK}) == len(BANK)
    for _, v in BANK:
        assert component(preset(v)) == state(v)
    for pos in (0, 4, 8, 40, 48, 52, 76, 77, 80, 84, 88, 92, 100):
        bad = bytearray(raw)
        bad[pos] ^= 255
        try:
            component(bad)
        except ValueError:
            continue
        raise AssertionError(f'accepted corrupt byte {pos}')
    for v in ((float('nan'), .35, .8, .3, .5, 0), (501, .35, .8, .3, .5, 0), (220, .35, .8, .3, .5, 2)):
        try:
            preset(v)
        except ValueError:
            continue
        raise AssertionError('accepted invalid parameter')
    print('PASS 8 preset round trips; 13 corruption and 3 invalid parameter rejections')


def host(module, out):
    import numpy as np
    from pedalboard import load_plugin
    rows = []
    for rate in (44100, 48000, 96000):
        t = np.arange(rate*2, dtype=np.float64)/rate
        dry = np.zeros((2, len(t)), dtype=np.float32)
        for at, frequency in ((0, 173), (.2, 257), (.45, 391)):
            u = t-at
            pulse = np.where((u >= 0) & (u < .12), np.exp(-35*np.maximum(u, 0)), 0)
            dry[0] += (.08*pulse*np.cos(2*np.pi*frequency*u)).astype(np.float32)
            dry[1] += (.055*pulse*np.cos(2*np.pi*(frequency+31)*u)).astype(np.float32)
        signatures = set()
        for name, values in BANK:
            outputs = []
            for block in (127, 1024):
                p = load_plugin(module)
                p.process(np.zeros((2, 1024), np.float32), rate, buffer_size=block, reset=True)
                p.preset_data = preset(values)
                assert component(p.preset_data) == state(values), name
                # Let the 10ms control transition settle before the score.
                p.process(np.zeros((2, rate//10), np.float32), rate, buffer_size=block, reset=False)
                wet = p.process(dry.copy(), rate, buffer_size=block, reset=False)
                assert component(p.preset_data) == state(values), name
                assert wet.shape == dry.shape and np.isfinite(wet).all() and np.max(np.abs(wet)) <= 1
                if values[5]:
                    assert np.array_equal(wet, dry), name
                else:
                    assert np.max(np.abs(wet-dry)) > 1e-4, name
                outputs.append(wet)
            error = float(np.max(np.abs(outputs[0]-outputs[1])))
            assert error < 1e-5, (name, rate, error)
            wet = outputs[0]
            signatures.add(hashlib.sha256(wet.tobytes()).hexdigest())
            rows.append(dict(name=name, rate=rate, partition_max_error=error, peak=float(np.max(np.abs(wet)))))
            if rate == 48000:
                dest = out/'PresetAuditions'
                dest.mkdir(exist_ok=True)
                with wave.open(str(dest/(name+'.wav')), 'wb') as w:
                    w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
                    w.writeframes(np.rint(wet.T*.5*32767).astype('<i2').tobytes())
        assert len(signatures) == len(BANK), (rate, len(signatures))
    (out/'preset-host-receipt.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    print('PASS 48 host renders; 24 partition comparisons; 8 distinct outputs per rate')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--module')
    args = p.parse_args()
    self_test()
    generate(args.out)
    if args.module:
        host(args.module, args.out)
