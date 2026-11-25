"use strict";
// Enumerate direct window sums, not the difference-graph construction.
function audit(api){
  const check=(b,msg)=>{if(!b)throw Error(msg);};
  const {solve,classify}=api;
  function* compositions(n,s){
    if(n===1){yield [s];return;}
    for(let i=0;i<=s;i++)for(const a of compositions(n-1,s-i))yield [i,...a];
  }
  const direct=(x,w)=>x.map((_,i)=>Array.from({length:w},(_,j)=>x[(i+j)%x.length]).reduce((a,b)=>a+b,0));
  const result={traces:0,measurementClasses:0,peakWitnesses:0,thresholdChecks:0,refusals:0,byN:{}};
  for(let n=1;n<=8;n++){
    let classes=0, traces=0;
    const families=[];
    for(let a=1;a<=n;a++){
      families.push([a]);
      for(let b=a+1;b<=n;b++)families.push([a,b]);
    }
    for(const widths of families){
      const groups=new Map();
      for(let total=0;total<=5;total++)for(const x of compositions(n,total)){
        const streams=widths.map(width=>({width,sums:direct(x,width)}));
        const key=JSON.stringify(streams), peak=Math.max(...x);
        if(!groups.has(key))groups.set(key,{streams,count:0,peaks:new Set()});
        const group=groups.get(key);group.count++;group.peaks.add(peak);traces++;
      }
      for(const {streams,count,peaks} of groups.values()){
        const r=solve(n,streams), min=Math.min(...peaks),max=Math.max(...peaks);
        check(r.status===(count===1?"unique":"ambiguous"),"status");
        check(r.count===String(count)&&r.minPeak===min&&r.maxPeak===max,"bounds/count");
        check(peaks.size===max-min+1,"peak interval");
        for(const [x,p] of [[r.lowWitness,min],[r.highWitness,max]]){
          check(x.every(v=>v>=0&&Number.isInteger(v))&&Math.max(...x)===p,"witness peak");
          check(streams.every(s=>direct(x,s.width).every((v,i)=>v===s.sums[i])),"witness streams");
          result.peakWitnesses++;
        }
        for(let t=0;t<=6;t++){
          const yes=[...peaks].some(p=>p>=t),no=[...peaks].some(p=>p<t);
          check(classify(r,t)===(yes&&no?"undetermined":yes?"certain-at-or-above":"certain-below"),"threshold");
          result.thresholdChecks++;
        }
        classes++;
      }
    }
    result.byN[n]={traces,classes};result.traces+=traces;result.measurementClasses+=classes;
  }
  const bad=[
    [4,[{width:2,sums:[1,0,0,0]}]],
    [6,[{width:4,sums:[1,1,1,1,1,1]}]],
    [4,[{width:1,sums:[1,1,1,1]},{width:2,sums:[3,3,3,3]}]],
    [4,[{width:2,sums:[0,1,2,1]} ,{width:4,sums:[3,3,3,3]}]]
  ];
  for(const [n,s] of bad){check(solve(n,s).status==="inconsistent","refusal");result.refusals++;}
  for(const [n,s] of [[0,[]],[4,[]],[2,[{width:1,sums:Array(2)}]],[2,[{width:1,sums:[0,-1]}]],[2,[{width:2,sums:[0,0]},{width:2,sums:[0,0]}]]]){
    let refused=false;try{solve(n,s);}catch(e){refused=e instanceof RangeError;}
    check(refused,"invalid input");result.refusals++;
  }
  const example=solve(16,[{width:8,sums:Array(16).fill(8)},{width:16,sums:Array(16).fill(16)}]);
  check(example.minPeak===1&&example.maxPeak===8&&example.count==="6435","constant example");
  result.example=example;
  const extra=solve(16,[{width:8,sums:Array(16).fill(8)},{width:16,sums:Array(16).fill(16)},{width:7,sums:Array(16).fill(7)}]);
  check(extra.status==="unique"&&extra.maxPeak===1,"coprime repair");
  const ws=[6,10,15];
  const streams=ws.map(width=>({width,sums:Array(30).fill(width)}));
  const pairs=[[0,1],[0,2],[1,2]].map(p=>solve(30,p.map(i=>streams[i])));
  check(pairs.every(r=>r.status==="ambiguous"),"pairwise ambiguity");
  const full=solve(30,streams);
  check(full.status==="unique"&&full.maxPeak===1,"three-way repair");
  result.multiwayRepair={widths:ws,pairGcd:pairs.map(r=>r.g),pairMaxPeak:pairs.map(r=>r.maxPeak),allGcd:full.g};
  const cap=solve(256,[{width:256,sums:Array(256).fill(1e9)}]);
  check(cap.maxPeak===1e9&&cap.minPeak===3906250&&cap.count.length>1000,"integer bounds");
  return result;
}
module.exports={audit};
if(typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(audit(require("./meter.cjs")),null,2));
