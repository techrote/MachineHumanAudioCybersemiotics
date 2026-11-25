'use strict';
// MHAC #442 Measurement / shape-aware envelope observation, synthetic only.
// Fixture generator and reference fit/measure adapted verbatim except shape parameter
// from scale-calibrated.cjs at 8b562f603acb1c621d701d8aaeff8369e5439bec, blob 4044edfe8fb3182f878f62c62cdcf952c28130e8.
// No human inference or canonical protocol change. Finite exploratory comparison.
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

 const methods=["rectangular-energy","symmetric-reference","shape-bank"],budgets=[0,.125,.25,.5];
 const bank=(m)=>[80,160,320].flatMap(L=>(m===0?[0]:m===1?[.5]:[.2,.5,.8]).map(shape=>{
   const a=Float64Array.from({length:L},(_,i)=>shape===0?1:shape===.5?(Math.min(i,L-1-i)/(L/2))**2:Math.min(i/(L-1)/shape,(1-i/(L-1))/(1-shape))**2);
   const n=Math.sqrt(dot(a,a)),w=a.map(x=>x/n);return {L,shape,w,sum:w.reduce((s,x)=>s+x,0)};
 }));
 const banks=methods.map((_,m)=>bank(m));
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
  const test=split==="eval",base=test?9100000:7100000,cs=[];
  const groups=test?["control","short","long","mixed","skew-early","skew-late","skew-unseen","missing-guard","noise-step","continuous-tone","compound"]:["control","short","long","mixed","skew-early"];
  for(const group of groups)for(const noise of [300,1200])for(const gain of [.3,1])for(const overlap of [false,true])for(let s=0;s<2;s++){
   cs.push({split,group,seed:base+s+noise*1000+Math.round(gain*10)*100+(overlap?10:0),noise,gain,overlap,guard:["missing-guard","compound"].includes(group),stepNoise:["noise-step","compound"].includes(group),tone:["continuous-tone","compound"].includes(group),shape:group==="skew-early"?.2:group==="skew-late"?.8:group==="skew-unseen"?.35:.5,durations:group==="short"?[80,80,80]:group==="long"?[320,320,320]:["mixed","compound"].includes(group)?[80,160,320]:[160,160,160]});
  }
  for(const group of ["null","null-step","null-tone"])for(const noise of [300,1200])for(let s=0;s<4;s++)cs.push({split,group,seed:base+500000+noise*1000+s,noise,null:true,stepNoise:group==="null-step",tone:group==="null-tone"});
  return cs;
 }
 const dc=conditions("dev"),ec=conditions("eval");
 ok(!ec.some(c=>dc.some(d=>d.seed===c.seed)),"split disjoint");
 const cal=methods.map((_,m)=>{
  const maxima=dc.filter(c=>c.null).map(c=>detect(make(c).pcm,m,null,true).maxima);
  return banks[m].map((h,k)=>Math.max(1,...maxima.map(v=>v[k])));
 });
 // Check actual retained parent reference against generic symmetric implementation.
 // Test null, overlap, low gain, long and asymmetric shapes without tuning either.
 let baselineChecks=0;
 for(const c of [dc[0],dc[5],dc[31],dc[47],dc[71],dc[dc.length-1],ec[0],ec[80]]){
  const pcm=make(c).pcm,a=fit(pcm,4,cal[1]),b=detect(pcm,1,cal[1]);
  ok(a.events.length===b.events.length,"reference event count");
  for(let k=0;k<a.events.length;k++){
   const x=a.events[k],y=b.events[k];
   ok(x.t===y.t&&x.L===y.L&&Math.abs(x.score-y.score)<=1e-10*Math.max(1,x.score),"reference event equivalence");baselineChecks++;
  }
 }
 function prepare(cs){return cs.map(c=>{const {truth,pcm}=make(c);return {condition:c,truth,peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0),fits:methods.map((_,m)=>detect(pcm,m,cal[m]))}})}
 const dev=prepare(dc),ev=prepare(ec);
 function summary(rows,m,threshold,tolerance=tol){
  const a={packets:rows.length,positive:0,tp:0,fp:0,fn:0,positiveFP:0,nullFalse:0,exact:0,durationExact:0,timingError:0,durationError:0,products:0,rectQueries:0,prefixAdds:0};
  for(const row of rows){
   const f=row.fits[m],b=measure(row.truth,f,threshold,tolerance);
   ok(b.tp+b.fn===row.truth.length&&b.tp+b.fp===b.seen.length,"accounting");
   a.positive+=+(row.truth.length>0);a.positiveFP+=row.truth.length?b.fp:0;a.nullFalse+=+(!row.truth.length&&b.fp>0);a.exact+=+(b.fn===0&&b.fp===0);
   for(const k of ["tp","fp","fn","durationExact","timingError","durationError"])a[k]+=b[k];
   for(const k of ["products","rectQueries","prefixAdds"])a[k]+=f[k];
  }
  return a;
 }
 const grid=[...Array.from({length:201},(_,i)=>i*.025),6,8,10,20,50,100,1000,1e9];
 const curves=methods.map((_,m)=>grid.map(threshold=>({threshold,...summary(dev,m,threshold)})));
 const groups=[...new Set(ec.map(c=>c.group))];
 const operating=budgets.map(budget=>({budget,receivers:methods.map((name,m)=>{
  const selected=curves[m].filter(x=>!x.nullFalse&&x.positiveFP<=budget*x.positive).sort((a,b)=>b.tp-a.tp||a.positiveFP-b.positiveFP||b.threshold-a.threshold)[0];ok(!!selected,"feasible");
  const evaluation=Object.fromEntries(groups.map(g=>[g,summary(ev.filter(r=>r.condition.group===g),m,selected.threshold)]));
  evaluation.all=summary(ev,m,selected.threshold);
  return {name,selected,evaluation,relaxed:summary(ev,m,selected.threshold,40)};
 })}));
 const thresholds=operating[3].receivers.map(x=>x.selected.threshold);
 const rows=ev.map(r=>({...r,metrics:r.fits.map((f,m)=>measure(r.truth,f,thresholds[m]))}));
 const witnesses=[...new Set([
  rows.findIndex(r=>r.condition.group==="skew-early"&&r.metrics[2].tp>r.metrics[1].tp),
  rows.findIndex(r=>r.condition.group==="skew-late"&&r.metrics[2].tp>r.metrics[1].tp),
  rows.findIndex(r=>r.condition.group==="skew-unseen"&&r.metrics[2].tp<3),
  rows.findIndex(r=>r.condition.group==="compound"&&r.metrics[2].tp===0),
  rows.findIndex(r=>r.condition.null&&r.metrics[2].fp>0),
  rows.findIndex(r=>r.condition.group==="mixed"&&r.metrics[0].tp>r.metrics[2].tp),
  rows.findIndex(r=>r.condition.group==="control"&&r.metrics[1].tp===3)
 ].filter(i=>i>=0))];
 const specimens=witnesses.map(i=>({i,pcm:Array.from(make(rows[i].condition).pcm)}));
 return {receipt:{schema:"mhac-shape-calibrated-v1",claimClass:"finite synthetic onset detection",parent:"8b562f603acb1c621d701d8aaeff8369e5439bec",parentBlob:"4044edfe8fb3182f878f62c62cdcf952c28130e8",rate,N,E,step,cap,tol,methods,budgets,grid,cal,development:dc,evaluation:ec,curves,operating,rows,witnesses,witnessBudget:.5,baselineChecks,assertions},specimens};
}
function cli(){
 const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
 const out=process.argv[2]||"shape-calibrated-output";fs.mkdirSync(out,{recursive:true});
 const {receipt,specimens}=experiment(),hash=b=>crypto.createHash("sha256").update(b).digest("hex");
 receipt.sourceSHA256=hash(fs.readFileSync(__filename));
 const peak=Math.max(1,...specimens.map(s=>s.pcm.reduce((a,x)=>Math.max(a,Math.abs(x)),0))),gain=Math.min(1,Math.floor(.12*32767)/peak);
 receipt.auditionGain=gain;
 function wav(pcm,g){const b=Buffer.alloc(44+pcm.length*2);b.write("RIFF");b.writeUInt32LE(b.length-8,4);b.write("WAVEfmt ",8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(receipt.rate,24);b.writeUInt32LE(receipt.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write("data",36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((x,j)=>b.writeInt16LE(Math.round(x*g),44+2*j));return b}
 receipt.specimens=specimens.map(({i,pcm})=>{const raw=wav(pcm,1),preview=wav(pcm,gain),name="witness-"+i+".wav",audition="audition-"+i+".wav";fs.writeFileSync(path.join(out,name),raw);fs.writeFileSync(path.join(out,audition),preview);return {i,name,audition,rawSHA256:hash(raw),auditionSHA256:hash(preview)}});
 fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2)+"\n");
 const table=receipt.operating.flatMap(o=>o.receivers.flatMap(r=>Object.entries(r.evaluation).map(([g,v])=>"<tr>"+[o.budget,r.name,g,r.selected.threshold,v.tp,v.fp,v.fn,v.durationExact,v.nullFalse].map(x=>"<td>"+x+"</td>").join("")+"</tr>"))).join("");
 const cards=receipt.specimens.map(s=>{const r=receipt.rows[s.i],scale=800/receipt.N;const rect=(t,L,y,c)=>'<rect x="'+(t*scale)+'" y="'+y+'" width="'+(L*scale)+'" height="12" fill="'+c+'" opacity=".65"/>';const lanes=r.truth.map(e=>rect(e.t,e.L,0,"#334155")).join("")+r.metrics.map((m,i)=>m.seen.map(e=>rect(e.t,e.L,20+i*20,["#0e7490","#b45309","#047857"][i])).join("")).join("");return "<section><h2>"+r.condition.group+" / "+s.i+"</h2><audio controls preload='none' src='"+s.audition+"'></audio><p>Rows: truth, rectangular, symmetric, shape bank. Horizontal extent = 300 ms. Bars show event intervals.</p><svg viewBox='0 0 800 76' width='100%' role='img' aria-label='Ground truth and detected intervals'>"+lanes+"</svg><pre>"+JSON.stringify({condition:r.condition,truth:r.truth,metrics:r.metrics,hashes:s},null,2)+"</pre></section>"}).join("");
 fs.writeFileSync(path.join(out,"index.html"),"<!doctype html><meta charset='utf-8'><title>MHAC shape calibration</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}td,th{padding:.35rem;border-bottom:1px solid #ccc;text-align:right}pre{overflow:auto;background:#eee;padding:1rem}audio{width:100%}</style><h1>Shape-aware event observation</h1><p>Synthetic PCM only. Opt-in playback; start at low hardware volume. Common attenuation across specimens. No human inference. <a href='receipt.json'>Replay receipt</a>.</p><table><thead><tr>"+["Budget","Receiver","Group","Threshold","TP","FP","FN","Duration exact","Null false"].map(x=>"<th>"+x+"</th>").join("")+"</tr></thead><tbody>"+table+"</tbody></table>"+cards);
 console.log(JSON.stringify({assertions:receipt.assertions,baselineChecks:receipt.baselineChecks,operating:receipt.operating,specimens:receipt.specimens},null,2));
}
module.exports={experiment};
if(require.main===module)cli();
