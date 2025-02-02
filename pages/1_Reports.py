import streamlit as st
import pandas as pd

st.set_page_config(page_title='Reports', page_icon='📄', layout="centered", initial_sidebar_state="auto", menu_items=None)

if 'valid_session' not in st.session_state: st.session_state['valid_session'] = False

display = st.empty()
if not st.session_state['valid_session']:
    with display.container():
        st.caption('ROYAL DESTINATIONS')
        st.info('Please login to view this page.')
        st.header('Comp Listings Portal')

        username = st.text_input('Username')
        password = st.text_input('Password')

        if st.button('LOGIN', use_container_width=True, type='primary'):
            if [username, password] in st.secrets['users']:
                st.session_state['valid_session'] = True
            else:
                st.warning('Please enter a valid username and password.')

if st.session_state['valid_session']:
    display.empty()