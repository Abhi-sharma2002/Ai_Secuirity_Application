"""Disposable scope/ledger doubles; never send provider traffic."""
import json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from app.evaluation import challenge_scope as scope, simple_runner
from app.evaluation.simple_config import load_config, EvaluationError
from app.evaluation.suite_context import challenge_suite


@pytest.fixture
def authorized(tmp_path, monkeypatch):
    for name, suffix in [('SCOPE','.json'),('JOURNAL','.jsonl'),('STOP','.stopped'),('CLOSED','.closed')]:
        monkeypatch.setattr(scope,name,tmp_path/('scope'+suffix))
    approval=SimpleNamespace(allowance_id='synthetic-parent',provider='azure_openai',confirmed_free_promotional=True,paid_azure_test_authorized=False)
    capacity=dict(stopped=False,remaining_calls=32,remaining_reserved_tokens=1024000)
    monkeypatch.setattr('app.llm.client.approval',lambda:approval)
    monkeypatch.setattr('app.llm.client.allowance_capacity',lambda a:capacity)
    with challenge_suite():
        from app.evaluation.challenges import definitions
        from app.evaluation.simple_config import ROOT
        import hashlib
        data=definitions();sha=hashlib.sha256((ROOT/'backend/benchmark_challenges/manifest.json').read_bytes()).hexdigest()
        receipt=dict(authorization=scope.AUTHORIZATION,max_calls=32,max_reservation_units=1024000,expires_at=None,
                     config=load_config(),manifest_sha256=sha,implementation_sha256=scope.implementation_hash(),
                     parent_allowance_id=approval.allowance_id,user_confirmed_trial_credits_and_quota=True,
                     cases=[c['case_id'] for c in data['cases']],allowed_rows=[[c['case_id'],m] for c in data['cases'] for m in 'ABC'])
        scope.SCOPE.write_text(json.dumps(receipt))
        yield receipt,capacity


def test_scope_binds_current_inputs_and_preserves_stop(authorized):
    scope.validate(load_config())
    scope.stop()
    with pytest.raises(EvaluationError,match='stopped or closed'):
        scope.validate(load_config())
    assert scope.STOP.exists()


def test_changed_settings_rejected_without_provider(authorized):
    with pytest.raises(EvaluationError,match='matching these inputs'):
        scope.validate({**load_config(),'max_tokens':701})


def test_current_row_maximum_is_funded_before_execution(authorized):
    receipt,capacity=authorized
    capacity.update(remaining_calls=1,remaining_reserved_tokens=32000)
    with pytest.raises(EvaluationError,match='row maximum'):
        scope.check_row(receipt['cases'][0],'C',load_config())
    assert scope.STOP.exists() and not scope.JOURNAL.exists()


def test_stage_is_journaled_before_call_and_cannot_repeat(authorized):
    receipt,_=authorized
    def call(*args):
        assert len(scope.JOURNAL.read_text().splitlines())==1
        return '{}', {'synthetic':True}
    with patch('app.llm.client.reserve',return_value=['synthetic-call']),patch('app.llm.client.call',side_effect=call) as provider:
        with scope.row(receipt['cases'][0],'A'):
            scope.invoke([],{},'generation',load_config())
            with pytest.raises(EvaluationError,match='already attempted'):
                scope.invoke([],{},'generation',load_config())
        assert provider.call_count==1


def test_failure_stops_and_never_retries(authorized):
    receipt,_=authorized
    with patch('app.llm.client.reserve',return_value=['synthetic-call']),patch('app.llm.client.call',side_effect=RuntimeError('synthetic')) as provider:
        with scope.row(receipt['cases'][0],'A'):
            with pytest.raises(EvaluationError,match='scope stopped'):
                scope.invoke([],{},'generation',load_config())
        assert scope.STOP.exists() and provider.call_count==1
