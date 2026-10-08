"""Verify supplied ZIP payload inventories and hashes without running their code."""
from pathlib import Path, PurePosixPath
import hashlib, json, zipfile, sys

def verify(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(set(names))!=len(names): raise ValueError('Duplicate members')
        if z.testzip() is not None: raise ValueError('CRC failure')
        for name in names:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe member')
        manifests=[n for n in names if n.count('/')==1 and n.endswith('/SHA256SUMS')]
        if len(manifests)!=1: raise ValueError('Manifest cardinality')
        manifest=manifests[0]; prefix=manifest.rsplit('/',1)[0]+'/'
        expected={}
        for line in z.read(manifest).decode().splitlines():
            digest,rel=line.split('  ',1)
            if rel in expected: raise ValueError('Duplicate manifest member')
            expected[rel]=digest
        actual={n[len(prefix):] for n in names if n!=manifest}
        if actual!=set(expected): raise ValueError('Manifest inventory mismatch')
        for rel,digest in expected.items():
            if hashlib.sha256(z.read(prefix+rel)).hexdigest()!=digest: raise ValueError(rel)
        return {'archive':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes':path.stat().st_size,'members':len(names),'payload_hashes_verified':len(expected),'manifest_sha256':hashlib.sha256(z.read(manifest)).hexdigest(),'crc_pass':True,'inventory_exact':True,'all_members_readable':True}
if __name__=='__main__':
    print(json.dumps([verify(Path(p)) for p in sys.argv[1:]],indent=2))
