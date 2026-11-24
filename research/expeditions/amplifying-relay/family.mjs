import {fromWeights,rate,peak,guards} from "./relay.mjs";
for(let k=2;k<=64;k++){
 const g=fromWeights([[0,k*k,0],[0,0,k*k],[1,0,0]],k),s=guards(g);
 if(rate(g).status!=="growing"||s.status!=="optimal"||s.cost!==1||s.solutions.length!==3)throw Error("guard family "+k);
 for(const edges of s.solutions){
  const p=peak(g,new Set(edges)),expect=edges[0]==="1:2"?BigInt(k):BigInt(k*k);
  if(p.unbounded||p.num!==expect*p.den||rate(g,new Set(edges)).num!==0n)throw Error("peak family "+k);
 }
 const cap=guards(g,{cap:{num:BigInt(k),den:1n}});
 if(cap.status!=="optimal"||cap.solutions.length!==1||cap.solutions[0][0]!=="1:2")throw Error("cap family "+k);
}
console.log("63 parametric ring cases K=2..64 passed");
