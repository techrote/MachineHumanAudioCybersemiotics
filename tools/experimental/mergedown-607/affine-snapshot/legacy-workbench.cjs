'use strict';
// Measurement lane, Refs #442 / #443. Synthetic-only. AI-assisted, no independent review.
// Distinct observation models, never pooled. Preserve the original source and calibration.
const REF='53eb42dd0103abccfb08111a0e6ec112b55e7750';
const PINS={'core.js':'47938c769604ae56a1f8cb92e5d4ccc3e20f8d59','phase.html':'c8f8631a9e76318a271d811e471af75e5c372acf','index.html':'5ee12f884479425acf8d3137a1974ff6df9c8cb4','phase-fit.cjs':'fd0fbca5bc784fadb9227baa628fb290506b841c','matched-fp.cjs':'e2c5e29240844a643ba966e5a261909d39f07862'};
const check=(v,m)=>{if(!v)throw Error(m)};
const near=(a,b)=>Math.abs(a-b)<1e-9;
const cutoffs=[.25,.5,.6,.75,.9,1];
function phaseAdapter(core,phase){
 const base=core.run(),p=phase.run(),tests=phase.tests();
 check(base.rows.length===288&&p.rows.length===288,'affine coverage');
 const rows=p.rows.map((r,i)=>{
  const b=base.rows[i];check(['p','q','rate','ms','frame'].every(k=>b[k]===r[k]),'condition join');
  check(near(b.optimalIndexAccuracy,r.halfAccuracy),'half-phase equality');
  const z=phase.inspect(r.p,r.q,r.rate,r.ms,r.frame);
  const curve=cutoffs.map(c=>{
   const kept=z.receipts.filter(x=>Math.max(...x.posterior)+1e-12>=c);
   const coverage=kept.reduce((s,x)=>s+x.probability,0),correct=kept.reduce((s,x)=>s+Math.max(...x.mass),0);
   check(correct<=coverage+1e-9,'correct mass');
   return {cutoff:c,coverage,correct,error:Math.max(0,coverage-correct),conditionalError:coverage>1e-12?Math.max(0,coverage-correct)/coverage:null};
  });
  check(near(curve[0].coverage,1)&&near(curve[0].correct,r.hiddenAccuracy),'Bayes reproduction');
  check(near(curve.at(-1).error,0),'certainty abstention');
  for(let j=1;j<curve.length;j++)check(curve[j].coverage<=curve[j-1].coverage+1e-9,'nested acceptance');
  return {...r,curve};
 });
 const summary={};for(const frame of ['receipt','fixed']){
  const rr=rows.filter(x=>x.frame===frame);
  summary[frame]=cutoffs.map((cutoff,j)=>{
   const coverage=rr.reduce((s,x)=>s+x.curve[j].coverage,0)/rr.length,correct=rr.reduce((s,x)=>s+x.curve[j].correct,0)/rr.length;
   return {cutoff,coverage,correct,error:Math.max(0,coverage-correct),conditionalError:coverage>1e-12?Math.max(0,coverage-correct)/coverage:null};
  });
 }
 return {schema:'mhac-phase-selective-v1',prior:p.phasePrior,unit:'probability mass, equally weighted finite conditions',tests,source:p.sourceRef,rows,summary,originalSummary:p.summary};
}
function operatingAdapter(b){
 check(b.schema==='mhac-matched-fp-v1'&&b.operating.length===4,'operating schema');
 const rows=b.operating.flatMap(o=>o.receivers.map(r=>{
  const d=r.selected,e=r.evaluation.known;
  check(d.positiveFP<=o.budget*d.positivePackets&&d.nullFalse===0,'development admissibility');
  check(e.tp+e.fn===576&&e.packets===192,'known evaluation denominator');
  const devRate=d.positiveFP/d.positivePackets,evalRate=e.fp/e.packets;
  return {budget:o.budget,receiver:r.name,threshold:d.threshold,devRate,evalRate,excess:evalRate-o.budget,devTP:d.tp,knownTP:e.tp,knownFP:e.fp,knownFN:e.fn,knownRecall:e.tp/(e.tp+e.fn),nullFalse:r.evaluation.null.nullFalse,unseenTP:r.evaluation.unseen.tp,overlapTP:r.evaluation.overlap.tp,products:e.products};
 }));
 const witness=b.rows.filter(r=>r.condition.f===500||r.condition.f===800);
 for(let m=0;m<3;m++){const q=rows.filter(r=>r.budget===b.witnessBudget)[m];check(witness.reduce((s,r)=>s+r.outcomes[m].tp,0)===q.knownTP&&witness.reduce((s,r)=>s+r.outcomes[m].fp,0)===q.knownFP,'packet aggregate reproduction')}
 return {schema:'mhac-operating-transfer-v1',unit:'false detections per positive packet; recall per injected onset',rows,assertions:b.assertions,source:b.sourceRef,witnessBudget:b.witnessBudget,witnesses:b.witnesses.map(i=>({i,...b.rows[i]}))};
}
function audit(core,phase,benchmark,detector,assert){
 const a=phaseAdapter(core,phase),b=benchmark.benchmark(detector,assert),o=operatingAdapter(b);
 return {schema:'mhac-legacy-workbench-v1',sourceRef:REF,pins:PINS,claimClass:'finite synthetic measurements under distinct observation models',phase:a,operating:o,benchmark:b};
}
function browser(data){
 const $=id=>document.getElementById(id),pct=x=>x==null?'undefined':(100*x).toFixed(2)+'%';
 const render=()=>{
  const f=$('frame').value,idx=Number($('condition').value),r=idx<0?data.phase.summary[f]:data.phase.rows.filter(x=>x.frame===f)[idx].curve;
  $('phaseRows').innerHTML=r.map(x=>'<tr><td>'+x.cutoff+'</td><td>'+pct(x.coverage)+'</td><td>'+pct(x.correct)+'</td><td>'+pct(x.error)+'</td><td>'+pct(x.conditionalError)+'</td></tr>').join('');
  const budget=Number($('budget').value);
  $('opRows').innerHTML=data.operating.rows.filter(x=>x.budget===budget).map(x=>'<tr><td>'+x.receiver+'</td><td>'+x.threshold+'</td><td>'+x.devRate.toFixed(4)+'</td><td>'+x.evalRate.toFixed(4)+'</td><td>'+pct(x.knownRecall)+'</td><td>'+x.knownFP+'</td><td>'+x.nullFalse+'</td><td>'+x.unseenTP+'</td></tr>').join('');
 };
 const populate=()=>{$('condition').innerHTML='<option value="-1">Equal-weight condition aggregate</option>'+data.phase.rows.filter(x=>x.frame===$('frame').value).map((r,i)=>'<option value="'+i+'">p='+r.p+', q='+r.q+'; '+r.rate+' Hz; '+r.ms+' ms</option>').join('');$('condition').value='-1';render()};
 $('frame').onchange=populate;$('condition').onchange=render;$('budget').onchange=render;populate();
}
function page(d,joined=false){
 const payload=JSON.stringify({phase:d.phase,operating:d.operating}).replace(/</g,'\\u003c');
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MHAC earlier measurement adapters</title><style>body{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem}table{border-collapse:collapse;width:100%}td,th{padding:.4rem;text-align:right;border-bottom:1px solid #aaa}td:first-child,th:first-child{text-align:left}select{font:inherit;margin:.4rem}nav a{display:inline-block;margin:.4rem}audio{width:100%}.scroll{overflow:auto}</style><h1>MHAC measurement workbench — earlier apparatus</h1><p>Synthetic only. Exact observation and noisy waveform detection have different denominators and are not pooled. No human data or calibrated sound-level claim.</p><nav><a href="affine/index.html">Affine receipt inspector</a><a href="affine/phase.html">Exact phase inspector</a><a href="receipt.json">Full replay receipt</a><a href="manifest.json">File manifest</a>'+(joined?'<a href="reconstruction/index.html">Joined reconstruction workbench</a>':'')+'</nav><h2>Exact hidden-phase selective decoding</h2><p>Uniform deletion and phase priors; accept the maximum posterior class only at or above the selected cutoff. Ties use an arbitrary fixed choice; expected correctness is the maximum joint mass. Coverage and wrong mass are unconditional; conditional error is undefined with zero coverage. Equal-weight condition aggregation is a descriptive design summary.</p><label>Frame <select id="frame"><option value="receipt">Receipt relative</option><option value="fixed">Known fixed reference</option></select></label><label>Condition <select id="condition"></select></label><div class="scroll"><table><thead><tr><th>Posterior cutoff</th><th>Coverage</th><th>Correct mass</th><th>Wrong mass</th><th>Error if accepted</th></tr></thead><tbody id="phaseRows"></tbody></table></div><h2>Development budget transfer</h2><p>Budget is development false detections per positive packet, not a bound on held-out errors. Known-family held-out recall uses 576 injected events; null and unseen counts are separate. No retuning on evaluation.</p><label>Development FP/packet budget <select id="budget"><option>0</option><option>0.125</option><option selected>0.25</option><option>0.5</option></select></label><div class="scroll"><table><thead><tr><th>Receiver</th><th>Threshold</th><th>Dev FP/packet</th><th>Eval FP/packet</th><th>Known recall</th><th>Known FP</th><th>Null false packets</th><th>Unseen TP</th></tr></thead><tbody id="opRows"></tbody></table></div><h2>Preserved operating-point specimens</h2><p>Same original input for all receivers, raw PCM; start with low hardware volume. Original traces use the 0.25 budget.</p>'+d.operating.witnesses.map(w=>'<h3>Packet '+w.i+'</h3><audio controls preload="none" src="witness-'+w.i+'.wav"></audio><p>True onsets (samples): '+w.truth.join(', ')+'</p>').join('')+'<script>('+browser.toString()+')('+payload+');</script></html>';
}
function loadPhase(html,core){
 const script=html.match(/<script id="phase-core">([\s\S]*?)<\/script>/);check(script,'phase script missing');
 return new Function('MHAC',script[1]+';return PHASE;')(core);
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict'),out=process.argv[2]||'legacy-workbench-output',joined=process.argv.includes('--with-reconstruction');
 check(!fs.existsSync(out)||fs.readdirSync(out).length===0,'Use new/empty output directory');
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),raw={};
 for(const [n,sha] of Object.entries(PINS)){const b=fs.readFileSync(path.join(__dirname,n));check(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')===sha,'source pin '+n);raw[n]=b}
 const core=require('./core.js'),phase=loadPhase(raw['phase.html'].toString('utf8'),core),detector=require('./phase-fit.cjs'),bench=require('./matched-fp.cjs'),d=audit(core,phase,bench,detector,assert);
 const files={'index.html':page(d,joined),'receipt.json':JSON.stringify(d,null,2)+'\n','affine/core.js':raw['core.js'],'affine/index.html':raw['index.html'],'affine/phase.html':raw['phase.html']};
 for(const w of d.operating.witnesses)files['witness-'+w.i+'.wav']=detector.wave(detector.make(w.condition).pcm);
 for(const [n,b] of Object.entries(files)){const f=path.join(out,n);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,b)}
 if(joined){const child=require('node:child_process').spawnSync(process.execPath,[path.join(__dirname,'joined-workbench.cjs'),path.join(out,'reconstruction')],{stdio:'inherit'});check(child.status===0,'joined reconstruction export failed')}
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({schema:'mhac-legacy-workbench-files-v1',sourceRef:REF,pins:PINS,sourceSHA256:hash(fs.readFileSync(__filename)),files:Object.fromEntries(Object.entries(files).map(([n,b])=>[n,hash(b)])),nestedManifest:joined?'reconstruction/manifest.json':null},null,2)+'\n');
 console.log(JSON.stringify({phase:d.phase.summary,operating:d.operating.rows},null,2));
}
module.exports={PINS,loadPhase,phaseAdapter,operatingAdapter,audit,page,browser};if(require.main===module)cli();
