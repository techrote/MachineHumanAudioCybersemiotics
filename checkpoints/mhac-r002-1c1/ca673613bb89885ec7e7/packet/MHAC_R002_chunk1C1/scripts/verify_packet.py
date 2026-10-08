"""Offline transport/content checks for this audit packet, not scientific validation.
Usage: python scripts/verify_packet.py [packet_root]
"""
from pathlib import Path
import ast, csv, hashlib, io, json, re, sys, zipfile
from verify_inputs import verify

def run(root: Path) -> dict:
    root=root.resolve()
    files={p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if any(p.is_symlink() for p in root.rglob('*')): raise ValueError('Symlink in packet')
    expected={}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        h,rel=line.split('  ',1)
        if rel in expected: raise ValueError('Duplicate manifest key')
        expected[rel]=h
    if set(expected)!=(set(files)-{'SHA256SUMS'}): raise ValueError('Manifest inventory mismatch')
    utf8=csvs=jsons=pys=links=0
    for rel,p in files.items():
        if rel!='SHA256SUMS' and hashlib.sha256(p.read_bytes()).hexdigest()!=expected[rel]: raise ValueError('Hash: '+rel)
        if p.suffix=='.zip': continue
        text=p.read_text(encoding='utf-8');utf8+=1
        if p.suffix=='.json': json.loads(text);jsons+=1
        if p.suffix=='.csv':
            rows=list(csv.DictReader(io.StringIO(text)))
            if not rows or any(None in r for r in rows): raise ValueError('CSV: '+rel)
            csvs+=1
        if p.suffix=='.py': ast.parse(text);pys+=1
        if p.suffix=='.md':
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)',text):
                if '://' in target or target.startswith(('#','mailto:')):continue
                path=target.split('#',1)[0]
                if not path:continue
                if not (p.parent/path).resolve().exists():raise ValueError('Broken link '+rel+' -> '+target)
                links+=1
    def readcsv(rel):return list(csv.DictReader((root/rel).open(encoding='utf-8')))
    overlap=readcsv('matrices/OVERLAP_MATRIX.csv')
    if {r['rq'] for r in overlap}!={f'RQ{i}' for i in range(1,7)} or len(overlap)!=6: raise ValueError('RQ cardinality')
    if not all(r['overlap_category']=='cannot_yet_assess_substantive_overlap' and r['already_addressed']=='not_established' for r in overlap):raise ValueError('Unsupported overlap status')
    cov=readcsv('matrices/COVERAGE_UNKNOWNS.csv'); cand=readcsv('matrices/CANDIDATE_QUESTIONS.csv')
    if len(cov)!=14 or len(cand)>3: raise ValueError('Audit bounds')
    identity=json.loads((root/'readings/COMPARATOR_IDENTITY.json').read_text())
    if identity['full_text_available_to_this_chunk'] or identity['version_of_record_read'] or identity['source_sha256'] is not None:raise ValueError('False full-text status')
    if 'PARTIAL' not in (root/'CHECKPOINT.md').read_text(): raise ValueError('Completion label')
    b=root/'inputs/MHAC_R002_chunk1B_packet_2026-10-04.zip'; bcheck=verify(b)
    receipt=json.loads((root/'inputs/MHAC_R002_chunk1B_archive_verification.json').read_text())
    if bcheck['sha256']!=receipt['archive_sha256']:raise ValueError('Prior receipt identity')
    # Nested 1A byte/hash/inventory verification without writing outside this packet.
    with zipfile.ZipFile(b) as zb:
        ba=zb.read('MHAC_R002_chunk1B/inputs/MHAC_R002_chunk1A_packet_2026-10-04.zip')
        ra=json.loads(zb.read('MHAC_R002_chunk1B/inputs/MHAC_R002_chunk1A_archive_verification.json'))
        if hashlib.sha256(ba).hexdigest()!=ra['archive_sha256']:raise ValueError('Nested1A identity')
        with zipfile.ZipFile(io.BytesIO(ba)) as za:
            if za.testzip() is not None:raise ValueError('Nested1A CRC')
            prefix='MHAC_R002_chunk1A/'; m={}
            for line in za.read(prefix+'SHA256SUMS').decode().splitlines():
                h,n=line.split('  ',1);m[n]=h
            if {n[len(prefix):] for n in za.namelist()}!=set(m)|{'SHA256SUMS'}:raise ValueError('Nested1A inventory')
            for n,h in m.items():
                if hashlib.sha256(za.read(prefix+n)).hexdigest()!=h:raise ValueError('Nested1A hash')
            for rec in json.loads((root/'provenance/PRIOR_COPY_IDENTITIES.json').read_text()):
                original=za.read(rec['original_member']) if rec['packet']=='1A' else zb.read(rec['original_member'])
                local=(root/rec['local_copy']).read_bytes()
                if local!=original or hashlib.sha256(local).hexdigest()!=rec['sha256']:raise ValueError('Prior copy '+rec['local_copy'])
    return {'status':'PASS','scope':'Packet transport, syntax, links and declared-scope consistency only; not research acceptance, source-fidelity or registry validation','packet_files':len(files),'payload_hashes_verified':len(expected),'utf8_files_read':utf8,'json_files_parsed':jsons,'csv_files_parsed':csvs,'python_files_parsed':pys,'local_markdown_links_checked':links,'rq_rows':len(overlap),'coverage_fields':len(cov),'candidate_questions':len(cand),'prior_1B':bcheck,'nested_1A_payload_hashes_verified':len(m),'prior_copies_byte_equal':True,'repository_tests_run':0,'primary_comparator_sections_read':0,'primary_comparator_screenshots':0,'scientific_completion_claimed':False}

if __name__=='__main__':
    try:
        result=run(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
    except (OSError,ValueError,AssertionError,KeyError,zipfile.BadZipFile) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)},indent=2));sys.exit(1)
    print(json.dumps(result,indent=2))
