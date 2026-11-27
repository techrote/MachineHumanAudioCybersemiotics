'use strict';
// Offline read-only viewer for qualified Integration 002 fixtures. Refs #607.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createHash}=require('node:crypto');
const root=path.resolve(process.argv[2]||'.'), evidence=path.join(root,'scheduled-v2-output');
const sha=b=>createHash('sha256').update(b).digest('hex');
const pin='bf6ef5c14903a7211322471e4057d3297c1d58c0cfa955d20abc08dde4e21ff3';
const read=n=>fs.readFileSync(path.join(evidence,n));
const names=fs.readdirSync(evidence).sort();
assert.equal(names.length,91);
assert.ok(names.every(n=>fs.lstatSync(path.join(evidence,n)).isFile()));
assert.equal(sha(names.map(n=>sha(read(n))+'  '+n+'\n').join('')),pin);
const manifest=JSON.parse(read('manifest.json'));
const raw=manifest.rows.map(r=>read(r.name+'-'+r.policy+'.json'));
const sessions=raw.map(b=>JSON.parse(b));
const exportData=raw.map(b=>b.toString('base64'));
assert.equal(sessions.length,45);
assert.equal(new Set(sessions.map(s=>s.name+'-'+s.policy)).size,45);
const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MHAC scheduled PCM — replay</title>
<style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem;background:#151b24;color:#e3e9ef}select,button,input{font:inherit;margin:.3rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#222d3b;padding:1rem}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:.4rem;border-bottom:1px solid #526075}button{cursor:pointer}audio{width:100%}.warn{color:#ffcc91}a{color:#a5d5ff}</style>
<h1>Scheduled PCM: 45-session replay</h1><p>Synthetic frozen fixtures only. Decoded packet, sender confirmation and evaluator genuineness are distinct. Neither authentication nor execution authority is established. The displayed confidence scores are original decoder outputs, not independently estimated.</p>
<label>Session <select id="session"></select></label><label>Slot <select id="slot"></select></label><button id="prev">Previous</button><button id="next">Next</button><p id="summary" class="warn"></p><audio id="audio" controls preload="none"></audio><label>Digital gain <input id="gain" type="range" min="0" max="0.25" step="0.01" value="0.12"></label><output id="gainText">12%</output><button id="stop">Stop</button><p>Start with low device volume. Gain is digital only, not calibrated SPL. Playback is opt-in; changing session stops playback.</p>
<h2>Timeline (2 seconds per slot)</h2><table><thead><tr><th>Slot / seconds</th><th>Origin</th><th>Fault</th><th>Decoder hits</th><th>Events</th></tr></thead><tbody id="timeline"></tbody></table><h2>Selected slot — original witness</h2><pre id="detail"></pre><h2>Session metrics</h2><pre id="metrics"></pre><button id="export">Export original trace JSON</button><p id="exportStatus"></p>
<script id="data" type="application/json">${JSON.stringify(sessions).replace(/</g,'\\u003c')}</script>
<script id="export-data" type="application/json">${JSON.stringify(exportData)}</script>
<script>
const exportData=JSON.parse(document.querySelector('#export-data').textContent);
const sessions=JSON.parse(document.querySelector('#data').textContent), q=id=>document.getElementById(id), session=q('session'), slot=q('slot'), audio=q('audio');
const option=(value,label)=>{const o=document.createElement('option');o.value=value;o.textContent=label;return o};
sessions.forEach((s,i)=>session.append(option(i,s.name+' / '+s.policy)));for(let i=0;i<10;i++)slot.append(option(i,i+' / '+2*i+' s'));
function stop(){audio.pause();audio.currentTime=0}function gain(){audio.volume=Number(q('gain').value);q('gainText').textContent=Math.round(audio.volume*100)+'%'}
function render(){const s=sessions[Number(session.value)],i=Number(slot.value);q('summary').textContent='Confirmations '+s.metrics.confirmations+'; genuine '+s.metrics.genuineConfirmations+'; false '+(s.metrics.confirmations-s.metrics.genuineConfirmations)+'; fresh genuine '+s.metrics.genuineFreshAtAck;q('detail').textContent=JSON.stringify(s.trace[i],null,2);q('metrics').textContent=JSON.stringify(s.metrics,null,2);q('timeline').replaceChildren();for(const t of s.trace){const tr=document.createElement('tr');for(const v of [t.slot+' / '+t.slot*2+' s',t.origin,t.fault,t.hits.length,t.events.map(e=>e.type).join(', ')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}if(t.slot===i)tr.style.background='#344b60';q('timeline').append(tr)}q('prev').disabled=i===0;q('next').disabled=i===9;}
function change(){stop();slot.value='0';const s=sessions[Number(session.value)];audio.src='scheduled-v2-output/'+s.name+'-'+s.policy+'.wav';gain();render();q('exportStatus').textContent=''}
session.onchange=change;slot.onchange=render;q('prev').onclick=()=>{slot.value=String(Math.max(0,Number(slot.value)-1));render()};q('next').onclick=()=>{slot.value=String(Math.min(9,Number(slot.value)+1));render()};q('gain').oninput=gain;q('stop').onclick=stop;q('export').onclick=()=>{const s=sessions[Number(session.value)],a=document.createElement('a');const bytes=Uint8Array.from(atob(exportData[Number(session.value)]),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([bytes],{type:'application/json'}));a.href=url;a.download=s.name+'-'+s.policy+'.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);q('exportStatus').textContent='Download requested: '+a.download};change();
</script></html>\n`;
const output=path.join(root,'index.html');
if(process.argv[3]==='--check')assert.equal(fs.readFileSync(output,'utf8'),html);else fs.writeFileSync(output,html);
console.log(JSON.stringify({schema:'mhac.schedule-inspector/1',sessions:sessions.length,slots:sessions.reduce((n,s)=>n+s.trace.length,0),evidence_pin:pin,html_sha256:sha(html),browser:'NOT_RUN'}));
