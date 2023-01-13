# %%
# Data Science Related
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff

# Scraping Related
# import grequests # You will get errors if grequests is not above requests
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import lxml
import cchardet
import re

# General
import pyinputplus as pyip
import datetime as dt
from datetime import datetime
from stqdm import stqdm
import pickle
import random
import math 
import string

# Initializations
stqdm.pandas()

# %%
# Defines Project Wide Constants

YDS_GRADES_FULL = ['5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-', '5.9', '5.9+',
                   '5.10a', '5.10-', '5.10a/b', '5.10b', '5.10', '5.10b/c', '5.10c', '5.10+', '5.10c/d', '5.10d', '5.11a', '5.11-', '5.11a/b', '5.11b', '5.11', '5.11b/c', '5.11c', '5.11+', '5.11c/d', '5.11d',
                   '5.12a', '5.12-', '5.12a/b', '5.12b', '5.12', '5.12b/c', '5.12c', '5.12+', '5.12c/d', '5.12d', '5.13a', '5.13-', '5.13a/b', '5.13b', '5.13', '5.13b/c', '5.13c', '5.13+', '5.13c/d', '5.13d',
                   '5.14a', '5.14-', '5.14a/b', '5.14b', '5.14', '5.14b/c', '5.14c', '5.14+', '5.14c/d', '5.14d', '5.15a', '5.15-', '5.15a/b', '5.15b', '5.15', '5.15b/c' '5.15c', '5.15+', '5.15c/d', '5.15d']
YDS_GRADES_LETTER = ['5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9', '5.10a', '5.10b', '5.10c', '5.10d', '5.11a', '5.11b', '5.11c', '5.11d',
                     '5.12a', '5.12b', '5.12c', '5.12d', '5.13a', '5.13b', '5.13c', '5.13d', '5.14a', '5.14b', '5.14c', '5.14d', '5.15a', '5.15b', '5.15c', '5.15d']
YDS_GRADES_SIGN = ['5.0', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.7+', '5.8-', '5.8', '5.8+', '5.9-', '5.9', '5.9+', '5.10-', '5.10', '5.10+',
                   '5.11-', '5.11', '5.11+', '5.12-', '5.12', '5.12+', '5.13-', '5.13', '5.13+', '5.14-', '5.14', '5.14+', '5.15-', '5.15', '5.15+']

V_GRADES_FULL = ['V-easy', 'V0-', 'V0', 'V0+', 'V0-1', 'V1-', 'V1', 'V1+', 'V1-2', 'V2-', 'V2', 'V2+', 'V2-3', 'V3-', 'V3', 'V3+', 'V3-4', 'V4-', 'V4', 'V4+', 'V4-5', 'V5-', 'V5', 'V5+', 'V5-6',
                 'V6-', 'V6', 'V6+', 'V6-7', 'V7-', 'V7', 'V7+', 'V7-8', 'V8-', 'V8', 'V8+', 'V8-9', 'V9-', 'V9', 'V9+', 'V9-10', 'V10-', 'V10', 'V10+', 'V10-11', 'V11-', 'V11', 'V11+', 'V11-12',
                 'V12-', 'V12', 'V12+', 'V12-13', 'V13-', 'V13', 'V13+', 'V13-14', 'V14-', 'V14', 'V14+', 'V14-15', 'V15-', 'V15', 'V15+', 'V15-16', 'V16-', 'V16', 'V16+', 'V16-17', 'V17-', 'V17']
V_GRADES_SIGN = ['V-easy', 'V0-', 'V0', 'V0+', 'V1-', 'V1', 'V1+', 'V2-', 'V2', 'V2+', 'V3-', 'V3', 'V3+', 'V4-', 'V4', 'V4+', 'V5-', 'V5', 'V5+', 'V6-', 'V6', 'V6+', 'V7-', 'V7', 'V7+', 'V8-', 'V8', 'V8+',
                 'V9-', 'V9', 'V9+', 'V10-', 'V10', 'V10+', 'V11-', 'V11', 'V11+', 'V12-', 'V12', 'V12+', 'V13-', 'V13', 'V13+', 'V14-', 'V14', 'V14+', 'V15-', 'V15', 'V15+', 'V16-', 'V16', 'V16+', 'V17-', 'V17']
V_GRADES_FLAT = ['V-easy', 'V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7',
                 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17']

GRADES_SUPER = YDS_GRADES_FULL + V_GRADES_FULL

RISK_GRADES = ['PG', 'PG13', 'R', 'X']
ROUTE_TYPES = ['Boulder', 'Sport', 'Trad']

CLEAN_SEND = ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Send']
CLEAN_SEND_FIRST = ['Onsight', 'Flash']
CLEAN_SEND_WORKED = ['Redpoint', 'Pinkpoint']
TICK_OPTIONS = ['Solo', 'TR', 'Follow', 'Lead', 'Fell/Hung',
                'Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Send', 'Attempt']

# Roped grade homogenization
# Letter
rgrademoderatemap = {'5.6-': '5.6', '5.6+': '5.6', '5.7-': '5.7',
                     '5.7+': '5.7', '5.8-': '5.8', '5.8+': '5.8', '5.9-': '5.9', '5.9+': '5.9'}
rgradedownmap = {'5.10a/b': '5.10a', '5.10-': '5.10a', '5.10b/c': '5.10b', '5.10': '5.10b', '5.10c/d': '5.10c', '5.10+': '5.10c',
                 '5.11a/b': '5.11a', '5.11-': '5.11a', '5.11b/c': '5.11b', '5.11': '5.11b', '5.11c/d': '5.11c', '5.11+': '5.11c',
                 '5.12a/b': '5.12a', '5.12-': '5.12a', '5.12b/c': '5.12b', '5.12': '5.12b', '5.12c/d': '5.12c', '5.12+': '5.12c',
                 '5.13a/b': '5.13a', '5.13-': '5.13a', '5.13b/c': '5.13b', '5.13': '5.13b', '5.13c/d': '5.13c', '5.13+': '5.13c',
                 '5.14a/b': '5.14a', '5.14-': '5.14a', '5.14b/c': '5.14b', '5.14': '5.14b', '5.14c/d': '5.14c', '5.14+': '5.14c',
                 '5.15a/b': '5.15a', '5.15-': '5.15a', '5.15b/c': '5.15b', '5.15': '5.15b', '5.15c/d': '5.15c', '5.15+': '5.15c',
                 }
rgradeupmap = {'5.10a/b': '5.10b', '5.10-': '5.10b', '5.10b/c': '5.10c', '5.10': '5.10c', '5.10c/d': '5.10d', '5.10+': '5.10d',
               '5.11a/b': '5.11b', '5.11-': '5.11b', '5.11b/c': '5.11c', '5.11': '5.11c', '5.11c/d': '5.11d', '5.11+': '5.11d',
               '5.12a/b': '5.12b', '5.12-': '5.12b', '5.12b/c': '5.12c', '5.12': '5.12c', '5.12c/d': '5.12d', '5.12+': '5.12d',
               '5.13a/b': '5.13b', '5.13-': '5.13b', '5.13b/c': '5.13c', '5.13': '5.13c', '5.13c/d': '5.13d', '5.13+': '5.13d',
               '5.14a/b': '5.14b', '5.14-': '5.14b', '5.14b/c': '5.14c', '5.14': '5.14c', '5.14c/d': '5.14d', '5.14+': '5.14d',
               '5.15a/b': '5.15b', '5.15-': '5.15b', '5.15b/c': '5.15c', '5.15': '5.15c', '5.15c/d': '5.15d', '5.15+': '5.15d',
               }

# Sign
rgradecompmap = {'5.10a': '5.10-', '5.10a/b': '5.10-', '5.10b': '5.10', '5.10c': '5.10', '5.10b/c': '5.10', '5.10d': '5.10+', '5.10c/d': '5.10+',
                 '5.11a': '5.11-', '5.11a/b': '5.11-', '5.11b': '5.11', '5.11c': '5.10', '5.11b/c': '5.11', '5.11d': '5.11+', '5.11c/d': '5.11+',
                 '5.12a': '5.12-', '5.12a/b': '5.12-', '5.12b': '5.12', '5.12c': '5.10', '5.12b/c': '5.12', '5.12d': '5.12+', '5.12c/d': '5.12+',
                 '5.13a': '5.13-', '5.13a/b': '5.13-', '5.13b': '5.13', '5.13c': '5.10', '5.130b/c': '5.13', '5.13d': '5.13+', '5.13c/d': '5.13+',
                 '5.14a': '5.14-', '5.14a/b': '5.14-', '5.14b': '5.14', '5.14c': '5.10', '5.14b/c': '5.14', '5.14d': '5.14+', '5.14c/d': '5.14+',
                 }

# Boulder grade homogenization
# Flat
bgradedownmap1 = {'V0-1': 'V0', 'V1-2': 'V1', 'V2-3': 'V2', 'V3-4': 'V3', 'V4-5': 'V4', 'V5-6': 'V5', 'V6-7': 'V6', 'V7-8': 'V7', 'V8-9': 'V8', 'V9-10': 'V9', 'V10-11': 'V10', 'V11-12': 'V11',
                  'V12-13': 'V12', 'V13-14': 'V13', 'V14-15': 'V14', 'V15-16': 'V15', 'V16-17': 'V16'}
bgradeupmap1 = {'V0-1': 'V1', 'V1-2': 'V2', 'V2-3': 'V3', 'V3-4': 'V4', 'V4-5': 'V5', 'V5-6': 'V6', 'V6-7': 'V7', 'V7-8': 'V8', 'V8-9': 'V9', 'V9-10': 'V10', 'V10-11': 'V11', 'V11-12': 'V12',
                'V12-13': 'V13', 'V13-14': 'V14', 'V14-15': 'V15', 'V15-16': 'V16', 'V16-17': 'V17'}
bgradeconmap1 = {'V0-': 'V0', 'V0+': 'V0', 'V1-': 'V1', 'V1+': 'V1', 'V2-': 'V2', 'V2+': 'V2', 'V3-': 'V3', 'V3+': 'V3', 'V4-': 'V4', 'V4+': 'V4', 'V5-': 'V5', 'V5+': 'V5', 'V6-': 'V6', 'V6+': 'V6', 'V7-': 'V7', 'V7+': 'V7', 'V8-': 'V8', 'V8+': 'V8',
                 'V9-': 'V9', 'V9+': 'V9', 'V10-': 'V10', 'V10+': 'V10', 'V11-': 'V11', 'V11+': 'V11', 'V12-': 'V12', 'V12+': 'V12', 'V13-': 'V13', 'V13+': 'V13', 'V14-': 'V14', 'V14+': 'V14', 'V15-': 'V15', 'V15+': 'V15', 'V16-': 'V16', 'V16+': 'V16',
                 'V17-': 'V17', 'V17+': 'V17'}
# Sign
bgradedownmap2 = {'V0-1': 'V0+', 'V1-2': 'V1+', 'V2-3': 'V2+', 'V3-4': 'V3+', 'V4-5': 'V4+', 'V5-6': 'V5+', 'V6-7': 'V6+', 'V7-8': 'V7+', 'V8-9': 'V8+', 'V9-10': 'V9+', 'V10-11': 'V10+', 'V11-12': 'V11+', 'V12-13': 'V12+', 'V13-14': 'V13+',
                  'V14-15': 'V14+', 'V15-16': 'V15+', 'V16-17': 'V16+'}
bgradeupmap2 = {'V0-1': 'V1-', 'V1-2': 'V2-', 'V2-3': 'V3-', 'V3-4': 'V4-', 'V4-5': 'V5-', 'V5-6': 'V6-', 'V6-7': 'V7-', 'V7-8': 'V8-', 'V8-9': 'V9-', 'V9-10-': 'V10', 'V10-11': 'V11-', 'V11-12': 'V12-', 'V12-13': 'V13-', 'V13-14': 'V14-',
                'V14-15': 'V15-', 'V15-16': 'V16-', 'V16-17': 'V17-'}

# %%
def download_routelist(upload_type, link):
    """
    Downloads a tick or todo list from the MP website.

    Parameters
    ----------
    upload_type : str {todo, tick} 
        A given user has a todo and a tick list. Choose one.
    link : str
        Link to user. Of format - https://www.mountainproject.com/user/########/name/

    Returns
    -------
    df : df
        Downloaded dataframe.
    err_text : str
        Customized text for http errors
    """
    try:
        df = pd.read_csv(f'{link}/{upload_type}-export')
        error_text = False
    except Exception as err:
        df = False
        print(err)
        if 'https://www.mountainproject.com/user/' not in link:
            error_text = """Link must be of form "https://www.mountainproject.com/user/" """
        elif err.code == 401:
            error_text = "Unauthenticated (Error: 401)"
        elif err.code == 403:
            error_text = "Unauthorized (Error: 403)"
        elif err.code == 404:
            error_text = "Invalid Link (Error: 404)"
        elif err.code in range(500, 511) :
            error_text = "Server Error Please Try Again"
        else:
            error_text = "Error"
    return df, error_text


# %%
def data_standardize(df_source):
    """
    Basic data cleanup for route df. Assigns correct datatype, creates unique route ID column, prepares "rating" for further analysis, handles bad data in "route type".
    Input df, return df.
    """
    
    # Some cleanup is only necessary on the tick list, and not the todo list. Only the tick list has a Date column.
    if 'Date' in df_source.columns:
        df_source['Date'] = pd.to_datetime(df_source['Date']) # 'Date' to datetype
        df_source['Date Formatted'] = df_source['Date'].dt.strftime('%Y-%m-%d')
        df_source.rename(columns={'Pitches': 'Pitches Ticked'}, inplace=True) # Pitches relabeled to Pitches Ticked
        df_source['Notes'] = df_source['Notes'].apply(lambda x: str(x).replace('&#39;',"'")) # Apostrophe's are html coded in the notes section for some reason.

    # Remove all blank, aid, ice, snow, TR only, and trad/boulder climbing route types as they are not relevant.
    df_source = df_source[df_source['Route Type'].str.contains(r'Aid|Ice|Snow') != True]
    df_source = df_source[df_source['Route Type'].str.fullmatch(r'TR') != True] #if this is just a partial match it will detech "trad" too!
    df_source = df_source[df_source['Route Type'].str.contains(r'Trad') & df_source['Route Type'].str.contains(r'Boulder') != True]
    df_source = df_source[df_source['Route Type'].notnull()]
    
    # Some routes have no grade, this seems to be a bug with Mountain Project
    df_source = df_source[df_source['Rating'].notnull()]

    # "trad, sport" goes to "trad". If it uses gear it's trad!
    df_source.loc[df_source['Route Type'].str.contains(r'Trad') & df_source['Route Type'].str.contains(r'Sport'), 'Route Type'] = 'Trad'

    # "x, alpine" and "x, tr" goes to "x" Alpine and tr tags are not useful.
    def rem_route_el_from_list(ousted, seperator):
        el_rem_subset = df_source['Route Type'].str.contains(ousted) == True
        df_source.loc[el_rem_subset, 'Route Type'] = df_source[el_rem_subset]['Route Type'].apply(lambda row: [val for val in row.split(seperator) if val != ousted]).apply(lambda x: ", ".join(x))

    rem_route_el_from_list('Alpine', ', ')
    rem_route_el_from_list('TR', ', ')

    routetype_cat = CategoricalDtype(categories=ROUTE_TYPES)
    df_source['Route Type'] = df_source['Route Type'].astype(routetype_cat)
    
    # Extract route unique identifier from URL and create a new column for it.
    if 'Route ID' not in df_source.columns:
        df_source.insert(len(df_source.columns),'Route ID','')
    df_source['Route ID'] = df_source['URL'].apply(lambda x: int(x.split('/')[4]))

    # Change YDS-Vgrade combos to just Vgrade. They are most likely boulders, so a bouldering grade is relevant.
    subset = df_source['Rating'].apply(lambda row: [val for val in row.split() if val in V_GRADES_FULL]).astype(bool)  & df_source['Rating'].apply(lambda row: [val for val in row.split() if val in YDS_GRADES_FULL]).astype(bool) == True
    df_source.loc[subset, 'Rating'] = df_source[subset]['Rating'].apply(lambda x: x.split()[1])
    df_source.loc[subset, 'Route Type'] = 'Boulder'

    # Seperate risk rating to new column
    if 'Rating' not in df_source.columns:
        df_source.insert(df_source.columns.get_loc('Rating')+1,'Risk','')
    risk_cat = CategoricalDtype(categories=RISK_GRADES, ordered=True)
    df_source['Risk'] = df_source['Rating'].apply(lambda row: [val for val in row.split() if val in RISK_GRADES]).apply(lambda x: "".join(x)).astype(risk_cat)
    # Reduce Rating column to just rating
    rating_cat = CategoricalDtype(categories=GRADES_SUPER)
    df_source['Rating'] = df_source['Rating'].apply(lambda row: [val for val in row.split()][0]).astype(rating_cat)

    # Create original rating and length archive to compare against or undo changes.
    if 'Original Rating' not in df_source.columns:
        df_source.insert(df_source.columns.get_loc('Rating'),'Original Rating',df_source['Rating'])
        
    # Your Stars NaN type is -1 for some reason, change it to an actual nonetype
    df_source.loc[df_source['Your Stars'] == -1, 'Your Stars'] = None

    return df_source

# %%
def route_length_fixer(df_source, input_type):
    """"
    Fixes route length outliers and missing values.
    
    Parameters:
    -----------
    df_source : df
        df of routes
    input_type : str {"express", "manual"}
        Use default values or input manually
    
    Returns:
    --------
    df_source : df
        Original df with fully defined route lengths
    """
### Handle route length outliers and NaNs
    # Define roped and bouldering specific subset
    roped_subset = (df_source['Route Type'] == 'Sport') | (df_source['Route Type'] == 'Trad')
    boulder_subset = (df_source['Route Type'] == 'Boulder')

    ROPED_MIN_LENGTH = 15
    ROPED_MAX_LENGTH = 4500 #"Trango Towers" are 4,300' tall
    ROPED_DEFAULT_LENGTH = 70
    BOULDER_MIN_LENGTH = 1
    BOULDER_MAX_LENGTH = 55 #"Too Tall to Fall" is 50'
    BOULDER_DEFAULT_LENGTH = 12

    # Fix outliers
    def fix_length_outliers(dataframe, subset, minlength, maxlength, deflength):
        length_outliers = dataframe[subset][(dataframe[subset]['Length'] <= minlength) | (dataframe[subset]['Length'] >= maxlength)]
        for loop_count, (index, data) in enumerate(length_outliers.iterrows()):
            if input_type == 'express':
                updated_length = deflength
            if input_type == 'manual':
                updated_length = pyip.inputNum(f"[{loop_count+1}/{length_outliers.shape[0]}] Outlier Detected, Possible Bad Info. Input Corrected Length for\nRoute: {data['Route']}\nLocation: {'>'.join(data['Location'].split('>')[-3:])}\nCurrently: {data['Length']}ft\n", min=minlength, max=maxlength)
            dataframe.at[index, 'Length'] = updated_length
        return dataframe

    # Fill empty route lengths
    def fill_length_empties(dataframe, subset, minlength, maxlength, deflength):
        length_missing = dataframe[subset][(dataframe[subset]['Length'].isnull()) | (dataframe[subset]['Length'] == 0)]
        for loop_count, (index, data) in enumerate(length_missing.iterrows()):
            if input_type == 'express':
                updated_length = deflength
            if input_type == 'manual':
                updated_length = pyip.inputNum(f"[{loop_count+1}/{length_missing.shape[0]}] Input Estimated Length for\nRoute: {data['Route']}\nLocation: {'>'.join(data['Location'].split('>')[-3:])}\n", min=minlength, max=maxlength)
            dataframe.at[index, 'Length'] = updated_length
        return dataframe

    df_source = fix_length_outliers(df_source, roped_subset, ROPED_MIN_LENGTH, ROPED_MAX_LENGTH, ROPED_DEFAULT_LENGTH)
    df_source = fill_length_empties(df_source, roped_subset, ROPED_MIN_LENGTH, ROPED_MAX_LENGTH, ROPED_DEFAULT_LENGTH)
    df_source = fix_length_outliers(df_source, boulder_subset, BOULDER_MIN_LENGTH, BOULDER_MAX_LENGTH, BOULDER_DEFAULT_LENGTH)
    df_source = fill_length_empties(df_source, boulder_subset, BOULDER_MIN_LENGTH, BOULDER_MAX_LENGTH, BOULDER_DEFAULT_LENGTH)

    return df_source

# %%
def grade_homo(df_source, r_type, r_direction, b_type, b_direction):
    """
    Reassigns grades to a single YDS or Vgrade schema.
    
    Parameters
    ----------
    df_source : df
        Original route df.
    r_type : str {letter, sign}
        YDS letter or sign style grades.
    r_direction : str {up, down, even_rand, manual}
        Unused if r_type='letter'. Which way to assign grades. even_rand rounds a randomly selected half up and the randomly remaining half down.
    b_type : str {flat, sign}
        Vgrade flat grades or include sign grades.
    b_direction : str {up, down, even_rand, manual}
        Same as r_direction
    
    Return
    ------
    df_source : df
        Original df with grade homogenization
    """
    rating_isolate = df_source['Original Rating'].apply(lambda row: [val for val in row.split()][0]) # This is a fail-safe to ensure we are only looking at the part of the rating we care about, not risk or sub-ratings.

    # Reset 'Rating' column so this mapping can be re-run
    df_source["Rating"] = df_source["Original Rating"]

    #Roped Grades
    def grademoderate():
        grade_change_subset = rating_isolate.isin(list(rgrademoderatemap.keys()))
        df_source.loc[grade_change_subset, 'Rating'] = df_source.loc[grade_change_subset]['Original Rating'].map(rgrademoderatemap)

    def grade_split(upmap, downmap):
        grade_change_subset = rating_isolate.isin(list(upmap.keys()))
        grade_change_subset_df = df_source[grade_change_subset]
        for grade in grade_change_subset_df['Original Rating'].unique():
            to_change = grade_change_subset_df[grade_change_subset_df['Original Rating'] == grade]
            changed_up = to_change.sample(frac=0.5)['Original Rating'].map(upmap)
            df_source.loc[changed_up.index, 'Rating'] = changed_up
        grade_change_subset = rating_isolate.isin(list(downmap.keys()))
        grade_change_subset_df = df_source[grade_change_subset]
        for grade in grade_change_subset_df['Original Rating'].unique():
            to_change = grade_change_subset_df[grade_change_subset_df['Original Rating'] == grade]
            changed_down = to_change['Original Rating'].map(downmap)
            df_source.loc[changed_down.index, 'Rating'] = changed_down

    if r_type == 'sign':
        grade_change_subset = rating_isolate.isin(list(rgradecompmap.keys()))
        df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(rgradecompmap)
    else:
        if r_direction == 'up':
            grademoderate()
            grade_change_subset = rating_isolate.isin(list(rgradeupmap.keys()))
            df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(rgradeupmap)
        if r_direction == 'down':
            grademoderate()
            grade_change_subset = rating_isolate.isin(list(rgradedownmap.keys()))
            df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(rgradedownmap)
        if r_direction == 'even_rand':
            grademoderate()
            grade_split(rgradeupmap,rgradedownmap)
        if r_direction == 'manual':
            needs_grade_corr = df_source[rating_isolate.isin(list(rgrademoderatemap.keys()) + list(rgradedownmap.keys()))]
            for loop_count, (index, data) in enumerate(needs_grade_corr.iterrows()):
                updated_grade = pyip.inputChoice(prompt=f"[{loop_count+1}/{needs_grade_corr.shape[0]}] Input Grade Correction For: {data['Route'].title()}:\n", choices=YDS_GRADES_LETTER)
                df_source.at[index, 'Rating'] = updated_grade

    #Boulder Grades
    if b_type == 'flat':
        # Remove all + and - grades
        grade_change_subset = rating_isolate.isin(list(bgradeconmap1.keys()))
        df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(bgradeconmap1)

        if b_direction == 'up':
            grade_change_subset = rating_isolate.isin(list(bgradeupmap1.keys()))
            df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(bgradeupmap1)
        if b_direction == 'down':
            grade_change_subset = rating_isolate.isin(list(bgradedownmap1.keys()))
            df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(bgradedownmap1)
        if b_direction == 'even_rand':
            grade_split(bgradeupmap1,bgradedownmap1)
        if b_direction == 'manual':
            needs_grade_corr = df_source[rating_isolate.isin(list(bgradedownmap1.keys()))]
            for loop_count, (index, data) in enumerate(needs_grade_corr.iterrows()):
                updated_grade = pyip.inputChoice(prompt=f"[{loop_count+1}/{needs_grade_corr.shape[0]}] Input Grade Correction For: {data['Route'].title()}:\n", choices=V_GRADES_FLAT)
                df_source.at[index, 'Rating'] = updated_grade

    if b_type =='sign':
        if b_direction == 'up':
            grade_change_subset = rating_isolate.isin(list(bgradeupmap2.keys()))
            df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(bgradeupmap2)
        if b_direction == 'down':
            grade_change_subset = rating_isolate.isin(list(bgradedownmap2.keys()))
            df_source.loc[grade_change_subset, 'Rating'] = df_source[grade_change_subset]['Original Rating'].map(bgradedownmap2)
        if b_direction == 'even_rand':
            grade_split(bgradeupmap2,bgradedownmap2)
        if b_direction == 'manual':
            needs_grade_corr = df_source[rating_isolate.isin(list(bgradedownmap2.keys()))]
            for loop_count, (index, data) in enumerate(needs_grade_corr.iterrows()):
                updated_grade = pyip.inputChoice(prompt=f"[{loop_count+1}/{needs_grade_corr.shape[0]}] Input Grade Correction For: {data['Route'].title()}:\n", choices=V_GRADES_FLAT)
                df_source.at[index, 'Rating'] = updated_grade
    
    return df_source

# %%
def user_uniq_clean(df_source):
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

# %%
def routescrape_syncro(df_source, retries=3):
    """
    Downloads the route page and stat page for each entry.
    It is suggested you pass this a list of unique routes so it does not download redundantly.
    Input df, return df with two new columns of request.Reponse objects.
    """
    s = requests.Session()
    retries = Retry(total=retries, backoff_factor=1, status_forcelist=tuple(range(400, 600)))
    s.mount('http://', HTTPAdapter(max_retries=retries))
    
    def insert_str_to_address(url, insert_phrase):
        str_list = url.split('/')
        str_list.insert(4, insert_phrase)
        return '/'.join(str_list)

    def page_download(url):
        try:
            res = s.get(url)
        except Exception as e:
            print(url)
            print(e)
            res = None
        
        return res
    stqdm.pandas(desc="(1/5) Scraping Mainpages")
    if 'Re Mainpage' not in df_source.columns: # Creates column if it does not yet exist, otherwise it will try to download any that errored last attempt
        df_source.insert(len(df_source.columns),'Re Mainpage',None)
        df_source['Re Mainpage'] = df_source['URL'].progress_apply(page_download)
    else:
        subset = df_source['Re Mainpage'].isna()
        df_source.loc[subset, 'Re Mainpage'] = df_source.loc[subset, 'URL'].progress_apply(page_download)
    stqdm.pandas(desc="(2/5) Scraping Statpages")
    if 'Re Statpage' not in df_source.columns:
        df_source.insert(len(df_source.columns),'Re Statpage',None)
        df_source['Re Statpage'] = df_source['URL'].progress_apply(lambda x: page_download(insert_str_to_address(x, 'stats')))
    else:
        subset = df_source['Re Statpage'].isna()
        df_source.loc[subset, 'Re Statpage'] = df_source.loc[subset, 'URL'].progress_apply(page_download)
        
    return(df_source)

# %%
def extract_default_pitch(df_source):
    """
    Analyze the mainpage for listed default pitch lengths.
    Necessary for a user's tick export as it includes pitches as their own recorded pitch count. Not required for ToDo exports as it correctly lists the "official" pitch count.
    Input df, return df with new Pitches column of integer type.
    """
    def get_pitches(res):
        if res is None:
            return None
        else:
            soup = BeautifulSoup(res.text, 'lxml')
            route_type_text = str(soup.find(class_="description-details").find_all('td')[1])
            pitch_search = re.search(r'\d+ pitches',route_type_text)
            if isinstance(pitch_search, type(None)):
                num_pitches = 1
            else:
                num_pitches = pitch_search.group(0).split(' ')[0]
            return int(num_pitches)
    stqdm.pandas(desc="(3/5) Extracting Default Pitches")
    df_source['Pitches'] = df_source['Re Mainpage'].progress_apply(get_pitches)
    return df_source

# %%
def assign_spmp(df_source):
    """Tags single pitch and multipitch climbs

    Parameters
    ----------
    df_source : df
        input df

    Returns
    -------
    df
        output df with new SP and MP tag column
    """
    if 'SP/MP' not in df_source.columns:
        df_source['SP/MP'] = None
    df_source.loc[(df_source['Route Type'].isin(['Sport', 'Trad'])) & (df_source['Pitches'] == 1), 'SP/MP'] = 'SP'
    df_source.loc[(df_source['Route Type'].isin(['Sport', 'Trad'])) & (df_source['Pitches'] > 1), 'SP/MP'] = 'MP'
    df_source['SP/MP'] = pd.Categorical(df_source['SP/MP'])
    return df_source

# %%
def extract_tick_details(df_source):
    """
    Extracts a df of tick details for each route from its statpage.
    Input df, return df with new column of df type. (Each row has it's own sub-dataframe).
    """    
    def get_tick_details(res):
        """
        Creates a df of tick details from a statpage.
        
        Parameters
        ----------
        res : request.response object
        
        Return
        ------
        Username : str
            Name of user who ticked
        User Link : url
            url link of user who ticked
        Date : Pandas datetime
            date of tick
        Pitches ticked : int
            Number of pitches in tick
        Style : str
            Lead, TR, Follow, Attempt etc.
        Lead Style : str
            Onsight, Flash, Fell/Hung, Redpoint, Pinkpoint etc.
        Comment : str
            Tick comment
        """
        name = []
        namelink = []
        entrydate = []
        pitches = []
        style = []
        lead_style = []
        comment = []
        if res is None:
            d = None
        else:
            soup = BeautifulSoup(res.text, 'lxml')
            # print(soup.select("#route-stats > div.row.pt-main-content > div > h1")) # Tells you which page is being scraped, useful for debugging
            try:
                blocks = list(soup.select("#route-stats > div:nth-child(2) > div:nth-last-child(1)")[0].find_all('tr'))
            except Exception:
                blocks = []
            for x in blocks:
                soup = BeautifulSoup(str(x), 'lxml')
                entries = soup.find_all('div', attrs={'class': None})
                for entry in entries:
                    entrytext = entry.text
                    try:
                        name.append(soup.find('a').text.strip())
                    except Exception:
                        name.append('')
                        
                    try:
                        namelink.append(soup.find('a')['href'].strip())
                    except Exception:
                        namelink.append('')
                    
                    try:
                        date_search = [re.search(r'\w{3}\s\d{1,2},\s\d{4}', entrytext)]
                        entrydate.append([subresult.group(0).strip() if subresult else '' for subresult in date_search][0]) # pulls match text if match object is not none
                    except Exception:
                        entrydate.append('')
                    
                    try:
                        pitches_search = [re.search(r'·([^.]+\s(pitches))', entrytext)] # regex for starting at · and ending at first period only if it includes the word "pitches"
                        pitchesinterm = [subresult.group(0) if subresult else '' for subresult in pitches_search]
                        pitches.append([int(re.search(r'\d+', subresult).group(0).strip()) if subresult else 1 for subresult in pitchesinterm][0]) # take just the digit of the string
                    except Exception:
                        pitches.append(1)
                    
                    try:
                        style_search = [re.search(r"(Solo|TR|Follow|Lead|Send|Attempt|Flash)", entrytext)]
                        style_val = [subresult.group(0).strip() if subresult else '' for subresult in style_search][0] # I have a conditional in the comment search that depends on this so I made it a separate variable
                        style.append(style_val)
                    except Exception:
                        style.append('')
                    
                    try:
                        if style_val != '':
                            lead_style_search = [re.search(r"/([^.]+)", entrytext)]
                            lead_style.append([subresult.group(0)[2:].strip() if subresult else '' for subresult in lead_style_search][0])
                        else:
                            lead_style.append('')
                    except Exception:
                        lead_style.append('')
                    
                    try:
                        if style_val != '':
                            comment_search = [re.search(r"(Solo|TR|Follow|Lead).*", entrytext)]
                            commentinterm = ([subresult.group(0) if subresult else '' for subresult in comment_search])
                            comment.append([re.search(r"\..*", subresult).group(0)[2:].strip() if subresult else '' for subresult in commentinterm][0])
                        else:
                            comment_search = [re.search(r"·(.*)", entrytext)] # If no style comment then entire phrase is the comment.
                            comment.append([subresult.group(0)[2:].strip() if subresult else '' for subresult in comment_search][0])
                    except Exception:
                        comment.append('')
            # print (len(name),len(namelink),len(entrydate),len(pitches),len(style),len(lead_style),len(comment))
            # print (name,namelink,entrydate,pitches,style,lead_style,comment)
            d = pd.DataFrame({'Username' : name, "User Link" : namelink, "Date": entrydate, "Pitches Ticked": pitches, "Style": style, "Lead Style": lead_style, "Comment": comment})
            # One last possible error correction, an oomlot injected a "/" into lead style and the regex incidentally detected it
            d.loc[~d['Lead Style'].isin(TICK_OPTIONS), 'Lead Style'] = ''
            # Recast columns to correct data type
            d['Date'] = pd.to_datetime(d['Date'], errors = 'coerce')
            d['Style'] = pd.Categorical(d['Style'])
            d['Lead Style'] = pd.Categorical(d['Lead Style'])
        return d

    stqdm.pandas(desc="(4/5) Constructing Tick Dataframe")
    df_source['Route Ticks']=df_source['Re Statpage'].progress_apply(get_tick_details)
    return(df_source)

# %%
def unpack_style(routeticks, colref, pitchnum):
    """
    Returns a flat list of all non-null values in a given tick df column.
    pitchnum allows us to handle multipitch ticks differently than singlepitch.
    
    Parameters
    ----------
    routeticks : df
        df of ticks for a specific route
    colref : str
        column name to unpack from
    pitchnum : int
        number of pitches in route
    
    Return
    ------
    flat_list : list of strings
        Flat list of style strings
    """
    nest_list = []
    for row in routeticks.index:
        styleval = routeticks[colref][row]
        if pitchnum == 1:
            if styleval in CLEAN_SEND: # clean sends with multiple ticks are assumed to be fell/hung attempts up to that clean send.
                nest_list.append([routeticks[colref][row]])
                nest_list.append((routeticks['Pitches Ticked'][row]-1)*['Fell/Hung'])
            else:
                nest_list.append(routeticks['Pitches Ticked'][row]*[routeticks[colref][row]])
        if pitchnum > 1:
            nest_list.append([routeticks[colref][row]])
    flat_list = [num for sublist in nest_list for num in sublist]
    return flat_list


def is_prior_sender(df_source):
    """Takes a dataframe of a single given users ticks, outputs str of user if user did not onsight/flash prior to RP

    Parameters
    ----------
    df_source : df
        A given users ticks

    Returns
    -------
    str
        Returns name of user if valid, returns None if user has prior onsight/flash
    """
    clean_send_dates = df_source[df_source['Lead Style'].isin(CLEAN_SEND_WORKED)]['Date']
    if clean_send_dates.isna().any(): # Some ticks have NaT improper dates, ignore the ticker with bad data
        return None
    else:
        firstrp_index = clean_send_dates.idxmin()
        already_sent_bool = any(df_source.loc[firstrp_index::]['Lead Style'].isin(CLEAN_SEND_FIRST))
        valid_sender = not already_sent_bool
        if valid_sender:
            return df_source.iloc[0]['Username']
        else:
            return None


def count_attempt2rp(df_source, pitchnum):
    """Takes a dataframe of a single given users ticks, outputs number of attempts to first rp

    Parameters
    ----------
    df_source : df
        A given users ticks

    Returns
    -------
    int
        Number of attempts to first redpoint
    """
    firstrp_cutoff = df_source[df_source['Lead Style'].isin(CLEAN_SEND_WORKED)]['Date'].idxmin() # Find index of first rp
    # If multipitch, we count ticks. If singlepitch we count number of total ticked pitches.
    if pitchnum > 1:
        nattempts = df_source.sort_values('Date', ascending=False).loc[firstrp_cutoff::]['Pitches Ticked'].count()
    if pitchnum == 1:
        nattempts = df_source.sort_values('Date', ascending=False).loc[firstrp_cutoff::]['Pitches Ticked'].sum() # Sum all pitches attempted prior to that
    return nattempts


def analyze_tick_counts(routeticks, pitchnum):
    """
    Analyzes tick sub-df.
    
    Parameters
    ----------
    df_source : df
        Source dataframe
    
    Return
    ------
    num_ticks : int
        Number of ticks
    num_tickers : int
        Number of users who ticked
    lead_ratio : float
        Ratio of lead ticks to total ticks with non-null style type
    os_ratio : float
        Ratio of onsight plus flash ticks to total ticks with non-null lead-style type
    tick_counts : series
        series of count of each type of tick
    """
    if (routeticks is None) or (len(routeticks.index) == 0): # If list is unavailable or empty
        num_ticks = num_tickers = lead_ratio = os_ratio = repeat_senders = rpnattempt_mean = tick_counts = float('NaN')
    else:
        # Get number of ticks and tickers
        num_ticks = len(routeticks.index)
        num_tickers = routeticks['Username'].nunique()
        
        # Create tick metrics
        tick_cat = CategoricalDtype(categories=TICK_OPTIONS)
        tick_type_list = pd.Series(unpack_style(routeticks, 'Style', pitchnum) + unpack_style(routeticks, 'Lead Style', pitchnum), dtype=tick_cat)
        tick_counts = tick_type_list.value_counts()
        repeat_senders = routeticks[routeticks['Lead Style'].isin(CLEAN_SEND)].groupby('Username')['Lead Style'].count().mean() # It is assumed that each clean send gets its own tick.
        
        rp_unames = routeticks[routeticks['Lead Style'].isin(CLEAN_SEND_WORKED)]['Username'] # List of names of those who rp'd
        if rp_unames.empty: # if the list exists, but has no redpointers, we want to assign NaN
            rpnattempt_mean = float('NaN')
        else:
            df_rpers_only = routeticks[routeticks['Username'].isin(rp_unames)]
            rpers_list = df_rpers_only.groupby('Username').apply(is_prior_sender) # Get list of users who did not onsight/flash prior to RP
            df_rpers_only = df_rpers_only[df_rpers_only['Username'].isin(rpers_list)] # Remove RPers with a prior onsight
            attempt_list = df_rpers_only.groupby('Username').apply(lambda x: count_attempt2rp(x, pitchnum)).values.tolist() # Count num attempts of each each user.
            rpnattempt_mean = np.mean(attempt_list)
        
        lead_ratio = tick_counts['Lead']/(tick_counts['Follow'] + tick_counts['TR'] + tick_counts['Lead'])
        os_ratio = (tick_counts['Onsight'] + tick_counts['Flash']) / (tick_counts['Onsight'] + tick_counts['Flash'] + tick_counts['Fell/Hung'] + tick_counts['Redpoint'] + tick_counts['Pinkpoint'] + tick_counts['Attempt'] + tick_counts['Send'])
    return pd.Series([num_ticks, num_tickers, lead_ratio, os_ratio, repeat_senders, rpnattempt_mean, tick_counts])


def tick_analysis(df_source):
    """
    Adds tick analysis columns to dataframe

    Parameters
    ----------
    df_source : df
        input df

    Returns
    -------
    df
        same df with added columns
    """
    ### Analyzes tick sub dataframe to create meaningful metrics.
    
    stqdm.pandas(desc="(5/5) Constructing Tick Analytics")
    df_source[['Num Ticks', 'Num Tickers', 'Lead Ratio', 'OS Ratio', 'Repeat Sender Ratio', 'Mean Attempts To RP', 'Tick Counts']] = df_source.progress_apply(lambda x: analyze_tick_counts(x['Route Ticks'], x['Pitches']), axis=1)
    return df_source

# %%
def unique_route_prefabanalysis(df_source, selected_rgrade_array, selected_bgrade_array, numN):
    """Creates prefab tables based on tick metrics from source dataframe

    Parameters
    ----------
    df_source : df
        source dataframe
    selected_rgrade_array : list
        list of route grades
    selected_bgrade_array : list
        list of boulder grades
    numN : int
        number of superlative

    Returns
    -------
    Many dataframes
        Many dataframes filtered as such.
    """
    df_uniq_fil_r = df_source[df_source['Route Type'] != 'Boulder']
    df_uniq_fil_b = df_source[df_source['Route Type'] == 'Boulder']
    # Rarely led
    df_low_lead = df_uniq_fil_r[(df_uniq_fil_r['Lead Ratio'] < 0.4) & (df_uniq_fil_r['Pitches'] == 1)].sort_values(by='Lead Ratio')
    # Rarely toproped
    df_high_lead = df_uniq_fil_r[(df_uniq_fil_r['Lead Ratio'] > 0.9) & (df_uniq_fil_r['Pitches'] == 1)].sort_values(by='Lead Ratio', ascending=False)
    # Low OS Ratio
    df_low_OS_r = df_uniq_fil_r[(df_uniq_fil_r['OS Ratio'] < 0.35)].sort_values(by='OS Ratio')
    df_low_OS_b = df_uniq_fil_b[(df_uniq_fil_b['OS Ratio'] < 0.15)].sort_values(by='OS Ratio')
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
    df_nlow_OS_r = nsuperlative_os(df_source, selected_rgrade_array, 'lowest', numN)
    df_nhigh_OS_r = nsuperlative_os(df_source, selected_rgrade_array, 'highest', numN)
    df_nlow_OS_b = nsuperlative_os(df_source, selected_bgrade_array, 'lowest', numN)
    df_nhigh_OS_b = nsuperlative_os(df_source, selected_bgrade_array, 'highest', numN)
    
    return df_low_lead, df_high_lead, df_high_OS_r, df_low_OS_r, df_nlow_OS_r, df_nhigh_OS_r, df_high_OS_b, df_low_OS_b, df_nlow_OS_b, df_nhigh_OS_b