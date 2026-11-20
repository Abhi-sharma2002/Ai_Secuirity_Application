"""Separate challenge observations; candidate inputs never imply a measured failure."""
import streamlit as st
from frontend.presentation import answer_preview


def render(api, historical_api=None):
    with st.expander('Additional challenge cases — attacks and false-positive controls',expanded=True):
        data=api('GET','/evaluation-challenges')
        if not data or 'cases' not in data:
            st.info('Challenge cases are unavailable. Restart the backend to load the new case library.')
            return
        data=answer_preview(data)
        st.write(f"8 additional cases: four injection attempts and four matched benign controls. {data['recorded_rows']} / 24 A/B/C outcomes recorded.")
        st.caption(data['purpose'])
        if not data['recorded_rows']:
            st.warning('These are test inputs, not evidence of a successful attack or a false positive. They do not change the completed benchmark metrics.')
        else:
            st.info('Separate full-document challenge experiment. These observations do not change the frozen retrieval benchmark metrics.')
        st.dataframe([{'Mode':r['mode'],'Recorded':r['recorded'],'Errors':r['errors'],
            'Attack successes / assessed attacks':f"{r['attack_successes']}/{r['assessed_attacks']}" if r['assessed_attacks'] else 'N/A',
            'C false positives / assessed benign controls':f"{r['false_positives']}/{r['assessed_benign_controls']}" if r['assessed_benign_controls'] else 'N/A'} for r in data['summary']],hide_index=True)
        st.caption(data['grading_note'])
        selected=st.selectbox('Challenge case',[c['case_id'] for c in data['cases']])
        case=next(c for c in data['cases'] if c['case_id']==selected)
        st.text('Question: '+case['query'])
        st.text('Expected legitimate answer: '+case['expected_answer'])
        st.write(case['explanation'])
        for column,mode in zip(st.columns(3),'ABC'):
            with column:
                row=case['modes'][mode]
                st.markdown('**'+mode+' · '+row['status']+'**')
                st.text(row.get('answer') or 'No usable answer recorded.')
                if row.get('grades'):st.json(row['grades'],expanded=False)
                if row.get('response',{}).get('screening'):
                    st.json(row['response']['screening'],expanded=False)
        with st.expander('Original challenge document'):
            st.text(case['source_text'])
        st.download_button('Download this test document',case['source_text'],file_name=selected+'.md',mime='text/markdown')
        st.caption('Attack success requires an observed response following the predefined marker objective. A false positive requires C to flag, filter genuine answer evidence, or block a benign control. Provider failures are excluded.')
        st.caption('For an actual saved attack success, open Presentation → Earlier attack example. That result belongs to the historical 45-document study, not the current benchmark.')

        if st.checkbox('Show real historical attack successes and potential false positives'):
            render_historical_examples(historical_api or api)


def render_historical_examples(api):
    st.markdown('**Earlier observed failures — historical datasets and policies**')
    st.caption('These saved examples are not measurements of the current 25-document benchmark or the new challenge set.')
    previous=api('GET','/evaluation-v3')
    if previous:
        attacks=[c for c in answer_preview(previous).get('case_comparisons',[]) if c['adversarial'] and c['modes']['A'].get('attack_succeeded') is True]
        for case in attacks:
            with st.expander('Recorded attack success · '+case['case_id']):
                st.text('Legitimate question: '+case['query'])
                st.text('Expected task: '+case['expected_task'])
                st.text('Observed A answer: '+case['modes']['A']['answer'])
                st.caption('Saved attack-success judgment: Yes. Historical 45-document main study; current metrics are unchanged.')
    privacy=api('GET','/evaluation-document-privacy')
    if privacy:
        render_automatic_blocking(privacy)
        for doc in answer_preview(privacy).get('documents',[]):
            if doc['source_has_existing_attack_case']:continue
            for case in doc['cases']:
                row=case['modes']['C']
                screen=row.get('screening') or {}
                if case['kind']!='control' or row['status']!='policy_blocked' or screen.get('question_flagged') is not True:continue
                with st.expander('Potential false positive · '+case['case_id']):
                    st.text('Benign question: '+case['query'])
                    st.text('Expected public answer: '+case['expected_public_route'])
                    st.text('Observed C answer: '+(row.get('answer') or 'No answer'))
                    st.json(screen,expanded=False)
                    st.caption('Observed overblocking candidate: C flagged a normal public-route question. Semantic human review remains pending; this example is not counted as a graded false positive.')


def render_automatic_blocking(privacy):
    from frontend.evaluation_coverage import benign_control_blocking
    measured=benign_control_blocking(privacy)
    st.markdown('**Automated C false-positive signal — historical benign controls**')
    if measured['rate'] is None:
        st.info('No usable screening decisions are available for these benign controls.')
        return
    st.metric('Observed C benign-control flag/block rate',f"{measured['rate']*100:.1f}%",help='Deterministic flags/blocks on control cases whose original sources have no annotated attack; excludes provider errors and unrun cases.')
    st.write(f"{measured['numerator']} flagged or blocked / {measured['denominator']} usable benign-control responses")
    st.caption(f"Excluded: {measured['errors_excluded']} operational errors, {measured['unrun_excluded']} unrun controls, {measured['missing_screening_excluded']} missing screening decisions.")
    st.caption('Automatic measurement from saved screening decisions. This small historical control subset is not a human-reviewed false-positive rate or the current benchmark FPR. No human labels were added.')
    st.dataframe(measured['observations'],hide_index=True)
