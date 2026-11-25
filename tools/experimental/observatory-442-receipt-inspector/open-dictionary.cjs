'use strict';
// MHAC #442 Measurement lane; synthetic only. New standalone receiver comparison, not reuse of joint-refit.
// Fixed/wide bank share pursuit; energy-envelope fits squared PCM minus leading guard noise estimate.
// All methods use same 4-sample grid, 5 ms exclusion, cap 4, 1 ms matching, matched development budget.
// Calibration only known triangles and null; evaluation includes unseen frequency and waveform families.
function experiment(){
 const rate=8000,N=2400,L=160,E=240000000,step=4,cap=4,tol=8,methods=["fixed-bank","wide-bank","energy-envelope"],budgets=[0,.125,.25,.5];
 let assertions=0;function ok(v,m){if(!v)throw Error(m);assertions++}
 const dot=(a,b)=>{let s=0;for(let i=0;i<a.length;i++)s+=a[i]*b[i];return s};
 const norm=a=>{const n=Math.sqrt(dot(a,a));return a.map(x=>x/n)};
 const env=Float64Array.from({length:L},(_,i)=>Math.min(i,L-1-i)/(L/2));
 const env2=norm(env.map(x=>x*x));
 function rng(seed){let x=seed>>>0;return ()=>{x=(x+0x6D2B79F5)|0;let z=x;z=Math.imul(z^z>>>15,z|1);z^=z+Math.imul(z^z>>>7,z|61);return ((z^z>>>14)>>>0)/4294967296}}
 function shape(f,phase,family,random){return norm(env.map((v,i)=>{
  let p=(i*f/rate+phase)%1;
  if(family==="chirp")p=(phase+(430*i+(1000-430)*i*i/(2*(L-1)))/rate)%1;
  return v*(family==="triangle"?1-4*Math.abs(p-.5):family==="burst"?2*random()-1:Math.sin(2*Math.PI*p));
 }))}
 const bank=Array.from({length:9},(_,k)=>{const f=300+100*k,a=shape(f,0,"triangle"),b=shape(f,.25,"triangle"),ab=dot(a,b);return {f,a,b:norm(b.map((x,i)=>x-ab*a[i]))}});
 for(const h of bank)ok(Math.abs(dot(h.a,h.b))<1e-12&&Math.abs(dot(h.a,h.a)-1)<1e-12&&Math.abs(dot(h.b,h.b)-1)<1e-12,"orthonormal bank");
 function make(c){const random=rng(c.seed),waveRand=rng(c.seed+17777),raw=new Float64Array(N),pcm=new Int16Array(N);const truth=c.family==="null"?[]:[300+Math.floor(random()*100),0,1800+Math.floor(random()*100)];
 if(truth.length){truth[1]=truth[0]+(c.overlap?96:420)+Math.floor(random()*9)-4;
 for(let k=0;k<3;k++){const h=shape(c.f,c.phases[k],c.family,waveRand);ok(Math.abs(dot(h,h)-1)<1e-12,"equal isolated energy");for(let j=0;j<L;j++)raw[truth[k]+j]+=Math.sqrt(E)*c.gain*h[j]}}
 for(let i=0;i<N;i++){const v=Math.round(raw[i]+(2*random()-1)*c.noise);if(Math.abs(v)>=32768)throw Error("clipping");pcm[i]=v}return {truth,pcm}}
 function fit(pcm,method){const envelope=method===2,indices=method===0?[2,5]:Array.from({length:9},(_,k)=>k),r=Float64Array.from(pcm);let operations=0;
 if(envelope){let mean=0;for(let i=0;i<L;i++)mean+=r[i]*r[i];mean/=L;for(let i=0;i<N;i++)r[i]=r[i]*r[i]-mean}
 const events=[];
 for(let iter=0;iter<cap;iter++){
  let best=null;
  for(let t=0;t<=N-L;t+=step){if(events.some(e=>Math.abs(e.t-t)<40))continue;
   if(envelope){let a=0;for(let j=0;j<L;j++)a+=r[t+j]*env2[j];operations+=L;const score=Math.max(0,a)/E;if(!best||score>best.score)best={t,k:-1,a:Math.max(0,a),b:0,score};}
   else for(const k of indices){const h=bank[k];let a=0,b=0;for(let j=0;j<L;j++){a+=r[t+j]*h.a[j];b+=r[t+j]*h.b[j]}operations+=2*L;const score=(a*a+b*b)/E;if(!best||score>best.score)best={t,k,a,b,score}}
  }
  if(!best||best.score<=0)break;
  const before=dot(r,r);
  for(let j=0;j<L;j++)r[best.t+j]-=envelope?best.a*env2[j]:best.a*bank[best.k].a[j]+best.b*bank[best.k].b[j];
  ok(dot(r,r)<=before+Math.max(1e-3,1e-12*before),"residual descent");
  events.push(best)
 }return {events,operations}}
 function measure(truth,fit,threshold){const seen=[];for(const e of fit.events){if(e.score<=threshold)break;seen.push(e.t)}seen.sort((a,b)=>a-b);
 let i=0,j=0,tp=0,abs=0;while(i<truth.length&&j<seen.length){if(seen[j]<truth[i]-tol)j++;else if(truth[i]<seen[j]-tol)i++;else{tp++;abs+=Math.abs(truth[i++]-seen[j++])}}return {seen,tp,fp:seen.length-tp,fn:truth.length-tp,abs}}
 function conditions(test){const base=test?981000:971000,cs=[];for(const noise of [300,1200])for(let i=0;i<12;i++)cs.push({group:"null",family:"null",noise,seed:base+1000+noise+i});
 const families=[["known","triangle",500],["known","triangle",800],...(test?[["offgrid","triangle",575],["offgrid","triangle",925],["novel-sine","sine",650],["novel-chirp","chirp",0],["novel-burst","burst",0]]:[])];
 for(const [group,family,f] of families)for(const gain of [.3,1])for(const noise of [300,1200])for(const overlap of [false,true])for(let i=0;i<(test?4:3);i++)cs.push({group,family,f,gain,noise,overlap,phases:test?[.093,.417,.827]:[.21,.49,.72],seed:base+i});return cs}
 const dc=conditions(false),ec=conditions(true);ok(!ec.some(c=>dc.some(d=>c.seed===d.seed)),"disjoint seeds");
 function prep(cs){return cs.map(c=>{const {truth,pcm}=make(c),fits=methods.map((_,m)=>fit(pcm,m));return {c,truth,peak:pcm.reduce((a,b)=>Math.max(a,Math.abs(b)),0),fits}})}
 const dev=prep(dc),ev=prep(ec),grid=[...Array.from({length:201},(_,i)=>i/200),2,4,10,100];
 function agg(rows,m,t,filter=()=>true){const z={packets:0,tp:0,fp:0,fn:0,exact:0,nullFalse:0,positiveFP:0,positivePackets:0,operations:0,absSamples:0};for(const r of rows){if(!filter(r))continue;const a=measure(r.truth,r.fits[m],t);ok(a.tp+a.fn===r.truth.length&&a.tp+a.fp===a.seen.length,"partition");z.packets++;for(const k of ["tp","fp","fn"])z[k]+=a[k];z.exact+=+(a.fp===0&&a.fn===0);z.operations+=r.fits[m].operations;z.absSamples+=a.abs;if(r.truth.length){z.positiveFP+=a.fp;z.positivePackets++}else z.nullFalse+=+(a.fp>0)}return z}
 const curves=methods.map((_,m)=>grid.map(threshold=>({threshold,...agg(dev,m,threshold)})));
 const groups=["known","offgrid","novel-sine","novel-chirp","novel-burst","null"];
 const operating=budgets.map(budget=>({budget,receivers:methods.map((name,m)=>{const selected=curves[m].filter(x=>x.nullFalse===0&&x.positiveFP<=budget*x.positivePackets).sort((a,b)=>b.tp-a.tp||a.positiveFP-b.positiveFP||b.threshold-a.threshold)[0];ok(!!selected,"feasible");
 const evaluation=Object.fromEntries(groups.map(g=>[g,agg(ev,m,selected.threshold,r=>r.c.group===g)]));evaluation.all=agg(ev,m,selected.threshold);evaluation.overlap=agg(ev,m,selected.threshold,r=>r.c.overlap===true);evaluation.separated=agg(ev,m,selected.threshold,r=>r.c.overlap===false);return {name,selected,evaluation}})}));
 const chosen=operating[3].receivers.map(r=>r.selected.threshold);
 const rows=ev.map(r=>({condition:r.c,truth:r.truth,peak:r.peak,fit:r.fits.map((f,m)=>({events:f.events,operations:f.operations,...measure(r.truth,f,chosen[m])}))}));
 const witnesses=[...new Set([rows.findIndex(r=>r.condition.group==="offgrid"&&r.fit[1].tp>r.fit[0].tp),rows.findIndex(r=>r.condition.group==="novel-burst"&&r.fit[2].tp>r.fit[1].tp),rows.findIndex(r=>r.condition.group==="novel-chirp"&&r.fit[2].fp>0),rows.findIndex(r=>r.condition.group==="null"),rows.findIndex(r=>r.condition.group==="known"&&r.fit[1].fn>0)].filter(i=>i>=0))];ok(witnesses.length>=3,"witness count");
 // Return sample arrays only for deterministic CLI export; receipts contain replay conditions.
 const specimens=witnesses.map(i=>({i,pcm:Array.from(make(rows[i].condition).pcm)}));
 return {receipt:{schema:"mhac-open-dictionary-v1",claimClass:"finite synthetic detector comparison",parent:"353ebec86c3d7c263ad7d7e4b971da772c5425cb",rate,N,L,E,step,cap,tol,methods,budgets,grid,development:dc,evaluation:ec,curves,operating,rows,witnesses,witnessBudget:.5,assertions},specimens};
}

module.exports={experiment};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
 const out=process.argv[2]||'open-dictionary-output';fs.mkdirSync(out,{recursive:true});
 const {receipt,specimens}=experiment(),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 receipt.sourceSHA256=hash(fs.readFileSync(__filename));
 receipt.specimens=specimens.map(({i,pcm})=>{
  const b=Buffer.alloc(44+pcm.length*2);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(receipt.rate,24);b.writeUInt32LE(receipt.rate*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(pcm.length*2,40);pcm.forEach((v,j)=>b.writeInt16LE(v,44+j*2));
  assert.equal(b.readUInt32LE(40),receipt.N*2);const name='witness-'+i+'.wav';fs.writeFileSync(path.join(out,name),b);return {i,name,sha256:hash(b)};
 });
 fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
 const rows=receipt.operating.flatMap(o=>o.receivers.flatMap(r=>Object.entries(r.evaluation).map(([g,v])=>'<tr>'+[o.budget,r.name,g,r.selected.threshold,v.tp,v.fp,v.fn,v.exact,v.operations].map(x=>'<td>'+x+'</td>').join('')+'</tr>'))).join('');
 const cards=receipt.specimens.map(s=>'<h2>'+s.name+'</h2><audio controls preload="none" src="'+s.name+'"></audio><pre>'+JSON.stringify({condition:receipt.rows[s.i].condition,truth:receipt.rows[s.i].truth,outcomes:receipt.rows[s.i].fit.map(f=>({seen:f.seen,tp:f.tp,fp:f.fp,fn:f.fn})),sha256:s.sha256},null,2)+'</pre>').join('');
 fs.writeFileSync(path.join(out,'index.html'),'<!doctype html><meta charset="utf-8"><title>MHAC dictionary transfer</title><style>body{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:1rem}td,th{padding:.3rem;border-bottom:1px solid #aaa;text-align:right}pre{overflow:auto;background:#eee;padding:1rem}audio{width:100%}</style><h1>Acoustic dictionary transfer</h1><p>Synthetic only; matching tolerance 1 ms. Thresholds calibrated on known triangles only. Playback opt-in; start at low hardware volume. All methods use the same PCM.</p><table><thead><tr>'+['Budget','Receiver','Group','Threshold','TP','FP','FN','Exact','Products'].map(s=>'<th>'+s+'</th>').join('')+'</tr></thead><tbody>'+rows+'</tbody></table>'+cards+'<p><a href="receipt.json">Full replay receipt</a></p>');
 console.log(JSON.stringify({assertions:receipt.assertions,operating:receipt.operating,specimens:receipt.specimens},null,2));
}
