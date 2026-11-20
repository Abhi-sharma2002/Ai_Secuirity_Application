"""Authentication UI tests use synthetic identities and no external requests."""
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from streamlit.testing.v1 import AppTest

SCRIPT = str(Path('frontend/streamlit_app.py').resolve())


def test_unconfigured_sign_in_does_not_read_documents_or_call_api():
    with patch('httpx.request', side_effect=AssertionError('No API before sign-in')):
        app = AppTest.from_file(SCRIPT).run(timeout=20)
    assert not app.exception
    assert any('configuration' in str(item.value) for item in app.info)
    assert not app.file_uploader


@pytest.mark.parametrize('reviewer', [False, True])
def test_workspace_and_requests_follow_verified_backend_permissions(reviewer):
    permissions = ['documents.read', 'documents.upload', 'search']
    if reviewer:
        permissions += ['evaluation.read', 'evaluation.review']
    calls = []
    def request(method, url, **kwargs):
        assert kwargs['headers'] == {'Authorization': 'Bearer synthetic-test-token'}
        calls.append((method, url))
        if url.endswith('/auth/me'):
            data = {'subject': 'synthetic-subject', 'roles': ['Lab.Reviewer' if reviewer else 'Lab.User'], 'permissions': permissions}
        elif url.endswith('/ready'):
            data = {'live': {'enabled': False, 'reason': 'Synthetic offline configuration'}, 'limits': {}}
        elif url.endswith('/search'):
            data = {'hits': []}
        else:
            data = {'documents': []}
        return httpx.Response(200, json=data, request=httpx.Request(method, url))
    with patch('frontend.authentication.sign_in_gate'), \
         patch('frontend.authentication.auth_headers', return_value={'Authorization': 'Bearer synthetic-test-token'}), \
         patch('httpx.request', side_effect=request), \
         patch('socket.socket.connect', side_effect=AssertionError('No external network')):
        app = AppTest.from_file(SCRIPT).run(timeout=20)
        assert not app.exception
        options = app.sidebar.radio[0].options
        assert ('Metrics / evaluation' in options) == reviewer
        assert ('Saved experiments' in options) == reviewer
        assert 'Search locally' in [button.label for button in app.button]
        assert all(method == 'GET' for method, _ in calls)
