#!/usr/bin/env python3
import hashlib, pathlib, shutil, subprocess, sys, zipfile
build=pathlib.Path(sys.argv[1]).resolve();out=build/'validation';out.mkdir(exist_ok=True)
def find_exec(name):
    names={name,name+'.exe'}
    xs=[p for p in build.rglob('*') if p.is_file() and p.name in names]
    if not xs: raise SystemExit(f'{name} executable not found')
    return xs[0]
validator=find_exec('validator');probe=find_exec('mhac_tts_sdk_probe')
original=sorted({p for p in build.rglob('*.vst3') if p.is_dir() and p.name in {'MHACLogos.vst3','MHACArticulum.vst3'}})
if len(original)!=2: raise SystemExit(f'expected 2 original bundles, found {original}')
ids={'MHACLogos.vst3':'2100','MHACArticulum.vst3':'2200'}
def exercise(b,tag):
    r=subprocess.run([str(validator),str(b)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/f'{tag}-{b.stem}-validator.txt').write_text(r.stdout)
    if r.returncode or '0 tests failed' not in r.stdout: raise SystemExit(f'validator failed for {b}: {r.returncode}')
    h=subprocess.run([str(probe),str(b),ids[b.name]],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/f'{tag}-{b.stem}-host.txt').write_text(h.stdout)
    if h.returncode or 'VST_TTS_HOST_PASS' not in h.stdout: raise SystemExit(f'host probe failed for {b}: {h.returncode}')
    print(tag,b.name,'validator+host PASS')
for b in original: exercise(b,'built')
package=build/'MHAC-VST-TTS-FOUNDRY-001.zip'
with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for b in original:
        for p in sorted(b.rglob('*')):
            if p.is_file():z.write(p,pathlib.Path(b.name)/p.relative_to(b))
    specimens=build/'specimens'
    if specimens.exists():
        for p in sorted(specimens.rglob('*')):
            if p.is_file():z.write(p,pathlib.Path('Specimens')/p.relative_to(specimens))
extract=build/'extracted-package';shutil.rmtree(extract,ignore_errors=True);extract.mkdir()
with zipfile.ZipFile(package) as z:
    bad=z.testzip()
    if bad:raise SystemExit(f'CRC failure {bad}')
    z.extractall(extract)
extracted=sorted(extract.glob('*.vst3'))
if len(extracted)!=2:raise SystemExit('extracted bundle count')
for b in extracted:exercise(b,'extracted')
sha=hashlib.sha256(package.read_bytes()).hexdigest();(out/'package-sha256.txt').write_text(f'{sha}  {package.name}\n')
print('PACKAGE_PASS',package,sha)
