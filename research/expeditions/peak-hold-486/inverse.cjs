'use strict';
// Synthetic cyclic maximum-meter inverse. No dependencies.
// windows: [{start,length,value}], every coordinate must be covered.
function compile(n, windows) {
  if (!Number.isInteger(n) || n<1 || n>512 || !Array.isArray(windows) || !windows.length)
    throw new RangeError('invalid ring or windows');
  const cap=Array(n).fill(Infinity);
  const rows=windows.map(({start,length,value})=>{
    if (!Number.isInteger(start)||start<0||start>=n||!Number.isInteger(length)||length<1||length>n||!Number.isSafeInteger(value)||value<0)
      throw new RangeError('invalid window');
    const indices=Array.from({length},(_,k)=>(start+k)%n);
    for(const i of indices)cap[i]=Math.min(cap[i],value);
    return {start,length,value,indices};
  });
  if(cap.some(x=>!Number.isFinite(x)))throw new RangeError('uncovered coordinate');
  const levels=new Map(), forced=new Set();
  let erasureLimit=null;
  for(let j=0;j<rows.length;j++){
    const row=rows[j], h=row.value;
    if(!h)continue;
    const candidates=row.indices.filter(i=>cap[i]===h);
    if(!candidates.length)return {status:'inconsistent',row:j,cap};
    erasureLimit=erasureLimit===null?candidates.length-1:Math.min(erasureLimit,candidates.length-1);
    if(candidates.length===1)forced.add(candidates[0]);
    if(!levels.has(h))levels.set(h,[]);
    levels.get(h).push(candidates);
  }
  const sparse=Array(n).fill(0), certificates=[];
  for(const [h,sets] of [...levels].sort((a,b)=>a[0]-b[0])){
    // Every solution must choose a point in the smallest candidate set.
    // Condition on that point, cut circle there, and greedily stab remaining intervals.
    const anchorSet=sets.reduce((a,b)=>a.length<=b.length?a:b);
    let best=null;
    for(const anchor of anchorSet){
      const distance=i=>(i-anchor+n)%n;
      const remaining=sets.filter(s=>!s.includes(anchor)).map(s=>{
        const sorted=s.slice().sort((a,b)=>distance(a)-distance(b));
        return {points:sorted,left:distance(sorted[0]),right:distance(sorted[sorted.length-1]),last:sorted[sorted.length-1]};
      }).sort((a,b)=>a.right-b.right);
      const chosen=[anchor];let last=0;
      for(const arc of remaining)if(last<arc.left){chosen.push(arc.last);last=arc.right;}
      // candidate points share a common level, so interval membership is exact.
      const chosenSet=new Set(chosen);
      if(!sets.every(s=>s.some(i=>chosenSet.has(i))))throw Error('internal stabbing failure');
      if(best===null||chosen.length<best.length)best=chosen;
    }
    for(const i of best)sparse[i]=h;
    certificates.push({level:h,minimum:best.length,positions:best});
  }
  return {status:'feasible',cap,sparse,forced:[...forced].sort((a,b)=>a-b),erasureLimit,certificates};
}
function observe(x,widths){
  return widths.flatMap(length=>x.map((_,start)=>({start,length,value:Math.max(...Array.from({length},(_,j)=>x[(start+j)%x.length]))})));
}
if(typeof module!=='undefined')module.exports={compile,observe};
