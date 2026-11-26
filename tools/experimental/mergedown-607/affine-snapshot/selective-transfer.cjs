'use strict';
// Measurement lane, Refs #442 / #443. Synthetic probability mass, not listening data.
// AI-assisted implementation and same-agent checks; no independent review.
const REF='cb329512d47b287366b8a4af03aa7046b88b8768';
const PINS={'core.js':'47938c769604ae56a1f8cb92e5d4ccc3e20f8d59','phase.html':'c8f8631a9e76318a271d811e471af75e5c372acf','legacy-workbench.cjs':'71766ee6194f36f16aca6459fcf64966105844ce'};
const CUT=[.5,.6,.75,.9,1];
const MODELS=[
 {id:'nominal',prior:[.25,.25,.25,.25],phase:'uniform',jitter:[[0,1]]},
 {id:'middle-late-1',prior:[.25,.25,.25,.25],phase:'uniform',jitter:[[1,1]]},
 {id:'middle-early-1',prior:[.25,.25,.25,.25],phase:'uniform',jitter:[[-1,1]]},
 {id:'middle-symmetric-1',prior:[.25,.25,.25,.25],phase:'uniform',jitter:[[-1,.25],[0,.5],[1,.25]]},
 {id:'middle-symmetric-2',prior:[.25,.25,.25,.25],phase:'uniform',jitter:[[-2,.25],[0,.5],[2,.25]]},
 {id:'late-phase',prior:[.25,.25,.25,.25],phase:'upper-half',jitter:[[0,1]]},
 {id:'biased-deletion',prior:[.1,.1,.1,.7],phase:'uniform',jitter:[[0,1]]},
 {id:'combined',prior:[.1,.1,.1,.7],phase:'upper-half',jitter:[[-1,.25],[0,.5],[1,.25]]}
];
const sum=a=>a.reduce((s,v)=>s+v,0), key=a=>a.join(','), argmax=a=>a.indexOf(Math.max(...a)), near=(a,b)=>Math.abs(a-b)<1e-9;
function transfer(core,phase,legacy){
 let assertions=0;const ok=(v,m)=>{if(!v)throw Error(m);assertions++};
 const rows=phase.run().rows, baseline=legacy.phaseAdapter(core,phase), all=[], witnesses=[];
 for(const c of rows){
  const {p,q,rate,ms,frame}=c, z=phase.inspect(p,q,rate,ms,frame), nominal=new Map(z.receipts.map(r=>[key(r.samples),r.posterior]));
  const condition={p,q,rate,ms,frame};
  for(const model of MODELS){
   const actual=new Map(), origins=new Map(), phaseMass=s=>{const lo=s.lo[0]/s.lo[1],hi=s.hi[0]/s.hi[1];return model.phase==='uniform'?hi-lo:2*Math.max(0,hi-Math.max(.5,lo))};
   for(const s of z.segments)for(const r of s.rows)for(const [shift,weight] of model.jitter){
    const mass=phaseMass(s)*model.prior[r.deleted-1]*weight;if(!mass)continue;
    const observed=r.samples.slice();observed[1]+=shift;
    ok(observed[0]<observed[1]&&observed[1]<observed[2],'ordered observation');
    const k=key(observed);if(!actual.has(k))actual.set(k,[0,0,0,0]);actual.get(k)[r.deleted-1]+=mass;
    if(!origins.has(k))origins.set(k,[]);origins.get(k).push({deleted:r.deleted,trueSamples:r.samples,observed,shift,mass,phase:[s.lo,s.hi]});
   }
   ok(near(sum([...actual.values()].map(sum)),1),'total evaluation mass');
   for(let i=0;i<4;i++)ok(near(sum([...actual.values()].map(a=>a[i])),model.prior[i]),'evaluation deletion marginal');
   const cells=[...actual].map(([k,mass])=>{
    const post=nominal.get(k),prediction=post?argmax(post):null,confidence=post?post[prediction]:null,probability=sum(mass);
    const correct=prediction===null?0:mass[prediction];
    return {samples:k.split(',').map(Number),mass,probability,prediction:prediction===null?null:prediction+1,confidence,correct,wrong:probability-correct,oracleCorrect:Math.max(...mass)};
   });
   const oov=sum(cells.filter(x=>x.prediction===null).map(x=>x.probability));
   const oracle=sum(cells.map(x=>x.oracleCorrect));
   const curve=CUT.map(cutoff=>{
    const keep=cells.filter(x=>x.confidence!==null&&x.confidence+1e-12>=cutoff);
    const coverage=sum(keep.map(x=>x.probability)),correct=sum(keep.map(x=>x.correct)),wrong=sum(keep.map(x=>x.wrong)),expectedWrong=sum(keep.map(x=>x.probability*(1-x.confidence)));
    ok(near(coverage,correct+wrong)&&coverage<=1-oov+1e-9,'mass conservation');
    return {cutoff,coverage,correct,wrong,expectedWrong,conditionalError:coverage>1e-12?wrong/coverage:null};
   });
   for(let j=1;j<curve.length;j++)ok(curve[j].coverage<=curve[j-1].coverage+1e-9,'nested coverage');
   if(model.id==='nominal'){
    const old=baseline.rows.find(x=>['p','q','rate','ms','frame'].every(k=>x[k]===c[k]));
    ok(near(oov,0)&&near(oracle,z.hiddenAccuracy),'nominal support and oracle');
    for(const x of curve){const y=old.curve.find(t=>t.cutoff===x.cutoff);ok(near(x.coverage,y.coverage)&&near(x.correct,y.correct)&&near(x.wrong,y.error)&&near(x.wrong,x.expectedWrong),'nominal previous curve')}
   }
   const strongest=cells.filter(x=>x.confidence!==null&&x.confidence+1e-12>=1&&x.wrong>1e-12).sort((a,b)=>b.wrong-a.wrong)[0];
   if(strongest){const candidates=origins.get(key(strongest.samples)).filter(x=>x.deleted!==strongest.prediction).sort((a,b)=>b.mass-a.mass);ok(candidates.length>0,'witness provenance');witnesses.push({condition,model:model.id,cell:strongest,origin:candidates[0]})}
   all.push({condition,model:model.id,oov,oracle,curve,cells});
  }
 }
 const summary=[];
 for(const frame of ['receipt','fixed'])for(const m of MODELS){
  const group=all.filter(x=>x.condition.frame===frame&&x.model===m.id),mean=a=>sum(a)/group.length;
  ok(group.length===144,'factorial size');
  summary.push({frame,model:m.id,conditions:group.length,oov:mean(group.map(x=>x.oov)),oracle:mean(group.map(x=>x.oracle)),curve:CUT.map((cutoff,j)=>{
   const coverage=mean(group.map(x=>x.curve[j].coverage)),correct=mean(group.map(x=>x.curve[j].correct)),wrong=mean(group.map(x=>x.curve[j].wrong)),expectedWrong=mean(group.map(x=>x.curve[j].expectedWrong));
   return {cutoff,coverage,correct,wrong,expectedWrong,conditionalError:coverage>1e-12?wrong/coverage:null};
  })});
 }
 // A single witness per observation frame and mechanism. Selection is diagnostic, not a new evaluation set.
 const selected=[];
 for(const frame of ['receipt','fixed'])for(const m of MODELS){
  const w=witnesses.filter(x=>x.condition.frame===frame&&x.model===m.id).sort((a,b)=>b.cell.wrong-a.cell.wrong)[0];
  if(w){const c=core.condition(w.condition.p,w.condition.q,w.condition.rate,w.condition.ms,w.condition.frame),b=core.wav(c,{samples:w.origin.trueSamples});let peak=0;const v=new DataView(b.buffer,b.byteOffset,b.byteLength);for(let i=44;i<b.length;i+=2)peak=Math.max(peak,Math.abs(v.getInt16(i,true)));ok(peak<=9000,'bounded specimen');selected.push({...w,sha256:core.sha256(b),peak,bytes:b.length})}
 }
 ok(all.length===2304,'all conditions');ok(selected.some(w=>w.model==='middle-late-1'&&w.condition.frame==='receipt'),'confidence failure witness');
 return {schema:'mhac-selective-transfer-v1',sourceRef:REF,pins:PINS,source:phase.run().sourceRef,claimClass:'finite synthetic feature observation model',seed:null,models:MODELS,summary,rows:all,witnesses:selected,assertions};
}
function browser(d){
 const $=x=>document.getElementById(x),pct=x=>x==null?'undefined':(100*x).toFixed(3)+'%';
 $('model').innerHTML=d.models.map(x=>'<option>'+x.id+'</option>').join('');
 function render(){
  const f=$('frame').value,m=$('model').value,s=d.summary.find(x=>x.frame===f&&x.model===m);
  $('rows').innerHTML=s.curve.map(x=>'<tr><td>'+x.cutoff+'</td><td>'+pct(x.coverage)+'</td><td>'+pct(x.wrong)+'</td><td>'+pct(x.expectedWrong)+'</td><td>'+pct(x.conditionalError)+'</td></tr>').join('');
  $('support').textContent='Outside nominal support: '+pct(s.oov)+'; matched-model oracle (unselective): '+pct(s.oracle);
  const w=d.witnesses.find(x=>x.condition.frame===f&&x.model===m);$('witness').textContent=w?JSON.stringify(w,null,2):'No selected certainty failure for this mechanism/frame.';
  $('audio').hidden=!w;if(w)$('audio').src='witness-'+d.witnesses.indexOf(w)+'.wav';else $('audio').removeAttribute('src');
 }
 $('frame').onchange=render;$('model').onchange=render;render();
}
function page(d){
 const payload=JSON.stringify({models:d.models,summary:d.summary,witnesses:d.witnesses}).replace(/</g,'\\u003c');
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MHAC selective transfer</title><style>body{font:16px system-ui;max-width:960px;margin:2rem auto;padding:0 1rem}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #aaa;text-align:right;padding:.4rem}pre{white-space:pre-wrap;overflow-wrap:anywhere}select{font:inherit;margin:.5rem}audio{width:100%}</style><h1>Selective decoding under feature-model mismatch</h1><p>Finite synthetic probability masses. The decoder is frozen at nominal uniform phase and deletion priors. Jitter perturbs only the observed middle onset index, not the waveform. Out-of-support receipts abstain. An oracle using the evaluation distribution is diagnostic only, not a deployable receiver. Equal-weight condition aggregate; no participants or calibrated SPL.</p><label>Frame <select id="frame"><option value="receipt">Receipt relative</option><option value="fixed">Fixed external clock</option></select></label><label>Evaluation model <select id="model"></select></label><p id="support"></p><table><thead><tr><th>Cutoff</th><th>Coverage</th><th>Wrong mass</th><th>Nominal expected wrong mass</th><th>Error among accepted</th></tr></thead><tbody id="rows"></tbody></table><h2>Selected certainty failure</h2><p>Diagnostic witness selected by maximum wrong cell mass, not independent evaluation. Audio is the original true-onset waveform; the indicated observation shift exists only in the synthetic feature extractor. Start at low hardware volume.</p><pre id="witness"></pre><audio id="audio" controls preload="none"></audio><p><a href="receipt.json">Full condition/cell trace</a> · <a href="manifest.json">SHA-256 manifest</a></p><script>('+browser.toString()+')('+payload+');</script></html>';
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),out=process.argv[2]||'selective-transfer-output';
 if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('Use new or empty output directory');
 for(const [n,pin] of Object.entries(PINS)){const b=fs.readFileSync(path.join(__dirname,n));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==pin)throw Error('Source pin '+n)}
 const core=require('./core.js'),legacy=require('./legacy-workbench.cjs'),phase=legacy.loadPhase(fs.readFileSync(path.join(__dirname,'phase.html'),'utf8'),core),d=transfer(core,phase,legacy),files={'index.html':page(d),'receipt.json':JSON.stringify(d,null,2)+'\n'};
 d.witnesses.forEach((w,i)=>{const c=core.condition(w.condition.p,w.condition.q,w.condition.rate,w.condition.ms,w.condition.frame);const b=core.wav(c,{samples:w.origin.trueSamples});if(core.sha256(b)!==w.sha256)throw Error('Witness hash');files['witness-'+i+'.wav']=b});
 fs.mkdirSync(out,{recursive:true});const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
 for(const [n,b] of Object.entries(files))fs.writeFileSync(path.join(out,n),b);
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({sourceRef:REF,pins:PINS,sourceSHA256:sha(fs.readFileSync(__filename)),files:Object.fromEntries(Object.entries(files).map(([n,b])=>[n,sha(b)]))},null,2)+'\n');
 console.log(JSON.stringify({assertions:d.assertions,summary:d.summary,witnesses:d.witnesses},null,2));
}
module.exports={transfer,browser,page};if(require.main===module)cli();
