"""UI calls FastAPI only. Untrusted content is always displayed as plain text."""
import os
import json
import sys
import importlib
from pathlib import Path
from uuid import uuid4
import httpx
import streamlit as st

# Support launching this file directly as well as through run_app.py.
# The UI uses the shared backend card-masking helper during page imports.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
for directory in (PROJECT_ROOT, PROJECT_ROOT / 'backend'):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from frontend.visibility import SHOW_CURRENT25
from frontend.error_messages import describe_error, provider_rejected
from frontend.presentation import metric_rows, page_label, expiry_label, answer_preview, answer_view, comparison_view
from frontend.observations import observation_metrics
from frontend.redaction import artifact_preview
from frontend.authentication import sign_in_gate, auth_headers, bind_identity, load_identity

BASE = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')
st.set_page_config(page_title='AI Security Document Lab', layout='wide')
st.title('AI Security Document Lab')
st.caption('Upload documents, ask questions and check the cited sources.')
sign_in_gate()



def api(method, path, **kwargs):
    try:
        r = httpx.request(method, BASE + path, timeout=180, headers=auth_headers(), follow_redirects=False, **kwargs)
        r.raise_for_status()
        return r.json()
    except httpx.TimeoutException:
        st.error('The local request timed out. Processing may still be running. Refresh Documents to inspect its state before submitting again; no automatic retry was made.')
        return None
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            st.session_state.clear()
            st.error('Your Microsoft access token is invalid or expired. Sign out and sign in again. No automatic request retry was made.')
            st.stop()
        elif exc.response.status_code == 403:
            st.error('Your assigned application role does not permit this action.')
        elif exc.response.status_code == 404 and path == '/predefined-documents':
            st.error('The running backend does not have the predefined-document route. Stop the app with Ctrl+C, restart it with .venv/bin/python run_app.py --live-answers from /home/sigmoid/Ai-Security-Poc, then refresh this page. No automatic retry was made.')
        else:
            st.error(f'Backend rejected this request (HTTP {exc.response.status_code}). Check the file limits and document state. No automatic retry was made.')
        return None
    except Exception as exc:
        st.error(f'Backend request failed ({type(exc).__name__}). Start the backend and inspect its request ID/logs.')
        return None


def artifact_bytes(run, filename):
    try:
        response = httpx.get(BASE+'/results/'+run+'/artifacts/'+filename, timeout=10, headers=auth_headers(), follow_redirects=False)
        return response.content if response.status_code == 200 else None
    except httpx.HTTPError:
        st.warning('Result file unavailable. Refresh after checking backend health; no model request was made.')
        return None


identity = load_identity(api)
if identity is None:
    st.info('An administrator must complete Microsoft sign-in configuration and assign an application role.')
    st.stop()
permissions = bind_identity(identity)
ready = api('GET', '/ready')
if ready and not ready['live']['enabled']:
    st.warning(ready['live']['reason'])
    missing = ready.get('configuration', {}).get('missing_configuration', [])
    if missing:
        st.info('Configure the backend root .env: ' + ', '.join(missing))
workspaces = ['Documents', 'Ask / compare']
if 'evaluation.read' in permissions:
    workspaces += ['Metrics / evaluation', 'Saved experiments']
page = st.sidebar.radio('Workspace', workspaces, index=2 if st.query_params.get('view') == 'metrics' and 'evaluation.read' in permissions else 1)
if ready:
    config = ready.get('configuration', {})
    st.caption('Provider: ' + str(config.get('provider', 'unknown')) + ' · Model: ' + str(config.get('model', 'unknown')))
selected_provider = (ready or {}).get('configuration', {}).get('provider', 'azure_openai')
with st.sidebar.expander('Provider setup'):
    st.write('Configure your existing Azure deployment in the root .env file: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY and AZURE_OPENAI_DEPLOYMENT. Keep the key private.')
    st.caption('Restart the app after changing settings. A compatible Azure deployment, trial credits and an authorized remaining allowance are required for live answers. Entering a key does not send a request or authorize calls.')
provider_name = 'OpenRouter' if selected_provider == 'openrouter' else 'Azure OpenAI'
external_mode = 'openrouter' if selected_provider == 'openrouter' else 'azure_openai'
with st.expander('Processing and defense details'):
    st.write(
        'Documents are parsed, indexed, and searched locally. Local-only mode never calls a model and returns matching evidence. '
        f'{provider_name} mode sends your question and retrieved passages to the external provider for answering (and, in C, screening). '
        'Use it only for content you are authorized to send. Uploaded files are shared with assigned application users. Files, indexes, and request results persist locally; encryption and secure erasure are not provided. '
        'A is the baseline; B adds instruction separation; C adds model-based screening and a payment-card-number check. These are experimental defenses, not production secrecy controls.'
    )
if page == 'Documents':
    st.subheader('Upload documents')
    if SHOW_CURRENT25:
        st.caption('Your uploaded files are separate from the 25 predefined study documents. Choose Predefined documents (25) in Ask / compare to use the current study.')
    st.caption('Upload TXT, Markdown, text PDF or DOCX files, then open Ask / compare to ask questions. Scanned PDFs require text extraction first.')
    if ready:
        with st.expander('Upload limits and extraction details'):
            st.caption('Up to 5 files per upload. The first upload may take longer while the cached CPU embedding model loads. UTF-8 TXT/MD and non-macro DOCX are supported. OCR is not supported.')
            st.json(ready.get('limits', {}), expanded=False)
    file_limit_bytes = (ready or {}).get('limits', {}).get('max_file_bytes', 5 * 1024 * 1024)
    file_limit_mb = max(1, (file_limit_bytes + 1024**2 - 1) // 1024**2)
    with st.form('upload', clear_on_submit=True):
        files = st.file_uploader('Upload documents', type=['txt', 'md', 'pdf', 'docx'], accept_multiple_files=True, max_upload_size=file_limit_mb)
        submit = st.form_submit_button('Upload and index')
    if submit and files:
        limit = (ready or {}).get('limits', {}).get('max_file_bytes', 5 * 1024 * 1024)
        if len(files) > 5 or any(f.size > limit for f in files):
            st.error(f'Choose at most 5 files, each no larger than {limit / 1024**2:g} MB.')
            value = None
        else:
            with st.spinner('Uploading, extracting text, creating chunks and indexing locally. Please wait; do not submit again.'):
                value = api('POST', '/documents', files=[('files', (f.name, f.getvalue(), 'application/octet-stream')) for f in files])
        if value:
            st.session_state['upload_result'] = value
            successful=[r for r in value.get('outcomes',[]) if r.get('status')=='ready' and r.get('document_id')]
            if successful:
                st.session_state['pending_uploaded_selection']=successful[-1]['document_id']
    if 'upload_result' in st.session_state:
        upload_preview = answer_preview(st.session_state['upload_result'])
        for outcome in upload_preview.get('outcomes', []):
            st.text(str(outcome.get('filename', 'Document')) + ' — ' + str(outcome.get('status', 'unknown')))
            if outcome.get('error'):
                st.warning(outcome['error'])
        with st.expander('Upload details'):
            st.json(upload_preview, expanded=False)
    show_deleted = st.checkbox('Show deleted documents', value=False,
                               help='Deleted documents are excluded from future retrieval. This only changes the history view; it does not delete or restore anything.')
    data = api('GET', '/documents', params={'include_deleted': show_deleted})
    documents = (data or {}).get('documents', [])
    if not documents:
        if show_deleted:
            st.info('No documents match this view.')
        else:
            st.info('No active documents yet. Deleted document history is hidden; use “Show deleted documents” to view it.')
    for item in answer_preview(documents):
        with st.expander(f"{item['filename']} | {item['status']}"):
            st.text(item['filename'])
            st.text(f"Document: {item['document_id']}\nVersion: {item['id']}\nActive: {item.get('active_version')}\nSHA256: {item['sha256']}")
            for warning in item.get('warnings', []):
                st.warning(warning)
            if item.get('error'):
                st.text(item['error'])
            for block in item.get('blocks', [])[:12]:
                st.caption(f"{page_label(block['page'])} · {block['section']}")
                st.text(block['text'][:5000])
            if item['status'] == 'needs_review' and 'documents.manage' not in permissions:
                st.info('An administrator must review and activate incomplete extraction.')
            if item['status'] == 'needs_review' and 'documents.manage' in permissions:
                accept = st.checkbox('I accept incomplete text extraction and its citation limits', key='a'+item['id'])
                if st.button('Activate available text only', disabled=not accept, key='p'+item['id']):
                    api('POST', f"/versions/{item['id']}/accept-partial")
                    st.rerun()
            if item.get('active_version') == item['id'] and not item.get('deleted') and 'documents.manage' in permissions:
                with st.form('replace'+item['id']):
                    replacement = st.file_uploader('Explicit replacement of this document', type=['txt','md','pdf','docx'], max_upload_size=file_limit_mb)
                    replace = st.form_submit_button('Replace active version')
                if replace and replacement:
                    with st.spinner('Replacing and indexing the new version locally…'):
                        st.json(answer_preview(api('POST', f"/documents/{item['document_id']}/replace", params={'expected_version': item['id']}, files={'file': (replacement.name, replacement.getvalue())})))
                confirm = st.checkbox('Confirm delete this document from future retrieval', key='d'+item['id'])
                if st.button('Delete', disabled=not confirm, key='b'+item['id']):
                    api('DELETE', f"/documents/{item['document_id']}", params={'expected_version': item['id']})
                    st.rerun()
            if item.get('active_version') is None and not item.get('deleted') and 'documents.manage' in permissions:
                confirm_unready = st.checkbox('Confirm delete this unready document', key='du'+item['id'])
                if st.button('Delete unready document', disabled=not confirm_unready, key='bu'+item['id']):
                    api('DELETE', f"/documents/{item['document_id']}")
                    st.rerun()
if page == 'Ask / compare':
    def clear_library_results():
        for key in ('answer', 'local_search', 'comparison', 'ask_document_id'):
            st.session_state.pop(key, None)
    if not st.session_state.get('uploaded_scope_default_v3'):
        clear_library_results()
        st.session_state['ask_library']='playground'
        st.session_state['uploaded_scope_default_v3']=True
    pending_upload=st.session_state.pop('pending_uploaded_selection',None)
    if pending_upload:
        clear_library_results()
        st.session_state['ask_library']='playground'
        st.session_state['ask_document_id']=pending_upload
    if not SHOW_CURRENT25 and st.session_state.get('ask_library') != 'playground':
        clear_library_results()
        st.session_state['ask_library']='playground'
    search_collection = st.radio('Document library', ['playground', 'predefined'] if SHOW_CURRENT25 else ['playground'],
        index=0, key='ask_library', on_change=clear_library_results,
        format_func=lambda value: 'Uploaded documents' if value == 'playground' else 'Predefined documents (25)')
    available_documents = (api('GET', '/documents' if search_collection == 'playground' else '/predefined-documents') or {}).get('documents', [])
    document_names = {item['document_id']: answer_preview(item['filename']) for item in available_documents
                      if search_collection == 'predefined' or (item.get('status') == 'ready' and item.get('active_version') == item.get('id'))}
    if 'ask_document_id' not in st.session_state or st.session_state['ask_document_id'] not in {'', *document_names}:
        st.session_state['ask_document_id'] = next(iter(document_names),'') if search_collection=='playground' else ''
    def clear_document_results():
        for key in ('answer','local_search','comparison'):
            st.session_state.pop(key,None)
    chosen_document = st.selectbox('Search within', [*document_names, ''], key='ask_document_id',
        on_change=clear_document_results,
        format_func=lambda value: document_names.get(value, 'All active documents'))
    if search_collection=='predefined':
        st.caption('This security-test library contains adversarial test content. Choose Uploaded documents for ordinary questions about your own files.')
    elif chosen_document:
        st.caption('Questions use only the selected uploaded document: '+document_names[chosen_document])
    st.caption('Ask any new question about this library. Search uses the selected document or all documents in this library; test-case expected answers are not used.')
    demo_id = next((did for did, name in document_names.items() if name == 'End-to-end live verification 20261026.txt'), None)
    def use_demo_question():
        st.session_state['ask_document_id'] = demo_id
        st.session_state['ask_question'] = 'How many study leave days does the ORCHID-LIVE-20261026 policy grant?'
        st.session_state.pop('answer', None)
        st.session_state.pop('local_search', None)
    if demo_id:
        st.button('Use verified demo question', on_click=use_demo_question,
                  help='Selects the fictional demo policy and fills the question. Click Ask to send it.')
    st.caption('Interactive capacity is for benign questions; benchmark attacks belong to separately authorized evaluation. Never resend a prohibited provider-blocked payload.')
    mode = st.selectbox('Defense configuration', ['A', 'B', 'C'], index=1,
                        format_func=lambda value: {'A': 'A — Baseline RAG', 'B': 'B — Instruction separation', 'C': 'C — LLM screening + instruction separation'}[value])
    st.caption('Choose a defense before asking. A: baseline · B: separation · C: screening + separation')
    active_policy = (ready or {}).get('answer_policy', {})
    if mode in {'B', 'C'}:
        st.caption('Backend answer policy: ' + active_policy.get('separation_version', 'Version unavailable — restart the updated backend'))
    # Users without live-call permission can still search their shared library locally.
    processing_mode = external_mode if 'live.call' in permissions else 'local'

    with st.form('question'):
        question = st.text_area('Question', max_chars=2000, key='ask_question')
        live_status = (ready or {}).get('live', {})
        can_use_external = live_status.get('mode_available', {}).get(mode, live_status.get('enabled', False))
        if processing_mode != 'local':
            st.caption(f'Clicking “Ask once via {provider_name}” sends your question and retrieved document passages to {provider_name} for processing.')
            if not can_use_external:
                st.info(live_status.get('reason') or 'Insufficient capacity for this configuration. A/B require 1 call; C requires 2.')
        can_ask = processing_mode == 'local' or can_use_external
        submit_question = st.form_submit_button('Search locally' if processing_mode == 'local' else 'Ask once via ' + provider_name, disabled=not can_ask)
    if submit_question and can_ask and question.strip():
        if processing_mode == 'local':
            with st.spinner('Searching local evidence. No model request will be made.'):
                st.session_state['local_search'] = api('POST', '/search', json={
                    'question': question, 'mode': mode, 'request_id': str(uuid4()),
                    'collection': search_collection, 'document_id': chosen_document or None})
            if st.session_state['local_search'] is None:
                st.stop()
            st.session_state.pop('answer', None)
        else:
            with st.spinner('Retrieving evidence and requesting an answer. No automatic retries.'):
                st.session_state['answer'] = api('POST', '/chat', json={
                    'question': question, 'mode': mode, 'request_id': str(uuid4()),
                    'external_processing_confirmed': True,
                    'collection': search_collection, 'document_id': chosen_document or None,
                })
            if st.session_state['answer'] is None:
                st.stop()
            st.session_state.pop('local_search', None)
        st.rerun()
    local_search = answer_preview(st.session_state.get('local_search'))
    if local_search is not None:
        st.subheader('Matching sources')
        st.info('No model was called. These are matching document passages, not a generated answer.')
        hits = local_search.get('hits', [])
        if not hits:
            st.info('No active evidence matched this question.')
        for hit in hits:
            with st.expander(str(hit.get('filename', 'Document')) + ' · ' + page_label(hit.get('page')), expanded=True):
                st.text(hit.get('text', ''))
                st.caption('Source: ' + str(hit.get('id')) + ' · Version: ' + str(hit.get('version_id')))
                if hit.get('partial_text'):
                    st.warning('This is explicitly accepted partial extraction.')
    value = st.session_state.get('answer')
    if value:
        saved_version = value.get('defense_versions', {}).get('separation')
        if value.get('mode') in {'B', 'C'}:
            st.caption('Policy used for this saved answer: ' + (saved_version or 'Unknown'))
            if active_policy.get('separation_version') and saved_version != active_policy['separation_version']:
                st.warning('This saved answer uses an older or unknown policy. It has not been regenerated with the current policy. A new submission consumes the existing live allowance.')
        rejected = provider_rejected(value)
        error_description = describe_error(answer_preview(value)) if value.get('status') in {'llm_error', 'screening_error'} else None
        measured = observation_metrics(value)
        value = answer_view(value)
        st.subheader('Answer')
        st.write('Configuration:', value.get('mode'), '· Status:', 'Azure blocked this request' if rejected else value.get('status'))
        if isinstance(value.get('latency_ms'), (int, float)):
            st.caption(f"Elapsed: {value['latency_ms']/1000:.2f} seconds · Local units reserved: {value.get('reservation_units', 0)}")
        if value.get('status') in {'llm_error', 'screening_error'}:
            st.error(error_description)
            if rejected:
                st.info('The provider declined the submitted content. For questions about your own file, choose Uploaded documents and select that file in Search within. This saved rejection is preserved; changing the selection sends no request.')
            st.caption('This is the saved result of your previous submission; it is not retried on refresh.')
        else:
            st.text(value.get('answer') or value.get('error', ''))
        for ref in value.get('references', []):
            if ref.get('partial_text'):
                st.warning('This citation uses explicitly accepted partial extraction; unread content may affect the answer.')
            st.caption(f"Source: {ref.get('filename', 'Document')} · {page_label(ref.get('page'))}")
        with st.expander('Measurements for this answer'):
            st.dataframe(measured, hide_index=True)
            st.caption('These observations update with your submitted answer. They do not change predefined benchmark results or assign missing judgments.')
    st.divider()
    st.subheader('Compare A/B/C on one benign question')
    st.caption('One frozen retrieval result; up to 4 calls / 128000 units. Unreviewed interactive observations, not benchmark security metrics. No automatic retries.')
    capacity = (ready or {}).get('live', {})
    can_compare = (capacity.get('enabled', False) and capacity.get('remaining_calls', 0) >= 4
                   and capacity.get('remaining_reserved_tokens', 0) >= 128000)
    with st.form('benign-comparison'):
        comparison_question = st.text_area('Benign comparison question', max_chars=2000)
        compare_submit = st.form_submit_button('Compare once — up to 4 calls', disabled=not can_compare)
    if compare_submit and comparison_question.strip():
        with st.spinner('Running A, B, then C with the same initial evidence. Stops on error.'):
            st.session_state['comparison'] = api('POST', '/compare', json={
                'question': comparison_question, 'request_id': str(uuid4()),
                'collection': search_collection, 'document_id': chosen_document or None,
                'external_processing_confirmed': True})
        if st.session_state['comparison'] is None:
            st.stop()
        st.rerun()
    comparison = st.session_state.get('comparison')
    if comparison:
        comparison = answer_preview(comparison)
        st.write('Comparison status:', comparison.get('status'))
        st.caption('Saved observations — semantic review pending; not rerun on refresh.')
        if comparison.get('error'):
            st.warning(comparison['error'])
        for column, label in zip(st.columns(3), 'ABC'):
            with column:
                st.write('Configuration ' + label)
                response = comparison.get('results', {}).get(label)
                if response is None:
                    st.info('Not executed.')
                else:
                    st.write('Status:', response.get('status'))
                    if label in {'B', 'C'}:
                        saved_version = response.get('defense_versions', {}).get('separation')
                        st.caption('Answer policy: ' + (saved_version or 'Unknown'))
                        if active_policy.get('separation_version') and saved_version != active_policy['separation_version']:
                            st.warning('Saved comparison uses an older or unknown policy; refresh does not rerun it.')
                    if response.get('status') in {'llm_error', 'screening_error'}:
                        st.error(describe_error(response))
                    else:
                        st.text(answer_view(response).get('answer') or response.get('error', ''))
                    for reference in answer_view(response)['references']:
                        st.caption('Source: ' + str(reference.get('filename')) + ' · ' + page_label(reference.get('page')))
                    st.caption('Latency: ' + str(response.get('latency_ms')) + ' ms')
                    with st.expander('Measurements — ' + label):
                        st.dataframe(observation_metrics({**response, 'mode': label}), hide_index=True)
        st.download_button('Download answers and citations JSON', json.dumps(comparison_view(comparison), indent=2),
                           file_name='benign-comparison-unreviewed.json', mime='application/json')
if page == 'Metrics / evaluation':
    metrics_ui = importlib.import_module('frontend.metrics')
    importlib.reload(metrics_ui)
    metrics_ui.render_metrics(api, BASE)

if page == 'Saved experiments':
    runs = api('GET', '/results')
    names = (runs or {}).get('runs', [])
    if not names:
        st.info('No saved experiments. Run the evaluator CLI; no example metrics are presented as measurements.')
    else:
        name = st.selectbox('Experiment', names, format_func=answer_preview)
        value = answer_preview(api('GET', '/results/'+name))
        if value:
            st.json(value['experiment'], expanded=False)
            summary = value.get('summary') or {}
            coverage = summary.get('coverage', {})
            st.warning('Saved observations only. Human review and error coverage determine which metrics are eligible.')
            st.subheader('Assignment metrics')
            st.dataframe(metric_rows(summary), hide_index=True, use_container_width=True)
            st.caption('Rates show numerator/denominator. N/A is not zero. Screening flags and blocks are observed behavior; false-positive judgments require benign-case review. Latency includes saved failed routes. Different models/prompt versions must not be pooled.')
            st.write('Review coverage', coverage)
            st.json(summary, expanded=False)
            with st.expander('Download actual results and human-review records'):
                st.caption('These downloads are masked previews. Original records remain local for review using the documented CLI. Review templates contain blank judgments; downloading does not approve a result.')
                for artifact in ['records.csv','comparison.csv','review-template.json','review-packets.json','operational-summary.json']:
                    content = artifact_bytes(name, artifact)
                    if content is not None:
                        st.download_button('Download masked '+artifact, artifact_preview(content, filename=artifact),
                                           file_name=answer_preview(name)+'-masked-'+artifact, key=name+artifact)
            with st.expander('Metric charts — check denominators and review status'):
                for artifact in ['asr','exposed_asr','benign_task_success','benign_false_flags','benign_false_blocks','quality','latency']:
                    content = artifact_bytes(name, artifact+'.png')
                    if content is not None:
                        st.image(content, caption=artifact.replace('_',' '))
            cases = sorted({row['case_id'] for row in value['results']})
            for case_id in cases:
                grouped = {row['mode']:row for row in value['results'] if row['case_id']==case_id}
                with st.expander(case_id):
                    first = next(iter(grouped.values()))
                    st.text(first.get('case', {}).get('query', ''))
                    for column, mode in zip(st.columns(3), 'ABC'):
                        with column:
                            st.write('Configuration '+mode)
                            row = grouped.get(mode)
                            if row is None:
                                st.info('No saved execution for this configuration.')
                                continue
                            response = row['response']
                            st.write('Status:', response['status'])
                            if response['status'] in {'llm_error','screening_error'}:
                                st.error(describe_error(response))
                            else:
                                st.text(response.get('answer',''))
                            judgment = row.get('judgment', {})
                            st.caption('Human reviewed' if judgment.get('reviewer') else 'Human review pending / operational error ungraded')
                            if judgment.get('reviewer'):
                                st.json({k:judgment.get(k) for k in ['attack_success','task_success','quality','notes']}, expanded=False)
                            for ref in response.get('references', []):
                                st.text(ref['filename']+' · '+ref['section']+' · '+ref['id'])
                                with st.expander('Source excerpt — masked document text'):
                                    st.text(ref['text'])
                            st.json({'screening':response.get('screening'),
                                     'original_evidence':response.get('candidate_evidence',[]),
                                     'retained_evidence':response.get('supplied_evidence',[])}, expanded=False)

