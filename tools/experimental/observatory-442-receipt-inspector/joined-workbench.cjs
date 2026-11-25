'use strict';
// Measurement lane #442 / Draft #443. AI-assisted synthetic measurements only.
// One shared regeneration, three original galleries plus joined packet-level diagnostics.
// Run: node joined-workbench.cjs NEW_OUTPUT_DIRECTORY ; open index.html.
const REF='fbe4224cd81aac931d20ba79aac000aa39cc703a';
const PINS={
  "region-refinement": "b9729da5b2f0532f2b509be21587b33f3ef21223",
  "joint-reconstruction": "a57455bb631f68808019435470dc63e7683cdedb",
  "selective-reconstruction": "5919b173dddacf6a30f7d058d0b08da042ffc7fa",
  "observatory-workbench": "03136eeaccc6f76a63e90bc7ad6f7fe0f57516bf",
  "matching-audit": "d1f3f8e39a96c9d0b60b16f8c26ccfc867efae87",
  "paired-sensitivity": "d8994eb0b026720de6ccd9cb417b8636a00eb62a"
};
const check=(x,m)=>{if(!x)throw Error(m)};
function join(inputs,workbench,matching,sensitivity){
 const cells=inputs.reduce((n,x)=>n+workbench.validate(x.receipt),0);
 const matchingReport=matching.audit(inputs), sensitivityReport=sensitivity.audit(inputs);
 const runs=[];let compared=0,ties=0,changedPairings=0;
 for(const [i,input] of inputs.entries()){
  const {name,blob,receipt:r}=input, m=matchingReport.runs[i],s=sensitivityReport.runs[i];
  check(name===m.name&&name===s.name&&blob===m.blob&&blob===s.blob,'report identity');
  check(!m.totals.cardinalityMismatch&&!m.totals.weightMismatch&&!m.totals.durationOutOfRange,'matching discrepancy: inspect standalone audit');
  const witnesses=matchingReport.witnesses.filter(w=>w.name===name);
  const map=new Map();
  for(const w of witnesses){
   const row=r.rows[w.packet],mi=r.methods.indexOf(w.method);
   check(row&&mi>=0&&r.criteria.includes(w.criterion),'witness identity');
   check(JSON.stringify(row.metrics[mi][w.criterion])===JSON.stringify(w.reported),'witness metric mismatch');
   const key=JSON.stringify([w.packet,w.method,w.criterion]);check(!map.has(key),'duplicate witness');map.set(key,w);
  }
  const comparisons=s.comparisons.map(c=>{
   const ai=r.methods.indexOf(c.methodA),bi=r.methods.indexOf(c.methodB);
   check(ai>=0&&bi>=0&&c.rows.length===r.rows.length,'comparison shape');
   const packets=c.rows.map((p,j)=>{
    const row=r.rows[j],a=row.metrics[ai][c.criterion],b=row.metrics[bi][c.criterion];
    check(p.packet===j&&p.group===row.condition.group&&p.seed===row.condition.seed&&p.n===row.truth.length&&p.a===a.tp&&p.b===b.tp&&p.fpA===a.fp&&p.fpB===b.fp,'paired row mismatch');
    const wa=map.get(JSON.stringify([j,c.methodA,c.criterion])),wb=map.get(JSON.stringify([j,c.methodB,c.criterion]));
    const range=(w,v)=>w?[w.optimal.lo,w.optimal.hi]:[v.durationError,v.durationError];
    const ra=range(wa,a),rb=range(wb,b),ambiguous=ra[0]!==ra[1]||rb[0]!==rb[1];
    // Compare sorted assignment lists, not arbitrary enumeration order.
    const pairs=v=>JSON.stringify(v.pairs.map(x=>x.join(':')).sort());
    const sameCount=a.tp===b.tp&&a.fp===b.fp;
    const sameFit=JSON.stringify(row.fits[ai].map(e=>[e.t,e.L]))===JSON.stringify(row.fits[bi].map(e=>[e.t,e.L]));
    // Pair indices are only comparable when prediction arrays have identical interval ordering.
    const pairingDiff=sameFit&&pairs(a)!==pairs(b);
    compared++;ties+=+ambiguous;changedPairings+=+(sameCount&&!sameFit);
    return {...p,aMetric:a,bMetric:b,aRange:ra,bRange:rb,ambiguous,sameCount,sameFit,pairingDiff,truth:row.truth,aFit:row.fits[ai],bFit:row.fits[bi],audio:input.specimens.some(v=>v.i===j)?name+'-audition-'+j+'.wav':null};
   });
   return {...c,rows:packets};
  });
  runs.push({name,blob,rate:r.rate,N:r.N,matching:m.totals,comparisons});
 }
 check(cells===matchingReport.runs.reduce((n,r)=>n+r.totals.cells,0),'audit coverage');
 return {schema:'mhac-joined-workbench-v1',sourceRef:REF,sourceBlobs:PINS,scope:'Finite synthetic measurement; no human or population inference.',cells,compared,ambiguousPairCells:ties,equalCountDifferentOrderedFitCells:changedPairings,runs};
}
function browser(d){
 const $=id=>document.getElementById(id), entries=d.runs.flatMap(r=>r.comparisons.map(c=>({run:r,...c})));
 const add=(node,tag,t)=>{const x=document.createElement(tag);x.textContent=t;node.append(x);return x};
 const options=(node,rows)=>{node.replaceChildren();for(const [v,t] of rows){const x=add(node,'option',t);x.value=String(v)}};
 const selected=()=>entries[Number($('comparison').value)];
 const fmt=x=>x===null?'undefined':x.toFixed(3);
 function refresh(){
  const c=selected(),f=$('filter').value;
  $('summary').textContent=c.run.name+' | '+c.criterion+' | recall A minus B: '+fmt(c.delta)+' pp | seed-block 2.5–97.5 percentiles: '+fmt(c.seedBlockResampling.lower)+' to '+fmt(c.seedBlockResampling.upper)+' pp (descriptive)';
  const rows=c.rows.filter(p=>f==='all'||f==='ambiguous'&&p.ambiguous||f==='count'&&!p.sameCount||f==='fit'&&p.sameCount&&!p.sameFit||f==='audio'&&p.audio);
  $('scope').textContent=rows.length+' / '+c.rows.length+' packets';
  options($('packet'),rows.map(p=>[p.packet,p.packet+' | '+p.group+' | seed '+p.seed]));detail();
 }
 function detail(){
  const c=selected(),p=$('packet').value===''?null:c.rows[Number($('packet').value)],audio=$('audio'),svg=$('plot');
  audio.pause();audio.removeAttribute('src');audio.load();audio.hidden=true;svg.replaceChildren();
  if(!p){$('details').textContent='No matching packets';$('trace').textContent='';return}
  const rate=c.run.rate,N=c.run.N,mae=(range,tp)=>tp?range.map(v=>(1000*v/rate/tp).toFixed(3)).join(' – ')+' ms':'undefined';
  $('details').textContent='TP/FP A: '+p.a+'/'+p.fpA+'; B: '+p.b+'/'+p.fpB+'. Conditional duration MAE ranges A: '+mae(p.aRange,p.a)+'; B: '+mae(p.bRange,p.b)+'. '+(p.ambiguous?'At least one optimal association admits different duration error.':'No duration range ambiguity in this audit.');
  const draw=(tag,a,t)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(a))e.setAttribute(k,v);if(t!==undefined)e.textContent=t;svg.append(e)};
  for(const [i,[label,events]] of [['Truth',p.truth],['A',p.aFit],['B',p.bFit]].entries()){
   const y=8+i*42;draw('text',{x:4,y:y+15,fill:'currentColor'},label);
   events.forEach((e,j)=>{draw('rect',{x:65+800*e.t/N,y:y+(j%3)*5,width:800*e.L/N,height:17,fill:['#64748b','#3178a5','#a06a32'][i],opacity:.7});draw('text',{x:65+800*e.t/N,y:y+30,'font-size':10,fill:'currentColor'},String(j))});
  }
  for(let i=0;i<=6;i++){const x=65+800*i/6;draw('line',{x1:x,x2:x,y1:0,y2:126,stroke:'currentColor',opacity:.15});draw('text',{x,y:145,'font-size':10,'text-anchor':'middle',fill:'currentColor'},(1000*N/rate*i/6).toFixed(0)+' ms')}
  if(p.audio){audio.src='reconstruction/'+p.audio;audio.hidden=false}
  $('trace').textContent=JSON.stringify({sourceRef:d.sourceRef,blob:c.run.blob,run:c.run.name,methodA:c.methodA,methodB:c.methodB,criterion:c.criterion,rate,N,packet:p},null,2);
 }
 options($('comparison'),entries.map((c,i)=>[i,c.run.name+' | '+c.methodA+' vs '+c.methodB+' | '+c.criterion]));
 $('comparison').onchange=refresh;$('filter').onchange=refresh;$('packet').onchange=detail;refresh();
}
function page(d){
 const data=JSON.stringify(d).replace(/</g,'\\u003c');
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MHAC joined measurement workbench</title><style>body{font:16px system-ui;max-width:1100px;margin:auto;padding:1rem;color-scheme:light dark}select{display:block;max-width:100%;font:inherit;margin:.5rem 0}svg,audio{width:100%}pre{overflow:auto;max-height:30rem}nav a{display:inline-block;margin:.3rem .8rem .3rem 0}</style><h1>MHAC joined measurement workbench</h1><p>Synthetic only. Original scoring unchanged. Equal counts do not imply identical ordered predictions. Duration ranges are conditional on optimal matching under the original criterion. Audio is opt-in, common attenuation, not calibrated SPL; start at low hardware volume.</p><nav><a href="reconstruction/index.html">Original reconstruction/audio gallery</a><a href="matching/index.html">Matching witnesses</a><a href="sensitivity/index.html">Condition and seed sensitivity</a><a href="receipt.json">Joined receipt</a><a href="manifest.json">File manifest</a></nav><label>Comparison<select id="comparison"></select></label><p id="summary"></p><label>Packet filter<select id="filter"><option value="all">All packets</option><option value="ambiguous">Duration ambiguity</option><option value="count">Different TP or FP</option><option value="fit">Equal counts, different ordered intervals</option><option value="audio">Preserved audio</option></select></label><p id="scope"></p><label>Packet<select id="packet"></select></label><p id="details"></p><svg id="plot" viewBox="0 0 900 155" role="img" aria-label="Ground truth and two receiver interval lanes"></svg><audio id="audio" controls preload="none" hidden></audio><details><summary>Replay trace and association pairs</summary><pre id="trace"></pre></details><script>('+browser.toString()+')('+data+');</script></html>';
}
function test(d){
 check(d.cells===16550&&d.compared===4380,'pinned coverage');
 check(d.runs.map(r=>r.comparisons.length).join(',')==='5,5,15','comparison coverage');
 const entries=d.runs.flatMap(r=>r.comparisons);
 check(entries.every(c=>c.rows.reduce((n,p)=>n+p.a,0)===c.a&&c.rows.reduce((n,p)=>n+p.b,0)===c.b),'aggregate joins');
 check(entries.some(c=>c.rows.some(p=>p.ambiguous)),'duration witness');
 check(entries.some(c=>c.rows.some(p=>p.sameCount&&!p.sameFit)),'equal count different intervals witness');
 check(entries.every(c=>c.rows.every(p=>p.aRange[0]<=p.aMetric.durationError&&p.aMetric.durationError<=p.aRange[1]&&p.bRange[0]<=p.bMetric.durationError&&p.bMetric.durationError<=p.bRange[1])),'range inclusion');
 const html=page(d);check(!/<audio[^>]*autoplay/i.test(html),'opt-in audio');
 return 7;
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),out=process.argv[2]||'joined-workbench-output';
 check(!fs.existsSync(out)||!fs.readdirSync(out).length,'Use new/empty output directory');
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 const mods={};for(const [name,blob] of Object.entries(PINS)){const f=path.join(__dirname,name+'.cjs'),b=fs.readFileSync(f);check(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')===blob,'source pin '+name);mods[name]=require(f)}
 const inputs=Object.keys(PINS).slice(0,3).map(name=>({name,blob:PINS[name],...mods[name].experiment()}));
 const w=mods['observatory-workbench'],m=mods['matching-audit'],s=mods['paired-sensitivity'];
 const d=join(inputs,w,m,s),tests=test(d),bundle=w.selfTest(inputs,hash),mr=m.audit(inputs),sr=s.audit(inputs);
 check(JSON.stringify(d)===JSON.stringify(join(inputs,w,m,s)),'repeat joined receipt');
 const files={'index.html':page(d),'receipt.json':JSON.stringify(d,null,2)+'\n','reconstruction/index.html':bundle.page,'reconstruction/manifest.json':JSON.stringify(bundle.data,null,2)+'\n','matching/index.html':m.page(mr),'matching/receipt.json':JSON.stringify(mr,null,2)+'\n','sensitivity/index.html':s.page(sr),'sensitivity/receipt.json':JSON.stringify(sr,null,2)+'\n'};
 for(const [name,b] of Object.entries(bundle.files))files['reconstruction/'+name]=b;
 const manifest={schema:'mhac-joined-workbench-files-v1',sourceRef:REF,sourceBlobs:PINS,sourceSHA256:hash(fs.readFileSync(__filename)),tests,files:Object.fromEntries(Object.entries(files).map(([name,b])=>[name,hash(b)]))};
 for(const [name,b] of Object.entries({...files,'manifest.json':JSON.stringify(manifest,null,2)+'\n'})){const f=path.join(out,name);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,b)}
 console.log(JSON.stringify({cells:d.cells,compared:d.compared,ambiguousPairCells:d.ambiguousPairCells,equalCountDifferentOrderedFitCells:d.equalCountDifferentOrderedFitCells,tests,files:Object.keys(files).length},null,2));
}
module.exports={PINS,join,page,test,browser};if(require.main===module)cli();
