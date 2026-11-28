"""Bounded exact-checkout Windows collection; never relabel historical binaries."""
import argparse, hashlib, io, json, os, re, shutil, struct, subprocess, sys, time, urllib.request, urllib.error, wave, zipfile
from pathlib import Path, PurePosixPath
HERE = Path(__file__).resolve().parent
CAT = json.loads((HERE / "catalogue.json").read_text(encoding="utf-8"))
def require(condition, message):
    if not condition:
        raise ValueError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def read_json(data):
    # SDK moduleinfo has trailing commas.
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", data.decode("utf-8-sig")))
def members(z):
    seen = set()
    require(len(z.infolist()) <= 2048 and sum(x.file_size for x in z.infolist()) <= 128*1024**2, "archive limit")
    for x in z.infolist():
        n=x.filename; p=PurePosixPath(n)
        require(not p.is_absolute() and "\\" not in n and all(s not in ("", ".", "..") and not s.endswith((" ",".")) and not re.search(r'[<>:"|?*\x00-\x1f]',s) and not re.fullmatch(r"(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?",s) for s in n.rstrip("/").split("/")), "unsafe path: "+n)
        require(n.rstrip("/").casefold() not in seen and ((x.external_attr>>16)&0o170000)!=0o120000, "collision/symlink: "+n)
        seen.add(n.rstrip("/").casefold())
    require(z.testzip() is None,"CRC")
    return [x.filename for x in z.infolist() if not x.is_dir()]
def preset(data,cid):
    require(len(data)>=56 and data[:4]==b"VST3" and struct.unpack_from("<I",data,4)[0]==1 and data[8:40].decode("ascii").upper()==cid,"preset identity")
    off=struct.unpack_from("<Q",data,40)[0]
    require(48<=off<=len(data)-8 and data[off:off+4]==b"List","preset list offset")
    count=struct.unpack_from("<I",data,off+4)[0]
    require(0<count<=64 and off+8+20*count==len(data),"preset list bounds")
    chunks=[]; kinds=set()
    for i in range(count):
        key,a,n=struct.unpack_from("<4sQQ",data,off+8+i*20)
        require(key not in kinds and 48<=a<=off and n<=off-a,"preset chunk")
        kinds.add(key); chunks.append((a,a+n))
    require(b"Comp" in kinds and all(a[1]<=b[0] for a,b in zip(sorted(chunks),sorted(chunks)[1:])),"preset missing component/overlap")
def probe_receipt(z,p):
    b=p["bundle"]
    if b=="MHACPalimpsestShuttle.vst3":
        s=z.read("sdk-probe.txt").decode("utf-8-sig")
        rows=re.findall(r"^SDK_AUTOMATION (.*)$",s,re.M)
        require(len(rows)==16 and len(set(rows))==16 and "SDK_EXTENDED_RATE_PASS automation_cases=10" in s and "SDK_STATE_PASS" in s and "SDK_PROBE_PASS automation_cases=6" in s,"Shuttle transcript contamination")
    elif b=="MHACTraceBell.vst3":
        s=z.read("sdk-probe.txt").decode("utf-8-sig")
        require(len(re.findall(r"^SDK_AUTOMATION ",s,re.M))==6 and "SDK_PROBE_PASS automation_cases=6" in s,"Trace Bell probe")
    elif b=="MHACOrbitLantern.vst3":
        s=z.read("sdk-replay.txt").decode("utf-8-sig")
        rows=re.findall(r"^SDK_REPLAY (.*)$",s,re.M)
        require(len(rows)==144 and len(set(rows))==144 and "SDK_REPLAY_PASS cases=144" in s,"Orbit replay")
    elif b=="MHACHarmonicMemoryBank.vst3":
        s=z.read("bank-sdk-replay.txt").decode("utf-8-sig")
        rows=re.findall(r"^SDK_BANK_CASE (.*)$",s,re.M)
        require(len(rows)==128 and len(set(rows))==128 and "SDK_BANK_REPLAY_PASS cases=128" in s,"Bank replay")
def audit(p,raw,source,digest,out=None):
    require(sha(raw)==digest,"outer SHA-256")
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        names=members(outer)
        require(names==[p["artifact"]+".zip"],"unexpected outer archive")
        inner=outer.read(names[0])
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        names=members(z); bundle=p["bundle"]
        receipt=dict(x.split("=",1) for x in z.read("BUILD-SOURCE.txt").decode("utf-8-sig").splitlines() if x)
        require(receipt=={"sdk":CAT["sdk"]["root"],"source":source},"source/SDK identity")
        links={}
        for line in z.read("SDK-GITLINKS.txt").decode("utf-8-sig").splitlines():
            m=re.fullmatch(r" ([a-f0-9]{40}) (\S+)(?: .*)?",line)
            require(m is not None and m[2] not in links,"unclean or duplicate SDK submodule")
            links[m[2]]=m[1]
        require(links==CAT["sdk"]["gitlinks"],"SDK gitlinks")
        require("Steinberg-SDK-LICENSE.txt" in names,"SDK license")
        dll=z.read(bundle+"/Contents/x86_64-win/"+bundle)
        require(dll[:2]==b"MZ","MZ")
        pe=struct.unpack_from("<I",dll,60)[0]
        require(dll[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",dll,pe+4)[0]==0x8664 and struct.unpack_from("<H",dll,pe+24)[0]==0x20b and struct.unpack_from("<H",dll,pe+22)[0]&0x2000,"AMD64 PE32+ DLL")
        module=read_json(z.read(bundle+"/Contents/Resources/moduleinfo.json"))
        require(module["Version"]==p["bundle_version"] and module["Name"]==bundle[:-5],"bundle metadata")
        require(len(module["Classes"])==2 and {x["Category"]:x["CID"] for x in module["Classes"]}==p["classes"] and all(x["Version"]==p["version"] and x["SDKVersion"]=="VST 3.8.0" for x in module["Classes"]),"class identity/version")
        log=z.read(p["validator"]).decode("utf-8-sig")
        require(re.findall(r"Result: (\d+) tests passed, (\d+) tests failed",log)==[("47","0")] and not re.search(r"(?im)^\s*(?:Info:\s*)?ERROR:",log),"validator errors")
        ids=sorted({int(i) for i in re.findall(r"Parameter \d+ \(id=(\d+)\)",log)})
        require(ids==sorted(p["parameter_ids"]),"parameter IDs "+str(ids))
        probe_receipt(z,p)
        counts={"presets":0,"custom_states":0,"audio":0}
        for n in names:
            data=z.read(n); suffix=Path(n).suffix.lower()
            if n.startswith(bundle+"/"): dest=Path("VST3")/p["kind"]/n
            elif suffix==".vstpreset":
                preset(data,p["classes"]["Audio Module Class"]); counts["presets"]+=1
                dest=Path("Presets")/bundle/n
            elif suffix in (".hm01",".cr01"):
                counts["custom_states"]+=1; dest=Path("CustomStates")/bundle/n
            elif suffix==".wav":
                with wave.open(io.BytesIO(data),"rb") as w: require(w.getnframes()>0 and w.getnchannels()>0,"empty WAV")
                counts["audio"]+=1; dest=Path("Audio")/p["kind"]/bundle/n
            elif "LICENSE" in n.upper(): dest=Path("Licenses")/bundle/n
            else: dest=Path("Qualification")/bundle/n
            if out is not None:
                path=out/dest; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
        return {"bundle":bundle,"kind":p["kind"],"name":p["name"],"source":source,"outer_sha256":digest,"binary_sha256":sha(dll),"classes":p["classes"],"parameters":ids,"version":p["version"],"bundle_version":p["bundle_version"],"validator":{"pass":47,"fail":0},**counts}
class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        new=super().redirect_request(req,fp,code,msg,headers,newurl)
        if new and urllib.parse.urlsplit(newurl).netloc!=urllib.parse.urlsplit(req.full_url).netloc:
            new.remove_header("Authorization")
        return new
def api(path,raw=False):
    url="https://api.github.com/repos/"+os.environ["GITHUB_REPOSITORY"]+path
    req=urllib.request.Request(url,headers={"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.build_opener(SafeRedirect()).open(req,timeout=60) as resp:
        data=resp.read(128*1024**2+1)
    require(len(data)<=128*1024**2,"HTTP response limit")
    return data if raw else json.loads(data)
def collect(source,event,out):
    require(re.fullmatch("[0-9a-f]{40}",source) and subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()==source,"exact checkout")
    for s in CAT["snapshots"]:
        require(subprocess.check_output(["git","rev-parse",source+":"+s["path"]],text=True).strip()==s["tree"],"frozen tree changed: "+s["path"])
    workflows={s["pr"]:s["release_workflow"] for s in CAT["snapshots"] if s["release_workflow"]}
    pending=set(workflows.values()); runs={}; deadline=time.monotonic()+2400
    while pending:
        for workflow in sorted(pending):
            data=api("/actions/workflows/"+workflow+"/runs?head_sha="+source+"&event="+event+"&per_page=30")
            exact=[x for x in data["workflow_runs"] if x["head_sha"]==source and x["event"]==event]
            if not exact: continue
            run=max(exact,key=lambda x:x["id"])
            if run["status"]!="completed": continue
            require(run["conclusion"]=="success","build failed: "+workflow+" "+str(run["id"]))
            runs[workflow]=run["id"]; pending.remove(workflow)
        if pending:
            require(time.monotonic()<deadline,"timed out: "+str(sorted(pending)))
            time.sleep(30)
    out.mkdir(parents=True,exist_ok=False); reports=[]
    for p in CAT["plugins"]:
        rid=runs[workflows[p["pr"]]]
        artifacts=api("/actions/runs/"+str(rid)+"/artifacts?per_page=100")["artifacts"]
        matches=[x for x in artifacts if x["name"]==p["artifact"] and not x["expired"]]
        require(len(matches)==1,"artifact missing/ambiguous "+p["artifact"])
        a=matches[0]; require(a["digest"].startswith("sha256:"),"missing published digest")
        raw=api("/actions/artifacts/"+str(a["id"])+"/zip",raw=True)
        require(len(raw)==a["size_in_bytes"],"artifact size")
        reports.append({**audit(p,raw,source,a["digest"][7:],out),"run":rid,"artifact_id":a["id"]})
    cids=[c for p in reports for c in p["classes"].values()]
    require(len(cids)==len(set(cids))==32,"cross-plugin class collision")
    cat=out/"Catalogue"; cat.mkdir()
    (cat/"catalogue.json").write_text(json.dumps({"source":source,"event":event,"qualification_scope":"exact-checkout Windows candidate; independent review and owner DAW audition separate","plugins":reports},indent=2)+"\n",encoding="utf-8")
    shutil.copyfile(HERE/"catalogue.json",cat/"source-inventory.json")
    (out/"README.md").write_text("# MHAC VST3 collection\n\nSource: "+source+"\n\nBuild event: "+event+"\n\nCandidate software qualification only; no scientific acceptance or physical listening claim.\n",encoding="utf-8")
    (out/"INSTALL.md").write_text("Copy each complete .vst3 directory from VST3/Instruments or VST3/Effects into the Windows VST3 directory (normally C:/Program Files/Common Files/VST3). Do not copy only the DLL. Remove conflicting prior versions first after backing up sessions. Rescan your DAW. Original presets and custom states are separate. Start at low monitoring gain; no acoustic calibration. See Catalogue and Qualification for precise version and host limitations.\n",encoding="utf-8")
def finish(out,archive):
    require((out/"Qualification"/"combined-host.json").is_file(),"missing fresh combined host qualification")
    require(json.loads((out/"Qualification"/"combined-host.json").read_text())["status"]=="pass","host qualification failed")
    files=sorted(p for p in out.rglob("*") if p.is_file())
    (out/"SHA256SUMS").write_text("".join(sha(p.read_bytes())+"  "+p.relative_to(out).as_posix()+"\n" for p in files),encoding="utf-8")
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(p for p in out.rglob("*") if p.is_file()):
            info=zipfile.ZipInfo("MHAC-VST3/"+p.relative_to(out).as_posix(),date_time=(2020,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None,"distribution CRC")
        expected={n:dig for dig,n in (x.split("  ",1) for x in z.read("MHAC-VST3/SHA256SUMS").decode().splitlines())}
        require(set(z.namelist())=={"MHAC-VST3/"+n for n in expected}|{"MHAC-VST3/SHA256SUMS"},"distribution inventory")
        for n,dig in expected.items(): require(sha(z.read("MHAC-VST3/"+n))==dig,"distribution member hash "+n)
    Path(str(archive)+".sha256").write_text(sha(archive.read_bytes())+"  "+archive.name+"\n")
def historical(directory):
    results=[]
    for p in CAT["plugins"]:
        h=p["historical"]; raw=(directory/("github-actions-artifact-"+str(h["artifact_id"])+".zip")).read_bytes()
        results.append(audit(p,raw,h["source"],h["sha256"]))
    require(len({c for p in results for c in p["classes"].values()})==32,"class collision")
    print(json.dumps({"scope":"historical static package audit, not integrated build","plugins":results},indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("mode",choices=["collect","finish","historical"]); a.add_argument("directory",type=Path); a.add_argument("--source"); a.add_argument("--event"); a.add_argument("--archive",type=Path); x=a.parse_args()
    if x.mode=="collect": collect(x.source,x.event,x.directory)
    elif x.mode=="finish": finish(x.directory,x.archive)
    else: historical(x.directory)
