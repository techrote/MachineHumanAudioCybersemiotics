"""Independent archived transcript audit for #633 9f28b3f4; no host execution."""
import hashlib, io, json, pathlib, re, sys, zipfile
PINS = {
    15233734011: ('2bdd984ca696964779bf3228e09b6e80502a51c14c7d321777ae11874f5fa017', 'bed4ea59c096f938822fd02a8f87707dc79f707c6b9467b0d2871201955fe8e0', 'MHACPalimpsestShuttle-Windows-x64.zip'),
    15233868488: ('8cbd5e26692aae3b19784ab58794f920c16c1d68b89bdbaeca6fce10567ede50', 'bc7838a4ebc7daa16cca8e0cd84f16e2b7bd866727824c7813ba72b51f787b5c', 'MHACTraceBell-Windows-x64.zip'),
}
def sha(data):
    return hashlib.sha256(data).hexdigest()
def require(ok, message):
    if not ok:
        raise ValueError(message)
def audit(raw, shuttle):
    text = raw.decode('utf-8-sig')
    frames = {44100:20000,48000:20000,96000:20000}
    if shuttle:
        frames.update({384000:92160,1234.568:20000,12345.678:20000,123456.780:20000,1234567.800:296298})
    expected = {(float(r),b,n,0.0) for r,n in frames.items() for b in (127,1024)}
    rows = re.findall(r'^SDK_AUTOMATION rate=([\d.]+) block=(\d+) frames=(\d+) max_error=(\S+)\s*$',text,re.M)
    got = [(float(r),int(b),int(n),float(e)) for r,b,n,e in rows]
    require(len(got)==len(expected) and set(got)==expected and len(re.findall(r'^SDK_AUTOMATION ',text,re.M))==len(expected),'automation matrix')
    require(len(re.findall(r'^SDK_STATE_PASS writes=20000 reads=[1-9]\d* blocks=[1-9]\d*\s*$',text,re.M))==1,'state receipt')
    require(len(re.findall(r'^SDK_PROBE_PASS automation_cases=6 stereo_frames=120000\s*$',text,re.M))==1,'final receipt')
    require(len(re.findall(r'^SDK_EXTENDED_RATE_PASS automation_cases=10\s*$',text,re.M))==int(shuttle),'extended receipt')
    return {'cases':len(got),'sha256':sha(raw)}
def run(root):
    result = {}; probes = []
    for artifact,(outer,inner,name) in PINS.items():
        data = (root/f'github-actions-artifact-{artifact}.zip').read_bytes()
        require(sha(data)==outer,'outer archive')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            require(z.namelist()==[name] and z.testzip() is None,'outer inventory')
            data = z.read(name)
        require(sha(data)==inner,'inner archive')
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            require(z.testzip() is None and z.namelist().count('sdk-probe.txt')==1,'inner archive')
            probes.append(z.read('sdk-probe.txt'))
        result[str(artifact)] = audit(probes[-1],artifact==15233734011)
    require(probes[0]!=probes[1],'cross-package transcript contamination')
    controls = [probes[1],probes[0]+probes[0].splitlines(keepends=True)[0],probes[0].replace(b'max_error=0',b'max_error=1',1),probes[0].replace(b'SDK_STATE_PASS',b'OTHER'),probes[0].replace(b'SDK_EXTENDED_RATE_PASS',b'OTHER')]
    for control in controls:
        try:
            audit(control,True)
        except ValueError:
            continue
        raise ValueError('negative control admitted')
    return {'archived_probe_receipts':result,'negative_controls_refused':len(controls),'fresh_host_execution':False}
if __name__ == '__main__':
    print(json.dumps(run(pathlib.Path(sys.argv[1])),indent=2,sort_keys=True))
