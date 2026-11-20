"""An existing Streamlit process may retain the pre-update presentation module."""
from pathlib import Path
from unittest.mock import patch
import httpx
from streamlit.testing.v1 import AppTest
from frontend import presentation


def test_startup_works_with_cached_presentation_missing_new_measurement_helper(monkeypatch):
    monkeypatch.delattr(presentation, 'observation_metrics', raising=False)
    def request(method, url, **kwargs):
        if url.endswith('/ready'):
            value={'live':{'enabled':False,'reason':'Synthetic offline check'},'limits':{}}
        else:
            value={'documents':[]}
        return httpx.Response(200,json=value,request=httpx.Request(method,url))
    with patch('httpx.request',side_effect=request),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve())).run(timeout=15)
        assert not app.exception
        app.sidebar.radio[0].set_value('Ask / compare').run()
        assert not app.exception
        assert any(item.label=='Question' for item in app.text_area)
