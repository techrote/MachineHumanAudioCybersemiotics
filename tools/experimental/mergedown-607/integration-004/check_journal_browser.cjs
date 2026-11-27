'use strict';
// Refs #607/#798. Offline file navigation only; no playback or sandbox bypass.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {createHash}=require('node:crypto'),{spawn}=require('node:child_process'),{pathToFileURL}=require('node:url');
const root=path.resolve(process.argv[2]||'.'), keys=['seed71/receipt.json','seed113/receipt.json','receipt.json','process-cut-receipt.json'];
const read=k=>fs.readFileSync(path.join(root,k)), sha=b=>createHash('sha256').update(b).digest('hex');
const groups=keys.map(k=>{const x=JSON.parse(read(k));return x.rows||x.results});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn, label='condition', timeout=12000){const end=Date.now()+timeout;do{const v=await fn();if(v)return v;await sleep(150)}while(Date.now()<end);throw Error(label+' readiness timeout after '+timeout+' ms')}
function staticCheck(){
 const html=read('index.html').toString('utf8'), payload=JSON.parse(html.match(/<script id="payload" type="application\/json">([^]*?)<\/script>/)[1]);
 assert.deepEqual(payload.map(d=>d.path),keys);
 for(const d of payload){assert.deepEqual(Buffer.from(d.base64,'base64'),read(d.path));assert.deepEqual(d.parsed,JSON.parse(read(d.path)))}
 assert.deepEqual(groups.map(g=>g.length),[14,14,20,8]);assert.equal(groups.flat().reduce((n,r)=>n+(r.trace?.length||0),0),96);
 return {status:'PASS',static_exports:4,groups:groups.map(g=>g.length),trace_events:96,browser:'NOT_RUN'};
}
async function browser(exe){
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac004-profile-')), downloads=fs.mkdtempSync(path.join(os.tmpdir(),'mhac004-exports-'));
 const chrome=spawn(exe,['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{stdio:['ignore','ignore','pipe']});
 let stderr='',launchError,ws,stage='launch-port',portReadError='',endpointError='',port=null;const errors=[];const started=Date.now();
 chrome.on('error',e=>launchError=e);chrome.stderr.on('data',b=>stderr=(stderr+b).slice(-4000));
 try{
  port=await until(()=>{if(launchError)throw launchError;if(chrome.exitCode!==null||chrome.signalCode!==null)throw Error('Chrome exit '+chrome.exitCode+' signal '+chrome.signalCode);try{const raw=fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').split('\n')[0].trim();if(!/^\d+$/.test(raw)||Number(raw)<1||Number(raw)>65535){portReadError='invalid or incomplete port file';return null}return Number(raw)}catch(e){portReadError=e.code||String(e);return null}},'DevTools port file',60000);
  const get=async p=>(await fetch(`http://127.0.0.1:${port}${p}`,{signal:AbortSignal.timeout(3000)})).json();
  stage='launch-target';const page=await until(async()=>{try{const target=(await get('/json/list')).find(x=>x.type==='page'&&x.webSocketDebuggerUrl);if(!target)endpointError='no page target';return target}catch(e){endpointError=String(e);return null}},'DevTools page target',30000);
  stage='launch-websocket';
  ws=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('CDP open timeout')),5000);ws.addEventListener('open',()=>{clearTimeout(t);resolve()},{once:true});ws.addEventListener('error',()=>{clearTimeout(t);reject(Error('CDP open error'))},{once:true})});
  let seq=0;const pending=new Map();
  ws.addEventListener('message',ev=>{const x=JSON.parse(ev.data);if(x.id){const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}}else if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text)});
  const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},10000);pending.set(id,{resolve,reject,t});ws.send(JSON.stringify({id,method,params}))});
  const js=async (expression,userGesture=false)=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
  stage='navigate';await call('Runtime.enable');await call('Page.enable');const url=pathToFileURL(path.join(root,'index.html')).href;
  const nav=await call('Page.navigate',{url});assert.ok(!nav.errorText,nav.errorText);await until(async()=>{try{return await js(`location.href===${JSON.stringify(url)} && document.readyState==='complete'`)}catch{return false}});
  const run=(body,gesture=false)=>js(`(()=>{const q=id=>document.getElementById(id),set=(id,i)=>{q(id).value=String(i);q(id).dispatchEvent(new Event('change',{bubbles:true}))};${body}})()`,gesture);
  assert.equal(await run("return q('evidence').options.length"),4);stage='timeline';let events=0,independent=0,audio=0;
  for(let g=0;g<groups.length;g++){
   assert.equal(await run(`set('evidence',${g});return q('scenario').options.length`),groups[g].length);
   for(let i=0;i<groups[g].length;i++){
    const r=groups[g][i],out=await run(`set('scenario',${i});const a=q('audio'),out={final:JSON.parse(q('final').textContent),hidden:q('audioPanel').hidden,src:a.getAttribute('src'),paused:a.paused,autoplay:a.autoplay,volume:a.volume,disabled:q('event').disabled,items:[]};for(let j=0;j<q('event').options.length;j++){set('event',j);out.items.push({detail:JSON.parse(q('detail').textContent),summary:q('summary').textContent,prev:q('prev').disabled,next:q('next').disabled})}return out`);
    assert.deepEqual(out.final,r.final??r);assert.equal(out.hidden,!r.file);assert.equal(out.disabled,!r.trace);assert.ok(out.paused&&!out.autoplay&&Math.abs(out.volume-.12)<1e-7);
    assert.equal(out.src,r.file?keys[g].split('/')[0]+'/'+r.file:null);
    const expected=r.trace?r.trace.map((t,j)=>({detail:t,summary:[t.label,'local '+t.local.commit,'witness '+t.witness.commit,typeof t.result==='string'?t.result:JSON.stringify(t.result)].join(' | '),prev:j===0,next:j===r.trace.length-1})):[{detail:r,summary:[r.name||r.cut,r.retry||r.error||'see receipt'].join(' | '),prev:true,next:true}];
    assert.deepEqual(out.items,expected);if(r.trace){events+=r.trace.length;audio++}else independent++;
   }
  }
  assert.equal(events,96);assert.equal(independent,28);assert.equal(audio,28);
  assert.ok(await run("set('evidence',0);set('scenario',0);set('event',0);if(!q('prev').disabled)return false;q('next').click();if(q('event').value!=='1')return false;q('prev').click();return q('event').value==='0'&&q('prev').disabled"));
  for(const gain of [0,7,25])assert.ok(await run(`q('gain').value=${gain};q('gain').dispatchEvent(new Event('input'));return Math.abs(q('audio').volume-${gain}/100)<1e-7&&q('gainValue').textContent==='${gain}%'`));
  assert.ok(await run("q('pause').click();q('stop').click();return q('audio').paused&&q('audio').currentTime===0"));
  stage='export';await call('Page.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});const exportHashes={};
  for(let g=0;g<keys.length;g++){
   const name=keys[g].replace('/','-'),original=read(keys[g]),file=path.join(downloads,name);
   await run(`set('evidence',${g});q('export').click()`,true);
   await until(()=>fs.existsSync(file)&&fs.statSync(file).size===original.length&&!fs.readdirSync(downloads).some(n=>n.endsWith('.crdownload')));
   assert.deepEqual(fs.readFileSync(file),original);exportHashes[name]=sha(original);
  }
  assert.deepEqual(errors,[]);return {status:'PASS',browser:await get('/json/version'),sessions:audio,trace_events:events,independent_cases:independent,gain_controls:3,export_sha256:exportHashes,errors,playback:'NOT_RUN',windows_persistence:'NOT_RUN'};
 }catch(e){console.log(JSON.stringify({status:'FAIL',stage,error:String(e),errors,stderr,launch:{elapsed_ms:Date.now()-started,pid:chrome.pid??null,exit_code:chrome.exitCode,signal:chrome.signalCode,port,port_read_error:portReadError,endpoint_error:endpointError,profile_entries:fs.readdirSync(profile).sort().slice(0,40)}}));throw e}
 finally{if(ws)ws.close();chrome.kill();await sleep(500);for(const d of [profile,downloads])try{fs.rmSync(d,{recursive:true,force:true})}catch{}}
}
async function main(){const checked=staticCheck();if(process.argv[3]==='--static-only'){console.log(JSON.stringify(checked));return}console.log(JSON.stringify(await browser(process.argv[3]||'google-chrome'),null,2))}
main().catch(e=>{console.error(e);process.exitCode=1});
