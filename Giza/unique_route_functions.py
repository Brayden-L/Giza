# These functions are intended to be applied to BOTH unique route lists generated from "to do" and "tick" datasets.

# %%
# Data Science Related
import os
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import streamlit as st
import time

# Scraping Related
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import lxml
import cchardet
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# General
import datetime as dt
from stqdm import stqdm

# Other Project Files
from constants import *

# Initializations
stqdm.pandas()


# %%
def download_routelist(upload_type, link):
    """
    Downloads a tick or todo list from the MP website. Takes a link string and returns a dataframe constructed from the requested .CSV as well as an error string if applicable.

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
        df = pd.read_csv(f"{link}/{upload_type}-export")
        error_text = False
    except Exception as err:
        df = False
        print(err)
        if "https://www.mountainproject.com/user/" not in link:
            error_text = (
                """Link must be of form "https://www.mountainproject.com/user/" """
            )
        elif err.code == 401:
            error_text = "Unauthenticated (Error: 401)"
        elif err.code == 403:
            error_text = "Unauthorized (Error: 403)"
        elif err.code == 404:
            error_text = "Invalid Link (Error: 404)"
        elif err.code in range(500, 511):
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
    if "Date" in df_source.columns:
        df_source["Date"] = pd.to_datetime(df_source["Date"])  # 'Date' to datetype
        df_source["Date Formatted"] = df_source["Date"].dt.strftime("%Y-%m-%d")
        df_source.rename(
            columns={"Pitches": "Pitches Ticked"}, inplace=True
        )  # Pitches relabeled to Pitches Ticked
        df_source["Notes"] = df_source["Notes"].apply(
            lambda x: str(x).replace("&#39;", "'")
        )  # Apostrophe's are html coded in the notes section for some reason.

    # Remove all blank, aid, ice, snow, TR only, and trad/boulder climbing route types as they are not relevant.
    df_source = df_source[df_source["Route Type"].str.contains(r"Aid|Ice|Snow") != True]
    df_source = df_source[
        df_source["Route Type"].str.fullmatch(r"TR") != True
    ]  # if this is just a partial match it will detech "trad" too!
    df_source = df_source[
        df_source["Route Type"].str.contains(r"Trad")
        & df_source["Route Type"].str.contains(r"Boulder")
        != True
    ]
    df_source = df_source[df_source["Route Type"].notnull()]

    # Some routes have no grade, this seems to be a bug with Mountain Project
    df_source = df_source[df_source["Rating"].notnull()]

    # "trad, sport" goes to "trad". If it uses gear it's trad!
    df_source.loc[
        df_source["Route Type"].str.contains(r"Trad")
        & df_source["Route Type"].str.contains(r"Sport"),
        "Route Type",
    ] = "Trad"

    # "x, alpine" and "x, tr" goes to "x" Alpine and tr tags are not useful.
    def rem_route_el_from_list(ousted, seperator):
        el_rem_subset = df_source["Route Type"].str.contains(ousted) == True
        df_source.loc[el_rem_subset, "Route Type"] = (
            df_source[el_rem_subset]["Route Type"]
            .apply(lambda row: [val for val in row.split(seperator) if val != ousted])
            .apply(lambda x: ", ".join(x))
        )

    rem_route_el_from_list("Alpine", ", ")
    rem_route_el_from_list("TR", ", ")

    # Route Type to categorical type
    routetype_cat = CategoricalDtype(categories=ROUTE_TYPES)
    df_source["Route Type"] = df_source["Route Type"].astype(routetype_cat)

    # Extract route unique identifier from URL and create a new column for it. This makes for a reliable unique key even if the route name changes.
    if "Route ID" not in df_source.columns:
        df_source.insert(len(df_source.columns), "Route ID", "")
    df_source["Route ID"] = df_source["URL"].apply(lambda x: int(x.split("/")[4]))

    # Change YDS-Vgrade combos to just Vgrade. They are most likely boulders, so a bouldering grade is relevant.
    # TODO a more robust assignment would check listed pitches and length to see if it is more likely to be a route or a boulder. These are rare enough it is not worth the effort for now.
    subset = (
        df_source["Rating"]
        .apply(lambda row: [val for val in row.split() if val in V_GRADES_FULL])
        .astype(bool)
        & df_source["Rating"]
        .apply(lambda row: [val for val in row.split() if val in YDS_GRADES_FULL])
        .astype(bool)
        == True
    )
    df_source.loc[subset, "Rating"] = df_source[subset]["Rating"].apply(
        lambda x: x.split()[1]
    )
    df_source.loc[subset, "Route Type"] = "Boulder"

    # Seperate risk rating to new column
    # This allows us to filter by risk, and also strips the rating column to just it's difficulty component which is the important part.
    if "Rating" not in df_source.columns:
        df_source.insert(df_source.columns.get_loc("Rating") + 1, "Risk", "")
    risk_cat = CategoricalDtype(categories=RISK_GRADES, ordered=True)
    df_source["Risk"] = (
        df_source["Rating"]
        .apply(lambda row: [val for val in row.split() if val in RISK_GRADES])
        .apply(lambda x: "".join(x))
        .astype(risk_cat)
    )
    # Reduce Rating column to just rating
    rating_cat = CategoricalDtype(categories=GRADES_SUPER)
    df_source["Rating"] = (
        df_source["Rating"]
        .apply(lambda row: [val for val in row.split()][0])
        .astype(rating_cat)
    )

    # Create original rating and length archive to compare against or undo changes.
    if "Original Rating" not in df_source.columns:
        df_source.insert(
            df_source.columns.get_loc("Rating"), "Original Rating", df_source["Rating"]
        )

    # Your Stars NaN type is -1 for some reason, change it to an actual nonetype
    df_source.loc[df_source["Your Stars"] == -1, "Your Stars"] = None

    # Avg stars NaN type is also -1 for some reason, change it to actual nonetype
    df_source.loc[df_source["Avg Stars"] == -1, "Avg Stars"] = None

    # Base Location is a useful column for filtering as it is the only location tier that is guaranteed to be consistent across zones.
    if "Base Location" not in df_source.columns:
        df_source.insert(len(df_source.columns), "Base Location", "")
    df_source["Base Location"] = df_source["Location"].apply(lambda x: x.split(">")[0])

    return df_source


# %%
def route_length_fixer(df_source, input_type):
    """ "
    Fixes route length outliers and missing values. Manual input is currently disabled

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
    # Handle route length outliers and NaNs
    ## Define roped and bouldering specific subset
    roped_subset = (df_source["Route Type"] == "Sport") | (
        df_source["Route Type"] == "Trad"
    )
    boulder_subset = df_source["Route Type"] == "Boulder"

    ROPED_MIN_LENGTH = 15
    ROPED_MAX_LENGTH = 4500  # "Trango Towers" are 4,300' tall
    ROPED_DEFAULT_LENGTH = 70
    BOULDER_MIN_LENGTH = 1
    BOULDER_MAX_LENGTH = 55  # "Too Tall to Fall" is 50'
    BOULDER_DEFAULT_LENGTH = 12

    # Fix outliers
    def fix_length_outliers(dataframe, subset, minlength, maxlength, deflength):
        length_outliers = dataframe[subset][
            (dataframe[subset]["Length"] <= minlength)
            | (dataframe[subset]["Length"] >= maxlength)
        ]
        for loop_count, (index, data) in enumerate(length_outliers.iterrows()):
            if input_type == "express":
                updated_length = deflength
            # if input_type == 'manual':
            #     pass
            dataframe.at[index, "Length"] = updated_length
        return dataframe

    # Fill empty route lengths
    def fill_length_empties(dataframe, subset, minlength, maxlength, deflength):
        length_missing = dataframe[subset][
            (dataframe[subset]["Length"].isnull()) | (dataframe[subset]["Length"] == 0)
        ]
        for loop_count, (index, data) in enumerate(length_missing.iterrows()):
            if input_type == "express":
                updated_length = deflength
            # if input_type == 'manual':
            #     pass
            dataframe.at[index, "Length"] = updated_length
        return dataframe

    df_source = fix_length_outliers(
        df_source,
        roped_subset,
        ROPED_MIN_LENGTH,
        ROPED_MAX_LENGTH,
        ROPED_DEFAULT_LENGTH,
    )
    df_source = fill_length_empties(
        df_source,
        roped_subset,
        ROPED_MIN_LENGTH,
        ROPED_MAX_LENGTH,
        ROPED_DEFAULT_LENGTH,
    )
    df_source = fix_length_outliers(
        df_source,
        boulder_subset,
        BOULDER_MIN_LENGTH,
        BOULDER_MAX_LENGTH,
        BOULDER_DEFAULT_LENGTH,
    )
    df_source = fill_length_empties(
        df_source,
        boulder_subset,
        BOULDER_MIN_LENGTH,
        BOULDER_MAX_LENGTH,
        BOULDER_DEFAULT_LENGTH,
    )

    return df_source


# %%
def grade_homo(df_source, r_type, r_direction, b_type, b_direction):
    """
    Reassigns grades to a single YDS or Vgrade schema.

    Parameters
    ----------
    df_source : df
        Original route df.
    r_type : str [letter, sign]
        YDS letter or sign style grades.
    r_direction : str [up, down, even_rand, manual]
        Unused if r_type='letter'. Which way to assign grades. even_rand rounds a randomly selected half up and the randomly remaining half down.
    b_type : str [flat, sign]
        Vgrade flat grades or include sign grades.
    b_direction : str [up, down, even_rand, manual]
        Used for both b_type.

    Return
    ------
    df_source : df
        Original df with grade homogenization
    """
    rating_isolate = df_source["Original Rating"].apply(
        lambda row: [val for val in row.split()][0]
    )  # This is a fail-safe to ensure we are only looking at the part of the rating we care about, not risk or sub-ratings.

    # Reset 'Rating' column so this mapping can be re-run
    df_source["Rating"] = df_source["Original Rating"]

    # Roped Grades
    def grademoderate():
        grade_change_subset = rating_isolate.isin(list(rgrademoderatemap.keys()))
        df_source.loc[grade_change_subset, "Rating"] = df_source.loc[
            grade_change_subset
        ]["Original Rating"].map(rgrademoderatemap)

    def grade_split(upmap, downmap):
        grade_change_subset = rating_isolate.isin(list(upmap.keys()))
        grade_change_subset_df = df_source[grade_change_subset]
        for grade in grade_change_subset_df["Original Rating"].unique():
            to_change = grade_change_subset_df[
                grade_change_subset_df["Original Rating"] == grade
            ]
            changed_up = to_change.sample(frac=0.5)["Original Rating"].map(upmap)
            df_source.loc[changed_up.index, "Rating"] = changed_up
        grade_change_subset = rating_isolate.isin(list(downmap.keys()))
        grade_change_subset_df = df_source[grade_change_subset]
        for grade in grade_change_subset_df["Original Rating"].unique():
            to_change = grade_change_subset_df[
                grade_change_subset_df["Original Rating"] == grade
            ]
            changed_down = to_change["Original Rating"].map(downmap)
            df_source.loc[changed_down.index, "Rating"] = changed_down

    if r_type == "sign":
        grade_change_subset = rating_isolate.isin(list(rgradecompmap.keys()))
        df_source.loc[grade_change_subset, "Rating"] = df_source[grade_change_subset][
            "Original Rating"
        ].map(rgradecompmap)
    else:
        if r_direction == "up":
            grademoderate()
            grade_change_subset = rating_isolate.isin(list(rgradeupmap.keys()))
            df_source.loc[grade_change_subset, "Rating"] = df_source[
                grade_change_subset
            ]["Original Rating"].map(rgradeupmap)
        if r_direction == "down":
            grademoderate()
            grade_change_subset = rating_isolate.isin(list(rgradedownmap.keys()))
            df_source.loc[grade_change_subset, "Rating"] = df_source[
                grade_change_subset
            ]["Original Rating"].map(rgradedownmap)
        if r_direction == "even_rand":
            grademoderate()
            grade_split(rgradeupmap, rgradedownmap)

    # Boulder Grades
    if b_type == "flat":
        # Remove all + and - grades
        grade_change_subset = rating_isolate.isin(list(bgradeconmapflat.keys()))
        df_source.loc[grade_change_subset, "Rating"] = df_source[grade_change_subset][
            "Original Rating"
        ].map(bgradeconmapflat)

        if b_direction == "up":
            grade_change_subset = rating_isolate.isin(list(bgradeupmapflat.keys()))
            df_source.loc[grade_change_subset, "Rating"] = df_source[
                grade_change_subset
            ]["Original Rating"].map(bgradeupmapflat)
        if b_direction == "down":
            grade_change_subset = rating_isolate.isin(list(bgradedownmapflat.keys()))
            df_source.loc[grade_change_subset, "Rating"] = df_source[
                grade_change_subset
            ]["Original Rating"].map(bgradedownmapflat)
        if b_direction == "even_rand":
            grade_split(bgradeupmapflat, bgradedownmapflat)

    if b_type == "sign":
        if b_direction == "up":
            grade_change_subset = rating_isolate.isin(list(bgradeupmapsign.keys()))
            df_source.loc[grade_change_subset, "Rating"] = df_source[
                grade_change_subset
            ]["Original Rating"].map(bgradeupmapsign)
        if b_direction == "down":
            grade_change_subset = rating_isolate.isin(list(bgradedownmapsign.keys()))
            df_source.loc[grade_change_subset, "Rating"] = df_source[
                grade_change_subset
            ]["Original Rating"].map(bgradedownmapsign)
        if b_direction == "even_rand":
            grade_split(bgradeupmapsign, bgradedownmapsign)

    return df_source


# %%
def routescrape_syncro(df_source, retries=3):
    """
    Downloads the route page and stat page for each entry.
    It is suggested you pass this a list of unique routes so it does not download redundantly.
    Input df
    Returns a text string for both .
    """
    # request setup
    s = requests.Session()
    retries = Retry(
        total=retries, backoff_factor=1, status_forcelist=tuple(range(400, 600))
    )
    s.mount("http://", HTTPAdapter(max_retries=retries))

    # Github Token Import
    # Set the GitHub token as an environment variable
    os.environ["GH_TOKEN"] = st.secrets["GITHUB_TOKEN"]

    # selenium setup
    firefoxOptions = Options()
    firefoxOptions.add_argument("--headless")
    # service = Service(GeckoDriverManager().install())
    service = Service()
    driver = webdriver.Firefox(
        options=firefoxOptions,
        service=service,
    )
    driver.implicitly_wait(2)
    butt_xpath = """//*[@id="route-stats"]/div[3]/div/div[4]/div/div/button"""
    login_xpath = """/html/body/div[1]/div/div/div[1]/button"""

    def insert_str_to_address(url, insert_phrase):
        str_list = url.split("/")
        str_list.insert(4, insert_phrase)
        return "/".join(str_list)

    def page_download_req(url):
        try:
            res = s.get(url).text
        except Exception as e:
            print(url)
            print(e)
            res = None
        return res

    def page_download_sel(url):
        try:
            driver.get(url)
            while True:
                # if there is a login popup, then exit it.
                login_x = driver.find_element(By.XPATH, login_xpath)
                if login_x:
                    driver.execute_script("arguments[0].click();", login_x)
                    print("woop")
                # click the "load more" button as many times as you can
                try:
                    butt = driver.find_element(By.XPATH, butt_xpath)
                    driver.execute_script("arguments[0].click();", butt)
                except Exception as e:
                    break
            res = driver.page_source
        except Exception as e:
            print(url)
            print(e)
            res = None
        return res

    stqdm.pandas(desc="(1/6) Scraping Mainpages")
    if (
        "Re Mainpage" not in df_source.columns
    ):  # Creates column if it does not yet exist, otherwise it will try to download any that errored last attempt
        df_source.insert(len(df_source.columns), "Re Mainpage", None)
        df_source["Re Mainpage"] = df_source["URL"].progress_apply(page_download_req)
    else:
        subset = df_source["Re Mainpage"].isna()
        df_source.loc[subset, "Re Mainpage"] = df_source.loc[
            subset, "URL"
        ].progress_apply(page_download_req)
    stqdm.pandas(desc="(2/6) Scraping Statpages")
    if "Re Statpage" not in df_source.columns:
        df_source.insert(len(df_source.columns), "Re Statpage", None)
        df_source["Re Statpage"] = df_source["URL"].progress_apply(
            lambda x: page_download_sel(insert_str_to_address(x, "stats"))
        )
    else:
        subset = df_source["Re Statpage"].isna()
        df_source.loc[subset, "Re Statpage"] = df_source.loc[
            subset, "URL"
        ].progress_apply(page_download_sel)
    driver.quit()
    return df_source


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
            soup = BeautifulSoup(res, "lxml")
            route_type_text = str(
                soup.find(class_="description-details").find_all("td")[1]
            )
            pitch_search = re.search(r"\d+ pitches", route_type_text)
            if isinstance(pitch_search, type(None)):
                num_pitches = 1
            else:
                num_pitches = pitch_search.group(0).split(" ")[0]
            return int(num_pitches)

    stqdm.pandas(desc="(3/6) Extracting Default Pitches")
    df_source["Pitches"] = df_source["Re Mainpage"].progress_apply(get_pitches)
    return df_source


# %%
def extract_num_star_ratings(df_source):
    """
    Analyzes statpage for number of ratings given to the climb. Input is dataframe, output is updated dataframe. num_star_ratings is int.
    """

    def get_num_star_ratings(res):
        if res is None:
            return None
        else:
            soup = BeautifulSoup(res, "lxml")
            num_star_ratings_html = soup.select_one(
                "#route-stats > div.onx-stats-table > div > div:nth-child(1) > div > h3 > span"
            )
            if num_star_ratings_html is None:
                num_star_rating = 0
            else:
                num_star_rating = int(num_star_ratings_html.text.replace(",", ""))
            if num_star_rating == -1:
                num_star_rating = 0
        return num_star_rating

    stqdm.pandas(desc="(4/6) Extracting Star Ratings")
    df_source["Num Star Ratings"] = df_source["Re Statpage"].progress_apply(
        get_num_star_ratings
    )
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
    # This looks like something that should happen at the data cleaning stage, but since tick list data requires official pitch counts to be extracted, it must be a seperate function after the extract is applied.
    if "SP/MP" not in df_source.columns:
        df_source["SP/MP"] = None
    df_source.loc[
        (df_source["Route Type"].isin(["Sport", "Trad"])) & (df_source["Pitches"] == 1),
        "SP/MP",
    ] = "SP"
    df_source.loc[
        (df_source["Route Type"].isin(["Sport", "Trad"])) & (df_source["Pitches"] > 1),
        "SP/MP",
    ] = "MP"
    if (
        df_source["SP/MP"].dtype != "category"
    ):  # If it isn't already categorical from a previous application of this function, then set it to categorical
        df_source["SP/MP"] = pd.Categorical(df_source["SP/MP"])
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
        # A clean and performant way to construct a dataframe is to append lists and then only turn it into a dataframe at the very end. This is in contrast to appending a dataframe.
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
            soup = BeautifulSoup(res, "lxml")
            # print(soup.select("#route-stats > div.row.pt-main-content > div > h1")) # Tells you which page is being scraped, useful for debugging
            try:
                blocks = list(
                    # could also search for tr tags with text including "·" and take their parents. This would be more tamper-proof
                    soup.select(
                        "#route-stats > div.onx-stats-table > div > div.col-lg-6.col-sm-12.col-xs-12.mt-2.max-height.max-height-md-1000.max-height-xs-400 > div > table > tbody"
                    )[0].find_all("tr")
                )
            except Exception:
                blocks = []
            for x in blocks:
                soup = BeautifulSoup(str(x), "lxml")
                entries = soup.find_all("div", attrs={"class": None})
                for entry in entries:
                    entrytext = entry.text
                    try:
                        name.append(soup.find("a").text.strip())
                    except Exception:
                        name.append("")

                    try:
                        namelink.append(soup.find("a")["href"].strip())
                    except Exception:
                        namelink.append("")

                    try:
                        date_search = [re.search(r"\w{3}\s\d{1,2},\s\d{4}", entrytext)]
                        entrydate.append(
                            [
                                subresult.group(0).strip() if subresult else ""
                                for subresult in date_search
                            ][0]
                        )  # pulls match text if match object is not none
                    except Exception:
                        entrydate.append("")

                    try:
                        pitches_search = [
                            re.search(r"·([^.]+\s(pitches))", entrytext)
                        ]  # regex for starting at · and ending at first period only if it includes the word "pitches"
                        pitchesinterm = [
                            subresult.group(0) if subresult else ""
                            for subresult in pitches_search
                        ]
                        pitches.append(
                            [
                                int(re.search(r"\d+", subresult).group(0).strip())
                                if subresult
                                else 1
                                for subresult in pitchesinterm
                            ][0]
                        )  # take just the digit of the string
                    except Exception:
                        pitches.append(1)

                    try:
                        style_search = [
                            re.search(
                                r"(Solo|TR|Follow|Lead|Send|Attempt|Flash)", entrytext
                            )
                        ]
                        style_val = [
                            subresult.group(0).strip() if subresult else ""
                            for subresult in style_search
                        ][
                            0
                        ]  # I have a conditional in the comment search that depends on this so I made it a separate variable
                        style.append(style_val)
                    except Exception:
                        style.append("")

                    try:
                        if style_val != "":
                            lead_style_search = [re.search(r"/([^.]+)", entrytext)]
                            lead_style.append(
                                [
                                    subresult.group(0)[2:].strip() if subresult else ""
                                    for subresult in lead_style_search
                                ][0]
                            )
                        else:
                            lead_style.append("")
                    except Exception:
                        lead_style.append("")

                    try:
                        if style_val != "":
                            comment_search = [
                                re.search(r"(Solo|TR|Follow|Lead).*", entrytext)
                            ]
                            commentinterm = [
                                subresult.group(0) if subresult else ""
                                for subresult in comment_search
                            ]
                            comment.append(
                                [
                                    re.search(r"\..*", subresult).group(0)[2:].strip()
                                    if subresult
                                    else ""
                                    for subresult in commentinterm
                                ][0]
                            )
                        else:
                            comment_search = [
                                re.search(r"·(.*)", entrytext)
                            ]  # If no style comment then entire phrase is the comment.
                            comment.append(
                                [
                                    subresult.group(0)[2:].strip() if subresult else ""
                                    for subresult in comment_search
                                ][0]
                            )
                    except Exception:
                        comment.append("")
            # print (len(name),len(namelink),len(entrydate),len(pitches),len(style),len(lead_style),len(comment))
            # print (name,namelink,entrydate,pitches,style,lead_style,comment)
            d = pd.DataFrame(
                {
                    "Username": name,
                    "User Link": namelink,
                    "Date": entrydate,
                    "Pitches Ticked": pitches,
                    "Style": style,
                    "Lead Style": lead_style,
                    "Comment": comment,
                }
            )
            # One last possible error correction, I've seen an oomlot injected a "/" into lead style and the regex incidentally detected it
            d.loc[~d["Lead Style"].isin(TICK_OPTIONS), "Lead Style"] = ""
            # Recast columns to correct data type
            d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
            d["Style"] = pd.Categorical(d["Style"])
            d["Lead Style"] = pd.Categorical(d["Lead Style"])
        return d

    stqdm.pandas(desc="(5/6) Constructing Tick Dataframe")
    df_source["Route Ticks"] = df_source["Re Statpage"].progress_apply(get_tick_details)
    return df_source


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
            if (
                styleval in CLEAN_SEND
            ):  # clean sends with multiple ticks are assumed to be fell/hung attempts up to that clean send.
                nest_list.append([routeticks[colref][row]])
                nest_list.append(
                    (routeticks["Pitches Ticked"][row] - 1) * ["Fell/Hung"]
                )
            else:
                nest_list.append(
                    routeticks["Pitches Ticked"][row] * [routeticks[colref][row]]
                )
        if pitchnum > 1:
            nest_list.append([routeticks[colref][row]])
    flat_list = [num for sublist in nest_list for num in sublist]
    return flat_list


def is_prior_sender(df_source):
    """Takes a dataframe of a single given users ticks on a specific climn, outputs str of user name if user redpointed. Ignores users who onsighted prior to a redpoint. This allows creation of a list of people who "worked" a route clean.

    Parameters
    ----------
    df_source : df
        A given users ticks for a single specific climb

    Returns
    -------
    str
        Returns name of user if valid, returns None if user has prior onsight/flash
    """
    clean_send_dates = df_source[df_source["Lead Style"].isin(CLEAN_SEND_WORKED)][
        "Date"
    ]
    if (
        clean_send_dates.isna().any()
    ):  # Some ticks have NaT improper dates (Ex: 20222/01/011), ignore the ticker with bad data. This is a rare edge case but I've seen it happen.
        return None
    else:
        firstrp_index = clean_send_dates.idxmin()
        already_sent_bool = any(
            df_source.loc[firstrp_index::]["Lead Style"].isin(CLEAN_SEND_FIRST)
        )
        valid_sender = not already_sent_bool
        if valid_sender:
            return df_source.iloc[0]["Username"]
        else:
            return None


def count_attempt2rp(df_source, pitchnum):
    """Takes a dataframe of a single given users ticks on a specific climb, outputs number of attempts to first redpoint.

    Parameters
    ----------
    df_source : df
        A given users ticks for a single specific climb
    pitchnum : int
        number of pitches in route

    Returns
    -------
    int
        Number of attempts to first redpoint
    """
    firstrp_cutoff = df_source[df_source["Lead Style"].isin(CLEAN_SEND_WORKED)][
        "Date"
    ].idxmin()  # Find index of first rp
    # If multipitch, we count ticks. If singlepitch we count number of total ticked pitches.
    if pitchnum > 1:
        nattempts = (
            df_source.sort_values("Date", ascending=False)
            .loc[firstrp_cutoff::]["Pitches Ticked"]
            .count()
        )
    if pitchnum == 1:
        nattempts = (
            df_source.sort_values("Date", ascending=False)
            .loc[firstrp_cutoff::]["Pitches Ticked"]
            .sum()
        )  # Sum all pitches attempted prior to that
    return nattempts


def analyze_tick_counts(routeticks, pitchnum):
    """
    Analyzes tick sub-df.

    Parameters
    ----------
    df_source : df
        Source dataframe
    pitchnum : int
        Number of pitches in route

    Return
    ------
    num_ticks : int
        Number of ticks
    num_tickers : int
        Number of users who ticked
    lead_ratio : float
        Lead Ticks / total non-null ticks
    os_ratio : float
        (onsight ticks + flash ticks) / (total non-null ticks)
    repeat_senders : float
        The mean amount of times users send a given climb clean. Minimum 1.
    rpnattempt_mean : float
        Number of attempts it takes the average climber who worked the route clean. Minimum 1.
    tick_counts : series
        Series with index as a string of tick type and the values as integers of counts of those types in the dataframe.
    """
    if (routeticks is None) or (
        len(routeticks.index) == 0
    ):  # If list is unavailable or empty
        num_ticks = (
            num_tickers
        ) = (
            lead_ratio
        ) = os_ratio = repeat_senders = rpnattempt_mean = tick_counts = float("NaN")
    else:
        # Get number of ticks and tickers
        num_ticks = len(routeticks.index)
        num_tickers = routeticks["Username"].nunique()

        # Create tick metrics
        tick_cat = CategoricalDtype(categories=TICK_OPTIONS)
        tick_type_list = pd.Series(
            unpack_style(routeticks, "Style", pitchnum)
            + unpack_style(routeticks, "Lead Style", pitchnum),
            dtype=tick_cat,
        )
        tick_counts = tick_type_list.value_counts()
        repeat_senders = (
            routeticks[routeticks["Lead Style"].isin(CLEAN_SEND)]
            .groupby("Username")["Lead Style"]
            .count()
            .mean()
        )  # It is assumed that each clean send gets its own tick. For example that a 2 pitch redpoint tick on a single pitch climb is one fell/hung into a redpoint, not two consecutive redpoints. Few people redpoint a climb multiple times in a session.

        rp_unames = routeticks[routeticks["Lead Style"].isin(CLEAN_SEND_WORKED)][
            "Username"
        ]  # List of names of those who rp'd
        if (
            rp_unames.empty
        ):  # if the list exists, but has no redpointers, we want to assign NaN
            rpnattempt_mean = float("NaN")
        else:
            df_rpers_only = routeticks[routeticks["Username"].isin(rp_unames)]
            rpers_list = df_rpers_only.groupby("Username").apply(
                is_prior_sender
            )  # Get list of users who did not onsight/flash prior to RP
            df_rpers_only = df_rpers_only[
                df_rpers_only["Username"].isin(rpers_list)
            ]  # Remove RPers with a prior onsight
            attempt_list = (
                df_rpers_only.groupby("Username")
                .apply(lambda x: count_attempt2rp(x, pitchnum))
                .values.tolist()
            )  # Count num attempts of each each user.
            rpnattempt_mean = np.mean(attempt_list)

        lead_ratio = tick_counts["Lead"] / (
            tick_counts["Follow"] + tick_counts["TR"] + tick_counts["Lead"]
        )
        os_ratio = (tick_counts["Onsight"] + tick_counts["Flash"]) / (
            tick_counts["Onsight"]
            + tick_counts["Flash"]
            + tick_counts["Fell/Hung"]
            + tick_counts["Redpoint"]
            + tick_counts["Pinkpoint"]
            + tick_counts["Attempt"]
            + tick_counts["Send"]
        )
    return pd.Series(
        [
            num_ticks,
            num_tickers,
            lead_ratio,
            os_ratio,
            repeat_senders,
            rpnattempt_mean,
            tick_counts,
        ]
    )


def climb_tick_analysis(df_source):
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
    # Analyzes tick sub dataframe to create meaningful metrics.
    stqdm.pandas(desc="(6/6) Constructing Tick Analytics")
    df_source[
        [
            "Num Ticks",
            "Num Tickers",
            "Lead Ratio",
            "OS Ratio",
            "Repeat Sender Ratio",
            "Mean Attempts To RP",
            "Tick Counts",
        ]
    ] = df_source.progress_apply(
        lambda x: analyze_tick_counts(x["Route Ticks"], x["Pitches"]), axis=1
    )
    return df_source


# %%
@st.experimental_memo
def unique_route_prefabanalysis(
    df_source, selected_rgrade_array, selected_bgrade_array, numN
):
    """Creates prefabricated data tables based on tick metrics from source dataframe

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
    df_uniq_fil_r = df_source[df_source["Route Type"] != "Boulder"]
    df_uniq_fil_b = df_source[df_source["Route Type"] == "Boulder"]
    # Rarely led
    df_low_lead = df_uniq_fil_r[
        (df_uniq_fil_r["Lead Ratio"] < 0.4) & (df_uniq_fil_r["Pitches"] == 1)
    ].sort_values(by="Lead Ratio")
    # Rarely toproped
    df_high_lead = df_uniq_fil_r[
        (df_uniq_fil_r["Lead Ratio"] > 0.9) & (df_uniq_fil_r["Pitches"] == 1)
    ].sort_values(by="Lead Ratio", ascending=False)
    # Low OS Ratio
    df_low_OS_r = df_uniq_fil_r[(df_uniq_fil_r["OS Ratio"] < 0.35)].sort_values(
        by="OS Ratio"
    )
    df_low_OS_b = df_uniq_fil_b[(df_uniq_fil_b["OS Ratio"] < 0.15)].sort_values(
        by="OS Ratio"
    )
    # High OS Ratio
    df_high_OS_r = df_uniq_fil_r[(df_uniq_fil_r["OS Ratio"] > 0.9)].sort_values(
        by="OS Ratio", ascending=False
    )
    df_high_OS_b = df_uniq_fil_b[(df_uniq_fil_b["OS Ratio"] > 0.7)].sort_values(
        by="OS Ratio", ascending=False
    )

    # N superlative OS Ratio by Grade
    def nsuperlative_os(data, rgrade_array, direction, numN):
        outlist = []
        for group in rgrade_array:
            if direction == "highest":
                outlist.extend(
                    list(data[data["Rating"] == group].nlargest(numN, "OS Ratio").index)
                )
            if direction == "lowest":
                outlist.extend(
                    list(
                        data[data["Rating"] == group].nsmallest(numN, "OS Ratio").index
                    )
                )
        df_out = data.loc[outlist]
        return df_out

    df_nlow_OS_r = nsuperlative_os(df_source, selected_rgrade_array, "lowest", numN)
    df_nhigh_OS_r = nsuperlative_os(df_source, selected_rgrade_array, "highest", numN)
    df_nlow_OS_b = nsuperlative_os(df_source, selected_bgrade_array, "lowest", numN)
    df_nhigh_OS_b = nsuperlative_os(df_source, selected_bgrade_array, "highest", numN)
    # High RP attempts
    df_high_RPA_r = df_uniq_fil_r[
        df_uniq_fil_r["Mean Attempts To RP"] > 1.8
    ].sort_values(by="Mean Attempts To RP", ascending=False)
    # Popular Repeated Route
    df_high_RSR_r = df_uniq_fil_r[
        df_uniq_fil_r["Repeat Sender Ratio"] > 1.2
    ].sort_values(by="Repeat Sender Ratio", ascending=False)
    df_high_RSR_b = df_uniq_fil_b[
        df_uniq_fil_b["Repeat Sender Ratio"] > 1.05
    ].sort_values(by="Repeat Sender Ratio", ascending=False)

    return (
        df_low_lead,
        df_high_lead,
        df_high_OS_r,
        df_low_OS_r,
        df_nlow_OS_r,
        df_nhigh_OS_r,
        df_high_OS_b,
        df_low_OS_b,
        df_nlow_OS_b,
        df_nhigh_OS_b,
        df_high_RPA_r,
        df_high_RSR_r,
        df_high_RSR_b,
    )
