"""Refs #607: deterministic offline viewer of frozen v42 and independent receipts."""
import base64
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
PINS = {
    'seed71/receipt.json': '994ee9bfc323b049d83bf2c3bd015529b244c755f17dc835649eac951f3d5ded',
    'seed113/receipt.json': '7ee5b3534f354db9b5e7f4ec70b611181e1828a25fe996ada4a3548b557df9fb',
    'receipt.json': 'a0563a0dd916107c5c916af7f76335a83d5fb8645c15ef47f39b7199a50ced40',
    'process-cut-receipt.json': '371db05a28bdf6ada45041dad6c58213f174c865624791edb24394eec9363131',
}
TEMPLATE = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MHAC 004 | Witness boundary</title>
<style>body{font:16px system-ui,sans-serif;background:#101820;color:#e4edf4;margin:24px;max-width:1100px}h1,h2{color:#a8e3e1}button,select,input{font:inherit;margin:5px;padding:6px;max-width:95%}pre{background:#1d2b36;padding:14px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:35em;overflow:auto}section{border:1px solid #506473;padding:14px;margin:14px 0}label{display:inline-block}p{max-width:80ch}button:focus,select:focus{outline:3px solid #a8e3e1}</style>
<h1>MHAC 004: Witnessed journal</h1>
<p>Synthetic evidence only. Single writer, public fixture keys, simulated independent witness. Joint rollback admits replay; process termination is not power-loss qualification. No physical audition or human comprehension evidence. Windows persistence not qualified.</p>
<label>Evidence <select id="evidence"></select></label><button id="export">Export original JSON</button>
<label>Scenario <select id="scenario"></select></label><label>Trace event <select id="event"></select></label>
<button id="prev">Previous</button><button id="next">Next</button>
<section id="audioPanel"><h2>Original session PCM</h2><audio id="audio" preload="none"></audio><button id="play">Play</button><button id="pause">Pause</button><button id="stop">Stop</button><label>Digital gain % <input id="gain" type="range" min="0" max="25" value="12"></label><output id="gainValue">12%</output><p>Manual playback; start with low system volume. No calibrated acoustic level. The viewer slider is capped at 25%.</p></section>
<section><h2>Commit and decision</h2><p id="summary"></p><pre id="detail"></pre></section>
<section><h2>Final recorded state / recovery receipt</h2><pre id="final"></pre></section>
<script id="payload" type="application/json">PAYLOAD</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('payload').textContent), el=id=>document.getElementById(id);
const evidence=el('evidence'),scenario=el('scenario'),event=el('event'),audio=el('audio');
const pretty=x=>JSON.stringify(x,null,2), current=()=>data[Number(evidence.value)], row=()=> (current().parsed.rows||current().parsed.results)[Number(scenario.value)];
function options(select,items){select.replaceChildren();items.forEach((s,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=s;select.append(o);});}
function stop(){audio.pause();if(audio.readyState)audio.currentTime=0;}
function update(){const r=row(), t=r.trace?.[Number(event.value)];el('summary').textContent=t?[t.label,'local '+t.local.commit,'witness '+t.witness.commit,typeof t.result==='string'?t.result:JSON.stringify(t.result)].join(' | '):[r.name||r.cut,r.retry||r.error||'see receipt'].join(' | ');el('detail').textContent=pretty(t||r);el('final').textContent=pretty(r.final??r);el('prev').disabled=!t||Number(event.value)===0;el('next').disabled=!t||Number(event.value)===r.trace.length-1;}
function chooseScenario(){stop();const r=row();options(event,r.trace?.map(t=>t.label+(t.role?' / '+t.role:''))||['Independent receipt']);event.disabled=!r.trace;el('audioPanel').hidden=!r.file;audio.removeAttribute('src');if(r.file)audio.src=current().path.split('/')[0]+'/'+r.file;audio.load();audio.volume=Number(el('gain').value)/100;update();}
function chooseEvidence(){options(scenario,(current().parsed.rows||current().parsed.results).map(r=>[r.seed,r.name||r.cut,r.policy].filter(x=>x!==undefined).join(' / ')));chooseScenario();}
options(evidence,data.map(d=>d.path));evidence.onchange=chooseEvidence;scenario.onchange=chooseScenario;event.onchange=update;el('prev').onclick=()=>{event.selectedIndex--;update();};el('next').onclick=()=>{event.selectedIndex++;update();};el('stop').onclick=stop;el('play').onclick=()=>audio.play().catch(e=>{el('summary').textContent='Playback error: '+e.message;});el('pause').onclick=()=>audio.pause();el('gain').oninput=()=>{audio.volume=Number(el('gain').value)/100;el('gainValue').textContent=el('gain').value+'%';};
el('export').onclick=()=>{const d=current(),bytes=Uint8Array.from(atob(d.base64),c=>c.charCodeAt(0)),url=URL.createObjectURL(new Blob([bytes],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=d.path.replace('/','-');a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);};
chooseEvidence();
</script></html>
'''


def main():
    subprocess.run([sys.executable, '-B', str(ROOT / 'audit_corpus.py')], check=True)
    payload = []
    for name, digest in PINS.items():
        p = ROOT / name
        raw = p.read_bytes()
        if p.is_symlink() or hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f'evidence digest mismatch: {name}')
        payload.append(dict(path=name, parsed=json.loads(raw), base64=base64.b64encode(raw).decode('ascii')))
    encoded = json.dumps(payload, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    html = TEMPLATE.replace('PAYLOAD', encoded).encode('utf-8')
    target = ROOT / 'index.html'
    if sys.argv[1:] == ['--check']:
        if target.read_bytes() != html:
            raise ValueError('generated inspector mismatch')
    elif not sys.argv[1:]:
        target.write_bytes(html)
    else:
        raise SystemExit('usage: inspect_journal.py [--check]')
    print('inspector: 4 pinned receipts; 28 sessions; 20 logical + 8 process-cut cases')


if __name__ == '__main__':
    main()
