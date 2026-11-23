// MHAC #209: finite context-late code synthesis. Node.js standard library only.

'use strict';

function validate(n, contexts) {
  if (!Number.isInteger(n)||n<1||n>10||!Array.isArray(contexts)) throw Error("expected 1..10 states and context array");
  for (const c of contexts) {
    if (!Array.isArray(c)||c.length!==n) throw Error("context length");
    for(const a of c) if(a!==null&&(!Array.isArray(a)||!a.length||a.some(x=>typeof x!=="string")||new Set(a).size!==a.length)) throw Error("allowed actions must be unique strings or null (impossible)");
  }
}

function common(group, context) {
  let result=null;
  for(const i of group) {
    const a=context[i];
    if(a===null) continue;
    result=result===null?[...a]:result.filter(x=>a.includes(x));
  }
  return result;
}

function validGroup(group, contexts) {
  return contexts.every(c=>{const a=common(group,c);return a===null||a.length>0;});
}

function forbidden(n, contexts) {
  validate(n,contexts);
  const bad=[];
  for(let m=1;m<(1<<n);m++) {
    const g=Array.from({length:n},(_,i)=>i).filter(i=>m&(1<<i));
    if(validGroup(g,contexts)) continue;
    if(g.every(i=>validGroup(g.filter(j=>i!==j),contexts))) bad.push(g);
  }
  return bad;
}

function solve(n, contexts) {
  validate(n,contexts);
  let best=Array.from({length:n},(_,i)=>[i]);
  function visit(i,groups) {
    if(i===n){if(groups.length<best.length)best=groups.map(g=>[...g]);return;}
    if(groups.length>=best.length)return;
    for(const g of groups) {
      g.push(i);
      if(validGroup(g,contexts))visit(i+1,groups);
      g.pop();
    }
    if(groups.length+1<best.length){groups.push([i]);visit(i+1,groups);groups.pop();}
  }
  visit(0,[]);
  return {alphabet:best.length,groups:best,decoder:contexts.map(c=>best.map(g=>common(g,c)?.[0]??null)),minimalForbidden:forbidden(n,contexts)};
}

function brute(n, contexts) {
  for(let k=1;k<=n;k++) {
    for(let code=0;code<k**n;code++) {
      let x=code; const labels=[];
      for(let i=0;i<n;i++){labels.push(x%k);x=Math.floor(x/k);}
      // Independent decoder-existence check: enumerate each context's action
      // union, and ask whether any action is allowed by all matching states.
      let ok=true;
      for(const c of contexts) {
        const actions=[...new Set(c.filter(a=>a!==null).flat())];
        for(let s=0;s<k;s++) {
          const active=c.map((a,i)=>({a,i})).filter(z=>z.a!==null&&labels[z.i]===s);
          if(active.length&&!actions.some(a=>active.every(z=>z.a.includes(a)))) {ok=false;break;}
        }
        if(!ok)break;
      }
      if(ok)return k;
    }
  }
  throw Error("unexpected impossible model");
}

function graphContexts(n, edges) {
  return edges.map(([i,j])=>Array.from({length:n},(_,k)=>k===i?["low"]:k===j?["high"]:null));
}

function graphEdges(n) {
  const edges=[];for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)edges.push([i,j]);return edges;
}

function run() {
  function check(b,msg){if(!b)throw Error(msg);}
  let graphs=0, setCases=0, supportCases=0;
  const graphHistogram={};
  for(let n=1;n<=5;n++) {
    const edges=graphEdges(n);
    for(let m=0;m<(1<<edges.length);m++) {
      const es=edges.filter((e,i)=>m&(1<<i));const c=graphContexts(n,es);
      const a=solve(n,c);
      check(a.alphabet===brute(n,c),"graph oracle");
      check(a.minimalForbidden.length===es.length&&a.minimalForbidden.every(g=>g.length===2),"edge reduction");
      check(a.groups.every(g=>validGroup(g,c)),"valid partition");
      graphs++;graphHistogram[n+":"+a.alphabet]=(graphHistogram[n+":"+a.alphabet]||0)+1;
    }
  }
  const acts=["a","b","c"];const sets=Array.from({length:7},(_,i)=>acts.filter((a,j)=>(i+1)&(1<<j)));
  for(const a of sets)for(const b of sets)for(const c of sets){const cs=[[a,b,c]];check(solve(3,cs).alphabet===brute(3,cs),"set oracle");setCases++;}
  const choices=[null,["a"],["b"],["a","b"]],contexts=[];
  for(const a of choices)for(const b of choices)for(const c of choices)contexts.push([a,b,c]);
  for(const a of contexts)for(const b of contexts){const cs=[a,b];check(solve(3,cs).alphabet===brute(3,cs),"two contexts");supportCases++;}
  const odd=solve(5,graphContexts(5,[[0,1],[1,2],[2,3],[3,4],[0,4]]));
  const path=solve(5,graphContexts(5,[[0,1],[1,2],[2,3],[3,4]]));
  const clique=Array.from({length:8},(_,i)=>i+1).map(n=>({n,...solve(n,graphContexts(n,graphEdges(n)))}));
  const higher=solve(3,[[["a","b"],["b","c"],["a","c"]]]);
  const negative=solve(3,[[["a"],["a"],null],[null,["a"],["a"]]]);
  check(odd.alphabet===3&&path.alphabet===2&&higher.alphabet===2&&negative.alphabet===1,"named controls");
  check(JSON.stringify(higher.minimalForbidden)==="[[0,1,2]]","triple obstruction");
  check(clique.every(c=>c.alphabet===c.n),"unbounded family small cases");
  for(const bad of [[[[]]],[[["a","a"]]],[[1]]]) {let refused=false;try{solve(1,bad);}catch{refused=true;}check(refused,"invalid inputs");}
  return {graphs,setCases,supportCases,totalOracleComparisons:graphs+setCases+supportCases,graphHistogram,odd,path,clique:clique.map(c=>({n:c.n,alphabet:c.alphabet})),higher,negative};
}

if (typeof module !== 'undefined') { module.exports={solve,forbidden,run}; if(require.main===module) console.log(JSON.stringify(run(),null,2)); }
