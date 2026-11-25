"use strict";
/* MHAC Adversarial Observatory #448 / Draft #449, 2026-11-25.
Synthetic receiver only, single AI agent. Parent 2ecf28b0535a957197e285b6a66ca6864d486dd2; main 495a98ca12bae467a507031f04931aa4254b1866.
Independent reimplementation of parent's waveform generator and hard receiver, same known slots, 750ms packet, 4 x 20ms pulses, 8kHz PCM16, uniform within-slot noise, random phase and signed carrier offset. No slot acquisition; not human perception. List decoder admits labels within relative projection-power width, uses radius one on lists; candidate sets grow with width, but unique accepts need not decrease (empty sets may become singletons). Initial incorrect monotonic acceptance assertion failed and was replaced by the actual set-inclusion invariant. Soft scores sum relative projection energy with one free replacement, not a probability or likelihood. Both reuse exactly the same quadrature features; extra codebook score computations are not free. Development chooses threshold per book by predeclared <=1% unconditional wrong rate then max correct, with fallback to minimum wrong; only k=0,1 tuned. Evaluation uses fresh seeds and includes out-of-model k=2. Parent replay uses separate original seeds for k=1; all 24 condition/book hard counts and label-error counts matched in connector execution. Finite synthetic results only; no guarantees under distribution shift. Raw noisy witness WAV is exact PCM; audition copy uses attenuation to <=4096/32767 peak. No automatic playback. Node 18+: node soft-label.cjs OUTPUT_DIRECTORY. Computational core and bytes executed twice in V8; no native filesystem or listening test. No canonical record edits, no human claims. */
function experiment(){
 const rate=8000,N=160,packet=6000,slots=[400,2000,3600,5200],freq=[400,600,800,1000],V=[[0,1,2,3],[1,0,3,2],[2,3,0,1],[3,2,1,0]];
 const books={odd_coset:V.concat(V.map(w=>w.map(x=>[1,0,2,3][x]))),even_coset:V.concat(V.map(w=>w.map(x=>[1,2,0,3][x])))};
 const grids={list:[0,.15,.35,.55,.75],soft:[0,.03,.08,.15,.25,.4]},seeds={development:[14111,14207,14323],evaluation:[22111,22229,22343,22447],parent_replay:[6011,7027,8089]};
 let checks=0,peak=0,clips=0;const ck=(x,m)=>{checks++;if(!x)throw Error(m)};
 const rng=s=>()=>{s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296};
 const dot=(a,b)=>{let z=0;for(let i=0;i<a.length;i++)z+=a[i]*b[i];return z},unit=a=>{const n=Math.sqrt(dot(a,a));return a.map(x=>x/n)};
 const env=Array.from({length:N},(_,i)=>Math.sin(Math.PI*i/(N-1))**2);
 const orth=freq.map(f=>{const a=env.map((e,i)=>e*Math.sin(2*Math.PI*f*i/rate)),b=env.map((e,i)=>e*Math.sin(2*Math.PI*f*i/rate+Math.PI/2)),u=unit(a),d=dot(u,b);return [u,unit(b.map((v,i)=>v-d*u[i]))]});
 function pulse(l,p,g,shift){const a=env.map((e,i)=>e*Math.sin(2*Math.PI*(freq[l]+shift)*i/rate+p));const s=g*Math.sqrt(N/dot(a,a));return a.map(v=>v*s)}
 const quant=x=>Math.max(-32768,Math.min(32767,Math.round(x*32767))),hd=(a,b)=>a.reduce((n,v,i)=>n+(v!==b[i]),0),empty=()=>({correct:0,wrong:0,abstain:0});
 function record(c,id,v){c[v<0?"abstain":v===id?"correct":"wrong"]++}
 const unique=a=>a.length===1?a[0]:-1;
 function decode(book,E){
  const hard=E.map(s=>s.indexOf(Math.max(...s))),hardID=unique(book.map((w,i)=>hd(w,hard)<=1?i:-1).filter(i=>i>=0)),max=E.map(s=>Math.max(...s));
  const sets=grids.list.map(t=>book.map((w,i)=>w.reduce((n,l,j)=>n+(E[j][l]<max[j]*(1-t)),0)<=1?i:-1).filter(i=>i>=0));
  for(let j=1;j<sets.length;j++)ck(sets[j-1].every(i=>sets[j].includes(i)),"nested candidate sets");
  const list=sets.map(unique),q=E.map((s,j)=>s.map(v=>max[j]>0?v/max[j]:0));
  const scores=book.map(w=>{const a=w.map((v,i)=>q[i][v]);return a.reduce((s,v)=>s+v,0)+Math.max(...a.map(v=>1-v))});
  const order=scores.map((v,i)=>({v,i})).sort((a,b)=>b.v-a.v||a.i-b.i),gap=order[0].v-order[1].v;
  const soft=grids.soft.map(t=>gap>Math.max(1e-10,t)?order[0].i:-1);
  if(E.every(s=>s.filter(x=>x===Math.max(...s)).length===1))ck(list[0]===hardID,"zero list width equals hard for unique labels");
  return {hard:hardID,list,soft,gap,labels:hard,scores};
 }
 function wav(windows,scale=1){const b=new Uint8Array(44+packet*2),v=new DataView(b.buffer);function tag(i,s){for(let j=0;j<s.length;j++)b[i+j]=s.charCodeAt(j)}tag(0,"RIFF");v.setUint32(4,b.length-8,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,packet*2,true);windows.forEach((w,i)=>w.forEach((x,j)=>v.setInt16(44+2*(slots[i]+j),Math.round(x*scale),true)));return b}
 const audio={},witnesses={};
 function run(part,ks,rs,selected=null){
  const out=[];
  for(const k of ks)for(const gain of [.04,.012])for(const noise of [0,.06,.18])for(const drift of [0,35]){
   const results={};
   for(const [name,book] of Object.entries(books)){
    const hard=empty(),list=grids.list.map(empty),soft=grids.soft.map(empty),selectedList=empty(),selectedSoft=empty();let total=0,errors=0;
    for(const seed of seeds[part]){const rand=rng(seed);for(let id=0;id<8;id++)for(let rep=0;rep<rs;rep++){
     const sent=book[id],actual=sent.slice(),positions=[0,1,2,3];for(let j=0;j<k;j++){const i=positions.splice(Math.floor(rand()*positions.length),1)[0];actual[i]=(actual[i]+1+Math.floor(rand()*3))%4}
     const windows=[],phases=[],shifts=[];
     for(let i=0;i<4;i++){const p=2*Math.PI*rand(),d=drift*(rand()<.5?-1:1);phases.push(p);shifts.push(d);const w=pulse(actual[i],p,gain,d).map(v=>{const z=v+noise*Math.sqrt(3)*(2*rand()-1);if(Math.abs(z)>1)clips++;const q=quant(z);peak=Math.max(peak,Math.abs(q));return q});windows.push(w)}
     const E=windows.map(w=>orth.map(([a,b])=>dot(w,a)**2+dot(w,b)**2)),d=decode(book,E);total++;errors+=hd(actual,d.labels);record(hard,id,d.hard);d.list.forEach((v,i)=>record(list[i],id,v));d.soft.forEach((v,i)=>record(soft[i],id,v));
     if(noise===0)ck(hd(actual,d.labels)===0,"noiseless carrier classification");
     if(selected){const l=d.list[selected[name].list],s=d.soft[selected[name].soft];record(selectedList,id,l);record(selectedSoft,id,s);
      if(name==="even_coset"&&k===1&&noise>0){
       const types=[["hard_wrong_list_refused",d.hard>=0&&d.hard!==id&&l<0],["hard_wrong_soft_correct",d.hard>=0&&d.hard!==id&&s===id],["soft_wrong",s>=0&&s!==id]];
       for(const [type,yes] of types)if(yes&&!witnesses[type]){
        witnesses[type]={part,k,gain,noise,drift,seed,id,rep,sent,actual,phases,shifts,labels:d.labels,hard:d.hard,list:l,soft:s,gap:d.gap,scores:d.scores,energy:E};
        audio[type+"_raw"]=wav(windows);audio[type+"_audition"]=wav(windows,Math.min(1,4096/Math.max(1,...windows.flat().map(Math.abs))));
        audio[type+"_intended"]=wav(sent.map(l=>pulse(l,.3,.04,0).map(quant)));
       }
      }
     }
    }}
    for(const c of [hard,...list,...soft,...(selected?[selectedList,selectedSoft]:[])])ck(c.correct+c.wrong+c.abstain===total,"outcome accounting");
    for(let j=1;j<soft.length;j++)ck(soft[j].correct+soft[j].wrong<=soft[j-1].correct+soft[j-1].wrong,"nested soft threshold");
    results[name]={total,labelErrors:errors,hard,list,soft,...(selected?{selectedList,selectedSoft}:{})};
   }out.push({k,gain,noise,drift,results})
  }return out
 }
 const dev=run("development",[0,1],8);
 const sum=(rows,name,field,index)=>rows.reduce((a,r)=>{const x=index===undefined?r.results[name][field]:r.results[name][field][index];for(const k of Object.keys(a))a[k]+=x[k];return a},empty());
 const selection={},development={};
 for(const name of Object.keys(books)){
  selection[name]={};development[name]={};
  for(const f of ["list","soft"]){
   const counts=grids[f].map((_,i)=>sum(dev,name,f,i));const n=counts[0].correct+counts[0].wrong+counts[0].abstain;
   const ix=counts.map((c,i)=>({c,i})).sort((a,b)=>{const x=a.c.wrong<=n*.01,y=b.c.wrong<=n*.01;if(x!==y)return x?-1:1;return (x?b.c.correct-a.c.correct||a.c.wrong-b.c.wrong:a.c.wrong-b.c.wrong||b.c.correct-a.c.correct)||b.i-a.i})[0].i;
   selection[name][f]=ix;development[name][f]={counts,index:ix,threshold:grids[f][ix],targetMet:counts[ix].wrong<=n*.01};
  }
 }
 const evaluation=run("evaluation",[0,1,2],8,selection),replay=run("parent_replay",[1],12);
 const aggregate={};for(const name of Object.keys(books)){aggregate[name]={};for(const k of [0,1,2]){const rows=evaluation.filter(x=>x.k===k);aggregate[name][k]=Object.fromEntries(["hard","selectedList","selectedSoft"].map(f=>[f,sum(rows,name,f)]))}}
 ck(clips===0,"no clipped samples");ck(seeds.development.every(x=>!seeds.evaluation.includes(x)&&!seeds.parent_replay.includes(x)),"seed separation");
 return {receipt:{schema:"mhac-448-soft-label-v1",parent:"2ecf28b0535a957197e285b6a66ca6864d486dd2",main:"495a98ca12bae467a507031f04931aa4254b1866",rate,N,packet,slots,freq,books,grids,seeds,checks,peak,clips,development,selection,dev,evaluation,replay,aggregate,witnesses},audio};
}
function compact(r){return {checks:r.checks,peak:r.peak,clips:r.clips,development:r.development,aggregate:r.aggregate,witnesses:Object.keys(r.witnesses),conditions:r.evaluation.filter(c=>c.k===1&&c.drift===35).map(c=>({gain:c.gain,noise:c.noise,results:Object.fromEntries(Object.entries(c.results).map(([n,v])=>[n,{hard:v.hard,selectedList:v.selectedList,selectedSoft:v.selectedSoft}]))}))}}
const expected={"checks":186914,"peak":13249,"clips":0,"development":{"odd_coset":{"list":{"counts":[{"correct":2636,"wrong":302,"abstain":1670},{"correct":2646,"wrong":349,"abstain":1613},{"correct":2566,"wrong":316,"abstain":1726},{"correct":2346,"wrong":150,"abstain":2112},{"correct":1997,"wrong":22,"abstain":2589}],"index":4,"threshold":0.75,"targetMet":true},"soft":{"counts":[{"correct":2904,"wrong":773,"abstain":931},{"correct":2882,"wrong":704,"abstain":1022},{"correct":2833,"wrong":629,"abstain":1146},{"correct":2773,"wrong":522,"abstain":1313},{"correct":2664,"wrong":393,"abstain":1551},{"correct":2503,"wrong":245,"abstain":1860}],"index":5,"threshold":0.4,"targetMet":false}},"even_coset":{"list":{"counts":[{"correct":3317,"wrong":447,"abstain":844},{"correct":3381,"wrong":483,"abstain":744},{"correct":3296,"wrong":432,"abstain":880},{"correct":2999,"wrong":239,"abstain":1370},{"correct":2503,"wrong":38,"abstain":2067}],"index":4,"threshold":0.75,"targetMet":true},"soft":{"counts":[{"correct":3624,"wrong":984,"abstain":0},{"correct":3604,"wrong":921,"abstain":83},{"correct":3581,"wrong":827,"abstain":200},{"correct":3516,"wrong":688,"abstain":404},{"correct":3410,"wrong":527,"abstain":671},{"correct":3244,"wrong":353,"abstain":1011}],"index":5,"threshold":0.4,"targetMet":false}}},"aggregate":{"odd_coset":{"0":{"hard":{"correct":2193,"wrong":145,"abstain":734},"selectedList":{"correct":1641,"wrong":7,"abstain":1424},"selectedSoft":{"correct":2055,"wrong":100,"abstain":917}},"1":{"hard":{"correct":1410,"wrong":192,"abstain":1470},"selectedList":{"correct":1104,"wrong":25,"abstain":1943},"selectedSoft":{"correct":1369,"wrong":144,"abstain":1559}},"2":{"hard":{"correct":80,"wrong":477,"abstain":2515},"selectedList":{"correct":43,"wrong":300,"abstain":2729},"selectedSoft":{"correct":113,"wrong":485,"abstain":2474}}},"even_coset":{"0":{"hard":{"correct":2359,"wrong":216,"abstain":497},"selectedList":{"correct":1727,"wrong":17,"abstain":1328},"selectedSoft":{"correct":2310,"wrong":151,"abstain":611}},"1":{"hard":{"correct":2111,"wrong":289,"abstain":672},"selectedList":{"correct":1663,"wrong":19,"abstain":1390},"selectedSoft":{"correct":2085,"wrong":220,"abstain":767}},"2":{"hard":{"correct":134,"wrong":740,"abstain":2198},"selectedList":{"correct":51,"wrong":441,"abstain":2580},"selectedSoft":{"correct":152,"wrong":752,"abstain":2168}}}},"witnesses":["hard_wrong_list_refused","soft_wrong"],"conditions":[{"gain":0.04,"noise":0,"results":{"odd_coset":{"hard":{"correct":173,"wrong":0,"abstain":83},"selectedList":{"correct":173,"wrong":0,"abstain":83},"selectedSoft":{"correct":173,"wrong":0,"abstain":83}},"even_coset":{"hard":{"correct":256,"wrong":0,"abstain":0},"selectedList":{"correct":256,"wrong":0,"abstain":0},"selectedSoft":{"correct":256,"wrong":0,"abstain":0}}}},{"gain":0.04,"noise":0.06,"results":{"odd_coset":{"hard":{"correct":173,"wrong":0,"abstain":83},"selectedList":{"correct":169,"wrong":0,"abstain":87},"selectedSoft":{"correct":173,"wrong":0,"abstain":83}},"even_coset":{"hard":{"correct":256,"wrong":0,"abstain":0},"selectedList":{"correct":254,"wrong":0,"abstain":2},"selectedSoft":{"correct":256,"wrong":0,"abstain":0}}}},{"gain":0.04,"noise":0.18,"results":{"odd_coset":{"hard":{"correct":72,"wrong":22,"abstain":162},"selectedList":{"correct":13,"wrong":5,"abstain":238},"selectedSoft":{"correct":70,"wrong":17,"abstain":169}},"even_coset":{"hard":{"correct":130,"wrong":37,"abstain":89},"selectedList":{"correct":26,"wrong":3,"abstain":227},"selectedSoft":{"correct":126,"wrong":31,"abstain":99}}}},{"gain":0.012,"noise":0,"results":{"odd_coset":{"hard":{"correct":173,"wrong":0,"abstain":83},"selectedList":{"correct":173,"wrong":0,"abstain":83},"selectedSoft":{"correct":173,"wrong":0,"abstain":83}},"even_coset":{"hard":{"correct":256,"wrong":0,"abstain":0},"selectedList":{"correct":256,"wrong":0,"abstain":0},"selectedSoft":{"correct":256,"wrong":0,"abstain":0}}}},{"gain":0.012,"noise":0.06,"results":{"odd_coset":{"hard":{"correct":61,"wrong":26,"abstain":169},"selectedList":{"correct":12,"wrong":4,"abstain":240},"selectedSoft":{"correct":53,"wrong":19,"abstain":184}},"even_coset":{"hard":{"correct":116,"wrong":42,"abstain":98},"selectedList":{"correct":18,"wrong":4,"abstain":234},"selectedSoft":{"correct":101,"wrong":36,"abstain":119}}}},{"gain":0.012,"noise":0.18,"results":{"odd_coset":{"hard":{"correct":12,"wrong":54,"abstain":190},"selectedList":{"correct":2,"wrong":7,"abstain":247},"selectedSoft":{"correct":12,"wrong":46,"abstain":198}},"even_coset":{"hard":{"correct":16,"wrong":85,"abstain":155},"selectedList":{"correct":1,"wrong":7,"abstain":248},"selectedSoft":{"correct":16,"wrong":63,"abstain":177}}}}]};
if(typeof module!=="undefined")module.exports={experiment,compact,expected};
if(typeof require!=="undefined"&&require.main===module){const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');const out=process.argv[2];if(!out)throw Error('usage: node soft-label.cjs OUTPUT_DIRECTORY');const {receipt,audio}=experiment();if(JSON.stringify(compact(receipt))!==JSON.stringify(expected))throw Error('qualification mismatch');fs.mkdirSync(out,{recursive:true});const hashes={};for(const [name,bytes] of Object.entries(audio)){const file=name+'.wav';fs.writeFileSync(path.join(out,file),bytes);hashes[file]=crypto.createHash('sha256').update(bytes).digest('hex')}fs.writeFileSync(path.join(out,'soft-label-receipt.json'),JSON.stringify(receipt,null,2)+'\n');fs.writeFileSync(path.join(out,'stimuli-sha256.json'),JSON.stringify(hashes,null,2)+'\n');console.log(JSON.stringify(compact(receipt),null,2));}
