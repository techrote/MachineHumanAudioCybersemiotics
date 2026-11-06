"""Reproduce ten fixed DOI/title decisions without screening or source reading."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.record_io import dumps, read_json
from tools.records import write_generated_records
from tools.screening import normalize_doi, verified_dois

AREA = 'research/registry/identity'
LEDGER = AREA + '/R006-REMAINING-DOIS-20261106.json'
QUEUE = AREA + '/R006-IDENTITY-QUEUE-20261106.json'
AID = 'AID-R006-REMAINING-DOIS-20261106'
ACTOR = {'kind':'agent', 'id':'codex-r006-remaining-dois-20261106', 'model':'GPT-6',
         'tool':'Codex; Python comparison of retained OpenAlex and bibliography metadata'}
# None means the first fixed occurrence is resolved; later occurrences link to it.
PLAN = {
 'SRC-NOV-NEES-LIEBMAN-2023': ('research/novelty/records', 'HIT-R002-PA6-02', 'research/searches/pilot/records'),
 'SRC-AUD-MCFARLANE-2020-REVIEW': ('research/sources/auditory/records', None, None),
 'SRC-R005R-EDWORTHY-2013': ('research/sources/auditory/records', None, None),
 'SRC-REL-MURPHY-2006': ('research/sources/related/records', 'HIT-R004-LK3-NSS-USE-SCENARIO-03', 'research/searches/related/records/hits'),
 'SRC-REL-GAVER-1986': ('research/sources/related/records', 'HIT-R004-LK-GAVER-1986-01', 'research/searches/related/records/hits'),
}


def pin(rid, rev=1):
    return {'id':rid, 'rev':rev}


def digest(value):
    return hashlib.sha256(dumps(value).encode()).hexdigest()


def text_key(value):
    # Presentation-only normalization; no punctuation, words or digits removed.
    return ' '.join(value.casefold().split())


def build(root, at):
    artifacts = {}
    def artifact(path, expected=None):
        blob = (root/path).read_bytes()
        sha = hashlib.sha256(blob).hexdigest()
        if expected is not None and sha != expected:
            raise ValueError('Evidence artifact hash mismatch: '+path)
        artifacts[path] = {'path':path,'sha256':sha}
        return blob
    queue = json.loads(artifact(QUEUE))
    selected = [c for c in queue['candidates'] if len(c['source_candidates'])==1
                and c['source_candidates'][0]['source_ref']['id'] in PLAN
                and any(m['scheme']=='doi' for m in c['source_candidates'][0]['matches'])]
    if len(selected)!=10:
        raise ValueError('Fixed scope must contain ten DOI occurrences')
    sources, source_rows, representatives = {}, {}, {}
    for sid,(directory,rid,hit_directory) in sorted(PLAN.items()):
        path = directory+'/'+sid+'.json'
        source = read_json(root/path)['revisions'][0]
        body = source['data']
        dois = verified_dois(body)
        if body['metadata_status']!='verified' or body['validity']!='active' or len(dois)!=1 or any(i['status']=='conflict' for i in body['identifiers']):
            raise ValueError('Source lacks unconflicted verified identity: '+sid)
        source_rows[sid] = body
        sources[sid] = {'source_ref':pin(sid),'path':path,'revision_sha256':digest(source),
                        'doi':next(iter(dois)),'title':body['title'],
                        'metadata_provenance':body['metadata_evidence'],
                        'verification_extent':'Inherited accepted source verification; no new paper retrieval or reading.'}
        if rid:
            hit_path = hit_directory+'/'+rid+'.json'
            # Some pilot layouts use a hits subdirectory.
            if not (root/hit_path).exists():
                hit_path = hit_directory+'/hits/'+rid+'.json'
            rep = read_json(root/hit_path)['revisions'][0]
            if rep['data']['status']!='resolved' or rep['data']['source_ref']!=pin(sid):
                raise ValueError('Representative source disagreement: '+rid)
            representatives[sid] = pin(rid)
            sources[sid]['existing_representative'] = {'ref':pin(rid),'path':hit_path,'revision_sha256':digest(rep)}
    output, occurrences, cache = {}, [], {}
    for candidate in selected:
        hid = candidate['hit_ref']['id']
        sid = candidate['source_candidates'][0]['source_ref']['id']
        path = 'research/searches/auditory/records/hits/'+hid+'.json'
        record = read_json(root/path)
        original = record['revisions'][0]
        before = original['data']
        doi = sources[sid]['doi']
        if before['status']!='unresolved' or doi not in {normalize_doi(i['value']) for i in before['returned_identifiers'] if i['scheme']=='doi'}:
            raise ValueError('Original DOI/status disagreement: '+hid)
        search_path = 'research/searches/auditory/records/'+before['search_ref']['id']+'.json'
        search = read_json(root/search_path)['revisions'][before['search_ref']['rev']-1]
        exp = search['data']['export']['value']
        manifest = json.loads(artifact(exp['path'],exp['sha256']))
        ordinal = before['ordinal']
        if 'OpenAlex' in search['data']['platform']:
            label = before['search_ref']['id'].rsplit('-',1)[1]
            key = (exp['path'],label)
            if key not in cache:
                works = []
                for page in manifest['runs'][label]['pages']:
                    if 'results' not in page:
                        continue
                    payload = gzip.decompress(artifact(page['file'],page['sha256']))
                    if hashlib.sha256(payload).hexdigest()!=page['payload_sha256']:
                        raise ValueError('Decompressed artifact hash mismatch')
                    rows = json.loads(payload)['results']
                    if len(rows)!=page['results']:
                        raise ValueError('OpenAlex page count mismatch')
                    works.extend((row,page['file'],i+1) for i,row in enumerate(rows))
                cache[key] = works
            row,page_path,item = cache[key][ordinal-1]
            title,actual_doi = row['display_name'],normalize_doi(row['doi'])
            if not any(i['value']==row['id'] for i in before['returned_identifiers']):
                raise ValueError('OpenAlex work ID disagreement')
            locator = {'path':page_path,'item':item,'work_id':row['id']}
        elif before['search_ref']['id']=='SRCH-R005R-C9NLGENERAL':
            section = next(s for s in manifest['sources'] if s['label']=='nees-liebman-am')
            row = section['entries'][ordinal-1]
            title,actual_doi = source_rows[sid]['title'],doi
            if text_key(title) not in text_key(row['text']) or doi not in row['text'].lower():
                raise ValueError('Bibliographic DOI/title disagreement')
            locator = {'path':exp['path'],'section':section['section'],'item':ordinal,
                       'file_page_start':row['file_page_start'],'file_page_end':row['file_page_end']}
        else:
            raise ValueError('Unreviewed export format')
        if actual_doi!=doi or text_key(title)!=text_key(source_rows[sid]['title']) or text_key(title) not in text_key(before['raw_metadata']):
            raise ValueError('Retained DOI/title disagreement: '+hid)
        after = copy.deepcopy(before)
        is_duplicate = sid in representatives
        after.update(status='duplicate' if is_duplicate else 'resolved',source_ref=pin(sid),
            resolution_reason='R006: explicit DOI and full title (case/whitespace normalized only) agree with retained export and accepted verified source. Identity only; no eligibility, new reading or independent-study assertion. See '+LEDGER)
        basis = [pin(hid),before['search_ref'],pin(sid),pin(AID)]
        if is_duplicate:
            after['duplicate_of'] = representatives[sid]
            basis.append(representatives[sid])
        else:
            representatives[sid] = pin(hid,2)
        revision = {'rev':2,'at':at,'actor':ACTOR,'basis':basis,'factual_status':'derived','data':after}
        output[path] = {**record,'revisions':[copy.deepcopy(original),revision]}
        occurrences.append({'hit_id':hid,'path':path,'input_ref':pin(hid),'output_ref':pin(hid,2),
            'input_revision_sha256':digest(original),'output_revision_sha256':digest(revision),
            'source_ref':pin(sid),'status':after['status'],'duplicate_of':after.get('duplicate_of'),
            'doi':doi,'search_ref':before['search_ref'],'ordinal':ordinal,'export_locator':locator})
    inputs = [pin(s) for s in sorted(PLAN)]+[o['input_ref'] for o in occurrences]
    output[AREA+'/records/'+AID+'.json'] = {'id':AID,'issue':6,'kind':'assistance','schema_version':1,'synthetic':False,
        'revisions':[{'rev':1,'at':at,'actor':ACTOR,'basis':inputs,'factual_status':'derived','data':{
        'subtype':'assistance','status':'performed','performed_at':{'state':'known','value':at},
        'task':'Resolve ten explicit-DOI discovery occurrences against five existing publications; preserve publication versions and distinct date meanings.',
        'input_refs':inputs,'output_refs':[o['output_ref'] for o in occurrences],'artifacts':[LEDGER,AREA+'/README.md'],
        'verification_steps':['Verified retained export, compressed page and decompressed payload hashes and original occurrence ordinal/work ID.',
            'Compared full title after case/whitespace normalization only and explicit DOI against accepted source revision 1.',
            'Linked duplicates to existing resolved occurrences where available; chose fixed in-tranche representatives for two previously unlinked sources.'],
        'limitations':'Accepted source metadata verification is inherited, not a new source reading. No fresh online lookup, eligibility decision, source alias, family-link assertion or study/sample inference. OpenAlex private raw responses were not inspected. Nees VoR and AM remain distinct; Edworthy online-first date and issue year remain distinct.',
        'independence':'One Codex/GPT-6 agent and software self-review; no independent human adjudication.'}}]}
    ledger = {'artifact_kind':'bounded_remaining_doi_tranche','issue':6,'resolved_at':at,'actor':ACTOR,
        'implementation_base':'822ce7130a00e75f150210d800de652e527f212a','sources':[sources[s] for s in sorted(sources)],
        'occurrences':occurrences,'input_artifacts':[artifacts[p] for p in sorted(artifacts)],
        'counts':{'occurrences':10,'existing_publications':5,'resolved_representatives':2,'duplicate_occurrences':8,
                  'new_source_records':0,'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0},
        'boundary':'Publication identity only; no corpus acceptance or full-source reading. Issue #6 remains open.'}
    return output,ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    target = ROOT/LEDGER
    if args.check and not target.exists():
        raise SystemExit('Frozen tranche ledger is missing')
    at = read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    records,ledger = build(ROOT,at)
    if target.exists() and read_json(target)!=ledger:
        raise SystemExit('Frozen remaining-DOI ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual = read_json(ROOT/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:
                raise SystemExit('Remaining-DOI record prefix drift: '+path)
        print('Ten DOI identity decisions reproduce; later revisions preserved.')
    else:
        write_generated_records(ROOT,records)
        target.write_text(dumps(ledger),encoding='utf-8')
        print('Recorded 10 identity decisions: 2 representatives, 8 duplicates; no screening decisions.')


if __name__=='__main__':
    main()
