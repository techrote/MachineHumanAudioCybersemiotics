"""Synthetic token circulation and original stereo sound art; standard library only."""
from itertools import permutations, product
from pathlib import Path
import hashlib, math, struct, wave


def replay(n, schedule, keep):
    """keep: sites that send their original token instead of forwarding arrival."""
    held = [{i} for i in range(n)]
    for i in schedule:
        j = (i + 1) % n
        if i in keep:
            token = i
        else:
            assert len(held[i] - {i}) == 1
            token = next(iter(held[i] - {i}))
        assert token in held[i] and token not in held[j]
        held[i].remove(token)
        held[j].add(token)
    assert all(len(h) == 1 for h in held)
    return tuple(next(iter(h)) for h in held)


def predicted(n, keep):
    # Original tokens travel to the next site that sends its own token.
    result = list(range(n))
    sites = sorted(keep)
    for i, j in zip(sites, sites[1:] + sites[:1]):
        result[j] = i
    return tuple(result)


def qualify():
    for n in range(2, 8):
        schedules = outcomes = 0
        histogram = {}
        for schedule in permutations(range(n)):
            pos = {v: k for k, v in enumerate(schedule)}
            forced = {i for i in range(n) if pos[i] < pos[(i - 1) % n]}
            flexible = sorted(set(range(n)) - forced)
            observed = set()
            for bits in product((0, 1), repeat=len(flexible)):
                keep = forced | {i for i, bit in zip(flexible, bits) if bit}
                got = replay(n, schedule, keep)
                assert got == predicted(n, keep)
                assert sorted(got) == list(range(n))
                assert got not in observed
                observed.add(got)
            assert len(observed) == 2 ** len(flexible)
            histogram[len(observed)] = histogram.get(len(observed), 0) + 1
            schedules += 1
            outcomes += len(observed)
        assert min(histogram) == 2 and max(histogram) == 2 ** (n - 1)
        print(n, schedules, outcomes, sorted(histogram.items()))
    # Negative control: a site cannot forward an arrival before it receives it.
    try:
        replay(3, (0, 1, 2), {1, 2})
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted impossible forwarding')


def render(folder):
    folder.mkdir(parents=True, exist_ok=True)
    rate = 16000
    gains = [(3, 1), (2, 2), (1, 3)]
    pitch = [(0, 4, 7, 4), (12, 9, 5, 9), (7, 2, 10, 2)]
    frames = 4 * rate
    reference = None
    files = []
    for bits in product((0, 1), repeat=2):
        keep = {0} | {i for i, bit in zip((1, 2), bits) if bit}
        owners = replay(3, (0, 1, 2), keep)
        pcm = bytearray()
        mono = bytearray()
        for k in range(frames):
            t = k / rate
            if t < 1:
                # Fixed handoff receipts at 0.1, 0.4 and 0.7 seconds.
                d = t - (0.1 + 0.3 * min(2, int(t / 0.3)))
                v = round(900 * math.sin(2 * math.pi * 880 * d) * math.exp(-80 * d)) if 0 <= d < .08 else 0
                l = r = v
            else:
                q = (t - 1) / .75
                event = min(3, int(q))
                d = (t - 1) - event * .75
                env = max(0, min(1, d / .025, (.75 - d) / .06))
                motif = [round(500 * env * math.sin(2 * math.pi * 220 * 2 ** (p[event] / 12) * d)) for p in pitch]
                l = sum(gains[i][0] * motif[token] for i, token in enumerate(owners))
                r = sum(gains[i][1] * motif[token] for i, token in enumerate(owners))
            assert max(abs(l), abs(r), abs(l + r)) < 32768
            pcm.extend(struct.pack('<hh', l, r))
            mono.extend(struct.pack('<h', l + r))
        if reference is None:
            reference = bytes(mono)
        assert mono == reference
        name = 'keep-' + ''.join(map(str, bits)) + '.wav'
        files.append((name, 2, bytes(pcm)))
        print(name, 'final tokens by seat', owners)
    assert len({payload for _, _, payload in files}) == 4
    files.append(('invariant-mono-sum.wav', 1, reference))
    for name, channels, payload in files:
        path = folder / name
        with wave.open(str(path), 'wb') as f:
            f.setparams((channels, 2, rate, frames, 'NONE', 'not compressed'))
            f.writeframes(payload)
        with wave.open(str(path), 'rb') as f:
            assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (channels, 2, rate, frames)
            assert f.readframes(frames) == payload
        print(name, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    qualify()
    render(Path(__file__).resolve().parent / 'audio')
