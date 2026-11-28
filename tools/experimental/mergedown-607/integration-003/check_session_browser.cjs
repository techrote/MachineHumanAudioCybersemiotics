'use strict';
// Refs #607: v40 evidence inspector, real browser DOM; no audio playback or sandbox bypass.
const fs=require('node:fs'), path=require('node:path'), os=require('node:os');
const assert=require('node:assert/strict'), {createHash}=require('node:crypto');
const {spawn}=require('node:child_process'), {pathToFileURL}=require('node:url');
const root=path.resolve(process.argv[2]);
const sha=b=>createHash('sha256').update(b).digest('hex');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn){for(let i=0;i<80;i++){const v=await fn();if(v)return v;await sleep(150);}throw Error('browser readiness timed out');}
const keys=['controls.json','seed113/receipt.json','seed71/receipt.json'];
function sourceRows(){
  return keys.filter(k=>k.includes('/')).flatMap(key=>JSON.parse(fs.readFileSync(path.join(root,key),'utf8')).rows.map(row=>({key,row})));
}
function staticCheck(){
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  const payload=JSON.parse(html.match(/<script id="payload" type="application\/json">([^]*?)<\/script>/)[1]);
  assert.deepEqual(Object.keys(payload).sort(),keys);
  for(const key of keys)assert.deepEqual(Buffer.from(payload[key],'base64'),fs.readFileSync(path.join(root,key)));
  const rows=sourceRows();assert.equal(rows.length,24);assert.equal(rows.reduce((n,r)=>n+r.row.trace.length,0),392);
  return {status:'PASS',static_export_bytes:keys.length,browser:'NOT_RUN'};
}
async function browser(exe){
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-schedule-'));
  const flags=['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'];
  const chrome=spawn(exe,flags,{stdio:['ignore','ignore','pipe']});
  let stderr='',launchError,ws,stage='launch';const errors=[],downloadEvents=[];
  chrome.on('error',e=>launchError=e);chrome.stderr.on('data',b=>stderr=(stderr+b).slice(-4000));
  try{
    const port=await until(()=>{if(launchError)throw launchError;if(chrome.exitCode!==null)throw Error('Chrome exit '+chrome.exitCode);try{return fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').split('\n')[0].trim()}catch{return null}});
    const get=async p=>(await fetch(`http://127.0.0.1:${port}${p}`,{signal:AbortSignal.timeout(3000)})).json();
    const page=await until(async()=>{try{return (await get('/json/list')).find(x=>x.type==='page')}catch{return null}});
    ws=new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('CDP open timeout')),5000);ws.addEventListener('open',()=>{clearTimeout(t);resolve()},{once:true});ws.addEventListener('error',()=>{clearTimeout(t);reject(Error('CDP open error'))},{once:true})});
    let seq=0;const pending=new Map();
    ws.addEventListener('message',ev=>{const x=JSON.parse(ev.data);if(x.id){const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}}else if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text);else if(x.method==='Page.downloadWillBegin'||x.method==='Page.downloadProgress')downloadEvents.push({method:x.method,params:x.params})});
    const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},10000);pending.set(id,{resolve,reject,t});ws.send(JSON.stringify({id,method,params}))});
    const evalJS=async (expression,userGesture=false)=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
    stage='navigate';await call('Runtime.enable');await call('Page.enable');
    const url=pathToFileURL(path.join(root,'index.html')).href;
    const nav=await call('Page.navigate',{url});assert.ok(!nav.errorText,nav.errorText);
    await until(async()=>{try{return await evalJS(`location.href===${JSON.stringify(url)} && document.readyState==='complete'`)}catch{return false}});
    const rows=sourceRows();
    assert.equal(await evalJS("document.querySelector('#session').options.length"),24);
    stage='timeline';let slots=0;
    for(let i=0;i<rows.length;i++){
      const {key,row}=rows[i];
      const result=await evalJS("(()=>{const q=id=>document.getElementById(id);q('session').value='"+i+"';q('session').dispatchEvent(new Event('change',{bubbles:true}));const a=q('audio'),out={metrics:JSON.parse(q('metrics').textContent),src:a.getAttribute('src'),paused:a.paused,autoplay:a.autoplay,volume:a.volume,detail:[]};for(let j=0;j<q('slot').options.length;j++){q('slot').value=String(j);q('slot').dispatchEvent(new Event('change',{bubbles:true}));out.detail.push({decode:JSON.parse(q('decode').textContent),state:JSON.parse(q('state').textContent),beliefs:JSON.parse(q('beliefs').textContent),location:q('location').textContent,prev:q('prev').disabled,next:q('next').disabled})}return out})()");
      assert.deepEqual(result.metrics,{result:row.result,metrics:row.metrics});
      assert.deepEqual(result.detail,row.trace.map((t,j)=>({decode:{job:t.job,fault:t.fault,decoded:t.decoded},state:{decision:t.decision,state:t.state},beliefs:{beliefs:t.beliefs,pending:t.pending},location:'Slot '+t.t+' | '+(t.start/16000).toFixed(3)+' s | '+row.file,prev:j===0,next:j===row.trace.length-1})));
      assert.equal(result.src,key.split('/')[0]+'/'+row.file);assert.ok(result.paused&&!result.autoplay&&Math.abs(result.volume-.12)<1e-7);slots+=row.trace.length;
    }
    assert.equal(slots,392);
    assert.ok(await evalJS("(()=>{const q=id=>document.getElementById(id);q('slot').value='0';q('slot').dispatchEvent(new Event('change'));if(!q('prev').disabled)return false;q('next').click();if(q('slot').value!=='1')return false;q('prev').click();return q('slot').value==='0'&&q('prev').disabled})()"));
    for(const gain of [0,7,25])assert.ok(await evalJS("(()=>{const g=document.querySelector('#gain');g.value="+gain+";g.dispatchEvent(new Event('input'));return Math.abs(document.querySelector('audio').volume-"+gain+"/100)<1e-7&&document.querySelector('#gainvalue').textContent==='"+gain+"%'})()"));
    assert.ok(await evalJS("(()=>{document.querySelector('#pause').click();document.querySelector('#stop').click();return document.querySelector('audio').paused&&document.querySelector('audio').currentTime===0})()"));
    stage='export';const downloads=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-export-'));
    let exportState={};
    try{
      await call('Page.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
      const exportHashes={};
      for(const key of keys){
        const i=rows.findIndex(x=>x.key===key),name=key.replace('/','-'),original=fs.readFileSync(path.join(root,key)),file=path.join(downloads,name);
        exportState={key,name,expected_bytes:original.length};
        if(key==='controls.json')await evalJS("document.querySelector('#controls').click()",true);
        else await evalJS("(()=>{const q=id=>document.getElementById(id);q('session').value='"+i+"';q('session').dispatchEvent(new Event('change'));q('export').click()})()",true);
        await until(()=>{exportState.files=fs.readdirSync(downloads);return fs.existsSync(file)&&fs.statSync(file).size===original.length&&!exportState.files.some(n=>n.endsWith('.crdownload'))});
        assert.deepEqual(fs.readFileSync(file),original);exportHashes[name]=sha(fs.readFileSync(file));
      }
      assert.deepEqual(errors,[]);
      return {status:'PASS',browser:await get('/json/version'),sessions:rows.length,slots,gain_controls:3,export_sha256:exportHashes,errors,playback:'NOT_RUN'};
    }catch(e){throw Error(String(e)+'; export state '+JSON.stringify(exportState))}finally{fs.rmSync(downloads,{recursive:true,force:true})}
  }catch(e){console.log(JSON.stringify({status:'FAIL',stage,error:String(e),errors,downloadEvents,stderr}));throw e}
  finally{if(ws)ws.close();chrome.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
}
async function main(){
  const checked=staticCheck();
  if(process.argv[3]==='--static-only'){console.log(JSON.stringify(checked));return;}
  console.log(JSON.stringify(await browser(process.argv[3]||'google-chrome'),null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
