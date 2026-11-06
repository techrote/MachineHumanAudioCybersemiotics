"""Reproduce a fixed 12-occurrence DOI/title adjudication; never screen sources."""
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
from tools.screening import normalize_doi

AREA = 'research/registry/identity'
LEDGER = AREA + '/R006-DOI-TRANCHE-20261106.json'
QUEUE = AREA + '/R006-IDENTITY-QUEUE-20261106.json'
AID = 'AID-R006-DOI-TRANCHE-20261106'
SOURCES = {'SRC-REL-' + key: key for key in ('BLATTNER-1989', 'EDWORTHY-1991', 'HELLIER-1993')}
ACTOR = {'kind': 'agent', 'id': 'codex-r006-doi-tranche-20261106', 'model': 'GPT-6',
         'tool': 'Codex; local Python, preserved Crossref/OpenAlex and bibliography metadata'}


def digest(value):
    return hashlib.sha256(dumps(value).encode()).hexdigest()


def pin(rid, rev=1):
    return {'id': rid, 'rev': rev}


def build(root, at):
    artifacts = {}
    def artifact(path, expected=None):
        blob = (root / path).read_bytes()
        sha = hashlib.sha256(blob).hexdigest()
        if expected is not None and sha != expected:
            raise ValueError('Evidence artifact hash mismatch: ' + path)
        artifacts[path] = {'path': path, 'sha256': sha}
        return blob
    queue = read_json(root / QUEUE)
    artifact(QUEUE)
    lookup_path = 'research/searches/related/exports/lookups/MANIFEST.json'
    lookups = read_json(root / lookup_path)['lookups']
    artifact(lookup_path)
    source_rows, source_evidence, representatives = {}, {}, {}
    for sid, key in SOURCES.items():
        source_path = 'research/sources/related/records/' + sid + '.json'
        source = read_json(root / source_path)['revisions'][0]
        body = source['data']
        dois = [normalize_doi(i['value']) for i in body['identifiers'] if i['scheme'] == 'doi' and i['status'] == 'verified']
        if body['metadata_status'] != 'verified' or body['validity'] != 'active' or len(dois) != 1 or not dois[0]:
            raise ValueError('Source lacks one verified DOI: ' + sid)
        lookup = lookups[key]
        items = json.loads(artifact(lookup['file'], lookup['sha256']))['message']['items']
        if normalize_doi(items[0]['DOI']) != dois[0] or items[0]['title'][0] != body['title']:
            raise ValueError('Crossref DOI/title disagreement: ' + sid)
        rid = 'HIT-R004-LK-' + key + '-01'
        representative_path = 'research/searches/related/records/hits/' + rid + '.json'
        representative = read_json(root / representative_path)['revisions'][0]
        if representative['data']['status'] != 'resolved' or representative['data']['source_ref'] != pin(sid):
            raise ValueError('Representative source disagreement: ' + rid)
        representatives[sid] = pin(rid)
        source_rows[sid] = body
        source_evidence[sid] = {'source_ref': pin(sid), 'revision_sha256': digest(source),
            'doi': dois[0], 'title': body['title'], 'lookup_path': lookup['file'], 'lookup_item': 1,
            'representative_ref': pin(rid), 'representative_revision_sha256': digest(representative)}
    output, occurrences, pages_cache = {}, [], {}
    selected = [c for c in queue['candidates'] if len(c['source_candidates']) == 1
                and c['source_candidates'][0]['source_ref']['id'] in SOURCES]
    if len(selected) != 12:
        raise ValueError('Fixed scope must contain twelve occurrences')
    for candidate in selected:
        hid = candidate['hit_ref']['id']
        sid = candidate['source_candidates'][0]['source_ref']['id']
        lane = 'related' if hid.startswith('HIT-R004-') else 'auditory'
        path = f'research/searches/{lane}/records/hits/{hid}.json'
        record = read_json(root / path)
        original = record['revisions'][0]
        before = original['data']
        doi = source_evidence[sid]['doi']
        if before['status'] != 'unresolved' or doi not in {normalize_doi(i['value']) for i in before['returned_identifiers'] if i['scheme'] == 'doi'}:
            raise ValueError('Original occurrence DOI/status mismatch: ' + hid)
        search = read_json(root / f'research/searches/{lane}/records/' / (before['search_ref']['id'] + '.json'))['revisions'][before['search_ref']['rev']-1]
        exp = search['data']['export']['value']
        raw = artifact(exp['path'], exp['sha256'])
        export = json.loads(raw)
        ordinal = before['ordinal']
        if search['data']['platform'] == 'Crossref REST API':
            key = before['search_ref']['id'].removeprefix('SRCH-R004-LK-')
            meta = export['lookups'][key]
            rows = json.loads(artifact(meta['file'], meta['sha256']))['message']['items']
            row = rows[ordinal-1]
            actual_doi, title = normalize_doi(row['DOI']), row['title'][0]
            locator = {'path': meta['file'], 'item': ordinal}
        elif 'OpenAlex' in search['data']['platform']:
            label = before['search_ref']['id'].rsplit('-', 1)[1]
            cache_key = (exp['path'], label)
            if cache_key not in pages_cache:
                works = []
                for page in export['runs'][label]['pages']:
                    if 'results' not in page:
                        continue
                    payload = gzip.decompress(artifact(page['file'], page['sha256']))
                    if hashlib.sha256(payload).hexdigest() != page['payload_sha256']:
                        raise ValueError('Decompressed artifact hash mismatch')
                    results = json.loads(payload)['results']
                    if len(results) != page['results']:
                        raise ValueError('OpenAlex page count mismatch')
                    works.extend((row, page['file'], i+1) for i, row in enumerate(results))
                pages_cache[cache_key] = works
            row, page_path, item = pages_cache[cache_key][ordinal-1]
            actual_doi, title = normalize_doi(row['doi']), row['display_name']
            locator = {'path': page_path, 'item': item, 'work_id': row['id']}
            if not any(i['value'] == row['id'] for i in before['returned_identifiers']):
                raise ValueError('OpenAlex occurrence ID mismatch')
        else:
            section = next(s for s in export['sources'] if s['label'] == 'nees-liebman-am')
            row = section['entries'][ordinal-1]
            title = source_rows[sid]['title']
            if title not in row['text'] or doi not in row['text'].lower():
                raise ValueError('Bibliographic DOI/title disagreement')
            actual_doi = doi
            locator = {'path': exp['path'], 'section': section['section'], 'item': ordinal,
                       'file_page_start': row['file_page_start'], 'file_page_end': row['file_page_end']}
        if actual_doi != doi or title != source_rows[sid]['title'] or title not in before['raw_metadata']:
            raise ValueError('Retained export DOI/title disagreement: ' + hid)
        after = copy.deepcopy(before)
        after.update(status='duplicate', source_ref=pin(sid), duplicate_of=representatives[sid],
            resolution_reason='R006: DOI and full title agree between retained occurrence export and verified source/Crossref metadata; duplicate of existing R004 resolved occurrence. Identity only; no eligibility, new reading, study or sample assertion. See ' + LEDGER)
        revision = {'rev': 2, 'at': at, 'actor': ACTOR,
                    'basis': [pin(hid), before['search_ref'], pin(sid), representatives[sid], pin(AID)],
                    'factual_status': 'derived', 'data': after}
        output[path] = {**record, 'revisions': [copy.deepcopy(original), revision]}
        occurrences.append({'hit_id': hid, 'path': path, 'input_ref': pin(hid), 'output_ref': pin(hid, 2),
            'input_revision_sha256': digest(original), 'output_revision_sha256': digest(revision),
            'source_ref': pin(sid), 'duplicate_of': representatives[sid], 'doi': doi,
            'search_ref': before['search_ref'], 'ordinal': ordinal, 'export_locator': locator})
    inputs = [pin(s) for s in sorted(SOURCES)] + [pin(o['hit_id']) for o in occurrences]
    output[AREA + '/records/' + AID + '.json'] = {'id': AID, 'issue': 6, 'kind': 'assistance',
        'schema_version': 1, 'synthetic': False, 'revisions': [{'rev': 1, 'at': at, 'actor': ACTOR,
        'basis': inputs, 'factual_status': 'derived', 'data': {'subtype': 'assistance', 'status': 'performed',
        'performed_at': {'state': 'known', 'value': at}, 'task': 'Adjudicate twelve DOI/title discovery duplicates against three existing publications and representatives.',
        'input_refs': inputs, 'output_refs': [o['output_ref'] for o in occurrences],
        'artifacts': [LEDGER, AREA + '/README.md'],
        'verification_steps': ['Verified retained export and page hashes, DOI and full title at original ordinal.',
            'Compared source revision 1 against retained Crossref first result; linked each duplicate to its already resolved R004 representative.',
            'Retained original revisions and all search identifiers/ordinals; no source or scientific record changed.'],
        'limitations': 'Metadata identity only; no new online retrieval, source reading, eligibility, study/sample identity or complete corpus. OpenAlex public derivatives omit abstracts; underlying private raw responses were not inspected. Distinct abstract-only DOI records remain separate.',
        'independence': 'One Codex/GPT-6 agent and deterministic software self-review; no independent human adjudication.'}}]}
    ledger = {'artifact_kind': 'bounded_doi_identity_tranche', 'issue': 6, 'resolved_at': at, 'actor': ACTOR,
        'implementation_base': '32e0c51dae98a5d88025af25fdc001290dc2d70e',
        'sources': [source_evidence[s] for s in sorted(SOURCES)], 'occurrences': occurrences,
        'input_artifacts': [artifacts[p] for p in sorted(artifacts)],
        'counts': {'occurrences': 12, 'existing_publications': 3, 'duplicate_occurrences': 12,
            'new_source_records': 0, 'screening_decisions_created': 0, 'study_records_created': 0, 'sample_records_created': 0},
        'boundary': 'Identity only. Original source access/reading remains unchanged; issue #6 and corpus gate remain open.'}
    return output, ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / LEDGER
    if args.check and not target.exists():
        raise SystemExit('Frozen tranche ledger is missing')
    at = read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    records, ledger = build(ROOT, at)
    if target.exists() and read_json(target) != ledger:
        raise SystemExit('Frozen DOI tranche ledger drift; no records written')
    if args.check:
        for path, expected in records.items():
            actual = read_json(ROOT / path)
            if {**actual, 'revisions': actual['revisions'][:len(expected['revisions'])]} != expected:
                raise SystemExit('DOI tranche record prefix drift: ' + path)
        print('Twelve duplicate resolutions reproduce; later revisions preserved.')
    else:
        write_generated_records(ROOT, records)
        target.write_text(dumps(ledger), encoding='utf-8')
        print('Recorded 12 duplicate occurrences -> 3 existing publications; no screening decisions.')


if __name__ == '__main__':
    main()
