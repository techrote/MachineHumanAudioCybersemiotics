'use strict';
// MHAC Measurement #442 Run 012. Synthetic only; no human inference.
// Fixture and three detector kernels adapted from shape-calibrated.cjs, 3e53875b60b2bb3518341507ab598f20f51ebdaf, blob c419664b6a512520bb5ef1747009f0d2ef00498f.
function experiment(){
 const rate=8000,N=2400,E=240000000,step=4,cap=4,tol=8,baseL=160;
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
   const h=Float64Array.from({length:L},(_,i)=>{const u=i/(L-1),env=Math.min(u/(c.shape??.5),(1-u)/(1-(c.shape??.5))),p=(i*f/rate+phase)%1;return env*(1-4*Math.abs(p-.5))});
   const n=Math.sqrt(dot(h,h)),a=Math.sqrt(E)*c.gain/n;ok(t+L<=N,"event bounds");ok(Math.abs(dot(h,h)*a*a/E-c.gain*c.gain)<1e-12,"isolated energy");
   for(let j=0;j<L;j++)raw[t+j]+=a*h[j];
  }
  for(let i=0;i<N;i++){const sigma=c.noise*(c.stepNoise&&i>=1100?3:1),tone=c.tone?650*Math.sin(2*Math.PI*710*i/rate):0;const v=Math.round(raw[i]+(2*random()-1)*sigma+tone);ok(Math.abs(v)<32768,"no clipping");pcm[i]=v}
  return {truth,pcm};
 }

 const methods=["rectangular-energy","symmetric-reference","shape-bank","energy-region"],budgets=[0,.125,.25,.5];
 const bank=(m)=>[80,160,320].flatMap(L=>(m===0?[0]:m===1?[.5]:[.2,.5,.8]).map(shape=>{
   const a=Float64Array.from({length:L},(_,i)=>shape===0?1:shape===.5?(Math.min(i,L-1-i)/(L/2))**2:Math.min(i/(L-1)/shape,(1-i/(L-1))/(1-shape))**2);
   const n=Math.sqrt(dot(a,a)),w=a.map(x=>x/n);return {L,shape,w,sum:w.reduce((s,x)=>s+x,0)};
 }));
 const banks=methods.slice(0,3).map((_,m)=>bank(m));
 function detect(pcm,m,cal=null,scanOnly=false){
  const r=Float64Array.from(pcm,x=>x*x),events=[],maxima=banks[m].map(()=>0);
  let products=0,rectQueries=0,prefixAdds=0;
  for(let iter=0;iter<(scanOnly?1:cap);iter++){
   const pref=new Float64Array(N+1);for(let i=0;i<N;i++){pref[i+1]=pref[i]+r[i];prefixAdds++}
   let best=null;
   for(let k=0;k<banks[m].length;k++){
    const h=banks[m][k],flank=h.L/2;
    for(let t=step;t<N-h.L;t+=step){
     if(events.some(e=>Math.abs(e.t-t)<40))continue;
     const lo=Math.max(0,t-flank),hi=Math.min(N,t+h.L+flank);
     const b=Math.max((pref[t]-pref[lo])/(t-lo),(pref[hi]-pref[t+h.L])/(hi-t-h.L));
     let a=0;
     if(m===0){a=(pref[t+h.L]-pref[t])*h.w[0];rectQueries++}
     else{for(let j=0;j<h.L;j++)a+=r[t+j]*h.w[j];products+=h.L}
     a-=b*h.sum;products++;
     maxima[k]=Math.max(maxima[k],a);
     const score=Math.max(0,a)/(cal?cal[k]:1);
     if(!best||score>best.score)best={t,L:h.L,shape:h.shape,a:Math.max(0,a),score,k};
    }
   }
   if(!best||best.score<=0)break;
   events.push(best);const h=banks[m][best.k];for(let j=0;j<h.L;j++)r[best.t+j]-=best.a*h.w[j];
  }
  return {events,maxima,products,rectQueries,prefixAdds};
 }
 function conditions(split){
  const test=split==="eval",base=test?19100000:17100000,cs=[];
  const groups=test?["control","short","long","mixed","skew-early","skew-late","skew-unseen","missing-guard","noise-step","continuous-tone","compound"]:["control","short","long","mixed","skew-early"];
  for(const group of groups)for(const noise of [300,1200])for(const gain of [.3,1])for(const overlap of [false,true])for(let s=0;s<1;s++){
   cs.push({split,group,seed:base+s+noise*1000+Math.round(gain*10)*100+(overlap?10:0),noise,gain,overlap,guard:["missing-guard","compound"].includes(group),stepNoise:["noise-step","compound"].includes(group),tone:["continuous-tone","compound"].includes(group),shape:group==="skew-early"?.2:group==="skew-late"?.8:group==="skew-unseen"?.35:.5,durations:group==="short"?[80,80,80]:group==="long"?[320,320,320]:["mixed","compound"].includes(group)?[80,160,320]:[160,160,160]});
  }
  for(const group of ["null","null-step","null-tone"])for(const noise of [300,1200])for(let s=0;s<2;s++)cs.push({split,group,seed:base+500000+noise*1000+s,noise,null:true,stepNoise:group==="null-step",tone:group==="null-tone"});
  return cs;
 }

 // Independent change-point baseline: 2 ms energy bins, max of two distant
 // flank medians, hysteretic region growth, no fitted acoustic templates.
 // All constants declared before evaluation; not causal (uses right flank).
 function region(pcm){
  const B=16,n=N/B,e=Array.from({length:n},(_,i)=>{let s=0;for(let j=0;j<B;j++)s+=pcm[i*B+j]**2;return s/B});
  const median=a=>{a.sort((a,b)=>a-b);return a.length?a[Math.floor(a.length/2)]:0};
  const candidates=[];
  for(let i=0;i<n;i++){
   const left=e.slice(Math.max(0,i-35),Math.max(0,i-11)),right=e.slice(Math.min(n,i+12),Math.min(n,i+36));
   if(!left.length&&!right.length)continue;
   const base=Math.max(10000,median(left),median(right)),peak=e[i],score=Math.max(0,peak-base)/base;
   if(score<=0||peak<(e[i-1]??-1)||peak<(e[i+1]??-1))continue;
   const floor=base+.12*(peak-base);let lo=i,hi=i+1;
   while(lo>0&&i-lo<12&&e[lo-1]>floor)lo--;
   while(hi<n&&hi-i<13&&e[hi]>floor)hi++;
   candidates.push({t:lo*B,L:(hi-lo)*B,score,peak:i*B+8});
  }
  candidates.sort((a,b)=>b.score-a.score||a.t-b.t);const events=[];
  for(const c of candidates){if(events.some(x=>Math.max(x.t,c.t)<Math.min(x.t+x.L,c.t+c.L)))continue;events.push(c);if(events.length===cap)break}
  return {events,maxima:[candidates[0]?.score??0],bins:n};
 }
 const dc=conditions("dev"),ec=conditions("eval");
 ok(!ec.some(c=>dc.some(d=>d.seed===c.seed)),"disjoint split");
 const cal=methods.map((_,m)=>{
  const maxima=dc.filter(c=>c.null).map(c=>m===3?region(make(c).pcm).maxima:detect(make(c).pcm,m,null,true).maxima);
  return maxima[0].map((_,k)=>Math.max(1e-9,...maxima.map(v=>v[k])));
 });
 function prepare(cs){return cs.map(c=>{const {truth,pcm}=make(c);return {condition:c,truth,peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0),fits:methods.map((_,m)=>{
  if(m!==3)return detect(pcm,m,cal[m]);
  const f=region(pcm);return {...f,events:f.events.map(e=>({...e,score:e.score/cal[m][0]}))};
 })}})}
 const dev=prepare(dc),ev=prepare(ec);
 const iou=(a,b)=>{const ov=Math.max(0,Math.min(a.t+a.L,b.t+b.L)-Math.max(a.t,b.t));return ov/(a.L+b.L-ov)};
 // Maximum cardinality matching, then greatest total overlap (or least onset error).
 // One event cannot count twice. Equal ties resolve by traversal order.
 function match(truth,seen,criterion){
  let best={pairs:[],weight:-Infinity};
  function visit(i,pairs,used,weight){
   if(i===truth.length){if(pairs.length>best.pairs.length||(pairs.length===best.pairs.length&&weight>best.weight))best={pairs:pairs.slice(),weight};return}
   visit(i+1,pairs,used,weight);
   for(let j=0;j<seen.length;j++){if(used&(1<<j))continue;const a=truth[i],b=seen[j],v=iou(a,b),err=Math.abs(a.t-b.t);
    if(criterion==="overlap"?v<.25:err>(criterion==="strict"?8:40))continue;
    pairs.push([i,j]);visit(i+1,pairs,used|(1<<j),weight+(criterion==="overlap"?v:-err));pairs.pop();
   }
  }
  visit(0,[],0,0);
  return {tp:best.pairs.length,fp:seen.length-best.pairs.length,fn:truth.length-best.pairs.length,pairs:best.pairs,
    onsetError:best.pairs.reduce((s,[i,j])=>s+Math.abs(truth[i].t-seen[j].t),0),
    durationError:best.pairs.reduce((s,[i,j])=>s+Math.abs(truth[i].L-seen[j].L),0),
    iouSum:best.pairs.reduce((s,[i,j])=>s+iou(truth[i],seen[j]),0)};
 }
 const tests=[
  match([{t:0,L:80}],[{t:16,L:80}],"overlap").tp===1,
  match([{t:0,L:80}],[{t:16,L:80}],"strict").tp===0,
  match([{t:0,L:80},{t:40,L:80}],[{t:20,L:80}],"overlap").tp===1,
  match([{t:0,L:80},{t:80,L:80}],[{t:0,L:160},{t:0,L:80}],"overlap").tp===2,
  match([],[{t:0,L:80}],"overlap").fp===1,
  match([{t:0,L:80}],[],"overlap").fn===1,
  match([{t:0,L:80}],[{t:80,L:80}],"overlap").tp===0,
  match([{t:0,L:80}],[{t:0,L:320}],"overlap").tp===1
 ];tests.forEach(v=>ok(v,"matching known answer"));
 // Same stopping rule for pursuit detectors as parent (stop at first below
 // threshold); region scores are already descending.
 function accepted(f,t){const a=[];for(const e of f.events){if(e.score<=t)break;a.push(e)}return a}
 function summary(rows,m,threshold,criterion){
  const a={tp:0,fp:0,fn:0,positive:0,positiveFP:0,nullFalse:0,onsetError:0,durationError:0,iouSum:0};
  for(const row of rows){const b=match(row.truth,accepted(row.fits[m],threshold),criterion);
   ok(b.tp+b.fn===row.truth.length,"truth accounting");
   a.positive+=+(row.truth.length>0);a.positiveFP+=row.truth.length?b.fp:0;a.nullFalse+=+(!row.truth.length&&b.fp>0);
   for(const k of ["tp","fp","fn","onsetError","durationError","iouSum"])a[k]+=b[k];
  }return a;
 }
 // Candidate thresholds at every unique development score, plus reject-all.
 // Threshold selection is on development only; criterion is varied explicitly.
 const groups=[...new Set(ec.map(c=>c.group))],criteria=["strict","overlap"],operating=[];
 for(const criterion of criteria)for(const budget of budgets){
  const receivers=methods.map((name,m)=>{
   const grid=[0,...new Set(dev.flatMap(row=>row.fits[m].events.map(e=>e.score)))].sort((a,b)=>a-b);
   const candidates=grid.map(threshold=>({threshold,...summary(dev,m,threshold,criterion)}));
   const selected=candidates.filter(x=>!x.nullFalse&&x.positiveFP<=budget*x.positive).sort((a,b)=>b.tp-a.tp||a.positiveFP-b.positiveFP||b.threshold-a.threshold)[0];
   ok(!!selected,"reject-all feasible");
   const evaluation=Object.fromEntries(["strict","relaxed","overlap"].map(k=>[k,summary(ev,m,selected.threshold,k)]));
   const byGroup=Object.fromEntries(groups.map(g=>[g,Object.fromEntries(["strict","overlap"].map(k=>[k,summary(ev.filter(row=>row.condition.group===g),m,selected.threshold,k)]))]));
   return {name,selected,evaluation,byGroup,thresholdCount:grid.length};
  });operating.push({criterion,budget,receivers});
 }
 const final=operating.find(o=>o.criterion==="overlap"&&o.budget===.5);
 const rows=ev.map(row=>({...row,metrics:row.fits.map((f,m)=>{const seen=accepted(f,final.receivers[m].selected.threshold);return {seen,strict:match(row.truth,seen,"strict"),overlap:match(row.truth,seen,"overlap")}})}));
 const witnesses=[...new Set([
  rows.findIndex(r=>r.condition.group==="skew-unseen"&&r.metrics.some(m=>m.overlap.tp>m.strict.tp)),
  rows.findIndex(r=>r.condition.group==="mixed"&&r.metrics.some(m=>m.overlap.tp===3)),
  rows.findIndex(r=>r.condition.group==="compound"&&r.metrics.every(m=>m.overlap.tp===0)),
  rows.findIndex(r=>r.condition.null&&r.metrics.some(m=>m.overlap.fp>0)),
  rows.findIndex(r=>r.condition.group==="control"&&r.metrics[3].overlap.tp>r.metrics[1].overlap.tp)
 ].filter(i=>i>=0))];
 const specimens=witnesses.map(i=>({i,pcm:Array.from(make(rows[i].condition).pcm)}));
 return {receipt:{schema:"mhac-presence-boundary-v1",claimClass:"finite synthetic exploratory measurement",parent:"3e53875b60b2bb3518341507ab598f20f51ebdaf",parentBlob:"c419664b6a512520bb5ef1747009f0d2ef00498f",rate,N,E,step,cap,tol,methods,budgets,criteria,cal,development:dc,evaluation:ec,operating,rows,witnesses,assertions},specimens};
}
function cli(){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),out=process.argv[2]||"presence-boundary-output";
 fs.mkdirSync(out,{recursive:true});const {receipt,specimens}=experiment(),hash=b=>crypto.createHash("sha256").update(b).digest("hex");
 receipt.sourceSHA256=hash(fs.readFileSync(__filename));
 const peak=Math.max(1,...specimens.map(s=>s.pcm.reduce((a,x)=>Math.max(a,Math.abs(x)),0))),gain=Math.min(1,Math.floor(.12*32767)/peak);receipt.auditionGain=gain;
 function wav(pcm,g){const b=Buffer.alloc(44+pcm.length*2);b.write("RIFF");b.writeUInt32LE(b.length-8,4);b.write("WAVEfmt ",8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(receipt.rate,24);b.writeUInt32LE(receipt.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write("data",36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((x,j)=>b.writeInt16LE(Math.round(x*g),44+2*j));return b}
 receipt.specimens=specimens.map(({i,pcm})=>{const raw=wav(pcm,1),preview=wav(pcm,gain),name="witness-"+i+".wav",audition="audition-"+i+".wav";fs.writeFileSync(path.join(out,name),raw);fs.writeFileSync(path.join(out,audition),preview);return {i,name,audition,rawSHA256:hash(raw),auditionSHA256:hash(preview)}});
 fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2)+"\n");
 const table=receipt.operating.flatMap(o=>o.receivers.flatMap(r=>Object.entries(r.evaluation).map(([k,v])=>"<tr>"+[o.criterion,o.budget,r.name,k,v.tp,v.fp,v.fn,v.nullFalse].map(x=>"<td>"+x+"</td>").join("")+"</tr>"))).join("");
 const cards=receipt.specimens.map(s=>{const r=receipt.rows[s.i],scale=800/receipt.N;const rect=(t,L,y,c)=>'<rect x="'+(t*scale)+'" y="'+y+'" width="'+(L*scale)+'" height="12" fill="'+c+'" opacity=".65"/>';const lanes=r.truth.map(e=>rect(e.t,e.L,0,"#334155")).join("")+r.metrics.map((m,i)=>m.seen.map(e=>rect(e.t,e.L,20+i*20,["#0e7490","#b45309","#047857","#7c3aed"][i])).join("")).join("");return "<section><h2>"+r.condition.group+" / "+s.i+"</h2><audio controls preload='none' src='"+s.audition+"'></audio><p>Rows: truth, rectangular, symmetric, shape bank, energy region. Horizontal extent = 300 ms.</p><svg viewBox='0 0 800 96' width='100%' role='img' aria-label='True and detected intervals'>"+lanes+"</svg><details><summary>Trace</summary><pre>"+JSON.stringify({condition:r.condition,truth:r.truth,metrics:r.metrics,hashes:s},null,2)+"</pre></details></section>"}).join("");
 fs.writeFileSync(path.join(out,"index.html"),"<!doctype html><meta charset='utf-8'><title>MHAC presence and boundary</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}td,th{padding:.35rem;border-bottom:1px solid #ccc;text-align:right}pre{overflow:auto;background:#eee;padding:1rem}audio{width:100%}</style><h1>Presence versus boundary accuracy</h1><p>Synthetic PCM only. Opt-in playback; begin at low hardware volume. Common attenuation. No human inference. <a href='receipt.json'>Replay receipt</a>.</p><table><thead><tr>"+["Calibration","Budget","Receiver","Scoring","TP","FP","FN","Null false"].map(x=>"<th>"+x+"</th>").join("")+"</tr></thead><tbody>"+table+"</tbody></table>"+cards);
 console.log(JSON.stringify({assertions:receipt.assertions,operating:receipt.operating.map(o=>({criterion:o.criterion,budget:o.budget,receivers:o.receivers.map(r=>({name:r.name,selected:r.selected,evaluation:r.evaluation}))})),specimens:receipt.specimens},null,2));
}
module.exports={experiment};if(require.main===module)cli();
