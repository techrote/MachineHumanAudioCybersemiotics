"""Original integer timbre score and finite tolerance-chain oracle. No listener model."""
import argparse
import hashlib
import io
import json
import struct
import wave
from pathlib import Path

MAX = 8
RATE = 16000
TONE = 4480
GAP = 640
FADE = 160

def valid(x):
    if type(x) is not int or not 0 <= x <= MAX:
        raise ValueError("patch must be an integer from 0 to 8")
    return x

def distance(a, b):
    return abs(valid(a) - valid(b))

def component(points, start, radius):
    points = set(map(valid, points))
    valid(start)
    if radius < 0 or start not in points:
        raise ValueError("bad radius or missing anchor")
    seen = {start}
    while True:
        nxt = seen | {x for x in points if any(distance(x,y) <= radius for y in seen)}
        if nxt == seen:
            return sorted(seen)
        seen = nxt

def analyze(path, radius=1, budget=3):
    path = list(map(valid,path))
    if not path or radius < 0 or budget < 0:
        raise ValueError("empty path or negative limit")
    steps = [distance(a,b) for a,b in zip(path,path[1:])]
    anchor = [distance(path[0],x) for x in path]
    return dict(path=path, radius=radius, budget=budget, steps=steps,
                all_local=all(d <= radius for d in steps),
                anchor_distances=anchor, endpoint_distance=anchor[-1],
                max_anchor_distance=max(anchor), path_length=sum(steps),
                anchor_pass=all(d <= radius for d in anchor),
                budget_pass=sum(steps) <= budget)

def triangle(phase):
    # integer, zero-centred triangle with 80-sample period
    p = phase % 80
    return 10000 - 500 * abs(p - 40)

def sample(index, mix):
    valid(mix)
    envelope = min(index, TONE-1-index, FADE)
    a = triangle(index)
    b = triangle(3*index)
    return ((MAX-mix)*a + mix*b)*envelope // (MAX*FADE)

def render(path):
    """Stereo: left migrates; right always sounds the first patch."""
    path = list(map(valid,path))
    if not path:
        raise ValueError("empty score")
    buf = io.BytesIO()
    with wave.open(buf,"wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        for patch in path:
            frames = bytearray()
            for i in range(TONE):
                frames.extend(struct.pack("<hh",sample(i,patch),sample(i,path[0])))
            out.writeframesraw(frames + bytes(4*GAP))
    return buf.getvalue()

PATHS = {
    "migration": list(range(9)),
    "closed_excursion": [0,1,2,3,2,1,0],
    "bounded": [0,1,0,1],
    "disconnected_jump": [0,1,8],
    "constant": [0,0,0],
}

def report():
    data = {}
    for name,path in PATHS.items():
        wav = render(path)
        data[name] = dict(**analyze(path), wav_sha256=hashlib.sha256(wav).hexdigest(),
                          wav_bytes=len(wav))
    return dict(cases=data, connected=component(range(9),0,1),
                disconnected=component([0,1,7,8],0,1))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.out:
        args.out.mkdir(parents=True,exist_ok=True)
        for name,path in PATHS.items():
            (args.out/(name+".wav")).write_bytes(render(path))
        (args.out/"report.json").write_text(json.dumps(report(),indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report(),sort_keys=True))

if __name__ == "__main__":
    main()
