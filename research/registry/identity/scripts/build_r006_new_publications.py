"""Reproduce fixed publication-identity batches; defaults retain the original tranche."""
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
sys.path.insert(0,str(ROOT))
from tools.record_io import dumps, read_json
from tools.records import write_generated_records
from tools.screening import normalize_doi

AREA='research/registry/identity'
PLAN=AREA+'/R006-NEW-DOI-PLAN-20261106.json'
LEDGER=AREA+'/R006-NEW-PUBLICATIONS-20261106.json'
AID='AID-R006-NEW-PUBLICATIONS-20261106'
ACTOR={'kind':'agent','id':'codex-r006-new-publications-20261106','model':'GPT-6',
       'tool':'Codex; fresh Crossref bibliographic metadata and retained discovery comparison'}


def pin(rid,rev=1):
    return {'id':rid,'rev':rev}


def digest(value):
    return hashlib.sha256(dumps(value).encode()).hexdigest()


def text_key(value):
    return ' '.join(value.casefold().split())


def build(root,at,*,plan_path=None,ledger_path=None,assistance_id=None,actor=None,
          expected_counts=(5,29,7),task=None,verification_steps=None):
    """Build one explicitly bounded batch; omitted options reproduce batch A."""
    plan_path=PLAN if plan_path is None else plan_path
    ledger_path=LEDGER if ledger_path is None else ledger_path
    assistance_id=AID if assistance_id is None else assistance_id
    actor=ACTOR if actor is None else actor
    if (plan_path!=PLAN or ledger_path!=LEDGER or assistance_id!=AID) and (task is None or verification_steps is None):
        raise ValueError('Configured batch needs its own task and verification narrative')
    artifacts={}
    def artifact(path,expected=None):
        blob=(root/path).read_bytes();sha=hashlib.sha256(blob).hexdigest()
        if expected is not None and sha!=expected:raise ValueError('Artifact hash mismatch: '+path)
        artifacts[path]={'path':path,'sha256':sha}
        return blob
    plan=json.loads(artifact(plan_path))
    if (len(plan['sources']),len(plan['selected']),len(plan['deferred']))!=expected_counts:
        raise ValueError('Fixed scope/count disagreement')
    source_ids=[s['source_id'] for s in plan['sources']]
    dois=[s['doi'] for s in plan['sources']]
    selected_ids=[s['hit_ref']['id'] for s in plan['selected']]
    deferred_ids={s['hit_ref']['id'] for s in plan['deferred']}
    if (len(set(source_ids))!=len(source_ids) or len(set(dois))!=len(dois)
            or len(set(selected_ids))!=len(selected_ids) or len(deferred_ids)!=len(plan['deferred'])
            or set(selected_ids)&deferred_ids):
        raise ValueError('Duplicate or overlapping fixed-plan identities')
    if {s['source_id'] for s in plan['selected']}!=set(source_ids):
        raise ValueError('Each source needs qualified occurrence evidence')
    output={};source_bodies={};source_rows=[]
    for spec in plan['sources']:
        sid=spec['source_id'];capture=spec['capture']
        metadata=json.loads(artifact(capture['path'],capture['sha256']));m=metadata['record']
        if metadata['http_status']!=200 or normalize_doi(m['DOI'])!=spec['doi'] or m['title'][0]!=spec['title']:
            raise ValueError('Crossref identity disagreement: '+sid)
        if not metadata['url'].startswith('https://api.crossref.org/works/') or normalize_doi(metadata['requested_doi'])!=spec['doi']:
            raise ValueError('Crossref request provenance disagreement')
        date_field='published-print' if m.get('published-print',{}).get('date-parts') else 'issued'
        parts=m[date_field]['date-parts'][0]
        date='-'.join(str(p).zfill(4 if i==0 else 2) for i,p in enumerate(parts))
        authors=[{'name':' '.join(a.get(k,'') for k in ('given','family')).strip(),'role':'author'} for a in m['author']]
        edition='; '.join([*m.get('container-title',[]),*(str(m[k]) for k in ('volume','issue','page') if k in m)])
        source_types={'journal-article':'article','proceedings-article':'conference_paper','book-chapter':'chapter'}
        if m['type'] not in source_types:raise ValueError('Unreviewed Crossref publication type')
        body={'title':m['title'][0],'authors':authors,'publication_date':{'state':'known','value':date},
            'identifiers':[{'scheme':'doi','value':spec['doi'],'status':'verified','provenance':capture['path']+' record.DOI/title/author; HTTP 200 on '+metadata['retrieved_at']}],
            'source_type':source_types[m['type']],
            'language':{'state':'not_reported','reason':'Language not inferred from an English metadata title.'},
            'edition':{'state':'known','value':edition or 'Crossref bibliographic record; article edition not independently inspected'},
            'metadata_status':'verified','metadata_evidence':[
                capture['path']+' record.DOI, title, author and dates; retained derivative SHA256 '+capture['sha256'],
                'Explicit DOI and full title cross-checked against the pinned retained discovery exports in '+ledger_path+'.',
                'publication_date uses Crossref '+date_field+'; issued/online/print date assertions are retained separately in the capture, not silently reconciled.'],
            'access_status':'metadata_only','access_at':metadata['retrieved_at'],
            'access_reason':'Crossref bibliographic identity metadata consulted; no abstract/article/PDF reading or availability verification. Original raw response is not committed; selected bibliographic derivative is retained.',
            'rights':{'status':'unknown','reason':'No article reuse or redistribution permission verified; only bibliographic metadata retained.',
                      'evidence':{'state':'unknown','reason':'No licence decision made from metadata availability.'}},
            'validity':'active','family_links':[],'manifestations':[]}
        inputs=[i['hit_ref'] for i in plan['selected'] if i['source_id']==sid]
        revision={'rev':1,'at':at,'actor':actor,'basis':inputs+[pin(assistance_id)],'factual_status':'source_reported','data':body}
        path=AREA+'/records/'+sid+'.json'
        output[path]={'id':sid,'kind':'source','issue':6,'schema_version':1,'synthetic':False,'revisions':[revision]}
        source_bodies[sid]=body
        source_rows.append({'source_ref':pin(sid),'path':path,'revision_sha256':digest(revision),'capture':capture,
                            'selected_publication_date_field':date_field,'reported_dates':{k:m[k] for k in ('issued','published-online','published-print') if k in m}})
    occurrences=[];representatives={};cache={}
    for item in plan['selected']:
        hid=item['hit_ref']['id'];sid=item['source_id'];doi=item['doi']
        lane='pilot' if hid.startswith('HIT-R002-') else 'related' if hid.startswith('HIT-R004-') else 'auditory'
        path=f'research/searches/{lane}/records/hits/{hid}.json'
        record=read_json(root/path);original=record['revisions'][item['hit_ref']['rev']-1];before=original['data']
        if item['hit_ref']['rev']!=1 or before['status']!='unresolved':raise ValueError('Original scope/status disagreement')
        ds={d for i in before['returned_identifiers'] if i['scheme'] in {'doi','url'} and (d:=normalize_doi(i['value']))}
        if ds!={doi}:raise ValueError('Original DOI disagreement: '+hid)
        sp=f'research/searches/{lane}/records/'+before['search_ref']['id']+'.json'
        search=read_json(root/sp)['revisions'][before['search_ref']['rev']-1];exp=search['data']['export']['value']
        manifest=json.loads(artifact(exp['path'],exp['sha256']));ordinal=before['ordinal']
        platform=search['data']['platform']
        if 'OpenAlex' in platform:
            label=before['search_ref']['id'].rsplit('-',1)[1];key=(exp['path'],label)
            if key not in cache:
                works=[]
                for page in manifest['runs'][label]['pages']:
                    if 'results' not in page:continue
                    raw=gzip.decompress(artifact(page['file'],page['sha256']))
                    if hashlib.sha256(raw).hexdigest()!=page['payload_sha256']:raise ValueError('Payload hash mismatch')
                    rows=json.loads(raw)['results']
                    if len(rows)!=page['results']:raise ValueError('Page count mismatch')
                    works.extend((r,page['file'],i+1) for i,r in enumerate(rows))
                cache[key]=works
            row,page_path,index=cache[key][ordinal-1];title=row['display_name'];actual_doi=normalize_doi(row['doi'])
            if not any(i['value']==row['id'] for i in before['returned_identifiers']):raise ValueError('Work ID disagreement')
            locator={'path':page_path,'item':index,'work_id':row['id'],'reported_publication_date':row.get('publication_date')}
        elif platform=='Crossref REST API':
            label=before['search_ref']['id'].removeprefix('SRCH-R004-LK-');entry=manifest['lookups'][label]
            rows=json.loads(artifact(entry['file'],entry['sha256']))['message']['items']
            row=rows[ordinal-1];title=row['title'][0];actual_doi=normalize_doi(row['DOI'])
            locator={'path':entry['file'],'item':ordinal}
        elif hid=='HIT-R002-N3-05':
            run=next(r for b in manifest['batches'] for r in b['runs'] if r['label']=='N3')
            row=run['results'][ordinal-1];title=row['title'];actual_doi=normalize_doi(row['url'])
            if before['raw_metadata']!=title+' | '+row['url'] or search['data']['query']!=run['query']:raise ValueError('Web export disagreement')
            locator={'path':exp['path'],'run':'N3','item':ordinal}
        else:raise ValueError('Unreviewed export format')
        expected_title=source_bodies[sid]['title']
        title_agrees=(text_key(title)==text_key(expected_title) if hid!='HIT-R002-N3-05' else text_key(title).startswith(text_key(expected_title)+' - '))
        if actual_doi!=doi or not title_agrees or text_key(expected_title) not in text_key(before['raw_metadata']):
            raise ValueError('Retained DOI/full-title disagreement: '+hid)
        duplicate=sid in representatives;after=copy.deepcopy(before)
        after.update(status='duplicate' if duplicate else 'resolved',source_ref=pin(sid),
            resolution_reason='R006: explicit DOI and full title agree between retained original export and fresh Crossref identity metadata. Metadata-only source; no eligibility, source reading, version alias or independent-study assertion. See '+ledger_path)
        basis=[item['hit_ref'],before['search_ref'],pin(sid),pin(assistance_id)]
        if duplicate:after['duplicate_of']=representatives[sid];basis.append(representatives[sid])
        else:representatives[sid]=pin(hid,2)
        revision={'rev':2,'at':at,'actor':actor,'basis':basis,'factual_status':'derived','data':after}
        output[path]={**record,'revisions':[copy.deepcopy(original),revision]}
        occurrences.append({'hit_id':hid,'path':path,'input_ref':item['hit_ref'],'output_ref':pin(hid,2),
            'input_revision_sha256':digest(original),'output_revision_sha256':digest(revision),
            'source_ref':pin(sid),'status':after['status'],'duplicate_of':after.get('duplicate_of'),
            'search_ref':before['search_ref'],'ordinal':ordinal,'doi':doi,'export_locator':locator})
    inputs=[i['hit_ref'] for i in plan['selected']]
    output[AREA+'/records/'+assistance_id+'.json']={'id':assistance_id,'issue':6,'kind':'assistance','schema_version':1,'synthetic':False,
        'revisions':[{'rev':1,'at':at,'actor':actor,'basis':inputs,'factual_status':'derived','data':{
        'subtype':'assistance','status':'performed','performed_at':{'state':'known','value':at},
        'task':task or 'Verify five new publication identities using fresh Crossref metadata and resolve 29 pinned discovery occurrences.',
        'input_refs':inputs,'output_refs':[pin(s['source_id']) for s in plan['sources']]+[o['output_ref'] for o in occurrences],
        'artifacts':[plan_path,ledger_path,AREA+'/README.md'],
        'verification_steps':verification_steps or ['Retrieved Crossref single-work bibliographic metadata for five explicit DOIs; kept selected-field derivatives and original-response hashes, omitting abstracts.',
            'Checked retained search export/page hashes, original ordinals/work IDs, explicit DOI and full title before source linking.',
            'Kept print/online/issued dates distinct and the Blattner abstract-only DOI separate from the full article. Deferred seven reference-list occurrences outside reviewed export formats.'],
        'limitations':'Metadata-only access, no article/abstract reading or empirical extraction. Crossref registration metadata and retained discovery are not independent human scientific review. No eligibility, study/sample links or corpus acceptance. Raw Crossref response bytes are not retained; selected bibliographic derivatives are hash-pinned.',
        'independence':'One Codex/GPT-6 agent with software self-review; no independent human adjudication.'}}]}
    ledger={'artifact_kind':'bounded_new_publication_identity_tranche','issue':6,'resolved_at':at,'actor':actor,
        'implementation_base':plan['accepted_base'],'sources':source_rows,'occurrences':occurrences,'deferred':plan['deferred'],
        'input_artifacts':[artifacts[p] for p in sorted(artifacts)],
        'counts':{'occurrences':len(occurrences),'new_source_records':len(source_rows),'resolved_representatives':len(representatives),'duplicate_occurrences':sum(o['status']=='duplicate' for o in occurrences),
                  'deferred_occurrences':len(plan['deferred']),'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0},
        'boundary':('Five publication identities, not five independent studies. Metadata-only access. Issue #6/corpus gate remain open.'
                    if len(source_rows)==5 else f'{len(source_rows)} publication identities; no independent-study count or corpus acceptance. Metadata-only access.')}
    return output,ledger


def main(*,root=None,build_options=None):
    root=ROOT if root is None else root;options=build_options or {}
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();target=root/(options.get('ledger_path') or LEDGER)
    if args.check and not target.exists():raise SystemExit('Frozen tranche ledger is missing')
    at=read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    records,ledger=build(root,at,**options)
    if target.exists() and read_json(target)!=ledger:raise SystemExit('Frozen new-publication ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual=read_json(root/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:raise SystemExit('New-publication record prefix drift: '+path)
        print('Five metadata-only source identities and 29 occurrence resolutions reproduce.' if not options else f"{len(ledger['sources'])} metadata-only identities and {len(ledger['occurrences'])} resolutions reproduce.")
    else:
        write_generated_records(root,records);target.write_text(dumps(ledger),encoding='utf-8')
        print('Recorded 5 metadata-only sources; 29 occurrences (5 representatives, 24 duplicates); 7 deferred.' if not options else f"Recorded {len(ledger['sources'])} metadata-only sources and {len(ledger['occurrences'])} occurrence resolutions.")


if __name__=='__main__':main()
