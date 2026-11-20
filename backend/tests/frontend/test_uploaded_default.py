from pathlib import Path
from unittest.mock import patch
import httpx
from streamlit.testing.v1 import AppTest


def test_ordinary_questions_default_to_one_uploaded_document_without_provider_calls(monkeypatch):
    # Ordinary users without the additional live-call role search locally.
    monkeypatch.setattr('frontend.authentication.bind_identity',
                        lambda identity: frozenset({'documents.read', 'documents.upload', 'search'}))
    calls=[]
    def request(method,url,**kwargs):
        calls.append((method,url,kwargs))
        if url.endswith('/ready'):value={'live':{'enabled':False,'reason':'Offline test'},'limits':{},'configuration':{'provider':'azure_openai'}}
        elif url.endswith('/documents'):value={'documents':[{'document_id':'intro','id':'v1','active_version':'v1','status':'ready','filename':'introduction.txt'},{'document_id':'other','id':'v2','active_version':'v2','status':'ready','filename':'other.txt'}]}
        elif url.endswith('/search'):value={'hits':[]}
        else:value={'documents':[]}
        return httpx.Response(200,json=value,request=httpx.Request(method,url))
    with patch('httpx.request',side_effect=request),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve()),default_timeout=20).run()
        assert not app.exception
        assert next(r for r in app.radio if r.label=='Document library').value=='playground'
        selector=next(s for s in app.selectbox if s.label=='Search within')
        assert selector.value=='intro'
        assert not any(url.endswith('/predefined-documents') for _,url,_ in calls)
        next(t for t in app.text_area if t.label=='Question').input('What do you know about this document?')
        next(b for b in app.button if b.label=='Search locally').click().run()
        posts=[kwargs['json'] for method,url,kwargs in calls if method=='POST' and url.endswith('/search')]
        assert posts[0]['document_id']=='intro' and posts[0]['collection']=='playground'
        assert not any(url.endswith('/chat') for _,url,_ in calls)
        app.session_state['answer']={'status':'llm_error','answer':'Old rejection'}
        next(s for s in app.selectbox if s.label=='Search within').set_value('other').run()
        assert not app.exception
        assert 'answer' not in app.session_state


def test_new_upload_selection_replaces_stale_document_and_answer():
    calls=[]
    def request(method,url,**kwargs):
        calls.append((method,url,kwargs))
        if url.endswith('/ready'):value={'live':{'enabled':False,'reason':'Offline test'},'limits':{}}
        elif url.endswith('/documents'):value={'documents':[{'document_id':k,'id':k+'-v','active_version':k+'-v','status':'ready','filename':k+'.txt'} for k in ['new','old']]}
        else:value={}
        return httpx.Response(200,json=value,request=httpx.Request(method,url))
    with patch('httpx.request',side_effect=request),patch('socket.socket.connect',side_effect=AssertionError('No network')):
        app=AppTest.from_file(str(Path('frontend/streamlit_app.py').resolve()),default_timeout=20).run()
        next(s for s in app.selectbox if s.label=='Search within').set_value('old').run()
        app.session_state['answer']={'status':'insufficient_evidence','answer':'Old source'}
        app.session_state['pending_uploaded_selection']='new'
        app.run()
        assert not app.exception
        assert next(s for s in app.selectbox if s.label=='Search within').value=='new'
        assert 'answer' not in app.session_state
        assert all(method=='GET' for method,_,_ in calls)
