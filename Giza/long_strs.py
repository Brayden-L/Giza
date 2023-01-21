# Long markdown and image strings for use in front end display

scrape_explainer = """
##### Options
It is first necessary to explain that streamlit works via a "session". Each person that accesses the app receives their own session. When the user exits the session, whatever occorred during that session is permanently deleted. This is not a full website, there is no database to store your data.<br><br>
With that said, there are three ways to access data:
1. You scrape it yourself, the data is stored in the session and you can use it in the analytical tool.
2. You scrape it yourself, you download the .PKL file, then come back later to a new session and upload it to the analytical tool.
3. You ignore the scrape tool and use one of the included datasets.<br><br>

##### How-To
1. Select whether you would like to scrape a tick list or a todo list. Giza supports both. Tick analyses are typically to gauge performance. To Do analyses are typically to find routes one would like to climb that fit certain parameters.
2. Provide a user profile link, and download the desired list.
3. Scrape the list to obtain full metrics.
4. Optionally download the scraped dataset for later user or personal use.
"""

analysis_explainer = """
**Note:** If you are unfamiliar with climbing terminology, please refer to this [explainer](https://www.thecrag.com/en/article/ticktypes).
##### How-To:
1. **Select List Type:** Ticks and ToDos provide different analytics as the use case for them is quite different. Tick analyses are typically to gauge performance. To Do analyses are typically to find routes one would like to climb that fit certain parameters.
2. **Select a Data Source:** If you've scraped a dataset in this session then it will automatically load here. Otherwise, you can select a preloaded dataset. You can also upload a Giza.PKL file if you have one saved.
3. **Select Grade Homogenization Settings:** This is so direct comparisons can be made among the entire dataset.
4. **Filter:** Maybe you'd like to only inspect sport climbs. Maybe you'd like to only look at harder climbs. Maybe you only want to see ticks in the last 12 months. All of these can be set via the filter and are applied to the entire analysis. Note: the best way to reset the filter is to go to another page and return to the Analysis Page.
5. **Overview Plots:** These provide general information about your dataset. These give you a good idea of the distribution of qualitative and quantitative metrics.
6. **Prefabricated Route Analysis:** These plots provide a list of routes according to a desired type. Examples are the 3 most rarely onsighted for each grade in a list, or popular to repeat send.
7. **Full Routes Data Table:** If the prefabricated data does not have what you are looking for, you can sort and filter however you wish within this table.
8. **(Ticks Only) Tick Pyramid Plots:** The namesake. This section provides a pyramid plot and scatter plot of time vs. grade for all "sent" climbs. It lists attempts to send within each marker. It also includes tooltips with additional details.
10. **(Ticks Only) Tick Report:** A small collection of time series plots and lists that indicate notable sends as compared to added metrics.
11. **(Ticks Only) Full Ticks Data Table:** If the provided analysis is not enough for you, you can sort and filter however you please within this table.<br><br>
##### Added Metrics:
Giza adds multiple new metrics gathered from tick data. They are:
- **Number of Ticks** : Positive Integer. Number of ticks, or, how many distinct climb entries were made by users for a given climb. This is a metric of popularity. As a rough rule, low is <30, high is >700.
- **Lead Ratio** : 0<Float<1. What portion of ticks were lead attempts. When low this is a signifier of a dangerous lead. When high this is typically a signifier that the climb is inconvenient to top rope, typically a steep climb. As a rough rule, low is <0.4, high is >0.9.
- **Onsight Ratio** : 0<Float<1. What portion of ticks were onsights or flashes. When low this is a signifier that the route is "tricky" or stout for the grade. When high this is a signifier that the climb is "straightforward" or soft for the grade. For routes low is <0.35 and high is >0.90. For boulders low is <0.15 and high is >0.7.
- **Mean Attempts to Redpoint** : Positive float >=1. This is the mean of how many attempts it took for a successful redpoint from the population of climbers that were not able to onsight/flash the route, but eventually worked to a redpoint. It primarily signifies difficulty to redpoint. Few climbers are meticulous about logging their attempts, so the value of this metric is diminished. As a rough rule, high is >1.80.
- **Repeat Sender Ratio** : Positive float >=1. This is the mean of total clean ascents from the population of climbers that have logged at least one clean ascent. Since many climbers will typically only climb a route/boulder until they obtain a clean ascent, this is an additional popularity metric. It signifies a climb so good that even those who have climbed it clean keep coming back. As a rough rule a value above 1.2 is notable.
"""

about_explainer = """
Giza is intended to supplement [Mountain Project](https://www.mountainproject.com/) user tick list data to to provide additional data insights that are not available on the base website. The core inspiration was to provide a [climbing pyramid](https://bomberclimbing.com/blog/rock-climbing-pyramid/#:~:text=A%20climbing%20pyramid%20is%20a,some%20more%20attention%20or%20support.), which is a useful tool for gauging progression and outlining appropriate future objectives. The analytic possibilities enabled by the user generated data is vast, so there are many additional capabilities provided.

**Core Features**
Giza enables three primary features that the Mountain Project does not.
 1. Homogenizes grades so that comparisons can be made between every climb in the dataset.
 2. Analyzes tick data to provide additional metrics by which to judge a climb, and compares this to tick data to find notable climbs based on those new metrics.
 3. Provides filterable plots to visualize metrics and performance.

**Example of Capability**:  
Giza is a data dashboard that empowers a climber with extended analytics based on their existing tick and todo lists. Some examples of what a user can do:

 - View a filterable climbing pyramid to gauge previous performance and aid in selection of future objectives.
 - Filter your todo list for climbs that are stout or soft for their grade.
 - Discover attributes about climbs and how they relate to your climbing ticks, such as an onsight of a notoriously tricky climb.
 - Look for hidden classics that the masses haven't yet caught onto, but a dedicated few seem to love.

**Contact**:  
Email: Braydenmlevy@gmail.com  
Github: https://github.com/Brayden-L  
LinkedIn: https://www.linkedin.com/in/braydenmlevy/

**Disclaimer**:  
Giza is for personal non-commercial use only. All Mountain Project data belongs to onX Maps Inc.  
.  
.  
.  
.  
.  
.  
.  
.  
.  

**Gritty Details**:
- Giza removes all routes of type aid, ice and snow as analytics for those types of climbs are less meaningful and more difficult to weave into the more standard styles of sport, trad and boulder.
- The best data is gathered from a user who ticks every climb and every attempt.
- A single pitch fell/hung tick with multiple pitches is considered as many attempts as ticked pitches. Similarly a single pitch redpoint with multiple ticked pitches is considered N-1 failed attempts and a successful redpoint.
- An unavoidable side effect of the previous assumption is that single pitch climbs broken into multiple pitches is incorrectly assumed to be multiple attempts. This should happen rarely because you're a crusher and you should send the full pitch anyway.
- Multipitch climbs only "count" as a single climb of the overall grade of the climb. This ignores the grade and style of the other pitches. For example a multipitch with 2 pitches of 4th class climbing and a single 5.11+ pitch is given the same value as a 12 pitch climb with every pitch at 5.11+.  This is a limitation of the source data.
- Routes with missing lengths are set to 70ft, boulders to 12ft.
"""

pyr_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1643667996984-fcc69743449d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1548&q=80");
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
background-size: cover
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
"""

blue_gradient_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1508615070457-7baeba4003ab?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80");
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
background-size: cover
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
"""