#!/usr/bin/env python3
"""Offline, owner-only pinned package assembly; no host execution."""
import hashlib, io, json, pathlib, re, stat, struct, sys, wave, zipfile, array
PINS = [
 ('orbit',739,46022847311,15210786073,'72abe8179d1c8290d29769e623a401c5d4fcba7f','7773d5aa091ebc34087563d8812f3048f97e6f0b3ca989dcf51f1d4525df60b1','93b51fee59c35588c8e3cc0d8ee691dd5399c3834d7ab75056eb4866d4f4a0d3','MHACOrbitLantern','0.3.1'),
 ('counterfactual',749,46018205199,15207530972,'1b1f6911fd869446a94d410408e88870204142c4','0469c67bea5be1ad3d03ce0dbae866d886c82143f0e82cdbfc22011b0f3b38b6','ed5540adaca7570da88bcfdbd6f2d15ec8b0df8617e6728d1e0e001934ed0d21','MHACCounterfactualResonator','0.2.0'),
 ('harmonic',749,46018205199,15207451185,'1b1f6911fd869446a94d410408e88870204142c4','56bd85930d4df21462c22d5ab4348fd9a67af459a1032e0179e9dd9d7002f3c6','384167054086822496f97f32714d84efb94c172bf617f2bf7311cf797716f54a','MHACHarmonicMemoryBank','0.2.0'),
 ('tracebell',633,45994220931,15195705883,'d996a0b8c457630e3d18a4b2a06393640f8d3fbf','fa74dd77708ab33537b0f69037ecc92f8236297ffc3f09580860d71fe82595c9','c36408772286a89314373a3126a878521df51b50dfa8e0a5e3fc8e70012ec327','MHACTraceBell','0.1.0'),
]
SDK='9fad9770f2ae8542ab1a548a68c1ad1ac690abe0'
LINKS=dict(zip('base cmake doc pluginterfaces public.sdk tutorials vstgui4'.split(), '3d2e82f8e6bff59c1d8b7a27491a29c2286b5206 de6e54eeaaab35b7145f5c32c279b5e892146e04 6d4737c9e70750056e731d88d49aa06eefc8a1a4 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c a3911a4615dabbfdfd9d181ee26b05c70c289a95 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34 76823bdbe286e4bdb9f79ab8986af5ce7202336c'.split()))
ROOT='https://github.com/techrote/MachineHumanAudioCybersemiotics'
def need(ok,msg):
 if not ok: raise ValueError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def files(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  need(len(z.infolist())<1000 and sum(x.file_size for x in z.infolist())<100_000_000,'ZIP bounds')
  out={}; seen=set()
  for x in z.infolist():
   n=x.filename; parts=n.split('/'); need(not x.is_dir() and all(p and p not in ('.','..') and not p.endswith((' ','.')) and not re.search(r'[\\<>:"|?*\x00-\x1f]',p) and not re.fullmatch(r'(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])',p.split('.')[0]) for p in parts),'unsafe path: '+n)
   need(n.casefold() not in seen and not stat.S_ISLNK(x.external_attr>>16),'duplicate/symlink');seen.add(n.casefold());out[n]=z.read(x)
  need(not z.testzip(),'CRC failure');return out
def pe(b):
 need(b[:2]==b'MZ','MZ'); o=struct.unpack_from('<I',b,60)[0];need(b[o:o+4]==b'PE\0\0' and struct.unpack_from('<H',b,o+4)[0]==0x8664 and struct.unpack_from('<H',b,o+24)[0]==0x20b and struct.unpack_from('<H',b,o+22)[0]&0x2000,'not AMD64 PE32+ DLL')
def preset(b,cid):
 need(len(b)>=56 and b[:4]==b'VST3' and struct.unpack_from('<I',b,4)[0]==1 and b[8:40].decode()==cid,'preset header/CID');o=struct.unpack_from('<Q',b,40)[0];need(48<=o<=len(b)-8 and b[o:o+4]==b'List','preset list');n=struct.unpack_from('<I',b,o+4)[0];need(0<n<=64 and o+8+20*n==len(b),'preset count');chunks=[]
 for i in range(n):
  tag,start,size=struct.unpack_from('<4sQQ',b,o+8+20*i);need(48<=start<=o and size<=o-start,'preset bounds');chunks.append((tag,start,start+size))
 need(sum(t==b'Comp' for t,_,_ in chunks)==1,'missing/duplicate component');return len(chunks)
def audio(b):
 with wave.open(io.BytesIO(b)) as w:
  c,s,r,n=w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes(); data=w.readframes(n);need(c in (1,2) and s==2 and 8000<=r<=192000 and len(data)==c*s*n and n>0,'PCM format');v=array.array('h');v.frombytes(data)
  if sys.byteorder!='little':v.byteswap()
  peak=max(map(abs,v));need(0<peak<32767,'silent or full-scale PCM');return dict(channels=c,rate=r,frames=n,peak=peak,sha256=sha(b))
def main(src,dest):
 out={}; receipts=[]; all_ids=set(); all_names=set()
 for key,pr,run,artifact,head,outer,inner,name,version in PINS:
  raw=(src/(key+'.zip')).read_bytes();need(sha(raw)==outer,'outer '+key);a=files(raw);need(len(a)==1,'outer count');inner_name,blob=next(iter(a.items()));need(sha(blob)==inner,'inner '+key);a=files(blob);prefix=name+'.vst3/Contents/';binary=a[prefix+'x86_64-win/'+name+'.vst3'];pe(binary)
  pins=dict(x.split('=',1) for x in a['BUILD-SOURCE.txt'].decode().splitlines());need(pins==dict(sdk=SDK,source=head),'source/sdk pins');links={}
  for line in a['SDK-GITLINKS.txt'].decode().splitlines():
   m=re.fullmatch(r' ([0-9a-f]{40}) (\S+) \(.*\)',line);need(m,'unclean SDK gitlink');links[m[2]]=m[1]
  need(links==LINKS,'SDK links');mi=json.loads(re.sub(r',\s*([}\]])',r'\1',a[prefix+'Resources/moduleinfo.json'].decode()));need(mi['Name']==name and mi['Version']==version and len(mi['Classes'])==2,'module identity');classes=mi['Classes'];ids=[x['CID'] for x in classes];need(all(re.fullmatch('[A-F0-9]{32}',x) for x in ids) and len(set(ids))==2 and not all_ids.intersection(ids) and name.casefold() not in all_names,'class/install collision');all_ids.update(ids);all_names.add(name.casefold());need(all(x['SDKVersion']=='VST 3.8.0' and x['Version']==version for x in classes),'class version');cid=next(x['CID'] for x in classes if x['Category']=='Audio Module Class')
  log=a['bank-validator.txt' if key=='harmonic' else 'validator.txt'].decode();need('Result: 47 tests passed, 0 tests failed' in log and not re.search(r'^\s*ERROR:',log,re.M) and all(x in log for x in ids),'validator transcript');params=re.findall(r'Parameter \d+ \(id=(\d+)\)',log);need(params and len(params)==len(set(params)),'parameter ID collision');presets={n:sha(b) for n,b in a.items() if n.endswith('.vstpreset') and preset(b,cid)};wav={n:audio(b) for n,b in a.items() if n.endswith('.wav')};need(wav and any('LICENSE' in n for n in a),'missing audio/license')
  receipts.append(dict(name=name,version=version,pr=pr,run=run,artifact=artifact,artifact_url=f'{ROOT}/actions/runs/{run}/artifacts/{artifact}',source=head,outer_sha256=outer,inner_sha256=inner,binary_sha256=sha(binary),class_ids=ids,parameter_ids=list(map(int,params)),standard_presets=presets,custom_state_files={n:sha(b) for n,b in a.items() if n.endswith(('.cr01','.hm01'))},audio=wav,validator_pass=47,validator_fail=0,files=len(a)))
  out.update({f'Packages/{name}/{n}':b for n,b in a.items()})
 out['catalogue.json']=(json.dumps(dict(sdk=SDK,gitlinks=LINKS,scope='offline archive inspection only; no new host load/render or listening',plugins=receipts),indent=2,sort_keys=True)+'\n').encode();out['assemble.py']=pathlib.Path(__file__).read_bytes();out['README.md']=b'''# MHAC Windows x64 owner review - catalogue increment\n\nExtract the archive. Copy each complete `.vst3` directory from `Packages/<plugin>/` to `C:\\Program Files\\Common Files\\VST3` (administrator rights may be needed), or a DAW-supported custom VST3 directory, then rescan. Retain all bundle contents. Orbit Lantern is an instrument; the others are effects. Load standard `.vstpreset` files via host preset functions where supported; `.cr01` and `.hm01` are custom state files, not interchangeable host presets. Follow the original per-plugin documentation. Start with monitoring muted, raise cautiously; original WAVs are unchanged and their measured digital peaks are listed in catalogue.json. No automatic playback, SPL or listening claims.\n\nThis is an incremental owner-review batch, not a replacement for ACCEL-038 or either Foundry catalogue. No new DAW tests, cross-plugin rendering or licensing grant. Original receipts and SDK licenses retained. Palimpsest Shuttle excluded because the exact-head validator emits explicit errors despite a 47/0 summary. Source files are referenced by immutable commit, not bundled. Rebuild this archive from the four original artifact ZIPs named orbit.zip, counterfactual.zip, harmonic.zip, tracebell.zip using python assemble.py INPUT_DIRECTORY OUTPUT.zip. Verify SHA256SUMS against extracted bytes.\n'''
 out['SHA256SUMS']=(''.join(f'{sha(b)}  {n}\n' for n,b in sorted(out.items()))).encode()
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,b in sorted(out.items()):
   i=zipfile.ZipInfo(n,(2026,11,27,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,b,compresslevel=9)
 print(json.dumps(dict(files=len(out),sha256=sha(dest.read_bytes()),plugins=[{k:r[k] for k in ('name','version','binary_sha256','class_ids','parameter_ids')}|dict(presets=len(r['standard_presets']),audio=len(r['audio']),max_peak=max(x['peak'] for x in r['audio'].values())) for r in receipts]),indent=2))
if __name__=='__main__': main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
