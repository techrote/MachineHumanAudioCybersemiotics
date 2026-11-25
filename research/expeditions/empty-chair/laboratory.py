"""Offline original sound-art miniature; no messaging or real recipients."""
import hashlib
import math
import struct
import wave
from pathlib import Path

RATE = 16000
FRAMES = RATE * 6
CALL = (220, 330, 294, 392, 247)
# title, invoked object, reply contract, return provenance, return score
CASES = (
    ('invocation', 'empty chair', 'none', 'none', ()),
    ('unanswered', 'fictional correspondent', 'required', 'none', ()),
    ('reflection', 'stone', 'none', 'local delay copy', CALL),
    ('staged-reply', 'fictional correspondent', 'required', 'scripted reply', CALL),
    ('witness-variation', 'future archive', 'optional', 'scripted witness', (247, 294, 330, 220, 196)),
)


def phrase(notes):
    out = []
    for f in notes:
        for i in range(RATE // 4):
            t = i / RATE
            env = min(1, i / 160, (RATE // 4 - 1 - i) / 320) * math.exp(-3*t)
            out.append(round(3600 * env * (math.sin(2*math.pi*f*t) + .23*math.sin(2*math.pi*f*2.01*t))))
    return out


def render(case):
    _, _, _, _, answer = case
    out = [0] * FRAMES
    call = phrase(CALL)
    out[RATE//2:RATE//2+len(call)] = call
    if answer:
        reply = phrase(answer)
        out[3*RATE:3*RATE+len(reply)] = reply
    assert len(out) == FRAMES and max(map(abs, out)) < 32768
    return struct.pack('<'+'h'*FRAMES, *out)


def classify(contract, provenance, deadline_passed):
    # Only stipulated fixture facts, never inferred from an acoustic waveform.
    if provenance in ('scripted reply', 'scripted witness'):
        return 'staged response (not verified uptake)'
    if contract == 'none':
        return 'no reply requested'
    if contract == 'optional':
        return 'optional reply absent'
    return 'required reply absent' if deadline_passed else 'awaiting required reply'


def main():
    output = Path(__file__).resolve().parent / 'audio'
    output.mkdir(exist_ok=True)
    rendered = {}
    for case in CASES:
        name, target, contract, provenance, _ = case
        pcm = render(case)
        assert pcm == render(case)
        path = output / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, FRAMES, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, RATE, FRAMES)
            assert w.readframes(FRAMES) == pcm
        rendered[name] = path.read_bytes()
        print(name, hashlib.sha256(rendered[name]).hexdigest(), '|', target, '|', classify(contract, provenance, True))
    assert rendered['invocation'] == rendered['unanswered']
    assert rendered['reflection'] == rendered['staged-reply']
    assert len(set(rendered.values())) == 3
    assert classify('required', 'local delay copy', True) == 'required reply absent'
    assert classify('required', 'none', False) == 'awaiting required reply'
    assert classify('none', 'none', True) == 'no reply requested'
    assert classify('optional', 'none', True) == 'optional reply absent'
    print('PASS: five reproducible files; three distinct byte sequences; two collision pairs; four negative/status controls.')


if __name__ == '__main__':
    main()
