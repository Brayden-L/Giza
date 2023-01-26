# Streamlit
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
from aggrid_formats import aggrid_uniq_format, aggrid_tick_format
import streamlit_nested_layout
# Other Project Files
from unique_route_functions import *
from tick_route_functions import tick_merge, flag_notable_ticks, clean_send_plots, tick_report
from long_strs import analysis_explainer
from Main_Page import session_state_init
# Visualization
import plotly.express as px
#General
import os
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta 
import pickle

### Setup
session_state_init()
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
data_source_type_selections = ['Use Session Dataset', 'Select Provided Dataset', 'Upload Pickle File']
# Set data source initial setting appropriately based on whether user scraped
if st.session_state.df_usend_uniq_ticks.empty:
    data_source_type_startind = 1
else:
    data_source_type_startind = 0
# Tick dataset selection
if anlist_type == 'Ticks':
    data_source_type = col1.radio("Data Source Selection", data_source_type_selections, help="placeholder ", horizontal=True, index=data_source_type_startind)
    if data_source_type == 'Use Session Dataset':
        if not st.session_state.df_usend_uniq_ticks.empty:
            unique_routes_df, import_details, user_ticks_df = st.session_state.tick_scrape_output
            col1.info(f"There is a currently loaded dataset saved on this session for user {import_details['username']} from date {import_details['date_scraped']}", icon="ℹ️")
        else:
            col1.info(f"There is currently no Tick dataset saved to this session, you may create one using the scrape tool or use a provided dataset.", icon="ℹ️")
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
# Todos dataset selection
if anlist_type == 'ToDos':
    data_source_type = col1.radio("Data Source Selection", data_source_type_selections, help="placeholder ", horizontal=True, index=data_source_type_startind)
    if data_source_type == 'Use Session Dataset':
        if not st.session_state.df_usend_uniq_todos.empty:
            unique_routes_df, import_details, _ = st.session_state.todo_scrape_output
            col1.info(f"There is a currently loaded dataset saved on this session for user {import_details['username']} from date {import_details['date_scraped']}", icon="ℹ️")
        else:
            col1.info(f"There is currently no ToDo dataset saved to this session, you may create one using the scrape tool or use a provided dataset.", icon="ℹ️")
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
    ### Grade Homogenization
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
        # This block ensures clean grade type assignment from the GUI selection
        gh_key = {'Sign (5.10-)': 'sign', 'Letter (5.10a)': 'letter', 'Sign (V4-)': 'sign', 'Flat (V4)': 'flat', 'Round Evenly By Random': 'even_rand', 'Round Down': 'down', 'Round Up': 'up' }
        grade_settings = [gh_key[route_grade_type], gh_key[route_round_type], gh_key[boulder_grade_type], gh_key[boulder_round_type]]
        unique_routes_df = grade_homo(unique_routes_df, *grade_settings)
        selected_rgrade_array = {'sign': YDS_GRADES_SIGN, 'letter': YDS_GRADES_LETTER}[gh_key[route_grade_type]]
        selected_bgrade_array = {'sign': V_GRADES_SIGN, 'flat': V_GRADES_FLAT}[gh_key[boulder_grade_type]]
    st.markdown('---')

    ### Filtering
    # Filter widget setup
    st.header("Filtering")
    move_fil = st.checkbox("Move Filter to Sidebar", help="Filters in the sidebar remove the need to scroll back and forth if you will be tweaking the filter settings a lot. This is at the expense of cramped visuals.")
    df_uniq_fil = unique_routes_df.copy()
    
    # Allows the filter to be drawn in wide on the page itself, or on the sidebar.
    if move_fil == False:
        fil_cont = st.container()
        r1col1, r1col2, r1col3 = fil_cont.columns([1.75,0.25,2.75])
        r2col1, r2col2, r2col3, r2col4 = fil_cont.columns([1.75,0.25,0.5,2.25])
        r3col1, r3col2 = fil_cont.columns([0.3, 4])
        r4col1, r4col2, r4col3 = fil_cont.columns([1.75,0.25,2.75])
        numtick_cont = r1col1.container()
        routetype_cont = r1col1.container()
        r_grade_cont = r1col3.container()
        b_grade_cont = r1col3.container()
        pitch_cont = r2col1.container()
        date_type_cont = r2col3.container()
        date_cont = r2col4.container()
        loc_tier_cont = r3col1.container()
        loc_cont = r3col2.container()
        style_cont = r4col1.container()
        lead_style_cont = r4col1.container()
        star_cont = r4col3.container()
        length_cont = r4col3.container()
    if move_fil == True:
        numtick_cont = routetype_cont = r_grade_cont = b_grade_cont = pitch_cont = date_type_cont = date_cont = loc_tier_cont = loc_cont = style_cont = lead_style_cont = star_cont = length_cont = st.sidebar.container()
    
    # Tick and Routetype Fil
    routetype_options = df_uniq_fil['Route Type'].unique().tolist()
    numtick_fil = numtick_cont.number_input(label="Minimum Tick Count Cutoff",
                                            value=30,
                                            help="Low tick counts make for poor quality metrics, this filter eliminates entries with tick counts below the cutoff")
    routetype_fil = routetype_cont.multiselect(label="Climb Type",
                                               options=routetype_options,
                                               default=routetype_options)

    # Grade filter
    def grade_filter_align(datalist, orderedlist):
        """Creates an ordered list of unique ratings that exist in entries that belong to the selected grade array """
        full_list = [i for i in orderedlist if i in datalist['Rating'].unique()]
        if full_list == []:
            trunc_full_list = orderedlist
            minval, maxval = orderedlist[0], orderedlist[-1]
        else:
            minval, maxval = full_list[0], full_list[-1]
            trunc_full_list = orderedlist[orderedlist.index(minval) : orderedlist.index(maxval)+1]
        return trunc_full_list, (minval, maxval)
    r_grade_fil, b_grade_fil = [], []

    if len(df_uniq_fil[df_uniq_fil['Rating'].isin(selected_rgrade_array)].index) >= 2: # This checks that there is at least 2 entries of this climb type, otherwise the double slider will error
        r_grade_min, r_grade_max = r_grade_cont.select_slider(label="Route Grade Filter",
                                                              options=grade_filter_align(df_uniq_fil, selected_rgrade_array)[0],
                                                              value=grade_filter_align(df_uniq_fil, selected_rgrade_array)[1])
        r_grade_fil = selected_rgrade_array[selected_rgrade_array.index(r_grade_min) : selected_rgrade_array.index(r_grade_max)+1]
    if len(df_uniq_fil[df_uniq_fil['Rating'].isin(selected_bgrade_array)].index) >= 2:
        b_grade_min, b_grade_max = b_grade_cont.select_slider(label="Boulder Grade Filter",
                                                              options=grade_filter_align(df_uniq_fil, selected_bgrade_array)[0],
                                                              value=grade_filter_align(df_uniq_fil, selected_bgrade_array)[1])
        b_grade_fil = selected_bgrade_array[selected_bgrade_array.index(b_grade_min) : selected_bgrade_array.index(b_grade_max)+1]
    all_grade_fil = r_grade_fil + b_grade_fil

    # Single pitch or multi pitch filter
    pitch_fil_sel = pitch_cont.multiselect(label="Pitch Type",
                                            options=['Single Pitch', 'Multi Pitch'],
                                            default=['Single Pitch', 'Multi Pitch'])
    pitch_fil_transf = {'Single Pitch': 'SP', 'Multi Pitch':'MP'}
    pitch_fil_sel = [pitch_fil_transf[x] for x in pitch_fil_sel]
    
    # Date filter
    if anlist_type == "Ticks":
        date_min = user_ticks_df['Date'].min()
        date_max = user_ticks_df['Date'].max()
        date_fil_type = date_type_cont.radio(label="Date Filter Type",
                                            options=['Date Range', 'Quick Filter'],
                                            index=0)
        if date_fil_type == 'Date Range':
            date_fil = date_cont.date_input(label="Date Filter",
                                            value=(date_min, date_max), 
                                            min_value=date_min,
                                            max_value=date_max)
            date_fil = pd.to_datetime(date_fil)
        if date_fil_type == 'Quick Filter':
            year_list = user_ticks_df['Date'].dt.year.unique().tolist()
            datefil_year_options = [f'Calendar Year: {str(year)}' for year in year_list]
            qdate_fil_widg_dict = {'label': "Quick Date Filter",
                                   'options': datefil_year_options+['Last 1 Month', 'Last 3 Months', 'Last 6 Months', 'Last 12 Months']}
            qdate_fil = date_cont.selectbox(label=qdate_fil_widg_dict['label'],
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
    loc_max_tier = df_uniq_fil['Location'].apply(lambda x: len(x.split('>'))).max()           
    loc_tier = loc_tier_cont.number_input(label="Location Tier",
                                        min_value=1,
                                        max_value=loc_max_tier,
                                        value=1,
                                        help='Location Tier describes how "deep" the location filter goes. Tier1 is typically a state, Tier2 is typically a geographic area or major destination, Tier3 is typically a sub-area, Tier4 and further typically denote crags and subcrags. It is important to note that between major areas these tiers do not often line up.')
    location_list = df_uniq_fil['Location'].apply(lambda x: '>'.join(x.split('>')[0:(loc_tier)])).unique()
    location_list.sort()
    loc_sel = loc_cont.multiselect(label="Location",
                                   options=location_list)
    
    if anlist_type == "Ticks":
        # Style filter
        style_options = user_ticks_df['Style'].unique().tolist()
        style_fil = style_cont.multiselect(label='Style',
                                            options=style_options,
                                            default=style_options,
                                            help='Note that "Flash", "Attempt", and "Send" refer to bouldering styles here')
        # Lead style filter
        lead_style_list = user_ticks_df['Lead Style'].unique().tolist()
        lead_style_fil = lead_style_cont.multiselect(label='Lead Style',
                                                options=lead_style_list,
                                                default=lead_style_list,
                                                help='"nan" is default for non-lead styles such as TR, follow, and all boulders')
    
    # Star filter
    min_stars, max_stars = float(df_uniq_fil['Avg Stars'].min()), float(df_uniq_fil['Avg Stars'].max())
    star_fil_min, star_fil_max = star_cont.slider(label='Avg Stars',
                                                    min_value=min_stars,
                                                    max_value=max_stars,
                                                    value=(min_stars, max_stars))
    
    # Length filter
    min_length, max_length = float(df_uniq_fil['Length'].min()), float(df_uniq_fil['Length'].max())
    length_fil_min, length_fil_max = length_cont.slider(label='Length',
                                                min_value=min_length,
                                                max_value=max_length,
                                                value=(min_length, max_length))
        
    # Apply unique route filters
    # TODO this filter could be a function
    df_uniq_fil = df_uniq_fil[(df_uniq_fil['SP/MP'].isin(pitch_fil_sel)) | (df_uniq_fil['SP/MP'].isna())]
    if not loc_sel == '':
        df_uniq_fil = df_uniq_fil[df_uniq_fil['Location'].str.contains('|'.join(loc_sel))]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Route Type'].isin(routetype_fil)]
    df_uniq_fil = df_uniq_fil[df_uniq_fil['Rating'].isin(all_grade_fil)]
    df_uniq_fil = df_uniq_fil[(df_uniq_fil['Avg Stars'] >= star_fil_min) & (df_uniq_fil['Avg Stars'] <= star_fil_max)]
    df_uniq_fil = df_uniq_fil[(df_uniq_fil['Length'] >= length_fil_min) & (df_uniq_fil['Length'] <= length_fil_max)]
    # df_uniq_fil = df_uniq_fil[df_uniq_fil['Num Ticks'] >= numtick_fil] # numtick filtering disabled
    # Apply tick filters
    if anlist_type == 'Ticks' and len(date_fil) == 2: # The second condition ensures this doesn't try to date filter with an incomplete date filter range
        if df_uniq_fil.empty:
            st.error("No Results From Filter")
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
            # user_ticks_mff = user_ticks_mf[user_ticks_mf['Num Ticks'] >= numtick_fil] # numtick filtering disabled
            user_ticks_mff = user_ticks_mf 
    
    st.markdown('---')
    with st.expander("Overview Plots", expanded=True):
        ### Basic Plots
        # Color sequence definitions
        desert_pallete = ['#779ECC', '#FF7F50', '#C70039', '#9FC0DE', '#F2C894', '#425356', '#ac7c5c']
        style_colordict = {'Lead':'#779ECC', 'TR':'#FF7F50', 'Follow':'#C70039', 'Send':'#9FC0DE', 'Attempt':'#F2C894', 'Flash':'#425356'}
        leadstyle_colordict = {'Fell/Hung':'#779ECC', 'Redpoint':'#FF985A', 'Pinkpoint':'#FFB6C1', 'Flash':'#425356', 'Onsight':'#BAC9B4'}
        routetype_colordict = {'Boulder':'#BAC9B4', 'Sport':'#FF985A', 'Trad':'#779ECC'}
        spmp_colordict = {'SP':'#F2C894', 'MP':'#BAC9B4'}
        baseloc_colordict = dict(zip(df_uniq_fil['Base Location'].value_counts().index, desert_pallete + px.colors.qualitative.Pastel2))
        color_dictdict = {'desert_pallete':desert_pallete, 'style_colordict':style_colordict, 'leadstyle_colordict':leadstyle_colordict, 'routetype_colordict':routetype_colordict, 'spmp_colordict':spmp_colordict, 'baseloc_colordict':baseloc_colordict}
        # Pie Plots
        # TODO this could be a function
        pie_header_cont = st.container()
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        pie_chart_margin = dict(t=35, b=35, l=35, r=35)
        pie_width = pie_height = 300
        if df_uniq_fil.empty:
            st.error("No Results From Filter")
        else:
            if anlist_type == 'Ticks' and len(date_fil) == 2:
                pie_header_cont.markdown('##### Ticked Pitch Count Pie Charts')
                pie_agg = 'Pitches Ticked'
                df_counts_leadstyle = user_ticks_mff.groupby('Style')[pie_agg].sum()
                fig_pie_leadstyle = px.pie(values=df_counts_leadstyle.values,
                                        names=df_counts_leadstyle.index,
                                        color=df_counts_leadstyle.index,
                                        color_discrete_map=style_colordict,
                                        title='Style',
                                        width=pie_width,
                                        height=pie_height)
                fig_pie_leadstyle.update_layout(margin=pie_chart_margin)
                fig_pie_leadstyle.update_traces(hole=.4)
                col4.plotly_chart(fig_pie_leadstyle)

                df_counts_leadstyle = user_ticks_mff.groupby('Lead Style')[pie_agg].sum()
                fig_pie_leadstyle = px.pie(values=df_counts_leadstyle.values,
                                        names=df_counts_leadstyle.index,
                                        color=df_counts_leadstyle.index,
                                        color_discrete_map=leadstyle_colordict,
                                        title='Lead Style',
                                        width=pie_width,
                                        height=pie_height)
                fig_pie_leadstyle.update_layout(margin=pie_chart_margin)
                fig_pie_leadstyle.update_traces(hole=.4)
                col5.plotly_chart(fig_pie_leadstyle)

            if anlist_type == 'ToDos': # Switches aggregate type if todo list
                pie_header_cont.markdown('##### Pitch Count Pie Charts')
                pie_agg = 'Pitches'

            df_counts_routetype = df_uniq_fil.groupby('Route Type')[pie_agg].sum()
            fig_pie_routetype = px.pie(values=df_counts_routetype.values,
                                    names=df_counts_routetype.index,
                                    color=df_counts_routetype.index,
                                    color_discrete_map=routetype_colordict,
                                    title='Climb Type',
                                    width=pie_width,
                                    height=pie_height)
            fig_pie_routetype.update_layout(margin=pie_chart_margin)
            fig_pie_routetype.update_traces(hole=.4)
            col1.plotly_chart(fig_pie_routetype)
            
            df_counts_spmp = df_uniq_fil.groupby('SP/MP')[pie_agg].sum()
            fig_pie_spmp = px.pie(values=df_counts_spmp.values,
                                names=df_counts_spmp.index,
                                color=df_counts_spmp.index,
                                color_discrete_map=spmp_colordict,
                                category_orders={},
                                title="Single or Multi Pitch",
                                width=pie_width,
                                height=pie_height)
            fig_pie_spmp.update_layout(margin=pie_chart_margin)
            fig_pie_spmp.update_traces(hole=.4)
            col2.plotly_chart(fig_pie_spmp)
            
            df_counts_loc1 = df_uniq_fil.groupby(df_uniq_fil['Location'].apply(lambda x: x.split('>')[0]))[pie_agg].sum()
            fig_pie_loc1 = px.pie(values=df_counts_loc1.values,
                                names=df_counts_loc1.index,
                                color_discrete_map=baseloc_colordict, 
                                title='Base Location',
                                width=pie_width,
                                height=pie_height)
            fig_pie_loc1.update_layout(margin=pie_chart_margin)
            fig_pie_loc1.update_traces(hole=.4)
            col3.plotly_chart(fig_pie_loc1)

        st.markdown('---')
        # Histograms
        # TODO: I really don't like the organization of this one, I use ugly if elses to direct to the proper figure draw command. It would be nice if I could compress it a bit.
        st.markdown('##### Histograms')
        if df_uniq_fil.empty:
            pass
        else:
            pvg_part_cont = st.container()
            pvg_graph_cont = st.container()
            pvgcol1, pvgcol2 = pvg_graph_cont.columns([1,1])
            grade_date_part_sel = pvg_part_cont.checkbox("Group Partition", help="Group columns by qualitative metric such as route type", key='PVG Group Partion')
            # The pitches v grades plot is one of the more difficult plots. It has to consider the following conditions:
            # 1. For each of the below conditions, a route and a boulder plot must be made
            # 2. Tick datasets must count total pitches, todo datasets must just count number of climbs
            # 3. There is an option to partition, and the plotting is then different
            # 4. If there is a partition, there is an option to partition by percentage instead of raw value
            if anlist_type == 'Ticks':
                # Tick Pitches V Grades histograms
                grade_date_part_dict = {'Route Type':'Route Type', 'Single or Multi Pitch':'SP/MP', 'Style':'Style', 'Lead Style':'Lead Style', 'Base Location':'Base Location'}
                grade_date_col_dict = {'Route Type':routetype_colordict, 'Single or Multi Pitch':spmp_colordict, 'Style':style_colordict, 'Lead Style':leadstyle_colordict, 'Base Location':baseloc_colordict}
                if grade_date_part_sel == True:
                    grade_date_part_sel = pvg_part_cont.selectbox("Partition By", options=grade_date_col_dict.keys(), key="PVG Partition By")
                    grade_date_perc_sel = pvg_part_cont.checkbox("Configure to Percentage", key="PVG Configure to Percentage")
                    rpitchagg = user_ticks_mff[user_ticks_mff['Route Type'] != 'Boulder'].groupby(by=['Rating', grade_date_part_dict[grade_date_part_sel]], observed=True)['Pitches Ticked'].sum().unstack()
                    bpitchagg = user_ticks_mff[user_ticks_mff['Route Type'] == 'Boulder'].groupby(by=['Rating', grade_date_part_dict[grade_date_part_sel]], observed=True)['Pitches Ticked'].sum().unstack()
                    if grade_date_perc_sel == True:
                        rpitchagg = rpitchagg.div(rpitchagg.sum(axis=1), axis=0)
                        bpitchagg = bpitchagg.div(bpitchagg.sum(axis=1), axis=0)
                    fig_hist_rgrade = px.histogram(rpitchagg,
                                                x=rpitchagg.index,
                                                y=rpitchagg.columns,
                                                color_discrete_map=grade_date_col_dict[grade_date_part_sel],
                                                category_orders={'Rating': r_grade_fil},
                                                marginal='box',
                                                title='Route Grades')
                    fig_hist_rgrade.update_xaxes(type='category')
                    pvgcol1.plotly_chart(fig_hist_rgrade)
                    if not bpitchagg.empty:
                        fig_hist_bgrade = px.histogram(bpitchagg,
                                                    x=bpitchagg.index,
                                                    y=bpitchagg.columns,
                                                    color_discrete_map=grade_date_col_dict[grade_date_part_sel],
                                                    category_orders={'Rating': b_grade_fil},
                                                    marginal='box',
                                                    title='Boulder Grades')
                        fig_hist_bgrade.update_xaxes(type='category')
                        pvgcol2.plotly_chart(fig_hist_bgrade)
                    else:
                        pvgcol2.warning("Bouldering Data Cannot Be Partitioned That Way")
                if grade_date_part_sel == False:
                    rpitchagg = user_ticks_mff[user_ticks_mff['Route Type'] != 'Boulder'].groupby('Rating', as_index=False, observed=True).sum()
                    bpitchagg = user_ticks_mff[user_ticks_mff['Route Type'] == 'Boulder'].groupby('Rating', as_index=False, observed=True).sum()
                    fig_hist_rgrade = px.histogram(rpitchagg,
                                                   x='Rating',
                                                   y='Pitches Ticked',
                                               category_orders={'Rating': r_grade_fil},
                                               marginal='box',
                                               title='Route Grades',
                                               text_auto=True)
                    fig_hist_rgrade.update_xaxes(type='category')
                    fig_hist_rgrade.update_traces(marker_color='#ac7c5c')
                    pvgcol1.plotly_chart(fig_hist_rgrade)
                    fig_hist_bgrade = px.histogram(bpitchagg,
                                                   x='Rating',
                                                   y='Pitches Ticked',
                                                category_orders={'Rating': b_grade_fil},
                                                marginal='box',
                                                title='Boulder Grades',
                                                text_auto=True)
                    fig_hist_bgrade.update_xaxes(type='category')
                    fig_hist_bgrade.update_traces(marker_color = '#BAC9B4')
                    pvgcol2.plotly_chart(fig_hist_bgrade)
            if anlist_type == 'ToDos':
                # Pitches V Grade histograms
                grade_date_part_dict = {'Route Type':'Route Type', 'Single or Multi Pitch':'SP/MP', 'Base Location':'Base Location'}
                grade_date_col_dict = {'Route Type':routetype_colordict, 'Single or Multi Pitch':spmp_colordict, 'Base Location':baseloc_colordict}
                if grade_date_part_sel == True:
                    grade_date_part_sel = pvg_part_cont.selectbox("Partition By", options=grade_date_col_dict.keys(), key="PVG Partition By")
                    grade_date_perc_sel = pvg_part_cont.checkbox("Configure to Percentage", key="PVG Configure to Percentage")
                    rpitchagg = df_uniq_fil[df_uniq_fil['Route Type'] != 'Boulder'].groupby(by=['Rating', grade_date_part_dict[grade_date_part_sel]], observed=True)['Route'].count().unstack()
                    bpitchagg = df_uniq_fil[df_uniq_fil['Route Type'] == 'Boulder'].groupby(by=['Rating', grade_date_part_dict[grade_date_part_sel]], observed=True)['Route'].count().unstack()
                    if grade_date_perc_sel == True:
                        rpitchagg = rpitchagg.div(rpitchagg.sum(axis=1), axis=0)
                        bpitchagg = bpitchagg.div(bpitchagg.sum(axis=1), axis=0)
                    fig_hist_rgrade = px.histogram(rpitchagg,
                                                x=rpitchagg.index,
                                                y=rpitchagg.columns,
                                                color_discrete_map=grade_date_col_dict[grade_date_part_sel],
                                                category_orders={'Rating': r_grade_fil},
                                                marginal='box',
                                                title='Route Grades')
                    fig_hist_rgrade.update_xaxes(type='category')
                    pvgcol1.plotly_chart(fig_hist_rgrade)
                    if bpitchagg.empty:
                        fig_hist_bgrade = px.histogram(bpitchagg,
                                                    x=bpitchagg.index,
                                                    y=bpitchagg.columns,
                                                    color_discrete_map=grade_date_col_dict[grade_date_part_sel],
                                                    category_orders={'Rating': b_grade_fil},
                                                    marginal='box',
                                                    title='Boulder Grades')
                        fig_hist_bgrade.update_xaxes(type='category')
                        pvgcol2.plotly_chart(fig_hist_bgrade)
                    else:
                        pvgcol2.warning("Bouldering Data Cannot Be Partitioned That Way")
                if grade_date_part_sel == False:
                    rpitchagg = df_uniq_fil[df_uniq_fil['Route Type'] != 'Boulder'].groupby('Rating', as_index=False, observed=True).sum()
                    bpitchagg = df_uniq_fil[df_uniq_fil['Route Type'] == 'Boulder'].groupby('Rating', as_index=False, observed=True).sum()
                    fig_hist_rgrade = px.histogram(rpitchagg,
                                                   x='Rating',
                                                   y='Pitches',
                                               category_orders={'Rating': r_grade_fil},
                                               marginal='box',
                                               title='Route Grades',
                                               text_auto=True)
                    fig_hist_rgrade.update_xaxes(type='category')
                    fig_hist_rgrade.update_traces(marker_color='#ac7c5c')
                    pvgcol1.plotly_chart(fig_hist_rgrade)
                    fig_hist_bgrade = px.histogram(bpitchagg,
                                                   x='Rating',
                                                   y='Pitches',
                                                category_orders={'Rating': b_grade_fil},
                                                marginal='box',
                                                title='Boulder Grades',
                                                text_auto=True)
                    fig_hist_bgrade.update_xaxes(type='category')
                    fig_hist_bgrade.update_traces(marker_color = '#BAC9B4')
                    pvgcol2.plotly_chart(fig_hist_bgrade)
            
            # Both Tick and ToDo histograms
            # TODO this could be a function
            col1, col2 = st.columns([1,1])
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
        pass
    else:
        with st.expander("Prefabricated Route Analysis"):
            col1, col2, col3 = st.columns([1,3,1])
            analysis_route_type_option = col1.radio("Route Type", options=['Routes', 'Boulders'], horizontal=True)
            analysis_options_r = ['Rarely Led Routes', 'Rarely Toproped Routes', 'Commonly Onsighted Routes', 'Rarely Onsighted Routes', 'N Most Onsighted Routes Per Grade', 'N Least Onsighted Routes Per Grade', 'Hard to Redpoint', 'Popular To Repeat Send (Classics)']
            analysis_options_b = ['Commonly Onsighted Boulders', 'Rarely Onsighted Boulders', 'N Most Onsighted Boulders Per Grade', 'N Least Onsighted Boulders Per Grade', 'Popular To Repeat Send (Classics)']
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
            pass
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
                # Pitches V Date
                pvd_cont = st.container()
                date_div_dict={'1 Day':'D', '1 Week':'W', '2 Week':'2W', '1 Month':'MS', '3 Month':'3MS', '6 Month':'6MS', '1 Year':'AS'}
                pvd_divtype = st.radio("Time Increment", options=date_div_dict.keys(), index=3, horizontal=True, key='Time Increment Pitches Vs. Date')
                col1, col2 = st.columns([1,1])
                pvd_part_sel = st.checkbox("Group Partition", help="Group columns by qualitative metric such as route type")
                pvd_part_dict = {'Route Type':'Route Type', 'Single or Multi Pitch':'SP/MP', 'Style':'Style', 'Lead Style':'Lead Style', 'Base Location':'Base Location'}
                pvd_col_dict = {'Route Type':routetype_colordict, 'Single or Multi Pitch':spmp_colordict, 'Style':style_colordict, 'Lead Style':leadstyle_colordict, 'Base Location':baseloc_colordict}
                if pvd_part_sel == True:
                    pvd_part_sel = st.selectbox("Pitches Vs. Date Partition By", options=pvd_part_dict.keys())
                    pitch_date_perc_sel = st.checkbox("Configure to Percentage")
                    pvd_dat = user_ticks_mff.groupby(by=[pd.Grouper(key='Date', freq=date_div_dict[pvd_divtype]), pvd_part_dict[pvd_part_sel]])['Pitches Ticked'].sum().fillna(0).unstack()
                    if pitch_date_perc_sel == True:
                        pvd_dat = pvd_dat.div(pvd_dat.sum(axis=1), axis=0)
                    fig_pvd = px.bar(pvd_dat, title='Pitches Vs. Date', color_discrete_map=pvd_col_dict[pvd_part_sel])
                    pvd_cont.plotly_chart(fig_pvd, use_container_width=True)
                else:
                    pvd_dat = user_ticks_mff.groupby(pd.Grouper(key='Date', freq=date_div_dict[pvd_divtype]))['Pitches Ticked'].sum().fillna(0)
                    fig_pvd = px.bar(pvd_dat, title='Pitches Vs. Date')
                    fig_pvd.layout.showlegend = False
                    fig_pvd.update_traces(marker_color=desert_pallete[6])
                    pvd_cont.plotly_chart(fig_pvd, use_container_width=True)
                
                # Route Grade V Date
                gvd_cont = st.container()
                gvd_divtype = st.radio("Time Increment", options=date_div_dict.keys(), index=3, horizontal=True, key='Time Increment Grade Vs. Date')
                gvd_type_sel = st.radio("Routes or Boulders", options=['Route', 'Boulder'], horizontal=True, key='Grade Vs. Date Type')
                gvd_norm_sel = st.checkbox("Normalize by Grade", key='Grade Vs. Date Normalize', help='Default will heatmap comparing all grades, this is useful for discovering "overall volume" and at which grade you were doing volume at. Enabling this will normalize along each grade, giving you a better idea as to when you were performing volume at a given grade.')
                if gvd_type_sel == 'Route':
                    gvd_data = user_ticks_mff[user_ticks_mff['Route Type'] != 'Boulder'].groupby(by=[pd.Grouper(key='Date', freq=date_div_dict[gvd_divtype]), 'Rating'], observed=True)['Rating'].count().fillna(0).unstack().sort_index().transpose()
                    gvd_cat = r_grade_fil[::-1]
                if gvd_type_sel == 'Boulder':
                    gvd_data = user_ticks_mff[user_ticks_mff['Route Type'] == 'Boulder'].groupby(by=[pd.Grouper(key='Date', freq=date_div_dict[gvd_divtype]), 'Rating'], observed=True)['Rating'].count().fillna(0).unstack().sort_index().transpose()
                    gvd_cat = b_grade_fil[::-1]
                gvd_data = gvd_data.reindex(gvd_cat)
                if gvd_norm_sel == True:
                    gvd_data = gvd_data.div(gvd_data.max(axis=1), axis=0)
                fig_gvd = px.imshow(gvd_data, title='Route Grade Vs. Date', color_continuous_scale='RdBu_r')
                fig_gvd.update_yaxes(type='category', showgrid=False)
                gvd_cont.plotly_chart(fig_gvd, use_container_width=True)
                                
                col1, col2 = st.columns([1,1])
                # Grade Breakthrough
                fig_breakthrough = px.scatter(user_ticks_mff[user_ticks_mff['Grade Breakthrough']==True], x='Date', y='Rating', category_orders={'Rating': r_grade_fil[::-1]}, hover_data=["Route", "Location"], title="Grade Breakthrough")
                fig_breakthrough.update_yaxes(type='category')
                fig_breakthrough.update_traces(marker_size=12, marker_color=desert_pallete[4])
                col1.plotly_chart(fig_breakthrough)
                
                # Risky Climbs
                fig_risk = px.scatter(user_ticks_mff[(~user_ticks_mff['Risk'].isna()) & (user_ticks_mff['Style'] == 'Lead')], x='Date', y='Rating', title='Risky Climbs', category_orders={'Rating': r_grade_fil[::-1]}, hover_data=["Risk", "Route", "Location", "Style", "Lead Style"])
                fig_risk.update_yaxes(type='category')
                fig_risk.update_traces(marker_size=12, marker_color=desert_pallete[5])
                col2.plotly_chart(fig_risk)
                
                # Notable Sends
                st.markdown('---')
                st.subheader("Notable Sends")
                df_bold_leads, df_impressive_OS, df_woops_falls = tick_report(user_ticks_mff) #func
                if all([df_bold_leads.empty, df_impressive_OS.empty, df_woops_falls.empty]):
                    st.error("No particularly notable sends, get out there!")
                col1,col2 = st.columns([1,5])
                notablesend_sel = col1.selectbox("Notable Send Type", options=['Bold Leads', 'Impressive Onsights', 'Whoops Falls'])
                if notablesend_sel == 'Bold Leads' and not df_bold_leads.empty:
                    notablesend_text = """##### [Led route with low lead ratio]
                                While others opted for the top rope, you faced the sharp end."""
                    notablesend_dat = df_bold_leads
                if notablesend_sel == 'Impressive Onsights' and not df_impressive_OS.empty:
                    notablesend_text = """##### [Onsighted or Flashed route with low OS ratio]  
                                Few others managed to nab the OS/Flash, but you did."""
                    notablesend_dat = df_impressive_OS
                if notablesend_sel =='Whoops Falls' and not df_woops_falls.empty:
                    notablesend_text = """##### [Fell/Hung route with high OS ratio]
                                We all fall, but these were your most agregious slip ups."""
                    notablesend_dat = df_woops_falls
                
                st.markdown(notablesend_text)
                notablesend_dat_pres, gb = aggrid_tick_format(notablesend_dat)
                AgGrid(data=notablesend_dat_pres, 
                    theme='balham',
                    gridOptions=gb.build(),
                    allow_unsafe_jscode=True)
                    
            with st.expander("Full Data Table: Ticks"):
                df_ticks_pres, gb = aggrid_tick_format(user_ticks_mff)
                AgGrid(data=df_ticks_pres, 
                    height= 800,
                    theme='balham',
                    gridOptions=gb.build(),
                    allow_unsafe_jscode=True)