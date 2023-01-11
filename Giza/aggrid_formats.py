import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

def aggrid_uniq_format(df_source):
    fulldat_orgcol_uniq = ['Route Link', 'Pitches', 'Route Type', 'Rating', 'Avg Stars', 'Length', 'Num Ticks', 'Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio', 'Location' ]
    fulldat_floatcol_uniq = ['Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio']
    df_source[fulldat_floatcol_uniq] = df_source[fulldat_floatcol_uniq].applymap(lambda x: float('{:,.2f}'.format(x)) if pd.notnull(x) else np.nan) # the if else here retains np.nans blank presentation
    df_source['Route Link'] = df_source.apply(lambda row: f"""<a target="_blank" href="{row['URL']}">{row['Route']}</a>""", axis=1)
    gb = GridOptionsBuilder.from_dataframe(df_source[fulldat_orgcol_uniq])
    gb.configure_side_bar()
    gb.configure_default_column(wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_columns(fulldat_orgcol_uniq[1:-1], width=90, type='leftAligned')
    gb.configure_columns(fulldat_floatcol_uniq, type=["numericColumn","numberColumnFilter"])
    gb.configure_column('Route Link',
                        header_name='Route',
                        pinned=True,
                        cellRenderer=JsCode('''function(params) {return params.value}'''))
    df_pres = df_source[fulldat_orgcol_uniq]
    return df_pres, gb

def aggrid_tick_format(df_source):
    fulldat_orgcol_ticks = ['Route', 'Date Formatted', 'Pitches', 'Route Type', 'Style', 'Lead Style', 'Rating', 'Avg Stars', 'Length', 'Num Ticks', 'Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio', 'Flash/Onsight', 'Worked Clean', 'Grade Breakthrough', 'Attempts', 'Location' ]
    fulldat_floatcol_ticks = ['Lead Ratio', 'OS Ratio', 'Mean Attempts To RP', 'Repeat Sender Ratio']
    df_source[fulldat_floatcol_ticks] = df_source[fulldat_floatcol_ticks].applymap(lambda x: float('{:,.2f}'.format(x)) if pd.notnull(x) else np.nan) # the if else here retains np.nans blank presentation
    df_source['Route'] = df_source.apply(lambda row: f"""<a target="_blank" href="{row['URL']}">{row['Route']}</a>""", axis=1)
    gb = GridOptionsBuilder.from_dataframe(df_source[fulldat_orgcol_ticks])
    gb.configure_side_bar()
    gb.configure_default_column(wrapHeaderText=True, autoHeaderHeight=True)
    gb.configure_columns(fulldat_orgcol_ticks[1:-1], width=90, type='leftAligned')
    gb.configure_columns(fulldat_floatcol_ticks, type=["numericColumn","numberColumnFilter"])
    gb.configure_column('Date Formatted', header_name='Date')
    gb.configure_column('Route',
                        pinned=True,
                        cellRenderer=JsCode('''function(params) {return params.value}'''))
    df_pres = df_source[fulldat_orgcol_ticks]
    return df_pres, gb