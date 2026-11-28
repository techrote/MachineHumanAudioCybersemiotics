'use strict';
// Refs #512; local synthetic experiment only. No new transport or scheduling policy.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const A=require('./airtime-v74.cjs'),P=require('./session-playground-v72.cjs');
const HTML=path.join(__dirname,'live-v75.html');
function create(dir,port=0){
 dir=path.resolve(dir);const token=crypto.randomBytes(24).toString('hex');
 const lock=dir+'.live75.lock';const fd=fs.openSync(lock,'wx');fs.closeSync(fd);
 let active=false;
 const state=()=>{if(!fs.existsSync(dir))return {initialized:false};const scheduler=A.load(dir),endpoints=P.cli(['show',dir]),recordings=[];
 for(const j of scheduler.jobs)for(const a of j.attempts)if(a.trace){const trace=JSON.parse(fs.readFileSync(path.join(dir,a.trace)));for(const t of trace.attempts)for(const [direction,w] of [['forward',t.forward],['return',t.return]])if(w){recordings.push({job:j.n,attempt:a.index+1,direction,...w,relative:path.join(path.dirname(a.trace),w.file)});}}
 return {initialized:true,scheduler,endpoints,recordings};};
 function action(b){const {op}=b;switch(op){case 'init':return A.init(dir,b.policy,b.budget,b.world);case 'register':return P.cli(['register',dir,b.type,String(b.seq),b.value,String(b.source),String(b.generation)]);case 'enqueue':return A.enqueue(dir,b.id,b.action,b.priority,b.plan);case 'step':return A.step(dir);case 'recover':return A.recover(dir);case 'ack':return P.cli(['ack',dir,b.token]);default:throw Error('unknown operation');}}
 const server=http.createServer(async(req,res)=>{const send=(code,obj)=>{res.writeHead(code,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(obj));};
 try{const host=`127.0.0.1:${server.address().port}`;if(req.headers.host!==host)return send(403,{error:'loopback host required'});
 const url=new URL(req.url,'http://'+host);if(req.method==='GET'&&url.pathname==='/'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Content-Security-Policy':"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:; img-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'",'X-Content-Type-Options':'nosniff'});return res.end(fs.readFileSync(HTML,'utf8').replace('__TOKEN__',token));}
 if(req.headers['x-mhac-token']!==token)return send(403,{error:'session token required'});
 if(req.method==='GET'&&url.pathname==='/state')return send(200,state());
 if(req.method==='GET'&&/^\/audio\/\d+$/.test(url.pathname)){const w=state().recordings?.[Number(url.pathname.split('/')[2])];if(!w)return send(404,{error:'recording unavailable'});const bytes=fs.readFileSync(path.join(dir,w.relative));res.writeHead(200,{'Content-Type':'audio/wav','Content-Length':bytes.length,'Cache-Control':'no-store'});return res.end(bytes);}
 if(req.method!=='POST'||url.pathname!=='/action')return send(404,{error:'route'});
 if(req.headers.origin!==`http://${host}`||req.headers['content-type']!=='application/json')return send(403,{error:'same-origin JSON required'});
 if(active)return send(409,{error:'command in progress'});active=true;try{let chunks=[],size=0;for await(const c of req){size+=c.length;if(size>8192){return send(413,{error:'request too large'});}chunks.push(c);}const b=JSON.parse(Buffer.concat(chunks));if(!b||typeof b!=='object'||Array.isArray(b))throw Error('object required');const result=action(b);return send(200,{result,state:state()});}finally{active=false;}
 }catch(e){if(!res.headersSent)send(400,{error:e.message});else res.destroy();}});
 server.once('close',()=>{fs.unlinkSync(lock);});server.once('error',()=>{if(fs.existsSync(lock))fs.unlinkSync(lock);});
 server.listen(port,'127.0.0.1');return server;
}
module.exports={create};if(require.main===module){try{const dir=process.argv[2]||'live-session75',port=Number(process.argv[3]||8765);const s=create(dir,port);s.on('listening',()=>console.log(`http://127.0.0.1:${s.address().port}/`));for(const sig of ['SIGINT','SIGTERM'])process.on(sig,()=>s.close(()=>process.exit(0)));}catch(e){console.error(e.message);process.exitCode=1;}}
