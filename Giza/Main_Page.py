import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_handling import *
from long_strs import pyr_bg_img

st.set_page_config(layout="centered", page_title="Main Page")
st.markdown(pyr_bg_img, unsafe_allow_html=True)

def session_state_init():
    if 'scrape_button_state' not in st.session_state:
        st.session_state.scrape_button_state = True
    if 'exp_button_state' not in st.session_state:
        st.session_state.exp_button_state = True
    if 'df_usend' not in st.session_state:
        st.session_state.df_usend = pd.DataFrame()
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
    if 'upload_link_ref_str' not in st.session_state:
        st.session_state.upload_link_ref_str = ''
    if 'df_import' not in st.session_state:
        st.session_state.df_import = pd.DataFrame()
    
session_state_init()

st.title("Giza")
st.header("Extended Rock Climbing Analytics")
st.subheader("Build your tick pyramid and discover notable sends")