"""Presentation uses real saved examples with explicit origin; no provider calls."""
from pathlib import Path
from unittest.mock import patch
import httpx
from streamlit.testing.v1 import AppTest
from app.evaluation.current25 import snapshot
from backend.tests.frontend.test_metrics_workspace import payload, application


def test_presentation_opens_with_actual_saved_answers_and_only_gets():
    data=snapshot();calls=[]
    def request(method,url,**kwargs):
        calls.append((method,url))
        if url.endswith('/ready'):value={'live':{'enabled':False,'reason':'Synthetic offline verification'},'limits':{}}
        elif url.endswith('/evaluation-current25'):value=data
        elif '/evidence/' in url:value={'hits':[]}
        elif url.endswith('/evaluation-v3'):value={'case_comparisons':[]}
        else:value={'documents':[]}
        return httpx.Response(200,json=value,request=httpx.Request(method,url))
    with patch('httpx.request',side_effect=request),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve()))
        app.query_params['view']='presentation'
        app.run(timeout=20)
        assert not app.exception
        assert app.sidebar.radio[0].value=='Presentation'
        metrics={m.label:m.value for m in app.metric}
        assert metrics['Predefined documents']=='25' and metrics['Uploaded documents']=='0'
        assert any('previously recorded Azure answers' in c.value for c in app.caption)
        assert all(method=='GET' for method,_ in calls)
        assert not any('/chat' in url or '/compare' in url for _,url in calls)


def test_metrics_rerun_reloads_a_stale_render_function(monkeypatch):
    from frontend import metrics
    def stale(*args):raise AssertionError('Stale renderer must be reloaded')
    monkeypatch.setattr(metrics,'render_metrics',stale)
    calls=[]
    with patch('httpx.request',side_effect=application(payload(),calls)),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve())).run(timeout=20)
        app.sidebar.radio[0].set_value('Metrics / evaluation').run()
        assert not app.exception
        assert any(m.label=='Predefined documents' for m in app.metric)
        assert not any(m.label.startswith('ASR —') for m in app.metric)


def test_presentation_recovers_when_file_watcher_removes_registered_module(monkeypatch):
    import sys
    from frontend import demo
    # Streamlit can remove sys.modules entries while a package attribute still
    # points to the earlier object. Import through the module registry first.
    monkeypatch.delitem(sys.modules,'frontend.demo',raising=False)
    calls=[]
    with patch('httpx.request',side_effect=application(payload(),calls)),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve()),default_timeout=20)
        app.query_params['view']='presentation'
        app.run()
        assert not app.exception
        assert all(method=='GET' for method,_ in calls)
