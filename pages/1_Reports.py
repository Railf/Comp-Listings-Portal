import streamlit as st
import pandas as pd
import numpy as np

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

    reports = [
        'Detail',
        '❗️ Comp Review',
        '🏘️ Comp Summary',
        '🏠 Unit Summary',
        '💲 Comp Booking Summary',
        '🕵️ Unit Comp Query',
        ]

    report = l.selectbox(label='Choose your report:', options=reports)
    

    match report:
        case 'Detail':
            st.info('This is the raw data that is populated with the comp listings script.')
            start_date = m.date_input('Start')
            end_date   = r.date_input('End', min_value=start_date)
            date_range = pd.date_range(start=start_date, end=end_date)
            date_range = date_range.strftime('%Y-%m-%d').to_list()

        case '❗️ Comp Review':
            st.info('This is a list of comps that have returned zeros or undefined on specific comp weeks.')
            start_date = m.date_input('Start')
            end_date   = r.date_input('End', min_value=start_date)
            date_range = pd.date_range(start=start_date, end=end_date)
            date_range = date_range.strftime('%Y-%m-%d').to_list()
        
        case '🏘️ Comp Summary':
            st.info('This is the per-comp, aggregate average of each non-zero-or-undefined value.')
            start_date = m.date_input('Start')
            end_date   = r.date_input('End', min_value=start_date)
            date_range = pd.date_range(start=start_date, end=end_date)
            date_range = date_range.strftime('%Y-%m-%d').to_list()
    
        case '🏠 Unit Summary':
            st.info('This is the per-unit, aggregate average of each non-zero-or-undefined comps.')
            start_date = m.date_input('Start')
            end_date   = r.date_input('End', min_value=start_date)
            date_range = pd.date_range(start=start_date, end=end_date)
            date_range = date_range.strftime('%Y-%m-%d').to_list()
        
        case '💲 Comp Booking Summary':
            st.info('This is the comparison of a date to the date prior, highlightling proposed bookings and associated rates.')
            start_date = m.date_input('Date', max_value=pd.to_datetime('today').date())
        
        case '🕵️ Unit Comp Query':
            st.info('Coming soon!')
            # st.info("This is the reflection of a unit\'s comps for a specific week.")
            # cdf  = pd.DataFrame(list(database['comps'].find({}, {"_id": 0})))
            # ddf  = pd.DataFrame(list(database['dates'].find({}, {"_id": 0})))
            # ddf['Start'] = pd.to_datetime(ddf['Start']).dt.date.astype(str)
            # ddf['End']   = pd.to_datetime(ddf['End']).dt.date.astype(str)
            # ddf['Week'] = ddf['Start'] + ' - ' + ddf['End']
            # cdf  = cdf.sort_values(by='unit_code').reset_index(drop=True)
            # cdf  = cdf['unit_code'].drop_duplicates().to_list()
            # ddf  = ddf.sort_values(by='Start').reset_index(drop=True)
            # ddf  = ddf['Week'].to_list()
            # unit = m.selectbox(label='Unit', options=cdf)
            # week = r.selectbox(label='Week', options=ddf)

        case _:
            st.info('Coming soon!')


    if st.button('Pull Report', use_container_width=True, type='primary'):

        match report:
            case 'Detail':
                df         = pd.DataFrame(list(database['detail'].find({"Date": {"$in": date_range}}, {"_id": 0})))
                df['Date'] = pd.to_datetime(df['Date'], format='mixed').dt.normalize()
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                st.dataframe(data=df, hide_index=True, use_container_width=True)


            case '❗️ Comp Review':
                df         = pd.DataFrame(list(database['detail'].find({"Date": {"$in": date_range}}, {"_id": 0})))
                df['Date'] = pd.to_datetime(df['Date'], format='mixed').dt.normalize()
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df         = df.groupby(['Date','Season','Unit','Comp'])[['Total_Rate','Service_Fee','Cost_to_Guest']].agg(np.average)
                df         = df[df.Cost_to_Guest == 0].reset_index()
                df         = df[['Season','Unit','Comp']]
                df         = df.drop_duplicates()
                st.dataframe(data=df, hide_index=True, use_container_width=True)

            case '🏘️ Comp Summary':
                df         = pd.DataFrame(list(database['detail'].find({"Date": {"$in": date_range}}, {"_id": 0})))
                df['Date'] = pd.to_datetime(df['Date'], format='mixed').dt.normalize()
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df         = df[df.Cost_to_Guest != 0]
                df         = df.groupby(['Date','Season','Unit','Comp'])[['Total_Rate','Service_Fee','Cost_to_Guest']].agg(
                    Total_Rate = ('Total_Rate', np.average),
                    Service_Fee = ('Service_Fee', np.average),
                    Cost_to_Guest = ('Cost_to_Guest', np.average),
                    Count = ('Total_Rate','size')
                )
                st.dataframe(data=df, use_container_width=True)


            case '🏠 Unit Summary':
                df         = pd.DataFrame(list(database['detail'].find({"Date": {"$in": date_range}}, {"_id": 0})))
                df['Date'] = pd.to_datetime(df['Date'], format='mixed').dt.normalize()
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df         = df[df.Cost_to_Guest != 0]
                df         = df.groupby(['Date','Season','Unit','Comp'])[['Total_Rate','Service_Fee','Cost_to_Guest']].agg(
                    Total_Rate = ('Total_Rate', np.average),
                    Service_Fee = ('Service_Fee', np.average),
                    Cost_to_Guest = ('Cost_to_Guest', np.average),
                    Count = ('Total_Rate','size')
                )
                df        = df.groupby(['Date','Season','Unit'])[['Total_Rate','Service_Fee','Cost_to_Guest']].agg(
                    Total_Rate = ('Total_Rate', np.average),
                    Service_Fee = ('Service_Fee', np.average),
                    Cost_to_Guest = ('Cost_to_Guest', np.average),
                    Count = ('Total_Rate','size')
                )
                st.dataframe(data=df, use_container_width=True)
            

            case '💲 Comp Booking Summary':
                prior_date   = start_date - pd.Timedelta(days=1)

                sdf          = pd.DataFrame(list(database['detail'].find({"Date": start_date.strftime('%Y-%m-%d')}, {"_id": 0})))
                pdf          = pd.DataFrame(list(database['detail'].find({"Date": prior_date.strftime('%Y-%m-%d')}, {"_id": 0})))
                sdf          = sdf[sdf.Cost_to_Guest == 0]
                pdf          = pdf[pdf.Cost_to_Guest != 0]

                df           = pd.merge(sdf, pdf, on=['Unit','Comp','Dates'], how='left', suffixes=('_s','_p'))
                df           = df[df.Cost_to_Guest_p.notnull()]
                df           = df[['Unit','Comp','Dates','Cost_to_Guest_p']]
                df['Nights'] = df['Dates'].str.split(' - ').apply(lambda x: (pd.to_datetime(x[1]) - pd.to_datetime(x[0])).days)
                df           = df.sort_values(by=['Unit','Comp','Dates']).reset_index(drop=True)
                df           = df.rename(columns={'Cost_to_Guest_p': 'Cost_to_Guest'})
                df           = df[['Unit','Comp','Dates','Nights','Cost_to_Guest']]
                st.dataframe(data=df, use_container_width=True, hide_index=True)
            

            case '🕵️ Unit Comp Query':
                '**Coming soon!**'
                # df = pd.DataFrame(list(database['detail'].find({"Unit": unit, "Dates": week}, {"_id": 0})))
                # st.dataframe(data=df, use_container_width=True, hide_index=True)

            case _:
                '**Coming soon!**'
    

    st.caption('... more in development and coming soon!')