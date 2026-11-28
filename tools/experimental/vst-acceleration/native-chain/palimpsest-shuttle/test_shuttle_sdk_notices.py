"""Portable regression for Windows case-insensitive provenance contamination."""
import tempfile
import unittest
from pathlib import Path
from shuttle_sdk_notices import copy_notices, REQUIRED


class CopyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name) / 'trace'
        self.dst = Path(self.tmp.name) / 'shuttle'
        self.src.mkdir()
        self.dst.mkdir()
        for name in REQUIRED:
            (self.src / name).write_bytes(name.encode())
        (self.src / 'sdk-probe.txt').write_bytes(b'trace six cases')
        (self.src / 'SDK-base-LICENSE.txt').write_bytes(b'license')
        (self.src / 'SDK-tutorials-NOTICE').write_bytes(b'notice')
        (self.src / 'SDK-unknown-LICENSE.txt').write_bytes(b'unrelated')
        (self.dst / 'sdk-probe.txt').write_bytes(b'shuttle sixteen cases')

    def test_copy_only_notices(self):
        self.assertEqual(copy_notices(self.src, self.dst), 5)
        self.assertEqual({p.name for p in self.dst.iterdir()},
                         REQUIRED | {'SDK-base-LICENSE.txt', 'SDK-tutorials-NOTICE', 'sdk-probe.txt'})
        self.assertEqual((self.dst / 'sdk-probe.txt').read_bytes(), b'shuttle sixteen cases')
        for name in REQUIRED | {'SDK-base-LICENSE.txt', 'SDK-tutorials-NOTICE'}:
            self.assertEqual((self.dst / name).read_bytes(), (self.src / name).read_bytes())

    def test_uppercase_probe_is_not_provenance(self):
        (self.src / 'sdk-probe.txt').unlink()
        (self.src / 'SDK-PROBE.txt').write_bytes(b'other unrelated log')
        self.test_copy_only_notices()

    def test_casefold_destination_collision(self):
        (self.dst / 'sdk-gitlinks.txt').write_bytes(b'prior')
        with self.assertRaises(ValueError):
            copy_notices(self.src, self.dst)
        self.assertEqual(len(list(self.dst.iterdir())), 2)

    def test_missing_required(self):
        (self.src / 'BUILD-SOURCE.txt').unlink()
        with self.assertRaises(ValueError):
            copy_notices(self.src, self.dst)
        self.assertEqual(len(list(self.dst.iterdir())), 1)

    def test_empty_notice(self):
        (self.src / 'SDK-base-LICENSE.txt').write_bytes(b'')
        with self.assertRaises(ValueError):
            copy_notices(self.src, self.dst)
        self.assertEqual(len(list(self.dst.iterdir())), 1)

    def test_same_directory(self):
        with self.assertRaises(ValueError):
            copy_notices(self.src, self.src)


if __name__ == '__main__':
    unittest.main()
