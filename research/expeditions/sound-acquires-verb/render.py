"""Original artistic stimuli. Requires espeak, NumPy and SciPy; no listening data."""
import hashlib
import pathlib
import subprocess
import tempfile
import wave
import sys
import numpy as np
from scipy.signal import butter, sosfiltfilt, resample_poly
from scipy.io import wavfile

FS = 24000
PHRASE = 'The glass remembers the rain.'
FOIL = 'The grass remembers the train.'

def pcm(x):
    return np.rint(np.clip(x, -.95, .95)*32767).astype('<i2')

def synth(text):
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d)/'speech.wav'
        subprocess.run(['espeak','-v','en','-s','145','-w',str(f),text],check=True)
        fs, x = wavfile.read(f)
        from math import gcd
        g = gcd(fs, FS)
        x = resample_poly(x.astype(float)/32768, FS//g, fs//g)
    return x * (.45/max(abs(x)))

def vocode(x, bands):
    edges = np.geomspace(150, 7000, bands+1)
    noise = np.random.default_rng(334).standard_normal(len(x))
    y = np.zeros(len(x))
    for lo,hi in zip(edges[:-1],edges[1:]):
        bp = butter(3,[lo,hi],btype='bandpass',fs=FS,output='sos')
        speech = sosfiltfilt(bp,x)
        env = np.maximum(0,sosfiltfilt(butter(2,160,fs=FS,output='sos'),abs(speech)))
        carrier = sosfiltfilt(bp,noise)
        y += env*carrier/max(np.sqrt(np.mean(carrier**2)),1e-12)
    return pcm(y*.42/max(abs(y)))

def triplets(semitones, count):
    t = np.arange(int(.05*FS))/FS
    envelope = np.sin(np.pi*np.arange(len(t))/(len(t)-1))**2
    a = pcm(.28*envelope*np.sin(2*np.pi*440*t))
    b = pcm(.28*envelope*np.sin(2*np.pi*440*2**(semitones/12)*t))
    gap = np.zeros(int(.075*FS),dtype='<i2')
    return np.tile(np.concatenate([a,gap,b,gap,a,np.tile(gap,2)]),count)

def render(folder):
    folder.mkdir(parents=True,exist_ok=True)
    def save(name,x):
        x = np.asarray(x,dtype='<i2')
        assert np.max(np.abs(x.astype(int))) < 32767
        with wave.open(str(folder/name),'wb') as w:
            w.setparams((1,2,FS,len(x),'NONE','not compressed'))
            w.writeframes(x.tobytes())
        with wave.open(str(folder/name),'rb') as w:
            assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,FS,len(x))
            assert w.readframes(len(x))==x.tobytes()
    clear, foil = synth(PHRASE),synth(FOIL)
    target = vocode(clear,4)
    save('01-target.wav',target)
    save('02-target-12bands.wav',vocode(clear,12))
    lead = max(len(clear),len(foil))
    pause = np.zeros(FS//2,dtype='<i2')
    def frame(cue):
        return np.concatenate([np.pad(cue,(0,lead-len(cue))),pause,target])
    for name,cue in [('03-neutral.wav',np.zeros(lead,dtype='<i2')),('04-congruent.wav',pcm(clear)),('05-incongruent.wav',pcm(foil))]:
        data = frame(cue)
        assert data[-len(target):].tobytes()==target.tobytes()
        save(name,data)
    target2 = triplets(8,8)
    save('06-triplet-target.wav',target2)
    for name,delta in [('07-close-prime.wav',2),('08-wide-prime.wav',14)]:
        data = np.concatenate([triplets(delta,16),target2])
        assert data[-len(target2):].tobytes()==target2.tobytes()
        save(name,data)
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob('*.wav'))}

if __name__=='__main__':
    out=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'audio')
    hashes=render(out)
    with tempfile.TemporaryDirectory() as d:
        assert render(pathlib.Path(d))==hashes
    print('Two render passes; matching WAV hashes, PCM round trips and invariant target tails.')
    for name,h in hashes.items(): print(h,name)
