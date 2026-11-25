"""Golden Receipt owner audition fixtures; standard-library-only SMF format 0.
At 120 BPM, 960 ticks = 1 s. Channel 1, no DAW-specific automation.
"""
from pathlib import Path
import struct

PPQ = 480

def vlq(n):
    if not 0 <= n <= 0x0fffffff:
        raise ValueError('MIDI delta out of range')
    out = [n & 127]
    while n >> 7:
        n >>= 7
        out.append((n & 127) | 128)
    return bytes(reversed(out))

def midi(notes, end):
    events = []
    for start, stop, pitch, velocity in notes:
        if not (0 <= start < stop <= end and 0 <= pitch <= 127 and 1 <= velocity <= 127):
            raise ValueError('invalid note')
        events += [(start, 1, bytes([0x90, pitch, velocity])), (stop, 0, bytes([0x80, pitch, 0]))]
    data = bytearray(b'\x00\xff\x51\x03\x07\xa1\x20')  # 500000 us/quarter
    prev = 0
    for tick, _, event in sorted(events):
        data += vlq(tick-prev) + event
        prev = tick
    data += vlq(end-prev) + b'\xff\x2f\x00'
    return b'MThd' + struct.pack('>IHHH', 6, 0, 1, PPQ) + b'MTrk' + struct.pack('>I', len(data)) + data

CASES = {
    '01-collision-witness': ([(480, 1440, 69, 114)], 2400),
    '02-velocity-ladder': ([(480+1920*i, 1440+1920*i, 69, v) for i,v in enumerate((25, 50, 80, 114, 127))], 10080),
    '03-staggered-chord': ([(480+120*i, 1920+120*i, p, 90) for i,p in enumerate((48,55,60,63,67,72))], 3360),
    '04-early-release': ([(480, 600, 69, 114), (2400, 3360, 69, 114)], 4320),
    '05-voice-capacity': ([(480, 1920, 48+i, 90) for i in range(17)] + [(2880,3840,69,114)], 4800),
}

def generate(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name,(notes,end) in CASES.items():
        (folder/(name+'.mid')).write_bytes(midi(notes,end))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    generate(parser.parse_args().output)
