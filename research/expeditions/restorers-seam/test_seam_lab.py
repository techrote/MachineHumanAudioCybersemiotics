import itertools
import tempfile
import unittest
import wave
from pathlib import Path
from seam_lab import (ALPHABET, OBS, FRAMES, analyze, compatible, distance,
                      energy, pcm, render, sidecar)

class TestSeam(unittest.TestCase):
    def test_main(self):
        a=analyze(OBS)
        self.assertEqual(a['count'],27)
        self.assertEqual(a['smooth'],[(1,1,1,1,1)])
        self.assertEqual(a['minimax']['hamming']['risk'],3)
        self.assertEqual(len(a['minimax']['hamming']['winners']),27)
        self.assertEqual(a['minimax']['squared'],{'risk':3,'winners':[(1,1,1,1,1)]})
        self.assertEqual(energy((1,0,2,0,1)),10)
    def test_controls(self):
        self.assertEqual(analyze((0,None,2),1)['smooth'],[(0,1,2)])
        self.assertEqual(analyze((0,None,2),1)['status'],'identified')
        self.assertEqual(analyze((0,None,2))['count'],3)
        self.assertEqual(analyze((0,None,2),0)['status'],'inconsistent')
        self.assertEqual(analyze((0,1,2))['minimax']['hamming']['risk'],0)
    def test_exhaustive(self):
        for observed in itertools.product((None,*ALPHABET),repeat=4):
            k=observed.count(None); a=analyze(observed)
            self.assertEqual(a['count'],3**k)
            self.assertEqual(a['minimax']['hamming']['risk'],k)
            self.assertEqual(len(a['minimax']['hamming']['winners']),3**k)
            self.assertEqual(a['minimax']['squared']['risk'],k)
            self.assertEqual(a['minimax']['squared']['winners'],[tuple(1 if x is None else x for x in observed)])
    def test_sidecar(self):
        for s in compatible(OBS):
            self.assertEqual([r['provenance'] for r in sidecar(OBS,s)],['observed']+['conjectural']*3+['observed'])
        with self.assertRaises(ValueError):sidecar(OBS,(0,1,1,1,1))
        with self.assertRaises(ValueError):compatible((3,))
        with self.assertRaises(ValueError):compatible(OBS,-1)
        with self.assertRaises(ValueError):distance((0,),(0,1),'hamming')
        with self.assertRaises(ValueError):distance((0,),(0,),'bogus')
    def test_audio(self):
        a=pcm((1,1,1,1,1)); b=pcm((1,0,2,0,1)); raw=pcm(OBS)
        stride=FRAMES*4
        self.assertEqual(a[:stride],b[:stride]);self.assertEqual(a[-stride:],b[-stride:])
        self.assertNotEqual(a,b);self.assertEqual(raw[stride:4*stride],bytes(3*stride))
        audit=pcm((1,1,1,1,1),'audit')
        self.assertEqual(audit[2:stride:4],bytes(FRAMES))
        self.assertEqual(audit[3:stride:4],bytes(FRAMES))
        self.assertEqual(audit[stride:4*stride],a[stride:4*stride])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); r=render(p); self.assertEqual(r,render(p))
            for name in r['audio']:
                with wave.open(str(p/name),'rb') as w:
                    self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()),(2,2,16000,20000))

if __name__=='__main__':unittest.main()
