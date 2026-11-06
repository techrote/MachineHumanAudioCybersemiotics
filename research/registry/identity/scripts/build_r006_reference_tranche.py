"""Resolve seven deferred bibliography occurrences from fixed source witnesses."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from tools.record_io import dumps,read_json
from tools.records import write_generated_records
from tools.screening import normalize_doi

AREA='research/registry/identity'
PLAN=AREA+'/R006-NEW-DOI-PLAN-20261106.json'
PREVIOUS=AREA+'/R006-NEW-PUBLICATIONS-20261106.json'
RECEIPT=AREA+'/R006-REFERENCE-WITNESSES-20261106.json'
LEDGER=AREA+'/R006-REFERENCE-TRANCHE-20261106.json'
AID='AID-R006-REFERENCE-TRANCHE-20261106'
ACTOR={'kind':'agent','id':'codex-r006-reference-provenance-20261106','model':'GPT-6',
       'tool':'Codex; urllib same-byte PDF retrieval, pypdf/Poppler bibliography inspection and retained-export comparison'}
CASES={
 'HIT-R005-RLFRAPDF-103':('RL-FRAPDF','fra-walker'),
 'HIT-R005-RLNL-047':('RL-NL','nees-perry'),
 'HIT-R005-RLNL-064':('RL-NL','nees-walker'),
 'HIT-R005-RLNLAM-047':('RL-NLAM','nees-perry'),
 'HIT-R005-RLNLAM-064':('RL-NLAM','nees-walker'),
 'HIT-R005R-C9NLGENERAL-00029':('general','nees-edworthy'),
 'HIT-R005R-C9RUSKIN-00125':('ruskin','ruskin-perry'),
}


def pin(rid,rev=1):return {'id':rid,'rev':rev}


def digest(value):return hashlib.sha256(dumps(value).encode()).hexdigest()


def key(value):return ' '.join(value.casefold().split())


def build(root,at,*,profile=None):
    config={
        'plan':PLAN,'previous':PREVIOUS,'receipt':RECEIPT,'ledger':LEDGER,
        'aid':AID,'actor':ACTOR,'cases':CASES,
        'base':'8f5e15e0445ffd70495fe15e434b6799098acced',
        'task':'Verify seven deferred bibliography occurrence identities using three freshly retrieved hash-matched review/report PDFs and five visually checked citation witnesses.',
        'steps':['All three retrieved PDFs returned HTTP 200 and match the retained original SHA-256 exactly.',
            'Rendered/inspected Nees AM file pages 36,49,51; FRA 41-42 (citation spans page break); Ruskin 71. Inspection limited to selected bibliography citations.',
            'Checked original export/hash/ordinal, full or explicitly abbreviated title, explicit DOI and existing resolved representative. Two rendered short entries receive corroboration, not transcription/source-version acceptance.'],
        'limitations':'No cited target article was retrieved/read; target source records remain metadata_only. Selected review/report reference pages were checked, not complete reports or empirical results. One agent; no independent human verification, version alias, sample identity, eligibility or corpus acceptance. PDFs/renders are not committed; exact receipt hashes/URLs and locators are retained.',
        'counts':{'occurrences':7,'duplicate_occurrences':7,'existing_target_publications':3,'source_pdf_retrievals':3,
            'visually_checked_citation_witnesses':5,'corroborated_model_abbreviations':2,'new_source_records':0,
            'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0},
    }
    if profile is not None:
        if set(profile)!=set(config):raise ValueError('Profile must supply its complete fixed scope and verification narrative')
        config=copy.deepcopy(profile)
    plan_path,previous_path,receipt_path,ledger_path=(config[k] for k in ('plan','previous','receipt','ledger'))
    aid,actor,cases=(config[k] for k in ('aid','actor','cases'))
    artifacts={}
    def artifact(path,expected=None):
        blob=(root/path).read_bytes();sha=hashlib.sha256(blob).hexdigest()
        if expected is not None and sha!=expected:raise ValueError('Artifact hash mismatch: '+path)
        artifacts[path]={'path':path,'sha256':sha};return blob
    plan=json.loads(artifact(plan_path));previous=json.loads(artifact(previous_path));receipt=json.loads(artifact(receipt_path))
    if parent_pin:=plan.get('parent_plan'):
        parent=json.loads(artifact(parent_pin['path'],parent_pin['sha256']))
        scope=plan['deferred']+plan['remaining_deferred']
        sort=lambda rows:sorted(rows,key=lambda row:row['hit_ref']['id'])
        if (len({row['hit_ref']['id'] for row in scope})!=len(scope)
                or sort(scope)!=sort(parent['deferred'])):
            raise ValueError('Parent deferred scope disagreement')
    if len(plan['deferred'])!=len(cases) or {i['hit_ref']['id'] for i in plan['deferred']}!=set(cases):raise ValueError('Fixed deferred scope disagreement')
    pdfs={r['key']:r for r in receipt['retrievals']};witnesses={w['key']:w for w in receipt['witnesses']}
    if len(pdfs)!=len(receipt['retrievals']) or len(witnesses)!=len(receipt['witnesses']):raise ValueError('Repeated receipt identity')
    if {c[1] for c in cases.values()}!=set(witnesses) or {w['pdf_key'] for w in witnesses.values()}!=set(pdfs):raise ValueError('Receipt scope disagreement')
    for pdf in pdfs.values():
        if pdf.get('http_status')!=200 or not pdf.get('pdf_header') or not pdf.get('hash_matches') or pdf['sha256']!=pdf['expected_sha256']:
            raise ValueError('Same-byte source PDF receipt failed')
    representatives={o['source_ref']['id']:o for o in previous['occurrences'] if o['status']=='resolved'}
    output={};occurrences=[]
    for item in plan['deferred']:
        hid=item['hit_ref']['id'];sid=item['source_id'];doi=item['doi'];label,wkey=cases[hid]
        witness=witnesses[wkey];pdf=pdfs[witness['pdf_key']]
        source_path=AREA+'/records/'+sid+'.json';source=read_json(root/source_path)['revisions'][0];body=source['data']
        if body['metadata_status']!='verified' or body['validity']!='active' or doi not in {normalize_doi(i['value']) for i in body['identifiers'] if i['scheme']=='doi' and i['status']=='verified'}:
            raise ValueError('Unverified target publication identity')
        if witness['checked_source_ref']!=pin(sid) or witness['checked_doi']!=doi or witness['checked_full_title']!=body['title']:
            raise ValueError('PDF witness identity disagreement')
        comparison_title=body['title']
        if capture_pin:=witness.get('title_subtitle_capture'):
            # Explicit opt-in only: use the exact prior DOI ledger's deposited fields,
            # never a witness-supplied expanded title or a fuzzy similarity rule.
            prior=next((s for s in previous.get('sources',[]) if s['source_ref']==pin(sid)),None)
            if label not in {'RL-NL','RL-NLAM'} or prior is None or capture_pin!=prior['capture']:
                raise ValueError('Title/subtitle capture pin disagreement')
            capture=json.loads(artifact(capture_pin['path'],capture_pin['sha256']));registered=capture['record']
            subtitles=registered.get('subtitle',[])
            if (capture.get('http_status')!=200 or normalize_doi(capture.get('requested_doi',''))!=doi
                    or normalize_doi(registered.get('DOI',''))!=doi or registered.get('title')!=[body['title']]
                    or not isinstance(subtitles,list) or len(subtitles)!=1
                    or not isinstance(subtitles[0],str) or not subtitles[0].strip()
                    or registered.get('relation') or registered.get('update-to')):
                raise ValueError('Registered title/subtitle identity disagreement')
            comparison_title=body['title']+': '+subtitles[0]
        if not witness['file_pages_1based'] or any(p<1 or p>pdf['page_count'] for p in witness['file_pages_1based']):raise ValueError('PDF witness page bounds disagreement')
        representative=representatives[sid];rep_record=read_json(root/representative['path'])
        rep=rep_record['revisions'][representative['output_ref']['rev']-1]
        if rep['data']['status']!='resolved' or rep['data']['source_ref']!=pin(sid):raise ValueError('Representative source disagreement')
        path='research/searches/auditory/records/hits/'+hid+'.json';record=read_json(root/path);original=record['revisions'][0];before=original['data']
        ds={d for i in before['returned_identifiers'] if i['scheme'] in {'doi','url'} and (d:=normalize_doi(i['value']))}
        if before['status']!='unresolved' or ds!={doi}:raise ValueError('Original occurrence DOI/status disagreement')
        search=read_json(root/('research/searches/auditory/records/'+before['search_ref']['id']+'.json'))['revisions'][before['search_ref']['rev']-1]
        exp=search['data']['export']['value'];export=json.loads(artifact(exp['path'],exp['sha256']));ordinal=before['ordinal']
        if label.startswith('RL-'):
            section=next(s for s in export['reference_lists'] if s['label']==label);row=section['entries'][ordinal-1];text=row['text']
            expected=('['+row['outcome_letters']+'] '+text) if label=='RL-NLAM' else text
            if row['ordinal']!=ordinal or before['raw_metadata']!=expected:raise ValueError('Original reference export disagreement')
            locator={'path':exp['path'],'reference_list':label,'item':ordinal}
            if label=='RL-NL':
                opening=re.search(r': "([^"]+)";',text)
                if not opening:raise ValueError('Abbreviated title disagreement')
                short,full_title=key(opening[1]),key(comparison_title)
                if capture_pin:
                    if (not short.startswith(key(body['title'])+': ')
                            or not (full_title==short or full_title.startswith(short+' '))):
                        raise ValueError('Registered title/subtitle prefix disagreement')
                elif not full_title.startswith(short):raise ValueError('Abbreviated title disagreement')
                corroborating=next(s for s in export['reference_lists'] if s['label']=='RL-NLAM')
                full=corroborating['entries'][ordinal-1]
                if full['ordinal']!=ordinal or doi not in full['text'].lower() or key(comparison_title) not in key(full['text']):raise ValueError('Rendered entry lacks matching full citation corroboration')
                if corroborating['manifestation']['sha256']!=pdf['sha256']:raise ValueError('Corroborating PDF hash disagreement')
                locator['corroborating_reference_list']='RL-NLAM'
                extent='Original model-rendered short title retained; publication identity corroborated by the Nees AM full citation. No claim of faithful original-preprint transcription or version equivalence.'
            else:
                if section['manifestation']['sha256']!=pdf['sha256']:raise ValueError('Reference source PDF hash disagreement')
                if key(comparison_title) not in key(text):raise ValueError('Full citation title disagreement')
                extent='Original byte-parsed citation checked against fresh same-byte PDF reference pages.'
            if capture_pin:extent+=' Deposited main title and subtitle checked separately in the hash-bound prior DOI capture; only an exact word-boundary prefix of their combined citation form is accepted.'
        elif label=='general':
            section=next(s for s in export['sources'] if s['label']=='nees-liebman-am');row=section['entries'][ordinal-1];text=row['text']
            if section['sha256']!=pdf['sha256'] or [row['file_page_start'],row['file_page_end']]!=[witness['file_pages_1based'][0]]*2:raise ValueError('General-reference source/page disagreement')
            expected=text+f" | source PDF pp.{row['file_page_start']}–{row['file_page_end']}, reference {ordinal}"
            if row['ordinal']!=ordinal or before['raw_metadata']!=expected or key(body['title']) not in key(text):raise ValueError('General-reference export disagreement')
            locator={'path':exp['path'],'section':section['section'],'item':ordinal};extent='Byte-derived general-bibliography citation and original page locator checked against fresh same-byte PDF.'
        elif label in {'ruskin','totland'}:
            row=export['references'][ordinal-1];text=row['citation_text']
            if export['source_sha256']!=pdf['sha256'] or row['pdf_pages']!=witness['file_pages_1based']:raise ValueError('Ruskin source/page disagreement')
            if row['ordinal']!=ordinal or not before['raw_metadata'].startswith(text+' | '+row['occurrence_id']+' | ') or key(body['title']) not in key(text):raise ValueError('Ruskin reference export disagreement')
            locator={'path':exp['path'],'item':ordinal,'occurrence_id':row['occurrence_id'],'pdf_pages':row['pdf_pages']};extent='Coordinate-bearing bibliography citation and original page/line provenance checked against fresh same-byte PDF.'
        else:raise ValueError('Unreviewed reference export format')
        if doi not in text.lower():raise ValueError('Reference text DOI disagreement')
        after=copy.deepcopy(before);after.update(status='duplicate',source_ref=pin(sid),duplicate_of=representative['output_ref'],
            resolution_reason='R006: reference publication identity checked against retained export, accepted DOI/title metadata and fresh hash-matched PDF bibliography witness. '+extent+' No eligibility, empirical extraction or independent-study assertion. See '+ledger_path)
        revision={'rev':2,'at':at,'actor':actor,'basis':[item['hit_ref'],before['search_ref'],pin(sid),representative['output_ref'],pin(aid)],'factual_status':'derived','data':after}
        output[path]={**record,'revisions':[copy.deepcopy(original),revision]}
        occurrences.append({'hit_id':hid,'path':path,'input_ref':item['hit_ref'],'output_ref':pin(hid,2),'source_ref':pin(sid),
            'input_revision_sha256':digest(original),'output_revision_sha256':digest(revision),'source_revision_sha256':digest(source),
            'duplicate_of':representative['output_ref'],'doi':doi,'export_locator':locator,'witness_key':wkey,
            'source_pdf_sha256':pdf['sha256'],'file_pages_1based':witness['file_pages_1based'],'verification_extent':extent})
    observed_counts={'occurrences':len(occurrences),'duplicate_occurrences':len(occurrences),
        'existing_target_publications':len({o['source_ref']['id'] for o in occurrences}),
        'source_pdf_retrievals':len(pdfs),'visually_checked_citation_witnesses':len(witnesses),
        'corroborated_model_abbreviations':sum(c[0]=='RL-NL' for c in cases.values()),
        'new_source_records':0,'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0}
    if observed_counts!=config['counts']:raise ValueError('Fixed profile count disagreement')
    inputs=[i['hit_ref'] for i in plan['deferred']]+[pin(s) for s in sorted({i['source_id'] for i in plan['deferred']})]
    output[AREA+'/records/'+aid+'.json']={'id':aid,'issue':6,'kind':'assistance','schema_version':1,'synthetic':False,'revisions':[{
        'rev':1,'at':at,'actor':actor,'basis':inputs,'factual_status':'derived','data':{
        'subtype':'assistance','status':'performed','performed_at':{'state':'known','value':at},
        'task':config['task'],
        'input_refs':inputs,'output_refs':[o['output_ref'] for o in occurrences],'artifacts':[receipt_path,ledger_path,AREA+'/README.md'],
        'verification_steps':config['steps'],
        'limitations':config['limitations'],
        'independence':'One Codex/GPT-6 agent and software self-review; no independent human adjudication.'}}]}
    ledger={'artifact_kind':'bounded_reference_identity_tranche','issue':6,'resolved_at':at,'actor':actor,
        'implementation_base':config['base'],'occurrences':occurrences,
        'input_artifacts':[artifacts[p] for p in sorted(artifacts)],'source_receipt':receipt_path,
        'counts':observed_counts,
        'boundary':'Identity of cited publications only. Original model-rendered provenance and search incompleteness remain intact; issue #6/corpus gate stay open.'}
    return output,ledger


def main(*,root=None,profile=None):
    root=ROOT if root is None else root
    ledger_path=LEDGER if profile is None else profile['ledger']
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();target=root/ledger_path
    if args.check and not target.exists():raise SystemExit('Frozen tranche ledger is missing')
    at=read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    records,ledger=build(root,at,profile=profile)
    if target.exists() and read_json(target)!=ledger:raise SystemExit('Frozen reference ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual=read_json(root/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:raise SystemExit('Reference tranche record prefix drift: '+path)
        print(str(ledger['counts']['occurrences'])+' bibliography duplicate resolutions reproduce; source-verification limits retained.')
    else:
        write_generated_records(root,records);target.write_text(dumps(ledger),encoding='utf-8');print('Recorded '+str(ledger['counts']['occurrences'])+' bibliography duplicates; no new sources or eligibility decisions.')


if __name__=='__main__':main()
