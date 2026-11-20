"""Read sanitized saved upload checks locally, without provider requests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_validation():
    folder = ROOT / 'results/upload_validation_20261030'
    path = folder / 'validation.json'
    if not path.exists():
        return None
    return json.loads(path.read_text())


def render_validation(data):
    import streamlit as st
    from frontend.charts import uploaded_chart
    saved = load_validation()
    if not saved:
        return
    st.subheader('Uploaded-document validation')
    current={(d['document_id'],d['version_id']) for d in data['documents']}
    frozen={(d['document_id'],d['version_id']) for d in saved['documents']}
    if current != frozen:
        st.info('Saved validation covers an earlier uploaded-library snapshot. New or replaced files need their own checks.')
    st.caption(f"{len(frozen)} files · {saved['recorded_rows']} / {saved['planned_rows']} A/B/C rows recorded · {saved['unrun_rows']} unrun")
    image=uploaded_chart(saved['rows'])
    st.image(image)
    st.download_button('Download uploaded-validation PNG',image,file_name='uploaded_document_validation.png',mime='image/png')
    st.caption('Saved live checks across separate implementation revisions. Errors remain visible; response status does not establish answer correctness or attack resistance.')
    with st.expander('Validation checks by document and mode'):
        st.dataframe([{'File':r['filename'],'Test':r['kind'],'Mode':r['mode'],
                       'Status':r['status'],'Run':r['implementation_run'],
                       'Citation scope':r['citations_in_approved_scope'],
                       'Full-card disclosure detected':r['full_card_in_delivered_answer']}
                      for r in saved['rows']],hide_index=True)
        st.caption('No human quality ratings were invented. Raw answers and protected values are excluded from this validation summary.')
