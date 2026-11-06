"""Reproduce eight fixed resource-URL identity decisions; never screen papers."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from tools.record_io import dumps, read_json
from tools.records import write_generated_records

AREA = 'research/registry/identity'
LEDGER = AREA+'/R006-URL-TRANCHE-20261106.json'
QUEUE = AREA+'/R006-IDENTITY-QUEUE-20261106.json'
AID = 'AID-R006-URL-TRANCHE-20261106'
ACTOR = {'kind':'agent','id':'codex-r006-url-tranche-20261106','model':'GPT-6',
         'tool':'Codex; Python comparison of retained web-discovery exports and accepted source provenance'}
# Exact publication resources reviewed in this batch; no host-level or fuzzy match.
PLAN = {
 'SRC-R005R-EDWORTHY-2013': ('research/sources/auditory/records',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC3628049/',
    ('research/searches/auditory/records/hits/HIT-R005R-C1LOAD-EQ1-03058.json',2)),
 'SRC-BRIER-2011-SIGNS': ('research/sources/brier/records',
    'https://tidsskrift.dk/signs/article/view/26864',
    ('research/searches/brier/records/hits/HIT-R003-B04-06.json',1)),
 'SRC-NOV-NEES-LIEBMAN-2023': ('research/novelty/records',
    'https://ldr.lafayette.edu/concern/publications/gx41mk40g',
    ('research/searches/pilot/records/hits/HIT-R002-PA6-02.json',1)),
 'SRC-R005R-RUSKIN-2020': ('research/sources/auditory/records',
    'https://rosap.ntl.bts.gov/view/dot/59041/dot_59041_DS1.pdf',None),
}
LABELS = {'SRCH-R002-PA6':'P-A6','SRCH-R002-PB1':'P-B1','SRCH-R004-G29':'G-29',
          'SRCH-R005-AW8':'A-W8','SRCH-R005-GW1':'G-W1','SRCH-R005-GW8':'G-W8',
          'SRCH-R005-GW9':'G-W9','SRCH-R005-RPSLR':'R-PSLR'}


def pin(rid,rev=1):
    return {'id':rid,'rev':rev}


def digest(value):
    return hashlib.sha256(dumps(value).encode()).hexdigest()


def build(root,at):
    artifacts = {}
    def artifact(path,expected=None):
        blob = (root/path).read_bytes()
        sha = hashlib.sha256(blob).hexdigest()
        if expected is not None and sha!=expected:
            raise ValueError('Evidence artifact hash mismatch: '+path)
        artifacts[path] = {'path':path,'sha256':sha}
        return blob
    queue = json.loads(artifact(QUEUE))
    selected = [c for c in queue['candidates'] if len(c['source_candidates'])==1
                and c['source_candidates'][0]['source_ref']['id'] in PLAN
                and c['source_candidates'][0]['matches']==[{'scheme':'url','value':PLAN[c['source_candidates'][0]['source_ref']['id']][1]}]]
    if len(selected)!=8:
        raise ValueError('Fixed scope must contain eight resource occurrences')
    sources,representatives = {},{}
    for sid,(directory,url,rep) in sorted(PLAN.items()):
        path = directory+'/'+sid+'.json'
        revision = read_json(root/path)['revisions'][0]
        body = revision['data']
        verified = [i for i in body['identifiers'] if i['scheme']=='url' and i['status']=='verified' and i['value']==url]
        if body['validity']!='active' or body['metadata_status']!='verified' or len(verified)!=1 or any(i['status']=='conflict' for i in body['identifiers']):
            raise ValueError('Source lacks exact verified resource: '+sid)
        sources[sid] = {'source_ref':pin(sid),'path':path,'revision_sha256':digest(revision),
            'title':body['title'],'verified_resource':url,'identifier_provenance':verified[0]['provenance'],
            'metadata_evidence':body['metadata_evidence'],
            'verification_extent':'Inherited accepted publication-specific resource verification; no fresh online retrieval or source reading.'}
        if rep:
            rep_path,rev = rep
            record = read_json(root/rep_path)
            r = record['revisions'][rev-1]
            if r['data']['status']!='resolved' or r['data']['source_ref']!=pin(sid):
                raise ValueError('Representative source disagreement: '+record['id'])
            representatives[sid] = pin(record['id'],rev)
            sources[sid]['existing_representative'] = {'ref':representatives[sid],'path':rep_path,'revision_sha256':digest(r)}
    output,occurrences = {},[]
    for candidate in selected:
        hid = candidate['hit_ref']['id']
        sid = candidate['source_candidates'][0]['source_ref']['id']
        lane = 'pilot' if hid.startswith('HIT-R002-') else 'related' if hid.startswith('HIT-R004-') else 'auditory'
        path = f'research/searches/{lane}/records/hits/{hid}.json'
        record = read_json(root/path)
        original = record['revisions'][0]
        before = original['data']
        url = PLAN[sid][1]
        if before['status']!='unresolved' or before['returned_identifiers']!=[{'scheme':'url','value':url}]:
            raise ValueError('Original resource/status disagreement: '+hid)
        search_path = f'research/searches/{lane}/records/'+before['search_ref']['id']+'.json'
        search = read_json(root/search_path)['revisions'][before['search_ref']['rev']-1]
        exp = search['data']['export']['value']
        export = json.loads(artifact(exp['path'],exp['sha256']))
        label = LABELS[before['search_ref']['id']]
        runs = [(batch,run) for batch in export['batches'] for run in batch['runs'] if run['label']==label]
        if len(runs)!=1:
            raise ValueError('Ambiguous export run label')
        batch,run = runs[0]
        ordinal = before['ordinal']
        row = run['results'][ordinal-1]
        if row['ordinal']!=ordinal or row['url']!=url or before['raw_metadata']!=row['title']+' | '+row['url']:
            raise ValueError('Retained result/ordinal disagreement: '+hid)
        if search['data']['query']!=run['query']:
            raise ValueError('Search query/export disagreement')
        duplicate = sid in representatives
        after = copy.deepcopy(before)
        after.update(status='duplicate' if duplicate else 'resolved',source_ref=pin(sid),
            resolution_reason='R006: original exported result URL equals the exact publication-specific verified source resource; exported query, ordinal and raw result label checked. Source verification inherited; hostname-only labels are not bibliographic titles. Identity only; no eligibility or new reading. See '+LEDGER)
        basis = [pin(hid),before['search_ref'],pin(sid),pin(AID)]
        if duplicate:
            after['duplicate_of'] = representatives[sid]
            basis.append(representatives[sid])
        else:
            representatives[sid] = pin(hid,2)
        revision = {'rev':2,'at':at,'actor':ACTOR,'basis':basis,'factual_status':'derived','data':after}
        output[path] = {**record,'revisions':[copy.deepcopy(original),revision]}
        occurrences.append({'hit_id':hid,'path':path,'input_ref':pin(hid),'output_ref':pin(hid,2),
            'input_revision_sha256':digest(original),'output_revision_sha256':digest(revision),
            'source_ref':pin(sid),'status':after['status'],'duplicate_of':after.get('duplicate_of'),
            'verified_resource':url,'search_ref':before['search_ref'],'search_revision_sha256':digest(search),
            'ordinal':ordinal,'export_locator':{'path':exp['path'],'batch':batch['batch'],'run':label,'item':ordinal},
            'original_result_label':row['title']})
    inputs = [pin(s) for s in sorted(PLAN)]+[o['input_ref'] for o in occurrences]
    output[AREA+'/records/'+AID+'.json'] = {'id':AID,'issue':6,'kind':'assistance','schema_version':1,'synthetic':False,
        'revisions':[{'rev':1,'at':at,'actor':ACTOR,'basis':inputs,'factual_status':'derived','data':{
        'subtype':'assistance','status':'performed','performed_at':{'state':'known','value':at},
        'task':'Adjudicate eight fixed publication-resource URL occurrences against four existing sources; retain original web labels and pilot provenance.',
        'input_refs':inputs,'output_refs':[o['output_ref'] for o in occurrences],'artifacts':[LEDGER,AREA+'/README.md'],
        'verification_steps':['Checked hash-bound original web exports, query, run label, ordinal, exact returned URL and unmodified raw result label.',
            'Checked exact verified source resource, source metadata provenance, and pre-existing representative source pins.',
            'Resolved one Ruskin representative and seven duplicates, preserving every original revision and scientific/access/reading state.'],
        'limitations':'Inherits accepted source metadata/resource verification. No current URL availability claim, new online retrieval, article/PDF reading, source alias, eligibility, study/sample independence or complete corpus. Some original labels are hostnames, not publication titles.',
        'independence':'One Codex/GPT-6 agent and software self-review; no independent human adjudication.'}}]}
    ledger = {'artifact_kind':'bounded_resource_url_tranche','issue':6,'resolved_at':at,'actor':ACTOR,
        'implementation_base':'3f6082f513604dce0c80922945a088458b2529d7','sources':[sources[s] for s in sorted(sources)],
        'occurrences':occurrences,'input_artifacts':[artifacts[p] for p in sorted(artifacts)],
        'counts':{'occurrences':8,'existing_publications':4,'resolved_representatives':1,'duplicate_occurrences':7,
                  'new_source_records':0,'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0},
        'boundary':'Completes the fixed 30-candidate queue, not publication reconciliation or corpus acceptance. Issue #6 stays open.'}
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
        raise SystemExit('Frozen URL ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual = read_json(ROOT/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:
                raise SystemExit('URL tranche record prefix drift: '+path)
        print('Eight URL identity decisions reproduce; later revisions preserved.')
    else:
        write_generated_records(ROOT,records)
        target.write_text(dumps(ledger),encoding='utf-8')
        print('Recorded 8 URL decisions: 1 representative, 7 duplicates; no screening decisions.')


if __name__=='__main__':
    main()
