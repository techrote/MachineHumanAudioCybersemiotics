function validate(p,max=64){if(!Array.isArray(p)||p.length<1||p.length>max||p.some(x=>!Number.isInteger(x)||x<0||x>=p.length)||new Set(p).size!==p.length)throw Error("expected permutation of 0..n-1 within size limit");}

function identity(n){return Array.from({length:n},(_,i)=>i)}

function cycles(p){validate(p);let seen=new Set(),out=[];for(let i=0;i<p.length;i++){if(seen.has(i))continue;let c=[],j=i;while(!seen.has(j)){seen.add(j);c.push(j);j=p[j]}out.push(c)}return out}

function parity(p){return (p.length-cycles(p).length)%2}

function swap(p,i,j){let q=p.slice();[q[i],q[j]]=[q[j],q[i]];return q}

function evenRoute(target){validate(target);if(parity(target))throw Error("odd endpoint: determinant obstruction");let p=identity(target.length),path=[p];while(true){let bad=p.map((x,i)=>x!==target[i]?i:-1).filter(i=>i>=0);if(!bad.length)return path;if(bad.length<3)throw Error("parity invariant");let i=bad[0],j=p.indexOf(target[i]),k=bad.find(x=>x!==i&&x!==j);let q=p.slice();q[i]=p[j];q[k]=p[i];q[j]=p[k];path.push(q);p=q}}

function vacancyRoute(target){validate(target);let n=target.length,goal=[...target,n],p=identity(n+1),path=[p];while(p.some((v,i)=>v!==goal[i])){let i=p.findIndex((v,i)=>v!==goal[i]);p=swap(p,n,i);path.push(p);let v=i;while(v!==n){let j=p.indexOf(goal[v]);p=swap(p,v,j);path.push(p);v=j}}return path}

function vacancyCost(target){return cycles(target).filter(c=>c.length>1).reduce((s,c)=>s+c.length+1,0)}

function directFloor(target){return cycles(target).reduce((s,c)=>Math.min(s,c.length%2===0?0:Math.sin(Math.PI/(2*c.length))),1)}

function matrix(a,b,t,active=a.length){validate(a,65);validate(b,65);if(a.length!==b.length||!Number.isFinite(t)||t<0||t>1||!Number.isInteger(active)||active<1||active>a.length)throw Error("invalid interpolation");return a.map((x,i)=>Array.from({length:active},(_,j)=>(x===j?1-t:0)+(b[i]===j?t:0)))}

function *permutations(p){if(!p.length){yield [];return}for(let i=0;i<p.length;i++)for(let q of permutations(p.filter((_,j)=>i!==j)))yield [p[i],...q]}

function assert(c,m){if(!c)throw Error(m)}

function bfs(n){let a=identity(n+1),key=x=>x.join(","),d=new Map([[key(a),0]]),q=[a];for(let k=0;k<q.length;k++){let p=q[k],v=p.indexOf(n);for(let i=0;i<=n;i++){if(i===v)continue;let b=swap(p,i,v),s=key(b);if(!d.has(s)){d.set(s,d.get(key(p))+1);q.push(b)}}}return d}

function gram(M,i,j){return M.reduce((s,row)=>s+row[i]*row[j],0)}

function verify(maxN=7){if(!Number.isInteger(maxN)||maxN<1||maxN>7)throw Error('verification bound is 1..7');let rows=[];for(let n=1;n<=maxN;n++){let d=bfs(n),r={n,permutations:0,even:0,odd:0,vacancyMoves:0,evenMoves:0,strictEvenImprovement:0,gramChecks:0,bfsStates:d.size,maxVacancyMoves:0};for(let p of permutations(identity(n))){r.permutations++;let path=vacancyRoute(p),end=path.at(-1),moves=path.length-1;assert(end.join(",")===[...p,n].join(","),"vacancy endpoint");assert(moves===vacancyCost(p)&&moves===d.get(end.join(",")),"BFS cost");r.vacancyMoves+=moves;r.maxVacancyMoves=Math.max(r.maxVacancyMoves,moves);for(let k=1;k<path.length;k++){let a=path[k-1],b=path[k],diff=a.map((v,i)=>v!==b[i]?i:-1).filter(i=>i>=0);assert(diff.length===2&&diff.includes(a.indexOf(n))&&diff.includes(b.indexOf(n)),"vacancy step");let M=matrix(a,b,.5,n);for(let i=0;i<n;i++){let g=gram(M,i,i);assert(g===(i===a[b.indexOf(n)]?.5:1),"vacancy diagonal");for(let j=0;j<i;j++)assert(gram(M,i,j)===0,"active support overlap");r.gramChecks++}}
if(parity(p)){r.odd++;let refused=false;try{evenRoute(p)}catch(e){refused=true}assert(refused,"odd refusal")}else{r.even++;let path=evenRoute(p);assert(path.at(-1).join(",")===p.join(","),"even endpoint");r.evenMoves+=path.length-1;if(path.length>1&&directFloor(p)<.5-1e-10)r.strictEvenImprovement++;for(let k=1;k<path.length;k++){let a=path[k-1],b=path[k],diff=a.map((v,i)=>v!==b[i]?i:-1).filter(i=>i>=0);assert(diff.length===3&&parity(b)===0,"three-cycle");let M=matrix(a,b,.5),moved=new Set(diff.map(i=>a[i]));for(let i=0;i<n;i++){assert(gram(M,i,i)===(moved.has(i)?.5:1),"cycle diag");for(let j=0;j<i;j++)assert(gram(M,i,j)===(moved.has(i)&&moved.has(j)?.25:0),"cycle offdiag");r.gramChecks++}}}}
rows.push(r)}return rows}

export {cycles,parity,evenRoute,vacancyRoute,vacancyCost,directFloor,matrix,verify};
