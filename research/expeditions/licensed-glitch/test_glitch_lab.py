import itertools
from pathlib import Path
import tempfile
import unittest
import wave

from glitch_lab import candidates, codebook, frontier, full_word_capacity, report


class GlitchLabTests(unittest.TestCase):
    def test_independent_small_frontiers(self):
        for n, t in [(2, 0), (3, 0), (3, 1), (4, 1), (4, 2)]:
            out = {}
            words = tuple(range(1 << n))
            # Direct subsets and string-coordinate distance, no symmetry reduction.
            far = {x: {y for y in words if sum(a != b for a, b in zip(
                format(x, f'0{n}b'), format(y, f'0{n}b'))) > 2*t} for x in words}
            for k in range(1, len(words) + 1):
                for a in itertools.combinations(words, k):
                    b = set.intersection(*(far[x] for x in a))
                    if b:
                        out[k] = max(out.get(k, 0), len(b))
            self.assertEqual(frontier(n, t)[0], out)

    def test_five_bit_boundary(self):
        self.assertEqual(frontier(5, 1)[0], {1:16, 2:10, 3:7, 4:6, 5:6, 6:6,
            7:3, 8:2, 9:2, 10:2, 11:1, 12:1, 13:1, 14:1, 15:1, 16:1})
        # Independent upper bound check: all 7-subsets containing zero.
        # Integer intersections on complement masks; no chosen-B symmetry.
        far = [sum(1 << y for y in range(32) if (x ^ y).bit_count() >= 3)
               for x in range(32)]
        for a in itertools.combinations(range(1, 32), 6):
            mask = far[0]
            for x in a:
                mask &= far[x]
            self.assertLess(mask.bit_count(), 7)

    def test_full_word_capacity(self):
        self.assertEqual(full_word_capacity(5, 1), 4)
        self.assertFalse(any(all((a ^ b).bit_count() >= 3 for a, b in itertools.combinations(c, 2))
                             for c in itertools.combinations(range(32), 5)))
        self.assertTrue(all((a ^ b).bit_count() >= 3 for a, b in itertools.combinations([0,7,25,30], 2)))

    def test_semantics_and_ambiguity(self):
        code = codebook()
        self.assertEqual([len(v) for v in code.values()], [6, 6])
        cases = 0
        for label, words in code.items():
            for word in words:
                for mask in [0, 1, 2, 4, 8, 16]:
                    received = word ^ mask
                    possible = candidates(received, code)
                    self.assertEqual({m for m, x in possible}, {label})
                    self.assertIn((label, word), possible)
                    cases += 1
        self.assertEqual(cases, 72)
        self.assertEqual(sorted(len(candidates(y, code)) for y in range(32)), [2]*30+[6]*2)
        self.assertEqual(sum(len(candidates(y, code)) for y in range(32)), 72)
        # Out-of-model two flips can change class, even with a unique label.
        self.assertEqual({m for m, x in candidates(1 ^ 2 ^ 4, code)}, {1})
        self.assertEqual(candidates(1, {0: [1], 1: [30]}, 0), [(0, 1)])

    def test_audio_and_provenance(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)
            result = report(p)
            hashes = result['wav_sha256']
            self.assertEqual(hashes['intentional'], hashes['corrupted'])
            self.assertNotEqual(hashes['intentional'], hashes['canonicalized'])
            self.assertNotEqual(result['sound_history']['intentional_sent'], result['sound_history']['corrupted_sent'])
            for f in p.glob('*.wav'):
                with wave.open(str(f), 'rb') as w:
                    self.assertEqual((w.getnchannels(), w.getsampwidth(), w.getframerate()), (1,2,8000))
                    self.assertEqual(w.getnframes() % 5440, 0)


if __name__ == '__main__':
    unittest.main()
