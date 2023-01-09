import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
import streamlit_nested_layout
from unique_route_handling import *
from tick_route_handling import tick_merge, flag_notable_ticks, clean_send_plots, tick_report
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
with st.expander('How It Works'):
    st.markdown("Placeholder")

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
        col1.info(f"There is a currently loaded scraped dataset saved on this session under username: {import_details['username']} from {import_details['date_scraped']}", icon="ℹ️")
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
        col1.info(f"There is a currently loaded scraped dataset saved on this session under username: {import_details['username']} from {import_details['date_scraped']}", icon="ℹ️")
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
    if anlist_type == "Ticks":
        col1, col2 = st.columns([1,3])
        date_min = user_ticks_df['Date'].min()
        date_max = user_ticks_df['Date'].max()
        date_fil_type = col1.radio("Date Filter Type", options=['Date Range', 'Quick Filter'])
        if date_fil_type == 'Date Range':
            date_fil = col2.date_input("Date Filter", value=(date_min, date_max), min_value=date_min, max_value=date_max)
            date_fil = pd.to_datetime(date_fil)
        if date_fil_type == 'Quick Filter':
            year_list = user_ticks_df['Date'].dt.year.unique().tolist()
            datefil_year_options = [f'Calendar Year: {str(year)}' for year in year_list]
            qdate_fil = col2.selectbox("Quick Date Filter", options=['Last 1 Month', 'Last 3 Months', 'Last 6 Months', 'Last 12 Months']+datefil_year_options)
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
    
    st.write(date_fil)
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Route Type'].isin(routetype_fil)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Rating'].isin(all_grade_fil)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Num Ticks'] >= numtick_fil]
    
    with st.expander("Full Unique Route Data Table"):
        # Formatting
        fulldat_orgcol_uniq = ['Route', 'Pitches', 'Route Type', 'Rating', 'Avg Stars', 'Length', 'Num Ticks', 'Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio', 'Location' ]
        fulldat_floatcol_uniq = ['Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio']
        df_uniq_fil[fulldat_floatcol_uniq] = df_uniq_fil[fulldat_floatcol_uniq].applymap(lambda x: float('{:,.2f}'.format(x)) if pd.notnull(x) else np.nan) # the if else here retains np.nans blank presentation
        df_uniq_fil['Route'] = df_uniq_fil.apply(lambda row: f"""<a target="_blank" href="{row['URL']}">{row['Route']}</a>""", axis=1)
        gb = GridOptionsBuilder.from_dataframe(df_uniq_fil[fulldat_orgcol_uniq])
        gb.configure_side_bar()
        gb.configure_default_column(wrapHeaderText=True, autoHeaderHeight=True)
        gb.configure_columns(fulldat_orgcol_uniq[1:-1], width=90, type='leftAligned')
        gb.configure_columns(fulldat_floatcol_uniq, type=["numericColumn","numberColumnFilter"])
        gb.configure_column('Route',
                            pinned=True,
                            cellRenderer=JsCode('''function(params) {return params.value}'''))
        AgGrid(data=df_uniq_fil[fulldat_orgcol_uniq], 
            height= 800,
            theme='balham',
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True)
    
    with st.expander("PreFab Unique Route Data Analysis"):
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
        
        df_uniq_fil_r = df_uniq_fil[df_uniq_fil['Route Type'] != 'Boulder']
        df_uniq_fil_b = df_uniq_fil[df_uniq_fil['Route Type'] == 'Boulder']
        # Rarely led
        df_low_lead = df_uniq_fil_r[(df_uniq_fil_r['Lead Ratio'] < 0.4) & (df_uniq_fil_r['Pitches'] == 1)].sort_values(by='Lead Ratio')
        # Rarely toproped
        df_high_lead = df_uniq_fil_r[(df_uniq_fil_r['Lead Ratio'] > 0.9) & (df_uniq_fil_r['Pitches'] == 1)].sort_values(by='Lead Ratio', ascending=False)
        # Low OS Ratio
        df_low_OS_r = df_uniq_fil_r[(df_uniq_fil_r['OS Ratio'] < 0.35)].sort_values(by='OS Ratio')
        df_low_OS_b = df_uniq_fil_b[(df_uniq_fil_b['OS Ratio'] < 0.35)].sort_values(by='OS Ratio')
        # High OS Ratio
        df_high_OS_r = df_uniq_fil_r[(df_uniq_fil_r['OS Ratio'] > 0.8)].sort_values(by='OS Ratio', ascending=False)
        df_high_OS_b = df_uniq_fil_b[(df_uniq_fil_b['OS Ratio'] > 0.8)].sort_values(by='OS Ratio', ascending=False)
        # N superlative OS Ratio by Grade
        def nsuperlative_os(data, rgrade_array, direction, numN):
            outlist = []
            for group in rgrade_array:
                if direction == 'highest':
                    outlist.extend(list(data[data['Rating'] == group].nlargest(numN, 'OS Ratio').index))
                if direction == 'lowest':
                    outlist.extend(list(data[data['Rating'] == group].nsmallest(numN, 'OS Ratio').index))
            df_out = data.loc[outlist]
            return df_out
        df_nlow_OS_r = nsuperlative_os(df_uniq_fil, selected_rgrade_array, 'lowest', numN)
        df_nhigh_OS_r = nsuperlative_os(df_uniq_fil, selected_rgrade_array, 'highest', numN)
        df_nlow_OS_b = nsuperlative_os(df_uniq_fil, selected_bgrade_array, 'lowest', numN)
        df_nhigh_OS_b = nsuperlative_os(df_uniq_fil, selected_bgrade_array, 'highest', numN)
        
        if analysis_route_type_option == 'Routes':
            analysis_datasets = [df_low_lead, df_high_lead, df_high_OS_r, df_low_OS_r, df_nlow_OS_r, df_nlow_OS_r]
        if analysis_route_type_option == 'Boulders':
            analysis_datasets = [df_high_OS_b, df_low_OS_b, df_nlow_OS_b, df_nlow_OS_b]
        
        analysis_dict = dict(zip(analysis_options, analysis_datasets))
        
        gb = GridOptionsBuilder.from_dataframe(analysis_dict[analysis_sel][fulldat_orgcol_uniq])
        gb.configure_side_bar()
        gb.configure_default_column(wrapHeaderText=True, autoHeaderHeight=True)
        gb.configure_columns(fulldat_orgcol_uniq[1:-1], width=90, type='leftAligned')
        gb.configure_column('Route',
                            pinned=True,
                            cellRenderer=JsCode('''function(params) {return params.value}'''))
        AgGrid(data=analysis_dict[analysis_sel][fulldat_orgcol_uniq], 
            height= 800,
            theme='balham',
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True)
    if anlist_type == 'Ticks' and len(date_fil) == 2:
        with st.expander("Full Tick Data Table"):
            user_ticks_merged = tick_merge(user_ticks_df, unique_routes_df)
            user_ticks_mf = user_ticks_merged.copy()
            user_ticks_mf = flag_notable_ticks(user_ticks_mf)
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Route Type'].isin(routetype_fil)]
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Rating'].isin(all_grade_fil)]
            user_ticks_mf = user_ticks_mf[(user_ticks_mf['Date'] >= date_fil[0]) & (user_ticks_mf['Date'] <= date_fil[1])]
            user_ticks_mff = user_ticks_mf[user_ticks_mf['Num Ticks'] >= numtick_fil]
            
            fulldat_orgcol_ticks = ['Route', 'Pitches', 'Route Type', 'Rating', 'Avg Stars', 'Length', 'Num Ticks', 'Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio', 'Flash/Onsight', 'Worked Clean', 'Grade Breakthrough', 'Attempts', 'Location' ]
            fulldat_floatcol_ticks = ['Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio']
            user_ticks_mff[fulldat_floatcol_ticks] = user_ticks_mff[fulldat_floatcol_ticks].applymap(lambda x: float('{:,.2f}'.format(x)) if pd.notnull(x) else np.nan) # the if else here retains np.nans blank presentation
            user_ticks_mff['Route'] = user_ticks_mff.apply(lambda row: f"""<a target="_blank" href="{row['URL']}">{row['Route']}</a>""", axis=1)
            gb = GridOptionsBuilder.from_dataframe(user_ticks_mff[fulldat_orgcol_ticks])
            gb.configure_side_bar()
            gb.configure_default_column(wrapHeaderText=True, autoHeaderHeight=True)
            gb.configure_columns(fulldat_orgcol_ticks[1:-1], width=90, type='leftAligned')
            gb.configure_columns(fulldat_floatcol_ticks, type=["numericColumn","numberColumnFilter"])
            gb.configure_column('Route',
                                pinned=True,
                                cellRenderer=JsCode('''function(params) {return params.value}'''))
            AgGrid(data=user_ticks_mff[fulldat_orgcol_ticks], 
                height= 800,
                theme='balham',
                gridOptions=gb.build(),
                allow_unsafe_jscode=True)
            
        with st.expander("Tick Pyramid Plots"):
            col1, col2, col3 = st.columns([1,2,5])
            pyr_plot_type_sel = col1.radio("Plot Type Selection", options=['Routes', 'Boulders'])
            col2.write("#")
            pyr_plot_igtick_bool = col2.checkbox("Ignore Tick Cutoff", value=True)
            if pyr_plot_igtick_bool == False:
                rpyrplot, rtimeplot, bpyrplot, btimeplot = clean_send_plots(user_ticks_mff, selected_rgrade_array, selected_bgrade_array)
            if pyr_plot_igtick_bool ==True:
                rpyrplot, rtimeplot, bpyrplot, btimeplot = clean_send_plots(user_ticks_mf, selected_rgrade_array, selected_bgrade_array)
            if pyr_plot_type_sel =='Routes':
                st.plotly_chart(rpyrplot, theme=None, use_container_width=True)
                st.plotly_chart(rtimeplot, theme=None, use_container_width=True)
            if pyr_plot_type_sel =='Boulders':
                st.plotly_chart(bpyrplot, theme=None, use_container_width=True)
                st.plotly_chart(btimeplot, theme=None, use_container_width=True)

        with st.expander("Tick Report"):
            df_bold_leads, df_impressive_OS, df_woops_falls = tick_report(user_ticks_mff)
            if not df_bold_leads.empty:
                st.text("While others opted for the top rope, you faced the sharp end.")
                st.write(df_bold_leads)
            if not df_impressive_OS.empty:
                st.text("Few others managed to nab the OS/Flash, but you did.")
                st.write(df_impressive_OS)
            if not df_woops_falls.empty:
                st.text("We all fall, but these were the least excuseable of yours...")
                st.write(df_woops_falls)