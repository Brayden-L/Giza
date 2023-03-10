# Giza
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://giza-levyb.streamlit.app/)

![](https://github.com/Brayden-L/Giza/blob/main/Giza/Data_Archive/readme_gif.gif)

# Purpose
Giza is a data analysis tool that allows users of the popular rock climbing website [Mountain Project](https://www.mountainproject.com/) to discover deeper insight into their past performance and potential future climbs.

Mountain Project aggregates user data to provide information about specific climbs. It informs the user on the location, difficulty, length and required gear. It also allows images to be posted, provides an area for users to post opinions / warnings, and pools data on user performance for each climb.

Users typically have two lists. A "tick" list is a diary of the climbs the user has attempted and provides details on when the climb was done, whether the climber was successful, and any other notes. A "to-do" list is simply a list of climbs the user would like to climb in the future.

From these two lists there arises two inherent use cases. A tick list allows a user to analyze their past performance, and a to-do list helps a climber find their next climb. While Mountain Project provides some tools to aid in these goals, they are limited in their scope and usability.

Giza provides three primary features that Mountain Project currently lacks:
1. Homogenizes grades and cleans the data so that comparisons can be made between every climb in the dataset.
2. Analyzes tick data to provide additional metrics by which to quantify a climb.
3. Provides filterable plots to visualize metrics and performance.

# Usage
You can access the web app [here](https://giza-levyb.streamlit.app/) or with the badge at the top of the readme.

If you are unfamiliar with climbing terminology, please refer to this [explainer](https://www.thecrag.com/en/article/ticktypes).

On the "Scrape" page, you can provide a link to a profile, and download the users tick or to-do data. The tool will first clean the data, then it will use existing route data to construct additional metrics. This process can be time intensive, especially for lists of over 1000 routes. If you're just interested in seeing what Giza can do, you can instead use one of the provided datasets.

The analysis page is the core of the app. In order, the various functional sections are:
1. **Select List Type:** Ticks and ToDos provide different analytics as the use case for them is quite different. Tick analyses are typically to gauge performance. To Do analyses are typically to find routes one would like to climb that fit certain parameters.
2. **Select a Data Source:** If you've scraped a dataset in this session then it will automatically load here. Otherwise, you can select a preloaded dataset. You can also upload a Giza.PKL file if you have one saved.
3. **Select Grade Homogenization Settings:** This is so direct comparisons can be made among the entire dataset.
4. **Filter:** Maybe you'd like to only inspect sport climbs. Maybe you'd like to only look at harder climbs. Maybe you only want to see ticks in the last 12 months. All of these can be set via the filter and are applied to the entire analysis.
5. **Overview Plots:** These provide general information about your dataset. These give you a good idea of the distribution of qualitative and quantitative metrics.
6. **Prefabricated Route Analysis:** These plots provide a list of routes according to a desired type. Examples are the 3 most rarely onsighted for each grade in a list, or popular to repeat send.
7. **Full Routes Data Table:** If the prefabricated data does not have what you are looking for, you can sort and filter however you wish within this table.
8. **(Ticks Only) Tick Pyramid Plots:** The namesake. This section provides a pyramid plot and scatter plot of time vs. grade for all "sent" climbs. It lists attempts to send within each marker. It also includes tooltips with additional details.
9. **(Ticks Only) Tick Report:** A small collection of time series plots and lists that indicate notable sends as compared to added metrics.
10. **(Ticks Only) Full Ticks Data Table:** If the provided analysis is not enough for you, you can sort and filter however you please within this table.

Giza adds multiple new metrics gathered from tick data. They are:

* **Number of Ticks** : Positive Integer. Number of ticks, or, how many distinct climb entries were made by users for a given climb. This is a metric of popularity. As a rough rule, low is <30, high is >700.
* **Lead Ratio** : 0<Float<1. What portion of ticks were lead attempts. When low this is a signifier of a dangerous lead. When high this is typically a signifier that the climb is inconvenient to top rope, typically a steep climb. As a rough rule, low is <0.4, high is >0.9.
* **Onsight Ratio** : 0<Float<1. What portion of ticks were onsights or flashes. When low this is a signifier that the route is "tricky" or stout for the grade. When high this is a signifier that the climb is "straightforward" or soft for the grade. For routes low is <0.35 and high is >0.90. For boulders low is <0.15 and high is >0.7.
* **Mean Attempts to Redpoint** : Positive float >=1. This is the mean of how many attempts it took for a successful redpoint from the population of climbers that were not able to onsight/flash the route, but eventually worked to a redpoint. It primarily signifies difficulty to redpoint. Few climbers are meticulous about logging their attempts, so the value of this metric is diminished. As a rough rule, high is >1.80.
* **Repeat Sender Mean** : Positive float >=1. This is the mean of total clean ascents from the population of climbers that have logged at least one clean ascent. Since many climbers will typically only climb a route/boulder until they obtain a clean ascent, this is an additional popularity metric. It signifies a climb so good that even those who have climbed it clean keep coming back. As a rough rule a value above 1.2 is notable.

# Built With
Libraries:
* [Pandas](https://github.com/pandas-dev/pandas) and [Numpy](https://github.com/numpy/numpy) - Basic data analysis libraries
* [Plotly](https://github.com/plotly) - Plotting and visualization
* [Requests](https://github.com/psf/requests) - HTTP requests
* [Selenium](https://pypi.org/project/selenium/) - HTTP requests for pages w/ javascript
* [BeautifulSoup](https://github.com/wention/BeautifulSoup4) - HTML parsing
* [Streamlit](https://github.com/streamlit) - Web app framework

Streamlit Components:
* [STQDM](https://github.com/Wirg/stqdm) - TQDM style download bars for streamlit
* [Streamlit_aggrid](https://github.com/PablocFonseca/streamlit-aggrid) - Ag Grid tables for streamlit
* [Streamlit_nested_layouts](https://github.com/joy13975/streamlit-nested-layout) - Enables nested columns and toggles

# Disclaimer
Giza is for personal non-commercial use only. All Mountain Project data belongs to onX Maps Inc.
