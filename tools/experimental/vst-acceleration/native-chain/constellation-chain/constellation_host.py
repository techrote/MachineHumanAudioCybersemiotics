"""ACCEL-048: exact-package Windows host performance, not independent qualification."""
import argparse, hashlib, io, json, re, struct, wave, zipfile
from pathlib import Path
import numpy as np

SDK = '9fad9770f2ae8542ab1a548a68c1ad1ac690abe0'
# artifact, outer digest, source, module name, processor CID, class version, PE digest
PINS = (
    (15249403545,'46355787386a4f3347bc3ab1c389337e2743b521315afe2221f7e1e72d61529c','646d1f4dadd4ded55b3c4f681e94856923611445','MHACOrbitLantern','24C15B793B8C4F4B98275F233EE969C4','0.4.0','fc064822aaf9b48e8df762eae0d394606d0bb9ff4107b84bd909e8a59f98e497'),
    (15251347207,'c6a3d5d969ae80527f2da415fdc809b1b177e347cfc745415fad9a3cc0c12047','b858c94f165dcc2c59e193b51e5e6a73de96cbfc','MHACHarmonicMemoryBank','AE00577BADF94D9C8F2FB9D04991475C','0.3.0','e8c469deed7cffe65b77c2e4261e5e8561d90f932f7c75832087fa35a64f68c9'),
    (15248002499,'369ec7afe0163626fd4d13c06f469984547e04f5f0b5fe52de3c4f3a45295217','b5f509eb5c857dc6e411a7718bdc40dfa09bb0ad','MHACPalimpsestShuttle','58F3C28ABA5142D1AF75DF83173B962E','0.2.0','fe2caece775dcf76b65fcc24082e284c96b487580d16652581e3973d9df5e59b'),
)
GITLINKS = dict(base='3d2e82f8e6bff59c1d8b7a27491a29c2286b5206',cmake='de6e54eeaaab35b7145f5c32c279b5e892146e04',doc='6d4737c9e70750056e731d88d49aa06eefc8a1a4',pluginterfaces='31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c',tutorials='33b73dfbb87f3fde3bce8c0a10cae934dc66ad34',vstgui4='76823bdbe286e4bdb9f79ab8986af5ce7202336c',**{'public.sdk':'a3911a4615dabbfdfd9d181ee26b05c70c289a95'})
MODES = (('persistent',0,0,1000),('count',4,0,1000),('energy',4,1,1000),('full',16,1,1000),('aligned',4,1,0))
def require(ok, why):
    if not ok: raise ValueError(why)
def sha(x): return hashlib.sha256(x).hexdigest()
def extract(path, pin, out):
    aid,digest,source,name,cid,version,binary=pin
    raw=path.read_bytes(); require(sha(raw)==digest,'outer archive digest '+name)
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        expected=name+'-Windows-x64.zip'
        require(outer.namelist()==[expected] and outer.testzip() is None,'outer inventory '+name)
        with zipfile.ZipFile(io.BytesIO(outer.read(expected))) as inner:
            require(inner.testzip() is None,'inner CRC '+name)
            receipt=dict(x.split('=',1) for x in inner.read('BUILD-SOURCE.txt').decode('utf-8-sig').splitlines())
            require(receipt==dict(sdk=SDK,source=source),'source receipt '+name)
            links=[x.split() for x in inner.read('SDK-GITLINKS.txt').decode('utf-8-sig').splitlines()]
            require(len(links)==7 and {x[1]:x[0] for x in links}==GITLINKS,'SDK gitlinks '+name)
            bundle=name+'.vst3'; rel=bundle+'/Contents/x86_64-win/'+bundle
            pe=inner.read(rel); require(sha(pe)==binary and pe[:2]==b'MZ','binary digest '+name)
            offset=struct.unpack_from('<I',pe,60)[0]
            require(pe[offset:offset+6]==b'PE\0\0\x64\x86','PE x64 '+name)
            info=json.loads(re.sub(r',\s*([}\]])',r'\1',inner.read(bundle+'/Contents/Resources/moduleinfo.json').decode('utf-8-sig')))
            classes=[c for c in info['Classes'] if c['Category']=='Audio Module Class']
            require(len(classes)==1 and classes[0]['CID']==cid and classes[0]['Version']==version and classes[0]['SDKVersion']=='VST 3.8.0','class identity '+name)
            # Only the pinned bundle is extracted; no path traversal or duplicate aliases.
            seen=set()
            for n in inner.namelist():
                if not n.startswith(bundle+'/') or n.endswith('/'): continue
                parts=n.split('/'); require(all(p and p not in ('.','..') and ':' not in p and '\\' not in p and not p.endswith((' ','.')) for p in parts),'unsafe bundle path')
                require(n.casefold() not in seen,'duplicate bundle path');seen.add(n.casefold())
                dst=out/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(inner.read(n))
    return out/rel,dict(artifact=aid,source=source,archive_sha256=digest,binary_sha256=binary,class_version=version,module_version=info['Version'],metadata_mismatch=info['Version']!=version)
def preset(cid,state):
    return struct.pack('<4si32sq',b'VST3',1,cid.encode(),48+len(state))+state+struct.pack('<4si4sqq',b'List',1,b'Comp',48,len(state))
def component(raw,cid):
    magic,v,c,pos=struct.unpack_from('<4si32sq',raw)
    require((magic,v,c)==(b'VST3',1,cid.encode()) and 48<=pos<=len(raw)-8,'preset header')
    tag,n=struct.unpack_from('<4si',raw,pos);require(tag==b'List' and 1<=n<=32 and pos+8+20*n==len(raw),'preset list')
    chunks={}
    for i in range(n):
        k,o,s=struct.unpack_from('<4sqq',raw,pos+8+20*i)
        require(k not in chunks and 48<=o<=pos and 0<=s<=pos-o,'preset extent');chunks[k]=raw[o:o+s]
    require(b'Comp' in chunks,'component missing');return chunks[b'Comp']
def orbit_state(): return struct.pack('<4s3HB3H',b'OL04',180,650,88,2,700,900,1400)
def bank_state(budget,energy,capture):
    return struct.pack('<4sHB',b'HM02',1000,0)+b''.join(struct.pack('<4HB',hz,800,1000,0,capture) for hz in (110,165,220,330))+bytes((budget,energy))
def shuttle_state(stagger):
    return struct.pack('<4s4HB',b'PS02' if stagger else b'PS01',650,850,200,400,0)+(struct.pack('<H',stagger) if stagger else b'')
def verify(p,cid,state): require(component(p.preset_data,cid)==state,'component state mismatch '+cid)
def checked(x,n):
    require(x.shape==(2,n) and np.isfinite(x).all() and np.max(np.abs(x))<=1,'audio shape/finite/bounds');return x
def set_raw(p,key,val):
    q=p.parameters[key];q.raw_value=val;require(abs(q.raw_value-val)<1e-5,'host parameter '+key)
def segmented(p,x,rate,block,events):
    # Event boundaries are explicit separate calls, never reset the running effect.
    chunks=[];start=0
    for end,changes in events+[(x.shape[1],[])]:
        require(start<=end<=x.shape[1],'event extent')
        if end>start: chunks.append(checked(p.process(x[:,start:end].copy(),rate,buffer_size=block,reset=False),end-start))
        for key,value in changes: set_raw(p,key,value)
        start=end
    return np.concatenate(chunks,axis=1)
def metrics(x):
    return dict(rms=float(np.sqrt(np.mean(x.astype(np.float64)**2))),side=float(np.sqrt(np.mean(((x[0].astype(np.float64)-x[1])*.5)**2))),peak=float(np.max(np.abs(x))))
def render(paths,rate,block,mode,load):
    _,budget,energy,stagger=mode
    o,b,s=[load(str(p)) for p in paths]; cids=[p[4] for p in PINS]
    require(o.is_instrument and b.is_effect and s.is_effect,'host roles')
    # Initialize host processing, then admit exact component states on silence.
    o.process([],duration=.1,sample_rate=rate,num_channels=2,buffer_size=block,reset=True)
    for p in (b,s): p.process(np.zeros((2,1024),np.float32),rate,buffer_size=block,reset=True)
    for p,cid,state in zip((o,b,s),cids,(orbit_state(),bank_state(budget,energy,1),shuttle_state(0))): p.preset_data=preset(cid,state)
    o.process([],duration=.4,sample_rate=rate,num_channels=2,buffer_size=block,reset=False)
    for p in (b,s): p.process(np.zeros((2,rate*2//5),np.float32),rate,buffer_size=block,reset=False)
    for p,cid,state in zip((o,b,s),cids,(orbit_state(),bank_state(budget,energy,1),shuttle_state(0))): verify(p,cid,state)
    midi=[(bytes((status,n,v)),t) for status,t,notes,v in ((144,0,(45,52,59,66),102),(128,.75,(45,52,59,66),0),(144,3,(69,),89),(128,3.5,(69,),0)) for n in notes]
    dry=checked(o.process(midi,duration=5.,sample_rate=rate,num_channels=2,buffer_size=block,reset=False),5*rate)
    verify(o,cids[0],orbit_state());require(np.max(np.abs(dry))>.001 and np.max(np.abs(dry[:,-rate//10:]))<1e-6,'Orbit activity/release')
    send=np.clip(dry*8.,-.9,.9).astype(np.float32)
    bank=segmented(b,send,rate,block,[(rate,[(f'b{i}_capture',0.) for i in range(1,5)]),(2*rate,[('admit_budgeted_erase',1.)]),(2*rate+1,[('admit_budgeted_erase',0.)])])
    verify(b,cids[1],bank_state(budget,energy,0))
    wet=segmented(s,bank,rate,block,[(2*rate,[('stereo_stagger',stagger/1000.)])]);verify(s,cids[2],shuttle_state(stagger))
    output=checked(dry*.4+wet*.35,5*rate)
    if budget==16: require(np.max(np.abs(bank[:,rate*5//2:]))<1e-7,'full erasure residual')
    return dry,bank,output
def save_wav(path,x,rate):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes(np.rint(x.T*.5*32767).astype('<i2').tobytes())
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('orbit','bank','shuttle','out'): p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--preflight-only',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    report=dict(scope=__doc__,packages=[],cases=[],status='started')
    def persist(): (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        paths=[]
        for path,pin in zip((a.orbit,a.bank,a.shuttle),PINS):
            module,row=extract(path,pin,a.out/'modules');paths.append(module);report['packages'].append(row);persist()
        if a.preflight_only: report['status']='preflight-only';return
        from pedalboard import load_plugin
        for rate in (44100,48000,96000):
            results={}
            for mode in MODES:
                name=mode[0];row=dict(rate=rate,mode=name,status='started');report['cases'].append(row);persist()
                x=render(paths,rate,257,mode,load_plugin);y=render(paths,rate,1024,mode,load_plugin)
                errors=[float(np.max(np.abs(u-v))) for u,v in zip(x,y)];row['partition_errors']=errors;persist()
                require(max(errors)<1e-5,'partition mismatch '+name)
                results[name]=x;row['window']=metrics(x[2][:,rate*5//2:rate*3]);row['status']='pass';persist()
                if rate==48000: save_wav(a.out/(name+'.wav'),x[2],rate)
            require(np.max(np.abs(results['persistent'][1][:,rate*5//2:rate*3]))>.001,'persistent bank silent')
            require(np.max(np.abs(results['energy'][2]-results['aligned'][2]))>1e-4,'missing stagger contrast')
            require(np.max(np.abs(results['persistent'][2]-results['full'][2]))>1e-4,'missing erasure contrast')
        report['status']='pass';print('CONSTELLATION_HOST_PASS cases=15 renders=30')
    except Exception as exc: report['status']='fail';report['error']=repr(exc);raise
    finally: persist()
if __name__=='__main__': main()
