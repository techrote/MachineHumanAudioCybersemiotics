"""Isolated bridge: verify the synthetic expedition from ordinary root CI."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave

EXPEDITION = Path(__file__).resolve().parents[1] / 'research/expeditions/spectral-doppelganger'


def circular_corr(samples):
    nz = [(i,v) for i,v in enumerate(samples) if v]
    out = [0]*len(samples)
    for i,a in nz:
        for j,b in nz:
            out[(j-i)%len(samples)] += a*b
    return out


class TestSpectralDoppelganger199(unittest.TestCase):
    def test_scoped_unit_suite(self):
        subprocess.run([sys.executable,'-m','unittest','-v'],
                       cwd=EXPEDITION,check=True,capture_output=True,text=True)

    def test_full_generated_witnesses(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            subprocess.run([sys.executable,str(EXPEDITION/'doppelganger.py'),
                            '--max-n','16','--out',tmp],check=True,capture_output=True,text=True)
            result=json.loads((out/'results.json').read_text(encoding='utf-8'))
            self.assertEqual(sum(r['raw_patterns'] for r in result['survey']),131064)
            self.assertEqual(sum(r['bracelets'] for r in result['survey']),5094)
            self.assertEqual(sum(r['ambiguous_pair_classes'] for r in result['survey']),539)
            self.assertEqual(sum(r['unresolved_triple_classes'] for r in result['survey']),0)
            self.assertEqual(result['antipodal_survey'][-1]['pair_collision_classes'],6)
            self.assertEqual(result['fourth_difference_count'],3168)
            expected={
                'pair.wav':('ae557d1fa6d5fb58340ba0a36810c6c008441340082a64fe4e989bbc3632e869',12),
                'third-order-collision.wav':('c48f746e406155829ee8082a70214e1725e5a1cb1f7fffe772e25e45189cf079',24),
            }
            for name,(digest,n) in expected.items():
                with self.subTest(name=name):
                    path=out/name
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
                    self.assertEqual(result['wav_sha256'][name],digest)
                    with wave.open(str(path),'rb') as f:
                        self.assertEqual((f.getnchannels(),f.getsampwidth(),f.getframerate()),(2,2,12000))
                        self.assertEqual(f.getnframes(),4*n*1800)
                        data=f.readframes(f.getnframes())
                    period=n*1800*4  # bytes per stereo period
                    self.assertEqual(data,data[:period]*4)
                    left,right=zip(*struct.iter_unpack('<hh',data[:period]))
                    self.assertNotEqual(left,right)
                    self.assertLessEqual(max(map(abs,left+right)),12000)
                    # Exact comparison at the actual generated PCM sample rate.
                    self.assertEqual(circular_corr(left),circular_corr(right))
