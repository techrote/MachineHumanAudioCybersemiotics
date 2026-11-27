'use strict';
// Refs #607: scheduled PCM timeline, ordinary local Chrome, no playback or network stimuli.
const fs=require('node:fs'), path=require('node:path'), os=require('node:os');
const assert=require('node:assert/strict'), {createHash}=require('node:crypto');
const {spawn}=require('node:child_process'), {pathToFileURL}=require('node:url');
const root=path.resolve(process.argv[2]);
const sha=b=>createHash('sha256').update(b).digest('hex');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn){for(let i=0;i<80;i++){const v=await fn();if(v)return v;await sleep(150);}throw Error('browser readiness timed out');}
async function browser(exe){
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-schedule-'));
  const flags=['--headless','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'];
  if(process.platform==='linux'&&process.getuid?.()===0)flags.unshift('--no-sandbox');
  const chrome=spawn(exe,flags,{stdio:['ignore','ignore','pipe']});
  let stderr='',launchError,ws;const errors=[];
  chrome.on('error',e=>launchError=e);chrome.stderr.on('data',b=>stderr=(stderr+b).slice(-4000));
  try{
    const port=await until(()=>{if(launchError)throw launchError;if(chrome.exitCode!==null)throw Error('Chrome exit '+chrome.exitCode);try{return fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').split('\n')[0].trim()}catch{return null}});
    const get=async p=>(await fetch(`http://127.0.0.1:${port}${p}`,{signal:AbortSignal.timeout(3000)})).json();
    const page=await until(async()=>{try{return (await get('/json/list')).find(x=>x.type==='page')}catch{return null}});
    ws=new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('CDP open timeout')),5000);ws.addEventListener('open',()=>{clearTimeout(t);resolve()},{once:true});ws.addEventListener('error',()=>{clearTimeout(t);reject(Error('CDP open error'))},{once:true})});
    let seq=0;const pending=new Map();
    ws.addEventListener('message',ev=>{const x=JSON.parse(ev.data);if(x.id){const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.reject(Error(JSON.stringify(x.error))):p.resolve(x.result)}}else if(x.method==='Runtime.exceptionThrown')errors.push(x.params.exceptionDetails.text)});
    const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,t=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},10000);pending.set(id,{resolve,reject,t});ws.send(JSON.stringify({id,method,params}))});
    const evalJS=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
    await call('Runtime.enable');await call('Page.enable');
    const url=pathToFileURL(path.join(root,'index.html')).href;
    const nav=await call('Page.navigate',{url});assert.ok(!nav.errorText,nav.errorText);
    await until(async()=>{try{return await evalJS(`location.href===${JSON.stringify(url)} && document.readyState==='complete'`)}catch{return false}});
    const evidence=path.join(root,'scheduled-v2-output');
    const manifest=JSON.parse(fs.readFileSync(path.join(evidence,'manifest.json'),'utf8'));
    const rows=manifest.rows.map(r=>JSON.parse(fs.readFileSync(path.join(evidence,r.name+'-'+r.policy+'.json'),'utf8')));
    assert.equal(await evalJS("document.querySelector('#session').options.length"),45);
    assert.equal(await evalJS("document.querySelector('#slot').options.length"),10);
    let slots=0;
    for(let i=0;i<rows.length;i++){
      const s=rows[i];
      const result=await evalJS(`(()=>{const q=id=>document.getElementById(id);q('session').value='${i}';q('session').dispatchEvent(new Event('change',{bubbles:true}));const a=q('audio'),out={metrics:JSON.parse(q('metrics').textContent),src:a.getAttribute('src'),paused:a.paused,autoplay:a.autoplay,volume:a.volume,rows:q('timeline').rows.length,detail:[]};for(let j=0;j<10;j++){q('slot').value=String(j);q('slot').dispatchEvent(new Event('change',{bubbles:true}));out.detail.push(JSON.parse(q('detail').textContent))}return out})()`);
      assert.deepEqual(result.metrics,s.metrics);assert.deepEqual(result.detail,s.trace);assert.equal(result.src,'scheduled-v2-output/'+s.name+'-'+s.policy+'.wav');assert.ok(result.paused&&!result.autoplay&&Math.abs(result.volume-.12)<1e-7);assert.equal(result.rows,10);slots+=10;
    }
    assert.ok(await evalJS("(()=>{const q=id=>document.getElementById(id);q('slot').value='0';q('slot').dispatchEvent(new Event('change'));if(!q('prev').disabled)return false;q('next').click();if(q('slot').value!=='1')return false;q('prev').click();q('slot').value='9';q('slot').dispatchEvent(new Event('change'));return q('next').disabled})()"));
    for(const gain of [0,.07,.25])assert.ok(await evalJS(`(()=>{const g=document.querySelector('#gain');g.value=${gain};g.dispatchEvent(new Event('input'));return Math.abs(document.querySelector('audio').volume-${gain})<1e-7})()`));
    assert.ok(await evalJS("(()=>{document.querySelector('#stop').click();return document.querySelector('audio').paused&&document.querySelector('audio').currentTime===0})()"));
    const downloads=fs.mkdtempSync(path.join(os.tmpdir(),'mhac-export-'));
    try{
      await call('Page.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
      await evalJS("document.querySelector('#export').click()");
      const s=rows.at(-1),name=s.name+'-'+s.policy+'.json';
      const file=path.join(downloads,name);await until(()=>fs.existsSync(file));assert.deepEqual(fs.readFileSync(file),fs.readFileSync(path.join(evidence,name)));
      assert.deepEqual(errors,[]);
      return {status:'PASS',browser:await get('/json/version'),sessions:rows.length,slots,gain_controls:3,export_sha256:sha(fs.readFileSync(file)),errors,playback:'NOT_RUN'};
    }finally{fs.rmSync(downloads,{recursive:true,force:true})}
  }catch(e){console.error(JSON.stringify({status:'FAIL',error:String(e),errors,stderr}));throw e}
  finally{if(ws)ws.close();chrome.kill();await sleep(500);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
}
async function main(){
  console.log(JSON.stringify(await browser(process.argv[3]||'google-chrome'),null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
