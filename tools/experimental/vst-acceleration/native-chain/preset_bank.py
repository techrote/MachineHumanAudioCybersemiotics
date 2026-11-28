#!/usr/bin/env python3
"""Pinned MHAC preset/MIDI audition kit; no host execution or SDK redistribution."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import unittest
import zipfile

# Windows moduleinfo processor IDs, not controller IDs. Only these exact source versions.
G = 'AF04645CE81D4ABEAB751C90FFAD9163'
F = '3F74DE8192E743E6A36CB226C39DD8CE'
PINS = {
    G: ('Golden Receipt', 'eb78ea3b7a08a646910e66235724f259aeeb8190', b'GR01', 5, 16777216),
    F: ('Freeze Socket', 'fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2', b'MHFZ\x01\x00\x00\x00', 10, 1000000),
}
# Parameter order is the pinned native Param enum; Hold/Bypass default off.
BANK = [
    (G, '01 Golden Quartet', (0, 0, .4, .5, .45)),
    (G, '02 Missing First', (0, .25, .4, .5, .45)),
    (G, '03 Missing Third', (0, .75, .4, .5, .45)),
    (G, '04 Equal Counterexample', (1, .25, .4, .5, .45)),
    (G, '05 Needle Clock', (0, 0, .03, .1, .35)),
    (G, '06 Long Lantern', (0, .5, .9, .9, .4)),
    (F, '01 Four Step Gate', (.5, .8, 1, 0, 0, 1, .15, .7, .25, 0)),
    (F, '02 Output Latch', (.64, .9, 1, 0, 0, 1, .1, .65, .25, 0)),
    (F, '03 Transport Pause', (.64, .9, 1, .5, 0, 1, .1, .65, .25, 0)),
    (F, '04 Bank Snapshot', (.64, .9, 1, 1, 0, 1, .1, .65, .25, 0)),
    (F, '05 Slow Tremor', (.12, .45, .6, 0, 0, .9, .5, .7, .4, 0)),
    (F, '06 Dry Reference', (.64, .9, 1, 0, 0, 1, .1, .65, .25, 1)),
]
HEADER = struct.Struct('<4si32sq')
ENTRY = struct.Struct('<4sqq')
LIST = struct.Struct('<4si')


def state(cid, values):
    _, _, magic, count, scale = PINS[cid]
    if len(values) != count or any(not math.isfinite(x) or not 0 <= x <= 1 for x in values):
        raise ValueError('invalid normalized parameters')
    # Nonnegative C++ lround/llround, not Python ties-to-even round().
    return magic + struct.pack('<' + 'I' * count, *(math.floor(x * scale + .5) for x in values))


def preset(cid, values):
    body = state(cid, values)
    return (HEADER.pack(b'VST3', 1, cid.encode('ascii'), HEADER.size + len(body)) + body
            + LIST.pack(b'List', 1) + ENTRY.pack(b'Comp', HEADER.size, len(body)))


def read_preset(raw, expected):
    # Strict parser for our one-Comp canonical subset, NOT a general VST3 parser.
    _, _, magic, count, scale = PINS[expected]
    size = len(magic) + count * 4
    if len(raw) != HEADER.size + size + LIST.size + ENTRY.size:
        raise ValueError('unexpected preset size')
    sig, version, cid, offset = HEADER.unpack_from(raw)
    if (sig, version, cid, offset) != (b'VST3', 1, expected.encode('ascii'), HEADER.size + size):
        raise ValueError('invalid header, class or list offset')
    if LIST.unpack_from(raw, offset) != (b'List', 1):
        raise ValueError('invalid list')
    if ENTRY.unpack_from(raw, offset + LIST.size) != (b'Comp', HEADER.size, size):
        raise ValueError('invalid component extent')
    body = raw[HEADER.size:offset]
    if not body.startswith(magic):
        raise ValueError('invalid state version')
    q = struct.unpack_from('<' + 'I' * count, body, len(magic))
    if any(x > scale for x in q):
        raise ValueError('state value outside range')
    return tuple(x / scale for x in q)


def vlq(n):
    if not 0 <= n <= 0xfffffff:
        raise ValueError('invalid MIDI delta')
    parts = [n & 127]
    while n >> 7:
        n >>= 7
        parts.append((n & 127) | 128)
    return bytes(reversed(parts))


def midi():
    # SMF format 0, 500 PPQN, 120 BPM: one tick = one millisecond.
    notes = [(0, 48, 102), (137, 55, 95), (503, 60, 83), (1299, 67, 95),
             (1701, 52, 102), (2101, 57, 89)]
    events = [(0, b'\xff\x51\x03\x07\xa1\x20')]
    events += [(t, bytes((0x90, p, v))) for t, p, v in notes]
    events += [(2401, bytes((0x80, p, 0))) for _, p, _ in notes]
    events += [(4000, b'\xff\x2f\x00')]
    data = bytearray()
    last = 0
    for tick, event in events:
        data += vlq(tick - last) + event
        last = tick
    return b'MThd' + struct.pack('>IHHH', 6, 0, 1, 500) + b'MTrk' + struct.pack('>I', len(data)) + data


def kit():
    files = {}
    records = []
    for cid, name, values in BANK:
        plugin, commit, _, _, _ = PINS[cid]
        path = f'{plugin}/{name}.vstpreset'
        raw = preset(cid, values)
        restored = read_preset(raw, cid)
        if preset(cid, restored) != raw:
            raise ValueError('non-idempotent preset')
        files[path] = raw
        records.append(dict(path=path, class_id=cid, source=commit, parameters=list(restored),
                            sha256=hashlib.sha256(raw).hexdigest()))
    files['Audition.mid'] = midi()
    files['manifest.json'] = (json.dumps(dict(scope='offline generated candidate; host untested',
        presets=records, midi_sha256=hashlib.sha256(files['Audition.mid']).hexdigest()), indent=2) + '\n').encode()
    files['READ-ME.txt'] = (
        'Install the exact qualified 0.1.0 Golden Receipt and Freeze Socket VST3 bundles first.\n'
        'Import Audition.mid on a Golden Receipt track; insert Freeze Socket after it.\n'
        'Load matching presets via your host preset browser/import; host support is UNTESTED.\n'
        'Start with low monitoring gain. Compare Golden 02/03 (collision), then 04 (counterexample).\n'
        'Compare Freeze 02/03/04 by automating Hold and Step A-D during playback; mode alone does not freeze.\n'
        'Use 06 for dry reference. Save, close, reopen and compare parameter values and audio.\n'
        'MIDI velocities are quantized; automation is not embedded. This is not the exact native-chain render.\n'
        'No binaries, SDK source, controller-only state or transient voices/capture history are included.\n'
    ).encode()
    return files


def write_kit(path):
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED) as z:
        for name, raw in sorted(kit().items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 0
            z.writestr(info, raw)


class Tests(unittest.TestCase):
    def test_roundtrip_and_known_bytes(self):
        self.assertEqual(state(G, (0, .25, .5, 1, 0)).hex(),
                         '475230310000000000004000000080000000000100000000')
        self.assertEqual(state(F, (0, .5, 1, 0, 0, 0, 0, 0, 0, 0))[:20].hex(),
                         '4d48465a010000000000000020a1070040420f00')
        self.assertEqual(len(BANK), 12)
        for cid, _, values in BANK:
            raw = preset(cid, values)
            self.assertEqual(raw, preset(cid, read_preset(raw, cid)))
            self.assertEqual(len(raw), 100 if cid == G else 124)
            for a, b in zip(values, read_preset(raw, cid)):
                self.assertLessEqual(abs(a - b), .5 / PINS[cid][-1] + 1e-15)

    def test_reject_mutations(self):
        for cid, _, values in BANK:
            raw = preset(cid, values)
            offset = HEADER.size + len(state(cid, values))
            for pos in (0, 4, 8, 40, 48, offset, offset + 4, offset + 8, offset + 12, offset + 20):
                bad = bytearray(raw)
                bad[pos] ^= 1
                with self.assertRaises(ValueError):
                    read_preset(bad, cid)
            for n in range(len(raw)):
                with self.assertRaises(ValueError):
                    read_preset(raw[:n], cid)
            with self.assertRaises(ValueError):
                read_preset(raw + b'\0', cid)
            bad = bytearray(raw)
            start = HEADER.size + len(PINS[cid][2])
            bad[start:start+4] = b'\xff' * 4
            with self.assertRaises(ValueError):
                read_preset(bad, cid)
        for x in (float('nan'), float('inf'), -.01, 1.01):
            with self.assertRaises(ValueError):
                state(G, (0, 0, 0, 0, x))

    def test_midi_independent_decode(self):
        raw = midi()
        self.assertEqual(struct.unpack_from('>4sIHHH4sI', raw), (b'MThd', 6, 0, 1, 500, b'MTrk', len(raw)-22))
        pos, tick = 22, 0
        on, off = [], []
        while pos < len(raw):
            delta = 0
            while True:
                b = raw[pos]; pos += 1; delta = (delta << 7) | (b & 127)
                if b < 128:
                    break
            tick += delta
            status = raw[pos]; pos += 1
            if status == 0xff:
                kind, size = raw[pos:pos+2]; pos += 2
                payload = raw[pos:pos+size]; pos += size
                if kind == 0x51:
                    self.assertEqual((tick, payload), (0, b'\x07\xa1\x20'))
                else:
                    self.assertEqual((kind, size, tick, pos), (0x2f, 0, 4000, len(raw)))
            else:
                pitch, velocity = raw[pos:pos+2]; pos += 2
                self.assertIn(status, (0x90, 0x80))
                (on if status == 0x90 else off).append((tick, pitch, velocity))
        self.assertEqual([x[:2] for x in on], [(0,48),(137,55),(503,60),(1299,67),(1701,52),(2101,57)])
        self.assertEqual(off, [(2401,x[1],0) for x in on])

    def test_manifest(self):
        files = kit()
        manifest = json.loads(files['manifest.json'])
        self.assertEqual(len(files), 15)
        self.assertEqual(len({r['path'] for r in manifest['presets']}), 12)
        for r in manifest['presets']:
            self.assertEqual(hashlib.sha256(files[r['path']]).hexdigest(), r['sha256'])
        self.assertEqual(hashlib.sha256(files['Audition.mid']).hexdigest(), manifest['midi_sha256'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.out:
        write_kit(args.out)
        print(hashlib.sha256(args.out.read_bytes()).hexdigest(), args.out)
