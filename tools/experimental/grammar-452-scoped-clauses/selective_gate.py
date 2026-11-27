"""MHAC #452: causal frequency-selective marker gate, synthetic only."""
import numpy as np
class SelectiveGate:
    def __init__(self,rate=16000,hop=64,coherence=.30,minimum_rms=120):
        t=np.arange(hop)/rate
        self.bases=np.stack([np.linalg.qr(np.stack([np.cos(2*np.pi*f*t),np.sin(2*np.pi*f*t)],axis=1))[0] for f in (3000,3300,3600)])
        self.coherence=coherence;self.minimum_rms=minimum_rms;self.hop=hop
    def measure(self,pcm):
        z=np.asarray(pcm,dtype=float)
        if z.shape!=(self.hop,):raise ValueError('wrong hop length')
        energy=float(z@z); projected=float(np.max(np.sum((self.bases.transpose(0,2,1)@z)**2,axis=1)))
        return projected/max(energy,1e-12),np.sqrt(projected/self.hop)
    def __call__(self,pcm):
        c,r=self.measure(pcm);return c>=self.coherence and r>=self.minimum_rms
