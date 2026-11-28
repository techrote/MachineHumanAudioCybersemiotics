"""Write original five-second performance MIDI (120 BPM, 480 PPQN)."""
import pathlib
import struct
import sys


def vlq(value):
    data = [value & 127]
    while value > 127:
        value >>= 7
        data.insert(0, 128 | (value & 127))
    return bytes(data)


def midi(pressure):
    events = [(0, bytes.fromhex('ff510307a120'))]
    for pitch in (45, 52, 59, 66):
        events.extend([(0, bytes([0x90, pitch, 102])), (720, bytes([0x80, pitch, 0]))])
    events.extend([(2880, bytes([0x90, 69, 89])), (3360, bytes([0x80, 69, 0]))])
    if pressure:
        events.extend((tick, bytes([0xa0, pitch, value])) for tick, pitch, value in ((240, 45, 127), (480, 59, 102), (3120, 69, 127)))
    events.append((4800, bytes.fromhex('ff2f00')))
    track = bytearray()
    last = 0
    for tick, message in sorted(events, key=lambda e: e[0]):
        track.extend(vlq(tick - last) + message)
        last = tick
    return b'MThd' + struct.pack('>IHHH', 6, 0, 1, 480) + b'MTrk' + struct.pack('>I', len(track)) + track


if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, pressure in (('baseline', False), ('pressure', True)):
        (out / (name + '.mid')).write_bytes(midi(pressure))
