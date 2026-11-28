from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading, json
root=Path.cwd()
server=ThreadingHTTPServer(('127.0.0.1',0),SimpleHTTPRequestHandler)
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--mute-audio'])
 page=b.new_page(accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 modes={}
 try:
  page.goto((root/'schedule-inspector.html').as_uri(),timeout=5000);modes['file']=page.title()
 except Exception as e: modes['file']=str(e).split('\n')[0]
 if modes.get('file')!='MHAC | Scheduled PCM relay':
  page=b.new_page(accept_downloads=True);page.on('pageerror',lambda e:errors.append(str(e)))
  try:page.goto(f'http://127.0.0.1:{server.server_port}/schedule-inspector.html',timeout=5000);modes['http']=page.title()
  except Exception as e:modes['http']=str(e).split('\n')[0]
 if not any(v=='MHAC | Scheduled PCM relay' for v in modes.values()):
  page=b.new_page(accept_downloads=True);page.on('pageerror',lambda e:errors.append(str(e)));page.set_content((root/'schedule-inspector.html').read_text());modes['fallback']='set_content'
 files=[root/'scheduled-clock-v3-output'/'manifest.json']
 for stem in ['delayed-ack-first','delayed-data-first','forged-reserve']:
  files += [root/'scheduled-clock-v3-output'/f'{stem}.{ext}' for ext in ['json','wav']]
 page.locator('#files').set_input_files(files)
 page.wait_for_function("document.querySelector('#status').textContent.includes('PCM loaded')")
 page.locator('#session').select_option('delayed-ack-first');page.wait_for_function("document.querySelector('#status').textContent.startsWith('delayed-ack-first')")
 assert page.locator('#timeline button').count()==10
 assert page.locator('#compare tr').count()==4
 page.locator('#timeline button').nth(3).click();assert 'Slot 4' in page.locator('#slot-summary').inner_text()
 page.wait_for_function("document.querySelector('#player').readyState>=1")
 duration=page.locator('#player').evaluate('(a)=>a.duration');assert duration==20
 page.locator('#player').evaluate('(a)=>a.play()');page.wait_for_function("document.querySelector('#player').currentTime>.1")
 page.locator('#player').evaluate('(a)=>a.pause()')
 page.locator('#session').select_option('forged-reserve');page.wait_for_function("document.querySelector('#status').textContent.startsWith('forged-reserve')")
 assert 'False confirms' in page.locator('#stats').inner_text()
 with page.expect_download() as d:page.locator('#export').click()
 recovered=json.loads(Path(d.value.path()).read_text());assert recovered['metrics']['invalid']==1 and recovered['metrics']['uniqueReceipts']==0
 assert not errors, errors
 result={'chromium':b.version,'launch':modes,'timelineSlots':10,'comparisonRows':3,'durationSeconds':duration,'mutedPlayheadAdvanced':True,'exportReread':True,'pageErrors':errors}
 (root/'clock-browser-receipt.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result));b.close()
server.shutdown()
