"""Offline checks for live source constraints and safe failure diagnostics."""
import json
from app.defenses import screening


def test_live_schema_limits_sources_without_changing_evaluation_contract():
    schema = screening.request_schema([{'id': 'first'}, {'id': 'second'}, {'id': 'first'}])
    assert schema['properties']['flagged_source_ids']['items']['enum'] == ['first', 'second']
    assert 'enum' not in screening.Screening.model_json_schema()['properties']['flagged_source_ids']['items']
    assert screening.request_schema([])['properties']['flagged_source_ids']['maxItems'] == 0


def test_malformed_decision_has_safe_diagnostic_and_no_retry(monkeypatch):
    attempts = []
    def call(*args):
        attempts.append(args)
        return json.dumps({'question_flagged': False, 'flagged_source_ids': [],
                           'reason_codes': ['none', 'secret_request']}), {}
    monkeypatch.setattr(screening.live, 'call', call)
    result = {'calls': []}
    assert screening.apply('Private question', [{'id': 'one', 'text': 'Private source'}],
                           ['reserved'], result) is None
    assert result['status'] == 'screening_error'
    assert result['screening_validation'][0]['reason'] == 'contradictory_screening_reasons'
    assert len(attempts) == 1
    assert 'Private' not in json.dumps(result)


def test_valid_live_decision_retains_clean_source(monkeypatch):
    evidence = [{'id': 'clean', 'text': 'Business fact'}, {'id': 'bad', 'text': 'Attack'}]
    def call(messages, schema, *args):
        assert schema['properties']['flagged_source_ids']['items']['enum'] == ['clean', 'bad']
        return json.dumps({'question_flagged': False, 'flagged_source_ids': ['bad'],
                           'reason_codes': ['instruction_redirection']}), {}
    monkeypatch.setattr(screening.live, 'call', call)
    assert screening.apply('Question', evidence, ['reserved'], {'calls': []}) == evidence[:1]
