"""Verify ACCEL-026 session receipts and produce a four-track type-1 MIDI file.
Requires numpy and mido; offline, no plugin execution. Refs #632.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import wave
import zipfile
import mido
import numpy as np

NAMES = ('Afterimage', 'Winter-Latch', 'Winter-Pause', 'Winter-Snapshot')
MODES = ('Legacy', 'Balanced', 'Bypass')
PINS = {'afterimage': '87774d7877810de06d0abb7ecdaff9bd290829c86ebc0cf8639fc5bef62dc089', 'winters': '5de9cae05307d7dd99e7b6b0d665a3a0342d930921e4a160ff91e4cc9e938c89', 'receipt': 'c13a44cfd6bf0a6979b362a8dd057bd7c309e95a467a8f2558c340404b320776'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def events(track):
    tick = 0
    result = []
    for msg in track:
        tick += msg.time
        if msg.type in ('note_on', 'note_off'):
            result.append((tick, msg.type, msg.note, msg.velocity))
    return result


def combine(inputs):
    result = mido.MidiFile(type=1, ticks_per_beat=480)
    result.add_track('Tempo').extend([mido.MetaMessage('set_tempo', tempo=500000), mido.MetaMessage('time_signature', numerator=4, denominator=4), mido.MetaMessage('end_of_track', time=11520)])
    originals = []
    for channel, raw in enumerate(inputs):
        source = mido.MidiFile(file=io.BytesIO(raw))
        require(source.type == 0 and source.ticks_per_beat == 480 and len(source.tracks) == 1, 'source MIDI format')
        require(source.length == 12 and [m.tempo for m in source.tracks[0] if m.type == 'set_tempo'] == [500000], 'source timing')
        track = result.add_track()
        pending = 0
        for msg in source.tracks[0]:
            pending += msg.time
            if msg.type == 'set_tempo':
                continue
            require(msg.type in ('track_name', 'note_on', 'note_off', 'end_of_track'), 'unexpected MIDI event')
            track.append(msg.copy(time=pending, **({'channel': channel} if not msg.is_meta else {})))
            pending = 0
        originals.append(events(source.tracks[0]))
    out = io.BytesIO()
    result.save(file=out)
    decoded = mido.MidiFile(file=io.BytesIO(out.getvalue()))
    require(decoded.type == 1 and len(decoded.tracks) == 5 and decoded.length == 12, 'combined MIDI extent')
    require([events(t) for t in decoded.tracks[1:]] == originals, 'changed note events')
    require(all(m.channel == i for i,t in enumerate(decoded.tracks[1:]) for m in t if not m.is_meta), 'channel mismatch')
    return out.getvalue(), sum(map(len, originals))


def audio(raw):
    with wave.open(io.BytesIO(raw), 'rb') as w:
        require((w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (2,2,48000,576000), 'WAV format')
        x = np.frombuffer(w.readframes(576000), dtype='<i2').astype(np.int32).reshape(-1,2)
    require(np.max(np.abs(x)) <= 8192 and np.any(x), 'WAV bounds')
    require(not np.any(x[:4800]) and not np.any(x[-12000:]), 'WAV silence')
    return x


def verify(z):
    require(z.testzip() is None, 'artifact CRC')
    report = json.loads(z.read('session/session.json'))
    require(report['complete'] is True and report['rate'] == 48000 and report['seconds'] == 12 and report['gains'] == [.5,.125,.125,.125], 'session metadata')
    for key, pin in PINS.items():
        require(report[key]['binary_sha256'] == pin and report[key]['sdk'] == '9fad9770f2ae8542ab1a548a68c1ad1ac690abe0', 'binary/SDK pin')
    cases = {(c['name'],c['block']):c for c in report['cases']}
    require(len(report['cases']) == 14 and set(cases) == {(n,b) for n in NAMES+MODES for b in (257,1024)}, 'case coverage')
    for n in NAMES+MODES:
        a,b = (cases[n,k] for k in (257,1024))
        require(a['restore_error'] == b['restore_error'] == b['partition_error'] == 0 and a['output']['float32_sha256'] == b['output']['float32_sha256'], 'restore/partition')
    for b in (257,1024):
        require(cases['Legacy',b]['oracle_error'] == cases['Bypass',b]['bypass_error'] == 0 and cases['Balanced',b]['contrast'] > 1e-4, 'effect oracle')
    stems = [audio(z.read('session/Stems/'+n+'.wav')) for n in NAMES]
    mixes = {n:audio(z.read('session/Comparisons/'+n+'.wav')) for n in ('Dry','Legacy','Balanced')}
    error = int(np.max(np.abs(sum(stems)-mixes['Dry'])))
    require(error <= 3 and error == report['stem_sum_lsb_error'], 'stem sum')
    midi, count = combine([z.read('session/MIDI/'+n+'.mid') for n in NAMES])
    require(count == 72, 'note count')
    changed = int(np.count_nonzero(mixes['Legacy'] != mixes['Balanced']))
    require(changed > 0, 'effect contrast PCM')
    return midi, dict(cases=len(cases), note_events=count, stem_sum_lsb=error, changed_pcm_words=changed, peaks={n:int(np.max(np.abs(x))) for n,x in mixes.items()})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('artifact',type=Path)
    p.add_argument('output',type=Path)
    a = p.parse_args()
    require(digest(a.artifact.read_bytes()) == 'f301c5f339cdb1e1717ead28e5f46afdb7527b8dbee9f1805527d3c19b02c431', 'published artifact digest')
    with zipfile.ZipFile(a.artifact) as z:
        midi, receipt = verify(z)
    a.output.write_bytes(midi)
    print(json.dumps(receipt, sort_keys=True))
