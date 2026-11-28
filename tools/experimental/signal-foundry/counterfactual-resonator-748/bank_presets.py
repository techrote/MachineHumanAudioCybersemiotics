"""Original component-only VST3 preset candidates for Harmonic Memory Bank."""
from pathlib import Path
import struct
import sys

CID = b'AE00577BADF94D9C8F2FB9D04991475C'


def encode(wet, bands):
    assert 0 <= wet <= 1000 and len(bands) == 4
    for hz, gain, peak, select, flags in bands:
        assert 40 <= hz <= 6000 and all(0 <= v <= 1000 for v in (gain, peak, select)) and 0 <= flags <= 7
    return struct.pack('<4sHB', b'HM01', wet, 0) + b''.join(struct.pack('<HHHHB', *b) for b in bands)


def wrap(state):
    assert len(state) == 43
    return struct.pack('<4sI32sq', b'VST3', 1, CID, 48 + len(state)) + state + struct.pack('<4sI4sqq', b'List', 1, b'Comp', 48, len(state))


def unwrap(preset):
    if len(preset) != 119 or preset[:48] != struct.pack('<4sI32sq', b'VST3', 1, CID, 91) or preset[91:] != struct.pack('<4sI4sqq', b'List', 1, b'Comp', 48, 43):
        raise ValueError('Invalid canonical preset container')
    state = preset[48:91]
    magic, wet, bypass = struct.unpack('<4sHB', state[:7])
    bands = [struct.unpack_from('<HHHHB', state, 7 + 9*i) for i in range(4)]
    if magic != b'HM01' or bypass != 0 or wet > 1000 or any(not 40 <= b[0] <= 6000 or max(b[1:4]) > 1000 or b[4] > 7 for b in bands):
        raise ValueError('Invalid canonical patch')
    return state


def main():
    out = Path(sys.argv[1]) if len(sys.argv) == 2 else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    patches = {
        '01 Soft Quartet': (350, [(f, 500, 250, 0, 1) for f in (110, 165, 220, 330)]),
        '02 Selective Choir': (650, [(f, 650, 1000, 1000, 5) for f in (110, 165, 220, 330)]),
        '03 Wide Memory': (550, [(f, 600, 900, 500, 5) for f in (82, 247, 740, 2220)]),
        '04 Erasure Study': (800, [(f, 700, 1000, 1000, flags) for f, flags in zip((250, 500, 900, 1500), (5, 7, 5, 7))]),
    }
    for name, (wet, bands) in patches.items():
        state = encode(wet, bands)
        preset = wrap(state)
        assert unwrap(preset) == state
        for i in list(range(48)) + list(range(91, 119)):
            bad = bytearray(preset); bad[i] ^= 1
            try:
                unwrap(bytes(bad))
            except ValueError:
                continue
            raise AssertionError('Malformed container accepted')
        if out:
            (out / (name + '.vstpreset')).write_bytes(preset)
            (out / (name + '.hm01')).write_bytes(state)
        print(name, len(preset), 'bytes')


if __name__ == '__main__':
    main()
