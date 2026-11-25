'use strict';
// MHAC #442 Measurement lane: duration-calibrated envelope pursuit, synthetic-only.
// Derived from multiscale-envelope.cjs at 844e4e8d7689bb703045b429ef0653af6fae0588 (blob c9c367d1df2d6f1d426178c2799f4423558cefe3).
// All methods share PCM, pursuit cap and onset grid. New split, not a replication of Run 009.
// Hypothesis: separate null scale calibration and two-sided conservative background contrast
// reduce longest-template bias and persistent-transition false alarms. Exploratory engineering.
// No human evidence, no acoustic identity inference, no canonical protocol changes.
function experiment(){
 const rate=8000,N=2400,E=240000000,step=4,cap=4,tol=8,baseL=160;
 const methods=["guard-fixed","local-fixed","local-multiscale","scale-calibrated","scale-calibrated-max-flank"],budgets=[0,.125,.25,.5],grid=[...Array.from({length:101},(_,i)=>i*.002),.25,.5,1,100],calGrid=[...Array.from({length:101},(_,i)=>i*.05),6,8,10,20,50,100,1000,1e9];
 let assertions=0;const ok=(v,m)=>{if(!v)throw Error(m);assertions++};
 function rng(seed){let x=seed>>>0;return ()=>{x=(x+0x6D2B79F5)|0;let z=x;z=Math.imul(z^z>>>15,z|1);z^=z+Math.imul(z^z>>>7,z|61);return ((z^z>>>14)>>>0)/4294967296}}
 const dot=(a,b)=>{let s=0;for(let i=0;i<a.length;i++)s+=a[i]*b[i];return s};
 const templates=[80,160,320].map(L=>{const a=Float64Array.from({length:L},(_,i)=>(Math.min(i,L-1-i)/(L/2))**2),n=Math.sqrt(dot(a,a)),w=a.map(x=>x/n);return {L,w,sum:w.reduce((s,x)=>s+x,0)}});
 function make(c){
  const random=rng(c.seed),raw=new Float64Array(N),pcm=new Int16Array(N);
  const first=(c.guard?16:300)+Math.floor(random()*(c.guard?28:100));
  const starts=c.null?[]:[first,first+(c.overlap?100:450)+Math.floor(random()*9)-4,1800+Math.floor(random()*100)];
  const truth=starts.map((t,k)=>({t,L:c.durations[k]}));
  for(let k=0;k<truth.length;k++){
   const {t,L}=truth[k],phase=(c.split==="dev"?.21:.093)+k*.317, f=c.split==="dev"?500:575;
   const h=Float64Array.from({length:L},(_,i)=>{const u=i/(L-1),env=c.skew?Math.min(u/.2,(1-u)/.8):2*Math.min(u,1-u),p=(i*f/rate+phase)%1;return env*(1-4*Math.abs(p-.5))});
   const n=Math.sqrt(dot(h,h)),a=Math.sqrt(E)*c.gain/n;ok(t+L<=N,"event bounds");ok(Math.abs(dot(h,h)*a*a/E-c.gain*c.gain)<1e-12,"isolated energy");
   for(let j=0;j<L;j++)raw[t+j]+=a*h[j];
  }
  for(let i=0;i<N;i++){const sigma=c.noise*(c.stepNoise&&i>=1100?3:1),tone=c.tone?650*Math.sin(2*Math.PI*710*i/rate):0;const v=Math.round(raw[i]+(2*random()-1)*sigma+tone);ok(Math.abs(v)<32768,"no clipping");pcm[i]=v}
  return {truth,pcm};
 }
 function fit(pcm,m,cal=null,scanOnly=false){
  const r=Float64Array.from(pcm,x=>x*x),events=[],maxima=[0,0,0];let products=0,prefixAdds=0;
  let guard=0;for(let i=0;i<baseL;i++)guard+=r[i];guard/=baseL;
  if(m===0)for(let i=0;i<N;i++)r[i]-=guard;
  for(let iter=0;iter<(scanOnly?1:cap);iter++){
   const pref=new Float64Array(N+1);if(m!==0)for(let i=0;i<N;i++){pref[i+1]=pref[i]+r[i];prefixAdds++}
   let best=null;
   for(const h of (m>=2?templates:[templates[1]]))for(let t=0;t<=N-h.L;t+=step){
    if(events.some(e=>Math.abs(e.t-t)<40))continue;
    let a=0;for(let j=0;j<h.L;j++)a+=r[t+j]*h.w[j];products+=h.L;
    if(m!==0){const flank=h.L/2,lo=Math.max(0,t-flank),hi=Math.min(N,t+h.L+flank),count=t-lo+hi-t-h.L;
     if(count){const left=t-lo,right=hi-t-h.L;
      let baseline=(pref[t]-pref[lo]+pref[hi]-pref[t+h.L])/count;
      if(m===4){if(!left||!right)continue;baseline=Math.max((pref[t]-pref[lo])/left,(pref[hi]-pref[t+h.L])/right)}
      a-=baseline*h.sum;products++}}
    // Normalize for duration: projection of fixed isolated energy scales roughly as 1/sqrt(L).
    const k=templates.indexOf(h);
    maxima[k]=Math.max(maxima[k],a);
    const score=m>=3?Math.max(0,a)/(cal?cal[k]:1):Math.max(0,a)*Math.sqrt(h.L/baseL)/E;
    if(!best||score>best.score)best={t,L:h.L,a:Math.max(0,a),score,h};
   }
   if(!best||best.score<=0)break;
   const {h,...e}=best;events.push(e);
   for(let j=0;j<h.L;j++)r[e.t+j]-=e.a*h.w[j];
  }
  return {events,products,prefixAdds,maxima};
 }
 function measure(truth,f,t,tolerance=tol){const seen=[];for(const e of f.events){if(e.score<=t)break;seen.push({t:e.t,L:e.L})}seen.sort((a,b)=>a.t-b.t);
  let i=0,j=0,tp=0,durationError=0,timingError=0,durationExact=0;while(i<truth.length&&j<seen.length){
   if(seen[j].t<truth[i].t-tolerance)j++;else if(truth[i].t<seen[j].t-tolerance)i++;else{tp++;durationExact+=+(truth[i].L===seen[j].L);durationError+=Math.abs(truth[i].L-seen[j].L);timingError+=Math.abs(truth[i++].t-seen[j++].t)}}
  return {seen,tp,fp:seen.length-tp,fn:truth.length-tp,durationError,timingError,durationExact}
 }
 function conditions(split){
  const test=split==="eval",base=test?3100000:2100000,cs=[];
  const groups=test?["control","short","long","mixed","skew","missing-guard","noise-step","continuous-tone","compound"]:["control","short","long","mixed"];
  for(const [g,group] of groups.entries())for(const noise of [300,1200])for(const gain of [.3,1])for(const overlap of [false,true])for(let s=0;s<(test?4:4);s++){
   cs.push({split,group,seed:base+s+noise*1000+Math.round(gain*10)*100+(overlap?10:0),noise,gain,overlap,guard:["missing-guard","compound"].includes(group),stepNoise:["noise-step","compound"].includes(group),tone:["continuous-tone","compound"].includes(group),skew:group==="skew",durations:group==="short"?[80,80,80]:group==="long"?[320,320,320]:["mixed","compound"].includes(group)?[80,160,320]:[160,160,160]})
  }
  for(const group of ["null","null-step","null-tone"])for(const noise of [300,1200])for(let s=0;s<8;s++)cs.push({split,group,seed:base+500000+noise*1000+s,noise,null:true,stepNoise:group==="null-step",tone:group==="null-tone"});
  return cs
 }
 // Seed ranges separated by 8000; condition seed increments within a cell are paired across groups.
 const dc=conditions("dev"),ec=conditions("eval");ok(!ec.some(c=>dc.some(d=>c.seed===d.seed)),"split seed separation");
 function prepare(cs){return cs.map(c=>{const {truth,pcm}=make(c);return {condition:c,truth,peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0),fits:methods.map((_,m)=>fit(pcm,m,calibration[m]))}})}
 const calibration={};const nulls=dc.filter(c=>c.null);
 for(const m of [3,4]){
  const peaks=nulls.map(c=>fit(make(c).pcm,m,null,true).maxima);
  calibration[m]=[0,1,2].map(k=>Math.max(1,...peaks.map(x=>x[k])));
  ok(calibration[m].every(x=>Number.isFinite(x)&&x>0),"calibration finite");
 }
 const dev=prepare(dc),ev=prepare(ec);
 function agg(rows,m,t,tolerance=tol){const a={packets:0,positive:0,tp:0,fp:0,fn:0,positiveFP:0,nullFalse:0,exact:0,durationError:0,timingError:0,durationExact:0,products:0,prefixAdds:0};for(const row of rows){const b=measure(row.truth,row.fits[m],t,tolerance);ok(b.tp+b.fn===row.truth.length&&b.tp+b.fp===b.seen.length,"partition");a.packets++;a.positive+=+(row.truth.length>0);for(const k of ["tp","fp","fn","durationError","timingError","durationExact"])a[k]+=b[k];a.positiveFP+=row.truth.length?b.fp:0;a.nullFalse+=+(!row.truth.length&&b.fp>0);a.exact+=+(b.fp===0&&b.fn===0);a.products+=row.fits[m].products;a.prefixAdds+=row.fits[m].prefixAdds}return a}
 const curves=methods.map((_,m)=>(m>=3?calGrid:grid).map(threshold=>({threshold,...agg(dev,m,threshold)})));
 const groups=[...new Set(ec.map(c=>c.group))];
 const operating=budgets.map(budget=>({budget,receivers:methods.map((name,m)=>{
  const selected=curves[m].filter(x=>!x.nullFalse&&x.positiveFP<=budget*x.positive).sort((a,b)=>b.tp-a.tp||a.positiveFP-b.positiveFP||b.threshold-a.threshold)[0];ok(!!selected,"feasible");
  const evaluation=Object.fromEntries(groups.map(g=>[g,agg(ev.filter(r=>r.condition.group===g),m,selected.threshold)]));evaluation.all=agg(ev,m,selected.threshold);const relaxed=agg(ev,m,selected.threshold,40);return {name,selected,evaluation,relaxed}
 })}));
 const thresholds=operating[3].receivers.map(x=>x.selected.threshold);
 const rows=ev.map(r=>({condition:r.condition,truth:r.truth,peak:r.peak,fit:r.fits.map((f,m)=>({...f,...measure(r.truth,f,thresholds[m])}))}));
 const witnesses=[...new Set([rows.findIndex(r=>r.condition.group==="missing-guard"&&r.fit[1].tp>r.fit[0].tp),rows.findIndex(r=>r.condition.group==="short"&&r.fit[2].tp>r.fit[1].tp),rows.findIndex(r=>r.condition.group==="long"&&r.fit[2].tp>r.fit[1].tp),rows.findIndex(r=>r.condition.group==="noise-step"&&r.fit[0].fp>r.fit[1].fp),rows.findIndex(r=>r.condition.group==="compound"&&r.fit[2].fn>0),rows.findIndex(r=>r.condition.group==="null-step"&&r.fit[2].fp>0),rows.findIndex(r=>r.condition.group==="null-tone"),rows.findIndex(r=>r.condition.group==="control"&&r.fit[2].tp<r.fit[0].tp)].filter(x=>x>=0))];
 for(const i of [rows.findIndex(r=>r.condition.group==="null-step"&&r.fit[2].fp>r.fit[4].fp),rows.findIndex(r=>r.condition.group==="mixed"&&r.fit[4].tp>r.fit[2].tp),rows.findIndex(r=>r.condition.group==="control"&&r.fit[4].tp<r.fit[0].tp)])if(i>=0&&!witnesses.includes(i))witnesses.push(i);
 const specimens=witnesses.map(i=>({i,pcm:Array.from(make(rows[i].condition).pcm)}));
 return {receipt:{schema:"mhac-scale-calibrated-envelope-v1",calibration,calGrid,calibrationNullPackets:nulls.length,firstHypotheses:methods.map((_,m)=>Object.fromEntries([80,160,320].map(L=>[L,ev.filter(r=>r.truth.length&&r.fits[m].events[0]?.L===L).length]))),claimClass:"finite synthetic onset detection",parent:"844e4e8d7689bb703045b429ef0653af6fae0588",rate,N,E,step,cap,tol,methods,budgets,development:dc,evaluation:ec,curves,operating,rows,witnesses,witnessBudget:.5,assertions},specimens}
}
function cli(){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),assert=require("node:assert/strict");
 const out=process.argv[2]||"scale-calibrated-output";fs.mkdirSync(out,{recursive:true});
 const {receipt,specimens}=experiment(),hash=b=>crypto.createHash("sha256").update(b).digest("hex");
 receipt.sourceSHA256=hash(fs.readFileSync(__filename));
 receipt.specimens=specimens.map(({i,pcm})=>{
  const b=Buffer.alloc(44+pcm.length*2);b.write("RIFF");b.writeUInt32LE(b.length-8,4);b.write("WAVEfmt ",8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(receipt.rate,24);b.writeUInt32LE(receipt.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write("data",36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((v,j)=>b.writeInt16LE(v,44+2*j));assert.equal(b.readUInt32LE(40),receipt.N*2);
  const name=`witness-${i}.wav`;fs.writeFileSync(path.join(out,name),b);return {i,name,sha256:hash(b)};
 });
 fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2)+"\n");
 const table=receipt.operating.flatMap(o=>o.receivers.flatMap(r=>Object.entries(r.evaluation).map(([g,v])=>"<tr>"+[o.budget,r.name,g,r.selected.threshold,v.tp,v.fp,v.fn,v.nullFalse,v.products].map(x=>`<td>${x}</td>`).join("")+"</tr>"))).join("");
 const cards=receipt.specimens.map(s=>`<section><h2>${s.name}</h2><audio controls preload="none" src="${s.name}"></audio><pre>${JSON.stringify({condition:receipt.rows[s.i].condition,truth:receipt.rows[s.i].truth,fit:receipt.rows[s.i].fit.map(f=>({seen:f.seen,tp:f.tp,fp:f.fp,fn:f.fn})),sha256:s.sha256},null,2)}</pre></section>`).join("");
 fs.writeFileSync(path.join(out,"index.html"),`<!doctype html><meta charset="utf-8"><title>MHAC multiscale envelope</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}td,th{padding:.35rem;border-bottom:1px solid #ccc;text-align:right}pre{overflow:auto;background:#eee;padding:1rem}audio{width:100%}</style><h1>Scale-calibrated acoustic event detection</h1><p>Finite synthetic onset tests only. Playback opt-in; start at low hardware volume. All receivers share PCM. Thresholds calibrated on duration-diverse development positives and stationary, step and tonal nulls. Scale denominators are maximum development null projections per duration; not probability estimates. <a href="receipt.json">Replay receipt</a>.</p><table><thead><tr>${["Budget","Receiver","Group","Threshold","TP","FP","FN","Null false packets","Products"].map(x=>`<th>${x}</th>`).join("")}</tr></thead><tbody>${table}</tbody></table>${cards}`);
 console.log(JSON.stringify({assertions:receipt.assertions,operating:receipt.operating,specimens:receipt.specimens},null,2));
}
module.exports={experiment};
if(require.main===module)cli();
