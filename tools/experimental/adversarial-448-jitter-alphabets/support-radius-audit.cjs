'use strict';
// Refs #448 #442. AI-assisted independent geometry implementation, no human or peer review.
// Exact pinned measurement sources at 5a1e3a857389ce8f6763c66847c9522179dcbf59. Finite feature model, no waveform detector.
// Equal-weight conditions; uniform continuous phase and deletion; uniform shifts within each declared finite set. Bayes forced prediction on support, otherwise refuse. Support decoder accepts only singleton.
function audit(core,phase){
 const REF="5a1e3a857389ce8f6763c66847c9522179dcbf59",pairs=[[1,1],[2,1],[3,2],[5,3],[8,5],[13,8],[21,13],[34,21],[55,34],[89,55],[144,89],[233,144],[377,233],[610,377],[987,610],[1597,987]],rates=[8000,16000,48000],spans=[200,800,1600];
 let assertions=0;const ok=(x,m)=>{if(!x)throw Error(m);assertions++},sum=a=>a.reduce((s,x)=>s+x,0),key=a=>a.join(","),near=(a,b)=>Math.abs(a-b)<1e-9;
 const middle=r=>Array.from({length:2*r+1},(_,i)=>[0,i-r,0]),cube=r=>middle(r).flatMap(a=>middle(r).flatMap(b=>middle(r).map(c=>[a[1],b[1],c[1]])));
 const policies=[{id:"nominal",shifts:middle(0)},{id:"middle1",shifts:middle(1)},{id:"middle2",shifts:middle(2)},{id:"cube1",shifts:cube(1)}];
 const evals=[{id:"clean",shifts:middle(0)},{id:"late1",shifts:[[0,1,0]]},{id:"early1",shifts:[[0,-1,0]]},{id:"uniform-middle1",shifts:middle(1)},{id:"late2",shifts:[[0,2,0]]},{id:"late3",shifts:[[0,3,0]]},{id:"uniform-cube1",shifts:cube(1)},{id:"common-late1",shifts:[[1,1,1]]}];
 function geometry(p,q,rate,ms,frame){
  const points=[0,p,p+q,2*p+q],D=rate*ms/1000,pad=rate/10;
  const x=points.map((_,d)=>{const a=points.filter((_,i)=>i!==d),lo=frame==="fixed"?0:a[0],den=frame==="fixed"?points[3]:a[2]-a[0];return a.map(t=>[(t-lo)*D,den])});
  const breaks=[[0,1],[1,1]];for(const a of x)for(const [n,d] of a)if(n%d)breaks.push([d-n%d,d]);
  const cmp=(a,b)=>a[0]*b[1]-b[0]*a[1];breaks.sort(cmp);const b=breaks.filter((a,i)=>i===0||cmp(a,breaks[i-1])!==0);
  const mass=new Map();
  for(let i=0;i<b.length-1;i++){const [l,ld]=b[i],[h,hd]=b[i+1],w=(h/hd-l/ld)/4;
   for(let d=0;d<4;d++){const a=x[d].map(([n,s])=>{const v=BigInt(n)*BigInt(ld)+BigInt(l)*BigInt(s),div=BigInt(s)*BigInt(ld);return pad+Number(v/div)});const k=key(a);if(!mass.has(k))mass.set(k,[0,0,0,0]);mass.get(k)[d]+=w;}
  }
  return mass;
 }
 function spread(m,shifts){const out=new Map();for(const [k,a] of m){const v=k.split(",").map(Number);for(const sh of shifts){const w=v.map((x,i)=>x+sh[i]);ok(w[0]<w[1]&&w[1]<w[2],"ordered");const j=key(w);if(!out.has(j))out.set(j,[0,0,0,0]);const b=out.get(j);for(let d=0;d<4;d++)b[d]+=a[d]/shifts.length;}}return out}
 const rows=[],witnesses=[];let cases=0;
 for(const [p,q] of pairs)for(const rate of rates)for(const ms of spans)for(const frame of ["receipt","fixed"]){
  const condition={p,q,rate,ms,frame},m=geometry(p,q,rate,ms,frame),z=phase.inspect(p,q,rate,ms,frame);
  ok(m.size===z.receipts.length,"pinned support cardinality");
  for(const r of z.receipts){const a=m.get(key(r.samples));ok(a&&a.every((v,i)=>near(v,r.mass[i])),"pinned probability cells")}
  const dec=policies.map(P=>({...P,map:spread(m,P.shifts)}));
  for(const E of evals){const actual=spread(m,E.shifts);ok(near(sum([...actual.values()].map(sum)),1),"total mass");for(const P of dec){
   let correct=0,wrong=0,ambiguous=0,oov=0,bayesCorrect=0,bayesWrong=0;const cells=[];
   for(const [k,a] of actual){const b=P.map.get(k),total=sum(a),candidates=b?b.map((x,i)=>x>0?i:-1).filter(i=>i>=0):[];
    if(!candidates.length)oov+=total;else{const pred=b.indexOf(Math.max(...b));bayesCorrect+=a[pred];bayesWrong+=total-a[pred];if(candidates.length===1){const d=candidates[0];correct+=a[d];wrong+=total-a[d];if(total-a[d]>1e-12){const other=a.findIndex((x,i)=>i!==d&&x>0);cells.push({observed:k.split(",").map(Number),actual:other+1,predicted:d+1,wrongMass:total-a[d]});}}else ambiguous+=total;}
   }
   const coverage=correct+wrong;ok(near(coverage+ambiguous+oov,1),"partition");ok(near(bayesCorrect+bayesWrong+oov,1),"Bayes partition");
   if(E.shifts.every(s=>P.shifts.some(t=>key(s)===key(t))))ok(wrong<1e-10&&oov<1e-10,"bounded support guarantee");
   if(cells.length){const cell=cells.sort((a,b)=>b.wrongMass-a.wrongMass)[0];const origin=[...m].find(([k,a])=>a[cell.actual-1]>0&&E.shifts.some(s=>key(k.split(",").map((x,i)=>Number(x)+s[i]))===key(cell.observed)));ok(origin,"witness origin");witnesses.push({condition,policy:P.id,evaluation:E.id,...cell,trueSamples:origin[0].split(",").map(Number)});}
   rows.push({condition,policy:P.id,evaluation:E.id,correct,wrong,coverage,ambiguous,oov,bayesCorrect,bayesWrong});cases++;
  }}
 }
 const summary=[];for(const frame of ["receipt","fixed"])for(const P of policies)for(const E of evals){const group=rows.filter(r=>r.condition.frame===frame&&r.policy===P.id&&r.evaluation===E.id);ok(group.length===144,"condition count");const o={frame,policy:P.id,evaluation:E.id};for(const k of ["correct","wrong","coverage","ambiguous","oov","bayesCorrect","bayesWrong"])o[k]=sum(group.map(r=>r[k]))/group.length;o.conditionalError=o.coverage?o.wrong/o.coverage:null;summary.push(o)}
 const get=(frame,policy,evaluation)=>summary.find(r=>r.frame===frame&&r.policy===policy&&r.evaluation===evaluation);
 ok(near(get("receipt","nominal","clean").coverage,.5033467717525334),"prior clean reproduction");
 ok(near(get("receipt","nominal","late1").coverage,.2476434628),"prior shifted coverage");
 ok(Math.abs(get("receipt","nominal","late1").conditionalError-.193536)<.000002,"prior shifted error");
 const selected=[];for(const P of policies)for(const E of evals){const w=witnesses.filter(w=>w.policy===P.id&&w.evaluation===E.id).sort((a,b)=>b.wrongMass-a.wrongMass)[0];if(w){const c=core.condition(w.condition.p,w.condition.q,w.condition.rate,w.condition.ms,w.condition.frame),a=core.wav(c,{samples:w.trueSamples}),b=core.wav(c,{samples:w.observed});selected.push({...w,trueHash:core.sha256(a),shiftedHash:core.sha256(b)});}}
 return {schema:"mhac-adversarial-support-radius-v1",sourceRef:REF,seed:null,claimClass:"finite synthetic feature model; no human data",policies,evals,cases,assertions,summary,rows,witnesses:selected};
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),dir=process.argv[2],out=process.argv[3];
 if(!dir||!out)throw Error('Usage: node support-radius-audit.cjs PINNED_MEASUREMENT_DIR NEW_OUTPUT_DIR');if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('nonempty output');
 const pins={"core.js":"47938c769604ae56a1f8cb92e5d4ccc3e20f8d59","phase.html":"c8f8631a9e76318a271d811e471af75e5c372acf"};
 for(const [n,h] of Object.entries(pins)){const b=fs.readFileSync(path.join(dir,n));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==h)throw Error('source pin '+n);}
 const core=require(path.resolve(dir,'core.js')),html=fs.readFileSync(path.join(dir,'phase.html'),'utf8'),phase=new Function('MHAC',html.match(/<script id="phase-core">([\s\S]*?)<\/script>/)[1]+'\nreturn PHASE;')(core);
 const d=audit(core,phase);fs.mkdirSync(out,{recursive:true});const files={'receipt.json':JSON.stringify(d,null,2)+'\n'};
 d.witnesses.forEach((w,i)=>{const c=core.condition(w.condition.p,w.condition.q,w.condition.rate,w.condition.ms,w.condition.frame);for(const [label,samples,h] of [['true',w.trueSamples,w.trueHash],['shifted',w.observed,w.shiftedHash]]){const b=core.wav(c,{samples});if(core.sha256(b)!==h)throw Error('specimen hash');files['witness-'+i+'-'+label+'.wav']=b;}});
 for(const [n,b] of Object.entries(files))fs.writeFileSync(path.join(out,n),b);
 const sha=b=>crypto.createHash('sha256').update(b).digest('hex');fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({sourceRef:d.sourceRef,pins,sourceSHA256:sha(fs.readFileSync(__filename)),files:Object.fromEntries(Object.entries(files).map(([n,b])=>[n,sha(b)]))},null,2)+'\n');console.log(JSON.stringify({cases:d.cases,assertions:d.assertions,summary:d.summary},null,2));
}
module.exports={audit};if(require.main===module)cli();
