// Original MHAC bounded finite model; no dependencies.
function experiment() {
  const NOTES=["B","C","D"], full=7;
  function labels(mask) {return NOTES.filter((_,i)=>mask&(1<<i));}
  function inspect(menus) {
    if (!Array.isArray(menus)||!menus.length||menus.some(x=>!Number.isInteger(x)||x<1||x>7)) throw Error("Expected nonempty family of nonempty 3-note menus");
    const unique=[...new Set(menus)].sort((a,b)=>a-b);
    const possible=unique.reduce((a,b)=>a|b,0);
    const guaranteed=unique.reduce((a,b)=>a&b,full);
    return {menus:unique.map(labels),possible:labels(possible),guaranteed:labels(guaranteed),
      completedTraces:labels(possible).map(n=>"A"+n),
      minMenuSize:Math.min(...unique.map(x=>labels(x).length)),
      maxMenuSize:Math.max(...unique.map(x=>labels(x).length)),
      possibleMask:possible,guaranteedMask:guaranteed};
  }
  function families() {
    return Array.from({length:127},(_,i)=>Array.from({length:7},(_,k)=>k+1).filter((_,k)=>(i+1)&(1<<k)));
  }
  function run() {
    let checks=0;
    function check(x,msg){checks++;if(!x)throw Error(msg);}
    const open=inspect([7]), split=inspect([1,2,4]), overlapping=inspect([3,5,6]), partial=inspect([3,5]);
    check(JSON.stringify(open.completedTraces)===JSON.stringify(split.completedTraces),"trace sets differ");
    check(open.guaranteedMask===7&&split.guaranteedMask===0,"open/split guarantees");
    check(overlapping.minMenuSize===2&&overlapping.guaranteedMask===0,"pairwise overlap not global");
    check(partial.guaranteedMask===1,"partial overlap guarantees B");
    check(JSON.stringify(inspect([5,3,3]))===JSON.stringify(partial),"duplicate/order invariance");
    const all=families(), byUnion={}, fullIntersectionCounts={};
    let zero=0;
    for(const menus of all){
      const s=inspect(menus);
      const independent=NOTES.filter((_,i)=>menus.every(x=>x&(1<<i)));
      check(JSON.stringify(independent)===JSON.stringify(s.guaranteed),"intersection oracle");
      check(s.completedTraces.length===NOTES.filter((_,i)=>menus.some(x=>x&(1<<i))).length,"union oracle");
      check((s.guaranteedMask&s.possibleMask)===s.guaranteedMask,"subset invariant");
      byUnion[s.possibleMask]=(byUnion[s.possibleMask]||0)+1;
      if(s.possibleMask===full){
        fullIntersectionCounts[s.guaranteedMask]=(fullIntersectionCounts[s.guaranteedMask]||0)+1;
        if(s.guaranteedMask===0)zero++;
      }
    }
    check(all.length===127&&new Set(all.map(x=>x.join(","))).size===127,"all families unique");
    check(byUnion[7]===109,"full trace class count");
    check(Object.keys(fullIntersectionCounts).length===8,"all intersections represented");
    check(Object.values(fullIntersectionCounts).reduce((a,b)=>a+b,0)===109,"intersection histogram");
    check(JSON.stringify(inspect([1]).guaranteed)===JSON.stringify(inspect([1]).possible),"single menu control");
    for(const bad of [[],[0],[8],[1.5],null]){let rejected=false;try{inspect(bad)}catch{rejected=true}check(rejected,"bad menu accepted")}
    return {schema:"unchosen-note/v1",checks,fullAlphabet:NOTES,totalFamilies:all.length,fullTraceClass:byUnion[7],fullTraceClassNoGuarantee:zero,byUnion,fullIntersectionCounts,examples:{open,split,overlapping,partial}};
  }
  return {inspect,families,run,labels};
}
export const {inspect,families,run,labels}=experiment();
