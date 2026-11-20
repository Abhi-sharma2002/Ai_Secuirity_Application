import json
from unittest.mock import patch
import pytest
from app.rag.assistant import respond


@pytest.mark.parametrize('mode',['A','B','C'])
def test_answer_schema_only_allows_current_source_chunk_ids(mode,monkeypatch):
    monkeypatch.setenv('EVAL_MODE','1')
    hits=[{'id':'first-chunk','document_id':'document-1','text':'Fact one.'},{'id':'second-chunk','document_id':'document-2','text':'Fact two.'}]
    def call(messages,schema,stage,reservation):
        if stage=='screening':
            return json.dumps({'question_flagged':False,'flagged_source_ids':['second-chunk'],'reason_codes':['instruction_redirection']}),{}
        expected=['first-chunk'] if mode=='C' else ['first-chunk','second-chunk']
        assert schema['properties']['source_ids']['items']['enum']==expected
        assert schema['properties']['source_ids']['minItems']==1
        return json.dumps({'status':'answered','answer':'Fact one.','source_ids':['first-chunk']}),{}
    with patch('app.llm.client.reserve',side_effect=AssertionError('No live reservations')):
        result=respond('What is the fact?',mode,initial={'hits':hits,'snapshot':[],'omitted_ids':[]},_evaluation_call=call)
    assert result['status']=='answered'
    assert result['defense_versions']['answer_contract']=='answer-source-id-enum-required-v2'


def test_application_still_rejects_invalid_citations_from_nonconforming_response(monkeypatch):
    monkeypatch.setenv('EVAL_MODE','1')
    def call(*args):return json.dumps({'status':'answered','answer':'Fact','source_ids':['document-id']}),{}
    r=respond('Question','B',initial={'hits':[{'id':'chunk-id','document_id':'document-id','text':'Fact'}],'snapshot':[],'omitted_ids':[]},_evaluation_call=call)
    assert r['status']=='invalid_citations' and r['references']==[]
