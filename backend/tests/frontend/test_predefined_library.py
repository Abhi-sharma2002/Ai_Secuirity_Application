"""New questions use the selected library without running a benchmark."""
from unittest.mock import patch
import httpx
import pytest
from fastapi import HTTPException
from app.api.runtime import Query, predefined_search
from backend.tests.frontend.test_openrouter_submission import application, ask_page


def test_local_question_routes_to_predefined_library():
    calls = []
    base = application({'enabled': False, 'reason': 'Synthetic disabled'}, calls, provider='azure_openai')
    def request(method, url, **kwargs):
        if url.endswith('/predefined-documents'):
            return httpx.Response(200, json={'documents': [
                {'document_id': 'fixture-one', 'filename': 'policy.txt'}]},
                request=httpx.Request(method, url))
        return base(method, url, **kwargs)
    with patch('httpx.request', side_effect=request), patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')):
        app = ask_page('azure_openai')
        next(r for r in app.radio if r.label == 'Document library').set_value('predefined').run()
        next(r for r in app.radio if r.label == 'Document handling').set_value('local').run()
        next(t for t in app.text_area if t.label == 'Question').input('A new policy question')
        next(b for b in app.button if b.label == 'Search locally').click().run()
        assert not app.exception
        posts = [(url, kw) for method, url, kw in calls if method == 'POST']
        assert len(posts) == 1
        assert posts[0][0].endswith('/search')
        assert posts[0][1]['json']['collection'] == 'predefined'


def test_unknown_predefined_document_is_rejected_before_retrieval():
    with patch('app.evaluation.simple_runner._manifest', return_value=({'fixtures': [{'fixture_id': 'known'}]}, 'hash')), \
         patch('app.evaluation.simple_runner._retrieve') as retrieve:
        with pytest.raises(HTTPException) as error:
            predefined_search(Query(question='New question', collection='predefined', document_id='unknown', request_id='test-request'))
        assert error.value.status_code == 409
        retrieve.assert_not_called()


def test_backend_error_remains_visible_after_local_submission():
    calls = []
    base = application({'enabled': False, 'reason': 'Synthetic disabled'}, calls, provider='azure_openai')
    def request(method, url, **kwargs):
        if method == 'POST' and url.endswith('/search'):
            return httpx.Response(500, json={'detail': 'Operational error'}, request=httpx.Request(method, url))
        return base(method, url, **kwargs)
    with patch('httpx.request', side_effect=request), patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')):
        app = ask_page('azure_openai')
        next(r for r in app.radio if r.label == 'Document handling').set_value('local').run()
        next(t for t in app.text_area if t.label == 'Question').input('A new question')
        next(b for b in app.button if b.label == 'Search locally').click().run()
        assert not app.exception
        assert any('HTTP 500' in error.value for error in app.error)


def test_search_defaults_to_current_predefined_library():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    calls=[]
    with patch('httpx.request',side_effect=application({'enabled':False,'reason':'Synthetic disabled'},calls,provider='azure_openai')), \
         patch('socket.socket.connect',side_effect=AssertionError('Network forbidden')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve())).run(timeout=15)
        app.sidebar.radio[0].set_value('Search evidence').run()
        assert next(r for r in app.radio if r.label=='Search library').value=='predefined'
        app.text_input[0].input('Study leave policy')
        next(b for b in app.button if b.label=='Search locally').click().run()
        assert not app.exception
        posts=[kw for method,url,kw in calls if method=='POST' and url.endswith('/search')]
        assert len(posts)==1 and posts[0]['json']['collection']=='predefined'
