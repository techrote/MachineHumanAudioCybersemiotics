function laboratory(){
 const assert=(b,m)=>{if(!b)throw Error(m)};
 const S=[];for(const a of [-1,1])for(const c of [-1,1])for(const u of [-1,1])for(const v of [-1,1])S.push([a,c,u,v]);
 const labels={A:S.map(s=>s[0]),C:S.map(s=>s[1]),B:S.map(s=>2*s[2]+s[3])};
 const model=(alpha,beta)=>S.map(([a,c,u,v])=>BigInt(20+5*a*u+c*(alpha*u+beta*v)+5*a*c));
 const identity=S.map((_,i)=>S.map((_,j)=>BigInt(i===j)));
 function apply(M,w,L){
   const lab=labels[L],factor=L==="B"?2n:1n;
   return M.map(row=>{let totals=new Map();row.forEach((v,k)=>totals.set(lab[k],(totals.get(lab[k])||0n)+v));return w.map((v,j)=>v*factor*totals.get(lab[j]));});
 }
 const reset=(M,w,d)=>M.every(row=>row.every((v,j)=>320n*v===d*w[j]));
 const word=(w,s)=>{let M=identity,d=1n;for(const L of s){M=apply(M,w,L);d*=160n}return [M,d]};
 const perms=["ABC","ACB","BAC","BCA","CAB","CBA"];
 const gcd=(a,b)=>b===0n?a:gcd(b,a%b);
 const rat=(a,b)=>{let g=gcd(a,b);return `${a/g}/${b/g}`};
 let wordChecks=0,rowChecks=0,cycleChecks=0,omissionChecks=0,mixtureChecks=0;
 let profiles=[];
 for(const [a,b] of [[0,5],[3,4],[-3,4],[5,0],[-5,0]]){
   const w=model(a,b);assert(w.every(x=>x>0n)&&w.reduce((x,y)=>x+y,0n)===320n,"weights");
   for(const L of "ABC"){let [M,d]=word(w,L);let [M2,d2]=word(w,L+L);assert(M.every((r,i)=>r.every((v,j)=>v*d2===M2[i][j]*d)),"idempotence");assert(M.every((r,i)=>r.every((v,j)=>w[i]*v===w[j]*M[j][i])),"detailed balance")}
   function visit(s,M,d){
     if(s.length){
       const target=a===0&&(/ABC|CBA/.test(s));
       assert(reset(M,w,d)===target,"word "+a+" "+s);
       assert(M.every(r=>r.reduce((x,y)=>x+y,0n)===d),"row sums");
       wordChecks++;rowChecks+=16;
     }
     if(s.length<8)for(const L of "ABC")if(!s.endsWith(L))visit(s+L,apply(M,w,L),d*160n);
   }
   visit("",identity,1n);
   const cycles=[];
   for(const s of perms){
     const [M,d]=word(w,s),[N,e]=word(w,s+s);
     // Residual scalar is alpha/64 = a/320; compare after multiplying denominators.
     assert(M.every((r,i)=>r.every((v,j)=>320n*(320n*N[i][j]-e*w[j])*d===BigInt(a)*(320n*v-d*w[j])*e)),"cycle factor");
     assert(reset(N,w,e)===(a===0),"two-cycle reset");
     const abs=x=>x<0n?-x:x;
     const nums=M.map(r=>r.reduce((sum,v,j)=>sum+abs(320n*v-d*w[j]),0n));
     let max=nums.reduce((x,y)=>x>y?x:y,0n);
     cycles.push({word:s,reset:reset(M,w,d),worstRowTV:rat(max,640n*d)});
     cycleChecks++;
   }
   profiles.push({alphaNumerator:a,betaNumerator:b,denominator:5,cycles});
 }
 const w=model(0,5);
 for(let e=0;e<=4;e++){
   const s="A".repeat(e+1)+"B".repeat(e+1)+"C".repeat(e+1);
   function omit(i,left,t){
     if(i===s.length){let [M,d]=word(w,t);assert(reset(M,w,d),"omission");omissionChecks++;return}
     omit(i+1,left,t+s[i]);if(left)omit(i+1,left-1,t);
   }
   omit(0,e,"");
 }
 const neg=model(-5,0),[X,d]=word(neg,"AAC"),[Y,e]=word(neg,"ABC");
 assert(d===e&&!reset(X,neg,d)&&!reset(Y,neg,e),"non-erasing components");
 assert(X.every((r,i)=>r.every((v,j)=>320n*(v+4n*Y[i][j])===5n*d*neg[j])),"hidden mixture");
 mixtureChecks=256;
 return {wordChecks,rowChecks,cycleChecks,omissionChecks,mixtureChecks,profiles,assertionFailures:0};
}
console.log(JSON.stringify(laboratory(),null,2));
