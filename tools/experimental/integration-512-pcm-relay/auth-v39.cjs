'use strict';
// Refs #512; experimental authenticated outcome/return adapter. Synthetic keys only.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const R=require('./role-v29.cjs'),O=require('./outcome-v34.cjs'),V=require('./paired-v38.cjs'),S=require('./semantic-v33.cjs'),E=require('./epoch-v26.cjs'),C=require('./sequence-v22.cjs'),{frame,wav}=require('./relay.cjs');
const BASE=R.STEP,BLOCK=C.FRAME+128,STEP=BASE+3*BLOCK,RATE=16000;
const labels=['applied','buffered','superseded','same-version','version-conflict','dependency-conflict','same-operation','blocked'];
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
// Fixed session and direction-specific 256-bit keys are provisioned locally, NOT recovered from PCM.
const fixture=(session=1,keyset=1)=>({session:Buffer.alloc(16,session),outcome:Buffer.alloc(32,keyset),confirm:Buffer.alloc(32,keyset+1)});
function mac(ctx,role,p,g,e,s,v,n){const nonce=Buffer.alloc(4);nonce.writeUInt32BE(n);return crypto.createHmac('sha256',ctx[role]).update('MHAC-auth-v39\0'+role+'\0').update(ctx.session).update(Buffer.from([...frame(p),g,e,labels.indexOf(s)+1,v])).update(nonce).digest().subarray(0,8);}
function encode(ctx,role,p,g,e,s,v,n,phase){const x=new Int16Array(STEP);x.set((role==='outcome'?O:V).encode(p,g,e,s,v,phase));const b=Buffer.alloc(12);b.writeUInt32BE(n);mac(ctx,role,p,g,e,s,v,n).copy(b,4);const digits=[...b].flatMap(v=>[1+(v>>4),1+(v&15)]);for(let i=0;i<3;i++)x.set(C.render(p,phase,()=>C.protect(digits.slice(8*i,8*i+8))),BASE+i*BLOCK+64);return x;}
function acquire(ctx,role,x,chunk=511){if(!(x instanceof Int16Array)||x.length!==STEP)throw Error('slot');const a=(role==='outcome'?O:V).acquire(x.subarray(0,BASE),chunk);if(a.status!=='receipt-candidate')return {status:'refused',reason:'base'};const digits=[];for(let i=0;i<3;i++){const d=C.acquire(x.subarray(BASE+i*BLOCK,BASE+(i+1)*BLOCK));if(d.status!=='ok'||Math.abs(d.start-64)>16||d.token.some(x=>x<1||x>16))return {status:'refused',reason:'extension'};digits.push(...d.token.map(x=>x-1));}const b=Buffer.from(Array.from({length:12},(_,i)=>16*digits[2*i]+digits[2*i+1])),n=b.readUInt32BE(0),s=role==='outcome'?a.outcome:a.delivery;if(!crypto.timingSafeEqual(b.subarray(4),mac(ctx,role,a.packet,a.generation,a.epoch,s,a.revision,n)))return {status:'refused',reason:'mac'};return {...a,challenge:n,authenticated:true};}
const packet=(seq,value)=>({kind:0,source:1,version:1,actor:9,event:7,seq,tree:['verify',[value]]}),A=packet(1,'open'),B=packet(2,'stopped'),Q={...B,kind:1};
const cases=['clean','lost-update-forged-confirm','lost-confirm','old-challenge','old-session','wrong-key','cross-role','authenticated-lie'];
function run(dir,name,mode,seed,ck){S.provision(dir,'typed');const r=S.receiver(dir),ctx=fixture(),auth=mode==='auth',phase=seed*.013,segments=[],trace=[];let belief=null,confirmed=false,expected=2,attempts=0,actual='buffered',knownChallenge=null;
function add(role,x,note){let a;if(role==='data')a=R.acquire(x.subarray(0,BASE));else a=auth?acquire(ctx,role,x): (role==='outcome'?O:V).acquire(x.subarray(0,BASE));segments.push(x);trace.push({role,note,decoded:a,actual,belief,confirmed});return a;}
function pad(x){const y=new Int16Array(STEP);y.set(x);return y;}
function data(p,g){const a=add('data',pad(R.encode(p,g,0,0,phase)),'original data');const d=r.receive(a);ck(d.ack,'data receipt');actual=r.snapshot().semantic.status['1:1'];}
function wire(role,s,v,n,context=ctx){return auth?encode(context,role,Q,1,0,s,v,n,phase):pad((role==='outcome'?O:V).encode(Q,1,0,s,v,phase));}
function outcome(x,note){const a=add('outcome',x,note);belief=O.observe(belief,a,B,1,'outcome');if(a.status==='receipt-candidate'&&belief&&!belief.conflict&&belief.outcome===a.outcome&&belief.revision===a.revision)knownChallenge=auth?a.challenge:0;return a;}
function confirm(x,note){const a=add('confirm',x,note);if(!confirmed&&E.matches(a,B,1,0)&&a.delivery==='applied'&&a.revision===2&&(!auth||a.challenge===expected))confirmed=true;return a;}
data(B,1);outcome(wire('outcome','buffered',1,1),'buffered');
if(name==='authenticated-lie'){outcome(wire('outcome','applied',2,2),'authorized endpoint lies before dependency');ck(belief?.outcome==='applied'&&actual==='buffered','authentication not truth');}
data(A,0);ck(actual==='applied','dependency applied');attempts++;
const lost=name==='lost-update-forged-confirm';outcome(lost?new Int16Array(STEP):wire('outcome','applied',2,expected),lost?'lost outcome':'genuine outcome');
if(name==='lost-update-forged-confirm')confirm(wire('confirm','applied',2,expected,fixture(1,9)),'unauthorized confirmation');
else if(name==='old-challenge')confirm(wire('confirm','applied',2,1),'old challenge');
else if(name==='old-session')confirm(wire('confirm','applied',2,expected,fixture(2)),'old session');
else if(name==='wrong-key')confirm(wire('confirm','applied',2,expected,fixture(1,9)),'wrong key');
else if(name==='cross-role'){const x=wire('confirm','applied',2,expected);if(auth)x.set(wire('outcome','applied',2,expected).subarray(BASE),BASE);else x.set(wire('outcome','applied',2,expected));confirm(x,'outcome substituted for confirmation');}
else if(name==='lost-confirm')confirm(new Int16Array(STEP),'lost confirmation');
else confirm(wire('confirm','applied',2,knownChallenge),'genuine confirmation');
const premature=confirmed&&belief?.outcome!=='applied',firstConfirmed=confirmed;
if(!confirmed){attempts++;outcome(wire('outcome','applied',2,expected),'bounded repair');confirm(wire('confirm','applied',2,knownChallenge),'genuine return');}
ck(confirmed,'final confirmation');ck(attempts<=2,'attempt bound');ck(JSON.stringify(S.receiver(dir).snapshot())===JSON.stringify(r.snapshot()),'persistent world reopen');
ck(premature===(name==='lost-update-forged-confirm'&&!auth),'false delivery witness');if(auth&&['lost-update-forged-confirm','old-challenge','old-session','wrong-key','cross-role'].includes(name))ck(!firstConfirmed,'strict refusal');
const pcm=new Int16Array(segments.length*STEP);segments.forEach((x,i)=>pcm.set(x,i*STEP));return {pcm,trace,actual,belief,confirmed,premature,firstConfirmed,attempts,slots:segments.length};}
function main(out){fs.mkdirSync(out,{recursive:true});const root=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-v39-'));let checks=0,rescans=0;const rows=[],ck=(x,m)=>{checks++;assert.ok(x,m);};try{for(const seed of (process.env.SEED?[Number(process.env.SEED)]:[71,113]))for(const name of cases)for(const mode of ['public','auth']){const {pcm,...r}=run(path.join(root,[seed,name,mode].join('-')),name,mode,seed,ck),file=[seed,name,mode].join('-')+'.wav',raw=wav(pcm);fs.writeFileSync(path.join(out,file),raw);const bytes=fs.readFileSync(path.join(out,file));for(const [i,t] of r.trace.entries()){const x=Int16Array.from({length:STEP},(_,n)=>bytes.readInt16LE(44+2*(i*STEP+n)));const a=t.role==='data'?R.acquire(x.subarray(0,BASE),true,127):mode==='auth'?acquire(fixture(),t.role,x,127):(t.role==='outcome'?O:V).acquire(x.subarray(0,BASE),127);assert.deepEqual(a,t.decoded);rescans++;}rows.push({seed,name,mode,file,sha256:hash(bytes),...r});}fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify({schema:'mhac-auth-v39',parent:'baa1bcf076da6d1dab6ef82c53a91cff67f239f7',rate:RATE,base:BASE,step:STEP,checks,rescans,rows},null,2)+'\n');console.log({checks,rescans,sessions:rows.length});}finally{fs.rmSync(root,{recursive:true,force:true});}}
module.exports={encode,acquire,fixture,mac,STEP,BASE};if(require.main===module)main(process.argv[2]||'auth-v39-output');
