"""Pinned Bell/Shuttle distribution refresh. Archived host evidence, not fresh host execution."""
import itertools, json, math, pathlib, re, sys, zipfile
import assemble as a
from extend import manifest
BASE='7800d5084eca08d5939ec7348faa5d9c57f0c828df92787d7cccabffe3842106'
HEAD='9f28b3f4f94bbc702dcf851a3a0f75485b189001'
RUN=46074275485
PINS=[('MHACPalimpsestShuttle',15233734011,'2bdd984ca696964779bf3228e09b6e80502a51c14c7d321777ae11874f5fa017','bed4ea59c096f938822fd02a8f87707dc79f707c6b9467b0d2871201955fe8e0'),('MHACTraceBell',15233868488,'8cbd5e26692aae3b19784ab58794f920c16c1d68b89bdbaeca6fce10567ede50','bc7838a4ebc7daa16cca8e0cd84f16e2b7bd866727824c7813ba72b51f787b5c')]
def probe(raw,shuttle):
    log=raw.decode('utf-8-sig'); frames={44100:20000,48000:20000,96000:20000}
    if shuttle: frames.update({384000:92160,1234.568:20000,12345.678:20000,123456.780:20000,1234567.800:296298})
    rows=re.findall(r'^SDK_AUTOMATION rate=([\d.]+) block=(\d+) frames=(\d+) max_error=([^\s]+)\s*$',log,re.M)
    expected={(float(r),b,n,0.0) for r,n in frames.items() for b in (127,1024)}
    got=[(float(r),int(b),int(n),float(e)) for r,b,n,e in rows]
    a.need(len(got)==len(expected) and set(got)==expected and len(re.findall(r'^SDK_AUTOMATION ',log,re.M))==len(expected),'automation matrix')
    a.need(len(re.findall(r'^SDK_STATE_PASS writes=20000 reads=[1-9]\d* blocks=[1-9]\d*\s*$',log,re.M))==1,'state receipt')
    a.need(len(re.findall(r'^SDK_PROBE_PASS automation_cases=6 stereo_frames=120000\s*$',log,re.M))==1,'probe final receipt')
    a.need(len(re.findall(r'^SDK_EXTENDED_RATE_PASS automation_cases=10\s*$',log,re.M))==int(shuttle),'extended receipt')
    return len(got)
def host(rows,names,field):
    expected=set(itertools.product(names,(44100,48000,96000))); got=[(x.get('name'),x['rate']) for x in rows]
    a.need(len(got)==len(expected) and set(got)==expected,'host matrix')
    a.need(all(x[field]==0 and math.isfinite(x['peak']) and 0<x['peak']<1 for x in rows),'host errors/peaks')
    return len(rows)
def main(src,dest):
    raw=(src/'MHAC-VST-eight-plugin-signal-refresh.zip').read_bytes(); a.need(a.sha(raw)==BASE,'base digest'); out=a.files(raw); manifest(out,'SHA256SUMS')
    for mod in ('assemble','extend'): a.need(pathlib.Path(sys.modules[mod].__file__).read_bytes()==out[mod+'.py'],'helper identity')
    cat=json.loads(out['catalogue.json']); updates=[]
    for name,artifact,outer,inner in PINS:
        raw=(src/f'github-actions-artifact-{artifact}.zip').read_bytes(); a.need(a.sha(raw)==outer,'outer digest'); z=a.files(raw); a.need(len(z)==1,'nested count'); blob=next(iter(z.values())); a.need(a.sha(blob)==inner,'inner digest'); f=a.files(blob)
        prior=next(p for p in cat['plugins'] if p['name']==name); prefix=name+'.vst3/Contents/'; binary=f[prefix+'x86_64-win/'+name+'.vst3']; a.pe(binary)
        a.need(dict(x.split('=',1) for x in f['BUILD-SOURCE.txt'].decode('utf-8-sig').splitlines())==dict(sdk=a.SDK,source=HEAD),'source/sdk')
        links={}
        for line in f['SDK-GITLINKS.txt'].decode('utf-8-sig').splitlines():
            m=re.fullmatch(r' ([0-9a-f]{40}) (\S+) \(.*\)',line); a.need(m and m[2] not in links,'gitlink'); links[m[2]]=m[1]
        a.need(links==a.LINKS,'gitlinks')
        mi=json.loads(re.sub(r',\s*([}\]])',r'\1',f[prefix+'Resources/moduleinfo.json'].decode('utf-8-sig'))); cl=mi['Classes']; ids=[c['CID'] for c in cl]; cid=next(c['CID'] for c in cl if c['Category']=='Audio Module Class'); a.need(mi['Name']==name and mi['Version']==prior['version'] and ids==prior['class_ids'] and all(c['SDKVersion']=='VST 3.8.0' and c['Version']==prior['version'] for c in cl),'module identity')
        log=f['validator.txt'].decode('utf-8-sig'); a.need('Result: 47 tests passed, 0 tests failed' in log and 'ERROR:' not in log.upper() and all(i in log for i in ids),'validator'); params=list(map(int,re.findall(r'Parameter \d+ \(id=(\d+)\)',log))); a.need(params==prior['parameter_ids'],'parameter IDs')
        presets={n:a.sha(b) for n,b in f.items() if n.endswith('.vstpreset') and a.preset(b,cid)}; wav={n:a.audio(b) for n,b in f.items() if n.endswith('.wav')}; a.need(presets==prior['standard_presets'] and wav==prior['audio'],'preset/audio stability')
        shuttle=name.endswith('Shuttle'); cases=probe(f['sdk-probe.txt'],shuttle); names={pathlib.PurePosixPath(n).stem for n in presets}; h=json.loads(f['host-receipt.json']); partitions=host(h,names if shuttle else {None},'partition_error' if shuttle else 'partition_max_error')
        if not shuttle: partitions+=host(json.loads(f['preset-host-receipt.json']),names,'partition_max_error')
        a.need(partitions==prior['host_partition_receipts'],'host receipt count')
        notices={n for n in f if n.startswith('SDK-') or n=='Steinberg-SDK-LICENSE.txt'}; a.need(len(notices)==8 and all(f[n] for n in notices) and f[prefix+'Resources/LICENSE.txt'],'license/provenance files')
        count=manifest(f,'SHA256SUMS.txt') if shuttle else None
        op='Packages/'+name+'/'; previous={n[len(op):]:b for n,b in out.items() if n.startswith(op)}; changes=sorted(n for n in set(previous)|set(f) if previous.get(n)!=f.get(n)); unchanged=sum(previous.get(n)==b for n,b in f.items())
        entry=dict(prior,source=HEAD,run=RUN,artifact=artifact,artifact_url=f'{a.ROOT}/actions/runs/{RUN}/artifacts/{artifact}',outer_sha256=outer,inner_sha256=inner,binary_sha256=a.sha(binary),files=len(f),scope='independently inspected archived Windows host evidence; no fresh host run',extended_rate_evidence='10 extended cases in packaged transcript' if shuttle else None,unchanged_previous_files=unchanged,sdk_automation_cases=cases,sdk_probe_sha256=a.sha(f['sdk-probe.txt']))
        cat['plugins'][cat['plugins'].index(prior)]=entry; updates.append(dict(name=name,artifact=artifact,old_artifact=prior['artifact'],binary_sha256=entry['binary_sha256'],probe_sha256=entry['sdk_probe_sha256'],automation_cases=cases,host_partitions=partitions,manifest=count,unchanged=unchanged,changed=changes,files=len(f),class_ids=len(ids),parameter_ids=len(params),presets=len(presets),wav=len(wav)))
        out={n:b for n,b in out.items() if not n.startswith(op)}; out.update({op+n:b for n,b in f.items()})
    a.need(updates[0]['probe_sha256']!=updates[1]['probe_sha256'],'cross-package contamination'); ids=[i for p in cat['plugins'] for i in p['class_ids']]; a.need(len(ids)==len(set(ids))==16,'class collision')
    for n in ('catalogue.json','README.md','SHA256SUMS'): out['Provenance/run051-'+n]=out[n]
    out.pop('SHA256SUMS'); cat.update(previous_distribution_sha256=BASE,shuttle_refresh=updates); out['catalogue.json']=(json.dumps(cat,indent=2,sort_keys=True)+'\n').encode(); out['refresh_shuttle.py']=pathlib.Path(__file__).read_bytes()
    out['README.md']=b'''# MHAC eight-plugin Windows x64 collection - Bell/Shuttle evidence refresh\n\nExtract the entire ZIP. Install the complete .vst3 bundles under Packages into your host VST3 scan directory (normally C:\\Program Files\\Common Files\\VST3); remove duplicate installed versions before rescanning. Orbit Lantern, Afterimage and Three Winters are instruments; the remaining five are effects. Standard .vstpreset files are host presets; custom states are not. Start with monitoring muted and increase cautiously. No autoplay or SPL claims.\n\nBell and Shuttle now use exact #633 commit 9f28b3f4; Shuttle contains all 16 SDK automation cases, including the 10 previously missing extended-rate cases. Original plugin presets, audio, prior catalogues and historical host evidence preserved. This is owner-review software, not scientific acceptance or a fresh eight-plugin host qualification. Original per-plugin instructions and licensing retained.\n\nRebuild: python refresh_shuttle.py INPUT_DIR OUTPUT.zip alongside assemble.py and extend.py, using the exact prior signal-refresh ZIP and pinned Actions ZIPs. Verify SHA256SUMS. Earlier README and manifest versions are under Provenance.\n'''
    out['SHA256SUMS']=''.join(f'{a.sha(b)}  {n}\n' for n,b in sorted(out.items())).encode()
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(out.items()):
            i=zipfile.ZipInfo(n,(2026,11,28,0,0,0)); i.compress_type=zipfile.ZIP_DEFLATED; i.external_attr=0o100644<<16; z.writestr(i,b,compresslevel=9)
    manifest(a.files(dest.read_bytes()),'SHA256SUMS'); print(json.dumps(dict(updates=updates,files=len(out),sha256=a.sha(dest.read_bytes())),indent=2))
if __name__=='__main__': main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
