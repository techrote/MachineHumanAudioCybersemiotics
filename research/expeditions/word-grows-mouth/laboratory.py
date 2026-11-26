"""Synthetic articulation score; no speech or perceptual model. Python >=3.11."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import wave

RATE = 24000
N = 28800
GAP = 4800
GESTURES = ("unfurl", "knuckle", "coil")
# (base Hz, partial ratios, octave excursion, brightness inversion)
BODIES = {
    "reed": (165, (1, 2, 3, 4, 5, 6), 1.0, False),
    "plate": (220, (1, 1.414, 2.16, 2.91, 4.07, 5.43), 0.75, False),
    "inverse": (260, (1, 1.5, 2.5, 3.7, 5.1, 6.2), -1.0, True),
}


def gesture(name, u):
    if not 0 <= u <= 1:
        raise ValueError("normalized time outside [0,1]")
    if name == "unfurl":
        x = u*u*(3-2*u)
        e = 0.65 + 0.35*u
    elif name == "knuckle":
        x = 0.5 + 0.42*math.sin(6*math.pi*u)
        e = 0.12 + 0.88*math.sin(3*math.pi*u)**4
    elif name == "coil":
        x = 0.5 + 0.45*math.sin(2*math.pi*(u+2*u*u))
        e = 0.7 + 0.3*math.cos(2*math.pi*u)**2
    else:
        raise ValueError("unknown gesture")
    return x, e


def parameters(body, x):
    base, ratios, span, invert = BODIES[body]
    root = base * 2**(span*(x-0.5))
    brightness = 1-x if invert else x
    weights = [math.exp(-((j-5*brightness)/1.75)**2)/(1+0.12*j)
               for j in range(len(ratios))]
    return [root*r for r in ratios], [w/sum(weights) for w in weights]


def render(name, body):
    phases = [0.0]*len(BODIES[body][1])
    samples = []
    for i in range(N):
        u = i/(N-1)
        x, e = gesture(name, u)
        freqs, weights = parameters(body, x)
        assert min(freqs) > 0 and max(freqs) < RATE/2
        for j, f in enumerate(freqs):
            phases[j] = (phases[j] + math.tau*f/RATE) % math.tau
        edge = min(1.0, i/480, (N-1-i)/480)
        y = 0.65 * e * edge * sum(w*math.sin(p) for w,p in zip(weights,phases))
        samples.append(round(32767*y))
    assert samples[0] == samples[-1] == 0
    assert max(map(abs,samples)) <= round(0.65*32767)
    return struct.pack(f"<{len(samples)}h", *samples)


def write_checked(path, pcm):
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        out.writeframes(pcm)
    with wave.open(str(path), "rb") as back:
        assert (back.getnchannels(), back.getsampwidth(), back.getframerate()) == (1, 2, RATE)
        assert back.getnframes() == len(pcm)//2
        assert back.readframes(back.getnframes()) == pcm
    return {"frames":len(pcm)//2,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "peak_pcm":max(map(abs,struct.unpack(f"<{len(pcm)//2}h",pcm)))}


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    cells, files = {}, {}
    checks = 0
    for g in GESTURES:
        for body in BODIES:
            pcm = render(g,body)
            assert pcm == render(g,body)
            cells[g,body] = pcm
            name = f"{g}-{body}.wav"
            files[name] = write_checked(out/name,pcm)
    assert len(set(cells.values())) == 9
    # The same x trajectory is sent to every body. This is a model-level check,
    # not recovered acoustic pitch or evidence of listener recognition.
    for g in GESTURES:
        for i in range(1001):
            x,e = gesture(g,i/1000)
            assert 0 <= x <= 1 and 0 <= e <= 1
            for b, (base,ratios,span,invert) in BODIES.items():
                f,w = parameters(b,x)
                recovered = math.log2(f[0]/base)/span+0.5
                assert abs(recovered-x) < 1e-12
                assert abs(sum(w)-1) < 1e-12 and min(w)>=0
                assert max(f)<RATE/2
                checks += 1
    ratios = {b:parameters(b,1)[0][0]/parameters(b,0)[0][0] for b in BODIES}
    assert ratios["reed"] > 1 and ratios["plate"] > 1 and ratios["inverse"] < 1
    try:
        gesture("unfurl",1.01)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid time accepted")
    for body in BODIES:
        pcm = (b"\x00\x00"*GAP).join(cells[g,body] for g in GESTURES)
        name = f"lexicon-{body}.wav"
        files[name] = write_checked(out/name,pcm)
    # A single gesture traversing three different resonant bodies.
    pcm = (b"\x00\x00"*GAP).join(cells["unfurl",b] for b in BODIES)
    files["three-mouths.wav"] = write_checked(out/"three-mouths.wav",pcm)
    receipt = {"python":sys.version.split()[0],"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "model_parameter_comparisons":checks,"distinct_cells":len(set(cells.values())),
               "unfurl_end_start_first_partial_ratios":ratios,"files":files,
               "limits":"Synthetic additive trajectories; no listener or speech validation."}
    (out.parent/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/"audio")
