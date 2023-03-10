# These functions blend sub-functions of unique route dataframes and tick dataframe type for use in streamlit
from constants import *
from unique_route_functions import (
    route_length_fixer,
    routescrape_syncro,
    extract_default_pitch,
    extract_num_star_ratings,
    assign_spmp,
    extract_tick_details,
    climb_tick_analysis,
)
from tick_route_functions import tick_uniq_clean


def uniqclean_ticktodo(df, type):
    """cleans dataframes of tick and todo type

    Parameters
    ----------
    df : pd.dataframe
        input dataframe
    type : str [Ticks, ToDos]
        type of list

    Returns
    -------
    df_return : pd.dataframe
        cleaned dataframe
    """
    if type == "Ticks":  # If ticks, special clean required
        df_return = tick_uniq_clean(df)
    if type == "ToDos":  # If todos, relabel necessary
        df_return = df.copy()
    df_return = route_length_fixer(df_return, "express")
    return df_return


def scrape_ticktodo(df, type, strip):
    """Runs scrape on tick and todo dataframes

    Parameters
    ----------
    df : pd.dataframe
        input dataframe
    type : str
        type of dataframe
    strip : bool
        whether to strip the final dataframe of data dense columns

    Returns
    -------
    df : pd.dataframe
        output dataframe
    scrape_stats : dict
        number of failed scrapes, list of routenames of failed scrapes, scrape failrate
    """
    # Scrape
    df = routescrape_syncro(df)
    if type == "Ticks":  # if ticks, need to get default pitch numbers
        df = extract_default_pitch(df)
    df = assign_spmp(df)
    df = extract_num_star_ratings(df)
    df = extract_tick_details(df)
    df = climb_tick_analysis(df)

    # Create scrape success details
    nfail_mainscr = df["Re Mainpage"].isna().sum()
    nfail_statscr = df["Re Statpage"].isna().sum()
    failed_mainscrape_list = df.loc[(df["Re Mainpage"].isna())]["Route"]
    failed_statscrape_list = df.loc[(df["Re Statpage"].isna())]["Route"]
    scrape_failrate = (
        1 - ((nfail_mainscr + nfail_statscr) / (2 * len(df.index)))
    ) * 100
    scrape_stats = {
        "nfail_mainscr": nfail_mainscr,
        "nfail_statscr": nfail_statscr,
        "failed_mainscrape_list": failed_mainscrape_list,
        "failed_statscrape_list": failed_statscrape_list,
        "scrape_failrate": scrape_failrate,
    }

    # Drop data dense columns that are no longer useful
    if strip == True:
        df.drop(
            columns=["Tick Counts", "Re Mainpage", "Re Statpage", "Route Ticks"],
            inplace=True,
        )  # This drastically cuts down on the file size once the analysis is finished.

    return df, scrape_stats
