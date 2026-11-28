'use strict';
// MHAC #442 Measurement lane. Synthetic-only; no human evidence.
// Parent phase-fit.cjs pinned at c01f4d294e16b06c08783e8014bbf2dee010cf72; run beside unchanged parent.
// Calibration: max development TP, zero null false packets, positive FP per packet budget.
// Evaluation is not forced to equal FP; report realised transfer, no population inference.
function benchmark(core,assert){
 const methods=["fixed","quadrature","joint-refit"],budgets=[0,.125,.25,.5],thresholds=[...Array.from({length:151},(_,i)=>i/100),100];
 let assertions=0;const check=(v,m)=>{assert(v,m);assertions++};
 function conditions(base,evalSet){
  const cs=[];for(const noise of [300,1200])for(let i=0;i<12;i++)cs.push({f:0,noise,seed:base+1000+noise+i});
  for(const f of evalSet?[500,800,650]:[500,800])for(const gain of [.3,1])for(const noise of [300,1200])for(const overlap of [false,true])for(const phase of ["fixed","shifted"])for(let i=0;i<(evalSet?6:4);i++)cs.push({f,gain,noise,overlap,phase,phases:phase==="fixed"?[0,0,0]:evalSet?[.093,.417,.827]:[.21,.49,.72],seed:base+i});
  return cs;
 }
 const dc=conditions(830000,false),ec=conditions(940000,true);check(ec.every(c=>!dc.some(d=>d.seed===c.seed)),"disjoint seeds");
 const prep=cs=>cs.map(c=>{const a=core.make(c);const fits=methods.map(m=>core.fit(a.pcm,m));return {c,truth:a.truth,peak:a.pcm.reduce((v,x)=>Math.max(v,Math.abs(x)),0),fits}});
 const dev=prep(dc),ev=prep(ec);
 function aggregate(rows,m,t,filter=()=>true){
  const a={packets:0,tp:0,fp:0,fn:0,exact:0,nullFalse:0,positiveFP:0,positivePackets:0,products:0};
  for(const r of rows){if(!filter(r))continue;const z=core.measure(r.truth,r.fits[m],t);
   a.packets++;a.tp+=z.tp;a.fp+=z.fp;a.fn+=z.fn;a.exact+=+(z.fp===0&&z.fn===0);a.products+=r.fits[m].products;
   if(r.c.f===0)a.nullFalse+=+(z.fp>0);else{a.positiveFP+=z.fp;a.positivePackets++}
   check(z.tp+z.fn===r.truth.length&&z.tp+z.fp===z.seen.length,"partition");
  }return a;
 }
 const curves=methods.map((_,m)=>thresholds.map(t=>({threshold:t,...aggregate(dev,m,t)})));
 const filters={all:r=>true,known:r=>r.c.f===500||r.c.f===800,overlap:r=>(r.c.f===500||r.c.f===800)&&r.c.overlap,separated:r=>(r.c.f===500||r.c.f===800)&&!r.c.overlap,shifted:r=>(r.c.f===500||r.c.f===800)&&r.c.phase==="shifted",unseen:r=>r.c.f===650,null:r=>r.c.f===0};
 const operating=budgets.map(b=>({budget:b,receivers:methods.map((name,m)=>{
  const options=curves[m].filter(x=>x.nullFalse===0&&x.positiveFP<=b*x.positivePackets).sort((a,z)=>z.tp-a.tp||a.positiveFP-z.positiveFP||z.threshold-a.threshold);
  check(options.length>0,"feasible");const selected=options[0];
  return {name,selected,evaluation:Object.fromEntries(Object.entries(filters).map(([k,f])=>[k,aggregate(ev,m,selected.threshold,f)]))};
 })}));
 const chosen=operating[2].receivers.map(r=>r.selected.threshold);
 const rows=ev.map(r=>({condition:r.c,truth:r.truth,peak:r.peak,outcomes:r.fits.map((f,m)=>core.measure(r.truth,f,chosen[m]))}));
 const witnesses=[rows.findIndex(r=>r.condition.f!==0&&r.condition.f!==650&&r.outcomes[2].tp>r.outcomes[0].tp),rows.findIndex(r=>r.condition.f!==0&&r.outcomes[2].fp>r.outcomes[0].fp),rows.findIndex(r=>r.condition.f===650),rows.findIndex(r=>r.condition.f===0)].filter(i=>i>=0);
 check(witnesses.length>=2,"witness coverage");
 return {schema:"mhac-matched-fp-v1",claimClass:"finite synthetic detector comparison",sourceRef:"c01f4d294e16b06c08783e8014bbf2dee010cf72",rate:8000,matchToleranceSamples:8,methods,budgets,thresholds,development:dc,evaluation:ec,curves,operating,rows,witnesses,witnessBudget:budgets[2],assertions};
}
module.exports={benchmark};
if(require.main===module){
 const core=require('./phase-fit.cjs'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
 const out=process.argv[2]||'matched-fp-output';fs.mkdirSync(out,{recursive:true});
 const receipt=benchmark(core,assert);receipt.sourceSHA256=crypto.createHash('sha256').update(fs.readFileSync(require.resolve('./phase-fit.cjs'))).digest('hex');
 assert.equal(receipt.sourceSHA256,'c6b9d0b72323cde354ec88ea041d7cc7b00ce13842d265d9ec9de19a4e280d27','parent source differs from pinned source');
 const specimens=receipt.witnesses.map(i=>{const r=receipt.rows[i],b=core.wave(core.make(r.condition).pcm),name='witness-'+i+'.wav';fs.writeFileSync(path.join(out,name),b);return {i,name,sha256:crypto.createHash('sha256').update(b).digest('hex')};});
 receipt.specimens=specimens;fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
 const table=receipt.operating.flatMap(o=>o.receivers.map(r=>'<tr><td>'+o.budget+'</td><td>'+r.name+'</td><td>'+r.selected.threshold+'</td><td>'+r.selected.positiveFP+'</td><td>'+r.evaluation.known.tp+'</td><td>'+r.evaluation.known.fp+'</td><td>'+r.evaluation.overlap.tp+'</td><td>'+r.evaluation.unseen.tp+'</td></tr>')).join('');
 const cards=specimens.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio><pre>'+JSON.stringify({sha256:s.sha256,condition:receipt.rows[s.i].condition,truth:receipt.rows[s.i].truth,outcomes:receipt.rows[s.i].outcomes.map(o=>({seen:o.seen,tp:o.tp,fp:o.fp,fn:o.fn}))},null,2)+'</pre>').join('');
 fs.writeFileSync(path.join(out,'index.html'),'<!doctype html><meta charset="utf-8"><title>MHAC operating point transfer</title><style>body{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:1rem}td,th{padding:.4rem;border-bottom:1px solid #aaa;text-align:right}pre{overflow:auto;background:#eee;padding:1rem}audio{width:100%}</style><h1>Matched development false-detection budgets</h1><p>Synthetic only. Onset tolerance: 1 ms. Budgets apply to development, not held-out FP. Playback opt-in; start with low hardware volume.</p><table><thead><tr><th>Budget FP/positive packet</th><th>Receiver</th><th>Threshold</th><th>Dev FP</th><th>Known TP</th><th>Known FP</th><th>Overlap TP</th><th>Unseen TP</th></tr></thead><tbody>'+table+'</tbody></table>'+cards+'<p><a href="receipt.json">Full replay receipt</a></p>');
 console.log(JSON.stringify({assertions:receipt.assertions,operating:receipt.operating,specimens},null,2));
}
