"""Known-answer tests for the #452 frequency-selective gate.
Run: python -m unittest test_selective_gate
These are synthetic local gate tests, not semantic or human qualification.
"""
import unittest
import numpy as np
from selective_gate import SelectiveGate

class GateTests(unittest.TestCase):
    def test_markers(self):
        g=SelectiveGate(); t=np.arange(64)/16000
        for f in (3000,3300,3600):
            for amplitude in (300,1000,5500):
                for phase in (0,.7,2.1):
                    self.assertTrue(g(amplitude*np.sin(2*np.pi*f*t+phase)))
    def test_silence_low_band_and_low_level(self):
        g=SelectiveGate(); t=np.arange(64)/16000
        self.assertFalse(g(np.zeros(64)))
        for f in (440,800,1600):
            self.assertFalse(g(5500*np.sin(2*np.pi*f*t)))
        self.assertFalse(g(100*np.sin(2*np.pi*3000*t)))
    def test_wrong_length(self):
        with self.assertRaises(ValueError): SelectiveGate()(np.zeros(63))
    def test_not_authentication(self):
        # An arbitrary non-message 3300 Hz tone is acoustically indistinguishable.
        self.assertTrue(SelectiveGate()(2000*np.sin(2*np.pi*3300*np.arange(64)/16000)))
