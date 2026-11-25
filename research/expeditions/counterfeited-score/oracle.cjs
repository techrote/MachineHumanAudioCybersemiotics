'use strict';
// Synthetic finite audit; no human or audio evidence.
function audit(){
  const n=6, ids=Array.from({length:n},(_,i)=>i);
  function permutations(xs){if(!xs.length)return [[]];return xs.flatMap((x,i)=>permutations(xs.filter((_,j)=>i!==j)).map(p=>[x,...p]));}
  function factorial(x){let r=1;for(let i=2;i<=x;i++)r*=i;return r;}
  const perms=permutations(ids), hist=Array(n+1).fill(0), survivors=Array(1<<n).fill(0);
  let assertions=0;
  function check(x,msg){assertions++;if(!x)throw Error(msg);}
  check(perms.length===factorial(n),"permutation count");
  check(new Set(perms.map(p=>p.join(","))).size===perms.length,"uniqueness");
  for(const p of perms){
    check(p.length===n&&p.every(x=>ids.includes(x))&&new Set(p).size===n,"bijection");
    const fixed=p.reduce((mask,x,i)=>mask|(x===i?1<<i:0),0);
    hist[ids.filter(i=>p[i]===i).length]++;
    for(let mask=0;mask<1<<n;mask++){
      const pass=ids.every(i=>!(mask&(1<<i))||p[i]===i);
      check(pass===((fixed&mask)===mask),"subset audit");
      if(pass)survivors[mask]++;
    }
  }
  function derangements(k){let a=1,b=0;if(k===0)return a;for(let j=2;j<=k;j++)[a,b]=[b,(j-1)*(a+b)];return b;}
  for(let k=0;k<=n;k++)check(hist[k]===factorial(n)/(factorial(k)*factorial(n-k))*derangements(n-k),"fixed point distribution");
  for(let mask=0;mask<1<<n;mask++){
    const missing=ids.filter(i=>!(mask&(1<<i)));
    check(survivors[mask]===factorial(missing.length),"remaining permutation count");
    if(missing.length>=2){
      const witness=[...ids];[witness[missing[0]],witness[missing[1]]]=[witness[missing[1]],witness[missing[0]]];
      check(witness.some((x,i)=>x!==i)&&ids.every(i=>!(mask&(1<<i))||witness[i]===i),"hidden transposition");
    }
    if(missing.length>=1){
      const arbitrary=[...ids];arbitrary[missing[0]]=(missing[0]+1)%n;
      check(arbitrary.some((x,i)=>x!==i)&&ids.every(i=>!(mask&(1<<i))||arbitrary[i]===i),"unrestricted-function witness");
    }
  }
  const tapes=ids.flatMap(a=>ids.map(b=>[a,b])); // independent cue/response pairs
  check(tapes.filter(([a,b])=>a===b).length===n,"independent response match count");
  return {permutations:perms.length,subset_policy_cases:perms.length*(1<<n),fixed_point_histogram:hist,remaining_after_k_distinct_passes:ids.concat(n).map(k=>factorial(n-k)),assertions};
}
console.log(JSON.stringify(audit(),null,2));
