// Original MHAC synthetic model. Node: node laboratory.cjs > execution.json
"use strict";
function run() {
  const n=4, full=(1<<n)-1;
  const pop=x=>{let k=0;while(x){x&=x-1;k++}return k};
  const perms=(xs)=>xs.length?xs.flatMap((v,i)=>perms(xs.filter((_,j)=>i!==j)).map(p=>[v,...p])):[[]];
  const orders=perms([0,1,2,3]);
  const fail=(cond,msg)=>{if(!cond)throw Error(msg)};
  const enabled=(sys,S,i)=>!(S&(1<<i))&&pop(S&sys[i][0])>=sys[i][1];
  // One arbitrary monotone quota per target, with no redundant zero quota menus.
  const options=Array.from({length:n},(_,i)=>{
    let a=[[0,0]];
    for(let m=1;m<=full;m++)if(!(m&(1<<i)))for(let k=1;k<=pop(m);k++)a.push([m,k]);
    return a;
  });
  const legal=(sys,p)=>{
    let S=0;
    for(let i of p){if(!enabled(sys,S,i))return false;S|=1<<i}
    return true;
  };
  function closure(sys,forbid=-1) {
    let S=0,old;
    do {old=S;for(let i=0;i<n;i++)if(i!==forbid&&enabled(sys,S,i))S|=1<<i}while(old!==S);
    return S;
  }
  function prefixDP(sys){
    const dp=Array(1<<n).fill(0);dp[0]=1;
    for(let S=0;S<full;S++)if(dp[S])for(let i=0;i<n;i++)if(enabled(sys,S,i))dp[S|(1<<i)]+=dp[S];
    return dp;
  }
  const tally={systems:0,feasible:0,infeasible:0,permutationChecks:0,prefixChecks:0,unionChecks:0,rankChecks:0,precedenceChecks:0,pairwiseInsufficient:0,orderCountHistogram:{}};
  function inspect(sys){
    tally.systems++;
    const good=orders.filter(p=>legal(sys,p));tally.permutationChecks+=orders.length;
    const dp=prefixDP(sys);
    fail(dp[full]===good.length,"DP count");
    fail((closure(sys)===full)===(good.length>0),"greedy feasibility");
    tally.orderCountHistogram[good.length]=(tally.orderCountHistogram[good.length]||0)+1;
    if(!good.length){tally.infeasible++;return}
    tally.feasible++;
    const actual=new Set([0]);
    for(let p of good){let S=0;for(let i of p){S|=1<<i;actual.add(S)}}
    for(let S=0;S<=full;S++){fail(Boolean(dp[S])===actual.has(S),"all prefixes extend");tally.prefixChecks++}
    for(let S of actual)for(let T of actual){fail(actual.has(S|T),"prefix union");tally.unionChecks++}
    const edges=[];
    for(let i=0;i<n;i++){
      const C=closure(sys,i);
      fail(pop(C)+1===Math.max(...good.map(p=>p.indexOf(i)+1)),"latest rank");
      tally.rankChecks++;
      for(let j=0;j<n;j++)if(i!==j){
        const forced=!(C&(1<<j));
        fail(forced===good.every(p=>p.indexOf(i)<p.indexOf(j)),"forced edge");
        tally.precedenceChecks++;
        if(forced)edges.push([i,j]);
      }
    }
    const pairOnly=orders.filter(p=>edges.every(([i,j])=>p.indexOf(i)<p.indexOf(j)));
    if(pairOnly.length>good.length)tally.pairwiseInsufficient++;
  }
  function walk(sys=[]){if(sys.length===n)inspect(sys);else for(let o of options[sys.length])walk([...sys,o])}
  walk();
  const example=[[0,0],[0,0],[0,0],[7,2]];
  const good=orders.filter(p=>legal(example,p));
  const scopeHistogram={};let scopeWorlds=0;
  for(let p of good){const r=p.indexOf(3);const choices=r*(r-1)/2;scopeHistogram[r+1]=(scopeHistogram[r+1]||0)+choices;scopeWorlds+=choices}
  fail(good.length===12&&scopeWorlds===24&&scopeHistogram[3]===6&&scopeHistogram[4]===18,"hidden scope example");
  const deadlock=[[6,1],[5,1],[3,1],[0,0]];
  fail(closure(deadlock)===8&&prefixDP(deadlock)[full]===0,"collective deadlock");
  const properRelaxations=[];
  for(let i=0;i<3;i++){const s=deadlock.map((o,j)=>j===i?[0,0]:o);fail(closure(s)===full,"relaxed deadlock");properRelaxations.push(prefixDP(s)[full])}
  return {contract:"Four labels; order runs from more expected to less expected; one exact hidden nonempty scope quota per target or no marker; all propositions stipulated true; no human data", optionsPerTarget:options.map(a=>a.length),tally,example:{validOrders:good.map(p=>p.map(i=>"ABCD"[i]).join("")),scopeWorlds,scopeWorldsByRank:scopeHistogram,uniformOrdersRank4:[6,12],uniformOrderScopePairsRank4:[18,24]},deadlock:{closure:"D",compatibleOrders:0,countsAfterSuspendingOneOfABC:properRelaxations},score:{target:[["D",0],["MARK",1]],edition1:{scope:["A","B"],order:"ABDC"},edition2:{scope:["B","C"],order:"BCDA"},edition3:{scope:["A","B","C"],order:"ABCD"},instruction:"Same target notes; preceding menu cards and order hypotheses are independent of the target; no claim of universal audibility"}};
}
if(typeof module!=="undefined"&&require.main===module) process.stdout.write(JSON.stringify(run(),null,2)+"\n");
