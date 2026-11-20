"""Explicit synthetic administrator for legacy non-auth HTTP boundary tests.

Production contains no equivalent override. Authentication security tests use
real signed synthetic JWTs and do not use this helper.
"""
from contextlib import contextmanager
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.auth import Principal

SYNTHETIC_ADMIN = Principal('11111111-1111-4111-8111-111111111111',
                            '44444444-4444-4444-8444-444444444444',
                            frozenset({'Lab.Admin', 'Lab.LiveCaller'}))


@contextmanager
def authenticated_client(app, **kwargs):
    headers = {**kwargs.pop('headers', {}), 'Authorization': 'Bearer synthetic-offline-test-token'}
    with patch('app.core.auth.validate_token', return_value=SYNTHETIC_ADMIN), \
            TestClient(app, headers=headers, **kwargs) as client:
        yield client
