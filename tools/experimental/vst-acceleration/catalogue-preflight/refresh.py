"""ACCEL-038 plus five-plugin catalogue: pinned offline assembly, not host execution.
Run beside assemble.py and extend.py from the exact previous distribution.
"""
import itertools, json, pathlib, re, sys, zipfile
import assemble as a
from extend import manifest
BASE = 'b0cc07827ad5efea7796254314038d0cabf855e249bb424c4240d5e0f03a45fe'
HOST = 'e9300c376c22bc937899d2eed1e5045cf3be8b922c0c08cd88d202d69bc2c6d9'
ORBIT = dict(source='976a7fbabe79c92f2785564a5d9c27806d7de594', outer_sha256='f6039ee0bcf9cd6952611387479dd96b42a64feb8f3fb249b313f6a01085a4e4', inner_sha256='43584f11892ead091f36a7e65b8e420065f50ec6da5f960c42bcf3c9dce046c1')
def main(src, dest):
    raw = (src/'MHAC-VST-five-plugin-owner-review.zip').read_bytes()
    a.need(a.sha(raw)==BASE, 'previous distribution digest')
    out = a.files(raw); manifest(out,'SHA256SUMS')
    a.need(pathlib.Path(a.__file__).read_bytes()==out['assemble.py'] and pathlib.Path(sys.modules['extend'].__file__).read_bytes()==out['extend.py'], 'assembly dependency bytes')
    cat=json.loads(out['catalogue.json']); old=cat['plugins']; orbit=next(p for p in old if p['name']=='MHACOrbitLantern')
    raw=(src/'github-actions-artifact-15194909235.zip').read_bytes(); a.need(a.sha(raw)==HOST,'ACCEL-038 host pin')
    host=a.files(raw); session=json.loads(host['session/session.json'])
    a.need(session['complete'] and len(session['cases'])==14 and all(c['restore_error']==0 and c.get('partition_error',0)==0 for c in session['cases']), 'historical session receipt')
    out['Provenance/run047-catalogue.json']=out['catalogue.json']; out['Provenance/run047-SHA256SUMS']=out.pop('SHA256SUMS'); out['Provenance/run047-README.md']=out['README.md']
    for n,b in host.items():
        if n.startswith('session/'): out['ACCEL038/'+n]=b
    for key,name,artifact,meta in [('orbit','MHACOrbitLantern',15222539017,ORBIT),('afterimage','MHACAfterimage',15148180211,session['afterimage']),('winters','MHACThreeWinters',15156181930,session['winters']),('receipt','MHACReceiptFold',15145497011,session['receipt'])]:
        raw=(src/f'github-actions-artifact-{artifact}.zip').read_bytes(); a.need(a.sha(raw)==meta['outer_sha256'],'outer '+key)
        f=a.files(raw); a.need(len(f)==1,'nested count'); blob=next(iter(f.values())); a.need(a.sha(blob)==meta['inner_sha256'],'inner '+key); f=a.files(blob)
        prefix=name+'.vst3/Contents/'; binary=f[prefix+'x86_64-win/'+name+'.vst3']; a.pe(binary)
        a.need(dict(x.split('=',1) for x in f['BUILD-SOURCE.txt'].decode().splitlines())==dict(sdk=a.SDK,source=meta['source']),'source/sdk')
        links={}
        for line in f['SDK-GITLINKS.txt'].decode().splitlines():
            m=re.fullmatch(r' ([0-9a-f]{40}) (\S+) \(.*\)',line); a.need(m and m[2] not in links,'gitlinks'); links[m[2]]=m[1]
        a.need(links==a.LINKS,'SDK dependency pins')
        mi=json.loads(re.sub(r',\s*([}\]])',r'\1',f[prefix+'Resources/moduleinfo.json'].decode())); cl=mi['Classes']; ids=[c['CID'] for c in cl]; version=mi['Version']; cid=next(c['CID'] for c in cl if c['Category']=='Audio Module Class')
        a.need(mi['Name']==name and len(ids)==len(set(ids))==2 and all(re.fullmatch('[A-F0-9]{32}',i) for i in ids) and all(c['SDKVersion']=='VST 3.8.0' and c['Version']==version for c in cl),'class identity')
        log=f['validator.txt'].decode(); a.need('Result: 47 tests passed, 0 tests failed' in log and not re.search(r'^\s*ERROR:',log,re.M|re.I) and all(i in log for i in ids),'validator')
        params=list(map(int,re.findall(r'Parameter \d+ \(id=(\d+)\)',log))); a.need(params and len(set(params))==len(params),'parameter IDs')
        presets={n:a.sha(b) for n,b in f.items() if n.endswith('.vstpreset') and a.preset(b,cid)}; wav={n:a.audio(b) for n,b in f.items() if n.endswith('.wav')}; a.need('Steinberg-SDK-LICENSE.txt' in f and prefix+'Resources/LICENSE.txt' in f,'license')
        if key=='orbit':
            a.need(ids==orbit['class_ids'] and params==orbit['parameter_ids'] and presets==orbit['standard_presets'] and wav==orbit['audio'],'Orbit compatibility')
            replay=f['sdk-replay.txt'].decode(); cases=re.findall(r'^SDK_REPLAY rate=(\d+) channels=(\d+) identity=(\d+) format=(\d+) block=(\d+) frames=(\d+) max_error=0\s*$',replay,re.M)
            expected=set(itertools.product(('44100','48000','96000'),('1','2'),('0','1','2'),('0','1'),('127','1024')))
            a.need(len(cases)==72 and {c[:5] for c in cases}==expected and 'SDK_REPLAY_PASS cases=72' in replay and 'SDK_CONTROLLER_PASS encodings=3 parameters=5' in replay,'Orbit replay coverage')
            old.remove(orbit); out={n:b for n,b in out.items() if not n.startswith('Packages/'+name+'/')}
        else:
            a.need(a.sha(binary)==meta['binary_sha256'] and cid==meta.get('cid',meta.get('processor_cid')),'ACCEL038 binary/class pin')
        old.append(dict(name=name,version=version,artifact=artifact,source=meta['source'],outer_sha256=meta['outer_sha256'],inner_sha256=meta['inner_sha256'],binary_sha256=a.sha(binary),class_ids=ids,parameter_ids=params,standard_presets=presets,audio=wav,files=len(f),validator_pass=47,validator_fail=0,scope='archived Windows receipts; no new host execution'))
        out.update({'Packages/'+name+'/'+n:b for n,b in f.items()})
    ids=[i for p in old for i in p['class_ids']]; a.need(len(ids)==len(set(ids))==16 and len({p['name'].casefold() for p in old})==8,'catalogue collision')
    cat.update(scope='offline package verification only; historical session uses exact archived Afterimage, Three Winters and Receipt Fold; no eight-plugin chain test',accel038_host_sha256=HOST,previous_distribution_sha256=BASE)
    out['catalogue.json']=(json.dumps(cat,indent=2,sort_keys=True)+'\n').encode(); out['refresh.py']=pathlib.Path(__file__).read_bytes()
    out['README.md']=("# MHAC eight-plugin Windows x64 owner-review collection\n\nCopy complete .vst3 directories from Packages/<plugin>/ into C:\\Program Files\\Common Files\\VST3 or a host-supported custom path. Rescan; avoid duplicate versions. Start muted, then raise monitoring cautiously. No calibrated SPL or listening claim. Orbit Lantern, Afterimage and Three Winters are instruments; the remaining plugins are effects. Follow each original package's instructions. ACCEL038/session contains the original 48 kHz, 12 s four-track stems, MIDI, presets and reference mixes; historical session gains are already applied to stems. Trace Bell and other added plugins were not part of that session. No new eight-plugin host test, license grant or owner acceptance. Preserve original receipts and previous catalogue. Rebuild with python refresh.py INPUT_DIR OUTPUT.zip beside the pinned previous assemble.py and extend.py, using the previous distribution and five original Actions ZIPs. Verify SHA256SUMS.\n").encode()
    out['SHA256SUMS']=''.join(f'{a.sha(b)}  {n}\n' for n,b in sorted(out.items())).encode()
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(out.items()):
            i=zipfile.ZipInfo(n,(2026,11,27,0,0,0)); i.compress_type=zipfile.ZIP_DEFLATED; i.external_attr=0o100644<<16; z.writestr(i,b,compresslevel=9)
    manifest(a.files(dest.read_bytes()),'SHA256SUMS'); print(a.sha(dest.read_bytes()),len(out),[(p['name'],p['version'],len(p['parameter_ids']),len(p['standard_presets'])) for p in old])
if __name__=='__main__': main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
