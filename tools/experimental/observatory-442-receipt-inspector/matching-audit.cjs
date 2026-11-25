'use strict';
// Measurement #442 / Draft #443. Synthetic only, AI-assisted, no independent review.
// Node >=18: node matching-audit.cjs NEW_OUTPUT_DIRECTORY; open index.html.
const REF='01adf34a0c6cfd879b7e07ca8ebfe3491d142ef5';
const PINS=[['region-refinement','b9729da5b2f0532f2b509be21587b33f3ef21223'],['joint-reconstruction','a57455bb631f68808019435470dc63e7683cdedb'],['selective-reconstruction','5919b173dddacf6a30f7d058d0b08da042ffc7fa']];
const K=['strict','relaxed','iou0.25','iou0.5','iou0.75'],EPS=1e-10;
function ok(x,m){if(!x)throw Error(m)}
function edges(a,b,k,rate){
 ok(K.includes(k),'unknown criterion');
 return b.flatMap((v,j)=>a.map((u,i)=>{
 const o=Math.max(0,Math.min(u.t+u.L,v.t+v.L)-Math.max(u.t,v.t)),iou=o/(u.L+v.L-o),e=Math.abs(u.t-v.t);
 return {i,j,w:k.startsWith('iou')?iou:-e,d:Math.abs(u.L-v.L),eligible:k.startsWith('iou')?iou>=Number(k.slice(3)):e<=rate*(k==='strict'?.001:.005)};
 }).filter(e=>e.eligible));
}
function better(a,b){if(!a||b.n>a.n||(b.n===a.n&&b.w>a.w+EPS))return b;
 if(a.n===b.n&&Math.abs(a.w-b.w)<=EPS)return {...a,lo:Math.min(a.lo,b.lo),hi:Math.max(a.hi,b.hi)};return a}
function solve(a,b,k,rate){
 ok(a.length<=12,'bounded truth count');
 const es=edges(a,b,k,rate);
 let states=new Map([[0,{n:0,w:0,lo:0,hi:0,pairs:[]}]]);
 for(let j=0;j<b.length;j++){
  const next=new Map(states);
  for(const [mask,s] of states)for(const e of es.filter(e=>e.j===j))if(!(mask&(1<<e.i))){
   const m=mask|(1<<e.i),v={n:s.n+1,w:s.w+e.w,lo:s.lo+e.d,hi:s.hi+e.d,pairs:[...s.pairs,[e.i,j]]};
   next.set(m,better(next.get(m),v));
  }states=next;
 }
 let best;for(const s of states.values())best=better(best,s);
 const ai=new Set(),aj=new Set();let gn=0,gw=0;
 for(const e of es.slice().sort((a,b)=>b.w-a.w||a.i-b.i||a.j-b.j))if(!ai.has(e.i)&&!aj.has(e.j)){ai.add(e.i);aj.add(e.j);gn++;gw+=e.w}
 return {...best,greedyN:gn,greedyW:gw};
}
function selfTest(){
 const s=solve([{t:0,L:100},{t:90,L:100}],[{t:0,L:190},{t:0,L:40}],'iou0.25',8000);ok(s.n===2&&s.greedyN===1,'greedy trap');
 const t=solve([{t:0,L:80}],[{t:0,L:40},{t:0,L:160}],'iou0.5',8000);ok(t.n===1&&t.lo===40&&t.hi===80,'duration tie');
 const large=Array.from({length:33},(_,i)=>({t:i===0||i===32?0:500,L:80}));ok(solve([{t:0,L:80},{t:0,L:80}],large,'strict',8000).n===2,'prediction index 32');
 ok(solve([],[],'strict',8000).n===0,'empty');
 let cases=0;
 for(let seed=1;seed<=300;seed++){
  let x=seed;const rnd=()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x>>>16};
  const gen=n=>Array.from({length:n},()=>({t:(rnd()%12)*8,L:(1+rnd()%10)*8}));
  const a=gen(rnd()%5),b=gen(rnd()%6);
  for(const k of K){
   const es=edges(a,b,k,8000);let best;
   function walk(i,used,n,w,d){if(i===a.length){best=better(best,{n,w,lo:d,hi:d});return}
    walk(i+1,used,n,w,d);for(const e of es)if(e.i===i&&!used.has(e.j)){used.add(e.j);walk(i+1,used,n+1,w+e.w,d+e.d);used.delete(e.j)}
   }walk(0,new Set(),0,0,0);
   const q=solve(a,b,k,8000);ok(q.n===best.n&&Math.abs(q.w-best.w)<1e-9&&q.lo===best.lo&&q.hi===best.hi,'enumeration mismatch '+seed+' '+k);cases++;
  }
 }return cases;
}
function audit(inputs){
 const runs=[],witnesses=[];
 for(const {name,blob,receipt:r} of inputs){
  const totals={cells:0,cardinalityMismatch:0,weightMismatch:0,durationOutOfRange:0,greedyLostCells:0,greedyLostMatches:0,greedyWeightLostCells:0,tiedDurationCells:0,maxDurationRangeSamples:0,maxPredictions:0};
  const byCriterion=Object.fromEntries(K.map(k=>[k,{cells:0,greedyLostCells:0,tiedDurationCells:0}]));
  for(const [i,row] of r.rows.entries())for(const [m,fit] of row.fits.entries())for(const k of r.criteria){
   const s=solve(row.truth,fit,k,r.rate),v=row.metrics[m][k],w=k.startsWith('iou')?v.iouSum:-v.onsetError,c=byCriterion[k];
   totals.cells++;c.cells++;totals.maxPredictions=Math.max(totals.maxPredictions,fit.length);
   const bn=s.n!==v.tp,bw=Math.abs(s.w-w)>1e-8,bd=v.durationError<s.lo||v.durationError>s.hi,lost=s.n-s.greedyN,gw=!lost&&s.w-s.greedyW>1e-8;
   ok(lost>=0,'greedy exceeds optimum');totals.cardinalityMismatch+=+bn;totals.weightMismatch+=+bw;totals.durationOutOfRange+=+bd;
   if(lost){totals.greedyLostCells++;totals.greedyLostMatches+=lost;c.greedyLostCells++}
   totals.greedyWeightLostCells+=+gw;
   if(s.hi>s.lo){totals.tiedDurationCells++;c.tiedDurationCells++;totals.maxDurationRangeSamples=Math.max(totals.maxDurationRangeSamples,s.hi-s.lo)}
   if(bn||bw||bd||lost||gw||s.hi>s.lo)witnesses.push({name,packet:i,condition:row.condition,method:r.methods[m],criterion:k,rate:r.rate,truth:row.truth,fit,reported:v,optimal:s});
  }runs.push({name,blob,rate:r.rate,rows:r.rows.length,totals,byCriterion});
 }
 return {schema:'mhac-matching-audit-v1',sourceRef:REF,scope:'finite synthetic trace audit; no human evidence',tolerance:EPS,runs,witnesses};
}
function page(r){
 const data=JSON.stringify(r).replace(/</g,'\\u003c');
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MHAC matching audit</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto;padding:1rem;color-scheme:light dark}pre{white-space:pre-wrap;overflow-wrap:anywhere}select{max-width:100%;font:inherit}svg{width:100%}td,th{padding:.4rem;text-align:right}</style><h1>Matching audit</h1><p>Finite synthetic traces; greedy is a scoring baseline, not a receiver. Duration ranges conditional on maximum cardinality and original secondary objective. No human inference. <a href="receipt.json">Full receipt</a></p><div id="summary"></div><label>Witness <select id="choice"></select></label><svg id="plot" viewBox="0 0 900 120" role="img" aria-label="Truth and predicted intervals with optimal associations"></svg><pre id="trace"></pre><script>const d='+data+';('+browser.toString()+')(d);</script></html>';
}
function browser(d){
 const $=id=>document.getElementById(id),t=document.createElement('table');
 for(const row of [['Run','Cells','Cardinality differences','Weight differences','Greedy weight losses','Duration ties'],...d.runs.map(r=>[r.name,r.totals.cells,r.totals.cardinalityMismatch,r.totals.weightMismatch,r.totals.greedyWeightLostCells,r.totals.tiedDurationCells])]){const tr=t.insertRow();for(const v of row)tr.insertCell().textContent=v}$('summary').append(t);
 d.witnesses.forEach((w,i)=>{const o=document.createElement('option');o.value=i;o.textContent=w.name+' #'+w.packet+' '+w.method+' '+w.criterion;$('choice').append(o)});
 function show(){const w=d.witnesses[Number($('choice').value)];if(!w)return;$('trace').textContent=JSON.stringify(w,null,2);const svg=$('plot');svg.replaceChildren();const end=Math.max(1,...[...w.truth,...w.fit].map(e=>e.t+e.L)),x=t=>80+800*t/end;
 const draw=(tag,a,txt)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(a))e.setAttribute(k,v);if(txt!==undefined)e.textContent=txt;svg.append(e)};
 for(const [i,j] of w.optimal.pairs)draw('line',{x1:x(w.truth[i].t+w.truth[i].L/2),y1:35,x2:x(w.fit[j].t+w.fit[j].L/2),y2:85,stroke:'#888'});
 for(const [a,y,label,col] of [[w.truth,20,'Truth','#527ca5'],[w.fit,70,'Fit','#a66b42']]){draw('text',{x:0,y:y+15,fill:'currentColor'},label);a.forEach((e,i)=>{draw('rect',{x:x(e.t),y:y+i%3*5,width:x(e.L)-80,height:20,fill:col,opacity:.65});draw('text',{x:x(e.t),y:y-2,fill:'currentColor','font-size':10},String(i))})}
 draw('text',{x:80,y:116,fill:'currentColor','font-size':12},'0 to '+(1000*end/w.rate).toFixed(1)+' ms (witness extent)');
 }$('choice').onchange=show;show();
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),out=process.argv[2]||'matching-audit-output';
 if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('use empty output directory');
 const inputs=PINS.map(([name,blob])=>{const f=path.join(__dirname,name+'.cjs'),b=fs.readFileSync(f);ok(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')===blob,'source mismatch '+name);return {name,blob,...require(f).experiment()}});
 const tests=selfTest(),r=audit(inputs);ok(JSON.stringify(r)===JSON.stringify(audit(inputs)),'repeat');
 fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({...r,tests},null,2)+'\n');fs.writeFileSync(path.join(out,'index.html'),page(r));console.log(JSON.stringify({tests,runs:r.runs,witnesses:r.witnesses.length},null,2));
}
module.exports={PINS,solve,audit,selfTest,page};if(require.main===module)cli();
