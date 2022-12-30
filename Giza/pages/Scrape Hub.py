import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_handling import *

st.set_page_config(layout="wide")

#Initializations
if 'scrape_button_state' not in st.session_state:
    st.session_state['scrape_button_state'] = True
if 'dl_button_state' not in st.session_state:
    st.session_state['dl_button_state'] = True
if 'df_usend_uniq' not in st.session_state:
    st.session_state['df_usend_uniq'] = pd.DataFrame()

st.warning("Scraping is time intensive (~1s/route) and can take as long as 20min for a routelist of ~1000. If you're mostly interested in exploring the functionality, try exploring with a provided dataset.", icon="⚠️")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.header('1. Download')
    upload_link = st.text_input("Climber Profile Link", value='https://www.mountainproject.com/user/14015/nick-wilder', placeholder='https://www.mountainproject.com/user/14015/nick-wilder')
    if st.button("Download Data"):
        st.session_state['scrape_button_state'] = True
        st.session_state['dl_button_state'] = True
        with st.spinner("Downloading"):
            st.session_state.df_usend, error_message = download_routelist('tick', upload_link)
            if error_message:
                st.error(error_message)
            else:
                st.session_state.df_usend = data_standardize(st.session_state.df_usend)
                st.session_state.df_usend_uniq = user_uniq_clean(st.session_state.df_usend)
                st.session_state.df_usend_uniq = route_length_fixer(st.session_state.df_usend_uniq, 'express')
                st.session_state.scrape_button_state = False
                st.success("Download Successful", icon="✅")
with col2:
    st.header('2. Scrape')
    numrows = len(st.session_state.df_usend_uniq.index)
    if numrows:
        st.session_state.cutoff = st.slider("""Scrape The "N" Most Recent Unique Routes""", min_value=0, max_value=numrows, value=numrows)
    if st.button("Scrape", disabled=st.session_state.scrape_button_state): # TODO Rerunning scrapes to fill missing values works in jupyter but not streamlit. The column is being re-cast to string for some reason upon page rerun.
        st.session_state.dl_button_state = False
        st.session_state.df_usend_uniq.drop(st.session_state.df_usend_uniq.iloc[st.session_state.cutoff:].index, inplace=True)
        st.session_state.df_usend_uniq = routescrape_syncro(st.session_state.df_usend_uniq)
        st.session_state.df_usend_uniq = extract_default_pitch(st.session_state.df_usend_uniq)
        st.session_state.df_usend_uniq = extract_tick_details(st.session_state.df_usend_uniq)
        st.session_state.df_usend_uniq = tick_analysis(st.session_state.df_usend_uniq)
        with col3:
            failed_mainscrape = st.session_state.df_usend_uniq["Re Mainpage"].isna().sum()
            failed_statscrape = st.session_state.df_usend_uniq["Re Statpage"].isna().sum()
            failed_mainscrape_list = st.session_state.df_usend_uniq.loc[(st.session_state.df_usend_uniq['Re Mainpage'].isna())]['Route']
            failed_statscrape_list = st.session_state.df_usend_uniq.loc[(st.session_state.df_usend_uniq['Re Statpage'].isna())]['Route']
            scrape_failrate = (1-((failed_mainscrape+failed_statscrape)/(2*numrows)))*100
            if failed_mainscrape+failed_statscrape == 0:
                col2.success("Scrape 100% Successful", icon="✅")
            else:
                st.session_state.scrape_button_state = True
                col2.warning(f"Scrape Completed With Missing Values ({scrape_failrate}% Success Rate)", icon="⚠️")
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
st.download_button(
    label="Download .PKL File For Giza",
    data=pickle.dumps(st.session_state.df_usend_uniq),
    file_name='scraped_climbs.pkl',
    disabled=st.session_state.dl_button_state,
    help="PKL files are used for further analysis within Giza"
)  
st.download_button(
    label="Download .CSV For Personal Use",
    data=st.session_state.df_usend_uniq.to_csv().encode('utf-8'),
    file_name='scraped_climbs.csv',
    mime='text/csv',
    disabled=st.session_state.dl_button_state,
    help="CSV files are nice if you want to poke around the data yourself in excel or another program"
)