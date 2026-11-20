"""Offline security boundary checks with locally signed synthetic tokens only."""
from types import SimpleNamespace
from unittest.mock import Mock
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.api import runtime
from app.core import auth
from app.storage import registry as reg

TENANT = '11111111-1111-4111-8111-111111111111'
API = '22222222-2222-4222-8222-222222222222'
WEB = '33333333-3333-4333-8333-333333333333'
ALICE = '44444444-4444-4444-8444-444444444444'
BOB = '55555555-5555-4555-8555-555555555555'


@pytest.fixture
def secured(tmp_path, monkeypatch):
    monkeypatch.setenv('ENTRA_TENANT_ID', TENANT)
    monkeypatch.setenv('ENTRA_API_CLIENT_ID', API)
    monkeypatch.setenv('ENTRA_WEB_CLIENT_ID', WEB)
    monkeypatch.setenv('LIVE_LLM_ENABLED', 'false')
    monkeypatch.setattr(reg, 'ROOT', tmp_path / 'runtime')
    reg.initialize()
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    keys = Mock()
    keys.get_signing_key_from_jwt.return_value = SimpleNamespace(key=private.public_key())
    monkeypatch.setattr(auth, 'signing_keys', lambda tenant: keys)
    monkeypatch.setattr('app.llm.client.call', Mock(side_effect=AssertionError('No live provider calls')))
    app = FastAPI()
    app.include_router(runtime.router)
    # Deliberately unclassified endpoint verifies deny-by-default behavior.
    @app.get('/new-unclassified', dependencies=[Depends(auth.require_access)])
    def unclassified():
        return {'unexpected': True}
    def token(assigned_roles=('Lab.User',), **overrides):
        now = int(time.time())
        claims = {'iss': f'https://login.microsoftonline.com/{TENANT}/v2.0', 'aud': API,
                  'tid': TENANT, 'oid': ALICE, 'sub': 'synthetic-user', 'azp': WEB,
                  'ver': '2.0', 'scp': 'access_as_user', 'roles': list(assigned_roles),
                  'iat': now - 10, 'nbf': now - 10, 'exp': now + 300}
        claims.update(overrides)
        return {'Authorization': 'Bearer ' + jwt.encode(claims, private, algorithm='RS256', headers={'kid': 'synthetic-key'})}
    with TestClient(app) as client:
        yield client, token, keys


def test_anonymous_has_health_only_and_no_provider_calls(secured):
    client, _, keys = secured
    assert client.get('/health').status_code == 200
    for path in ('/documents', '/ready', '/auth/me', '/results', '/diagnostics', '/evaluation-current25'):
        assert client.get(path).status_code == 401
    assert client.post('/chat', json={}).status_code == 401
    keys.get_signing_key_from_jwt.assert_not_called()


@pytest.mark.parametrize('changes', [
    {'aud': WEB}, {'iss': 'https://untrusted.example/v2.0'}, {'tid': BOB},
    {'azp': BOB}, {'exp': 1}, {'nbf': 9999999999}, {'ver': '1.0'},
    {'scp': ''}, {'scp': None}, {'idtyp': 'app'}, {'oid': 'invalid'}, {'roles': 'Lab.Admin'},
])
def test_invalid_claims_rejected(secured, changes):
    client, token, _ = secured
    assert client.get('/auth/me', headers=token(**changes)).status_code == 401


def test_signature_and_algorithm_are_verified(secured):
    client, _, _ = secured
    forged = jwt.encode({'roles': ['Lab.Admin']}, 'synthetic-test-key-at-least-32-bytes', algorithm='HS256', headers={'kid': 'synthetic'})
    assert client.get('/auth/me', headers={'Authorization': 'Bearer ' + forged}).status_code == 401
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    forged = jwt.encode({'exp': int(time.time()) + 60}, private, algorithm='RS256', headers={'kid': 'synthetic'})
    assert client.get('/auth/me', headers={'Authorization': 'Bearer ' + forged}).status_code == 401


def test_role_required_and_live_role_is_additive(secured):
    client, token, _ = secured
    for roles in ([], ['Lab.LiveCaller'], ['Owner'], ['lab.admin']):
        assert client.get('/auth/me', headers=token(roles)).status_code == 403
    assert client.get('/documents', headers=token()).status_code == 200
    for role in ('Lab.User', 'Lab.Reviewer', 'Lab.Admin'):
        headers = token([role])
        assert 'live.call' not in client.get('/auth/me', headers=headers).json()['permissions']
        assert client.post('/chat', headers=headers, json={}).status_code == 403
    headers = token(['Lab.User', 'Lab.LiveCaller'])
    assert 'live.call' in client.get('/auth/me', headers=headers).json()['permissions']
    assert client.post('/chat', headers=headers, json={}).status_code == 422


def test_user_cannot_manage_documents_or_access_evaluation(secured, monkeypatch):
    client, token, _ = secured
    manage = Mock(side_effect=AssertionError('Must not execute'))
    monkeypatch.setattr(runtime.life, 'delete', manage)
    for role in ('Lab.User', 'Lab.Reviewer'):
        assert client.delete('/documents/anything', headers=token([role])).status_code == 403
    assert client.get('/evaluation-current25', headers=token()).status_code == 403
    assert client.get('/results/run/artifacts/records.json', headers=token()).status_code == 403
    assert client.get('/diagnostics', headers=token(['Lab.Reviewer'])).status_code == 403
    assert client.post('/documents', headers=token(), files={'file': ('bad.exe', b'bad')}).status_code == 201
    manage.assert_not_called()


def test_new_routes_fail_closed_and_role_headers_are_ignored(secured):
    client, token, _ = secured
    assert client.get('/new-unclassified', headers=token(['Lab.Admin'])).status_code == 403
    assert client.get('/documents', headers={'X-Role': 'Lab.Admin', 'X-User': ALICE}).status_code == 401


def test_missing_identity_config_fails_closed(secured, monkeypatch):
    client, token, _ = secured
    monkeypatch.delenv('ENTRA_TENANT_ID')
    assert client.get('/documents', headers=token()).status_code == 503
    assert client.get('/health').status_code == 200


def test_identity_bound_idempotency_does_not_reveal_other_users_answers(secured, monkeypatch):
    client, token, _ = secured
    monkeypatch.setattr(runtime.life, 'snapshot', lambda: [])
    response = Mock(side_effect=[{'status': 'answered', 'answer': 'Alice private question'},
                                 {'status': 'answered', 'answer': 'Bob private question'}])
    monkeypatch.setattr(runtime, 'respond', response)
    query = {'question': 'Synthetic question', 'request_id': 'same-request-123', 'mode': 'A'}
    alice = token(['Lab.User', 'Lab.LiveCaller'])
    bob = token(['Lab.User', 'Lab.LiveCaller'], oid=BOB)
    first = client.post('/chat', headers=alice, json=query)
    second = client.post('/chat', headers=bob, json=query)
    assert first.json()['answer'] == 'Alice private question'
    assert second.json()['answer'] == 'Bob private question'
    assert client.post('/chat', headers=alice, json=query).json() == first.json()
    assert response.call_count == 2
    assert response.call_args.kwargs['run_context']['authenticated_subject'] == TENANT + ':' + BOB
    with reg.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM requests').fetchone()[0] == 2


def test_review_attribution_uses_verified_identity(secured, monkeypatch):
    client, token, _ = secured
    submit = Mock(return_value={'provider_requests_made': 0})
    monkeypatch.setattr('app.evaluation.simple_review.submit_quality', submit)
    monkeypatch.setattr(runtime, 'refresh_evaluation_reports', lambda: None)
    payload = {'case_id': 'synthetic', 'mode': 'A', 'record_sha256': 'a' * 64,
               'reviewer': 'Pretending to be someone else', 'quality_0_4': 3, 'task_correct': True}
    assert client.post('/evaluation-v3/quality-review', headers=token(), json=payload).status_code == 403
    assert client.post('/evaluation-v3/quality-review', headers=token(['Lab.Reviewer']), json=payload).status_code == 200
    assert submit.call_args.kwargs['reviewer'] == TENANT + ':' + ALICE


def test_every_existing_route_has_an_explicit_policy():
    assert {(method, route.path) for route in runtime.router.routes for method in route.methods
            if route.path != '/health'} <= auth.ROUTE_PERMISSIONS.keys()
