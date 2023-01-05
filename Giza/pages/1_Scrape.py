import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_handling import *
import json

def disable_buttons():
    st.session_state['scrape_button_state'] = True
    st.session_state['dl_button_state'] = True
    st.session_state['df_usend_uniq'] = pd.DataFrame()

st.set_page_config(layout="wide")

st.warning("Scraping is time intensive, if you're mostly interested in exploring the functionality, try a provided dataset.", icon="⚠️")
st.header('Select Route List Type')
list_type_options = ["Ticks", "ToDos"]
st.session_state.list_type = st.radio("List Type", 
                                    options=list_type_options,
                                    horizontal=True,
                                    on_change=disable_buttons,
                                    index=list_type_options.index(st.session_state.list_type),
                                    help="Ticks is a list of routes the user has climbed, ToDos is a list of routes the user would like to climb.")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.header('1. Download')
    st.write("Link to a user profile")
    upload_link = st.text_input("Climber Profile Link", 
                                value='https://www.mountainproject.com/user/14015/nick-wilder',
                                placeholder='https://www.mountainproject.com/user/14015/nick-wilder',
                                label_visibility='collapsed')
    if st.button(f"Download {st.session_state.list_type} Data"):
        st.session_state['scrape_button_state'] = True
        st.session_state['dl_button_state'] = True
        with st.spinner("Downloading"):
            if st.session_state.list_type == "Ticks":
                st.session_state.df_usend, error_message = download_routelist('tick', upload_link)
            if st.session_state.list_type == "ToDos":
                st.session_state.df_usend, error_message = download_routelist('todo', upload_link)
            if error_message:
                st.error(error_message)
            else:
                st.session_state.df_usend = data_standardize(st.session_state.df_usend)
                if st.session_state.list_type == "Ticks": # If ticks, special clean required
                    st.session_state.df_usend_uniq = user_uniq_clean(st.session_state.df_usend)
                if st.session_state.list_type == "ToDos": # If todos, relabel necessary
                    st.session_state.df_usend_uniq = st.session_state.df_usend.copy()
                st.session_state.df_usend_uniq = route_length_fixer(st.session_state.df_usend_uniq, 'express')
                st.session_state.scrape_button_state = False
                st.success("Download Successful", icon="✅")
with col2:
    st.header('2. Scrape')
    st.write("Download and extract route information")
    numrows = len(st.session_state.df_usend_uniq.index)
    if numrows:
        st.session_state.scrape_cutoff = st.slider("""Scrape The "N" Most Recent Routes""", min_value=0, max_value=numrows, value=numrows)
        st.markdown(f"Estimated Scrape Time: {(2+(st.session_state.scrape_cutoff/45)):.0f}min")
    if st.button(f"Scrape {st.session_state.list_type}", disabled=st.session_state.scrape_button_state): # TODO Rerunning scrapes to fill missing values works in jupyter but not streamlit. The column is being re-cast to string for some reason upon page rerun.
        st.session_state.dl_button_state = False
        st.session_state.df_usend_uniq.drop(st.session_state.df_usend_uniq.iloc[st.session_state.scrape_cutoff:].index, inplace=True)
        st.session_state.df_usend_uniq = routescrape_syncro(st.session_state.df_usend_uniq)
        if st.session_state.list_type == "Ticks": # if ticks, need to get default pitch numbers
            st.session_state.df_usend_uniq = extract_default_pitch(st.session_state.df_usend_uniq)
        st.session_state.df_usend_uniq = extract_tick_details(st.session_state.df_usend_uniq)
        st.session_state.df_usend_uniq = tick_analysis(st.session_state.df_usend_uniq)
        # This is the end of the line for our data extraction, creating a seperate session state df for each will allow a user to scrape both and use both in the same session.
        if st.session_state.list_type == "Ticks":
            st.session_state.df_usend_uniq_ticks = st.session_state.df_usend_uniq.copy()
            st.session_state.tick_upload_link_ref = upload_link.split('/')[5]
            st.session_state.upload_link_ref_str = st.session_state.tick_upload_link_ref
        if st.session_state.list_type == "ToDos":
            st.session_state.df_usend_uniq_todos = st.session_state.df_usend_uniq.copy()
            st.session_state.todo_upload_link_ref = upload_link.split('/')[5]
            st.session_state.upload_link_ref_str = st.session_state.todo_upload_link_ref
        with col3:
            failed_mainscrape = st.session_state.df_usend_uniq["Re Mainpage"].isna().sum()
            failed_statscrape = st.session_state.df_usend_uniq["Re Statpage"].isna().sum()
            failed_mainscrape_list = st.session_state.df_usend_uniq.loc[(st.session_state.df_usend_uniq['Re Mainpage'].isna())]['Route']
            failed_statscrape_list = st.session_state.df_usend_uniq.loc[(st.session_state.df_usend_uniq['Re Statpage'].isna())]['Route']
            scrape_failrate = (1-((failed_mainscrape+failed_statscrape)/(2*numrows)))*100
            if failed_mainscrape+failed_statscrape == 0:
                col2.success(f"Scrape 100% Successful | Continue To Analysis", icon="✅")
            else:
                st.session_state.scrape_button_state = True
                col2.warning(f"Scrape Completed With Missing Values ({scrape_failrate}% Success Rate | You May Continue To Analysis)", icon="⚠️")
                col1, col2 = st.columns([1,1])
                with col1:
                    st.warning(f"{failed_mainscrape} failed mainpage scrapes")
                    failed_mainscrape_list
                with col2:
                    st.warning(f"{failed_statscrape} failed statpage scrapes")
                    failed_statscrape_list
                st.info("To retry, redownload the data then scrape again.", icon="ℹ️")
st.markdown('---')
st.header('3. Export')
st.write("Save current route list for later or to use on your own")
if st.session_state.list_type == "Ticks":
    dl_val = st.session_state.df_usend_uniq_ticks
if st.session_state.list_type == "ToDos":
    dl_val = st.session_state.df_usend_uniq_todos
st.download_button(
    label=f"Download {st.session_state.list_type}.PKL File For Giza",
    data=pickle.dumps(dl_val),
    file_name=f'scraped_climbs_{st.session_state.list_type.lower()}_{st.session_state.upload_link_ref_str}.pkl',
    disabled=st.session_state.dl_button_state,
    help="PKL files are what Giza uses to build your analysis"
)  
st.download_button(
    label=f"Download {st.session_state.list_type}.CSV For Personal Use",
    data=dl_val.to_csv().encode('utf-8'),
    file_name=f'scraped_climbs_{st.session_state.list_type.lower()}_{st.session_state.upload_link_ref_str}.csv',
    mime='text/csv',
    disabled=st.session_state.dl_button_state,
    help="CSV files are nice if you want to poke around the data yourself in excel or another program"
)