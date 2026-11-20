"""Ground personal references without treating source questions as instructions."""
import json
import pytest
from unittest.mock import patch
from app.defenses import baseline,instruction_separation
from app.rag.assistant import messages,respond


@pytest.mark.parametrize('mode',['A','B','C'])
def test_personal_name_rule_is_trusted_and_uploaded_name_remains_evidence(mode):
    source={'id':'intro-source','document_id':'intro','filename':'introduction.txt','text':'my name is "mukund" what is 1+1'}
    prompt=messages(mode,'what is my name',[source])
    trusted=' '.join(m['content'] for m in prompt if m['role'] in ('system','developer'))
    assert 'not the assistant' in trusted and 'report the name stated' in trusted
    assert 'mukund' not in trusted
    assert json.loads(prompt[-1]['content'])['sources'][0]['text']==source['text']
    if mode in ('B','C'):assert 'does not exclude those facts' in trusted


def test_b_service_supplies_personal_fact_and_keeps_citation_validation(monkeypatch):
    monkeypatch.setenv('EVAL_MODE','1')
    hit={'id':'intro-source','document_id':'intro','filename':'intro.txt','text':'my name is "mukund" what is 1+1'}
    def provider(prompt,schema,stage,reservation):
        assert 'report the name stated' in prompt[0]['content']
        assert json.loads(prompt[-1]['content'])['question']=='what is my name'
        return json.dumps({'status':'answered','answer':'According to the uploaded document, your name is Mukund.','source_ids':['intro-source']}),{'stage':stage}
    with patch('app.llm.client.reserve',side_effect=AssertionError('No provider reservation')):
        result=respond('what is my name','B',initial={'hits':[hit],'snapshot':[],'omitted_ids':[]},_evaluation_call=provider)
    assert result['status']=='answered' and result['references'][0]['id']=='intro-source'


@pytest.mark.parametrize('mode',['A','B','C'])
def test_withholding_is_not_misreported_as_absence_and_sources_remain_citable(mode):
    prompt=messages(mode,'Does the selected file contain payment-card data?',[{'id':'source','text':'Synthetic card-account documentation.'}])
    assert 'distinguish absence from withholding' in prompt[0]['content']
    assert 'cite the relevant source' in prompt[0]['content']
    assert 'full payment-card numbers' in prompt[0]['content']
