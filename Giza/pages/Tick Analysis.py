import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_handling import *

st.set_page_config(layout="wide")

st.title("Tick Analysis")
st.subheader("Explore Your Ticks and Discover Notable Sends")
st.markdown('---')

col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.header('Download')
    upload_link = st.text_input("Climber Profile Link", value='https://www.mountainproject.com/user/200180658/brayden-l', placeholder='https://www.mountainproject.com/user/200180658/brayden-l')
    if st.button("Download Data"):
        with st.spinner("Downloading"):
            st.session_state.df_usend, error_message = download_routelist('tick', upload_link)
            if error_message:
                st.error(error_message)
            else:
                st.success("Download Successful", icon="✅")
with col2:
    st.header('Scrape')
    if st.button("Scrape"):
        with st.spinner("Scraping"):
            st.session_state.df_usend = data_standardize(st.session_state.df_usend)
            st.session_state.df_usend_uniq = st.session_state.df_usend.drop_duplicates(subset="Route ID")
            st.session_state.df_usend_uniq = user_uniq_clean(st.session_state.df_usend_uniq)
            # st.session_state.df_usend_uniq = routescrape_asyncro(st.session_state.df_usend_uniq)
            # st.session_state.df_usend_uniq = extract_default_pitch(st.session_state.df_usend_uniq)
            # st.session_state.df_usend_uniq = extract_tick_details(st.session_state.df_usend_uniq)
            # st.session_state.df_usend_uniq = tick_analysis(st.session_state.df_usend_uniq)
        st.session_state.df_usend_uniq

with col3:
    st.subheader("Select Grade Homegenization Type")
    col1, col2 = st.columns([1,1])
    with col1:
        route_grade_type = st.radio("Routes", options=['Letter (5.10a)', 'Sign (5.10-)'])
    with col2:
        boulder_grade_type = st.radio("Boulders", options=['Flat (V4)', 'Sign (V4-)'])