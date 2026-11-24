function checkGrid(){
  const mod=(x,q)=>((x%q)+q)%q;
  function least(q){for(let p=2;p<=q;p++)if(q%p===0)return p}
  let cases=0,directions=0;
  const examples=[];
  for(let n=2;n<=8;n++)for(let q=2;q<=36;q++){
    let agree=0;
    for(let a=0;a<q;a++)for(let b=0;b<q;b++){
      if(!a&&!b)continue;
      const counts=new Uint16Array(q);
      for(let x=0;x<n;x++)for(let y=0;y<n;y++)counts[mod(a*x+b*y,q)]++;
      agree=Math.max(agree,...counts);directions++;
    }
    const predicted=n*Math.ceil(n/least(q));
    if(agree!==predicted)throw Error("finite alphabet mismatch");
    if(n===4&&[2,3,5,7,11,12].includes(q))examples.push({q,distance:n*n-agree});
    cases++;
  }
  return {cases,directions,examples,assertion_failures:0};
}
console.log(JSON.stringify(checkGrid(),null,2));
