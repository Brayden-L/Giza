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
import pickle

### Setup
st.set_page_config(layout="wide")
unique_routes_df = pd.DataFrame()

### Header
st.title("Tick Analysis")
st.subheader("Explore Your Ticks and Discover Notable Sends")
st.markdown('---')
with st.expander('✋ Help ✋'):
    st.markdown(analysis_explainer, unsafe_allow_html=True)

### Dataset Selection
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

### Grade Homogenization
if not unique_routes_df.empty:
    with col3:
        st.subheader("Grade Homegenization Type")
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
    
    ### Filtering
    # Filter widget setup
    # Enabling the filters to be moved to the sidebar makes the code much less readable but I think it is worth it. I'm not super happy with the overall flow of the code.
    st.header("Filtering")
    move_fil = st.checkbox("Move Filter to Sidebar", help="Filters in the sidebar remove the need to scroll back and forth if you will be tweaking the filter settings a lot. This is at the expense of cramped visuals.")
    df_uniq_fil = unique_routes_df.copy()
    
    # Routetype and tick filter
    col1, col2, col3 = st.columns([1.75,0.25,2.75])
    routetype_options = df_uniq_fil['Route Type'].unique().tolist()
    routetype_fil_widg_dict = {'label': "Climb Type",
                               'options': routetype_options,
                               'default': routetype_options} 
    numtick_fil_widg_dict = {'label': "Minimum Tick Count Cutoff", 
                            'min_value': 1,
                            'value': 30,
                            'help': "Low tick counts make for poor quality metrics, this filter eliminates entries with tick counts below the cutoff"}
    if move_fil == True:
        numtick_fil = st.sidebar.number_input(label=numtick_fil_widg_dict['label'],
                                        min_value=numtick_fil_widg_dict['min_value'],
                                        value=numtick_fil_widg_dict['value'],
                                        help=numtick_fil_widg_dict['help'])
        routetype_fil = st.sidebar.multiselect(label=routetype_fil_widg_dict['label'],
                                               options=routetype_fil_widg_dict['options'],
                                               default=routetype_fil_widg_dict['default'])
    if move_fil == False:
        numtick_fil = col1.number_input(label=numtick_fil_widg_dict['label'],
                                min_value=numtick_fil_widg_dict['min_value'],
                                value=numtick_fil_widg_dict['value'],
                                help=numtick_fil_widg_dict['help'])
        routetype_fil = col1.multiselect(label=routetype_fil_widg_dict['label'],
                                         options=routetype_fil_widg_dict['options'],
                                         default=routetype_fil_widg_dict['default'])

    # Grade filter
    def grade_filter_align(datalist, orderedlist):
        full_list = [i for i in orderedlist if i in datalist['Rating'].unique()]
        minval = full_list[0]
        maxval = full_list[-1]
        trunc_full_list = orderedlist[orderedlist.index(minval) : orderedlist.index(maxval)+1]
        return trunc_full_list, (minval, maxval)
    r_grade_fil, b_grade_fil = [], []
    r_grade_fil_widg_dict = {'label': "Route Grade Filter",
                            'options': grade_filter_align(df_uniq_fil, selected_rgrade_array)[0],
                            'value': grade_filter_align(df_uniq_fil, selected_rgrade_array)[1]}
    b_grade_fil_widg_dict ={'label': "Boulder Grade Filter",
                            'options': grade_filter_align(df_uniq_fil, selected_bgrade_array)[0],
                            'value': grade_filter_align(df_uniq_fil, selected_bgrade_array)[1]}
    
    if move_fil == True:
        if any(df_uniq_fil['Rating'].unique().isin(selected_rgrade_array)):
            r_grade_min, r_grade_max = st.sidebar.select_slider(label=r_grade_fil_widg_dict["label"],
                                                        options=r_grade_fil_widg_dict["options"],
                                                        value=r_grade_fil_widg_dict["value"])
            r_grade_fil = selected_rgrade_array[selected_rgrade_array.index(r_grade_min) : selected_rgrade_array.index(r_grade_max)+1]
        if any(df_uniq_fil['Rating'].unique().isin(selected_bgrade_array)):
            b_grade_min, b_grade_max = st.sidebar.select_slider(label=b_grade_fil_widg_dict['label'],
                                                        options=b_grade_fil_widg_dict['options'],
                                                        value=b_grade_fil_widg_dict['value'])
            b_grade_fil = selected_bgrade_array[selected_bgrade_array.index(b_grade_min) : selected_bgrade_array.index(b_grade_max)+1]
    if move_fil == False:
        if any(df_uniq_fil['Rating'].unique().isin(selected_rgrade_array)):
            r_grade_min, r_grade_max = col3.select_slider(label=r_grade_fil_widg_dict["label"],
                                                        options=r_grade_fil_widg_dict["options"],
                                                        value=r_grade_fil_widg_dict["value"])
            r_grade_fil = selected_rgrade_array[selected_rgrade_array.index(r_grade_min) : selected_rgrade_array.index(r_grade_max)+1]
        if any(df_uniq_fil['Rating'].unique().isin(selected_bgrade_array)):
            b_grade_min, b_grade_max = col3.select_slider(label=b_grade_fil_widg_dict['label'],
                                                        options=b_grade_fil_widg_dict['options'],
                                                        value=b_grade_fil_widg_dict['value'])
            b_grade_fil = selected_bgrade_array[selected_bgrade_array.index(b_grade_min) : selected_bgrade_array.index(b_grade_max)+1]
    all_grade_fil = r_grade_fil + b_grade_fil

    # Single pitch or multi pitch filter
    col1, col2, col3, col4 = st.columns([1.75,0.25,0.5,2.25])
    pitch_fil_widg_dict = {'label': "Pitch Type", 
                           'options': ['Single Pitch', 'Multi Pitch'],
                           'default': ['Single Pitch', 'Multi Pitch']}
    if move_fil == True:
        pitch_fil_sel = st.sidebar.multiselect(label=pitch_fil_widg_dict['label'],
                                               options=pitch_fil_widg_dict['options'],
                                               default=pitch_fil_widg_dict['default'])
    if move_fil == False:
        pitch_fil_sel = col1.multiselect(label=pitch_fil_widg_dict['label'],
                                               options=pitch_fil_widg_dict['options'],
                                               default=pitch_fil_widg_dict['default'])
    pitch_fil_transf = {'Single Pitch': 'SP', 'Multi Pitch':'MP'}
    pitch_fil_sel = [pitch_fil_transf[x] for x in pitch_fil_sel]
    # Date filter
    if anlist_type == "Ticks":
        date_min = user_ticks_df['Date'].min()
        date_max = user_ticks_df['Date'].max()
        date_fil_type_widg_dict = {'label': "Date Filter Type",
                                   'options': ['Date Range', 'Quick Filter'],
                                   'index': 1}
        date_fil_widg_dict = {'label': "Date Filter",
                             'value': (date_min, date_max), 
                            'min_value': date_min,
                            'max_value': date_max}
        if move_fil == True:
            date_fil_type = st.sidebar.radio(label=date_fil_type_widg_dict['label'],
                                             options=date_fil_type_widg_dict['options'],
                                             index=date_fil_type_widg_dict['index'])
        if move_fil == False:
            date_fil_type = col3.radio(label=date_fil_type_widg_dict['label'],
                                       options=date_fil_type_widg_dict['options'],
                                       index=date_fil_type_widg_dict['index'])
        if date_fil_type == 'Date Range':
            if move_fil == True:
                date_fil = st.sidebar.date_input(label=date_fil_widg_dict['label'],
                                                value=date_fil_widg_dict['value'], 
                                                min_value=date_fil_widg_dict['min_value'],
                                                max_value=date_fil_widg_dict['max_value'])
            if move_fil == False:
                date_fil = col4.date_input(label=date_fil_widg_dict['label'],
                                                value=date_fil_widg_dict['value'], 
                                                min_value=date_fil_widg_dict['min_value'],
                                                max_value=date_fil_widg_dict['max_value'])
            date_fil = pd.to_datetime(date_fil)
        if date_fil_type == 'Quick Filter':
            year_list = user_ticks_df['Date'].dt.year.unique().tolist()
            datefil_year_options = [f'Calendar Year: {str(year)}' for year in year_list]
            qdate_fil_widg_dict = {'label': "Quick Date Filter",
                                   'options': datefil_year_options+['Last 1 Month', 'Last 3 Months', 'Last 6 Months', 'Last 12 Months']}
            if move_fil == True:
                qdate_fil = st.sidebar.selectbox(label=qdate_fil_widg_dict['label'],
                                                 options=qdate_fil_widg_dict['options'])
            if move_fil == False:
                qdate_fil = col4.selectbox(label=qdate_fil_widg_dict['label'],
                                           options=qdate_fil_widg_dict['options'])
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
    
    # Location filter
    col1, col2 = st.columns([0.3, 4])
    loc_max_tier = df_uniq_fil['Location'].apply(lambda x: len(x.split('>'))).max()           
    loc_tier_widg_dict = {'label': "Location Tier",
                          'min_value': 1,
                          'max_value': loc_max_tier,
                          'value': 1,
                          'help': 'Location Tier describes how "deep" the location filter goes. Tier1 is typically a state, Tier2 is typically a geographic area or major destination, Tier3 is typically a sub-area, Tier4 and further typically denote crags and subcrags. It is important to note that between major areas these tiers do not often line up.'}
    if move_fil == True:
        loc_tier = st.sidebar.number_input(label=loc_tier_widg_dict['label'],
                                           min_value=loc_tier_widg_dict['min_value'],
                                           max_value=loc_tier_widg_dict['max_value'],
                                           value=loc_tier_widg_dict['value'],
                                           help=loc_tier_widg_dict['help'])
    if move_fil == False:
        loc_tier = col1.number_input(label=loc_tier_widg_dict['label'],
                                     min_value=loc_tier_widg_dict['min_value'],
                                     max_value=loc_tier_widg_dict['max_value'],
                                     value=loc_tier_widg_dict['value'],
                                     help=loc_tier_widg_dict['help'])
    location_list = df_uniq_fil['Location'].apply(lambda x: '>'.join(x.split('>')[0:(loc_tier)])).unique()
    location_list.sort()
    location_list_widg_dict = {'label': "Location",
                               'options': location_list}
    if move_fil == True:
        loc_sel = st.sidebar.multiselect(label=location_list_widg_dict['label'],
                                         options=location_list_widg_dict['options'])
    if move_fil == False:
        loc_sel = col2.multiselect(label=location_list_widg_dict['label'],
                                   options=location_list_widg_dict['options'])
    
    col1, col2, col3 = st.columns([1.75,0.25,2.75])
    if anlist_type == "Ticks":
        # Style filter
        style_options = user_ticks_df['Style'].unique().tolist()
        style_fil_widg_dict = {'label': 'Style',
                            'options': style_options,
                            'default': style_options,
                            'help': 'Note that "Flash", "Attempt", and "Send" refer to bouldering styles here'}
        if move_fil == True:
            style_fil = st.sidebar.multiselect(label=style_fil_widg_dict['label'],
                                               options=style_fil_widg_dict['options'],
                                               default=style_fil_widg_dict['default'],
                                               help=style_fil_widg_dict['help'])
        if move_fil == False:
            style_fil = col1.multiselect(label=style_fil_widg_dict['label'],
                                         options=style_fil_widg_dict['options'],
                                         default=style_fil_widg_dict['default'],
                                         help=style_fil_widg_dict['help'])
        # Lead style filter
        lead_style_list = user_ticks_df['Lead Style'].unique().tolist()
        lead_style_fil_widg_dict = {'label': 'Lead Style',
                            'options': lead_style_list,
                            'default': lead_style_list,
                            'help': '"nan" is default for non-lead styles such as TR, follow, and all boulders'}
        if move_fil == True:
            lead_style_fil = st.sidebar.multiselect(label=lead_style_fil_widg_dict['label'],
                                                    options=lead_style_fil_widg_dict['options'],
                                                    default=lead_style_fil_widg_dict['default'],
                                                    help=lead_style_fil_widg_dict['help'])
        if move_fil == False:
            lead_style_fil = col1.multiselect(label=lead_style_fil_widg_dict['label'],
                                              options=lead_style_fil_widg_dict['options'],
                                              default=lead_style_fil_widg_dict['default'],
                                              help=lead_style_fil_widg_dict['help'])
    
    # Star filter
    min_stars, max_stars = float(df_uniq_fil['Avg Stars'].min()), float(df_uniq_fil['Avg Stars'].max())
    star_fil_widg_dict = {'label': 'Avg Stars',
                          'min_value': min_stars,
                          'max_value': max_stars,
                          'value': (min_stars, max_stars)}
    if move_fil == True:
        star_fil_min, star_fil_max = st.sidebar.slider(label=star_fil_widg_dict['label'],
                                                       min_value=star_fil_widg_dict['min_value'],
                                                       max_value=star_fil_widg_dict['max_value'],
                                                       value=star_fil_widg_dict['value'])
    if move_fil == False:
        star_fil_min, star_fil_max = col3.slider(label=star_fil_widg_dict['label'],
                                                 min_value=star_fil_widg_dict['min_value'],
                                                 max_value=star_fil_widg_dict['max_value'],
                                                 value=star_fil_widg_dict['value'])
    
    # Length filter
    min_length, max_length = float(df_uniq_fil['Length'].min()), float(df_uniq_fil['Length'].max())
    length_fil_widg_dict = {'label': 'Length',
                          'min_value': min_length,
                          'max_value': max_length,
                          'value': (min_length, max_length)}
    if move_fil == True:
        length_fil_min, length_fil_max = st.sidebar.slider(label=length_fil_widg_dict['label'],
                                                    min_value=length_fil_widg_dict['min_value'],
                                                    max_value=length_fil_widg_dict['max_value'],
                                                    value=length_fil_widg_dict['value'])
    if move_fil == False:
        length_fil_min, length_fil_max = col3.slider(label=length_fil_widg_dict['label'],
                                                 min_value=length_fil_widg_dict['min_value'],
                                                 max_value=length_fil_widg_dict['max_value'],
                                                 value=length_fil_widg_dict['value'])
        
    # Apply unique route filters
    df_uniq_fil = df_uniq_fil[(df_uniq_fil['SP/MP'].isin(pitch_fil_sel)) | (df_uniq_fil['SP/MP'].isna())]
    if not loc_sel == '':
        df_uniq_fil = df_uniq_fil[df_uniq_fil['Location'].str.contains('|'.join(loc_sel))]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Route Type'].isin(routetype_fil)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Rating'].isin(all_grade_fil)]
    df_uniq_fil = df_uniq_fil[(df_uniq_fil['Avg Stars'] >= star_fil_min) & (df_uniq_fil['Avg Stars'] <= star_fil_max)]
    df_uniq_fil = df_uniq_fil[(df_uniq_fil['Length'] >= length_fil_min) & (df_uniq_fil['Length'] <= length_fil_max)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Num Ticks'] >= numtick_fil]
    # Apply tick filters
    if anlist_type == 'Ticks' and len(date_fil) == 2:
        if df_uniq_fil.empty:
            st.error("No Tick Results With Current Filter Settings")
        else:
            # Initialize tick dataframe
            user_ticks_merged = tick_merge(user_ticks_df, unique_routes_df)
            user_ticks_mf = user_ticks_merged.copy()
            user_ticks_mf = flag_notable_ticks(user_ticks_mf)
            
            user_ticks_mf = user_ticks_mf[(user_ticks_mf['SP/MP'].isin(pitch_fil_sel)) | user_ticks_mf['SP/MP'].isna()]
            if not loc_sel == '':
                user_ticks_mf = user_ticks_mf[user_ticks_mf['Location'].str.contains('|'.join(loc_sel))]
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Route Type'].isin(routetype_fil)]
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Rating'].isin(all_grade_fil)]
            user_ticks_mf = user_ticks_mf[(user_ticks_mf['Date'] >= date_fil[0]) & (user_ticks_mf['Date'] <= date_fil[1])]
            user_ticks_mf = user_ticks_mf[(user_ticks_mf['Avg Stars'] >= star_fil_min) & (user_ticks_mf['Avg Stars'] <= star_fil_max)]
            user_ticks_mf = user_ticks_mf[(user_ticks_mf['Length'] >= length_fil_min) & (user_ticks_mf['Length'] <= length_fil_max)]
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Style'].isin(style_fil)]
            user_ticks_mf = user_ticks_mf[user_ticks_mf['Lead Style'].isin(lead_style_fil)]
            user_ticks_mff = user_ticks_mf[user_ticks_mf['Num Ticks'] >= numtick_fil]
    
    st.markdown('---')
    with st.expander("Overview Plots", expanded=True):
        ### Basic Plots
        # Pie Plots
        pie_header_cont = st.container()
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        pie_chart_margin = dict(t=35, b=35, l=35, r=35)
        if df_uniq_fil.empty:
            st.error("No Results With Current Filter Settings")
        else:
            if anlist_type == 'Ticks' and len(date_fil) == 2:
                pie_header_cont.markdown('##### Ticked Pitch Count Pie Charts')
                pie_agg = 'Pitches Ticked'
                df_counts_leadstyle = user_ticks_mff.groupby('Style')[pie_agg].sum()
                fig_pie_leadstyle = px.pie(values=df_counts_leadstyle.values,
                                        names=df_counts_leadstyle.index,
                                        color=df_counts_leadstyle.index,
                                        color_discrete_map={'Lead':'#779ECC', 'TR':'#FF7F50', 'Follow':'#C70039', 'Send':'#9FC0DE', 'Attempt':'#F2C894'},
                                        title='Style',
                                        width=300,
                                        height=300)
                fig_pie_leadstyle.update_layout(margin=pie_chart_margin)
                fig_pie_leadstyle.update_traces(hole=.4)
                col4.plotly_chart(fig_pie_leadstyle)

                df_counts_leadstyle = user_ticks_mff.groupby('Lead Style')[pie_agg].sum()
                fig_pie_leadstyle = px.pie(values=df_counts_leadstyle.values,
                                        names=df_counts_leadstyle.index,
                                        color=df_counts_leadstyle.index,
                                        color_discrete_map={'Fell/Hung':'#779ECC', 'Redpoint':'#FF985A', 'Pinkpoint':'#FFB6C1', 'Flash':'#425356', 'Onsight':'#BAC9B4'},
                                        title='Lead Style',
                                        width=300,
                                        height=300)
                fig_pie_leadstyle.update_layout(margin=pie_chart_margin)
                fig_pie_leadstyle.update_traces(hole=.4)
                col5.plotly_chart(fig_pie_leadstyle)

            if anlist_type == 'ToDos':
                pie_header_cont.markdown('##### Pitch Count Pie Charts')
                pie_agg = 'Pitches'

            df_counts_routetype = df_uniq_fil.groupby('Route Type')[pie_agg].sum()
            fig_pie_routetype = px.pie(values=df_counts_routetype.values,
                                    names=df_counts_routetype.index,
                                    color=df_counts_routetype.index,
                                    color_discrete_map={'Boulder':'#BAC9B4', 'Sport':'#FF985A', 'Trad':'#779ECC'},
                                    title='Climb Type',
                                    width=300,
                                    height=300)
            fig_pie_routetype.update_layout(margin=pie_chart_margin)
            fig_pie_routetype.update_traces(hole=.4)
            col1.plotly_chart(fig_pie_routetype)
            
            df_counts_spmp = df_uniq_fil.groupby('SP/MP')[pie_agg].sum()
            fig_pie_spmp = px.pie(values=df_counts_spmp.values,
                                names=df_counts_spmp.index,
                                color=df_counts_spmp.index,
                                color_discrete_map={'SP':'#F2C894', 'MP':'#BAC9B4'},
                                category_orders={},
                                title="Single or Multi Pitch",
                                width=300,
                                height=300)
            fig_pie_spmp.update_layout(margin=pie_chart_margin)
            fig_pie_spmp.update_traces(hole=.4)
            col2.plotly_chart(fig_pie_spmp)
            
            df_counts_loc1 = df_uniq_fil.groupby(df_uniq_fil['Location'].apply(lambda x: x.split('>')[0]))[pie_agg].sum()
            fig_pie_loc1 = px.pie(values=df_counts_loc1.values,
                                names=df_counts_loc1.index,
                                color_discrete_sequence=px.colors.qualitative.Pastel2,
                                title='Base Location',
                                width=300,
                                height=300)
            fig_pie_loc1.update_layout(margin=pie_chart_margin)
            fig_pie_loc1.update_traces(hole=.4)
            col3.plotly_chart(fig_pie_loc1)
        
        st.markdown('---')
        # Histograms
        st.markdown('##### Histograms')
        col1, col2 = st.columns([1,1])
        if anlist_type == 'Ticks':
            fig_hist_rgrade = px.histogram(user_ticks_mff[user_ticks_mff['Route Type'] != 'Boulder'].groupby('Rating', as_index=False, observed=True).sum(),
                                        x='Rating',
                                        y='Pitches',
                                        category_orders={'Rating': r_grade_fil},
                                        marginal='box',
                                        title='Route Grades',
                                        text_auto=True)
            fig_hist_rgrade.update_xaxes(type='category')
            fig_hist_rgrade.update_traces(marker_color='#ac7c5c')
            col1.plotly_chart(fig_hist_rgrade)
            fig_hist_bgrade = px.histogram(user_ticks_mff[user_ticks_mff['Route Type'] == 'Boulder'].groupby('Rating', as_index=False, observed=True)['Pitches'].sum(),
                                        x='Rating',
                                        y='Pitches',
                                        category_orders={'Rating': b_grade_fil},
                                        marginal='box',
                                        title='Boulder Grades',
                                        text_auto=True)
            fig_hist_bgrade.update_xaxes(type='category')
            fig_hist_bgrade.update_traces(marker_color = '#BAC9B4')
            col2.plotly_chart(fig_hist_bgrade)
        if anlist_type == 'ToDos':
            fig_hist_rgrade = px.histogram(df_uniq_fil[df_uniq_fil['Route Type'] != 'Boulder'],
                                        x='Rating',
                                        category_orders={'Rating': r_grade_fil},
                                        marginal='box',
                                        title='Route Grades',
                                        text_auto=True)
            fig_hist_rgrade.update_xaxes(type='category')
            fig_hist_rgrade.update_traces(marker_color='#ac7c5c')
            col1.plotly_chart(fig_hist_rgrade)
            fig_hist_bgrade = px.histogram(df_uniq_fil[df_uniq_fil['Route Type'] == 'Boulder'],
                                        x='Rating',
                                        category_orders={'Rating': b_grade_fil},
                                        marginal='box',
                                        title='Boulder Grades',
                                        text_auto=True)
            fig_hist_bgrade.update_xaxes(type='category')
            fig_hist_bgrade.update_traces(marker_color = '#BAC9B4')
            col2.plotly_chart(fig_hist_bgrade)
        fig_hist_mppitches = px.histogram(df_uniq_fil[df_uniq_fil['SP/MP']=='MP'],
                                          x='Pitches',
                                          marginal="box",
                                          title='Multi Pitch Pitch Counts')
        fig_hist_mppitches.update_traces(marker_color = '#779ECC')
        col1.plotly_chart(fig_hist_mppitches)
        fig_hist_length = px.histogram(df_uniq_fil,
                                       x='Length',
                                       marginal='box',
                                       title=' Length')
        fig_hist_length.update_traces(marker_color = '#FF985A')
        fig_hist_length.update_layout(xaxis_title="Length (ft)")
        col2.plotly_chart(fig_hist_length)
        fig_hist_avgstars = px.histogram(df_uniq_fil,
                                         x='Avg Stars',
                                         marginal='box',
                                         title='Stars')
        fig_hist_avgstars.update_traces(marker_color='#ac7c5c')
        col1.plotly_chart(fig_hist_avgstars)
        fig_hist_numticks = px.histogram(df_uniq_fil,
                                         x='Num Ticks',
                                         marginal='box',
                                         title='Number of Ticks')
        fig_hist_numticks.update_traces(marker_color = '#BAC9B4')
        col2.plotly_chart(fig_hist_numticks)
        fig_hist_leadratio = px.histogram(df_uniq_fil,
                                          x='Lead Ratio',
                                          marginal='box',
                                          title='Lead Ratio')
        fig_hist_leadratio.update_traces(marker_color = '#779ECC')
        col1.plotly_chart(fig_hist_leadratio)
        fig_hist_osratio = px.histogram(df_uniq_fil,
                                        x='OS Ratio',
                                        marginal='box',
                                        title='OS Ratio')
        fig_hist_osratio.update_traces(marker_color = '#FF985A')
        col2.plotly_chart(fig_hist_osratio)
        fig_hist_repsend = px.histogram(df_uniq_fil,
                                        x='Repeat Sender Ratio',
                                        marginal='box',
                                        title='Repeat Sender Ratio')
        fig_hist_repsend.update_traces(marker_color='#ac7c5c')
        col1.plotly_chart(fig_hist_repsend)
        fig_hist_att2rp = px.histogram(df_uniq_fil, x='Mean Attempts To RP', marginal='box', title='Mean Attempts to RP')
        fig_hist_att2rp.update_traces(marker_color = '#BAC9B4')
        col2.plotly_chart(fig_hist_att2rp)


        
    ### Route analysis
    st.markdown('---')
    st.markdown("##### Route Analysis")
    if df_uniq_fil.empty:
        st.error("No Unique Route Results With Current Filter Settings")
    else:
        with st.expander("Prefabricated Route Analysis"):
            col1, col2, col3 = st.columns([1,3,1])
            analysis_route_type_option = col1.radio("Route Type", options=['Routes', 'Boulders'], horizontal=True)
            analysis_options_r = ['Rarely Led Routes', 'Rarely Toproped Routes', 'Commonly Onsighted Routes', 'Rarely Onsighted Routes', 'N Most Onsighted Routes Per Grade', 'N Least Onsighted Routes Per Grade', 'Hard to Redpoint', 'Popular To Repeat Send']
            analysis_options_b = ['Commonly Onsighted Boulders', 'Rarely Onsighted Boulders', 'N Most Onsighted Boulders Per Grade', 'N Least Onsighted Boulders Per Grade', 'Popular To Repeat Send']
            if analysis_route_type_option == 'Routes':
                analysis_options = analysis_options_r
            if analysis_route_type_option == 'Boulders':
                analysis_options = analysis_options_b
            analysis_sel = col2.selectbox('Analysis Type', options=analysis_options)
            numN=1
            if analysis_sel in ['N Most Onsighted Routes Per Grade', 'N Least Onsighted Routes Per Grade', 'N Most Onsighted Boulders Per Grade', 'N Least Onsighted Boulders Per Grade']:
                numN = col3.number_input("N =", min_value=1, value=3)
            df_low_lead, df_high_lead, df_high_OS_r, df_low_OS_r, df_nlow_OS_r, df_nhigh_OS_r, df_high_OS_b, df_low_OS_b, df_nlow_OS_b, df_nhigh_OS_b, df_high_RSA_r, df_high_RSR_r, df_high_RSR_b = unique_route_prefabanalysis(df_uniq_fil, selected_rgrade_array, selected_bgrade_array, numN)
            
            if analysis_route_type_option == 'Routes':
                analysis_datasets = [df_low_lead, df_high_lead, df_high_OS_r, df_low_OS_r, df_nlow_OS_r, df_nhigh_OS_r, df_high_RSA_r, df_high_RSR_r]
            if analysis_route_type_option == 'Boulders':
                analysis_datasets = [df_high_OS_b, df_low_OS_b, df_nlow_OS_b, df_nhigh_OS_b, df_high_RSR_b]
            
            analysis_dict = dict(zip(analysis_options, analysis_datasets))
            df_uniq_prefab_pres, gb = aggrid_uniq_format(analysis_dict[analysis_sel])
            AgGrid(data=df_uniq_prefab_pres, 
                height= 800,
                theme='balham',
                gridOptions=gb.build(),
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True)

        with st.expander("Full Data Table: Routes"):
            df_uniq_fil_pres, gb = aggrid_uniq_format(df_uniq_fil)
            AgGrid(data=df_uniq_fil_pres, 
                height= 800,
                theme='balham',
                gridOptions=gb.build(),
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True, key="Full Data: Routes")
    
    ### Tick analysis
    if anlist_type == 'Ticks' and len(date_fil) == 2:
        if df_uniq_fil.empty:
            st.error("No Tick Results With Current Filter Settings")
        else:
            st.markdown('---')
            st.markdown("##### Tick Analysis")
            with st.expander("Tick Pyramid Plots", expanded=True):
                st.markdown('**Note**: These plots only count "sent" routes. Number of attempts to send is recorded inside the block.')
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
                    
            with st.expander("Tick Report", expanded=True):
                fig_breakthrough = px.line(user_ticks_mff[user_ticks_mff['Grade Breakthrough']==True], x='Date', y='Rating', category_orders={'Rating': r_grade_fil[::-1]})
                fig_breakthrough.update_yaxes(type='category')
                st.plotly_chart(fig_breakthrough)
                # Notable Sends
                df_bold_leads, df_impressive_OS, df_woops_falls = tick_report(user_ticks_mff)
                if all([df_bold_leads.empty, df_impressive_OS.empty, df_woops_falls.empty]):
                    st.error("No particularly notable sends, get out there!")
                if not df_bold_leads.empty:
                    st.markdown("""##### [Led route with low lead ratio]
                                While others opted for the top rope, you faced the sharp end.""")
                    df_bold_leads_pres, gb = aggrid_tick_format(df_bold_leads)
                    AgGrid(data=df_bold_leads_pres, 
                        theme='balham',
                        gridOptions=gb.build(),
                        allow_unsafe_jscode=True)
                    st.text('')
                st.markdown('---')
                if not df_impressive_OS.empty:
                    st.markdown("""##### [Onsighted or Flashed route with low OS ratio]  
                                Few others managed to nab the OS/Flash, but you did.""")
                    df_impressive_OS_pres, gb = aggrid_tick_format(df_impressive_OS)
                    AgGrid(data=df_impressive_OS_pres, 
                        theme='balham',
                        gridOptions=gb.build(),
                        allow_unsafe_jscode=True)
                    st.text('')
                st.markdown('---')
                if not df_woops_falls.empty:
                    st.markdown("""##### [Fell/Hung route with high OS ratio]
                                We all fall, but these were your most agregious slip ups.""")
                    df_woops_falls_pres, gb = aggrid_tick_format(df_woops_falls)
                    AgGrid(data=df_woops_falls_pres, 
                        theme='balham',
                        gridOptions=gb.build(),
                        allow_unsafe_jscode=True)
                    st.text('')
                    
            with st.expander("Full Data Table: Ticks"):
                df_ticks_pres, gb = aggrid_tick_format(user_ticks_mff)
                AgGrid(data=df_ticks_pres, 
                    height= 800,
                    theme='balham',
                    gridOptions=gb.build(),
                    allow_unsafe_jscode=True)