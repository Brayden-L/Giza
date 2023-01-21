# These functions are intended to be applied solely to tick type datasets.

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import streamlit as st

def tick_uniq_clean(df_source):
    """
    Creatres a unique dataframe of routes from a tick list. It has some irrelevant columns left over that should be removed.
    input df, return df.
    """
    df_output = df_source.drop_duplicates(subset="Route ID")
    col_list = ['Date', 'Notes', 'Your Stars', 'Style', 'Lead Style']
    for col in col_list:
        if col in df_output.columns:
            df_output.drop(columns=col, inplace=True)
    return df_output

@st.experimental_memo
def tick_merge(df_ticks, df_uniq):
    """Merges unique route metrics with a tick list.

    Parameters
    ----------
    df_ticks : df
        dataframe of user ticks
    df_uniq : df
        dataframe of unique routes

    Returns
    -------
    df_out
        dataframe of merged dataframes
    """
    # merge unique dataframe details to user data frame. This will delete the user data frame of length and rating information and replace it with that from the unique dataframe
    if 'Rating' in df_ticks.columns:
        df_ticks.drop(columns=['Rating'], inplace=True)
    if 'Length' in df_ticks.columns:
        df_ticks.drop(columns=['Length'], inplace=True)
    df_uniq_colkeep = ['Route ID', 'Pitches', 'Lead Ratio', 'Num Ticks', 'Num Tickers', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio', 'Rating', 'Length', 'SP/MP']
    df_out = df_ticks.merge(df_uniq[df_uniq_colkeep], how='left', on='Route ID')
    return df_out

@st.experimental_memo
def flag_notable_ticks(df_source):
    """ Takes a tick list dataframe, adds tag columns to track notable sends.

    Parameters
    ----------
    df_source : df
        input dataframe, should be a merged tick list with unique route analytics already added.

    Returns
    -------
    df
        output dataframe
    """
    from unique_route_functions import count_attempt2rp
    from constants import CLEAN_SEND_FIRST, CLEAN_SEND_WORKED
    #Initialize columns
    df_source.insert(len(df_source.columns),'Flash/Onsight',None)
    df_source.insert(len(df_source.columns),'Worked Clean',None)
    df_source.insert(len(df_source.columns),'Grade Breakthrough',None)
    df_source.insert(len(df_source.columns),'Attempts',float('NaN'))

    # We want to tag important climbs, namely flash/onsights, worked clean routes and grade breakthroughs.
    # Tag climbs that were flash/onsight
    df_source.loc[df_source['Lead Style'].isin(CLEAN_SEND_FIRST), 'Flash/Onsight'] = True

    # Create column that flags climbs that were worked. There are three possibilities to consider. We want 1 and 2.
    # 1. Worked to clean send, no further sends.
    # 2. Worked to clean send, additional attempts.
    # 3. Sent clean first try, additional attempts.
    df_all_dupes = df_source[df_source.duplicated(subset="Route ID", keep=False)] # First we filter for all duplicate entries.
    df_all_worked = df_all_dupes.groupby('Route ID').filter(lambda x: ~x['Lead Style'].isin(CLEAN_SEND_FIRST).any()) # Then we remove all groups which have a lead style of flash or onsight to eliminate group 3.
    df_worked_clean_rponly = df_all_worked[df_all_worked.groupby('Route ID')['Lead Style'].apply(lambda x: x.isin(CLEAN_SEND_WORKED))] # fell/hungs and TRs remain, so we take ticks from CLEAN_SEND_WORKED.
    if not df_worked_clean_rponly.empty:
        df_worked_clean_earliest = df_worked_clean_rponly.loc[df_worked_clean_rponly.groupby('Route ID')['Date'].idxmin()] # Use only the earliest redpoint to correctly identify the first redpoint.
        df_source.loc[df_worked_clean_earliest.index.values, "Worked Clean"] = True

    # Flag grade breakthrough ticks
    dfbreakthr = df_source[(df_source['Flash/Onsight'] == True) | (df_source['Worked Clean'] == True)]
    breakthrough_indexes = dfbreakthr.groupby('Rating', observed=True)['Date'].idxmin().values
    df_source.loc[breakthrough_indexes, "Grade Breakthrough"] = True
    df_source.loc[breakthrough_indexes]

    # Count number of attempts to send
    # Assumes no style lead ticks are fell/hung
    # Assumes rp/pp with no prior tick history has one prior attempt
    # Counts clean ticks with multiple pitches as total attempts. It also counts fell/hung, and TR with multiple pitches as multiple attempts.
    # !!! This will falsely identify a single pitch climb broken into multiple pitches as two attempts, there isn't really a good way to detect this.
    df_worked_clean = df_all_worked.groupby('Route ID').filter(lambda x: x['Lead Style'].isin(CLEAN_SEND_WORKED).any()) # Filters out worked climbs that were never done clean.
    if not df_worked_clean.empty:
        num_to_send = df_worked_clean.groupby('Route ID').apply(lambda x: count_attempt2rp(x, x.iloc[0]['Pitches']))
        num_to_send.rename('Attempts', inplace=True)
        matched_attempts = df_source[df_source['Worked Clean'] == True].merge(num_to_send, left_on="Route ID", right_index=True,  how="left")
        matched_attempts.index = df_source[df_source['Worked Clean'] == True].index # I'm dumb and this is the best way I could find to get my index to remain
        df_source.loc[matched_attempts.index, "Attempts"] = matched_attempts.iloc[:,-1]
        df_source.loc[df_source['Attempts'] == 1, 'Attempts'] = 2 # This assumes rp with 1 pitch and no prior ticks had one prior attempt
    else:
        df_source['Attempts'] = None
    return df_source

@st.experimental_memo
def clean_send_plots(df_source, selected_rgrade_array, r_grade_fil, selected_bgrade_array, b_grade_fil):
    """Creates a pyramid and grade vs time plot based on clean sends for routes and boulders seperately

    Parameters
    ----------
    df_source : df
        source dataframe
    selected_rgrade_array : list
        list of route grades relevant to source dataframe
    r_grade_fil : list
        filtered list of relevant route grades
    selected_bgrade_array : list
        list of boulder grades relevant to source dataframe
    b_grade_fil : list
        filtered list of relevant boulder grades

    Returns
    -------
    fig1, fig2, fig3, fig4
        plotly figures
    """
    from constants import CLEAN_SEND_FIRST, CLEAN_SEND, YDS_GRADES_FULL, V_GRADES_FULL
    import plotly.express as px

    # Create dataframe of clean sends for analysis
    df_usendf_r = df_source[df_source['Rating'].isin(YDS_GRADES_FULL)]
    df_usendf_r.loc[df_usendf_r['Lead Style'].isin(CLEAN_SEND_FIRST), "Attempts"] = '' # Optionally change attempts from blank to 1 or other
    df_clean_sends_r = df_usendf_r[(df_usendf_r['Lead Style'].isin(CLEAN_SEND))]
    # df_clean_sends_r = df_clean_sends_r.loc[df_clean_sends_r.groupby('Route ID')['Date'].idxmin()] # Optionally ignore subequent clean sends
    df_clean_sends_r['Date Formatted'] = df_clean_sends_r['Date'].dt.date

    df_usendf_b = df_source[df_source['Rating'].isin(V_GRADES_FULL)]
    df_usendf_b.loc[df_usendf_b['Lead Style'].isin(CLEAN_SEND_FIRST), "Attempts"] = '' # Optionally change attempts from blank to 1 or other
    df_clean_sends_b = df_usendf_b[(df_usendf_b['Style'].isin(CLEAN_SEND))]
    # df_clean_sends_b = df_clean_sends_b.loc[df_clean_sends_r.groupby('Route ID')['Date'].idxmin()] # Optionally ignore subequent clean sends
    df_clean_sends_b['Date Formatted'] = df_clean_sends_b['Date'].dt.date

    rpy_fig = px.bar(df_clean_sends_r, y="Rating", orientation='h', height=45*len(r_grade_fil), category_orders={"Rating": selected_rgrade_array[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars'])
    rpy_fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':20}, title={'text':'<b>Climbing Pyramid</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Number of Routes Sent'}, yaxis={'title': '', 'type': 'category'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
    rpy_fig.update_traces(marker_color='#ac7c5c', marker_line_width=2, marker_line_color='#8b532d', textposition="inside", insidetextanchor='middle', textfont={"color": 'White', "size": 12, "family": 'Arial Black'},  hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

    rhistory_fig = px.scatter(df_clean_sends_r, "Date", "Rating", height=45*len(r_grade_fil), category_orders={"Rating": selected_rgrade_array[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars'])
    rhistory_fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':20}, title={'text':'<b>Send by Date</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Date'}, yaxis={'title': '', 'type': 'category'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
    rhistory_fig.update_traces(marker_symbol='square', marker_color='#ac7c5c', marker_size=25, marker_line_width=2, marker_line_color='#8b532d', textfont={"color": 'White', "size": 12}, hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

    bpyr_fig = px.bar(df_clean_sends_b, y="Rating", orientation='h', height=45*len(b_grade_fil), category_orders={"Rating": selected_bgrade_array[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars'])
    bpyr_fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':18}, title={'text':'<b>Climbing Pyramid</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Number of Problems Sent'}, yaxis={'title': '', 'type': 'category'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
    bpyr_fig.update_traces(marker_color='#ac7c5c', marker_line_width=2, marker_line_color='#8b532d', textposition="inside", insidetextanchor='middle', textfont={"color": 'White', "size": 12, "family": 'Arial Black'},  hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

    bhistory_fig = px.scatter(df_clean_sends_b, "Date", "Rating", height=45*len(b_grade_fil), category_orders={"Rating": selected_bgrade_array[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars'])
    bhistory_fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':20}, title={'text':'<b>Send by Date</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Date'}, yaxis={'title': '', 'type': 'category'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
    bhistory_fig.update_traces(marker_symbol='square', marker_color='#ac7c5c', marker_size=25, marker_line_width=2, marker_line_color='#8b532d', textfont={"color": 'White', "size": 12}, hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

    return rpy_fig, rhistory_fig, bpyr_fig, bhistory_fig

def tick_report(df_source):
    """Generates dataframes of routes filtered by some metric

    Parameters
    ----------
    df_source : df
        input dataframe

    Returns
    -------
    df_bold_leads, df_impressive_OS, df_woops_falls
        output dataframes
    """
    # User led something rarely led
    df_bold_leads = df_source[(df_source['Lead Ratio'] < 0.4) & (df_source['Style'] == 'Lead') & (df_source['Route Type'] != 'Boulder')].sort_values(by='Lead Ratio', ascending=True)
    # User onsighted something rarely onsighted
    df_impressive_OS = df_source[(df_source['OS Ratio'] < 0.35) & (df_source['Flash/Onsight'] == True) & (df_source['Route Type'] != 'Boulder')].sort_values(by='OS Ratio')
    # User fell on something rarely fallen on
    df_woops_falls = df_source[(df_source['OS Ratio'] > 0.8) & (df_source['Style'] == 'Lead') & (df_source['Lead Style'] == 'Fell/Hung') & (df_source['Route Type'] != 'Boulder')].sort_values(by='OS Ratio', ascending=True)
    return df_bold_leads, df_impressive_OS, df_woops_falls