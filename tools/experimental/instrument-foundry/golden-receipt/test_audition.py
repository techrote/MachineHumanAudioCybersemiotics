"""Independent SMF decoder and negative controls for make_audition.py."""
import struct
import unittest
from make_audition import CASES, midi, vlq


def decode(b):
    if b[:14] != b'MThd' + struct.pack('>IHHH', 6, 0, 1, 480):
        raise ValueError('header')
    if b[14:18] != b'MTrk' or struct.unpack('>I', b[18:22])[0] != len(b)-22:
        raise ValueError('track')
    i, t, peak = 22, 0, 0
    active, found, tempo = {}, [], []
    def read_delta():
        nonlocal i
        n = 0
        for _ in range(4):
            v = b[i]; i += 1
            n = (n << 7) | (v & 127)
            if not v & 128:
                return n
        raise ValueError('delta')
    while i < len(b):
        t += read_delta()
        status = b[i]; i += 1
        if status == 255:
            kind = b[i]; i += 1
            length = read_delta()
            value = b[i:i+length]; i += length
            if kind == 81:
                tempo.append((t, int.from_bytes(value, 'big')))
            elif kind == 47:
                if length or i != len(b) or active:
                    raise ValueError('end')
                return sorted(found), t, tempo, peak
            else:
                raise ValueError('meta')
        elif status in (0x90, 0x80):
            pitch, vel = b[i:i+2]; i += 2
            if status == 0x90:
                if pitch in active or not vel:
                    raise ValueError('note on')
                active[pitch] = (t, vel)
                peak = max(peak, len(active))
            else:
                start, velocity = active.pop(pitch)
                found.append((start, t, pitch, velocity))
        else:
            raise ValueError('status')
    raise ValueError('missing end')


class AuditionTests(unittest.TestCase):
    def test_fixtures(self):
        for (name, (notes, end)), expected in zip(CASES.items(), (1, 1, 6, 1, 17)):
            with self.subTest(name=name):
                b = midi(notes, end)
                self.assertEqual(b, midi(notes, end))
                self.assertEqual(decode(b), (sorted(notes), end, [(0, 500000)], expected))

    def test_invalid_deltas(self):
        for n in (-1, 0x10000000):
            with self.subTest(n=n), self.assertRaises(ValueError):
                vlq(n)

    def test_invalid_notes(self):
        for notes in ([(0,0,60,100)], [(0,1,128,100)], [(0,481,60,100)], [(0,1,60,0)]):
            with self.subTest(notes=notes), self.assertRaises(ValueError):
                midi(notes, 480)

    def test_damaged_track(self):
        b = midi(*CASES['01-collision-witness'])
        with self.assertRaises(ValueError):
            decode(b[:-1])

if __name__ == '__main__':
    unittest.main()
