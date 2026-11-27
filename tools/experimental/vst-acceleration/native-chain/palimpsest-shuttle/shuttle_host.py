"""ACCEL-040: PS01 presets and actual host render, no DAW-scanning claim."""
import argparse, hashlib, json, struct, wave
from pathlib import Path
CID=b'58F3C28ABA5142D1AF75DF83173B962E'
BANK=(('01 Forward',(600,0,350,0,0)),('02 Mirror',(700,1000,0,0,0)),
      ('03 Shuttle',(750,850,700,1000,0)),('04 Fractured Memory',(500,550,950,500,0)),
      ('05 Dry',(350,750,250,500,1)))
H=struct.Struct('<4si32sq')
L=struct.Struct('<4si')
E=struct.Struct('<4sqq')
S=struct.Struct('<4s4HB')
def state(v):
    if len(v)!=5 or any(type(x)!=int or not 0<=x<=1000 for x in v[:4]) or v[4] not in (0,1):
        raise ValueError('patch')
    return S.pack(b'PS01',*v)
def preset(v):
    b=state(v)
    return H.pack(b'VST3',1,CID,H.size+len(b))+b+L.pack(b'List',1)+E.pack(b'Comp',H.size,len(b))
def component(raw):
    magic,ver,cid,pos=H.unpack_from(raw)
    assert (magic,ver,cid)==(b'VST3',1,CID)
    tag,n=L.unpack_from(raw,pos)
    assert tag==b'List' and 1<=n<=32 and pos+L.size+n*E.size==len(raw)
    chunks={}
    for i in range(n):
        key,start,size=E.unpack_from(raw,pos+L.size+i*E.size)
        assert key not in chunks and H.size<=start and 0<=size and start+size<=pos
        chunks[key]=raw[start:start+size]
    b=chunks[b'Comp']
    sig,*v=S.unpack(b)
    assert sig==b'PS01' and state(v)==b
    return b
def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--module');args=a.parse_args()
    dest=args.out/'Presets';dest.mkdir(parents=True,exist_ok=True)
    for name,v in BANK:
        raw=preset(v);assert component(raw)==state(v)
        (dest/(name+'.vstpreset')).write_bytes(raw)
    assert len({preset(v) for _,v in BANK})==len(BANK)
    if not args.module:return
    import numpy as np
    from pedalboard import load_plugin
    rows=[]
    for rate in (44100,48000,96000):
        t=np.arange(rate*2)/rate
        dry=np.zeros((2,len(t)),np.float32)
        for at,f in ((0,173),(.2,257),(.45,391)):
            u=t-at;pulse=np.where((u>=0)&(u<.12),np.exp(-35*np.maximum(u,0)),0)
            dry[0]+=(.08*pulse*np.cos(2*np.pi*f*u)).astype(np.float32)
            dry[1]+=(.055*pulse*np.cos(2*np.pi*(f+31)*u)).astype(np.float32)
        signatures=set()
        for name,v in BANK:
            outputs=[]
            for block in (127,1024):
                p=load_plugin(args.module)
                p.process(np.zeros((2,1024),np.float32),rate,buffer_size=block,reset=True)
                p.preset_data=preset(v)
                assert component(p.preset_data)==state(v)
                p.process(np.zeros((2,rate//10),np.float32),rate,buffer_size=block,reset=False)
                wet=p.process(dry.copy(),rate,buffer_size=block,reset=False)
                assert component(p.preset_data)==state(v)
                assert wet.shape==dry.shape and np.isfinite(wet).all() and np.max(np.abs(wet))<=1
                if v[4]:assert np.array_equal(wet,dry)
                else:assert np.max(np.abs(wet-dry))>1e-4
                outputs.append(wet)
            error=float(np.max(np.abs(outputs[0]-outputs[1])))
            assert error<1e-5,(name,rate,error)
            wet=outputs[0];signatures.add(hashlib.sha256(wet.tobytes()).hexdigest())
            rows.append(dict(name=name,rate=rate,partition_error=error,peak=float(np.max(np.abs(wet)))))
            if rate==48000:
                with wave.open(str(args.out/(name+'.wav')),'wb') as w:
                    w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate)
                    w.writeframes(np.rint(wet.T*.5*32767).astype('<i2').tobytes())
        assert len(signatures)==len(BANK)
    (args.out/'host-receipt.json').write_text(json.dumps(rows,indent=2))
    print('SHUTTLE_HOST_PASS 30 renders; 15 partition comparisons')
if __name__=='__main__':main()
