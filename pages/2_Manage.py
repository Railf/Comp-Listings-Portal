import streamlit as st
import pandas as pd

from pymongo import MongoClient

def display_setting_widget(database, collection_name, filter_by_column, status_icon):
    st.subheader(f'{status_icon} {collection_name.title()}')

    df = pd.DataFrame(list(database[collection_name].find({}, {"_id": 0})))
    df = df.sort_values(by=filter_by_column).reset_index(drop=True)
    modified_df = st.data_editor(data=df, use_container_width=True, num_rows='dynamic', key=f'{collection_name}_data_editor')

    l, r = st.columns(2)

    l.download_button(label='DOWNLOAD', data=df.to_csv(index=False), file_name=f'{collection_name}.csv', use_container_width=True, key=f'{collection_name}_download_button')
    
    if r.button(label='UPDATE', type='primary', use_container_width=True, key=f'{collection_name}_update_button'):
        database[collection_name].delete_many({})
        database[collection_name].insert_many(modified_df.to_dict(orient='records'))
        st.toast(f'**{collection_name.title()}** have been updated!', icon=status_icon)





st.set_page_config(page_title='Manage', page_icon='⚙️', layout="centered", initial_sidebar_state="auto", menu_items=None)

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

    with st.sidebar:
        st.caption('ROYAL DESTINATIONS')

    st.info('Manage the settings for comp listings and dates.')

    client   = MongoClient(st.secrets['database']['url'])
    database = client[st.secrets['database']['name']]

    display_setting_widget(database=database, collection_name='comps', filter_by_column='unit_code', status_icon='🏘️')
    display_setting_widget(database=database, collection_name='dates', filter_by_column='Start',     status_icon='🗓️')
