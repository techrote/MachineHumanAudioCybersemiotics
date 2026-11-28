'use strict';
// Refs #512. v74 sender-local dependency-aware arbitration; v73 retained unchanged.
const fs=require('node:fs'),path=require('node:path'),P=require('./session-playground-v72.cjs');
const S=require('./semantic-v33.cjs');
const DATA=77440,QUERY=169216,CAP=8,MAX=16000000;
const file=d=>path.join(d,'airtime.json');
function load(d){const s=JSON.parse(fs.readFileSync(file(d)));if(s.schema!==74)throw Error('schema');return s;}
function save(d,s){const tmp=file(d)+'.stage';const fd=fs.openSync(tmp,'w');try{fs.writeFileSync(fd,JSON.stringify(s,null,2)+'\n');fs.fsyncSync(fd);}finally{fs.closeSync(fd);}fs.renameSync(tmp,file(d));}
function init(d,policy,budget,world='typed'){if(!['fifo','priority','dependency'].includes(policy)||!Number.isSafeInteger(budget)||budget<0||budget>MAX)throw Error('budget/policy');P.init(d,world);const s={schema:74,policy,budget,spent:0,next:1,jobs:[],pending:null};save(d,s);return s;}
function enqueue(d,id,action,priority,plan){const s=load(d);if(s.pending)throw Error('recover pending reservation');if(s.jobs.length>=CAP||!['data','query'].includes(action)||!Number.isInteger(priority)||priority<0||priority>3||!Array.isArray(plan)||plan.length<1||plan.length>(action==='data'?1:3)||plan.some(p=>!Array.isArray(p)||p.length!==2||!['clean','erase','gap','delay96','delay160'].includes(p[0])||!['clean','erase','gap'].includes(p[1])))throw Error('job');if(!P.endpoints(d).j.snapshot().offers.some(o=>`${o.p.source}:${o.g}`===id))throw Error('offer');const j={n:s.next++,id,action,priority,plan,cursor:0,status:'queued',attempts:[]};s.jobs.push(j);save(d,s);return j;}
// Only sender-local registered packets and pending jobs inform arbitration. No reporter state or delivery-success oracle.
// Promote a queued earlier ordered DATA to the priority of its highest-priority queued dependent.
// This is a dispatch preference, not a proof of receipt or an execution gate.
function select(s,requester){
 const full=requester.delivery.length>=2;
 const q=s.jobs.filter(j=>j.status==='queued'&&!(full&&j.action==='query')&&s.budget-s.spent>=(j.action==='data'?DATA:QUERY));
 const offered=new Map(requester.offers.map(o=>[`${o.p.source}:${o.g}`,o.p]));
 const ordered=j=>{const p=offered.get(j.id);return j.action==='data'&&p&&S.contract(p)?.type==='ordered'?p:null;};
 const earlier=(a,b)=>{const x=ordered(a),y=ordered(b);return !!(x&&y&&x.source===y.source&&x.actor===y.actor&&x.version===y.version&&x.seq<y.seq);};
 const rank=j=>s.policy==='fifo'?0:s.policy==='priority'?j.priority:Math.max(j.priority,...q.filter(k=>earlier(j,k)).map(k=>k.priority));
 // Deterministic topological tie-break: choose only candidates without an earlier equal-rank predecessor.
 const best=Math.max(-1,...q.map(rank));
 const top=q.filter(j=>rank(j)===best);
 const ready=s.policy==='dependency'?top.filter(j=>!top.some(k=>earlier(k,j))):top;
 return ready.sort((a,b)=>a.n-b.n)[0];
}
function finish(d,s,j,result,cost,status){const p=s.pending;s.spent-=p.reserved-cost;j.attempts.push({index:j.cursor,charged:cost,status,trace:result});j.cursor++;j.status=status==='evidence-consumed'||j.action==='data'||j.cursor===j.plan.length?status:'queued';s.pending=null;save(d,s);return {decision:status,job:j.n,charged:cost,remaining:s.budget-s.spent};}
function step(d,cut=false){const s=load(d);if(s.pending)throw Error('recover pending reservation');const requester=P.endpoints(d).j.snapshot(),j=select(s,requester);if(!j)return {decision:'no-eligible-job',remaining:s.budget-s.spent};const reserved=j.action==='data'?DATA:QUERY,out=`job-${j.n}-attempt-${j.cursor+1}`;s.spent+=reserved;s.pending={n:j.n,reserved,out};save(d,s);if(cut===true)process.exit(73);const r=P.run(d,j.id,j.action,[j.plan[j.cursor]],path.join(d,out));if(cut==='after')process.exit(74);if(!Number.isSafeInteger(r.wireSamples)||r.wireSamples<0||r.wireSamples>reserved)throw Error('reservation exceeded');return finish(d,s,j,out+'/trace.json',r.wireSamples,r.stop);}
// An ambiguous interrupted attempt consumes its full reservation. Never infer an effect or replay DATA.
function recover(d){const s=load(d);if(!s.pending)return {decision:'nothing-pending'};const j=s.jobs.find(j=>j.n===s.pending.n);return finish(d,s,j,null,s.pending.reserved,'interrupted-unknown');}
function cli([op,d,...a]){if(!d)throw Error('directory required');if(op==='init')return init(d,a[0],Number(a[1]),a[2]);if(op==='enqueue')return enqueue(d,a[0],a[1],Number(a[2]),a[3].split(',').map(x=>x.split(':')));if(op==='step')return step(d);if(op==='recover')return recover(d);if(op==='show')return load(d);if(['register','peek','ack','endpoints'].includes(op))return P.cli([op==='endpoints'?'show':op,d,...a]);throw Error('init|register|enqueue|step|recover|show|endpoints|peek|ack');}
module.exports={init,enqueue,step,recover,load,select,DATA,QUERY,CAP};if(require.main===module){try{console.log(JSON.stringify(cli(process.argv.slice(2)),null,2));}catch(e){console.error(e.message);process.exitCode=1;}}
