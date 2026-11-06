"""Reproduce the fixed Ferreira original/correction identity review; never screen studies."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from tools.record_io import dumps,read_json
from tools.records import write_generated_records
from tools.screening import normalize_doi
from research.registry.identity.scripts.build_r006_new_publications import digest,pin,text_key

AREA='research/registry/identity'
PLAN=AREA+'/R006-FERREIRA-CORRECTION-PLAN-20261106.json'
RECEIPT=AREA+'/R006-FERREIRA-CORRECTION-WITNESS-20261106.json'
LEDGER=AREA+'/R006-FERREIRA-CORRECTION-20261106.json'
ORIGINAL='SRC-R006-G-FERREIRA-ERP'
NOTICE='SRC-R006-G-FERREIRA-CORRECTION'
READING='AID-R006-FERREIRA-NOTICE-READING-20261106'
AID='AID-R006-FERREIRA-CORRECTION-20261106'
OD='10.1371/journal.pone.0281680'
ND='10.1371/journal.pone.0295826'
PDF_SHA='bb7420089cf82b07e78ab4756efe5588a35de81b9da9dfe58c01d9b292905ccb'
NOTICE_HIT='HIT-R005R-C1RECOVERY-EQ1-00705'
HITS={'HIT-R005R-C1RECOVERY-EQ5-00158','HIT-R005R-C1LOAD-EQ5-01402','HIT-R005R-C1RECOVERY-EQ1-00537'}
ACTOR={'kind':'agent','id':'codex-r006-ferreira-correction-20261106','model':'GPT-6',
       'tool':'Codex; fresh Crossref metadata, publisher correction PDF/Poppler reading and retained-export comparison'}


def build(root,at,*,plan_path=PLAN,receipt_path=RECEIPT):
    artifacts={}
    def artifact(path,expected=None):
        raw=(root/path).read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if expected is not None and sha!=expected:raise ValueError('Artifact hash mismatch: '+path)
        artifacts[path]={'path':path,'sha256':sha};return raw
    plan=json.loads(artifact(plan_path));receipt=json.loads(artifact(receipt_path))
    if plan['original_doi']!=OD or plan['notice_doi']!=ND:raise ValueError('Fixed DOI scope disagreement')
    refs=plan['held_occurrences']
    if len(refs)!=3 or {r['id'] for r in refs}!=HITS or any(r['rev']!=1 for r in refs):raise ValueError('Fixed held occurrence scope disagreement')
    if plan['notice_occurrence']!=pin(NOTICE_HIT):raise ValueError('Fixed notice occurrence scope disagreement')
    parent=json.loads(artifact(plan['parent_plan']['path'],plan['parent_plan']['sha256']))
    held=[g for g in parent['not_admitted'] if g['doi']==OD]
    if len(held)!=1 or sorted(held[0]['hit_refs'],key=lambda r:r['id'])!=sorted(refs,key=lambda r:r['id']):raise ValueError('Parent held scope disagreement')
    original=json.loads(artifact(plan['original_capture']['path'],plan['original_capture']['sha256']))
    notice=json.loads(artifact(plan['notice_capture']['path'],plan['notice_capture']['sha256']))
    old=json.loads(artifact(held[0]['capture']['path'],held[0]['capture']['sha256']))
    for capture,doi in [(original,OD),(notice,ND)]:
        if (capture['http_status']!=200 or normalize_doi(capture['requested_doi'])!=doi
                or normalize_doi(capture['record']['DOI'])!=doi
                or not capture['url'].startswith('https://api.crossref.org/works/')):raise ValueError('Registration/request identity disagreement')
    om,nm=original['record'],notice['record']
    relation=om.get('relation',{})
    if (set(relation)!={'correction'} or len(relation['correction'])!=1
            or normalize_doi(relation['correction'][0].get('id'))!=ND
            or relation['correction'][0].get('id-type')!='doi' or om.get('update-to')):raise ValueError('Original correction relation disagreement')
    updates=nm.get('update-to',[])
    if (len(updates)!=1 or normalize_doi(updates[0].get('DOI'))!=OD or updates[0].get('type')!='correction'
            or updates[0].get('source')!='publisher' or nm.get('relation')):raise ValueError('Notice correction target disagreement')
    if (om['title']!=old['record']['title'] or normalize_doi(old['record']['DOI'])!=OD
            or nm['title']!=['Correction: '+om['title'][0]]):raise ValueError('Original/notice title disagreement')
    names=lambda m:[' '.join(a.get(k,'') for k in ('given','family')).strip() for a in m['author']]
    if names(om)!=names(nm) or len(names(om))!=8:raise ValueError('Author identity/order disagreement')
    if om['issued']['date-parts']!=[[2023,2,16]] or nm['issued']['date-parts']!=[[2023,12,7]]:raise ValueError('Fixed publication dates disagreement')
    if any(m['type']!='journal-article' or m['container-title']!=['PLOS ONE'] for m in [om,nm]):raise ValueError('Registration venue/type disagreement')
    pdf=receipt['retrieval']
    if (pdf['http_status']!=200 or not pdf['pdf_header'] or pdf['sha256']!=PDF_SHA or pdf['page_count']!=1
            or pdf['url']!='https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0295826&type=printable'):raise ValueError('Publisher PDF receipt disagreement')
    if (receipt['checked_original_doi']!=OD or receipt['checked_notice_doi']!=ND
            or receipt['checked_notice_title']!=nm['title'][0] or receipt['notice_source_ref']!=pin(NOTICE)):raise ValueError('Publisher notice identity witness disagreement')
    if (receipt['file_pages_1based']!=[1] or receipt['reading_status']!='full_item_read' or receipt['original_article_read'] is not False
            or receipt['rights_statement_checked'] is not True or receipt['results_effect_assessment']!='not_performed'
            or receipt['correction_topics']!=['corresponding_author','affiliations','funding']):raise ValueError('Notice reading/scope boundary disagreement')
    inputs=sorted(refs+[plan['notice_occurrence']],key=lambda r:r['id']);output={}
    def record(rid,kind,body,basis,status='source_reported'):
        return {'id':rid,'kind':kind,'issue':6,'schema_version':1,'synthetic':False,'revisions':[{
            'rev':1,'at':at,'actor':ACTOR,'basis':basis,'factual_status':status,'data':body}]}
    def source(capture,spec,is_notice):
        m=capture['record'];date='-'.join(str(v).zfill(4 if n==0 else 2) for n,v in enumerate(m['issued']['date-parts'][0]))
        return {'title':m['title'][0],'authors':[{'name':n,'role':'author'} for n in names(m)],
            'publication_date':{'state':'known','value':date},'identifiers':[{'scheme':'doi','value':ND if is_notice else OD,'status':'verified','provenance':spec['path']+' record.DOI/title/author; HTTP 200 on '+capture['retrieved_at']}],
            'source_type':'correction' if is_notice else 'article','language':{'state':'not_reported','reason':'Language not inferred from metadata.'},
            'edition':{'state':'known','value':'; '.join([*m['container-title'],m['volume'],m['issue'],m['page']])},
            'metadata_status':'verified','metadata_evidence':[spec['path']+'; SHA256 '+spec['sha256'],
                'Publisher notice p.1 and reciprocal Crossref original relation.correction / notice update-to confirm distinct original and correction identities; see '+RECEIPT,
                'Correction scope: corresponding author, omitted affiliations and funding disclosure; original paper methods/results not assessed. Source first registered with correction already known; no earlier local active revision is invented.'],
            'access_status':'full_text_available' if is_notice else 'metadata_only','access_at':pdf['at'] if is_notice else capture['retrieved_at'],
            'access_reason':'Complete one-page publisher correction notice retrieved and read; original article not read.' if is_notice else 'Bibliographic registration and notice Reference 1 checked; original article/abstract not retrieved or read.',
            'rights':({'status':'redistribution_permitted','reason':'Publisher correction PDF p.1 states Creative Commons Attribution terms permitting redistribution with author/source credit; no licence version inferred.',
                       'evidence':{'state':'known','value':RECEIPT+' rights_witness; publisher correction PDF p.1 copyright sidebar'}} if is_notice else
                      {'status':'unknown','reason':'Correction-notice reuse terms are not transferred to the original article.','evidence':{'state':'unknown','reason':'Original article reuse terms not inspected.'}}),
            'validity':'active' if is_notice else 'corrected',
            'family_links':[{'relation':'correction_of','source_ref':pin(ORIGINAL),'reason':'Publisher notice Reference 1 and reciprocal Crossref relation/update-to identify the original. Not a second experiment, sample or source alias.'}] if is_notice else [],
            'manifestations':[{'id':'MAN-R006-FERREIRA-CORRECTION-PDF','sha256':PDF_SHA,'extent':1,'coordinate':'file_page_1based','location':'Public publisher correction PDF '+pdf['url']+'; local bytes/renders not committed.'}] if is_notice else []}
    output[AREA+'/records/'+NOTICE+'.json']=record(NOTICE,'source',source(notice,plan['notice_capture'],True),inputs+[pin(AID)])
    output[AREA+'/records/'+READING+'.json']=record(READING,'assistance',{
        'subtype':'reading','source_ref':pin(NOTICE),'manifestation_id':'MAN-R006-FERREIRA-CORRECTION-PDF','access_at_read':'full_text_available',
        'reading_status':'full_item_read','ranges':[[1,1]],'method':receipt['reading_extent'],'status':'performed','performed_at':{'state':'known','value':receipt['checked_at']},
        'independence':receipt['independence']},[pin(NOTICE)])
    output[AREA+'/records/'+ORIGINAL+'.json']=record(ORIGINAL,'source',source(original,plan['original_capture'],False),inputs+[pin(NOTICE),pin(READING),pin(AID)])
    occurrences=[];representatives={};cache={}
    for ref in inputs:
        is_notice=ref['id']==NOTICE_HIT;doi,sid,m=(ND,NOTICE,nm) if is_notice else (OD,ORIGINAL,om)
        path='research/searches/auditory/records/hits/'+ref['id']+'.json';row=read_json(root/path);first=row['revisions'][0];before=first['data']
        dois={d for i in before['returned_identifiers'] if i['scheme'] in {'doi','url'} and (d:=normalize_doi(i['value']))}
        if first['rev']!=1 or before['status']!='unresolved' or dois!={doi}:raise ValueError('Original hit identity/status disagreement')
        sp='research/searches/auditory/records/'+before['search_ref']['id']+'.json';search=read_json(root/sp)['revisions'][before['search_ref']['rev']-1]['data']
        if 'OpenAlex' not in search['platform']:raise ValueError('Unreviewed occurrence platform')
        exp=search['export']['value'];manifest=json.loads(artifact(exp['path'],exp['sha256']));label=before['search_ref']['id'].rsplit('-',1)[1];key=(exp['path'],label)
        if key not in cache:
            works=[]
            for page in manifest['runs'][label]['pages']:
                if 'results' not in page:continue
                payload=gzip.decompress(artifact(page['file'],page['sha256']))
                if hashlib.sha256(payload).hexdigest()!=page['payload_sha256']:raise ValueError('Payload hash mismatch')
                results=json.loads(payload)['results']
                if len(results)!=page['results']:raise ValueError('Page count mismatch')
                works.extend((r,page['file'],n+1) for n,r in enumerate(results))
            cache[key]=works
        work,page_path,index=cache[key][before['ordinal']-1]
        if (normalize_doi(work['doi'])!=doi or text_key(work['display_name'])!=text_key(m['title'][0])
                or text_key(before['raw_metadata'].split(' | first author:',1)[0])!=text_key(m['title'][0])
                or not any(i['value']==work['id'] for i in before['returned_identifiers'])):raise ValueError('Retained DOI/full-title/work-ID disagreement')
        representative=representatives.get(sid)
        after=copy.deepcopy(before);after.update(status='resolved' if representative is None else 'duplicate',source_ref=pin(sid),
            resolution_reason=('R006: separate correction-notice DOI/full title checked against retained OpenAlex export, fresh registration and fully read publisher notice. Not an alias or independent-study assertion. See '+LEDGER if is_notice else
            'R006: original publication DOI/full title checked against retained OpenAlex export and fresh registration; separate publisher correction notice fully read and linked. Original source first registered as corrected, metadata_only; notice changes corresponding-author, affiliation and funding information. No original-paper reading, eligibility, empirical-results or independent-study assertion. See '+LEDGER))
        basis=[ref,before['search_ref'],pin(sid),pin(READING),pin(AID)]
        if not is_notice:basis.append(pin(NOTICE))
        if representative is not None:after['duplicate_of']=representative;basis.append(representative)
        revision={'rev':2,'at':at,'actor':ACTOR,'basis':basis,'factual_status':'derived','data':after};output[path]={**row,'revisions':[copy.deepcopy(first),revision]}
        occurrences.append({'hit_id':ref['id'],'path':path,'input_ref':ref,'output_ref':pin(ref['id'],2),'source_ref':pin(sid),'doi':doi,
            'input_revision_sha256':digest(first),'output_revision_sha256':digest(revision),'status':after['status'],'duplicate_of':after.get('duplicate_of'),
            'export_locator':{'path':page_path,'item':index,'work_id':work['id'],'ordinal':before['ordinal'],'reported_publication_date':work.get('publication_date')}})
        if representative is None:representatives[sid]=pin(ref['id'],2)
    output[AREA+'/records/'+AID+'.json']=record(AID,'assistance',{
        'subtype':'assistance','status':'performed','performed_at':{'state':'known','value':at},'task':'Resolve three held Ferreira original-paper occurrences plus one retained correction-notice occurrence, keeping the read notice separate from the corrected original metadata identity.',
        'input_refs':inputs,'output_refs':[pin(ORIGINAL),pin(NOTICE),pin(READING)]+[o['output_ref'] for o in occurrences],
        'artifacts':[plan_path,receipt_path,LEDGER,AREA+'/README.md'],
        'verification_steps':['Two fresh Crossref requests returned HTTP 200; selected bibliographic derivatives retained without abstracts.',
            'Publisher-linked one-page correction PDF returned HTTP 200; full rendered notice, original reference, correction paragraphs, date/DOIs and rights sidebar checked.',
            'Original registration relation.correction and notice update-to agree; all eight full author names agree despite deposited given/family splitting differences.',
            'Verified three-case held parent scope and separate retained notice occurrence, export/page/payload hashes, original DOI/full title/work IDs and append-only hit revisions. Original paper not read.'],
        'limitations':'Correction paragraph scope only; no original-paper methods/results assessment, eligibility, study/sample identity or corpus acceptance. Original access remains metadata_only; notice reading/rights do not transfer to original. Raw metadata/PDF/HTML/renders and author contact address not committed.',
        'independence':'One Codex/GPT-6 agent with software self-review; no independent human adjudication.'},inputs,'derived')
    sources=[{'source_ref':pin(rid),'path':AREA+'/records/'+rid+'.json','revision_sha256':digest(output[AREA+'/records/'+rid+'.json']['revisions'][0])} for rid in [ORIGINAL,NOTICE]]
    ledger={'artifact_kind':'bounded_correction_aware_publication_identity_tranche','issue':6,'resolved_at':at,'actor':ACTOR,'implementation_base':plan['accepted_base'],
        'sources':sources,'occurrences':occurrences,'notice_reading_ref':pin(READING),'receipt':receipt_path,'input_artifacts':[artifacts[p] for p in sorted(artifacts)],
        'counts':{'occurrences':4,'original_occurrences':3,'notice_occurrences':1,'resolved_representatives':2,'duplicate_occurrences':2,'new_source_records':2,'correction_notices':1,'notice_full_readings':1,'original_article_readings':0,'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0},
        'boundary':'Original and correction are distinct publications, not independent experiments or samples. Correction known on first source registration; no earlier local source revision or scientific acceptance invented.'}
    return output,ledger


def main(*,root=ROOT):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();target=root/LEDGER
    if args.check and not target.exists():raise SystemExit('Frozen correction ledger is missing')
    at=read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    records,ledger=build(root,at)
    if target.exists() and read_json(target)!=ledger:raise SystemExit('Frozen correction ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual=read_json(root/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:raise SystemExit('Correction record prefix drift: '+path)
        print('Three original-paper and one correction-notice occurrence identities, with notice-only reading, reproduce.')
    else:
        write_generated_records(root,records);target.write_text(dumps(ledger));print('Recorded three original-paper and one separate correction-notice links with notice-only reading.')


if __name__=='__main__':main()
