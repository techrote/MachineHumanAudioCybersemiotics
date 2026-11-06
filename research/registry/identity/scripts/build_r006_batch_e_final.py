"""Keep the fixed Jeon 2010 conference / 2012 journal identities separate."""
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
from research.registry.identity.scripts import build_r006_new_publications as E

AREA=E.AREA
PLAN=AREA+'/R006-E-FINAL-PLAN-20261106.json'
LEDGER=AREA+'/R006-E-FINAL-20261106.json'
AID='AID-R006-E-FINAL-20261106'
CONFERENCE='SRC-R006-E-JEON-UNAVAILABLE'
JOURNAL='SRC-R006-E-JEON-2012-AES'
DOI='10.1145/1753846.1753978'
TITLE='Auditory menus are not just spoken visual menus'
SUBTITLE='a case study of "unavailable" menu items'
INDEX_TITLE='Auditory Menus Are Not Just Spoken Visual Menus: A Case Study of “Unavailable” Menu Items'
AUTHORS=['Myounghoon Jeon','Siddharth Gupta','Benjamin K. Davison','Bruce N. Walker']
AES_URL='https://aes.org/publications/elibrary/elibrary-page/?id=16362'
LEGACY_URL='https://www.aes.org/e-lib/browse.cfm?elib=16362'
HITS={'HIT-R005R-C1LOAD-EQ1-03013','HIT-R005R-C1RECOVERY-EQ1-00478'}
ACTOR={'kind':'agent','id':'codex-r006-e-final-20261106','model':'GPT-6',
       'tool':'Codex; Crossref subtitle / AES publisher metadata and retained OpenAlex provenance adjudication'}


def build(root,at):
    artifacts={}
    def artifact(value):
        p=value['path'] if isinstance(value,dict) else value
        raw=(root/p).read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if isinstance(value,dict) and sha!=value['sha256']:raise ValueError('Artifact hash mismatch: '+p)
        artifacts[p]={'path':p,'sha256':sha};return json.loads(raw)
    plan=artifact(PLAN);parent=artifact(plan['parent_plan']);sub=artifact(plan['reference_subplan'])
    if (plan['selected']!=sub['remaining_deferred'] or {i['hit_ref']['id'] for i in plan['selected']}!=HITS
            or sorted(sub['deferred']+plan['selected'],key=lambda i:i['hit_ref']['id'])!=sorted(parent['deferred'],key=lambda i:i['hit_ref']['id'])):
        raise ValueError('Fixed residual scope disagreement')
    if (plan['source_ref']!=E.pin(CONFERENCE) or plan['new_source_id']!=JOURNAL
            or plan['full_title']!=TITLE+': '+SUBTITLE or plan['retained_index_title']!=INDEX_TITLE
            or plan['quote_mapping']!={'“':'"','”':'"'} or plan['conference_publication_date']!='2010-04-10'
            or plan['publisher_publication_date']!='2012-07-06' or plan['retained_publication_date']!='2012-08-27'
            or plan['retained_work_id']!='https://openalex.org/W1492156475' or plan['retained_venue_url']!=LEGACY_URL
            or plan['retained_biblio']!={'volume':'60','issue':None,'first_page':'505','last_page':'518'}):
        raise ValueError('Fixed title/publication separation disagreement')
    fresh=artifact(plan['fresh_crossref']);old=artifact(plan['previous_crossref']);pub=artifact(plan['publisher'])
    for cap in (fresh,old):
        m=cap['record']
        if (cap['http_status']!=200 or normalize_doi(m['DOI'])!=DOI or m['title']!=[TITLE]
                or m['type']!='proceedings-article' or m['page']!='3319-3324'
                or m['container-title']!=["CHI '10 Extended Abstracts on Human Factors in Computing Systems"]
                or m['published-print']['date-parts']!=[[2010,4,10]]
                or [' '.join(a.get(k,'') for k in ('given','family')).strip() for a in m['author']]!=AUTHORS):
            raise ValueError('Conference bibliographic disagreement')
    if (fresh['record'].get('subtitle')!=[SUBTITLE] or fresh['raw_response_sha256']!=old['raw_response_sha256']
            or fresh['requested_doi']!=DOI or fresh['url']!='https://api.crossref.org/works/10.1145%2F1753846.1753978'):
        raise ValueError('Subtitle capture provenance disagreement')
    full=TITLE+': '+fresh['record']['subtitle'][0]
    if E.text_key(INDEX_TITLE.translate(str.maketrans(plan['quote_mapping'])))!=E.text_key(full):
        raise ValueError('Fixed title representation disagreement')
    meta=pub['metadata']
    expected={'citation_title':[INDEX_TITLE],'citation_author':['Jeon, Myounghoon','Gupta, Siddharth','Davison, Benjamin K.','Walker, Bruce N.'],
              'citation_journal_title':['Journal of the Audio Engineering Society'],'citation_volume':['60'],
              'citation_issue':['7/8'],'citation_firstpage':['505'],'citation_lastpage':['518'],
              'citation_publication_date':['2012/07/06'],'citation_publisher':['Audio Engineering Society']}
    if (pub['http_status']!=200 or pub['url']!=AES_URL or pub['final_url']!=AES_URL
            or any(meta.get(k)!=v for k,v in expected.items()) or meta.get('citation_doi')):
        raise ValueError('Journal publisher bibliographic disagreement')
    source_path=AREA+'/records/'+CONFERENCE+'.json';source=read_json(root/source_path)['revisions'][0];sb=source['data']
    if (sb['metadata_status']!='verified' or sb['title']!=TITLE or sb['publication_date']!={'state':'known','value':'2010-04-10'}
            or [a['name'] for a in sb['authors']]!=AUTHORS or sb['access_status']!='metadata_only'
            or DOI not in {i['value'] for i in sb['identifiers'] if i['scheme']=='doi' and i['status']=='verified'}):
        raise ValueError('Accepted conference source disagreement')
    previous=artifact(plan['previous_ledger']);rep=next(o for o in previous['occurrences'] if o['status']=='resolved' and o['source_ref']==E.pin(CONFERENCE))
    if read_json(root/rep['path'])['revisions'][rep['output_ref']['rev']-1]['data']['source_ref']!=E.pin(CONFERENCE):
        raise ValueError('Conference representative disagreement')
    output={};occurrences=[];cache={};journal_rep=None
    for item in plan['selected']:
        hid=item['hit_ref']['id'];path='research/searches/auditory/records/hits/'+hid+'.json';record=read_json(root/path);original=record['revisions'][0];before=original['data']
        ds={d for i in before['returned_identifiers'] if i['scheme'] in {'doi','url'} and (d:=normalize_doi(i['value']))}
        if item['hit_ref']!=E.pin(hid) or item['source_id']!=CONFERENCE or item['doi']!=DOI or before['status']!='unresolved' or ds!={DOI}:
            raise ValueError('Original occurrence scope/DOI disagreement')
        search=read_json(root/('research/searches/auditory/records/'+before['search_ref']['id']+'.json'))['revisions'][before['search_ref']['rev']-1]['data']
        if 'OpenAlex' not in search['platform']:raise ValueError('Unreviewed original platform')
        exp=search['export']['value'];manifest=artifact(exp);label=before['search_ref']['id'].rsplit('-',1)[1];key=(exp['path'],label)
        if key not in cache:
            rows=[]
            for page in manifest['runs'][label]['pages']:
                if 'results' not in page:continue
                blob=(root/page['file']).read_bytes()
                if hashlib.sha256(blob).hexdigest()!=page['sha256']:raise ValueError('Stored page hash disagreement')
                artifacts[page['file']]={'path':page['file'],'sha256':page['sha256']};raw=gzip.decompress(blob)
                if hashlib.sha256(raw).hexdigest()!=page['payload_sha256']:raise ValueError('Payload hash disagreement')
                works=json.loads(raw)['results']
                if len(works)!=page['results']:raise ValueError('Page count disagreement')
                rows.extend((row,page['file'],i+1) for i,row in enumerate(works))
            cache[key]=rows
        row,page_path,index=cache[key][before['ordinal']-1]
        authors=[a['author']['display_name'] for a in row['authorships']]
        aes_locations=[l for l in row['locations'] if l.get('landing_page_url')==LEGACY_URL]
        expected_raw=INDEX_TITLE+' | first author: Myounghoon Jeon | 2012-08-27 | conference-paper | '+plan['retained_work_id']
        if (row['id']!=plan['retained_work_id'] or row['display_name']!=INDEX_TITLE or normalize_doi(row['doi'])!=DOI
                or row['publication_date']!='2012-08-27' or row['biblio']!=plan['retained_biblio'] or authors!=AUTHORS
                or row['type']!='conference-paper' or before['raw_metadata']!=expected_raw
                or not any(i['value']==row['id'] for i in before['returned_identifiers'])
                or len(aes_locations)!=1 or aes_locations[0].get('source',{}).get('display_name')!='Journal of the Audio Engineering Society'):
            raise ValueError('Retained mixed-identity provenance disagreement')
        after=copy.deepcopy(before);duplicate=journal_rep is not None
        after.update(status='duplicate' if duplicate else 'resolved',source_ref=E.pin(JOURNAL),
            resolution_reason='R006: title, all four authors, AES item 16362, journal volume 60 and pages 505-518 identify the 2012 journal report. Original ACM DOI identifies the separate CHI EA 2010 conference paper, not this journal report; the erroneous/mixed index DOI assertion, 2012-08-27 date and conference-paper type remain literal discovery provenance. No alias, shared/independent-sample or eligibility assertion. See '+LEDGER)
        basis=[item['hit_ref'],before['search_ref'],E.pin(JOURNAL),E.pin(CONFERENCE),E.pin(AID)]
        if duplicate:after['duplicate_of']=journal_rep;basis.append(journal_rep)
        else:journal_rep=E.pin(hid,2)
        revision={'rev':2,'at':at,'actor':ACTOR,'basis':basis,'factual_status':'derived','data':after}
        output[path]={**record,'revisions':[copy.deepcopy(original),revision]}
        occurrences.append({'hit_id':hid,'path':path,'input_ref':item['hit_ref'],'output_ref':E.pin(hid,2),
            'input_revision_sha256':E.digest(original),'output_revision_sha256':E.digest(revision),
            'source_ref':E.pin(JOURNAL),'status':after['status'],'duplicate_of':after.get('duplicate_of'),
            'rejected_discovery_doi':DOI,'conference_source_ref':E.pin(CONFERENCE),
            'export_locator':{'path':page_path,'item':index,'work_id':row['id'],'original_ordinal':before['ordinal'],'reported_date':row['publication_date'],'reported_biblio':row['biblio'],'journal_location_url':LEGACY_URL}})
    body={'title':INDEX_TITLE,'authors':[{'name':n,'role':'author'} for n in AUTHORS],
        'publication_date':{'state':'known','value':'2012-07-06'},
        'identifiers':[{'scheme':'url','value':AES_URL,'status':'verified','provenance':plan['publisher']['path']+' HTTP 200, publisher citation metadata; AES item 16362'}],
        'source_type':'article','language':{'state':'not_reported','reason':'Language not inferred from English metadata/abstract.'},
        'edition':{'state':'known','value':'Journal of the Audio Engineering Society; 60(7/8); 505-518'},
        'metadata_status':'verified','metadata_evidence':[plan['publisher']['path']+' citation_title/author/journal_title/volume/issue/firstpage/lastpage/publication_date; actual response hash retained.',
            'Retained OpenAlex AES item URL, title, authors, volume and pages checked in '+LEDGER,
            'DOI 10.1145/1753846.1753978 belongs to a distinct 2010 conference report; it is not assigned to this journal source. No journal DOI was verified; this is not a claim that none exists.',
            'Publisher 2012-07-06 and discovery 2012-08-27 dates remain distinct.'],
        'access_status':'abstract_only','access_at':pub['retrieved_at'],'access_reason':plan['publisher_reading_extent'],
        'rights':{'status':'unknown','reason':'No article redistribution or reuse permission verified; only bibliographic derivative retained.','evidence':{'state':'unknown','reason':'Publisher metadata availability is not an article licence.'}},
        'validity':'active','family_links':[],'manifestations':[]}
    srev={'rev':1,'at':at,'actor':ACTOR,'basis':[i['hit_ref'] for i in plan['selected']]+[E.pin(AID)],'factual_status':'source_reported','data':body}
    journal_path=AREA+'/records/'+JOURNAL+'.json';output[journal_path]={'id':JOURNAL,'kind':'source','issue':6,'schema_version':1,'synthetic':False,'revisions':[srev]}
    inputs=[i['hit_ref'] for i in plan['selected']]+[E.pin(CONFERENCE)];outputs=[E.pin(JOURNAL)]+[o['output_ref'] for o in occurrences]
    output[AREA+'/records/'+AID+'.json']={'id':AID,'kind':'assistance','issue':6,'schema_version':1,'synthetic':False,'revisions':[{
        'rev':1,'at':at,'actor':ACTOR,'basis':inputs,'factual_status':'derived','data':{'subtype':'assistance','status':'performed','performed_at':{'state':'known','value':at},
        'task':'Adjudicate two mixed OpenAlex records against distinct 2010 conference and 2012 publisher journal identities without transferring the conference DOI or counting independent samples.',
        'input_refs':inputs,'output_refs':outputs,'artifacts':[PLAN,LEDGER,AREA+'/README.md'],
        'verification_steps':['Fresh Crossref subtitle captured; old/fresh raw response hashes agree, exposing an omitted field rather than evidence of a changed title.',
            'AES HTTP 200 citation metadata verifies a distinct 2012 journal report: full title, four authors, volume/issue/pages and publisher date.',
            'Checked original compressed page and payload hashes, ordinals, work ID, literal title/authors, mixed DOI/date/type, journal biblio and AES location. Assigned journal URL only; original wrong DOI retained on discovery records.',
            'Eight bibliography cases and these two occurrences partition the parent deferred plan. Old conference source remains unchanged.'],
        'limitations':plan['publisher_reading_extent']+' '+plan['incidental_exposure']['extent']+' No full-text reading, eligibility, study/sample or alias/family decision; potential conference/journal overlap remains unresolved. Raw HTML/abstract/source PDF not committed.',
        'independence':'One Codex/GPT-6 agent and software self-review; no independent human adjudication.'}}]}
    ledger={'artifact_kind':'bounded_mixed_publication_identity_adjudication','issue':6,'resolved_at':at,'actor':ACTOR,'implementation_base':plan['accepted_base'],
        'source':{'source_ref':E.pin(JOURNAL),'path':journal_path,'revision_sha256':E.digest(srev)},'occurrences':occurrences,
        'conference_source_unchanged':{'source_ref':E.pin(CONFERENCE),'revision_sha256':E.digest(source)},
        'publication_separation':{'conference':E.pin(CONFERENCE),'journal':E.pin(JOURNAL),'study_sample_overlap':'not_adjudicated; no independent-study increment'},
        'input_artifacts':[artifacts[p] for p in sorted(artifacts)],
        'counts':{'occurrences':2,'new_source_records':1,'resolved_representatives':1,'duplicate_occurrences':1,'rejected_discovery_doi_assertions':2,'screening_decisions_created':0,'study_records_created':0,'sample_records_created':0},
        'boundary':'Separate conference and journal publications, not independent samples. Journal abstract_only; no whole paper read or corpus acceptance.'}
    return output,ledger


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();target=ROOT/LEDGER
    if args.check and not target.exists():raise SystemExit('Frozen mixed-identity ledger missing')
    at=read_json(target)['resolved_at'] if target.exists() else datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    records,ledger=build(ROOT,at)
    if target.exists() and read_json(target)!=ledger:raise SystemExit('Frozen mixed-identity ledger drift; no records written')
    if args.check:
        for path,expected in records.items():
            actual=read_json(ROOT/path)
            if {**actual,'revisions':actual['revisions'][:len(expected['revisions'])]}!=expected:raise SystemExit('Mixed-identity record prefix drift: '+path)
        print('Two journal occurrences and separate conference identity reproduce; no study/sample inference.')
    else:
        write_generated_records(ROOT,records);target.write_text(dumps(ledger));print('Recorded distinct journal source and two occurrences; no conference DOI transfer.')


if __name__=='__main__':main()
