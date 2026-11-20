"""Microsoft login gate; tokens are used only for server-side API requests."""
import importlib.util
import os
import streamlit as st


def sign_in_gate():
    if os.environ.get('LOCAL_ACCESS_TOKEN'):
        return
    try:
        configured = bool(st.secrets.get('auth', {}).get('client_id'))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        configured = False
    if not configured:
        st.info('Microsoft sign-in needs local configuration before this workspace can open.')
        st.caption('Follow docs/AUTHENTICATION.md and copy .streamlit/secrets.toml.example to .streamlit/secrets.toml. Keep secrets local.')
        st.stop()
    if importlib.util.find_spec('authlib') is None:
        st.error('Install the authentication dependencies listed in backend/requirements.txt before signing in.')
        st.stop()
    if not st.user.is_logged_in:
        st.info('Sign in with your organization’s Microsoft account to open the shared document library.')
        if st.button('Sign in with Microsoft', type='primary'):
            st.login()
        st.stop()
    if not st.user.tokens.get('access'):
        st.error('No API access token is available. Check the API scope and expose_tokens setting, then sign out and sign in again.')
        if st.button('Sign out'):
            st.session_state.clear()
            st.logout()
        st.stop()
    if st.sidebar.button('Sign out'):
        st.session_state.clear()
        st.logout()


def auth_headers():
    local_token = os.environ.get('LOCAL_ACCESS_TOKEN')
    if local_token:
        return {'Authorization': 'Bearer ' + local_token}
    token = st.user.tokens.get('access') if st.user.is_logged_in else None
    return {'Authorization': 'Bearer ' + token} if token else {}


def load_identity(api):
    return api('GET', '/auth/me')


def bind_identity(identity):
    subject = identity['subject']
    previous = st.session_state.get('_authenticated_subject')
    if previous != subject:
        # A different account must never inherit answers/downloads from the old UI.
        st.session_state.clear()
        st.session_state['_authenticated_subject'] = subject
    st.sidebar.caption(('Local access' if os.environ.get('LOCAL_ACCESS_TOKEN') else 'Signed in') + ' · ' + ', '.join(identity['roles']))
    return frozenset(identity['permissions'])
