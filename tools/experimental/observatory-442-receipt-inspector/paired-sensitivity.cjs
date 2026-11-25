'use strict';
// Measurement lane #442 / Draft #443. AI-assisted synthetic trace analysis only.
// Node >=18: node paired-sensitivity.cjs NEW_OUTPUT_DIRECTORY
const REF='d0632accb566f7b4634989ee36aeb1c6e2907f15';
const PINS=[['region-refinement','b9729da5b2f0532f2b509be21587b33f3ef21223'],['joint-reconstruction','a57455bb631f68808019435470dc63e7683cdedb'],['selective-reconstruction','5919b173dddacf6a30f7d058d0b08da042ffc7fa']];
const PAIRS=[[['shape-fit','symmetric-fit']],[['joint-fit','symmetric-fit']],[['joint-fit','symmetric-fit'],['overlap-gated','joint-fit'],['fixed-bg-joint','joint-fit']]];
const SEED=246813579,REPS=2000;
function check(x,m){if(!x)throw Error(m)}
function rng(seed){let x=seed>>>0;return ()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x/4294967296}}
function total(rows){return rows.reduce((s,r)=>({n:s.n+r.n,a:s.a+r.a,b:s.b+r.b,fpA:s.fpA+r.fpA,fpB:s.fpB+r.fpB}),{n:0,a:0,b:0,fpA:0,fpB:0})}
function delta(t){return t.n?100*(t.a-t.b)/t.n:null}
function group(rows,key){const out=new Map();for(const r of rows){const k=r[key];if(!out.has(k))out.set(k,[]);out.get(k).push(r)}return out}
function distribution(units,reps,seed){
 check(units.length&&reps>0,'empty resampling');const random=rng(seed),values=[];let zero=0;
 for(let i=0;i<reps;i++){let a=0,b=0,n=0;for(let j=0;j<units.length;j++){const v=units[Math.floor(random()*units.length)];a+=v.a;b+=v.b;n+=v.n}if(n)values.push(100*(a-b)/n);else zero++}
 values.sort((a,b)=>a-b);const q=p=>values.length?values[Math.floor(p*(values.length-1))]:null;
 return {units:units.length,reps,zeroDenominator:zero,lower:q(.025),median:q(.5),upper:q(.975),negative:values.filter(v=>v<0).length,positive:values.filter(v=>v>0).length,zero:values.filter(v=>v===0).length};
}
function compare(rows,reps=REPS,seed=SEED){
 check(rows.every(r=>Number.isInteger(r.n)&&r.n>=0&&r.a>=0&&r.a<=r.n&&r.b>=0&&r.b<=r.n&&Number.isSafeInteger(r.seed)),'invalid input');
 const pos=rows.filter(r=>r.n>0),nulls=rows.filter(r=>r.n===0),all=total(rows);
 const byGroup=[...group(rows,'group')].map(([name,x])=>{const t=total(x);return {name,packets:x.length,...t,delta:delta(t),leaveOut:delta(total(rows.filter(r=>r.group!==name)))}});
 const blocks=[...group(pos,'seed')].map(([seed,x])=>({seed,packets:x.length,...total(x)}));
 const groups=byGroup.filter(g=>g.n>0);
 // Null packets cannot change recall; report their false detections separately.
 return {packets:rows.length,...all,delta:delta(all),win:rows.filter(r=>r.a>r.b).length,loss:rows.filter(r=>r.a<r.b).length,tie:rows.filter(r=>r.a===r.b).length,
 nulls:{packets:nulls.length,...total(nulls)},byGroup,blocks,
 equalGroup:groups.length?groups.reduce((s,g)=>s+g.delta,0)/groups.length:null,
 packetResampling:pos.length?distribution(pos,reps,seed):null,
 seedBlockResampling:blocks.length?distribution(blocks,reps,seed):null};
}
function audit(inputs){
 const runs=inputs.map(({name,blob,receipt:r},i)=>{
 const comparisons=PAIRS[i].flatMap(([a,b])=>r.criteria.map(k=>{
 const ai=r.methods.indexOf(a),bi=r.methods.indexOf(b);check(ai>=0&&bi>=0,'missing method '+a+' '+b);
 const rows=r.rows.map((p,j)=>{
 const av=p.metrics[ai][k],bv=p.metrics[bi][k],n=p.truth.length;
 check(av.tp+av.fn===n&&bv.tp+bv.fn===n&&av.tp+av.fp===p.fits[ai].length&&bv.tp+bv.fp===p.fits[bi].length,'count identity');
 return {packet:j,group:p.condition.group,seed:p.condition.seed,n,a:av.tp,b:bv.tp,fpA:av.fp,fpB:bv.fp};
 });
 return {a,b,criterion:k,...compare(rows),rows};
 }));
 return {name,blob,rate:r.rate,comparisons};
 });
 return {schema:'mhac-paired-sensitivity-v1',sourceRef:REF,seed:SEED,repetitions:REPS,scope:'Finite synthetic corpus; resampling is descriptive sensitivity, not a population confidence interval or human evidence.',runs};
}
function selfTest(){
 const row=(seed,group,n,a,b)=>({seed,group,n,a,b,fpA:0,fpB:0});
 const x=[row(1,'x',1,1,0),row(1,'y',1,1,0),row(2,'x',1,0,1),row(2,'y',1,0,1),row(3,'null',0,0,0)];
 const t=compare(x,200,1);check(t.delta===0&&t.blocks.length===2&&t.packetResampling.units===4&&t.seedBlockResampling.units===2,'shared seed block');
 check(t.seedBlockResampling.lower===-100&&t.seedBlockResampling.upper===100,'block extremes');
 check(JSON.stringify(t)===JSON.stringify(compare(x,200,1)),'determinism');
 const tie=compare(x.map(r=>({...r,b:r.a})),200,1);check(tie.seedBlockResampling.zero===200&&tie.packetResampling.zero===200,'identical policies');
 const z=compare([row(3,'null',0,0,0)],20,1);check(z.delta===null&&z.seedBlockResampling===null,'undefined recall');
 const y=compare([row(1,'x',1,1,0),row(2,'y',3,0,3)],20,1);check(y.delta===-50&&y.equalGroup===0&&y.byGroup[0].leaveOut===-100,'weighting');
 let failed=false;try{compare([row(1,'x',1,2,0)],20,1)}catch(e){failed=true}check(failed,'invalid receipt');
 const zero=distribution([{n:0,a:0,b:0}],10,1);check(zero.zeroDenominator===10&&zero.median===null,'zero denominator');
 return 8;
}
function browser(d){
 const $=x=>document.getElementById(x),entries=d.runs.flatMap(r=>r.comparisons.map(c=>({run:r.name,...c})));
 const opt=(v,i)=>{const o=document.createElement('option');o.value=i;o.textContent=v;return o};
 entries.forEach((c,i)=>$('pair').append(opt(c.run+' / '+c.a+' vs '+c.b+' / '+c.criterion,i)));
 const fmt=x=>x===null?'—':x.toFixed(3);
 function table(node,rows){const t=document.createElement('table');for(const [i,row] of rows.entries()){const tr=t.insertRow();for(const v of row){const cell=document.createElement(i?'td':'th');cell.textContent=v;tr.append(cell)}}node.replaceChildren(t)}
 function show(){
 const c=entries[Number($('pair').value)];if(!c)return;
 $('headline').textContent='Finite recall difference: '+fmt(c.delta)+' pp; equal-group weighting: '+fmt(c.equalGroup)+' pp. Packet wins / ties / losses: '+[c.win,c.tie,c.loss].join(' / ')+'.';
 table($('uncertainty'),[['Resampling unit','Units','2.5th','Median','97.5th','Negative / zero / positive'],...[[ 'Packet (ignores shared seeds)',c.packetResampling],['Shared seed block',c.seedBlockResampling]].filter(x=>x[1]).map(([n,x])=>[n,x.units,fmt(x.lower),fmt(x.median),fmt(x.upper),[x.negative,x.zero,x.positive].join(' / ')])]);
 table($('groups'),[['Group','Packets','True events','A matches','B matches','A FP','B FP','Delta pp','Delta without group pp'],...c.byGroup.map(g=>[g.name,g.packets,g.n,g.a,g.b,g.fpA,g.fpB,fmt(g.delta),fmt(g.leaveOut)])]);
 const svg=$('plot');svg.replaceChildren();const draw=(tag,a,txt)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(a))e.setAttribute(k,v);if(txt!==undefined)e.textContent=txt;svg.append(e)};
 const rows=c.byGroup.filter(g=>g.delta!==null),max=Math.max(1,...rows.map(g=>Math.abs(g.delta))),h=32*rows.length+25,center=510;
 svg.setAttribute('viewBox','0 0 900 '+h);draw('line',{x1:center,x2:center,y1:0,y2:h,stroke:'currentColor',opacity:.4});
 rows.forEach((g,i)=>{const width=300*Math.abs(g.delta)/max,y=i*32+5;draw('text',{x:4,y:y+15,fill:'currentColor','font-size':14},g.name);draw('rect',{x:g.delta<0?center-width:center,y,width,height:20,fill:g.delta<0?'#a66b42':'#527ca5'});draw('text',{x:825,y:y+15,fill:'currentColor','font-size':13},fmt(g.delta)+' pp')});
 $('trace').textContent=JSON.stringify(c.rows.filter(r=>r.a!==r.b||r.fpA!==r.fpB),null,2);
 }$('pair').onchange=show;show();
}
function page(r){
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MHAC paired sensitivity</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem;color-scheme:light dark}select{max-width:100%;font:inherit}table{border-collapse:collapse;width:100%}td,th{padding:.4rem;border-bottom:1px solid #8885;text-align:right}td:first-child,th:first-child{text-align:left}svg{width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere}.scroll{overflow:auto}</style><h1>Paired receiver sensitivity</h1><p>Positive differences favour A. Recall differences are percentage points. Seed blocks preserve shared waveform seeds across condition groups. Quantiles are empirical resampling sensitivity, not inferential confidence intervals. Null packets have undefined recall; false positives are retained. <a href="receipt.json">Full replay receipt</a></p><label>Comparison <select id="pair"></select></label><p id="headline"></p><div id="uncertainty" class="scroll"></div><h2>Condition dependence</h2><svg id="plot" role="img" aria-label="Signed group recall differences"></svg><div id="groups" class="scroll"></div><details><summary>Packets with different counts</summary><pre id="trace"></pre></details><script>const d='+JSON.stringify(r).replace(/</g,'\\u003c')+';('+browser.toString()+')(d);</script></html>';
}
function cli(){
 const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),out=process.argv[2]||'paired-sensitivity-output';
 if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('Use an empty output directory');
 const inputs=PINS.map(([name,blob])=>{const f=path.join(__dirname,name+'.cjs'),b=fs.readFileSync(f);check(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')===blob,'source mismatch '+name);return {name,blob,...require(f).experiment()}});
 const tests=selfTest(),r=audit(inputs);check(JSON.stringify(r)===JSON.stringify(audit(inputs)),'repeat');
 fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({...r,tests},null,2)+'\n');fs.writeFileSync(path.join(out,'index.html'),page(r));console.log(JSON.stringify({tests,runs:r.runs.map(x=>({name:x.name,comparisons:x.comparisons.length}))}));
}
module.exports={PINS,compare,audit,selfTest,page};if(require.main===module)cli();
