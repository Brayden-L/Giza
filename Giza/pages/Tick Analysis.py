import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_handling import *

st.set_page_config(layout="wide")

st.title("Tick Analysis")
st.subheader("Explore Your Ticks and Discover Notable Sends")
st.markdown('---')
with st.expander('How It Works'):
    st.markdown("Placeholder")
    



col1, col2, col3 = st.columns([1,1,1])
data_source_type = col1.radio("Data Source Selection", ['Select Provided Dataset', 'Upload Pickle File'], help="placeholder ")
if data_source_type == "Select Provided Dataset":
    col1.selectbox("Profiles", ["1","2","3"])
if data_source_type == "Upload Pickle File":
    col1.file_uploader("Upload Pickle")
with col3:
    st.subheader("Select Grade Homegenization Type")
    grade_settings = ['letter', 'even_rand', 'flat', 'even_rand']
    route_round_type = 'Round Evenly By Random'
    col1, col2 = st.columns([1,1])
    with col1:
        route_grade_type = st.radio("Routes", options=['Sign (5.10-)', 'Letter (5.10a)'])
        if route_grade_type == 'Letter (5.10a)':
            route_round_type = st.radio("Route Round Type", options=['Round Evenly By Random', 'Round Up', 'Round Down'], help='placeholder')
    with col2:
        boulder_grade_type = st.radio("Boulders", options=['Sign (V4-)', 'Flat (V4)'])
        boulder_round_type = st.radio("Boulder Round Type", options=['Round Evenly By Random', 'Round Up', 'Round Down'], help='placeholder')
    gh_key = {'Sign (5.10-)': 'sign', 'Letter (5.10a)': 'letter', 'Sign (V4-)': 'sign', 'Flat (V4)': 'flat', 'Round Evenly By Random': 'even_rand', 'Round Down': 'down', 'Round Up': 'up' }
    grade_settings = [gh_key[route_grade_type], gh_key[route_round_type], gh_key[boulder_grade_type], gh_key[boulder_round_type]]
    st.session_state.df_usend_uniq = grade_homo(st.session_state.df_usend_uniq, *grade_settings)



st.markdown('---')
# gb = GridOptionsBuilder.from_dataframe(st.session_state.df_usend_uniq)
# gb.configure_pagination(paginationAutoPageSize=True)
# AgGrid(data=st.session_state.df_usend_uniq, gridOptions=gb.build(), columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
