/* Finite synthetic three-survivor margin search; exact final comparison. */
const search = function search(){
 const N=12,K=3,A=1000,L=N+K-2;
 let seed=788;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 const triples=[];for(let i=0;i<N;i++)for(let j=i+1;j<N;j++)for(let k=j+1;k<N;k++)for(let s=0;s<K;s++)for(let u=s+1;u<K;u++)triples.push([i+s,j+s,k+s,i+u,j+u,k+u,i,j,k,s,u]);
 function raw(a,b,c,d,e,f){const p=(a-b)**2+(a-c)**2+(b-c)**2,q=(d-e)**2+(d-f)**2+(e-f)**2,C=Math.abs((a-b)*(d-e)+(a-c)*(d-f)+(b-c)*(e-f));if(!p||!q)return [p+q,3];if(C>p)return [p*q-C*C,3*p];if(C>q)return [p*q-C*C,3*q];return [p+q-2*C,3]}
 function score(x,stop=-1){let best=Infinity,witness=null,frac=null;for(const t of triples){const [a,b]=raw(...t.slice(0,6).map(i=>x[i]));let v=a/b;if(v<best){best=v;witness=t.slice(6);frac=[a,b];if(best<=stop)return {best,witness,frac}}}return {best,witness,frac}}
 let best=Array.from({length:L+1},(_,i)=>Math.round(A*(2*(i/L)**2-1))),val=score(best).best,base=val,randomBest=0,evals=1;
 for(let i=0;i<4000;i++){let x=Array.from({length:L+1},()=>Math.round(A*(2*rand()-1)));let z=score(x,val);evals++;randomBest=Math.max(randomBest,z.best);if(z.best>val){best=x;val=z.best}}
 let initial=val;
 for(let i=0;i<16000;i++){let x=best.slice(),j=Math.floor(rand()*x.length);let step=[1,5,20,80,300][Math.floor(rand()*5)];x[j]=Math.max(-A,Math.min(A,x[j]+Math.round((2*rand()-1)*step)));let z=score(x,val);evals++;if(z.best>val){best=x;val=z.best}}
 // exact full certificate, BigInt cross-multiplication (all raw integers exact as safe IEEE integers)
 let cert=null,where=[];
 for(const t of triples){let [a,b]=raw(...t.slice(0,6).map(i=>best[i]));if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a<0||b<=0)throw Error("unsafe");if(!cert||BigInt(a)*BigInt(cert[1])<BigInt(cert[0])*BigInt(b)){cert=[a,b];where=[t.slice(6)]}else if(BigInt(a)*BigInt(cert[1])===BigInt(cert[0])*BigInt(b))where.push(t.slice(6))}
 let den=BigInt(cert[1])*BigInt(A)**2n,num=BigInt(cert[0]);let a=num,b=den;while(b){[a,b]=[b,a%b]}const D=Number(num)/Number(den);return {N,K,A,evals,checks:triples.length,sequence:best,quantizedQuadraticRadius:Math.sqrt(base)/A/2,randomSearchRadius:Math.sqrt(initial)/A/2,finalDistanceSquared:(num/a)+"/"+(den/a),finalRadius:Math.sqrt(D)/2,where,improvementVsExactQuadratic:Math.sqrt(D/(32/41499133)),claim:"finite seeded heuristic; exact final certificate, no global optimality claim"};
};
console.log(JSON.stringify(search(),null,2));
