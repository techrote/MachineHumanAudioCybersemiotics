"""Build an offline v40 evidence viewer from two exact reproduced receipts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

PINS = {
    'seed71/receipt.json': 'e4c68135b9b6381803461677a39b410968aa78eb237315d5bd1532c7b5c097a9',
    'seed113/receipt.json': 'cb6b6bff77eac3163159ec1f22083a372604b7b418c386db0c1abcdaf926aed1',
    'controls.json': 'b5e855b68aa12a6da31c947e8d3627cebbd315b740a939b3e700f95574466772',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def build(root):
    payload = {}
    for name, digest in PINS.items():
        require(not (root / name).is_symlink(), 'receipt symlink')
        raw = (root / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, 'receipt hash: ' + name)
        payload[name] = base64.b64encode(raw).decode('ascii')
        if name == 'controls.json':
            continue
        directory = (root / name).parent
        rows = json.loads(raw)['rows']
        expected = {'receipt.json'}
        require(len(rows) == 12, 'session count')
        for row in rows:
            filename = row['file']
            require(Path(filename).name == filename and filename.endswith('.wav') and filename not in expected, 'WAV name')
            wav = directory / filename
            require(not wav.is_symlink() and hashlib.sha256(wav.read_bytes()).hexdigest() == row['sha256'], 'WAV hash: ' + filename)
            expected.add(filename)
        require({p.name for p in directory.iterdir()} == expected, 'seed inventory')
    return TEMPLATE.replace('PAYLOAD_PLACEHOLDER', json.dumps(payload, sort_keys=True, separators=(',', ':'))).encode('utf-8')


TEMPLATE = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MHAC Integration 003 — evidence inspector</title>
<style>
:root{color-scheme:dark}body{max-width:1100px;margin:2rem auto;padding:0 1rem;background:#101820;color:#e4edf3;font:16px system-ui}h1,h2{line-height:1.2}fieldset{border:1px solid #587080;margin:1rem 0;padding:1rem}label,button,select{margin:.4rem}button,select{font:inherit;padding:.35rem}pre{background:#1a2833;padding:1rem;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:1rem}audio{max-width:100%}.warning{color:#ffcc8a}
</style>
<h1>Integration 003 / authenticated session</h1>
<p>Frozen v40 synthetic evidence. A valid MAC is not proof of truth or freshness. Decoder outputs and sender beliefs are distinct from receiver state. No human comprehension, device actuation or power-loss durability is established.</p>
<fieldset><legend>Session and slot</legend><label>Session <select id="session"></select></label><label>Slot <select id="slot"></select></label><button id="prev">Previous</button><button id="next">Next</button><p id="location"></p></fieldset>
<fieldset><legend>Original PCM (opt-in)</legend><p class="warning">Start at low system volume. Digital gain defaults to 12%, ceiling 25%; not calibrated SPL. Play manually.</p><audio id="audio" preload="none"></audio><button id="play">Play</button><button id="pause">Pause</button><label>Gain <input id="gain" type="range" min="0" max="25" value="12"><output id="gainvalue">12%</output></label><button id="stop">Stop</button></fieldset>
<button id="export">Download exact original seed receipt</button><button id="controls">Download original role controls</button>
<section><div><h2>Transmission and decoder</h2><pre id="decode"></pre></div><div><h2>Receiver admission and state</h2><pre id="state"></pre></div><div><h2>Sender beliefs and pending</h2><pre id="beliefs"></pre></div><div><h2>Final outcomes and metrics</h2><pre id="metrics"></pre></div></section>
<script id="payload" type="application/json">PAYLOAD_PLACEHOLDER</script>
<script>
'use strict';
const $=id=>document.getElementById(id);
const payload=JSON.parse($('payload').textContent);
const bytes=key=>Uint8Array.from(atob(payload[key]),c=>c.charCodeAt(0));
const rows=Object.keys(payload).filter(k=>k.includes('/')).sort().flatMap(key=>JSON.parse(new TextDecoder().decode(bytes(key))).rows.map(row=>({key,row})));
const show=(id,value)=>{$(id).textContent=JSON.stringify(value,null,2);};
const option=(value,label)=>new Option(label,value);
const audio=$('audio'); audio.volume=.12;
function stop(){audio.pause();audio.currentTime=0;}
function slot(){const {row}=rows[+$('session').value];const t=row.trace[+$('slot').value];$('location').textContent=`Slot ${t.t} | ${(t.start/16000).toFixed(3)} s | ${row.file}`;show('decode',{job:t.job,fault:t.fault,decoded:t.decoded});show('state',{decision:t.decision,state:t.state});show('beliefs',{beliefs:t.beliefs,pending:t.pending});show('metrics',{result:row.result,metrics:row.metrics});$('prev').disabled=+$('slot').value===0;$('next').disabled=+$('slot').value===row.trace.length-1;}
function session(){const {key,row}=rows[+$('session').value];stop();audio.src=key.split('/')[0]+'/'+row.file;$('slot').replaceChildren(...row.trace.map((t,i)=>option(i,`Slot ${t.t}`)));slot();}
function download(key){const url=URL.createObjectURL(new Blob([bytes(key)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=key.replace('/','-');document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);}
$('session').replaceChildren(...rows.map(({row},i)=>option(i,`${row.seed} / ${row.name} / ${row.bits?`HMAC${row.bits}`:'public checksum'}`)));
$('session').onchange=session;$('slot').onchange=slot;$('prev').onclick=()=>{$('slot').selectedIndex--;slot();};$('next').onclick=()=>{$('slot').selectedIndex++;slot();};$('gain').oninput=()=>{audio.volume=+$('gain').value/100;$('gainvalue').textContent=$('gain').value+'%';};$('play').onclick=()=>audio.play().catch(e=>{$('location').textContent='Playback refused: '+e.message;});$('pause').onclick=()=>audio.pause();$('stop').onclick=stop;$('export').onclick=()=>download(rows[+$('session').value].key);$('controls').onclick=()=>download('controls.json');session();
</script></html>
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    generated = build(args.root)
    output = args.root / 'index.html'
    if args.check:
        require(output.read_bytes() == generated, 'inspector bytes')
    else:
        output.write_bytes(generated)
    print('verified 3 receipts and 24 WAVs; inspector SHA256', hashlib.sha256(generated).hexdigest())


if __name__ == '__main__':
    main()
