"""Package this local audit and verify every member. No network or repository tests.
Usage: PYTHONDONTWRITEBYTECODE=1 python scripts/package_packet.py [packet_root] [output_zip]
"""
from pathlib import Path
import datetime, hashlib, json, sys, zipfile
from verify_packet import run

def package(root: Path, archive: Path) -> dict:
    root=root.resolve();archive=archive.resolve()
    if archive.is_relative_to(root): raise ValueError('Archive must be outside packet directory')
    files=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS')
    (root/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in files),encoding='utf-8')
    qa=run(root)
    files=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    top='MHAC_R002_chunk1C1/'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:z.write(p,top+p.relative_to(root).as_posix())
    with zipfile.ZipFile(archive) as z:
        expected={top+p.relative_to(root).as_posix():p for p in files}
        if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(expected):raise ValueError('ZIP inventory')
        if z.testzip() is not None:raise ValueError('ZIP CRC')
        for name,p in expected.items():
            data=z.read(name)
            if data!=p.read_bytes() or hashlib.sha256(data).hexdigest()!=hashlib.sha256(p.read_bytes()).hexdigest():raise ValueError('ZIP member: '+name)
    receipt={'status':'PASS','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_filename':archive.name,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'archive_top_directory':top.rstrip('/'),'members':len(files),'member_inventory_exact':True,'zip_crc_all_pass':True,'all_members_readable_and_byte_equal':True,'all_member_hashes_equal_local_payload':True,'manifest_sha256':hashlib.sha256((root/'SHA256SUMS').read_bytes()).hexdigest(),'packet_verifier':qa,'chunk_status':'PARTIAL','scope_limit':'Metadata-only comparator; primary text not read. Packet integrity is not research acceptance. No complete Git tree or methodological compliance asserted.','receipt_location':'External to archive; excluded from payload manifest to avoid recursive hashing.'}
    receipt_path=archive.parent/'MHAC_R002_chunk1C1_archive_verification.json'
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return receipt

if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    archive=Path(sys.argv[2]) if len(sys.argv)>2 else root.parent/'MHAC_R002_chunk1C1_packet_2026-10-04.zip'
    try:print(json.dumps(package(root,archive),indent=2))
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)},indent=2));sys.exit(1)
