import hashlib,json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from app.evaluation import upload_validation_final_scope as scope
from app.evaluation.simple_config import load_config,EvaluationError
from app.evaluation.suite_context import upload_validation_final_suite,execution_scope
from app.llm.client import ModelFailure


@pytest.fixture
def approved(tmp_path,monkeypatch):
    monkeypatch.setattr(scope,'ROOT',tmp_path);monkeypatch.setattr(scope,'implementation_hash',lambda:'synthetic-source')
    for name,suffix in [('SCOPE','.json'),('JOURNAL','.jsonl'),('STOP','.stopped'),('CLOSED','.closed')]:monkeypatch.setattr(scope,name,tmp_path/('scope'+suffix))
    plan={'documents':[{} for _ in range(10)],'cases':[{'case_id':f'case-{i}'} for i in range(23)]}
    path=tmp_path/'.private/all_uploads_validation_20261030_v1_inputs.json';path.parent.mkdir();path.write_text(json.dumps({'plan':plan}))
    approval=SimpleNamespace(allowance_id='synthetic',provider='azure_openai',confirmed_free_promotional=True,paid_azure_test_authorized=False)
    monkeypatch.setattr('app.llm.client.approval',lambda:approval)
    monkeypatch.setattr('app.llm.client.allowance_capacity',lambda a:dict(stopped=False,remaining_calls=36,remaining_reserved_tokens=1152000))
    prior=tmp_path/'results/upload_validation_20261030_v1';prior.mkdir(parents=True)
    for i in range(9,23):
        for mode in 'ABC':(prior/f'case-{i}--{mode}.json').write_text('{}')
    receipt=dict(authorization=scope.AUTHORIZATION,max_calls=36,max_reservation_units=1152000,expires_at=None,config=load_config(),prior_rows_sha256=scope.prior_hash(),
        manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),implementation_sha256='synthetic-source',parent_allowance_id='synthetic',
        user_confirmed_trial_credits_and_quota=True,cases=[c['case_id'] for c in plan['cases']],allowed_rows=scope.untouched_rows(plan),
        continue_content_filter_errors=True,sensitive_payload_explicitly_approved=True)
    scope.SCOPE.write_text(json.dumps(receipt))
    with upload_validation_final_suite():yield receipt


def test_new_scope_dispatch_and_sensitive_consent_required(approved):
    assert execution_scope() is scope
    scope.validate(load_config())
    approved['sensitive_payload_explicitly_approved']=False;scope.SCOPE.write_text(json.dumps(approved))
    with pytest.raises(EvaluationError):scope.validate(load_config())


def test_filter_is_recorded_without_replay_and_next_row_can_advance(approved):
    with patch('app.llm.client.reserve',return_value=['synthetic']),patch('app.llm.client.call',side_effect=ModelFailure('provider',{'provider_error_code':'content_filter'})) as call:
        with scope.row('case-0','A'):
            with pytest.raises(EvaluationError,match='provider_content_filter:') as error:scope.invoke([],{},'generation',load_config())
            assert scope.may_continue(str(error.value)) and not scope.STOP.exists()
            with pytest.raises(EvaluationError,match='already attempted'):scope.invoke([],{},'generation',load_config())
        assert call.call_count==1
    scope.check_row('case-1','C',load_config())


def test_nonfilter_failure_stops_and_unknown_row_is_never_funded(approved):
    with pytest.raises(EvaluationError):scope.check_row('not-approved','A',load_config())
    with patch('app.llm.client.reserve',return_value=['synthetic']),patch('app.llm.client.call',side_effect=RuntimeError('synthetic')):
        with scope.row('case-0','B'),pytest.raises(EvaluationError):scope.invoke([],{},'generation',load_config())
    assert scope.STOP.exists()


def test_prior_rows_cannot_be_rewritten_and_cap_cannot_drift(approved):
    config=load_config();config['max_tokens']=700
    with pytest.raises(EvaluationError):scope.validate(config)
    (scope.ROOT/'results/upload_validation_20261030_v1/case-9--A.json').write_text('{"modified":true}')
    with pytest.raises(EvaluationError):scope.validate(load_config())
