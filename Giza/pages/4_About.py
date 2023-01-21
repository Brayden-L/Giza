import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from long_strs import blue_gradient_bg_img, about_explainer

st.set_page_config(layout="wide")
st.markdown(blue_gradient_bg_img, unsafe_allow_html=True)

st.header('About')
st.markdown(about_explainer, unsafe_allow_html=True)