"""TECM application entry point. Run with: python -m streamlit run app.py"""
import time
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from config.settings import SESSION_IDLE_SECONDS,SESSION_MAX_SECONDS
from modules.authentication.service import authenticate,profile,permissions,AccessDenied
from dashboard.pages import render

st.set_page_config(page_title='TECM | Condition monitoring',page_icon='⚡',layout='wide')
st.markdown('''<style>
.stApp { background: #f5f7fb; }
[data-testid="stSidebar"] { background: #102b46; }
[data-testid="stSidebar"] * { color: #eef5ff; }
[data-testid="stMetric"] { background: white; border: 1px solid #e1e7ef; padding: 16px; border-radius: 12px; }
h1,h2,h3 { color: #163b5b; }
</style>''',unsafe_allow_html=True)
now=time.time()
if 'principal' in st.session_state:
    if now-st.session_state.get('last_activity',0)>SESSION_IDLE_SECONDS or now-st.session_state.get('signed_in',0)>SESSION_MAX_SECONDS:
        st.session_state.clear();st.info('Session expired. Please sign in again.')
if 'principal' not in st.session_state:
    st.title('TECM')
    st.subheader('Transformer and Equipment Condition Monitoring')
    st.caption('Private engineering workspace • Sign in to your organisation')
    with st.form('login',clear_on_submit=True):
        email=st.text_input('Email')
        password=st.text_input('Password',type='password')
        submit=st.form_submit_button('Sign in',type='primary')
    if submit:
        try:
            st.session_state.principal=authenticate(email,password)
            st.session_state.signed_in=now;st.session_state.last_activity=now
            st.rerun()
        except AccessDenied as exc:st.error(str(exc))
        except SQLAlchemyError:st.error('Database unavailable. Run python -m scripts.manage init, or contact the administrator.')
    st.caption('Accounts are provisioned by an administrator. No public self-registration.')
    st.stop()
try:
    principal=st.session_state.principal
    user=profile(principal);grants=permissions(principal)
except (AccessDenied,SQLAlchemyError):
    st.session_state.clear();st.error('Your session is unavailable. Reload and sign in again.');st.stop()
st.session_state.last_activity=now
with st.sidebar:
    st.title('⚡ TECM')
    st.caption(user['organisation'])
    st.write(user['name'])
    st.caption(user['role'].replace('_',' ').title())
    if st.button('Sign out'):
        st.session_state.clear();st.rerun()
try:
    render(principal,user,grants)
except AccessDenied as exc:st.error(str(exc))
except ValueError as exc:st.error(str(exc))
except SQLAlchemyError:
    st.error('The change could not be saved. Check duplicate codes or references, then retry. No partial transaction was committed.')
