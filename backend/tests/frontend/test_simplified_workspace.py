from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from backend.tests.frontend.test_metrics_workspace import application
from app.evaluation.simple_dashboard import snapshot


def test_simple_workspace_keeps_saved_metrics_and_removes_added_panels():
    calls=[]
    with patch('httpx.request',side_effect=application(snapshot(),calls)),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve()),default_timeout=20).run()
        assert app.sidebar.radio[0].options==['Documents','Ask / compare','Metrics / evaluation','Saved experiments']
        app.sidebar.radio[0].set_value('Metrics / evaluation').run()
        assert not app.exception
        assert next(r for r in app.radio if r.label=='Results').value=='Saved study'
        assert not any('Additional challenge' in e.label for e in app.expander)
        assert not any('Same questions' in m.value for m in app.markdown)
        next(r for r in app.radio if r.label=='Metrics display').set_value('Table').run()
        assert app.dataframe[0].value.iloc[1]['A']=='11.1% (2/18)' or '11.1% (2/18)' in app.dataframe[0].value['A'].tolist()
        for page in ['Documents','Saved experiments','Ask / compare']:
            app.sidebar.radio[0].set_value(page).run()
            assert not app.exception
        assert all(method=='GET' for method,_ in calls)
