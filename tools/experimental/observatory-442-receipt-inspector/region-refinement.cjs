'use strict';
// Measurement lane #442; synthetic boundary refinement. No human inference.
// Fixture, detector and matching adapted from 35dd1e519daf9154fae1dbd95aa8069a22f6a936 blob d747555d5c06a07dd8931bb464f23aa153aa4b31.
function experiment(){
 const rate=8000,N=2400,E=240000000,step=4,cap=4,tol=8,baseL=160;
 let assertions=0;const ok=(v,m)=>{if(!v)throw Error(m);assertions++};
 function rng(seed){let x=seed>>>0;return ()=>{x=(x+0x6D2B79F5)|0;let z=x;z=Math.imul(z^z>>>15,z|1);z^=z+Math.imul(z^z>>>7,z|61);return ((z^z>>>14)>>>0)/4294967296}}
 const dot=(a,b)=>{let s=0;for(let i=0;i<a.length;i++)s+=a[i]*b[i];return s};
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

 function conditions(split){
  const test=split==="eval",base=test?23100000:21100000,cs=[];
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
 const iou=(a,b)=>{const ov=Math.max(0,Math.min(a.t+a.L,b.t+b.L)-Math.max(a.t,b.t));return ov/(a.L+b.L-ov)};
 // Maximum cardinality matching, then greatest total overlap (or least onset error).
 // One event cannot count twice. Equal ties resolve by traversal order.
 function match(truth,seen,criterion){
  let best={pairs:[],weight:-Infinity};
  function visit(i,pairs,used,weight){
   if(i===truth.length){if(pairs.length>best.pairs.length||(pairs.length===best.pairs.length&&weight>best.weight))best={pairs:pairs.slice(),weight};return}
   visit(i+1,pairs,used,weight);
   for(let j=0;j<seen.length;j++){if(used&(1<<j))continue;const a=truth[i],b=seen[j],v=iou(a,b),err=Math.abs(a.t-b.t);
    if(criterion.startsWith("iou")?v<Number(criterion.slice(3)):err>(criterion==="strict"?8:40))continue;
    pairs.push([i,j]);visit(i+1,pairs,used|(1<<j),weight+(criterion.startsWith("iou")?v:-err));pairs.pop();
   }
  }
  visit(0,[],0,0);
  return {tp:best.pairs.length,fp:seen.length-best.pairs.length,fn:truth.length-best.pairs.length,pairs:best.pairs,
    onsetError:best.pairs.reduce((s,[i,j])=>s+Math.abs(truth[i].t-seen[j].t),0),
    durationError:best.pairs.reduce((s,[i,j])=>s+Math.abs(truth[i].L-seen[j].L),0),
    iouSum:best.pairs.reduce((s,[i,j])=>s+iou(truth[i],seen[j]),0)};
 }

 const methods=["region","low-threshold","symmetric-fit","shape-fit"];
 const criteria=["strict","relaxed","iou0.25","iou0.5","iou0.75"],B=8;
 function bins(pcm){return Array.from({length:N/B},(_,i)=>{let sum=0;for(let j=0;j<B;j++)sum+=pcm[i*B+j]**2;return sum/B})}
 // Boundary-only comparison: same proposals, same threshold. Fixed +/-42 ms
 // fitting window; nonnegative signal amplitude and free constant background.
 // No .35 or .65 shape in the bank. Offline; uses future samples.
 function refine(e,y,m){
  if(m===0)return {...e};
  const peak=Math.floor(e.peak/B),lo=Math.max(0,peak-42),hi=Math.min(y.length,peak+43),n=hi-lo;
  if(m===1){
   const flank=[...y.slice(Math.max(0,peak-42),Math.max(0,peak-22)),...y.slice(Math.min(y.length,peak+23),Math.min(y.length,peak+43))].sort((a,b)=>a-b);
   const b=Math.max(10000,flank[Math.floor(flank.length/2)]??10000),floor=b+.025*Math.max(0,y[peak]-b);
   let a=peak,z=peak+1;while(a>lo&&peak-a<40&&y[a-1]>floor)a--;while(z<hi&&z-peak<41&&y[z]>floor)z++;
   return {...e,t:a*B,L:(z-a)*B};
  }
  let sy=0;for(let i=lo;i<hi;i++)sy+=y[i];const my=sy/n;
  let best=null;
  for(const D of [10,20,40])for(const q of (m===2?[.5]:[.2,.5,.8])){
   const w=Array.from({length:D},(_,j)=>Math.min((j+.5)/D/q,(1-(j+.5)/D)/(1-q))**2);
   const sx=w.reduce((a,b)=>a+b,0),xx=w.reduce((a,b)=>a+b*b,0)-sx*sx/n;
   for(let t=Math.max(lo,peak-D+1);t<=Math.min(peak,hi-D);t++){
    let xy=0;for(let j=0;j<D;j++)xy+=(y[t+j]-my)*w[j];
    const amplitude=Math.max(0,xy/xx),improvement=amplitude*amplitude*xx;
    const background=my-amplitude*sx/n;
    if(background<0)continue;
    if(!best||improvement>best.improvement)best={t:t*B,L:D*B,shape:q,improvement,amplitude,background};
   }
  }
  return best?{...e,...best}: {...e,fallback:true};
 }
 const dc=conditions("dev"),ec=conditions("eval");
 ok(!ec.some(c=>dc.some(d=>d.seed===c.seed)),"disjoint splits");
 function prepare(cs){return cs.map(c=>{const {truth,pcm}=make(c);return {condition:c,truth,pcm,proposals:region(pcm).events}})}
 const dev=prepare(dc),ev=prepare(ec);
 const grid=[0,...new Set(dev.flatMap(r=>r.proposals.map(e=>e.score)))];
 function devScore(threshold){
  let tp=0,positiveFP=0,nullFalse=0,positive=0;
  for(const r of dev){const b=match(r.truth,r.proposals.filter(e=>e.score>threshold),"iou0.25");tp+=b.tp;positive+=+(r.truth.length>0);positiveFP+=r.truth.length?b.fp:0;nullFalse+=+(!r.truth.length&&b.fp>0)}
  return {threshold,tp,positiveFP,nullFalse,positive};
 }
 const selected=grid.map(devScore).filter(a=>a.nullFalse===0&&a.positiveFP<=.5*a.positive).sort((a,b)=>b.tp-a.tp||a.positiveFP-b.positiveFP||b.threshold-a.threshold)[0];
 ok(!!selected,"threshold feasible");
 const rows=ev.map(r=>{
  const proposals=r.proposals.filter(e=>e.score>selected.threshold),y=bins(r.pcm);
  const fits=methods.map((name,m)=>proposals.map(e=>refine(e,y,m)));
  for(const f of fits){ok(f.length===proposals.length,"same proposals");for(const e of f)ok(e.t>=0&&e.L>0&&e.t+e.L<=N,"fit interval bounds")}
  const metrics=fits.map(f=>Object.fromEntries(criteria.map(k=>[k,match(r.truth,f,k)])));
  for(const mm of metrics)for(const b of Object.values(mm))ok(b.tp+b.fn===r.truth.length&&b.tp+b.fp===proposals.length,"one-to-one accounting");
  return {condition:r.condition,truth:r.truth,proposals,fits,metrics};
 });
 function aggregate(rows){
  const result=[];
  for(let m=0;m<methods.length;m++){
   const metrics={};
   for(const k of criteria){
    const a={tp:0,fp:0,fn:0,onsetError:0,durationError:0,iouSum:0};
    for(const r of rows)for(const key of Object.keys(a))a[key]+=r.metrics[m][k][key];
    metrics[k]=a;
   }
   result.push({name:methods[m],metrics});
  }
  return result;
 }
 const results=aggregate(rows),byGroup={};
 for(const g of new Set(ec.map(c=>c.group)))byGroup[g]=aggregate(rows.filter(r=>r.condition.group===g));
 const seedBlocks=[...new Set(ec.filter(c=>!c.null).map(c=>c.seed))].map(seed=>({seed,results:aggregate(rows.filter(r=>r.condition.seed===seed))}));
 const witnesses=[...new Set([
 rows.findIndex(r=>r.metrics[3]["iou0.75"].tp>r.metrics[0]["iou0.75"].tp),
 rows.findIndex(r=>r.metrics[3]["iou0.75"].tp<r.metrics[0]["iou0.75"].tp),
 rows.findIndex(r=>r.condition.group==="skew-unseen"&&r.metrics[0]["iou0.25"].tp>0),
 rows.findIndex(r=>r.condition.group==="compound"&&r.metrics.every(m=>m["iou0.25"].tp===0)),
 rows.findIndex(r=>r.condition.null&&r.proposals.length>0)
 ].filter(i=>i>=0))];
 const specimens=witnesses.map(i=>({i,pcm:Array.from(ev[i].pcm)}));
 const exact=Array.from({length:N/B},()=>10000);for(let j=0;j<20;j++)exact[100+j]+=100000*Math.min((j+.5)/20/.2,(1-(j+.5)/20)/.8)**2;
 const fitted=refine({peak:104*B,t:100*B,L:20*B,score:1},exact,3);
 ok(fitted.t===800&&fitted.L===160&&fitted.shape===.2,"exact shape known answer");
 ok(match([{t:0,L:80},{t:40,L:80}],[{t:20,L:80}],"iou0.25").tp===1,"one to one");
 return {receipt:{schema:"mhac-region-refinement-v1",claimClass:"finite synthetic exploratory measurement",parent:"35dd1e519daf9154fae1dbd95aa8069a22f6a936",parentBlob:"d747555d5c06a07dd8931bb464f23aa153aa4b31",rate,N,methods,criteria,selected,development:dc,evaluation:ec,results,byGroup,seedBlocks,rows,witnesses,assertions},specimens};
}
function cli(){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),out=process.argv[2]||"region-refinement-output";
 fs.mkdirSync(out,{recursive:true});const {receipt,specimens}=experiment(),hash=b=>crypto.createHash("sha256").update(b).digest("hex");
 receipt.sourceSHA256=hash(fs.readFileSync(__filename));
 const peak=Math.max(1,...specimens.map(s=>s.pcm.reduce((a,x)=>Math.max(a,Math.abs(x)),0))),gain=Math.min(1,Math.floor(.12*32767)/peak);receipt.auditionGain=gain;
 function wav(pcm,g){const b=Buffer.alloc(44+pcm.length*2);b.write("RIFF");b.writeUInt32LE(b.length-8,4);b.write("WAVEfmt ",8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(receipt.rate,24);b.writeUInt32LE(receipt.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write("data",36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((x,j)=>b.writeInt16LE(Math.round(x*g),44+2*j));return b}
 receipt.specimens=specimens.map(({i,pcm})=>{const raw=wav(pcm,1),preview=wav(pcm,gain),name="witness-"+i+".wav",audition="audition-"+i+".wav";fs.writeFileSync(path.join(out,name),raw);fs.writeFileSync(path.join(out,audition),preview);return {i,name,audition,rawSHA256:hash(raw),auditionSHA256:hash(preview)}});
 fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2)+"\n");

 const table=receipt.results.flatMap(r=>Object.entries(r.metrics).map(([k,v])=>"<tr>"+[r.name,k,v.tp,v.fp,v.fn,v.tp?(v.onsetError/v.tp/8).toFixed(2):"-",v.tp?(v.durationError/v.tp/8).toFixed(2):"-"].map(x=>"<td>"+x+"</td>").join("")+"</tr>")).join("");
 const cards=receipt.specimens.map(s=>{
  const r=receipt.rows[s.i],scale=800/receipt.N;
  const rect=(t,L,y,c)=>'<rect x="'+(t*scale)+'" y="'+y+'" width="'+(L*scale)+'" height="12" fill="'+c+'" opacity=".65"/>';
  const lanes=r.truth.map(e=>rect(e.t,e.L,0,"#334155")).join("")+r.fits.map((f,i)=>f.map(e=>rect(e.t,e.L,20+i*20,["#0e7490","#b45309","#047857","#7c3aed"][i])).join("")).join("");
  return "<section><h2>"+r.condition.group+" / "+s.i+"</h2><audio controls preload='none' src='"+s.audition+"'></audio><p>Rows: truth, region, low threshold, symmetric fit, shape fit. Horizontal extent = 300 ms.</p><svg viewBox='0 0 800 96' width='100%' role='img' aria-label='True and fitted intervals'>"+lanes+"</svg><details><summary>Trace</summary><pre>"+JSON.stringify({condition:r.condition,truth:r.truth,fits:r.fits,metrics:r.metrics,hashes:s},null,2)+"</pre></details></section>";
 }).join("");
 fs.writeFileSync(path.join(out,"index.html"),"<!doctype html><meta charset='utf-8'><title>MHAC boundary refinement</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}td,th{padding:.35rem;border-bottom:1px solid #ccc;text-align:right}pre{overflow:auto;background:#eee;padding:1rem}audio{width:100%}</style><h1>Boundary refinement on fixed proposals</h1><p>Synthetic PCM only. Opt-in playback; begin at low hardware volume. Common attenuation. No human inference. <a href='receipt.json'>Replay receipt</a>.</p><table><thead><tr>"+["Receiver","Scoring","TP","FP","FN","MAE onset ms","MAE duration ms"].map(x=>"<th>"+x+"</th>").join("")+"</tr></thead><tbody>"+table+"</tbody></table>"+cards);
 console.log(JSON.stringify({assertions:receipt.assertions,selected:receipt.selected,results:receipt.results,specimens:receipt.specimens},null,2));
}
module.exports={experiment};if(require.main===module)cli();
