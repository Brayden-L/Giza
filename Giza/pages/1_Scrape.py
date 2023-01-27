import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import streamlit_nested_layout
from unique_route_functions import *
from st_blend_functions import uniqclean_ticktodo, scrape_ticktodo
from long_strs import scrape_explainer
from Main_Page import session_state_init
from datetime import date
import pickle

### Setup
session_state_init()


def disable_buttons():
    st.session_state.scrape_button_state = True
    st.session_state.exp_button_state = True
    st.session_state.df_usend_uniq = pd.DataFrame()


st.warning(
    "Scraping stat pages is disallowed, no additional metrics will be created.",
    icon="⚠️",
)
with st.expander("✋ Help ✋"):
    st.markdown(scrape_explainer, unsafe_allow_html=True)

### Download
st.header("1. Select Route List Type")
list_type_options = ["Ticks", "ToDos"]
st.session_state.list_type = st.radio(
    "List Type",
    options=list_type_options,
    horizontal=True,
    on_change=disable_buttons,
    index=list_type_options.index(st.session_state.list_type),
    help="Ticks is a list of routes the user has climbed, ToDos is a list of routes the user would like to climb.",
)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.header("2. Download")
    st.write("Link to a user profile")
    upload_link = st.text_input(
        "Climber Profile Link",
        value="https://www.mountainproject.com/user/200554494/amity-warme",
        placeholder="https://www.mountainproject.com/user/...",
        label_visibility="collapsed",
        on_change=disable_buttons,
    )
    if st.button(f"Download {st.session_state.list_type} Data", disabled=False):
        st.session_state.scrape_button_state = True
        st.session_state.exp_button_state = True
        with st.spinner("Downloading"):
            if st.session_state.list_type == "Ticks":
                st.session_state.df_usend, error_message = download_routelist(
                    "tick", upload_link
                )  # func
            if st.session_state.list_type == "ToDos":
                st.session_state.df_usend, error_message = download_routelist(
                    "todo", upload_link
                )  # func
            if error_message:
                st.error(error_message)
            else:
                st.session_state.df_usend = data_standardize(st.session_state.df_usend)
                st.session_state.df_usend_uniq = uniqclean_ticktodo(
                    df=st.session_state.df_usend, type=st.session_state.list_type
                )  # func
                st.session_state.scrape_button_state = False
                st.success("Download Successful", icon="✅")

### Scrape
with col2:
    st.header("3. Scrape")
    st.write("Download and extract route information")
    numrows = len(st.session_state.df_usend_uniq.index)
    if numrows:
        st.session_state.scrape_cutoff = st.slider(
            """Scrape The "N" Most Recent Routes""",
            min_value=0,
            max_value=numrows,
            value=numrows,
        )
        st.markdown(
            f"Estimated Scrape Time: {(2+(st.session_state.scrape_cutoff/45)):.0f}min"
        )
    if st.button(
        f"Scrape {st.session_state.list_type}",
        disabled=st.session_state.scrape_button_state,
    ):
        st.session_state.exp_button_state = False
        st.session_state.df_usend_uniq.drop(
            st.session_state.df_usend_uniq.iloc[st.session_state.scrape_cutoff :].index,
            inplace=True,
        )  # Apply filtering
        st.session_state.df_usend = st.session_state.df_usend[
            st.session_state.df_usend["Route"].isin(
                st.session_state.df_usend_uniq["Route"]
            )
        ]  # This applies the filter to df_usend too so it matches the filtering done to the unique list
        st.session_state.df_usend_uniq, scrape_stats = scrape_ticktodo(
            st.session_state.df_usend_uniq, type=st.session_state.list_type, strip=True
        )  # func
        with col3:
            if scrape_stats["nfail_mainscr"] + scrape_stats["nfail_statscr"] == 0:
                col2.success(f"Scrape 100% Successful | Continue To Analysis", icon="✅")
            else:
                st.session_state.scrape_button_state = True
                col2.warning(
                    f"Scrape Completed With Missing Values ({scrape_stats['scrape_failrate']:.2f}% Success Rate | You May Continue To Analysis)",
                    icon="⚠️",
                )
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.warning(
                        f"{scrape_stats['nfail_mainscr']} failed mainpage scrapes"
                    )
                    scrape_stats["failed_mainscrape_list"]
                with col2:
                    st.warning(
                        f"{scrape_stats['nfail_statscr']} failed statpage scrapes"
                    )
                    scrape_stats["failed_statscrape_list"]
                st.info("To retry, redownload the data then scrape again.", icon="ℹ️")

### Session state handling
# This is the end of the line for our data extraction, creating a seperate session state df for each will allow a user to scrape both and use both in the same session. We must package it for session state and file export.
# Variables are sent in many different directions, as this section has to handle two different types of dataframe to handle, and send it to both the session.state and package it up for download.
st.session_state.upload_link_ref_str = "/".join(
    upload_link.split("/")[4:6]
)  # This extracts the user ID and user name from the URL
scrape_details = {
    "route_list_type": st.session_state.list_type.lower(),
    "username": st.session_state.upload_link_ref_str,
    "date_scraped": date.today(),
}  # This is the full "package", it provides the dataframes as well as some meta data.
if st.session_state.list_type == "Ticks":
    st.session_state.df_usend_uniq_ticks = st.session_state.df_usend_uniq.copy()
    st.session_state.tick_scrape_output = [
        st.session_state.df_usend_uniq_ticks,
        scrape_details,
        st.session_state.df_usend,
    ]
    full_scrape_output = st.session_state.tick_scrape_output
    uniq_df_output = st.session_state.df_usend_uniq_ticks
if st.session_state.list_type == "ToDos":
    st.session_state.df_usend_uniq_todos = st.session_state.df_usend_uniq.copy()
    st.session_state.todo_scrape_output = [
        st.session_state.df_usend_uniq_todos,
        scrape_details,
        None,
    ]
    full_scrape_output = st.session_state.todo_scrape_output
    uniq_df_output = st.session_state.df_usend_uniq_todos

### Export
st.markdown("---")
st.header("4. Export")
st.write("Save current route list for later or to use on your own")
st.download_button(
    label=f"Download {st.session_state.list_type}.PKL File For Giza",
    data=pickle.dumps(full_scrape_output),
    file_name=f"Giza_{st.session_state.list_type.lower()}_{st.session_state.upload_link_ref_str}_{date.today()}.pkl",
    disabled=st.session_state.exp_button_state,
    help="PKL files are what Giza uses to build your analysis",
)
st.download_button(
    label=f"Download {st.session_state.list_type}.CSV For Personal Use",
    data=uniq_df_output.to_csv().encode("utf-8"),
    file_name=f"Giza_{st.session_state.list_type.lower()}_{st.session_state.upload_link_ref_str}_{date.today()}.csv",
    mime="text/csv",
    disabled=st.session_state.exp_button_state,
    help="CSV files are nice if you want to poke around the data yourself in excel or another program",
)
