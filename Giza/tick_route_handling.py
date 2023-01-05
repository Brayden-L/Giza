import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype

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
    df_ticks.drop(columns=['Rating', 'Length'], inplace=True)
    df_out = df_ticks.merge(df_uniq[['Route ID', 'Pitches', 'Lead Ratio', 'Num Ticks', 'Num Tickers', 'OS Ratio', 'Mean Attempts To RP', 'Rating', 'Length']], how='left', on='Route ID')
    return df_out

# #Initialize columns
# df_usendm.insert(len(df_usendm.columns),'Flash/Onsight',None)
# df_usendm.insert(len(df_usendm.columns),'Worked Clean',None)
# df_usendm.insert(len(df_usendm.columns),'Grade Breakthrough',None)
# df_usendm.insert(len(df_usendm.columns),'Attempts',float('NaN'))

# # We want to tag important climbs, namely flash/onsights, worked clean routes and grade breakthroughs.
# # Tag climbs that were flash/onsight
# df_usendm.loc[df_usendm['Lead Style'].isin(CLEAN_SEND_FIRST), 'Flash/Onsight'] = True

# # Create column that flags climbs that were worked. There are three possibilities to consider. We want 1 and 2.
# # 1. Worked to clean send, no further sends.
# # 2. Worked to clean send, additional attempts.
# # 3. Sent clean first try, additional attempts.
# df_all_dupes = df_usendm[df_usendm.duplicated(subset="Route ID", keep=False)] # First we filter for all duplicate entries.
# df_all_worked = df_all_dupes.groupby('Route ID').filter(lambda x: ~x['Lead Style'].isin(CLEAN_SEND_FIRST).any()) # Then we remove all groups which have a lead style of flash or onsight to eliminate group 3.
# df_worked_clean_rponly = df_all_worked[df_all_worked.groupby('Route ID')['Lead Style'].apply(lambda x: x.isin(CLEAN_SEND_WORKED))] # fell/hungs and TRs remain, so we take ticks from CLEAN_SEND_WORKED.
# df_worked_clean_earliest = df_worked_clean_rponly.loc[df_worked_clean_rponly.groupby('Route ID')['Date'].idxmin()] # Use only the earliest redpoint to correctly identify the first redpoint.
# df_usendm.loc[df_worked_clean_earliest.index.values, "Worked Clean"] = True

# # Flag grade breakthrough ticks
# dfbreakthr = df_usendm[(df_usendm['Flash/Onsight'] == True) | (df_usendm['Worked Clean'] == True)]
# breakthrough_indexes = dfbreakthr.groupby('Rating', observed=True)['Date'].idxmin().values
# df_usendm.loc[breakthrough_indexes, "Grade Breakthrough"] = True
# df_usendm.loc[breakthrough_indexes]

# # Count number of attempts to send
# # Assumes no style lead ticks are fell/hung
# # Assumes rp/pp with no prior tick history has one prior attempt
# # Counts clean ticks with multiple pitches as total attempts. It also counts fell/hung, and TR with multiple pitches as multiple attempts.
# # !!! This will falsely identify a single pitch climb broken into multiple pitches as two attempts, there isn't really a good way to detect this.
# df_worked_clean = df_all_worked.groupby('Route ID').filter(lambda x: x['Lead Style'].isin(CLEAN_SEND_WORKED).any()) # Filters out worked climbs that were never done clean.
# num_to_send = df_worked_clean.groupby('Route ID').apply(lambda x: count_attempt2rp(x, x.iloc[0]['Pitches']))
# num_to_send.rename('Attempts', inplace=True)
# matched_attempts = df_usendm[df_usendm['Worked Clean'] == True].merge(num_to_send, on="Route ID", how="left")
# matched_attempts.index = df_usendm[df_usendm['Worked Clean'] == True].index # I'm dumb and this is the best way I could find to get my index to remain
# df_usendm.loc[matched_attempts.index, "Attempts"] = matched_attempts.iloc[:,-1]
# df_usendm.loc[df_usendm['Attempts'] == 1, 'Attempts'] = 2 # This assumes rp with 1 pitch and no prior ticks had one prior attempt

# # User led something rarely led
# df_bold_leads = df_usendm[(df_usendm['Num Ticks'] >= 30) & (df_usendm['Lead Ratio'] < 0.4) & (df_usendm['Style'] == 'Lead') & (df_usendm['Route Type'] != 'Boulder')].sort_values(by='Lead Ratio', ascending=False)
# # User onsighted something rarely onsighted
# df_impressive_OS = df_usendm[(df_usendm['Num Ticks'] >= 30) & (df_usendm['OS Ratio'] < 0.35) & (df_usendm['Flash/Onsight'] == True) & (df_usendm['Route Type'] != 'Boulder')].sort_values(by='OS Ratio')
# # User fell on something rarely fallen on
# df_woops_falls = df_usendm[(df_usendm['Num Ticks'] >= 30) & (df_usendm['OS Ratio'] > 0.8) & (df_usendm['Style'] == 'Lead') & (df_usendm['Lead Style'] == 'Fell/Hung') & (df_usendm['Route Type'] != 'Boulder')].sort_values(by='OS Ratio')

# # Set visualization settings accordant to modifications and filters.
# if grade_settings[0] == 'letter':
#     ryaxorder = YDS_GRADES_LETTER
# if grade_settings[0] == 'sign':
#     ryaxorder = YDS_GRADES_SIGN

# if grade_settings[2] == 'flat':
#     byaxorder = V_GRADES_FLAT
# if grade_settings[2] == 'sign':
#     byaxorder = V_GRADES_SIGN

# # Create dataframe of clean sends for analysis
# df_usendf_r.loc[df_usendf_r['Lead Style'].isin(CLEAN_SEND_FIRST), "Attempts"] = '' # Optionally change attempts from blank to 1 or other
# df_clean_sends_r = df_usendf_r[(df_usendf_r['Lead Style'].isin(CLEAN_SEND))]
# # df_clean_sends_r = df_clean_sends_r.loc[df_clean_sends_r.groupby('Route ID')['Date'].idxmin()] # Optionally ignore subequent clean sends
# df_clean_sends_r['Date Formatted'] = df_clean_sends_r['Date'].dt.date

# df_usendf_b.loc[df_usendf_b['Lead Style'].isin(CLEAN_SEND_FIRST), "Attempts"] = '' # Optionally change attempts from blank to 1 or other
# df_clean_sends_b = df_usendf_b[(df_usendf_b['Style'].isin(CLEAN_SEND))]
# # df_clean_sends_b = df_clean_sends_b.loc[df_clean_sends_r.groupby('Route ID')['Date'].idxmin()] # Optionally ignore subequent clean sends
# df_clean_sends_b['Date Formatted'] = df_clean_sends_b['Date'].dt.date

# fig = px.bar(df_clean_sends_r, y="Rating", orientation='h', category_orders={"Rating": ryaxorder[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars']) # The [::-1] is an inverse slice
# fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':20}, title={'text':'<b>Climbing Pyramid</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Number of Routes Sent'}, yaxis={'title': 'Grade'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
# fig.update_traces(marker_color='#7A4F25', textposition = "inside", textfont={"color": 'White', "size": 12, "family": 'Arial Black'},  hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')
# # fig.update_traces(marker_color=list(map(lambda x: '#7A4F25' if (x=='') else '#bf9315', df_clean_sends['Attempts'])), textposition = "inside",  hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

# fig = px.scatter(df_clean_sends_r, "Date", "Rating", category_orders={"Rating": ryaxorder[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars'])
# fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':20}, title={'text':'<b>Send by Date</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Date'}, yaxis={'title': 'Grade'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
# fig.update_traces(marker_symbol='square', marker_color='#7A4F25', marker_size=20, marker_line_width=2, marker_line_color='black', textfont={"color": 'White', "size": 12}, hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

# fig = px.bar(df_clean_sends_b, y="Rating", orientation='h', category_orders={"Rating": byaxorder[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars']) # The [::-1] is an inverse slice
# fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':18}, title={'text':'<b>Climbing Pyramid</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Number of Problems Sent'}, yaxis={'title': 'Grade'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
# fig.update_traces(marker_color='#7A4F25', textposition = "inside", textfont={"color": 'White', "size": 12, "family": 'Arial Black'},  hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')
# # fig.update_traces(marker_color=list(map(lambda x: '#7A4F25' if (x=='') else '#bf9315', df_clean_sends['Attempts'])), textposition = "inside",  hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')

# fig = px.scatter(df_clean_sends_b, "Date", "Rating", category_orders={"Rating": byaxorder[::-1]}, text='Attempts', custom_data=['Route', 'Date Formatted', 'Location', 'Length', 'Avg Stars'])
# fig.update_layout(font={'family':'Courier New', 'color':'black', 'size':20}, title={'text':'<b>Send by Date</b>', 'x':0.5, 'font_size':30}, xaxis={'title': 'Date'}, yaxis={'title': 'Grade'}, paper_bgcolor='#ece5dc', plot_bgcolor='#F5D3A5', bargap=0)
# fig.update_traces(marker_symbol='square', marker_color='#7A4F25', marker_size=20, marker_line_width=2, marker_line_color='black', textfont={"color": 'White', "size": 12}, hovertemplate='Name: %{customdata[0]}<br>Date: %{customdata[1]}<br>Location: %{customdata[2]}<br>Length: %{customdata[3]}ft<br>Avg Stars: %{customdata[4]}')