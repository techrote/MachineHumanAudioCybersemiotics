// Original synthetic laboratory; executed functions serialized verbatim from the V8 run.
function assert(ok,msg){if(!ok)throw Error(msg)}

function parameters(t){
  assert(Array.isArray(t)&&t.length===4&&t.every(x=>Number.isSafeInteger(x)&&x>=0),"invalid table");
  const [a,b,c,d]=t,n=a+b+c+d;
  assert(n>=2&&n<=10_000,"unsupported roster size");
  const r0=a+b,r1=c+d,c0=a+c,c1=b+d;
  assert(r0*r1*c0*c1>0,"constant partition");
  const determinant=a*d-b*c;
  const denominator=r0*r1*c0*c1;
  assert(Number.isSafeInteger(denominator)&&Number.isSafeInteger(determinant**2),"unsafe arithmetic");
  return {n,r0,r1,c0,c1,determinant,num:determinant**2,den:denominator,connected:t.filter(x=>x>0).length>=3};
}

function projectScaled(t,x,axis){
  const groups=axis===0?[[0,1],[2,3]]:[[0,2],[1,3]];
  const sizes=groups.map(g=>g.reduce((s,i)=>s+t[i],0));
  assert(sizes.every(v=>v>0),"constant partition");
  const sums=groups.map(g=>g.reduce((s,i)=>s+t[i]*x[i],0));
  const out=[0,0,0,0];
  groups.forEach((g,k)=>g.forEach(i=>out[i]=sums[k]*sizes[1-k]));
  assert(out.every(Number.isSafeInteger),"unsafe projection arithmetic");
  return out;
}

function roundScaled(t,x){return projectScaled(t,projectScaled(t,x,0),1)}

function equalOccupied(t,x,y){return t.every((w,i)=>w===0||x[i]===y[i])}

function bound(n,s=1){
  assert(Number.isSafeInteger(n)&&Number.isSafeInteger(s)&&s>=1&&n-s>=2&&n<=60_000,"invalid bridge count");
  const a=Math.floor((n-s)/2),d=n-s-a;
  return {num:a*d,den:(a+s)*(d+s),witness:[a,s,0,d]};
}

function verifyTable(t,p,full){
  const {n,c0,c1,num,den,connected}=p;
  const x=[-c1,c0,-c1,c0],y=roundScaled(t,x);
  assert(equalOccupied(t,y,x.map(v=>v*num)),"direct contrast recurrence");
  assert(connected===(num<den),"connectivity mismatch");
  if(!full)return;
  const rowDen=p.r0*p.r1,pr=projectScaled(t,x,0);
  const diff=x.map((v,i)=>v*rowDen-pr[i]);
  const sq=v=>t.reduce((sum,w,i)=>sum+w*v[i]**2,0);
  const left=den*sq(diff),right=(den-num)*rowDen**2*sq(x);
  assert(Number.isSafeInteger(left)&&Number.isSafeInteger(right)&&left===right,"half-step movement identity");
  assert(equalOccupied(t,roundScaled(t,diff),[0,0,0,0]),"one-pass erasure witness");
  if(num>0&&num<den){
    const rev=projectScaled(t,projectScaled(t,diff,1),0);
    assert(!equalOccupied(t,rev,[0,0,0,0]),"reverse-order preservation witness");
  }
  for(let i=0;i<4;i++){
    if(!t[i])continue;
    const e=[0,0,0,0];e[i]=1;
    const z=roundScaled(t,e),zz=roundScaled(t,z);
    assert(t.every((w,j)=>!w||n*zz[j]-t[i]*den**2===num*(n*z[j]-t[i]*den)),"general two-round recurrence");
    const reverse=projectScaled(t,projectScaled(t,e,1),0);
    const same=equalOccupied(t,z,reverse);
    if(num===0||num===den)assert(same,"commuting control");
  }
  if(num>0&&num<den){
    const reverse=projectScaled(t,projectScaled(t,x,1),0);
    assert(!equalOccupied(t,y,reverse),"noncommutation witness");
  }
}

function census(maxN=60){
  assert(Number.isInteger(maxN)&&maxN>=3&&maxN<=60,"bounded exact census");
  const totals={tables:0,constantExcluded:0,connected:0,disconnected:0,orthogonal:0,extremal:0,contrastChecks:0,fullTables:0,bridgeBoundChecks:0};
  const rows=[];
  for(let n=2;n<=maxN;n++){
    const row={n,tables:0,constantExcluded:0,connected:0,disconnected:0,orthogonal:0,extremal:0,contrastChecks:0,fullTables:0,bridgeBoundChecks:0};
    const g=n>=3?bound(n):null;
    for(let a=0;a<=n;a++)for(let b=0;b<=n-a;b++)for(let c=0;c<=n-a-b;c++){
      const d=n-a-b-c,t=[a,b,c,d];row.tables++;
      if(!(a+b&&c+d&&a+c&&b+d)){row.constantExcluded++;continue}
      const p=parameters(t);
      verifyTable(t,p,n<=30);row.contrastChecks++;if(n<=30)row.fullTables++;
      if(!p.connected){row.disconnected++;continue}
      row.connected++;
      if(!p.num)row.orthogonal++;
      assert(p.num*g.den<=g.num*p.den,"global sharp bound");
      if(p.num*g.den===g.num*p.den)row.extremal++;
      const s=p.determinant>=0?b+c:a+d;
      const h=bound(n,s);
      assert(p.num*h.den<=h.num*p.den,"bridge-specific sharp bound");
      row.bridgeBoundChecks++;
    }
    if(g){
      const p=parameters(g.witness);
      assert(p.connected&&p.num*g.den===g.num*p.den&&row.extremal>0,"missing global witness");
      for(let s=1;s<=n-2;s++){
        const h=bound(n,s),q=parameters(h.witness);
        assert(q.connected&&q.num*h.den===h.num*q.den,"missing bridge witness");
      }
    }
    for(const key of Object.keys(totals))totals[key]+=row[key];
    rows.push(row);
  }
  return {maxN,totals,rows};
}

function makeWav(num,den,rounds=32){
  assert(Number.isSafeInteger(num)&&Number.isSafeInteger(den)&&num>=0&&den>0&&num<=den,"invalid rate");
  assert(Number.isInteger(rounds)&&rounds>0&&rounds<=256,"invalid rounds");
  const rate=8000,frames=400,bytes=new Uint8Array(44+rounds*frames*4),v=new DataView(bytes.buffer);
  const str=(off,s)=>{for(let i=0;i<s.length;i++)v.setUint8(off+i,s.charCodeAt(i))};
  str(0,"RIFF");v.setUint32(4,bytes.length-8,true);str(8,"WAVE");str(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,2,true);v.setUint32(24,rate,true);v.setUint32(28,rate*4,true);v.setUint16(32,4,true);v.setUint16(34,16,true);str(36,"data");v.setUint32(40,bytes.length-44,true);
  const a=BigInt(num),b=BigInt(den);let p=1n,q=1n;
  for(let k=0;k<rounds;k++){
    const move=Number(12000n*p*(b-a)/(q*b));
    const residual=Number(12000n*p*a/(q*b));
    for(let j=0;j<frames;j++){
      const phase=j%20,tri=phase<10?2*phase-10:30-2*phase;
      const fade=Math.min(20,j,frames-1-j);
      const off=44+(k*frames+j)*4;
      v.setInt16(off,Math.trunc(move*tri*fade/200),true);
      v.setInt16(off+2,Math.trunc(residual*tri*fade/200),true);
    }
    p*=a;q*=b;
  }
  return bytes;
}

function hash(bytes){let h=2166136261;for(const b of bytes)h=Math.imul(h^b,16777619)>>>0;return h.toString(16).padStart(8,"0")}

function audioCases(){
  const cases={orthogonal:[0,1],oneBridge101:[2500,2601],disconnected:[1,1],constant:[0,1]};
  // A constant input has zero movement AND zero disagreement; silence both channels.
  const silent=makeWav(1,1);silent.fill(0,44);
  const waves={};
  for(const [name,[num,den]] of Object.entries(cases))waves[name]=name==="constant"?silent:makeWav(num,den);
  for(const w of Object.values(waves)){
    assert(w.length===51244&&new DataView(w.buffer).getUint32(40,true)===51200,"WAV header");
  }
  const leftZero=w=>{const v=new DataView(w.buffer);for(let i=44;i<w.length;i+=4)if(v.getInt16(i,true)!==0)return false;return true};
  const rightZero=w=>{const v=new DataView(w.buffer);for(let i=46;i<w.length;i+=4)if(v.getInt16(i,true)!==0)return false;return true};
  assert(leftZero(waves.disconnected)&&leftZero(waves.constant)&&!rightZero(waves.disconnected)&&rightZero(waves.constant),"silence ambiguity");
  assert(!leftZero(waves.oneBridge101)&&!rightZero(waves.oneBridge101),"connected audio witness");
  assert(rightZero(waves.orthogonal)&&!leftZero(waves.orthogonal),"one-round control");
  return waves;
}

function run(){
  const data=census();
  const audio=audioCases();
  const bad=[[-1,1,1,1],[1,1,0,0],[1.5,1,1,1],[0,0,0,0]];
  let rejected=0;
  for(const t of bad){try{parameters(t)}catch(e){rejected++}}
  assert(rejected===bad.length,"invalid table acceptance");
  return {...data,invalidTablesRejected:rejected,audio:Object.fromEntries(Object.entries(audio).map(([k,v])=>[k,{bytes:v.length,fnv1a:hash(v)}]))};
}

export { parameters, bound, census, makeWav, audioCases, run };
