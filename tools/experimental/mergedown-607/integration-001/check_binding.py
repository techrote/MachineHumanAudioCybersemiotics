"""Independent aligned PCM audit of the frozen #513 v2 binding witnesses.
Not a blind acquisition test or an authenticity claim. Standard library only.
"""
import hashlib
import itertools
import json
import math
import sys
import wave
from pathlib import Path

PIN = '8fc53c22966b27e3ec62519271471431fe3b10b0f404c93f9ed9a57121ca450a'
VOCAB = 'fault open stopped overload not quote question verify pump-reports relay-reports uncertain and if end'.split()
FIELDS = 'kind source version actor event seq'.split()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repair(words):
    """Solve two parity equations directly; no enumeration of candidate words."""
    w = list(words)
    missing = [i for i, x in enumerate(w) if x is None]
    if len(w) != 8 or len(missing) > 2:
        return None
    a = -sum(x for x in w if x is not None) % 17
    b = -sum((i + 1) * x for i, x in enumerate(w) if x is not None) % 17
    if len(missing) == 2:
        i, j = missing
        w[j] = (b - (i + 1) * a) * pow(j - i, -1, 17) % 17
        w[i] = (a - w[j]) % 17
    elif missing:
        w[missing[0]] = a
    return w if sum(w) % 17 == sum((i + 1) * x for i, x in enumerate(w)) % 17 == 0 else None


def packet(words):
    m, b = repair(words[:8]), repair(words[8:16])
    if m is None or b is None or m[0] > 1 or min(m[1:6]) < 1:
        return None, None
    n = b[0] + 1
    if not 1 <= n <= 4 or any(x != 13 for x in b[n + 1:6]):
        return None, None
    # Parse prefix tokens backwards with a stack, rather than recursive descent.
    stack = []
    for x in reversed(b[1:n + 1]):
        arity = 0 if x < 4 else 1 if x < 11 else 2
        if x >= 13 or len(stack) < arity:
            return None, None
        stack.append([VOCAB[x], *[stack.pop() for _ in range(arity)]])
    if len(stack) != 1:
        return None, None
    return dict(zip(FIELDS, m[:6]), tree=stack[0]), m + b


def tag(frame):
    h = hashlib.sha256(b'MHAC-relay-v2\0' + bytes(frame)).digest()
    n = int.from_bytes(h[:4], 'big') % 17**6
    return [(n // 17**i) % 17 for i in range(6)]


# Central 40 ms of each 80 ms symbol; integer-bin DFT power, not upstream normalized score.
BANK = [(tuple(math.cos(math.tau * f * i / 16000) for i in range(640)),
         tuple(math.sin(math.tau * f * i / 16000) for i in range(640)))
        for f in range(400, 2001, 100)]


def symbol(x):
    energy = sum(v*v for v in x)
    if energy < 640 * 250**2:
        return None
    power = [sum(v*c for v, c in zip(x, a))**2 + sum(v*c for v, c in zip(x, b))**2 for a,b in BANK]
    order = sorted(range(17), key=power.__getitem__, reverse=True)
    p, q = (power[i] for i in order[:2])
    # Independent conservative dominance criterion; valid for these aligned fixtures only.
    return order[0] if p > 4*q and p > 0.35*640*energy else None


def decode(samples):
    start = 256 + 640 + 160  # known fixture offset, no preamble acquisition
    words = [symbol(samples[start+1280*i:start+1280*i+640]) for i in range(24)]
    p, frame = packet(words)
    t = repair(words[16:])
    return p, p if p is not None and t is not None and t[:6] == tag(frame) else None, words


def audit(root):
    path = root / 'receipt.json'
    require(digest(path) == PIN, 'frozen receipt mismatch')
    r = json.loads(path.read_text())
    rows = {x['name']: x for x in r['rows']}
    sessions = {x['policy']: x for x in r['sessions']}
    require({p.name for p in root.glob('*.wav')} == {x['file'] for x in r['stimuli']}, 'WAV inventory')
    counts = dict(wavs=0, aligned_slots=0, v1_packets=0, v2_packets=0, parity_pairs=0)
    for spec in r['stimuli']:
        p = root / spec['file']
        require(digest(p) == spec['sha256'], 'WAV digest: '+p.name)
        with wave.open(str(p), 'rb') as f:
            require((f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (1,2,16000,spec['samples']), 'WAV format')
            data = f.readframes(f.getnframes())
        import struct
        pcm = struct.unpack('<'+'h'*(len(data)//2), data)
        require(max(map(abs, pcm)) == spec['peak'] <= 8192, 'peak')
        counts['wavs'] += 1
        for i in range(0,len(pcm),32000):
            a,b,words = decode(pcm[i:i+32000])
            counts['aligned_slots'] += 1
            counts['v1_packets'] += a is not None
            counts['v2_packets'] += b is not None
            if p.stem in rows:
                row = rows[p.stem]
                require(([a] if a else []) == row['v1'] and ([b] if b else []) == row['v2'], 'witness decode '+p.name)
            else:
                slot = sessions[p.stem]['trace'][i//32000]
                expected = [h['packet'] for h in slot['hits'] if h['status']=='ok']
                require(([b] if b else []) == expected, 'slot decode '+p.name)
            if p.stem == 'clean':
                for offset in (0,8,16):
                    block = words[offset:offset+8]
                    for j,k in itertools.combinations(range(8),2):
                        erased = block.copy()
                        erased[j] = erased[k] = None
                        require(repair(erased) == block, 'two erasures')
                        counts['parity_pairs'] += 1
    # Independently recount fresh ACKs against configured context and preceding sends.
    for name,s in sessions.items():
        sent, received, confirmed = set(), set(), set()
        fresh = 0
        key = lambda p: json.dumps(dict(p,kind=0),sort_keys=True)
        for row in s['trace']:
            if row['tx'] and row['tx']['kind']==0:
                sent.add(key(row['tx']))
            for event in row['events']:
                p = event['packet']; k = key(p)
                current = p['version'] == row['current'][str(p['source'])]
                if event['type']=='data':
                    require(event['accepted']==current,'data context')
                    if current: received.add(k)
                else:
                    accepted = k in sent and k not in confirmed
                    require(event['accepted']==accepted and event['fresh']==current,'ack decision')
                    if accepted:
                        confirmed.add(k); fresh += int(current)
        require((len(received),len(confirmed),fresh)==(s['received'],s['confirmed'],s['fresh']),'session accounting')
    return counts


if __name__ == '__main__':
    print(json.dumps(audit(Path(sys.argv[1])),sort_keys=True))
