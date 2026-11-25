from playwright.sync_api import sync_playwright
from pathlib import Path
import json, re, hashlib, wave
p=Path.cwd(); src=(p/'return-window.js').read_text(); html=(p/'return-window.html').read_text(); result={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--mute-audio','--disable-dev-shm-usage']); result['version']=b.version
 page=b.new_page(accept_downloads=True); errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
 try:
  page.goto((p/'return-window.html').as_uri(),timeout=5000); page.wait_for_function('document.getElementById("policy").options.length===6',timeout=2000); result['launch']='file://'
 except Exception as e:
  result['fileLaunchError']=str(e).splitlines()[0]; page.close(); page=b.new_page(accept_downloads=True); errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
  # identical HTML markup and both script bodies, inserted locally to bypass denied file URL
  page.set_content(re.sub(r'<script src="return-window.js"></script><script>[\s\S]*?</script>', '', html)); page.add_script_tag(content=src); page.add_script_tag(content=re.search(r'<script>([\s\S]*?)</script>',html).group(1)); result['launch']='set_content + exact scripts'
 assert page.locator('#policy option').count()==6
 assert '0 / 40' in page.locator('#tick').inner_text()
 page.select_option('#scenario','overload'); page.select_option('#dl','0'); page.select_option('#al','0'); page.select_option('#to','6'); page.click('#step'); assert page.locator('#channel span').count()==1
 page.click('#offer'); assert page.locator('#channel span').count()==2
 page.click('#drop-ack'); assert page.locator('#channel span').count()==3
 page.click('#reset'); assert page.locator('#channel span').count()==0
 page.click('#run'); assert page.locator('#channel span').count()==40
 assert json.loads(page.locator('#stats').inner_text())['received']==12
 page.select_option('#policy','ack-first'); assert json.loads(page.locator('#stats').inner_text())['received']==11
 page.select_option('#delay','12'); assert json.loads(page.locator('#stats').inner_text())['confirmed']==0
 page.select_option('#delay','2'); page.click('#play'); page.wait_for_function('document.getElementById("audio").currentTime>0.1',timeout=5000); result['mediaDuration']=page.locator('#audio').evaluate('(a)=>a.duration'); result['playhead']=page.locator('#audio').evaluate('(a)=>a.currentTime'); assert result['mediaDuration']==10; page.click('#stop'); assert page.locator('#audio').evaluate('(a)=>a.paused')
 with page.expect_download() as d: page.click('#json')
 j=json.loads(Path(d.value.path()).read_text()); assert j['metrics']['received']==11 and j['policy']=='ack-first' and j['config']['delay']==2 and j['until']==40
 with page.expect_download() as d: page.click('#wav')
 f=Path(d.value.path()); result['browserWavSha256']=hashlib.sha256(f.read_bytes()).hexdigest(); assert result['browserWavSha256']==hashlib.sha256((p/'out/ackFirst.wav').read_bytes()).hexdigest()
 with wave.open(str(f)) as w: assert w.getframerate()==8000 and w.getnframes()==80000
 page.click('#test'); page.wait_for_function('document.getElementById("status").textContent.includes("374497 assertions passed")',timeout=20000)
 result.update({'controls':'pass','timeline':'pass','jsonExport':'pass','wavExport':'byte-identical native CLI witness','regressionStatus':page.locator('#status').inner_text(),'pageErrors':errors,'mutedHeadless':True}); assert not errors
 b.close()
print(json.dumps(result,indent=2)); (p/'browser-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
