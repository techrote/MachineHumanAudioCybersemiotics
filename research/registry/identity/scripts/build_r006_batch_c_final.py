"""Resolve the seven fixed batch C residue cases with explicit presentation provenance."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import gzip
import hashlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from tools.record_io import dumps,read_json
from tools.records import write_generated_records
from tools.screening import normalize_doi
from research.registry.identity.scripts import build_r006_new_publications as E

AREA=E.AREA
PLAN=AREA+'/R006-C-FINAL-PLAN-20261106.json'
LEDGER=AREA+'/R006-C-FINAL-20261106.json'
AID='AID-R006-C-FINAL-20261106'
WILCOX='SRC-R006-WILCOX-2011-ALARMS'
TISLAR='SRC-R006-TISLAR-2018-LEARNABILITY'
VENUE='HIT-R005R-C5SERIES-01072'
UUID='7847b94c-1b79-4dea-9dba-62cfb4548102'
DOI='10.2345/0899-8205-45.4.284'
RAW_TITLE='<i>A Human Factors Perspective</i>'+chr(10)+'            : Auditory Alarm Signals'
DISPLAY_TITLE='A Human Factors Perspective : Auditory Alarm Signals'
ACTOR={'kind':'agent','id':'codex-r006-c-final-20261106','model':'GPT-6',
       'tool':'Codex; fixed Crossref title presentation, PubMed/Georgia Tech identity metadata and retained-export checks'}
OPTIONS={'plan_path':PLAN,'ledger_path':LEDGER,'assistance_id':AID,'actor':ACTOR,'expected_counts':(1,6,0),
 'task':'Resolve seven batch C residual identity cases using a fixed Wilcox title-presentation decision and exact ICAD venue provenance; record actual partial/abstract access exposure without eligibility or extraction.',
 'verification_steps':['Fixed exact raw Crossref title and DOI; retained both original and display title, with PubMed bibliographic corroboration.',
   'Checked six OpenAlex DOI/full-title occurrences through original hashes, payloads, ordinals and work IDs; checked one venue occurrence through original manifest, gzip/payload hashes, JSON pointer and fresh Georgia Tech identity fields.',
   'Recorded Wilcox publisher first-page search excerpts as partial_text and Tislar embedded abstract exposure as abstract_only. No full article or eligibility assessment.']}


def build(root,at):
    artifacts={}
    def artifact(pin):
        path=pin['path'];blob=(root/path).read_bytes();sha=hashlib.sha256(blob).hexdigest()
        if sha!=pin['sha256']:raise ValueError('Artifact hash mismatch: '+path)
        artifacts[path]={'path':path,'sha256':sha}
        import json
        return json.loads(blob)
    plan=read_json(root/PLAN);parent=artifact(plan['parent_plan']);subplan=artifact(plan['reference_subplan'])
    unadmitted,=parent['not_admitted'];old=artifact(unadmitted['capture'])
    if ({i['hit_ref']['id'] for i in plan['selected']}!={r['id'] for r in unadmitted['hit_refs']}
            or plan['venue']!=subplan['remaining_deferred'][0] or len(subplan['remaining_deferred'])!=1
            or plan['venue']['hit_ref']!=E.pin(VENUE)):
        raise ValueError('Fixed residual scope disagreement')
    raw=artifact(plan['raw_crossref']);pubmed=artifact(plan['pubmed']);fresh=artifact(plan['gatech'])
    display=artifact(plan['sources'][0]['capture'])
    for cap in (old,raw):
        if (cap['http_status']!=200 or normalize_doi(cap['record']['DOI'])!=DOI or cap['record']['title']!=[RAW_TITLE]
                or cap['record']['type']!='journal-article' or len(cap['record']['author'])!=1
                or cap['record']['author'][0].get('family')!='Wilcox'):
            raise ValueError('Fixed raw title/DOI disagreement')
    expected=copy.deepcopy(raw['record']);expected['title']=[DISPLAY_TITLE]
    if (display['record']!=expected or display['original_record_title']!=RAW_TITLE
            or display['parent_capture']!=plan['raw_crossref'] or plan['sources'][0]['source_id']!=WILCOX
            or plan['title_decision']['line_feed_codepoint']!=10 or plan['title_decision']['raw_title']!=RAW_TITLE or plan['title_decision']['display_title']!=DISPLAY_TITLE
            or E.text_key(RAW_TITLE.replace('<i>','').replace('</i>',''))!=E.text_key(DISPLAY_TITLE)):
        raise ValueError('Fixed title presentation disagreement')
    pm=pubmed['record']
    if (pubmed['http_status']!=200 or pm['identifiers']['doi']!=DOI
            or pm['title']!='A human factors perspective: auditory alarm signals.'
            or pm['authors']!=['Stephen B Wilcox'] or pm['publication_year']!='2011'
            or pm['volume']!='45' or pm['issue']!='4'):
        raise ValueError('PubMed bibliographic disagreement')
    records,ledger=E.build(root,at,**OPTIONS)
    source_path=AREA+'/records/'+WILCOX+'.json';body=records[source_path]['revisions'][0]['data']
    body.update(access_status='partial_text',access_at=at,
        access_reason=plan['reading_exposure']['wilcox']['extent']+' Publisher URL: '+plan['reading_exposure']['wilcox']['url'])
    body['metadata_evidence'] += ['Exact record-specific title presentation documented in '+PLAN+'; raw Crossref title retained unchanged in both original and fresh captures.',
        plan['pubmed']['path']+' DOI/title/author/year/volume/issue corroboration; publisher PDF bibliographic header also exposed through web search.']
    ledger['sources'][0]['revision_sha256']=E.digest(records[source_path]['revisions'][0])
    for occurrence in ledger['occurrences']:
        revision=records[occurrence['path']]['revisions'][1]
        revision['data']['resolution_reason']='R006: explicit DOI and full retained title agree after the record-specific Crossref presentation decision. Partial tool-mediated text exposure is logged separately; no eligibility, full reading, version alias or independent-study assertion. See '+LEDGER
        occurrence['output_revision_sha256']=E.digest(revision)

    path='research/searches/auditory/records/hits/'+VENUE+'.json';record=read_json(root/path);original=record['revisions'][0];before=original['data']
    if before['status']!='unresolved' or before['ordinal']!=1072:raise ValueError('Venue original state/ordinal disagreement')
    search=read_json(root/('research/searches/auditory/records/'+before['search_ref']['id']+'.json'))['revisions'][before['search_ref']['rev']-1]
    exp=search['data']['export']['value'];manifest=artifact(exp)
    rows=[r for y in manifest['years'] for r in y['results']]+manifest['unassigned_or_out_of_range'];row=rows[before['ordinal']-1]
    stored=(root/row['raw_path']).read_bytes()
    if hashlib.sha256(stored).hexdigest()!=row['storage_sha256']:raise ValueError('Venue storage hash disagreement')
    payload=gzip.decompress(stored)
    if hashlib.sha256(payload).hexdigest()!=row['raw_sha256']:raise ValueError('Venue payload hash disagreement')
    artifacts[row['raw_path']]={'path':row['raw_path'],'sha256':row['storage_sha256']}
    import json
    node=json.loads(payload)
    for token in row['raw_locator'].strip('/').split('/'):
        node=node[int(token)] if isinstance(node,list) else node[token]
    meta=node['metadata'];values=lambda obj,key:[v['value'] for v in obj.get(key,[])]
    if (row['repository_item_id']!=UUID or node['uuid']!=UUID or row['title']!=values(meta,'dc.title')
            or row['authors']!=values(meta,'dc.contributor.author') or row['doi']!=values(meta,'dc.identifier.doi')
            or row['issued_dates']!=values(meta,'dc.date.issued')):
        raise ValueError('Venue retained item disagreement')
    expected_text=row['title'][0]+' | '+'; '.join(row['authors'])+' | issued: '+', '.join(row['issued_dates'])+' | '+', '.join(row['resource_type'])+' | '+row['repository_url']
    if before['raw_metadata']!=expected_text:raise ValueError('Venue discovery text disagreement')
    fmeta=fresh['metadata'];doi=plan['venue']['doi']
    discovered_dois={d for i in before['returned_identifiers'] if i['scheme'] in {'doi','url'} and (d:=normalize_doi(i['value']))}
    if discovered_dois!={doi}:raise ValueError('Venue original DOI disagreement')
    if (fresh['http_status']!=200 or fresh['record']['uuid']!=UUID or fresh['record']['withdrawn']
            or values(fmeta,'dc.title')!=row['title'] or values(fmeta,'dc.identifier.doi')!=row['doi']
            or values(fmeta,'dc.contributor.author')!=row['authors'] or values(fmeta,'dc.date.issued')!=row['issued_dates']
            or {normalize_doi(v) for v in row['doi']}!={doi}):
        raise ValueError('Fresh venue identity disagreement')
    source_path=AREA+'/records/'+TISLAR+'.json';source=read_json(root/source_path);srev=source['revisions'][0];sb=srev['data']
    if (sb['metadata_status']!='verified' or E.text_key(sb['title'])!=E.text_key(row['title'][0])
            or doi not in {i['value'] for i in sb['identifiers'] if i['scheme']=='doi' and i['status']=='verified'}):
        raise ValueError('Accepted venue source disagreement')
    author_names=[' '.join(reversed(a.split(', ',1))) for a in row['authors']]
    if author_names!=[a['name'] for a in sb['authors']]:raise ValueError('Venue author disagreement')
    previous=read_json(root/(AREA+'/R006-DOI-C-20261106.json'))
    representative=next(o for o in previous['occurrences'] if o['status']=='resolved' and o['source_ref']==E.pin(TISLAR))
    rep=read_json(root/representative['path'])['revisions'][representative['output_ref']['rev']-1]
    if rep['data']['status']!='resolved' or rep['data']['source_ref']!=E.pin(TISLAR):raise ValueError('Venue representative disagreement')
    after=copy.deepcopy(before);after.update(status='duplicate',source_ref=E.pin(TISLAR),duplicate_of=representative['output_ref'],
      resolution_reason='R006: original venue ordinal, repository UUID, exact DOI/full title and author/date metadata agree across the retained ICAD manifest, original compressed API item and fresh Georgia Tech record. No eligibility or study/sample assertion. See '+LEDGER)
    rev={'rev':2,'at':at,'actor':ACTOR,'basis':[E.pin(VENUE),before['search_ref'],E.pin(TISLAR),representative['output_ref'],E.pin(AID)],'factual_status':'derived','data':after}
    records[path]={**record,'revisions':[copy.deepcopy(original),rev]}
    ledger['occurrences'].append({'hit_id':VENUE,'path':path,'input_ref':E.pin(VENUE),'output_ref':E.pin(VENUE,2),'input_revision_sha256':E.digest(original),'output_revision_sha256':E.digest(rev),'source_ref':E.pin(TISLAR),'status':'duplicate','duplicate_of':representative['output_ref'],'search_ref':before['search_ref'],'ordinal':before['ordinal'],'doi':doi,'export_locator':{'path':row['raw_path'],'json_pointer':row['raw_locator'],'repository_item_id':UUID,'manifest_path':exp['path'],'manifest_ordinal':1072}})
    observed=copy.deepcopy(sb);observed.update(access_status='abstract_only',access_at=at,access_reason=plan['reading_exposure']['tislar']['extent'])
    observed['metadata_evidence'].append(plan['gatech']['path']+' fresh DOI/title/author/date/UUID identity corroboration; original embedded abstract exposure logged in '+LEDGER)
    obs={'rev':2,'at':at,'actor':ACTOR,'basis':[E.pin(TISLAR),E.pin(VENUE),E.pin(AID)],'factual_status':'source_reported','data':observed}
    records[source_path]={**source,'revisions':[copy.deepcopy(srev),obs]}
    ledger['source_access_observations']=[{'source_ref':E.pin(TISLAR),'output_ref':E.pin(TISLAR,2),'input_revision_sha256':E.digest(srev),'output_revision_sha256':E.digest(obs),'extent':plan['reading_exposure']['tislar']['extent']}]
    ledger['counts'].update(occurrences=7,duplicate_occurrences=6,source_access_observations=1)
    ledger['boundary']='One new publication and seven occurrence identities; Wilcox partial tool-mediated text exposure and Tislar abstract exposure are not full readings, eligibility or independent studies. Issue #6/corpus gate remain open.'
    artifacts.update({x['path']:x for x in ledger['input_artifacts']});ledger['input_artifacts']=[artifacts[p] for p in sorted(artifacts)]
    aid=records[AREA+'/records/'+AID+'.json']['revisions'][0];extra=[E.pin(VENUE),E.pin(TISLAR)]
    aid['basis']=[*aid['basis'],*extra];aid['data']['input_refs']=[*aid['data']['input_refs'],*extra]
    aid['data']['output_refs']+=[E.pin(VENUE,2),E.pin(TISLAR,2)]
    aid['data']['limitations']='Wilcox publisher first-page search excerpts were exposed through web search: partial_text only, with no stable whole-article bytes or contiguous/full reading. Tislar embedded abstract was exposed but not appraised; access observation is abstract_only. No full-paper reading, eligibility, extraction, sample identity, independent human adjudication or corpus acceptance. Raw metadata response bytes and source texts not committed; selected derivatives and original-response hashes retained.'
    return records,ledger


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();target=ROOT/LEDGER
    if args.check and not target.exists():raise SystemExit('Frozen residue ledger missing')
    at=read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    records,ledger=build(ROOT,at)
    if target.exists() and read_json(target)!=ledger:raise SystemExit('Frozen residue ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual=read_json(ROOT/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:raise SystemExit('Residue prefix drift: '+path)
        print('Seven fixed residue resolutions and bounded source-access observations reproduce.')
    else:
        write_generated_records(ROOT,records);target.write_text(dumps(ledger));print('Recorded seven residue identities; no eligibility decisions.')


if __name__=='__main__':main()
