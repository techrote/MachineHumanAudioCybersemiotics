// Exact integer synthetic tests. Run node lab.js; no dependencies.
"use strict";
function check(ok,msg){if(!ok)throw Error(msg);}
function range(n){return Array.from({length:n},(_,i)=>i);}
function pop(x){let c=0;for(;x;x&=x-1)c++;return c;}
function bfs(g,u){const d=g.map(()=>-1),q=[u];d[u]=0;for(let i=0;i<q.length;i++)for(const v of g[q[i]])if(d[v]<0){d[v]=d[q[i]]+1;q.push(v);}return d;}
function graph(n,edges){const g=range(n).map(()=>[]);for(const [u,v] of edges){g[u].push(v);g[v].push(u);}return g;}
function witness(g,u,v,D,h){
  const d=bfs(g,u),L=d[v],l=Math.floor(L/2);
  check(L>0&&d.every(x=>x>=0)&&g.every((ns,i)=>ns.every(j=>Math.abs(d[i]-d[j])===1)),"connected bipartite input");
  // To saturate beyond the threshold, rescale the denominator so step 1/l is exact.
  if(l===0)h=0;
  else if(l*h>D){D=l;h=1;}
  const M=2*D+h,full=(1<<M)-1;
  const E=i=>((1<<D)-1)<<(i*h);
  const O=i=>full^(E(i)|E(i+1));
  const t=l*h;
  const lastOdd=L%2?((1<<t)-1)|(((1<<(D-t))-1)<<(D+t)):O(l-1);
  const rows=d.map(a=>a>=2*l?(a%2?lastOdd:E(l)):(a%2?O((a-1)/2):E(a/2)));
  return {rows,D,h,M};
}
function edgesOf(g){return g.flatMap((ns,i)=>ns.filter(j=>j>i).map(j=>[i,j]));}
let counts={graphs:0,witnesses:0,decoderCells:0,oracleTransitions:0,oracleDistances:0,lobeControls:0,signatureControls:0};
function verify(g,w){
  const {rows,D,M}=w;
  check(rows.every(x=>pop(x)===D),"row normalization");
  check(pop(rows.reduce((a,b)=>a|b,0))===M,"exact vulnerability");
  // Actual action collapses second endpoint onto first, otherwise identity.
  for(const [u,v] of edgesOf(g)){
    const seen=new Map();
    for(let x=0;x<g.length;x++)for(let j=0;j<M;j++)if(rows[x]&(1<<j)){
      const key=(x===v?u:x)*M+j;
      check(!seen.has(key)||seen.get(key)===x,"decoder collision");
      seen.set(key,x);counts.decoderCells++;
    }
  }
}
function run(){
  // Independent path oracle: enumerate all D-subsets of a (2D+h)-set.
  // Reachability only uses disjointness; no interval witness or bound in recurrence.
  for(let D=1;D<=4;D++)for(let h=0;h<=D;h++){
    const M=2*D+h,sets=range(1<<M).filter(x=>pop(x)===D);
    const adj=sets.map(x=>sets.map((y,j)=>[y,j]).filter(([y])=>!(x&y)).map(([,j])=>j));
    let reach=new Set([0]);
    for(let L=1;L<=10;L++){
      const next=new Set();for(const i of reach)for(const j of adj[i]){next.add(j);counts.oracleTransitions++;}
      reach=next;const tv=[...reach].map(i=>D-pop(sets[0]&sets[i]));
      const cap=Math.min(D,Math.floor(L/2)*h);
      check(Math.min(...tv)===(L%2?D-cap:0),"oracle minimum TV");
      check(Math.max(...tv)===(L%2?D:cap),"oracle maximum TV");
      counts.oracleDistances++;
    }
  }
  for(let n=2;n<=5;n++){
    const all=range(n).flatMap(i=>range(n).filter(j=>j>i).map(j=>[i,j]));
    for(let m=0;m<1<<all.length;m++){
      const g=graph(n,all.filter((_,j)=>m&(1<<j))),d=bfs(g,0);
      if(d.some(x=>x<0)||g.some((ns,i)=>ns.some(j=>Math.abs(d[i]-d[j])!==1)))continue;
      counts.graphs++;
      for(let u=0;u<n;u++)for(let v=u+1;v<n;v++)for(let D=1;D<=4;D++)for(let h=0;h<=D;h++){
        const L=bfs(g,u)[v],w=witness(g,u,v,D,h);verify(g,w);
        const actual=w.D-pop(w.rows[u]&w.rows[v]),cap=Math.min(D,Math.floor(L/2)*h);
        check(actual*D===(L%2?D-cap:cap)*w.D,"witness endpoint");
        check(w.h*D<=h*w.D,"budget");
        // Check reference-edge classifier error for every vertex.
        const a=0,b=g[a][0],da=bfs(g,a),db=bfs(g,b);
        for(let x=0;x<n;x++){
          const err=da[x]%2?pop(w.rows[x]&w.rows[a]):w.D-pop(w.rows[x]&w.rows[a]);
          const dist=da[x]%2?db[x]:da[x];
          check(err<=Math.min(w.D,dist/2*w.h),"anchor certificate");counts.signatureControls++;
        }
        counts.witnesses++;
      }
    }
  }
  // Opposite endpoints identical; attach equal numbers of leaves to each.
  // Balanced parity becomes nearly unguessable even as normalized slack shrinks.
  for(let l=1;l<=10;l++)for(const K of [0,1,10,50,200]){
    const L=2*l+1,n=L+1+2*K;
    const es=range(L).map(i=>[i,i+1]);
    for(let j=0;j<K;j++){es.push([0,L+1+j],[L,L+1+K+j]);}
    const g=graph(n,es),w=witness(g,0,L,l,1);
    // BFS witness on the left leaves is the first odd set, not the same as
    // final right leaves. Replace both by a common disjoint support.
    const complement=((1<<w.M)-1)^w.rows[0];
    let leaf=0;for(let j=0;j<w.M&&pop(leaf)<l;j++)if(complement&(1<<j))leaf|=1<<j;
    for(let j=L+1;j<n;j++)w.rows[j]=leaf;
    check(w.rows[0]===w.rows[L],"identical endpoints");verify(g,w);
    const d=bfs(g,0),p=range(w.M).map(j=>[0,1].map(k=>w.rows.reduce((s,x,i)=>s+((d[i]%2===k&&(x&(1<<j)))?1:0),0)));
    const guess=p.reduce((s,x)=>s+Math.max(...x),0);
    check(2*guess>=n*l&&2*guess<=(n+2*l)*l,"parity bound");counts.lobeControls++;
  }
  // Triangle shortcut violates bipartiteness; an opposite-end shortcut
  // preserves it and directly forbids the previously equal endpoint rows.
  const g=graph(4,[[0,1],[1,2],[2,3]]),w=witness(g,0,3,1,1);
  check(w.rows[0]===w.rows[3],"path alias");
  check(Boolean(w.rows[0]&w.rows[3]),"new edge invalidates alias");
  return counts;
}
console.log(JSON.stringify(run()));
