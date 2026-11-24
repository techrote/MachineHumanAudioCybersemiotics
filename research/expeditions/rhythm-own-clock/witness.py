"""Original pulse-score witnesses; standard-library PCM renderer."""
import hashlib
import json
import struct
import wave
from pathlib import Path

RATE = 8000
TICK = 960
SCORES = {
    'nominal-flat': [1, 1, 1, 1],
    'nominal-ramp': [1, 2, 4, 8],
    'observed-flat': [1, 1, 1, 1],
    'observed-ramp': [1, 1, 1, 1],
    'curvature': [1, 2, 2, 1],
}


def render(intervals, path):
    # 250 Hz square wave, integer envelope, 40 ms; 120 ms base interval.
    starts = [0]
    for d in intervals:
        starts.append(starts[-1] + TICK * d)
    samples = [0] * (starts[-1] + TICK)
    for start in starts:
        for i in range(320):
            gain = 6000 * min(i, 319-i, 32) // 32
            samples[start+i] = gain if (i//16)%2 == 0 else -gain
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        w.writeframes(struct.pack('<'+'h'*len(samples), *samples))
    data = path.read_bytes()
    return {'intervals': intervals, 'onset_samples': starts,
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    output = Path(__file__).parent / 'results'
    output.mkdir(exist_ok=True)
    receipt = {name: render(intervals, output / (name+'.wav'))
               for name, intervals in SCORES.items()}
    assert receipt['observed-flat']['sha256'] == receipt['observed-ramp']['sha256']
    assert receipt['nominal-flat']['sha256'] != receipt['nominal-ramp']['sha256']
    assert receipt['curvature']['sha256'] != receipt['observed-flat']['sha256']
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
