"""Separate rational oracle and real browser fixture for OBS-AFFINE-001.
Run: python check_affine.py /path/to/empty/scratch [--browser /path/to/chromium]
Browser mode needs Playwright installed separately; no online dependencies at runtime.
"""
import argparse, hashlib, json, subprocess, wave
from collections import Counter
from fractions import Fraction
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("scratch",type=Path)
p.add_argument("--browser")
args=p.parse_args()
src=Path(__file__).resolve().parent/"affine-snapshot"
root=args.scratch.resolve()
root.mkdir(parents=True,exist_ok=True)
assert not any(root.iterdir()),"Use an empty scratch directory"
for name,pin in {"core.js":"47938c769604ae56a1f8cb92e5d4ccc3e20f8d59","index.html":"5ee12f884479425acf8d3137a1974ff6df9c8cb4"}.items():
 b=(src/name).read_bytes()
 assert hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()==pin,name
result=subprocess.run(["node",str(src/"core.js")],cwd=root,check=True,capture_output=True,text=True)
assert json.loads(result.stdout)=={"assertions":1036,"status":"PASS"}
receipt=json.loads((root/"receipt.json").read_text())
assert len(receipt["rows"])==288
for c in receipt["rows"]:
 p,q,r,ms=c["p"],c["q"],c["rate"],c["ms"]
 a=[0,p,p+q,2*p+q]; groups=Counter()
 for i,row in enumerate(c["rows"]):
  b=a[:i]+a[i+1:]
  lo,hi=(0,a[-1]) if c["frame"]=="fixed" else (b[0],b[-1])
  expected=[r//10+int(Fraction((x-lo)*r*ms,1000*(hi-lo))+Fraction(1,2)) for x in b]
  assert row["samples"]==expected
  groups[tuple(expected)]+=1
 assert c["distinctReceipts"]==len(groups) and c["optimalIndexAccuracy"]==len(groups)/4
print("Native 1036; rational oracle 1152 rows, 288 conditions PASS")
print(receipt["summary"])
if args.browser:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=args.browser,headless=True)
  page=browser.new_page(accept_downloads=True)
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  html=(src/"index.html").read_text().replace('<script src="core.js"></script>',"<script>"+(src/"core.js").read_text()+"</script>")
  page.set_content(html,wait_until="load")
  assert page.locator("#rows tr").count()==4
  assert "2/4 distinct receipts" in page.locator("#status").inner_text()
  assert page.locator("#player").get_attribute("src") is None
  for i in (1,3):
   with page.expect_download() as dl:
    page.locator("#rows tr").nth(i).get_by_text("WAV",exact=True).click()
   dl.value.save_as(root/f"deletion-{i+1}.wav")
  w=root/"deletion-2.wav"
  assert w.read_bytes()==(root/"deletion-4.wav").read_bytes()
  assert hashlib.sha256(w.read_bytes()).hexdigest()==receipt["witness"]["stimuli"][1]["sha256"]
  with wave.open(str(w)) as f:
   assert (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes())==(1,2,8000,8000)
  page.locator("#frame").select_option("fixed")
  page.locator("#apply").click()
  assert "4/4 distinct receipts" in page.locator("#status").inner_text()
  with page.expect_download() as dl:
   page.locator("#save").click()
  dl.value.save_as(root/"condition.json")
  assert json.loads((root/"condition.json").read_text())["distinctReceipts"]==4
  page.locator("#selftest").click()
  assert json.loads(page.locator("#tests").inner_text())["assertions"]==1036
  page.locator("#p").fill("0")
  page.locator("#apply").click()
  assert page.locator("#status").inner_text()=="Unsupported condition"
  assert not errors
  browser.close()
 print("Real DOM fixture and WAV/JSON downloads PASS")
