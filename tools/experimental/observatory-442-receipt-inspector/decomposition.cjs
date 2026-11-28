"use strict";
// MHAC Measurement lane #442. Synthetic-only. Parent adaptive renderer copied verbatim from pinned adaptive.html (see README).
const adaptiveLab=function adaptiveLab(core){
"use strict";
const rate=8000,L=160,N=3200, stride=4, tol=8, separation=160;
const specs=["triangle500","triangle800","sine650"];
const energy=x=>x.reduce((s,v)=>s+v*v,0);
function template(name){
 const frequency={triangle500:500,triangle800:800,sine650:650}[name];
 if(!frequency)throw Error("unknown family");
 const raw=Array.from({length:L},(_,i)=>{const phase=i*frequency/rate%1;return Math.min(i,L-1-i)/(L/2)*(name==="sine650"?Math.sin(2*Math.PI*phase):1-4*Math.abs(phase-.5));});
 const scale=Math.sqrt(240000000/energy(raw));
 return Int16Array.from(raw,x=>Math.round(x*scale));
}
const kernels=specs.map(template), energies=kernels.map(energy);
function rng(seed){let x=seed>>>0;return ()=>{x=(x+0x6D2B79F5)|0;let z=x;z=Math.imul(z^z>>>15,z|1);z^=z+Math.imul(z^z>>>7,z|61);return ((z^z>>>14)>>>0)/4294967296;};}
function make(c){
 const rand=rng(c.seed), signal=new Int32Array(N),pcm=new Int16Array(N);
 let truth=[];
 if(c.family!=="null"){
 const row=core.condition(144,89,rate,200,"fixed").rows[c.deleted-1].samples.slice();
 if(c.spacing==="overlap")row[1]=row[0]+96;
 truth=row.map(t=>Math.round(800+(t-800)*(1+c.drift)+(2*rand()-1)*8));
 const k=kernels[specs.indexOf(c.family)];
 for(const t of truth)for(let j=0;j<L;j++)signal[t+j]+=Math.round(c.gain*k[j]);
 }
 let peak=0,ne=0;
 for(let i=0;i<N;i++){const noise=Math.round((2*rand()-1)*c.noise);ne+=noise*noise;const v=signal[i]+noise;if(Math.abs(v)>32767)throw Error("clip");pcm[i]=v;peak=Math.max(peak,Math.abs(v));}
 return {truth,pcm,peak,snr:ne&&truth.length?10*Math.log10(energy(signal)/ne):null};
}
const names=["absolute-single","cosine-single","cosine-bank"];
function score(pcm){
 const prefix=new Float64Array(N+1);for(let i=0;i<N;i++)prefix[i+1]=prefix[i]+pcm[i]*pcm[i];
 const rows=names.map(()=>[]);
 for(let t=0;t<=N-L;t+=stride){
 let a=0,b=0;for(let j=0;j<L;j++){a+=pcm[t+j]*kernels[0][j];b+=pcm[t+j]*kernels[1][j];}
 const e=prefix[t+L]-prefix[t],ca=e?a/Math.sqrt(e*energies[0]):0,cb=e?b/Math.sqrt(e*energies[1]):0;
 rows[0].push(a/energies[0]);rows[1].push(ca);rows[2].push(Math.max(ca,cb));
 }
 return rows;
}
function detect(s,threshold){
 const candidates=[];for(let i=0;i<s.length;i++)if(s[i]>threshold&&s[i]>=(s[i-1]??-Infinity)&&s[i]>(s[i+1]??-Infinity))candidates.push([i*stride,s[i]]);
 candidates.sort((a,b)=>b[1]-a[1]||a[0]-b[0]);
 const chosen=[];for(const [t] of candidates)if(chosen.every(v=>Math.abs(t-v)>=separation))chosen.push(t);
 return chosen.sort((a,b)=>a-b);
}
function match(truth,seen){
 let i=0,j=0,tp=0,abs=0;const pairs=[];
 while(i<truth.length&&j<seen.length){if(seen[j]<truth[i]-tol)j++;else if(truth[i]<seen[j]-tol)i++;else{tp++;abs+=Math.abs(seen[j]-truth[i]);pairs.push([truth[i++],seen[j++]]);}}
 return {tp,fp:seen.length-tp,fn:truth.length-tp,abs,pairs};
}
function wave(pcm){const b=new Uint8Array(44+pcm.length*2),v=new DataView(b.buffer);const str=(o,s)=>{for(let i=0;i<s.length;i++)b[o+i]=s.charCodeAt(i);};str(0,"RIFF");v.setUint32(4,b.length-8,true);str(8,"WAVE");str(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);str(36,"data");v.setUint32(40,pcm.length*2,true);for(let i=0;i<pcm.length;i++)v.setInt16(44+2*i,pcm[i],true);return b;}
const noiseLevels=[300,1200], gains=[.3,1], rocQuantiles=[.5,.75,.9,.95,1];
function nulls(base){return noiseLevels.flatMap((noise,n)=>Array.from({length:24},(_,i)=>({family:"null",noise,gain:0,seed:base+n*100+i,drift:0,spacing:"none",deleted:0}))); }
function positives(){const out=[];for(const family of specs)for(const gain of gains)for(const noise of noiseLevels)for(const spacing of ["separated","overlap"])for(let i=0;i<4;i++)out.push({family,gain,noise,spacing,seed:0xA7100000+i,drift:i%2?0.005:-0.005,deleted:i+1});return out;}
const quantile=(x,q)=>x.slice().sort((a,b)=>a-b)[Math.ceil(x.length*q)-1];
function run(){
 let assertions=0;const ok=(b,m)=>{if(!b)throw Error(m);assertions++;};
 const dev=nulls(0xD3000000),evaluation=[...nulls(0xE5000000),...positives()];
 ok(new Set(dev.map(x=>x.seed)).size===48,"dev uniqueness");
 ok(evaluation.every(c=>!dev.some(d=>c.seed===d.seed)),"split");
 ok(specs.every((_,i)=>Math.abs(energies[i]/240000000-1)<.001),"energy match");
 const prior=core.tests();ok(prior.status==="PASS","parent core");
 const maxScores=dev.map(c=>score(make(c).pcm).map(a=>Math.max(...a)));
 const thresholds=names.map((_,i)=>rocQuantiles.map(q=>quantile(maxScores.map(x=>x[i]),q)));
 const detectors=[{name:"fixed .55",type:0,threshold:.55},...names.flatMap((name,type)=>rocQuantiles.map((q,j)=>({name,type,q,threshold:thresholds[type][j]})))];
 const rows=[],summary={};let maxPeak=0;
 for(const c of evaluation){
 const a=make(c),s=score(a.pcm);maxPeak=Math.max(maxPeak,a.peak);ok(a.peak<10000,"digital peak");
 ok(a.truth.every((v,i)=>v>=0&&v+L<=N&&(i===0||v>a.truth[i-1])),"truth range");
 const outcomes=detectors.map(d=>{
 const seen=detect(s[d.type],d.threshold),m=match(a.truth,seen);ok(m.tp+m.fn===a.truth.length&&m.tp+m.fp===seen.length,"matching partition");ok(seen.every((x,i)=>x%stride===0&&(i===0||x-seen[i-1]>=separation)),"NMS");
 const k=[c.family,c.gain,c.noise,c.spacing,d.name,d.q??"fixed"].join("/");
 const agg=summary[k]??={n:0,tp:0,fp:0,fn:0,packetsWithFalse:0,exact:0,abs:0};
 agg.n++;agg.tp+=m.tp;agg.fp+=m.fp;agg.fn+=m.fn;agg.abs+=m.abs;agg.packetsWithFalse+=Number(m.fp>0);agg.exact+=Number(m.fp===0&&m.fn===0);
 return {seen,...m};
 });
 rows.push({condition:c,truth:a.truth,snrDb:a.snr,peak:a.peak,sha256:core.sha256(wave(a.pcm)),outcomes});
 }
 for(const d of detectors.filter(x=>x.q)){const count=maxScores.filter(s=>s[d.type]>d.threshold).length;ok(count<=Math.floor(48*(1-d.q)+1e-9),"development false alarm bound");}
 for(const family of specs)for(const sign of [-1,1])ok(rows.filter(x=>x.condition.family===family&&Math.sign(x.condition.drift)===sign).length===16,"balanced drift");
 ok(match([10,20],[11,19]).tp===2&&match([10],[100]).fp===1,"matching examples");
 ok(rows.length===144,"evaluation count");
 return {schema:"mhac-adaptive-observation-v1",claimClass:"synthetic detector measurement; no human evidence",parent:"bec8b0f45283036a1ed580960108809da6d52382",source:"07fb2f67a5a2cf26312699410f00152033cae843",rate,L,N,stride,tol,separation,specs,energies,dev,devMaxScores:maxScores,detectors,rows,summary,maxPeak,assertions,prior};
}
return {make,score,detect,match,wave,run,rate,L,N,templates:specs};
};

function decomposition(core, prior) {
"use strict";
const rate=8000,L=160,N=3200,stride=4,tol=8,cap=4;
const families=["triangle500","triangle800","sine650"];
const energy=a=>a.reduce((s,x)=>s+x*x,0);
function template(f){const raw=Array.from({length:L},(_,i)=>{const phase=i*f/rate%1;return Math.min(i,L-1-i)/(L/2)*(1-4*Math.abs(phase-.5));});const scale=Math.sqrt(240000000/energy(raw));return Float64Array.from(raw,x=>Math.round(x*scale));}
const kernels=[500,800].map(template),es=kernels.map(energy);
const methods=[{name:"independent-20ms",sep:160,subtract:false},{name:"independent-5ms",sep:40,subtract:false},{name:"residual-5ms",sep:40,subtract:true}];
const grid=[.05,.075,.1,.125,.15,.175,.2,.25,.3,.4,.55];
function scan(x,chosen,sep){let best=null;for(let t=0;t<=N-L;t+=stride){if(chosen.some(e=>Math.abs(t-e.t)<sep))continue;for(let k=0;k<2;k++){let dot=0;const h=kernels[k];for(let j=0;j<L;j++)dot+=x[t+j]*h[j];const amp=dot/es[k];if(amp>0&&(!best||amp>best.amp))best={t,k,amp};}}return best;}
function path(pcm,m){let x=Float64Array.from(pcm),events=[],residual=energy(x),ops=0;
 for(let i=0;i<cap;i++){const e=scan(x,events,m.sep);ops++;if(!e)break;
 const prev=residual;if(m.subtract){for(let j=0;j<L;j++)x[e.t+j]-=e.amp*kernels[e.k][j];residual=energy(x);}
 events.push({...e,drop:m.subtract?prev-residual:null,residual:m.subtract?residual:null});
 }return {events,scans:ops,initialEnergy:energy(pcm)};}
function choose(path,threshold){const events=[];for(const e of path.events){if(e.amp<=threshold)break;events.push(e);}return events;}
function evaluate(a,p,threshold){const events=choose(p,threshold),seen=events.map(e=>e.t).sort((a,b)=>a-b);return {seen,...prior.match(a.truth,seen),events};}
function conditions(base,count,includeUnseen){const out=[];for(const noise of [300,1200])for(let i=0;i<12;i++)out.push({family:"null",noise,gain:0,seed:base+0x1000+noise*16+i,drift:0,spacing:"none",deleted:0});
 for(const family of families.slice(0,includeUnseen?3:2))for(const gain of [.3,1])for(const noise of [300,1200])for(const spacing of ["separated","overlap"])for(let i=0;i<count;i++)out.push({family,gain,noise,spacing,seed:base+i,drift:i%2?.005:-.005,deleted:i%4+1});return out;}
function totals(rows,i,threshold){const result={tp:0,fp:0,fn:0,nullFalse:0,nullPackets:0,exactPositive:0,positivePackets:0,sepTP:0,overTP:0,sepTruth:0,overTruth:0,unseenTP:0,unseenTruth:0};
 for(const row of rows){const m=evaluate(row.a,row.paths[i],threshold),c=row.c;result.tp+=m.tp;result.fp+=m.fp;result.fn+=m.fn;if(c.family==="null"){result.nullPackets++;result.nullFalse+=+(m.fp>0);}else{result.positivePackets++;result.exactPositive+=+(m.fp===0&&m.fn===0);if(c.spacing==="overlap"){result.overTP+=m.tp;result.overTruth+=row.a.truth.length;}else{result.sepTP+=m.tp;result.sepTruth+=row.a.truth.length;}if(c.family==="sine650"){result.unseenTP+=m.tp;result.unseenTruth+=row.a.truth.length;}}}
 return result;}
function run(){let assertions=0;const ok=(v,m)=>{if(!v)throw Error(m);assertions++;};
 const dev=conditions(0xB4010000,4,false),test=conditions(0xC5020000,4,true);
 ok(test.every(c=>!dev.some(d=>d.seed===c.seed)),"disjoint seed sets");
 const makeRows=cs=>cs.map(c=>{const a=prior.make(c),paths=methods.map(m=>path(a.pcm,m));ok(a.peak<10000,"PCM bound");for(const p of paths){ok(p.events.length<=cap,"cap");for(const e of p.events){ok(e.t%stride===0&&e.t+L<=N,"range");if(e.drop!==null){ok(e.drop>=-1e-5,"energy nonincrease");ok(Math.abs(e.drop-e.amp*e.amp*es[e.k])<.01,"projection energy identity");}}}return {c,a,paths};});
 const d=makeRows(dev),e=makeRows(test);
 const calibration=methods.map((m,i)=>grid.map(threshold=>{const z=totals(d,i,threshold);return {threshold,...z,f1:2*z.tp/(2*z.tp+z.fp+z.fn)};}));
 // Fixed development-only selection: maximise F1 with <= 2/24 null packets, tie to higher threshold.
 const selected=calibration.map(arr=>arr.filter(x=>x.nullFalse<=2).sort((a,b)=>b.f1-a.f1||b.threshold-a.threshold)[0]);
 ok(selected.every(Boolean),"feasible calibration");
 const summary=methods.map((m,i)=>({method:m.name,threshold:selected[i].threshold,development:selected[i],evaluation:totals(e,i,selected[i].threshold)}));
 const rows=e.map(row=>{const outcomes=row.paths.map((p,i)=>{const q=evaluate(row.a,p,selected[i].threshold);ok(q.tp+q.fn===row.a.truth.length&&q.tp+q.fp===q.seen.length,"partition");return q;});return {condition:row.c,truth:row.a.truth,peak:row.a.peak,sha256:core.sha256(prior.wave(row.a.pcm)),initialEnergy:row.paths[0].initialEnergy,outcomes};});
 const clean={family:"triangle500",gain:1,noise:0,spacing:"overlap",seed:123,drift:0,deleted:1},a=prior.make(clean),p=path(a.pcm,methods[2]);
 ok(evaluate(a,p,.2).tp>=2,"clean overlapping witness");
 const witnesses=[rows.findIndex(r=>r.condition.spacing==="overlap"&&r.outcomes[2].tp>r.outcomes[0].tp),rows.findIndex(r=>r.condition.family!=="null"&&r.outcomes[2].fp>r.outcomes[0].fp),rows.findIndex(r=>r.condition.family==="sine650"),rows.findIndex(r=>r.condition.family==="null")];
 ok(witnesses.every(i=>i>=0),"retained witness classes");
 return {schema:"mhac-observatory-decomposition-v1",claimClass:"synthetic computational measurement; no human evidence",parent:"cd0e7ec2265a6657fcd31f6ae2a18f504053b66c",source:"07fb2f67a5a2cf26312699410f00152033cae843",rate,L,N,stride,tol,cap,methods,grid,dev,test,calibration,summary,rows,witnesses,assertions};
}
return {run,path,evaluate,methods,rate,make:prior.make,wave:prior.wave};
}

if(typeof module!=="undefined"&&module.exports){const core=require("./core.js");const lab=decomposition(core,adaptiveLab(core));module.exports=lab;if(require.main===module){const fs=require("node:fs"),path=require("node:path"),out=process.argv[2]||"decomposition-output";fs.mkdirSync(out,{recursive:true});const receipt=lab.run();fs.writeFileSync(path.join(out,"receipt.json"),JSON.stringify(receipt,null,2)+"\n");for(const i of receipt.witnesses){const row=receipt.rows[i],bytes=lab.wave(lab.make(row.condition).pcm);if(core.sha256(bytes)!==row.sha256)throw Error("stimulus hash mismatch");fs.writeFileSync(path.join(out,"witness-"+i+".wav"),bytes);}console.log(JSON.stringify({assertions:receipt.assertions,summary:receipt.summary},null,2));}}
