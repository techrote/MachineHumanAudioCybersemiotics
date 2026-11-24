"use strict";
function main(){
  // Fractions p,a,c,t,q on a tenths grid. q' denominator D^3.
  const D=10, scale=D**3;
  let configurations=0, transitions=0, checks=0;
  function assert(x,msg){checks++;if(!x)throw Error(msg)}
  for(let t=1;t<D;t++)for(let p=t+1;p<=D;p++)for(let a=1;a<=D;a++)for(let c=0;c<=D;c++){
    configurations++;
    // low-regime fixed point = a*p / (D^2-(D-a)*(D-c)).
    const den=D**2-(D-a)*(D-c), num=a*p;
    const relation=num*D-t*den;
    for(let q=0;q<=D;q++){
      transitions++;
      const factor=q<t?D-c:D;
      const next=a*p*D+(D-a)*factor*q;
      // independent mass bookkeeping: fresh B, inherited B, overwritten B.
      const fresh=a*p*D, inherited=(D-a)*q*D;
      const overwritten=q<t?(D-a)*q*c:0;
      assert(next===fresh+inherited-overwritten,"mass accounting");
      assert(next>=0&&next<=scale,"range");
      if(q>=t)assert(next>=t*D**2,"high basin");
      else{
        if(relation<=0&&(D-a)*(D-c)>0)assert(next<t*D**2,"low basin");
        if(relation<0)assert(next<t*D**2,"strict low basin");
        if(relation>0)assert(next>q*D**2,"recovery progress");
        if(relation===0&&(D-a)*(D-c)===0)assert(next===t*D**2,"degenerate equality");
        // movement points toward low fixed point
        assert(Math.sign(next-q*D**2)===Math.sign(num*D-q*den),"fixed point direction");
      }
    }
  }
  const paths=[];
  function gcd(a,b){return b?gcd(b,a%b):a}
  function frac(a,b=1n){let g=gcd(a,b);return [a/g,b/g]}
  function add([a,b],[c,d]){return frac(a*d+c*b,b*d)}
  function mul([a,b],[c,d]){return frac(a*c,b*d)}
  function run(label,raw,retain,start,steps){
    let q=start;const values=[];
    for(let i=0;i<=steps;i++){
      values.push(Number(q[0])/Number(q[1]));
      const low=2n*q[0]<q[1];
      q=add(mul(raw,[3n,5n]),mul(mul(retain,low?[1n,2n]:[1n,1n]),q));
    }
    paths.push({label,values});
    return q;
  }
  run("low-start", [1n,4n],[3n,4n],[0n,1n],12);
  run("high-start",[1n,4n],[3n,4n],[3n,5n],12);
  run("raw-recovery",[3n,4n],[1n,4n],[0n,1n],12);
  assert(paths[0].values.every(q=>q<.5),"low example");
  assert(paths[1].values.every(q=>q===.6),"high example");
  assert(paths[2].values[2]>.5,"recovery example");
  const out={configurations,transitions,checks,paths};
  return out;
}
console.log(JSON.stringify(main(),null,2));
