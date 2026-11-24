// MHAC #234; dependency-free exact grid laboratory. C=correct, W=wrong, S=abstain.
// Bounds are integer numerators: divide by n*D for mean loss difference.
function counts(a,b) {
  if(!Array.isArray(a)||!Array.isArray(b)||a.length!==b.length||!a.length||a.some(x=>!['C','W','S'].includes(x))||b.some(x=>!['C','W','S'].includes(x))) throw Error("matched nonempty C/W/S roster required");
  let w=0,p=0,m=0,aa=0,bb=0;
  for(let i=0;i<a.length;i++){w+=Number(a[i]==='W')-Number(b[i]==='W');aa+=Number(a[i]==='S');bb+=Number(b[i]==='S');if(a[i]==='S'&&b[i]!=='S')p++;if(b[i]==='S'&&a[i]!=='S')m++;}
  return {n:a.length,w,p,m,r:a.length-p-m,aa,bb};
}

function bounds(c,D,T=null) {
  const {n,w,p,m,r}=c;
  if(![n,w,p,m,r,D].every(Number.isSafeInteger)||n<1||D<1||!Number.isSafeInteger(n*D)||!Number.isSafeInteger(2*n*D)||Math.abs(w)>n||p<0||m<0||r<0||p+m+r!==n||T!==null&&(!Number.isSafeInteger(T)||T<0||T>n*D))throw Error("invalid grid or count");
  return T===null?[w*D-m*D,w*D+p*D]:[w*D-Math.min(T,m*D)+Math.max(0,T-(m+r)*D),w*D+Math.min(T,p*D)-Math.max(0,T-(p+r)*D)];
}

function marginalBounds(n,wa,wb,aa,bb,D,T=null){
  if(![n,wa,wb,aa,bb].every(Number.isSafeInteger)||n<1||Math.min(wa,wb,aa,bb)<0||wa+aa>n||wb+bb>n)throw Error("invalid marginal counts");
  const overlap=Math.max(0,aa+bb-n),p=aa-overlap,m=bb-overlap;
  return bounds({n,w:wa-wb,p,m,r:n-p-m},D,T);
}

function words(alphabet,n){let rows=[[]];for(let i=0;i<n;i++)rows=rows.flatMap(r=>alphabet.map(x=>[...r,x]));return rows;}

function tally(a,v){return a.filter(x=>x===v).length;}

function update(map,k,lo,hi){const prev=map.get(k);map.set(k,prev?[Math.min(prev[0],lo),Math.max(prev[1],hi)]:[lo,hi]);}

function assertEq(a,b,where){if(JSON.stringify(a)!==JSON.stringify(b))throw Error(where+" "+JSON.stringify([a,b]));}

function verify(){
  let pairs=0,assignments=0,budgetChecks=0,marginalChecks=0,unconstrainedMarginalChecks=0;
  for(let n=1;n<=4;n++){
    const policies=words(['C','W','S'],n), costs=words([0,1,2],n), marginals=new Map(), unbudgeted=new Map();
    for(const a of policies)for(const b of policies){
      const c=counts(a,b), ext=new Map();let low=Infinity,high=-Infinity;pairs++;
      const key=[tally(a,'W'),tally(b,'W'),c.aa,c.bb];
      for(const z of costs){
        const loss=(p)=>p.reduce((s,x,i)=>s+(x==='W'?2:x==='S'?z[i]:0),0);
        const delta=loss(a)-loss(b),T=z.reduce((s,x)=>s+x,0);assignments++;update(ext,T,delta,delta);low=Math.min(low,delta);high=Math.max(high,delta);
      }
      assertEq(bounds(c,2),[low,high],"unconstrained pair");update(unbudgeted,key.join(","),low,high);
      for(const [T,range] of ext){assertEq(bounds(c,2,T),range,"budget pair");budgetChecks++;update(marginals,[...key,T].join(","),...range);}
    }
    for(const [key,range] of marginals){const [wa,wb,aa,bb,T]=key.split(",").map(Number);assertEq(marginalBounds(n,wa,wb,aa,bb,2,T),range,"budget marginals");marginalChecks++;}
    for(const [key,range] of unbudgeted){const [wa,wb,aa,bb]=key.split(",").map(Number);assertEq(marginalBounds(n,wa,wb,aa,bb,2),range,"unbudgeted marginals");unconstrainedMarginalChecks++;}
  }
  const a=['C','C','S','S','S','S','S','S','S','S'], b=['C','C','C','C','C','C','C','C','W','S'];
  const example=counts(a,b);assertEq(bounds(example,10),[-10,60],"reversed ranking");
  const matched=counts(['C','W','S'],['W','C','S']);assertEq(bounds(matched,10),[0,0],"matched cancellation");
  const same=counts(['C','S'],['S','C']);assertEq(bounds(same,10),[-10,10],"equal marginal opposite pairing");assertEq(bounds(same,10,0),[0,0],"zero fallback");
  let refusals=0;for(const f of [()=>counts([],[]),()=>counts(['X'],['C']),()=>counts(['C'],['C','S']),()=>marginalBounds(2,2,0,1,0,2),()=>bounds(same,2,5)]){try{f()}catch(e){refusals++;}}assertEq(refusals,5,"input refusals");
  return {pairs,assignments,budgetChecks,marginalChecks,unconstrainedMarginalChecks,refusals,example,exampleRangeNumerator:bounds(example,10),matched,disjointSameMarginals:same};
}

if (typeof module !== 'undefined') module.exports={counts,bounds,marginalBounds,verify};
if (typeof require !== 'undefined' && require.main === module) console.log(JSON.stringify(verify(),null,2));
