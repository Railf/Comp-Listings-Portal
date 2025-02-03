import streamlit as st
import pandas as pd

from pymongo import MongoClient

st.set_page_config(page_title='Reports', page_icon='📄', layout="wide", initial_sidebar_state="auto", menu_items=None)

if 'valid_session' not in st.session_state: st.session_state['valid_session'] = False

display = st.empty()
if not st.session_state['valid_session']:
    with display.container():
        st.caption('ROYAL DESTINATIONS')
        st.header('Comp Listings Portal')
        st.info('Please login to view this page.')
        with st.form('login'):
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')

            if st.form_submit_button('LOGIN', use_container_width=True, type='primary'):
                if [username, password] in st.secrets['users']:
                    st.session_state['valid_session'] = True
                else:
                    st.warning('Please enter a valid username and password.')

if st.session_state['valid_session']:
    display.empty()

    with st.sidebar:
        st.caption('ROYAL DESTINATIONS')

    client   = MongoClient(st.secrets['database']['url'])
    database = client[st.secrets['database']['name']]
    
    l, m, r = st.columns(3)

    report = l.selectbox(label='Choose your report:', options=['Detail','❗️ Comp Review','🏘️ Comp Summary','🏠 Unit Summary'])
    start_date = m.date_input('Start')
    end_date   = r.date_input('End', min_value=start_date)
    date_range = pd.date_range(start=start_date, end=end_date)
    

    if report == 'Detail':
        st.info('This is the raw data that is populated with the comp listings script.')

    if report == '❗️ Comp Review':
        st.info('This is a list of comps that have returned zeros or undefined on specific comp weeks.')
        
    if report == '🏘️ Comp Summary':
        st.info('This is the per-comp, aggregate average of each non-zero-or-undefined value.')
    
    if report == '🏠 Unit Summary':
        st.info('This is the per-unit, aggregate average of each non-zero-or-undefined comps.')


    if st.button('Pull Report', use_container_width=True, type='primary'):

        if report:
            df         = pd.DataFrame(list(database['test'].find({}, {"_id": 0})))
            df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
            df         = df[df.Date.isin(date_range)]
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            st.dataframe(data=df, hide_index=True, use_container_width=True)
    

    st.caption('... more in development and coming soon!')