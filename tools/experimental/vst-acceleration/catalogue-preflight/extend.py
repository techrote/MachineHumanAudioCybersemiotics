#!/usr/bin/env python3
"""Frozen Run 045 distribution + exact repaired VST packages, offline only."""
import assemble as a
import json, pathlib, re, sys, zipfile, math
BASE='d58faf344111f0eb3882aa47f58e2e28baac84517f74e65b2f5e8df68c86ae29'
HEAD='ca1ed99b0c8632a2ed977289fa9d49929273be70'
RUN=46030439105
PINS=[('tracebell-15213334539.zip',15213334539,'438bd442336a041e873f7044cdd768549764c5613a807281aa7ab81a013a5dff','8e0349eaa3cfe6f524893db355503017da116369b147ed651f00c175257e3e94','MHACTraceBell',6,8,27),('shuttle-15213579147.zip',15213579147,'078c4060ea83e14fd8a067df269cc9034bd301de0bd5989a83956ccce0561b3a','5136d8d581ec057d725742b40e78b48aa4ed063152f7301fa6219046cf78b4b2','MHACPalimpsestShuttle',5,5,15)]
HOST='693419854d3d7141234f95a64e2d98f1feb050ec276ccdd187f47b64bfe84e7e'
def manifest(f,key):
 lines=f[key].decode().splitlines(); found={}
 for line in lines:
  digest,n=line.split(maxsplit=1); n=n.lstrip('*'); a.need(n not in found and n in f and digest.lower()==a.sha(f[n]),'manifest: '+n);found[n]=digest
 a.need(set(found)==set(f)-{key},'manifest coverage');return len(found)
def main(src,dest):
 raw=(src/'MHAC-VST-catalogue-increment-20261127.zip').read_bytes();a.need(a.sha(raw)==BASE,'base digest');out=a.files(raw);manifest(out,'SHA256SUMS');old=json.loads(out['catalogue.json']);out['Provenance/previous-catalogue.json']=out['catalogue.json'];out['Provenance/previous-SHA256SUMS']=out.pop('SHA256SUMS');out['Provenance/previous-README.md']=out['README.md'];receipts=old['plugins'];new=[]
 for fn,artifact,outer,inner,name,np,npre,ncases in PINS:
  raw=(src/fn).read_bytes();a.need(a.sha(raw)==outer,'outer');f=a.files(raw);a.need(len(f)==1,'nested count');blob=next(iter(f.values()));a.need(a.sha(blob)==inner,'inner');f=a.files(blob);prefix=name+'.vst3/Contents/';binary=f[prefix+'x86_64-win/'+name+'.vst3'];a.pe(binary)
  a.need(dict(x.split('=',1) for x in f['BUILD-SOURCE.txt'].decode().splitlines())==dict(sdk=a.SDK,source=HEAD),'source'); links={}
  for line in f['SDK-GITLINKS.txt'].decode().splitlines():
   m=re.fullmatch(r' ([0-9a-f]{40}) (\S+) \(.*\)',line);a.need(m and m[2] not in links,'gitlink');links[m[2]]=m[1]
  a.need(links==a.LINKS,'gitlinks');mi=json.loads(re.sub(r',\s*([}\]])',r'\1',f[prefix+'Resources/moduleinfo.json'].decode()));a.need(mi['Name']==name and mi['Version']=='0.1.0','name/version');cl=mi['Classes'];ids=[x['CID'] for x in cl];a.need(len(ids)==2 and len(set(ids))==2 and all(re.fullmatch('[A-F0-9]{32}',x) for x in ids) and all(x['SDKVersion']=='VST 3.8.0' and x['Version']=='0.1.0' for x in cl),'class');cid=next(x['CID'] for x in cl if x['Category']=='Audio Module Class')
  log=f['validator.txt'].decode();a.need('Result: 47 tests passed, 0 tests failed' in log and not re.search(r'^\s*ERROR:',log,re.M|re.I) and all(x in log for x in ids),'validator');params=list(map(int,re.findall(r'Parameter \d+ \(id=(\d+)\)',log)));a.need(len(set(params))==len(params)==np,'parameter count');presets={n:a.sha(b) for n,b in f.items() if n.endswith('.vstpreset') and a.preset(b,cid)};a.need(len(presets)==npre,'preset count');wav={n:a.audio(b) for n,b in f.items() if n.endswith('.wav')};a.need(wav and 'Steinberg-SDK-LICENSE.txt' in f and prefix+'Resources/LICENSE.txt' in f,'licensing/audio')
  cases=json.loads(f['host-receipt.json']);cases+=json.loads(f['preset-host-receipt.json']) if 'preset-host-receipt.json' in f else [];a.need(len(cases)==ncases and all(x.get('partition_error',x.get('partition_max_error'))==0 and 0<x['peak']<1 and math.isfinite(x['peak']) for x in cases),'host cases')
  prev=next((x for x in receipts if x['name']==name),None); unchanged=None
  if prev:
   a.need(prev['class_ids']==ids and prev['parameter_ids']==params and prev['standard_presets']==presets and prev['audio']==wav,'Trace Bell stability');p='Packages/'+name+'/';before={k[len(p):]:v for k,v in out.items() if k.startswith(p)};a.need(set(before)==set(f),'inventory');unchanged=sum(before[n]==f[n] for n in f);out={k:v for k,v in out.items() if not k.startswith(p)};receipts.remove(prev)
  if 'SHA256SUMS.txt' in f: manifest(f,'SHA256SUMS.txt')
  rec=dict(name=name,version='0.1.0',pr=633,run=RUN,artifact=artifact,artifact_url=f'{a.ROOT}/actions/runs/{RUN}/artifacts/{artifact}',source=HEAD,outer_sha256=outer,inner_sha256=inner,binary_sha256=a.sha(binary),class_ids=ids,parameter_ids=params,standard_presets=presets,custom_state_files={},audio=wav,validator_pass=47,validator_fail=0,files=len(f),host_partition_receipts=ncases,unchanged_previous_files=unchanged,extended_rate_evidence='Full hosted job log only; packaged sdk-probe.txt omits 10 cases' if 'Shuttle' in name else None);receipts.append(rec);new.append(rec);out.update({f'Packages/{name}/{n}':b for n,b in f.items()})
 ids=[i for x in receipts for i in x['class_ids']];a.need(len(set(ids))==len(ids)==10 and len({x['name'].casefold() for x in receipts})==5,'catalogue collision');raw=(src/'host-15213519440.zip').read_bytes();a.need(a.sha(raw)==HOST,'host evidence outer');host=a.files(raw);audio={n:a.audio(b) for n,b in host.items() if n.endswith('.wav')};reports={n:json.loads(b) for n,b in host.items() if n.endswith('.json')};a.need(len(audio)==25 and len(reports)==11,'host inventory');out.update({'HistoricalHostEvidence/'+n:b for n,b in host.items()});out['catalogue.json']=(json.dumps(dict(sdk=a.SDK,gitlinks=a.LINKS,scope='offline independent package verification; original hosted results only; not new host runs',plugins=receipts,previous_distribution_sha256=BASE,historical_host_artifact=15213519440,historical_host_sha256=HOST,historical_audio=audio,historical_receipts=list(reports)),indent=2,sort_keys=True)+'\n').encode();out['extend.py']=pathlib.Path(__file__).read_bytes();out['README.md']=('''# MHAC Windows x64 — five-plugin owner-review increment

Extract; copy only complete .vst3 bundle directories from Packages/<plugin>/ into C:\\Program Files\\Common Files\\VST3 or a host-supported custom directory. Rescan. Orbit Lantern is an instrument; the remaining four are effects. Standard .vstpreset files use host preset import; custom states are not host presets. Keep monitoring muted initially; original digital amplitudes are listed in catalogue.json. No SPL or listening claim.

This supersedes the four-plugin increment, not either Foundry catalogue or ACCEL-038. Trace Bell retains its class IDs, parameter IDs, presets and original WAV bytes but is a different build binary. Do not install both builds together. Original prior archive remains separate. Palimpsest Shuttle now passes the exact repaired hosted validator; sdk-probe.txt contains only standard-rate cases; the ten extended-rate cases are evidenced by the actual hosted job https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/46030439105/job/140612568815 . Previous failed build remains excluded. HistoricalHostEvidence contains original older-host experiments, not proof that these five current binaries work together. No new host execution or independent human review; HOLD for cross-plugin test and owner authorization. Licenses and original receipts preserved; no new license grant.

Rebuild: python extend.py INPUT_DIR OUTPUT.zip with the four exact ZIP inputs named in extend.py (previous increment, Trace Bell, Shuttle, host evidence). assemble.py is the original four-plugin assembly dependency. SHA256SUMS covers every other output file.
''').encode();out['SHA256SUMS']=''.join(f'{a.sha(b)}  {n}\n' for n,b in sorted(out.items())).encode()
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,b in sorted(out.items()):
   i=zipfile.ZipInfo(n,(2026,11,27,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,b,compresslevel=9)
 manifest(a.files(dest.read_bytes()),'SHA256SUMS');print(json.dumps(dict(sha256=a.sha(dest.read_bytes()),files=len(out),plugins=[{k:r[k] for k in ['name','binary_sha256','class_ids','parameter_ids']}|dict(presets=len(r['standard_presets']),wav=len(r['audio']),host=r.get('host_partition_receipts'),unchanged=r.get('unchanged_previous_files')) for r in receipts],historical_wav=len(audio),historical_receipts=len(reports)),indent=2))
if __name__=='__main__':main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
