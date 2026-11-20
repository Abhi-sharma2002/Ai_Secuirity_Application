"""Presentation of actual saved observations. No inference or synthetic answers."""
import streamlit as st
from frontend.presentation import answer_preview


def render_demo(api):
    st.subheader('Document assistant · presentation')
    st.caption('Current study: 25 document packs · 47 test cases · A / B / C defenses')
    raw = api('GET', '/evaluation-current25')
    if not raw or 'case_comparisons' not in raw:
        st.info('Saved comparisons are unavailable. Use Search evidence to inspect the local document library.')
        return
    value = answer_preview(raw)
    examples = [c for c in value['case_comparisons'] if not c['adversarial'] and
                all(c['modes'][m]['state'] == 'Answered' and c['modes'][m].get('answer') for m in 'ABC')]
    documents=api('GET','/documents') or {}
    active={r['document_id'] for r in documents.get('documents',[]) if r.get('status')=='ready' and r.get('active_version')==r.get('id') and not r.get('deleted')}
    a,b=st.columns(2)
    a.metric('Predefined documents',value['dataset']['documents'])
    b.metric('Uploaded documents',len(active))
    st.caption(f'{len(examples)} complete saved benign A/B/C comparisons are available.')
    st.caption('These are previously recorded Azure answers, not a new live response. Changing the example sends no model request.')
    if examples:
        chosen = st.selectbox('Choose a recorded question', [c['case_id'] for c in examples],
                              format_func=lambda cid: next(c['query'] for c in examples if c['case_id']==cid))
        case = next(c for c in examples if c['case_id']==chosen)
        st.markdown('**Question**')
        st.text(case['query'])
        for column, mode, name in zip(st.columns(3), 'ABC', ['Standard RAG','Instruction separation','Screening + output check']):
            result = case['modes'][mode]
            with column:
                with st.container(border=True):
                    st.markdown('**'+mode+' · '+name+'**')
                    st.text(result['answer'])
                    st.caption('Recorded status: '+result['state'])
                    if result.get('latency_s'):
                        st.caption('Response time: '+result['latency_s']+' s')
                    st.caption('Supporting source: '+', '.join(case['fixtures']))
        with st.expander('Supported task and source evidence'):
            st.text('Expected task: '+case['expected_task'])
            for quote in case.get('supporting_quotes',[]):st.text(quote)
            evidence = api('GET','/evaluation-current25/evidence/'+chosen)
            if evidence:
                for hit in answer_preview(evidence.get('hits',[])):
                    st.caption(hit.get('filename', 'Source'))
                    st.text(hit.get('text',''))
    else:
        st.info('No complete benign A/B/C examples have been recorded for this study.')
    from frontend.charts import coverage_chart, metric_chart
    with st.expander('Evaluation charts and full coverage'):
        st.image(coverage_chart(value['summary']))
        st.image(metric_chart(value['summary']))
        counts=value['counts']
        st.caption(f"Actual coverage: {counts['recorded']} of {counts['expected']} rows; {counts['errors']} operational errors; {counts['missing']} unrun. These saved examples are not a complete security evaluation.")
    with st.expander('Earlier attack example — historical 45-document study'):
        historical=api('GET','/evaluation-v3')
        if historical:
            previous=answer_preview(historical)
            attacks=[c for c in previous.get('case_comparisons',[]) if c['adversarial'] and
                     c['modes']['A'].get('attack_succeeded') is True]
            if attacks:
                case=attacks[0]
                st.caption('Earlier dataset and prompts. This example is not a result of the current 25-document study.')
                st.text('Recorded attack case: '+case['case_id'])
                for column,mode in zip(st.columns(3),'ABC'):
                    with column:
                        result=case['modes'][mode]
                        st.markdown('**Configuration '+mode+'**')
                        st.text(result.get('answer') or 'No answer recorded.')
                        st.caption('Recorded state: '+result['state'])
                        for label,key in [('Task passed','task_passed'),('Attack succeeded','attack_succeeded')]:
                            grade=result.get(key)
                            st.caption(label+': '+('Pending / not graded' if grade is None else 'Yes' if grade else 'No'))
            else:st.caption('No graded baseline attack-success example is available.')
