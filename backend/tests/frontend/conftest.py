"""Existing view tests use an explicit synthetic sign-in, not the real provider.

Security tests in test_authentication.py exercise the actual gate and identity
loading. This fixture supplies identity only to older non-auth view tests.
"""
import pytest


@pytest.fixture(autouse=True)
def synthetic_identity_for_existing_view_tests(request, monkeypatch):
    if request.path.name == 'test_authentication.py':
        return
    from frontend import authentication
    from backend.tests.auth_helpers import SYNTHETIC_ADMIN
    principal = SYNTHETIC_ADMIN
    identity = {'subject': principal.subject, 'roles': sorted(principal.roles),
                'permissions': sorted(principal.permissions)}
    monkeypatch.setattr(authentication, 'sign_in_gate', lambda: None)
    monkeypatch.setattr(authentication, 'auth_headers', lambda: {})
    monkeypatch.setattr(authentication, 'load_identity', lambda api: identity)
    monkeypatch.setattr(authentication, 'bind_identity', lambda identity: principal.permissions)
