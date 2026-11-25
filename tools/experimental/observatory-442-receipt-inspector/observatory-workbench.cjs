'use strict';
// Measurement lane #442, Refs #443. Synthetic-only offline reconstruction workbench.
// Pinned inputs from 1c6b167aadab320ded495a36fe2ee58cd7ce37bf; no upstream mutation.
// Node >=18: node observatory-workbench.cjs OUTPUT (new/empty directory), then open OUTPUT/index.html.
// Rebuilds three frozen experiments, verifies source Git blob IDs, and exports portable receipts/audio.
// Other experiments remain accessible through their own original interfaces; no pooled metrics.
const BASE='1c6b167aadab320ded495a36fe2ee58cd7ce37bf';
const INPUTS=[
 ['region-refinement','b9729da5b2f0532f2b509be21587b33f3ef21223'],
 ['joint-reconstruction','a57455bb631f68808019435470dc63e7683cdedb'],
 ['selective-reconstruction','5919b173dddacf6a30f7d058d0b08da042ffc7fa']
];
const LIMIT=Math.floor(.12*32767);
function check(x,m){if(!x)throw Error(m)}
function aggregate(rows,methods,criterion){
 return methods.map((name,i)=>{
  const a={name,tp:0,fp:0,fn:0,onsetError:0,durationError:0,iouSum:0};
  for(const r of rows)for(const k of ['tp','fp','fn','onsetError','durationError','iouSum'])a[k]+=r.metrics[i][criterion][k];
  return a;
 });
}
function validate(r){
 check(INPUTS.some(([name])=>r.schema==='mhac-'+name+'-v1'),'unsupported receipt schema');
 check(Number.isInteger(r.rate)&&r.rate>0&&Number.isInteger(r.N)&&r.N>0,'invalid sample clock');
 check(r.rows.length===r.evaluation.length,'evaluation row count');
 check(new Set(r.methods).size===r.methods.length&&r.methods.length>0,'unique methods');
 check(new Set(r.criteria).size===r.criteria.length&&r.criteria.length>0,'unique criteria');
 const validEvent=e=>Number.isInteger(e.t)&&Number.isInteger(e.L)&&e.t>=0&&e.L>0&&e.t+e.L<=r.N;
 let cells=0;
 for(const [index,row] of r.rows.entries()){
  check(JSON.stringify(row.condition)===JSON.stringify(r.evaluation[index]),'condition order');
  check(row.truth.every(validEvent),'truth bounds');
  check(row.fits.length===r.methods.length&&row.metrics.length===r.methods.length,'method arity');
  for(const [i,fit] of row.fits.entries()){
   check(fit.every(validEvent),'fit bounds');
   for(const k of r.criteria){
    const m=row.metrics[i][k];
    for(const key of ['tp','fp','fn'])check(Number.isInteger(m[key])&&m[key]>=0,'invalid count');
    for(const key of ['onsetError','durationError','iouSum'])check(Number.isFinite(m[key])&&m[key]>=0,'invalid measurement');
    check(m.tp+m.fp===fit.length&&m.tp+m.fn===row.truth.length,'row accounting');
    check(Array.isArray(m.pairs)&&m.pairs.length===m.tp,'pair count');
    const a=new Set(),b=new Set();let onset=0,duration=0,ious=0;
    for(const [u,v] of m.pairs){
     check(Number.isInteger(u)&&Number.isInteger(v)&&row.truth[u]&&fit[v]&&!a.has(u)&&!b.has(v),'invalid one-to-one matching');
     a.add(u);b.add(v);const e=row.truth[u],f=fit[v],ov=Math.max(0,Math.min(e.t+e.L,f.t+f.L)-Math.max(e.t,f.t));
     const iou=ov/(e.L+f.L-ov),err=Math.abs(e.t-f.t);
     check(k.startsWith('iou')?iou>=Number(k.slice(3)):err<=r.rate*(k==='strict'?.001:.005),'pair violates criterion');
     onset+=err;duration+=Math.abs(e.L-f.L);ious+=iou;
    }
    check(onset===m.onsetError&&duration===m.durationError&&Math.abs(ious-m.iouSum)<1e-9,'pair metric mismatch');
    cells++;
   }
  }
 }
 for(const k of r.criteria)for(const [i,v] of aggregate(r.rows,r.methods,k).entries()){
  check(r.results[i].name===v.name,'method order');
  for(const key of Object.keys(v).filter(x=>x!=='name'))check(Math.abs(r.results[i].metrics[k][key]-v[key])<1e-8,'aggregate mismatch');
 }
 return cells;
}
function wave(pcm,rate,gain){
 const b=new Uint8Array(44+2*pcm.length),d=new DataView(b.buffer);
 const put=(s,i)=>{for(let j=0;j<s.length;j++)b[i+j]=s.charCodeAt(j)};
 put('RIFF',0);d.setUint32(4,b.length-8,true);put('WAVEfmt ',8);d.setUint32(16,16,true);
 d.setUint16(20,1,true);d.setUint16(22,1,true);d.setUint32(24,rate,true);d.setUint32(28,rate*2,true);
 d.setUint16(32,2,true);d.setUint16(34,16,true);put('data',36);d.setUint32(40,pcm.length*2,true);
 pcm.forEach((x,i)=>d.setInt16(44+2*i,Math.round(x*gain),true));return b;
}
function bundle(inputs,hash){
 check(inputs.length===INPUTS.length,'input count');
 let peak=1,cells=0;const files={},runs=[];
 for(const [i,x] of inputs.entries()){
  const [name,blob]=INPUTS[i],r=x.receipt;
  check(x.name===name&&x.blob===blob&&r.schema==='mhac-'+name+'-v1','input identity');
  cells+=validate(r);
  check(new Set(x.specimens.map(s=>s.i)).size===x.specimens.length,'duplicate specimen');
  for(const s of x.specimens){
   check(Number.isInteger(s.i)&&r.rows[s.i]&&s.pcm.length===r.N,'specimen shape');
   for(const v of s.pcm){check(Number.isInteger(v)&&v>=-32768&&v<=32767,'PCM range');peak=Math.max(peak,Math.abs(v))}
  }
 }
 const gain=Math.min(1,LIMIT/peak);
 for(const [i,x] of inputs.entries()){
  const [name,blob]=INPUTS[i],r=x.receipt;
  const specimens=x.specimens.map(s=>{
   const raw=wave(s.pcm,r.rate,1),audition=wave(s.pcm,r.rate,gain);
   const rawName=name+'-raw-'+s.i+'.wav',audioName=name+'-audition-'+s.i+'.wav';
   files[rawName]=raw;files[audioName]=audition;
   let previewPeak=0;const d=new DataView(audition.buffer);
   for(let k=44;k<audition.length;k+=2)previewPeak=Math.max(previewPeak,Math.abs(d.getInt16(k,true)));
   check(previewPeak<=LIMIT,'audition digital peak');
   return {i:s.i,pcm:s.pcm,rawName,audioName,rawSHA256:hash(raw),auditionSHA256:hash(audition),previewPeak};
  });
  runs.push({name,blob,sourceRef:BASE,receipt:r,specimens});
 }
 return {data:{schema:'mhac-observatory-workbench-v1',claimClass:'finite synthetic measurement; no human evidence',sourceRef:BASE,gain,rawPeak:peak,previewLimit:LIMIT,validatedMetricCells:cells,runs},files};
}
function browser(data){
 const $=id=>document.getElementById(id);
 const set=(id,v)=>{$(id).textContent=v};
 const opt=(el,values)=>{el.replaceChildren();for(const [v,label] of values){const o=document.createElement('option');o.value=v;o.textContent=label;el.append(o)}};
 function table(el,heads,rows){
  el.replaceChildren();const t=document.createElement('table'),h=document.createElement('tr');
  for(const v of heads){const c=document.createElement('th');c.textContent=v;h.append(c)}t.append(h);
  for(const row of rows){const tr=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;tr.append(c)}t.append(tr)}el.append(t);
 }
 const selected=()=>data.runs[Number($('run').value)];
 const criterion=()=>$('criterion').value;
 const rows=()=>selected().receipt.rows.map((r,i)=>({r,i})).filter(({r})=>$('group').value==='*'||r.condition.group===$('group').value);
 function reset(){
  const {receipt:r}=selected();
  opt($('criterion'),r.criteria.map(k=>[k,k==='strict'?'Onset ≤ 1 ms':k==='relaxed'?'Onset ≤ 5 ms':'IoU ≥ '+k.slice(3)]));$('criterion').value='iou0.75';
  opt($('group'),[['*','All conditions'],...Array.from(new Set(r.rows.map(x=>x.condition.group))).map(x=>[x,x])]);
  opt($('a'),r.methods.map((x,i)=>[i,x]));opt($('b'),r.methods.map((x,i)=>[i,x]));$('b').value=r.methods.length-1;
  refresh();
 }
 function refresh(){
  const {receipt:r,specimens,blob,sourceRef}=selected(),k=criterion(),a=Number($('a').value),b=Number($('b').value),rr=rows();
  const totals=aggregate(rr.map(x=>x.r),r.methods,k);
  set('scope',rr.length+' packets | '+rr.reduce((s,x)=>s+x.r.truth.length,0)+' true events | '+r.rate+' Hz | '+(1000*r.N/r.rate)+' ms each');
  set('provenance',sourceRef+' / Git blob '+blob+' / '+r.schema+' / '+r.assertions+' original computational assertions');
  table($('summary'),['Receiver','TP','FP','FN','Precision','Recall','Onset MAE ms*','Duration MAE ms*'],totals.map(x=>[x.name,x.tp,x.fp,x.fn,x.tp+x.fp?(x.tp/(x.tp+x.fp)*100).toFixed(1)+'%':'—',x.tp+x.fn?(x.tp/(x.tp+x.fn)*100).toFixed(1)+'%':'—',x.tp?(1000*x.onsetError/x.tp/r.rate).toFixed(2):'—',x.tp?(1000*x.durationError/x.tp/r.rate).toFixed(2):'—']));
  const deltas=rr.map(({r:row,i})=>({i,d:row.metrics[b][k].tp-row.metrics[a][k].tp}));
  set('paired',r.methods[b]+' vs '+r.methods[a]+': '+deltas.filter(x=>x.d>0).length+' packet wins / '+deltas.filter(x=>x.d===0).length+' ties / '+deltas.filter(x=>x.d<0).length+' losses. Descriptive, not independent trials.');
  const mode=$('filter').value,choices=rr.filter(({r:row,i})=>mode==='all'||(mode==='audio'&&specimens.some(s=>s.i===i))||(mode==='loss'&&row.metrics[b][k].tp<row.metrics[a][k].tp)||(mode==='gain'&&row.metrics[b][k].tp>row.metrics[a][k].tp));
  const old=$('packet').value;opt($('packet'),choices.map(({r:row,i})=>[i,i+' · '+row.condition.group+' · '+row.condition.seed+(specimens.some(s=>s.i===i)?' · audio':'')]));
  if(choices.some(x=>String(x.i)===old))$('packet').value=old;
  detail();
 }
 function detail(){
  const run=selected(),r=run.receipt,k=criterion(),a=Number($('a').value),b=Number($('b').value),v=$('packet').value,row=v===''?null:r.rows[Number(v)],audio=$('audio');
  audio.pause();audio.removeAttribute('src');audio.load();audio.hidden=true;
  const svg=$('timeline');svg.replaceChildren();
  if(!row){set('packetmeta','No matching packets');set('trace','');set('audioinfo','No specimen');$('packetmetrics').replaceChildren();return}
  const specimen=run.specimens.find(s=>s.i===Number(v)),NS='http://www.w3.org/2000/svg';
  function draw(tag,attrs,txt){const e=document.createElementNS(NS,tag);for(const [k,val] of Object.entries(attrs))e.setAttribute(k,val);if(txt!==undefined)e.textContent=txt;svg.append(e)}
  const X=180,W=800,lanes=[['Ground truth',row.truth],...r.methods.map((name,i)=>[name,row.fits[i]])],top=specimen?110:24;
  svg.setAttribute('viewBox','0 0 1000 '+(top+lanes.length*26+28));
  if(specimen){
   const samples=specimen.pcm,scale=32/32768;
   draw('text',{x:4,y:15,fill:'currentColor'},'PCM (raw, fixed full-scale axis)');
   draw('line',{x1:X,y1:58,x2:X+W,y2:58,stroke:'#aaa'});
   for(let i=0;i<800;i++){const chunk=samples.slice(Math.floor(i*samples.length/800),Math.floor((i+1)*samples.length/800));if(chunk.length)draw('line',{x1:X+i,x2:X+i,y1:58-Math.max(...chunk)*scale,y2:58-Math.min(...chunk)*scale,stroke:'#2563a5'});}
   audio.src=specimen.audioName;audio.hidden=false;
   set('audioinfo','Common attenuation '+data.gain.toFixed(6)+'; preview peak '+specimen.previewPeak+' counts. SHA-256 '+specimen.auditionSHA256);
  }else set('audioinfo','No preserved PCM for this packet. Interval traces remain available.');
  for(const [i,[label,events]] of lanes.entries()){
   const y=top+i*26;draw('text',{x:4,y:y+14,fill:'currentColor','font-size':12},label);
   draw('rect',{x:X,y,width:W,height:18,fill:'#888','fill-opacity':.08});
   for(const e of events)draw('rect',{x:X+e.t/r.N*W,y,width:e.L/r.N*W,height:18,fill:i===0?'#475569':i===a+1?'#2563a5':i===b+1?'#a75519':'#39857f','fill-opacity':.7,stroke:'currentColor','stroke-width':.4});
  }
  const end=top+lanes.length*26;
  for(let t=0;t<=6;t++){const x=X+t*W/6;draw('line',{x1:x,y1:top,x2:x,y2:end,stroke:'#888','stroke-opacity':.2});draw('text',{x,y:end+14,'text-anchor':'middle',fill:'currentColor','font-size':11},(1000*r.N/r.rate*t/6).toFixed(0)+' ms')}
  set('packetmeta','Packet '+v+' · '+row.condition.group+' · seed '+row.condition.seed);
  table($('packetmetrics'),['Receiver','TP','FP','FN'],r.methods.map((n,i)=>{const m=row.metrics[i][k];return[n,m.tp,m.fp,m.fn]}));
  set('trace',JSON.stringify({sourceRef:run.sourceRef,blob:run.blob,packet:Number(v),criterion:k,row,specimen:specimen?{rawSHA256:specimen.rawSHA256,auditionSHA256:specimen.auditionSHA256}:null},null,2));
 }
 opt($('run'),data.runs.map((r,i)=>[i,r.name+' ('+r.receipt.rows.length+' packets)']));
 $('run').value=data.runs.length-1;$('run').onchange=reset;
 for(const id of ['criterion','group','a','b','filter'])$(id).onchange=refresh;
 $('packet').onchange=detail;
 $('export').onclick=()=>{const blob=new Blob([$('trace').textContent+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='packet-trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
 reset();
}
function html(data){
 const json=JSON.stringify(data).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MHAC Observatory workbench</title><style>body{font:15px system-ui;max-width:1200px;margin:auto;padding:1.5rem;color-scheme:light dark}h1{font-size:1.6rem}h2{font-size:1.2rem;margin-top:1.5rem}label{display:inline-flex;flex-direction:column;margin:.4rem .7rem .4rem 0;gap:.3rem}select,button{font:inherit;padding:.4rem}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{padding:.4rem;border-bottom:1px solid #8885;text-align:right}td:first-child,th:first-child{text-align:left}pre{overflow:auto;max-height:24rem;background:#8881;padding:1rem}svg{width:100%;display:block}audio{width:100%}p{overflow-wrap:anywhere}.scroll{overflow:auto}</style><h1>MHAC Observatory / reconstruction workbench</h1><p>Finite synthetic experiments only; separate seed splits and thresholds. Never pool these runs as one benchmark. Audio is opt-in; start at low hardware volume. Digital peak is not calibrated SPL. <a href="manifest.json">Manifest and receipts</a>.</p><label>Experiment<select id="run"></select></label><label>Condition<select id="group"></select></label><label>Matching criterion<select id="criterion"></select></label><p id="scope"></p><p id="provenance"></p><div id="summary" class="scroll"></div><p>* Mean absolute errors conditional on matched events, not unconditional accuracy.</p><h2>Paired packet inspection</h2><label>Baseline<select id="a"></select></label><label>Comparator<select id="b"></select></label><label>Filter<select id="filter"><option value="all">All packets</option><option value="audio">Preserved audio</option><option value="gain">Comparator gains</option><option value="loss">Comparator losses</option></select></label><p id="paired"></p><label>Packet<select id="packet"></select></label><p id="packetmeta"></p><svg id="timeline" role="img" aria-label="Raw waveform when available and event interval overlays"></svg><audio id="audio" controls preload="none" hidden></audio><p id="audioinfo"></p><div id="packetmetrics"></div><details><summary>Replay trace</summary><pre id="trace"></pre></details><button id="export">Export selected trace</button><p>Earlier laboratories remain in the source tree: index.html, adaptive.html, phase.html, decomposition.html; original CLI scripts and galleries remain unchanged.</p><script>const aggregate='+aggregate.toString()+';('+browser.toString()+')('+json+');</script></html>';
}
function selfTest(inputs,hash){
 check(hash(new Uint8Array())==='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','SHA-256 empty');
 const x=bundle(inputs,hash),y=bundle(inputs,hash);
 check(JSON.stringify(x.data)===JSON.stringify(y.data),'deterministic manifest');
 const page=html(x.data);check(page===html(y.data)&&!/<audio[^>]*autoplay/i.test(page),'deterministic opt-in page');
 const expected=[[25,110,113,120],[48,198,229,239,237,243],[50,194,245,237,235,239,235,240,239]];
 for(const [i,run] of x.data.runs.entries())check(JSON.stringify(aggregate(run.receipt.rows,run.receipt.methods,'iou0.75').map(x=>x.tp))===JSON.stringify(expected[i]),'pinned count regression');
 const bad=JSON.parse(JSON.stringify(inputs[0].receipt));bad.rows[0].metrics[0][bad.criteria[0]].tp++;
 let refused=false;try{validate(bad)}catch(e){refused=true}check(refused,'corrupt receipt refused');
 for(const [name,bytes] of Object.entries(x.files)){
  const d=new DataView(bytes.buffer);check(d.getUint32(4,true)===bytes.length-8&&d.getUint32(40,true)===bytes.length-44,'WAV length');
  check(hash(bytes)===hash(y.files[name]),'deterministic WAV');
 }
 return { ...x,page };
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const out=process.argv[2]||'observatory-workbench-output';
 if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('Use a new or empty output directory');
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const inputs=INPUTS.map(([name,blob])=>{
  const file=path.join(__dirname,name+'.cjs'),source=fs.readFileSync(file);
  const actual=crypto.createHash('sha1').update('blob '+source.length+'\0').update(source).digest('hex');
  check(actual===blob,'pinned source mismatch: '+name);
  return {name,blob,...require(file).experiment()};
 });
 const {data,files,page}=selfTest(inputs,hash);
 fs.mkdirSync(out,{recursive:true});
 for(const [name,bytes] of Object.entries(files))fs.writeFileSync(path.join(out,name),bytes);
 fs.writeFileSync(path.join(out,'index.html'),page);
 const manifest={...data,workbenchSHA256:hash(fs.readFileSync(__filename)),htmlSHA256:hash(page)};
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 console.log(JSON.stringify({runs:data.runs.map(r=>({name:r.name,rows:r.receipt.rows.length,specimens:r.specimens.length})),validatedMetricCells:data.validatedMetricCells,gain:data.gain,rawPeak:data.rawPeak,wavs:Object.keys(files).length},null,2));
}
module.exports={INPUTS,aggregate,validate,wave,bundle,html,selfTest};
if(require.main===module)cli();
