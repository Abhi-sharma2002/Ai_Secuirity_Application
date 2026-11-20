"""No network: authorize only untouched rows and the exact refusal exception."""
import csv
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from app.evaluation import current25_continuation_scope as scope, simple_runner
from app.evaluation.simple_config import load_config, EvaluationError
from app.evaluation.suite_context import continuation_suite, execution_scope
from app.llm.client import ModelFailure

@pytest.fixture
def authorized(tmp_path,monkeypatch):
    for name,suffix in [('SCOPE','.json'),('JOURNAL','.jsonl'),('STOP','.stopped'),('CLOSED','.closed')]:
        monkeypatch.setattr(scope,name,tmp_path/('scope'+suffix))
    approval=SimpleNamespace(allowance_id='test',provider='azure_openai',confirmed_free_promotional=True,paid_azure_test_authorized=False)
    monkeypatch.setattr('app.llm.client.approval',lambda:approval)
    monkeypatch.setattr('app.llm.client.allowance_capacity',lambda a:dict(stopped=False,remaining_calls=163,remaining_reserved_tokens=5216000))
    with continuation_suite():
        data,sha=simple_runner._manifest()
        keys=[(c['case_id'],m) for c in data['cases'] for m in 'ABC']
        prior=tmp_path/'prior.csv'
        with prior.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['case_id','mode']);w.writerows(keys[:19])
        receipt=dict(authorization=scope.AUTHORIZATION,max_calls=163,max_reservation_units=5216000,expires_at=None,
            config=load_config(),manifest_sha256=sha,implementation_sha256=scope.implementation_hash(),parent_allowance_id='test',
            user_confirmed_trial_credits_and_quota=True,cases=[c['case_id'] for c in data['cases']],
            allowed_rows=keys[19:],continue_content_filter_errors=True,prior_records=str(prior),prior_records_sha256=hashlib.sha256(prior.read_bytes()).hexdigest())
        scope.SCOPE.write_text(json.dumps(receipt));yield receipt,keys


def test_prior_rows_excluded_and_dispatch_selects_new_scope(authorized):
    receipt,keys=authorized
    assert execution_scope() is scope
    with pytest.raises(EvaluationError,match='outside'):
        scope.check_row(*keys[18],load_config())
    scope.check_row(*keys[19],load_config())
    assert not scope.JOURNAL.exists()


def test_filter_is_recorded_and_next_distinct_row_allowed_without_retry(authorized):
    receipt,keys=authorized
    failure=ModelFailure('provider',{'provider_error_code':'content_filter'})
    with patch('app.llm.client.reserve',return_value=['fake']),patch('app.llm.client.call',side_effect=failure) as call:
        with scope.row(*keys[19]):
            with pytest.raises(EvaluationError,match='provider_content_filter:') as error:
                scope.invoke([],{},'generation',load_config())
            assert scope.may_continue(str(error.value)) and not scope.STOP.exists()
            with pytest.raises(EvaluationError,match='already attempted'):
                scope.invoke([],{},'generation',load_config())
        assert call.call_count==1
    scope.check_row(*keys[20],load_config())


def test_other_failures_stop_and_cannot_advance(authorized):
    receipt,keys=authorized
    with patch('app.llm.client.reserve',return_value=['fake']),patch('app.llm.client.call',side_effect=ModelFailure('provider',{'provider_error_code':'quota'})):
        with scope.row(*keys[19]),pytest.raises(EvaluationError,match='scope stopped'):
            scope.invoke([],{},'generation',load_config())
    assert scope.STOP.exists() and not scope.may_continue('provider_content_filter: fake')


def test_changed_prior_records_rejected(authorized):
    receipt,keys=authorized
    from pathlib import Path
    Path(receipt['prior_records']).write_text('changed')
    with pytest.raises(EvaluationError,match='matching these inputs'):scope.validate(load_config())
