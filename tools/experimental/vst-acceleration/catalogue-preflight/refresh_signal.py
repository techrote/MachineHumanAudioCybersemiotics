"""Pinned distribution update; archive audit, not new native Windows execution."""
import itertools,json,pathlib,re,sys,zipfile
import assemble as a
from extend import manifest
BASE='5592de05b6e2e46c00a9b2a247e2e8c5c64b4e5a23286fb1be72ee241a0c9bc1'
HEAD='b4e0641135f46fc1be3bffa4a995e33e9527d306'
RUN=46061613171
PINS=[('MHACHarmonicMemoryBank',15228973006,'33fd869fb32c620008e0a23d49710489fbb0e10970b8325a75c5fca75a8efe86','1b30d65509ec0278fe392b52b49ddcf5b4baee7e3ac93e18060b5912470bda72','bank-validator.txt'),('MHACCounterfactualResonator',15228688642,'b821fdd41052afc8c47674195fe644eb392cf722fbbd2acc2adc6550ca38690c','b0c862dac7a093ba5a0b84a527c9374e16666541a44e3766392b07a93071d52d','validator.txt')]
def audit_replay(log):
    pattern=r'^SDK_BANK_CASE rate=(\d+) band=(\d+) block=(\d+) reverse=(\d+) manual=(\d+) mono=(\d+) format=(\d+)\s*$'
    cases=re.findall(pattern,log,re.M)
    expected={(r,b,k,v,m,c,f) for (r,f),b,k,v,m,c in itertools.product([('48000','0'),('96000','1')],map(str,range(4)),['127','257'],['0','1'],['0','1'],['0','1'])}
    a.need(len(cases)==128 and set(cases)==expected,'SDK bank case matrix')
    a.need(len(re.findall(r'^SDK_BANK_BEGIN ',log,re.M))==128,'SDK bank begin count')
    a.need(re.findall(r'^SDK_BANK_REPLAY_PASS cases=128 checks=([1-9]\d*)\s*$',log,re.M)==['19977021'],'SDK replay final receipt')
    a.need(len(re.findall(r'^SDK_BANK_CONTROLLER_PASS parameters=42\s*$',log,re.M))==1,'controller receipt')
    return {'cases':len(cases),'controller_parameters':42,'reported_assertions':19977021,'scope':'archived SDK module replay, not fresh execution'}
def main(src,dest):
    raw=(src/'MHAC-VST-eight-plugin-owner-review.zip').read_bytes();a.need(a.sha(raw)==BASE,'base digest'); out=a.files(raw);manifest(out,'SHA256SUMS')
    a.need(pathlib.Path(a.__file__).read_bytes()==out['assemble.py'] and pathlib.Path(sys.modules['extend'].__file__).read_bytes()==out['extend.py'],'helper identities')
    cat=json.loads(out['catalogue.json']); old=cat['plugins']; updates=[]
    for name,artifact,outer,inner,logname in PINS:
        raw=(src/f'github-actions-artifact-{artifact}.zip').read_bytes();a.need(a.sha(raw)==outer,'outer digest'); z=a.files(raw);a.need(len(z)==1,'nested count');blob=next(iter(z.values()));a.need(a.sha(blob)==inner,'inner digest');f=a.files(blob)
        prior=next(p for p in old if p['name']==name); prefix=name+'.vst3/Contents/'; binary=f[prefix+'x86_64-win/'+name+'.vst3'];a.pe(binary)
        a.need(dict(x.split('=',1) for x in f['BUILD-SOURCE.txt'].decode('utf-8-sig').splitlines())==dict(sdk=a.SDK,source=HEAD),'source/sdk')
        links={}
        for line in f['SDK-GITLINKS.txt'].decode('utf-8-sig').splitlines():
            m=re.fullmatch(r' ([0-9a-f]{40}) (\S+) \(.*\)',line);a.need(m and m[2] not in links,'gitlinks');links[m[2]]=m[1]
        a.need(links==a.LINKS,'sdk gitlinks')
        mi=json.loads(re.sub(r',\s*([}\]])',r'\1',f[prefix+'Resources/moduleinfo.json'].decode('utf-8-sig'))); cl=mi['Classes'];ids=[c['CID'] for c in cl];cid=next(c['CID'] for c in cl if c['Category']=='Audio Module Class');a.need(mi['Name']==name and mi['Version']==prior['version'] and ids==prior['class_ids'] and len(set(ids))==2 and all(c['SDKVersion']=='VST 3.8.0' for c in cl),'module identity')
        log=f[logname].decode('utf-8-sig');a.need('Result: 47 tests passed, 0 tests failed' in log and 'ERROR:' not in log.upper() and all(i in log for i in ids),'validator'); params=list(map(int,re.findall(r'Parameter \d+ \(id=(\d+)\)',log)));a.need(params==prior['parameter_ids'],'parameter IDs')
        presets={n:a.sha(b) for n,b in f.items() if n.endswith('.vstpreset') and a.preset(b,cid)};states={n:a.sha(b) for n,b in f.items() if n.endswith(('.cr01','.hm01'))}; wav={n:a.audio(b) for n,b in f.items() if n.endswith('.wav')}; a.need(presets==prior['standard_presets'] and states==prior['custom_state_files'] and wav==prior['audio'],'preset/state/audio stability')
        a.need('Steinberg-SDK-LICENSE.txt' in f and prefix+'Resources/LICENSE.txt' in f,'licenses')
        op='Packages/'+name+'/'; previous={n[len(op):]:b for n,b in out.items() if n.startswith(op)}; changes=sorted(n for n in set(previous)|set(f) if previous.get(n)!=f.get(n)); replay=audit_replay(f['bank-sdk-replay.txt'].decode()) if name.endswith('Bank') else None
        entry=dict(prior,source=HEAD,run=RUN,artifact=artifact,artifact_url=f'{a.ROOT}/actions/runs/{RUN}/artifacts/{artifact}',outer_sha256=outer,inner_sha256=inner,binary_sha256=a.sha(binary),files=len(f),scope='independently inspected archive; no fresh host run');entry['sdk_replay']=replay
        old[old.index(prior)]=entry;updates.append(dict(name=name,previous_artifact=prior['artifact'],new_artifact=artifact,changed=changes,unchanged=len(set(previous)&set(f))-sum(n in previous and n in f for n in changes),class_ids=len(ids),parameter_ids=len(params),presets=len(presets),custom_states=len(states),audio=len(wav),sdk_replay=replay,binary_sha256=entry['binary_sha256']))
        out={n:b for n,b in out.items() if not n.startswith(op)};out.update({op+n:b for n,b in f.items()})
    ids=[i for p in old for i in p['class_ids']];a.need(len(ids)==len(set(ids))==16,'class collisions');out['Provenance/run049-catalogue.json']=out['catalogue.json'];out['Provenance/run049-SHA256SUMS']=out.pop('SHA256SUMS');out['Provenance/run049-README.md']=out['README.md'];cat.update(previous_distribution_sha256=BASE,signal_refresh=updates);out['catalogue.json']=(json.dumps(cat,indent=2,sort_keys=True)+'\n').encode();out['refresh_signal.py']=pathlib.Path(__file__).read_bytes();out['README.md']+=b'\nSignal refresh: Harmonic Memory Bank and Counterfactual Resonator updated to b4e0641; original historical host evidence is unchanged. Bank archived SDK replay covers 128 cases. No new native host execution. Rebuild using python refresh_signal.py INPUT_DIR OUTPUT.zip alongside assemble.py and extend.py, with the original eight-plugin ZIP and the two pinned Actions ZIPs.\n';out['SHA256SUMS']=''.join(f'{a.sha(b)}  {n}\n' for n,b in sorted(out.items())).encode()
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(out.items()):
            i=zipfile.ZipInfo(n,(2026,11,27,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,b,compresslevel=9)
    manifest(a.files(dest.read_bytes()),'SHA256SUMS');print(json.dumps(dict(updates=updates,files=len(out),sha256=a.sha(dest.read_bytes())),indent=2))
if __name__=='__main__':main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
