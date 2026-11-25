"""Synthetic countermonument instrument, no participant data or device control."""
import hashlib
import itertools
import math
from pathlib import Path
import wave
import struct

RULES = {('M', 'offer'): 'O', ('O', 'decline'): 'M',
         ('O', 'accept'): 'G', ('M', 'withdraw'): 'V',
         ('O', 'withdraw'): 'V', ('G', 'release'): 'V'}
ACTIONS = ('offer', 'decline', 'accept', 'withdraw', 'release')


def step(state, seat, action):
    if not 0 <= seat < len(state) or (state[seat], action) not in RULES:
        raise ValueError('ineligible transition')
    return state[:seat] + (RULES[state[seat], action],) + state[seat+1:]


def machine(state):
    return sum(s in 'MO' for s in state)


def qualify():
    frontier = {('M',) * 3}
    visited = set(frontier)
    valid = invalid = 0
    for _ in range(7):
        next_states = set()
        for state, seat, action in itertools.product(frontier, range(3), ACTIONS):
            try:
                result = step(state, seat, action)
            except ValueError:
                invalid += 1
                assert (state[seat], action) not in RULES
                continue
            valid += 1
            assert machine(result) <= machine(state)
            assert result[seat] == RULES[state[seat], action]
            assert all(result[i] == state[i] for i in range(3) if i != seat)
            assert state[seat] != 'G' or action == 'release'
            assert state[seat] != 'V'
            next_states.add(result)
        visited |= next_states
        frontier = next_states
    assert visited == set(itertools.product('MOGV', repeat=3))
    assert step(step(('M',), 0, 'offer'), 0, 'decline') == ('M',)
    assert step(('M',), 0, 'withdraw') == ('V',)
    return len(visited), valid, invalid


SCENES = {
    'invitation': [(0, 'offer'), (0, 'decline'), (1, 'offer'), (1, 'decline')],
    'handoff': [(0, 'offer'), (0, 'accept'), (1, 'offer'), (1, 'accept')],
    'vacancy': [(0, 'withdraw'), (1, 'withdraw'), (2, 'offer'), (2, 'decline')],
    'release': [(0, 'offer'), (0, 'accept'), (0, 'release'), (1, 'withdraw')],
}
RATE = 16000
FRAMES = 8000


def render(events):
    state = ('M',) * 3
    states = [state]
    for seat, action in events:
        state = step(state, seat, action)
        states.append(state)
    samples = []
    for state in states:
        for i in range(FRAMES):
            t = i / RATE
            env = min(1, i / 240, (FRAMES-1-i) / 240)
            value = 0.0
            for seat, role in enumerate(state):
                f = (165, 220, 330)[seat]
                if role in 'MO':
                    value += 0.12 * math.sin(2*math.pi*f*t)
                elif role == 'G':
                    value += 0.12 * math.sin(2*math.pi*f*1.5*t) * (0.65+0.35*math.cos(2*math.pi*4*t))
            sample = round(32767 * env * value)
            assert abs(sample) <= 12000
            samples.append(sample)
    return struct.pack('<' + 'h'*len(samples), *samples), states


def main():
    print('reachable states, valid/invalid transition checks:', qualify())
    audio = Path(__file__).parent / 'audio'
    audio.mkdir(exist_ok=True)
    for name, events in SCENES.items():
        pcm, states = render(events)
        assert pcm == render(events)[0]
        path = audio / (name + '.wav')
        with wave.open(str(path), 'wb') as w:
            w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            w.writeframes(pcm)
        with wave.open(str(path), 'rb') as w:
            assert w.getparams()[:4] == (1, 2, RATE, 5*FRAMES)
            assert w.readframes(5*FRAMES) == pcm
        print(name, [''.join(s) for s in states], hashlib.sha256(path.read_bytes()).hexdigest())
    assert render(SCENES['invitation'])[0][:FRAMES*2] == render(SCENES['invitation'])[0][FRAMES*2:FRAMES*4]
    assert render(SCENES['handoff'])[0] != render(SCENES['vacancy'])[0]
    print('PASS: repeat, readback, invitation invariance, handoff/vacancy distinction')


if __name__ == '__main__':
    main()
