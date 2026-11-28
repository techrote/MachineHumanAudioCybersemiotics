import subprocess,tempfile,pathlib,json,hashlib,urllib.request,urllib.error,base64
from playwright.sync_api import sync_playwright
with tempfile.TemporaryDirectory() as root:
    proc=subprocess.Popen(['node','live-v75.cjs',str(pathlib.Path(root)/'session'),'0'],stdout=subprocess.PIPE,text=True)
    try:
        url=proc.stdout.readline().strip()
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
            page=browser.new_page(accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            # Ordinary navigation is blocked in this environment; use actual HTTP via a test-only bridge.
            def bridge(route,opts):
                headers=opts.get('headers',{});headers['Origin']=url.rstrip('/')
                req=urllib.request.Request(url.rstrip('/')+route,data=opts.get('body','').encode() if opts.get('method')=='POST' else None,headers=headers,method=opts.get('method','GET'))
                try:
                    with urllib.request.urlopen(req) as r: return {'status':r.status,'bytes':base64.b64encode(r.read()).decode()}
                except urllib.error.HTTPError as e: return {'status':e.code,'bytes':base64.b64encode(e.read()).decode()}
            page.expose_function('bridge',bridge)
            html=urllib.request.urlopen(url).read().decode(); shim="<script>window.fetch=async (route,opts)=>{const r=await bridge(route,opts);const b=Uint8Array.from(atob(r.bytes),c=>c.charCodeAt(0));return new Response(b,{status:r.status});};</script>"
            page.set_content(shim+html);page.wait_for_function("document.querySelector('#status').textContent==='Ready'")
            def click(id):
                page.locator('#'+id).click();page.wait_for_function("document.querySelector('#status').textContent!=='Working…'");assert not page.locator('#error').inner_text(),page.locator('#error').inner_text()
            click('init');click('register');click('enqueue');click('step');page.select_option('#action','query');page.select_option('#back','erase');page.select_option('#retry','1');click('enqueue');click('step');click('step');assert 'report' in page.locator('#evidence').inner_text();page.locator('#deliveries button').click();page.wait_for_function("document.querySelector('#evidence').textContent==='[]'");page.select_option('#recording','0');click('loadAudio');page.wait_for_function("document.querySelector('#audio').readyState>=1");assert page.evaluate("document.querySelector('#audio').volume") == .12;assert page.evaluate("document.querySelector('#wave').getContext('2d').getImageData(0,0,1000,100).data.some(x=>x!==0)")
            page.evaluate("async()=>{const a=document.querySelector('#audio');a.muted=true;await a.play();}");page.wait_for_function("document.querySelector('#audio').currentTime>0.1");page.evaluate("document.querySelector('#audio').pause()")
            with page.expect_download() as download: page.locator('#export').click()
            data=json.loads(pathlib.Path(download.value.path()).read_text());assert data['scheduler']['spent']==77440+2*169216;assert len(data['recordings'])==5;assert not errors,errors;page=browser.new_page();page.expose_function('bridge',bridge);page.set_content(shim+html);page.wait_for_function("document.querySelector('#status').textContent==='Ready'");assert page.locator('#jobs tr').count()==2
            print(json.dumps({'navigation':'blocked; injected HTML with actual HTTP bridge','browser':browser.version,'live_controls':'pass','return_repair':'pass','ack':'pass','waveform':'pass','muted_playhead':'pass','export':'pass','reload':'pass','samples':data['scheduler']['spent']}));browser.close()
    finally:
        proc.terminate();proc.wait(timeout=10)
