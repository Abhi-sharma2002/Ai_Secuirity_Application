"""Actual metrics UI with labeled synthetic replies; sockets are forbidden."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import httpx
from PIL import Image
from streamlit.testing.v1 import AppTest

from app.evaluation import simple_dashboard as dashboard, simple_reporting as report
from app.evaluation.simple_config import load_config
from backend.tests.evaluation.test_simple_reporting import DATA, BENIGN, ATTACKS, row
from frontend.presentation import evaluation_metric_rows


def payload(rows=()):
    return {'status': 'partial' if rows else 'no_records', 'counts': {
        'recorded': len(rows), 'expected': len(DATA['cases']) * 3,
        'missing': len(DATA['cases']) * 3 - len(rows), 'errors': 0,
        'needs_review': 0, 'quality_reviewed': 0},
        'summary': report.summarize(rows, DATA), 'configuration': load_config(),
        'dataset': {'cases': len(DATA['cases']), 'documents': len(DATA['fixtures'])},
        'origin': 'synthetic UI test only', 'records': list(rows), 'notes': ['Errors are excluded from rates.'],
        'definitions': [dict(zip(('key', 'metric', 'formula', 'better', 'kind'), d)) for d in dashboard.DEFINITIONS],
        'charts_current': False, 'artifacts': [], 'provider_execution_enabled': False}


def application(data, calls):
    def request(method, url, **kwargs):
        calls.append((method, url))
        value = data if url.endswith(('/evaluation-v3', '/evaluation-current25')) else (
            {'live': {'enabled': False, 'reason': 'Synthetic offline test'}, 'limits': {}}
            if url.endswith('/ready') else {'documents': []})
        return httpx.Response(200, json=value, request=httpx.Request(method, url))
    return request


def metrics_page():
    script = Path(__file__).resolve().parents[3] / 'frontend/streamlit_app.py'
    app = AppTest.from_file(str(script),default_timeout=20).run(timeout=15)
    app.sidebar.radio[0].set_value('Metrics / evaluation').run()
    assert not app.exception
    return app


def test_every_metric_has_na_or_explicit_denominators():
    data = payload()
    rows = evaluation_metric_rows(data['summary'], data['definitions'])
    assert len(rows) == len(dashboard.DEFINITIONS)
    assert all(r['A'].startswith('N/A') for r in rows)
    data = payload([row(ATTACKS[0], attack_succeeded='true'), row(BENIGN[0], 'C')])
    rows = evaluation_metric_rows(data['summary'], data['definitions'])
    by_name = {r['Metric']: r for r in rows}
    assert by_name['Attack success — all']['A'] == '100.0% (1/1)'
    assert by_name['Attack success — all']['B'] == 'N/A'
    assert by_name['False positive rate']['A'] == 'N/A (C only)'


def test_current_and_saved_metrics_keep_tables_and_read_only_refresh(monkeypatch):
    monkeypatch.setattr('frontend.visibility.SHOW_CURRENT25',True)
    calls=[]
    with patch('httpx.request',side_effect=application(payload(),calls)),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=metrics_page()
        assert next(r for r in app.radio if r.label=='Results').value=='Saved study'
        assert next(r for r in app.radio if r.label=='Metrics display').value=='Graphs'
        assert not any(e.label=='How to explain these graphs' for e in app.expander)
        next(r for r in app.radio if r.label=='Metrics display').set_value('Table').run()
        assert set(app.dataframe[0].value.columns)=={'Metric','A','B','C'}
        assert all(v.startswith('N/A') for v in app.dataframe[0].value['A'])
        assert any('unavailable values are not zero' in c.value for c in app.caption)
        next(r for r in app.radio if r.label=='Results').set_value('25-document study').run()
        next(b for b in app.button if b.label=='Refresh results').click().run()
        assert not app.exception and any(u.endswith('/evaluation-current25') for _,u in calls)
        assert all(m=='GET' for m,_ in calls)


def test_graph_view_renders_without_cloud_or_artifact_requests():
    from frontend.charts import metric_chart
    calls=[]
    with patch('frontend.charts.metric_chart',wraps=metric_chart) as chart,patch('httpx.request',side_effect=application(payload([row()]),calls)),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=metrics_page();next(r for r in app.radio if r.label=='Metrics display').set_value('Graphs').run()
        assert not app.exception
        assert chart.call_count==2
        assert all(m=='GET' for m,_ in calls)


def test_upload_validation_is_visible_separate_from_interactive_history():
    calls=[];base=application(payload(),calls)
    docs=[dict(document_id='test-document',version_id='test-version',filename='sample.txt')]
    saved=dict(documents=docs,planned_rows=3,recorded_rows=1,unrun_rows=2,rows=[dict(
        filename='sample.txt',kind='summary',mode='B',status='answered',implementation_run=3,
        citations_in_approved_scope=True,full_card_in_delivered_answer=False)])
    def request(method,url,**kwargs):
        if url.endswith('/evaluation-uploads'):
            calls.append((method,url));return httpx.Response(200,json=dict(documents=docs,document_count=1,observations=[],note='Interactive responses only'),request=httpx.Request(method,url))
        return base(method,url,**kwargs)
    with patch('httpx.request',side_effect=request),patch('frontend.upload_validation.load_validation',return_value=saved),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=metrics_page();next(r for r in app.radio if r.label=='Results').set_value('Uploaded documents').run()
        assert not app.exception
        assert any(s.value=='Uploaded-document validation' for s in app.subheader)
        assert any('1 / 3' in c.value and '2 unrun' in c.value for c in app.caption)
        assert app.dataframe[0].value.iloc[0]['Status']=='answered'
        assert all(m=='GET' for m,_ in calls)


def test_five_tests_per_document_are_reachable_and_png_is_downloadable(monkeypatch):
    monkeypatch.setattr('frontend.visibility.SHOW_CURRENT25',True)
    from app.evaluation.document_suite import snapshot
    from app.evaluation.suite_context import current_suite
    with current_suite():privacy=snapshot()
    calls=[];base=application(payload(),calls)
    def request(method,url,**kwargs):
        if url.endswith('/evaluation-current25-privacy'):
            calls.append((method,url));return httpx.Response(200,json=privacy,request=httpx.Request(method,url))
        return base(method,url,**kwargs)
    with patch('httpx.request',side_effect=request),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=metrics_page()
        assert len(app.get('download_button'))==1
        next(r for r in app.radio if r.label=='Results').set_value('25-document study').run()
        next(r for r in app.radio if r.label=='Study view').set_value('Five tests per document').run()
        assert not app.exception
        assert len(app.dataframe[0].value)==5
        assert set(app.dataframe[0].value['A'])=={'Not run'}
        assert len(app.get('download_button'))==1
        assert all(method=='GET' for method,_ in calls)


def test_current25_study_is_hidden_by_default():
    calls=[]
    with patch('httpx.request',side_effect=application(payload(),calls)),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=metrics_page()
        assert next(r for r in app.radio if r.label=='Results').options==['Saved study','Uploaded documents']
        app.sidebar.radio[0].set_value('Ask / compare').run()
        assert next(r for r in app.radio if r.label=='Document library').options==['Uploaded documents']
        app.sidebar.radio[0].set_value('Documents').run()
        assert not app.exception
        assert not any('25 predefined' in c.value for c in app.caption)
        assert not any('/evaluation-current25' in url or '/predefined-documents' in url for _,url in calls)
