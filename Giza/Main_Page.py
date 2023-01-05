import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_handling import *
import json
import os

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1643667996984-fcc69743449d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1548&q=80");
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
"""

st.set_page_config(layout="centered", page_title="Main Page")
st.markdown(page_bg_img, unsafe_allow_html=True)

if 'scrape_button_state' not in st.session_state:
    st.session_state.scrape_button_state = True
if 'dl_button_state' not in st.session_state:
    st.session_state.dl_button_state = True
if 'df_usend_uniq' not in st.session_state:
    st.session_state.df_usend_uniq = pd.DataFrame()
if 'df_usend_uniq_ticks' not in st.session_state:
    st.session_state.df_usend_uniq_ticks = pd.DataFrame()
if 'df_usend_uniq_todos' not in st.session_state:
    st.session_state.df_usend_uniq_todos = pd.DataFrame()
if 'list_type' not in st.session_state:
    st.session_state.list_type = "Ticks"
if 'df_ticks_fil' not in st.session_state:
    st.session_state.df_ticks_fil = pd.DataFrame()
if 'tick_upload_link_ref' not in st.session_state:
    st.session_state.tick_upload_link_ref = ''
if 'todo_upload_link_ref' not in st.session_state:
    st.session_state.todo_upload_link_ref = ''

st.title("Giza")
st.header("Extended Rock Climbing Analytics")