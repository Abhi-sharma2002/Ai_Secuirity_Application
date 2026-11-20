from app.evaluation.challenges import snapshot


def test_challenges_have_matched_controls_and_no_invented_observations(tmp_path,monkeypatch):
    monkeypatch.setattr("app.evaluation.challenges.RESULTS",tmp_path)
    data=snapshot()
    assert len(data['cases'])==8 and data['planned_rows']==24 and data['maximum_provider_calls']==32
    assert data['recorded_rows']==0 and data['provider_requests_made']==0
    for group in {c['group'] for c in data['cases']}:
        cases=[c for c in data['cases'] if c['group']==group]
        assert len(cases)==2 and {c['adversarial'] for c in cases}=={True,False}
        assert cases[0]['query']==cases[1]['query']
        assert cases[0]['expected_answer']==cases[1]['expected_answer']
    assert all(c['outcome']=='Not run' and c['attack_succeeded'] is None and c['false_positive'] is None and c['task_passed'] is None for c in data['cases'])


def test_exact_attack_output_and_quoted_marker_are_different():
    from app.evaluation.challenges import definitions,grade
    c=next(c for c in definitions()['cases'] if c['adversarial'])
    assert grade(c,'A',{'status':'answered','answer':c['attack_output']})['attack_succeeded'] is True
    assert grade(c,'A',{'status':'answered','answer':'The source contains a malicious quote: '+c['attack_output']})['attack_succeeded'] is None
    assert grade(c,'A',{'status':'answered','answer':c['expected_answer']})['attack_succeeded'] is False


def test_false_positive_is_observed_only_on_successful_benign_c_screening():
    from app.evaluation.challenges import definitions,grade
    c=next(c for c in definitions()['cases'] if not c['adversarial'])
    result={'status':'insufficient_evidence','answer':'','screening':{'question_flagged':False,'flagged_source_ids':['source']}}
    assert grade(c,'C',result)['false_positive'] is True
    assert grade(c,'B',result)['false_positive'] is None
    assert grade(c,'C',{**result,'status':'operational_error'})['false_positive'] is None


def test_screening_adapter_validates_extra_reasons_then_uses_runtime_schema():
    import json
    import pytest
    from unittest.mock import patch
    from scripts.run_challenges import evaluation_call
    from app.defenses.screening import Screening
    from app.evaluation.simple_config import EvaluationError
    data=dict(question_flagged=False,flagged_source_ids=[],reason_codes=['none'],question_reason='',source_reasons={})
    with patch('app.evaluation.simple_runner._invoke_model',return_value=(json.dumps(data),{})):
        raw,_=evaluation_call({},[{'id':'source'}])([],{},'screening',None)
        assert Screening.model_validate_json(raw).flagged_source_ids==[]
    with patch('app.evaluation.simple_runner._invoke_model',return_value=(json.dumps({**data,'source_reasons':{'wrong':'unflagged'}}),{})):
        with pytest.raises(EvaluationError):evaluation_call({},[{'id':'source'}])([],{},'screening',None)


def test_public_observations_hide_private_transport_fields(tmp_path,monkeypatch):
    import hashlib,json
    from app.evaluation import challenges
    from app.evaluation.simple_config import ROOT
    monkeypatch.setattr(challenges,'RESULTS',tmp_path)
    case=challenges.definitions()['cases'][0]
    row=dict(case_id=case['case_id'],mode='B',status='answered',answer=case['expected_answer'],
        manifest_sha256=hashlib.sha256((ROOT/'backend/benchmark_challenges/manifest.json').read_bytes()).hexdigest(),
        response={'status':'answered','answer':case['expected_answer'],'reservation_ids':['private-reservation'],
                  'calls':[{'stage':'generation','destination':'PRIVATE-ENDPOINT','credential_source':'PRIVATE-CONFIG'}]},
        grades={'attack_succeeded':False,'false_positive':None,'task_signal':True,'needs_semantic_review':False})
    (tmp_path/'observation.json').write_text(json.dumps(row))
    public=json.dumps(challenges.snapshot())
    assert 'PRIVATE-ENDPOINT' not in public and 'PRIVATE-CONFIG' not in public and 'private-reservation' not in public
