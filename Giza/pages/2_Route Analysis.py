import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
import streamlit_nested_layout
from unique_route_handling import *
from tick_route_handling import tick_merge, flag_notable_ticks, clean_send_plots, tick_report
from aggrid_formats import aggrid_uniq_format, aggrid_tick_format
from long_strs import analysis_explainer
import os
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta 
from itertools import compress
import pickle

st.set_page_config(layout="wide")
unique_routes_df = pd.DataFrame()

st.title("Tick Analysis")
st.subheader("Explore Your Ticks and Discover Notable Sends")
st.markdown('---')
with st.expander('Details'):
    st.markdown(analysis_explainer)

col1, col2, col3 = st.columns([1.5,0.25,1.25])
col1.header('Dataset Selection')
anlist_type = col1.radio("List Type", options=["Ticks", "ToDos"], horizontal=True)
data_source_type_selections = ['Select Provided Dataset', 'Upload Pickle File']
if anlist_type == 'Ticks':
    if not st.session_state.df_usend_uniq_ticks.empty:
        data_source_type_selections.insert(0, 'Use Session Dataset')
    data_source_type = col1.radio("Data Source Selection", data_source_type_selections, help="placeholder ", horizontal=True)
    if data_source_type == 'Use Session Dataset':
        unique_routes_df, import_details, user_ticks_df = st.session_state.tick_scrape_output
        col1.info(f"There is a currently loaded dataset saved on this session for user {import_details['username']} from date {import_details['date_scraped']}", icon="ℹ️")
    if data_source_type == "Select Provided Dataset":
        preldata_path = Path(__file__).parents[1] / 'Data_Archive/Ticks/'
        files = os.listdir(preldata_path)
        preldata_sel = col1.selectbox("Profiles", files)
        try:
            unique_routes_df, import_details, user_ticks_df = pickle.load(open(preldata_path / preldata_sel, 'rb'))
        except:
            st.error("File Not Found", icon="⚠️")
    if data_source_type == "Upload Pickle File":
        tick_upload = col1.file_uploader("Upload Pickle")
        if tick_upload is not None:
            try:
                unique_routes_df, import_details, user_ticks_df = pickle.load(tick_upload)
            except:
                st.error("File Error", icon="⚠️")
if anlist_type == 'ToDos':
    if not st.session_state.df_usend_uniq_todos.empty:
        data_source_type_selections.insert(0, 'Use Session Dataset')
    data_source_type = col1.radio("Data Source Selection", data_source_type_selections, help="placeholder ", horizontal=True)
    if data_source_type == 'Use Session Dataset':
        unique_routes_df, import_details, _ = st.session_state.todo_scrape_output
        col1.info(f"There is a currently loaded dataset saved on this session for user {import_details['username']} from date {import_details['date_scraped']}", icon="ℹ️")
    if data_source_type == "Select Provided Dataset":
        preldata_path = Path(__file__).parents[1] / 'Data_Archive/ToDos/'
        files = os.listdir(preldata_path)
        preldata_sel = col1.selectbox("Profiles", files)
        try:
            unique_routes_df, import_details, _ = pickle.load(open(preldata_path / preldata_sel, 'rb'))
        except:
            st.error("File Not Found", icon="⚠️")
    if data_source_type == "Upload Pickle File":
        todo_upload = col1.file_uploader("Upload Pickle")
        if todo_upload is not None:
            try:
                unique_routes_df, import_details, _ = pickle.load(todo_upload)
            except:
                st.error("File Error", icon="⚠️")

if not unique_routes_df.empty:
    with col3:
        st.subheader("Select Grade Homegenization Type")
        grade_settings = ['letter', 'even_rand', 'flat', 'even_rand']
        route_round_type = 'Round Evenly By Random'
        col1, col2 = st.columns([1,1])
        with col1:
            route_grade_type = st.radio("Routes", options=['Letter (5.10a)', 'Sign (5.10-)'])
            if route_grade_type == 'Letter (5.10a)':
                route_round_type = st.radio("Route Round Type", options=['Round Evenly By Random', 'Round Up', 'Round Down'], help='Round Evenly By Random rounds up half of the population and rounds down the other half. Which route belongs to which half is random.')
        with col2:
            boulder_grade_type = st.radio("Boulders", options=['Flat (V4)', 'Sign (V4-)'])
            boulder_round_type = st.radio("Boulder Round Type", options=['Round Evenly By Random', 'Round Up', 'Round Down'], help='Round Evenly By Random rounds up half of the population and rounds down the other half. Which route belongs to which half is random.')
        gh_key = {'Sign (5.10-)': 'sign', 'Letter (5.10a)': 'letter', 'Sign (V4-)': 'sign', 'Flat (V4)': 'flat', 'Round Evenly By Random': 'even_rand', 'Round Down': 'down', 'Round Up': 'up' }
        grade_settings = [gh_key[route_grade_type], gh_key[route_round_type], gh_key[boulder_grade_type], gh_key[boulder_round_type]]
        route_grade_array_dict = {'sign': YDS_GRADES_SIGN, 'letter': YDS_GRADES_LETTER}
        unique_routes_df = grade_homo(unique_routes_df, *grade_settings)
        selected_rgrade_array = {'sign': YDS_GRADES_SIGN, 'letter': YDS_GRADES_LETTER}[gh_key[route_grade_type]]
        selected_bgrade_array = {'sign': V_GRADES_SIGN, 'flat': V_GRADES_FLAT}[gh_key[boulder_grade_type]]
    st.markdown('---')
    
    # Filtering
    st.header("Filtering")
    df_uniq_fil = unique_routes_df.copy()
    col1, col2, col3 = st.columns([1.25,0.25,2.75])
    with col1:
        routetype_fil = st.multiselect("Climb Type", options=['Sport', 'Trad', 'Boulder'], default=['Sport', 'Trad', 'Boulder'])
        numtick_fil = st.number_input("Minimum Tick Count Cutoff", min_value=1, value=30, help="Low tick counts make for poor quality metrics, this eliminates entries with tick counts below the cutoff")
    with col3:
        def grade_filter_align(datalist, orderedlist):
            full_list = [i for i in orderedlist if i in datalist['Rating'].unique()]
            minval = full_list[0]
            maxval = full_list[-1]
            trunc_full_list = orderedlist[orderedlist.index(minval) : orderedlist.index(maxval)+1]
            return trunc_full_list, (minval, maxval)
        r_grade_fil, b_grade_fil = [], []
        if any(df_uniq_fil['Rating'].unique().isin(selected_rgrade_array)):
            r_grade_min, r_grade_max = st.select_slider("Route Grade Filter",
                                                        options=grade_filter_align(df_uniq_fil, selected_rgrade_array)[0],
                                                        value=grade_filter_align(df_uniq_fil, selected_rgrade_array)[1])
            r_grade_fil = selected_rgrade_array[selected_rgrade_array.index(r_grade_min) : selected_rgrade_array.index(r_grade_max)+1]
        if any(df_uniq_fil['Rating'].unique().isin(selected_bgrade_array)):
            b_grade_min, b_grade_max = st.select_slider("Boulder Grade Filter",
                                                        options=grade_filter_align(df_uniq_fil, selected_bgrade_array)[0],
                                                        value=grade_filter_align(df_uniq_fil, selected_bgrade_array)[1])
            b_grade_fil = selected_bgrade_array[selected_bgrade_array.index(b_grade_min) : selected_bgrade_array.index(b_grade_max)+1]
        all_grade_fil = r_grade_fil + b_grade_fil

    col1, col2, col3, col4 = st.columns([1.25,0.25,0.5,2.25])
    pitch_fil_sel = col1.multiselect("Pitch Type", options=['Single Pitch', 'Multi Pitch'], default=['Single Pitch', 'Multi Pitch'])
    if anlist_type == "Ticks":
        date_min = user_ticks_df['Date'].min()
        date_max = user_ticks_df['Date'].max()
        date_fil_type = col3.radio("Date Filter Type", options=['Date Range', 'Quick Filter'])
        if date_fil_type == 'Date Range':
            date_fil = col4.date_input("Date Filter", value=(date_min, date_max), min_value=date_min, max_value=date_max)
            date_fil = pd.to_datetime(date_fil)
        if date_fil_type == 'Quick Filter':
            year_list = user_ticks_df['Date'].dt.year.unique().tolist()
            datefil_year_options = [f'Calendar Year: {str(year)}' for year in year_list]
            qdate_fil = col4.selectbox("Quick Date Filter", options=datefil_year_options+['Last 1 Month', 'Last 3 Months', 'Last 6 Months', 'Last 12 Months'])
            def date_del_month(num_months):
                deldate = date.today() + relativedelta(months=num_months)
                date_fil = pd.to_datetime((deldate, date.today()))
                return date_fil
            if qdate_fil == 'Last 1 Month':
                date_fil = date_del_month(-1)
            if qdate_fil == 'Last 3 Months':
                date_fil = date_del_month(-3)
            if qdate_fil == 'Last 6 Months':
                date_fil = date_del_month(-6)
            if qdate_fil == 'Last 12 Months':
                date_fil = date_del_month(-12)
            for year in year_list:
                if qdate_fil == f'Calendar Year: {str(year)}':
                    date_fil = pd.to_datetime((date(year, 1, 1), date(year, 12, 31)))
    col1, col2 = st.columns([0.3, 4])
    loc_max_tier = df_uniq_fil['Location'].apply(lambda x: len(x.split('>'))).max()
    loc_tier = col1.number_input("Location Tier", min_value=1, max_value=loc_max_tier, value=1, help='Location Tier describes how "deep" the location filter goes. Tier1 is typically a state, Tier2 is typically a geographic area or major destination, Tier3 is typically a sub-area, Tier4 and further typically denote crags and subcrags.')
    location_list = df_uniq_fil['Location'].apply(lambda x: '>'.join(x.split('>')[0:(loc_tier)])).unique()
    loc_sel = col2.multiselect("Location", options=location_list)

    if len(pitch_fil_sel) == 1:
        if pitch_fil_sel[0] == 'Single Pitch':
            df_uniq_fil = df_uniq_fil[df_uniq_fil['Pitches'] == 1]
        if pitch_fil_sel[0] == 'Multi Pitch':
            df_uniq_fil = df_uniq_fil[df_uniq_fil['Pitches'] > 1]
    if not loc_sel == '':
        df_uniq_fil = df_uniq_fil[df_uniq_fil['Location'].str.contains('|'.join(loc_sel))]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Route Type'].isin(routetype_fil)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Rating'].isin(all_grade_fil)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Num Ticks'] >= numtick_fil]
    
    st.markdown('---')    
    with st.expander("Prefabricated Route Analysis"):
        col1, col2, col3 = st.columns([1,3,1])
        analysis_route_type_option = col1.radio("Route Type", options=['Routes', 'Boulders'], horizontal=True)
        analysis_options_r = ['Rarely Led Routes', 'Rarely Toproped Routes', 'Commonly Onsighted Routes', 'Rarely Onsighted Routes', 'N Most Onsighted Routes Per Grade', 'N Least Onsighted Routes Per Grade']
        analysis_options_b = ['Commonly Onsighted Boulders', 'Rarely Onsighted Boulders', 'N Most Onsighted Boulders Per Grade', 'N Least Onsighted Boulders Per Grade']
        if analysis_route_type_option == 'Routes':
            analysis_options = analysis_options_r
        if analysis_route_type_option == 'Boulders':
            analysis_options = analysis_options_b
        analysis_sel = col2.selectbox('Analysis Type', options=analysis_options)
        numN=1
        if analysis_sel in ['N Most Onsighted Routes Per Grade', 'N Least Onsighted Routes Per Grade', 'N Most Onsighted Boulders Per Grade', 'N Least Onsighted Boulders Per Grade']:
            numN = col3.number_input("N =", min_value=1, value=3)
        df_low_lead, df_high_lead, df_high_OS_r, df_low_OS_r, df_nlow_OS_r, df_nhigh_OS_r, df_high_OS_b, df_low_OS_b, df_nlow_OS_b, df_nhigh_OS_b = unique_route_prefabanalysis(df_uniq_fil, selected_rgrade_array, selected_bgrade_array, numN)
        
        if analysis_route_type_option == 'Routes':
            analysis_datasets = [df_low_lead, df_high_lead, df_high_OS_r, df_low_OS_r, df_nlow_OS_r, df_nhigh_OS_r]
        if analysis_route_type_option == 'Boulders':
            analysis_datasets = [df_high_OS_b, df_low_OS_b, df_nlow_OS_b, df_nhigh_OS_b]
        
        analysis_dict = dict(zip(analysis_options, analysis_datasets))
        df_uniq_prefab_pres, gb = aggrid_uniq_format(analysis_dict[analysis_sel])
        AgGrid(data=df_uniq_prefab_pres, 
            height= 800,
            theme='balham',
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True)

    with st.expander("Full Data: Routes"):
        # Formatting
        df_uniq_fil_pres, gb = aggrid_uniq_format(df_uniq_fil)
        AgGrid(data=df_uniq_fil_pres, 
            height= 800,
            theme='balham',
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True)
        
    if anlist_type == 'Ticks' and len(date_fil) == 2:
        user_ticks_merged = tick_merge(user_ticks_df, unique_routes_df)
        user_ticks_mf = user_ticks_merged.copy()
        user_ticks_mf = flag_notable_ticks(user_ticks_mf)
        if len(pitch_fil_sel) == 1:
            if pitch_fil_sel[0] == 'Single Pitch':
                user_ticks_mf = user_ticks_mf[user_ticks_mf['Pitches'] == 1]
            if pitch_fil_sel[0] == 'Multi Pitch':
                user_ticks_mf = user_ticks_mf[user_ticks_mf['Pitches'] > 1]
        if not loc_sel == '':
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Location'].str.contains('|'.join(loc_sel))]
        user_ticks_mf = user_ticks_mf[user_ticks_mf['Route Type'].isin(routetype_fil)]
        user_ticks_mf = user_ticks_mf[user_ticks_mf['Rating'].isin(all_grade_fil)]
        user_ticks_mf = user_ticks_mf[(user_ticks_mf['Date'] >= date_fil[0]) & (user_ticks_mf['Date'] <= date_fil[1])]
        user_ticks_mff = user_ticks_mf[user_ticks_mf['Num Ticks'] >= numtick_fil]
        st.markdown('---')
        with st.expander("Tick Pyramid Plots"):
            col1, col2, col3 = st.columns([1,2,5])
            pyr_plot_type_sel = col1.radio("Plot Type Selection", options=['Routes', 'Boulders'])
            col2.write("#")
            pyr_plot_igtick_bool = col2.checkbox("Ignore Tick Cutoff", value=True)
            if pyr_plot_igtick_bool == False:
                rpyrplot, rtimeplot, bpyrplot, btimeplot = clean_send_plots(user_ticks_mff, selected_rgrade_array, r_grade_fil, selected_bgrade_array, b_grade_fil)
            if pyr_plot_igtick_bool ==True:
                rpyrplot, rtimeplot, bpyrplot, btimeplot = clean_send_plots(user_ticks_mff, selected_rgrade_array, r_grade_fil, selected_bgrade_array, b_grade_fil)
            if pyr_plot_type_sel =='Routes':
                st.plotly_chart(rpyrplot, theme=None, use_container_width=True)
                st.plotly_chart(rtimeplot, theme=None, use_container_width=True)
            if pyr_plot_type_sel =='Boulders':
                st.plotly_chart(bpyrplot, theme=None, use_container_width=True)
                st.plotly_chart(btimeplot, theme=None, use_container_width=True)

        with st.expander("Notable Sends"):
            df_bold_leads, df_impressive_OS, df_woops_falls = tick_report(user_ticks_mff)
            if not df_bold_leads.empty:
                st.markdown("##### [Led route with low lead ratio] | While others opted for the top rope, you faced the sharp end.")
                df_bold_leads_pres, gb = aggrid_tick_format(df_bold_leads)
                AgGrid(data=df_bold_leads_pres, 
                    theme='balham',
                    gridOptions=gb.build(),
                    allow_unsafe_jscode=True)
                st.text('')
            st.markdown('---')
            if not df_impressive_OS.empty:
                st.markdown("##### [OS'd route with low OS ratio] | Few others managed to nab the OS/Flash, but you did.")
                df_impressive_OS_pres, gb = aggrid_tick_format(df_impressive_OS)
                AgGrid(data=df_impressive_OS_pres, 
                    theme='balham',
                    gridOptions=gb.build(),
                    allow_unsafe_jscode=True)
                st.text('')
            st.markdown('---')
            if not df_woops_falls.empty:
                st.markdown("##### [Fell/hung route with high OS ratio] | We all fall, but these were your most agregious slip ups.")
                df_woops_falls_pres, gb = aggrid_tick_format(df_woops_falls)
                AgGrid(data=df_woops_falls_pres, 
                    theme='balham',
                    gridOptions=gb.build(),
                    allow_unsafe_jscode=True)
                st.text('')
                
        with st.expander("Full Data: Ticks"):
            df_ticks_pres, gb = aggrid_tick_format(user_ticks_mff)
            AgGrid(data=df_ticks_pres, 
                height= 800,
                theme='balham',
                gridOptions=gb.build(),
                allow_unsafe_jscode=True)