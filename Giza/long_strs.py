analysis_explainer = """**Note:** If you are unfamiliar with climbing terminology, please refer to this [explainer](https://www.thecrag.com/en/article/ticktypes).
### Features
Giza enables three primary features that the Mountain Project does not.
 1. Homogenizes grades so that comparisons can be made between every climb in the dataset.
 2. Analyzes tick data to provide additional metrics by which to judge a climb, and analyzes the data to find notable climbs based on those new metrics.
 3. Provides filterable plots to visualize performance.

### Added Metrics:
- **Num Ticks** : Positive Integer. Number of ticks, or, how many distinct climb entries were made by users for a given climb. This is a metric of popularity. As a rough rule, low is <30, high is >1000.
- **Lead Ratio** : 0<Float<1. What portion of ticks were lead attempts. When low this is a signifier of a dangerous lead. When high this is typically a signifier that the climb is inconvenient to top rope, typically a steep climb. As a rough rule, low is <0.4, high is >0.9.
- **OS Ratio** : 0<Float<1. What portion of ticks were onsights or flashes. When low this is a signifier that the route is "tricky" or stout for the grade. When high this is a signifier that the climb is "straightforward" or soft for the grade. As a rough rule, low is <0.35, and high is >0.80.
- **Mean Attempts to RP** : Positive float >=1. This is the mean of how many attempts it took for a successful redpoint from the population of climbers that were not able to onsight/flash the route, but eventually worked to a redpoint. It primarily signifies difficulty to redpoint. Few climbers are meticulous about logging their attempts, so the value of this metric is diminished. As a rough rule, low is <1.25, high is >2.00.
- **Repeat Sender Ratio** : Positive float >=1. This is the mean of total clean ascents from the population of climbers that have logged at least one clean ascent. Since many climbers will typically only climb a route/boulder until they obtain a clean ascent, this is an additional popularity metric. It signifies a climb so good that even those who have climbed it clean keep coming back. As a rough rule, high is >1.25."""

about_explainer = """**Summary**:  
Giza is a data dashboard that enables a climber with extended analytics based on their existing tick and todo lists. Some examples of what a user can do:

 - View a filterable [climbing pyramid](https://bomberclimbing.com/blog/rock-climbing-pyramid/#:~:text=A%20climbing%20pyramid%20is%20a,some%20more%20attention%20or%20support.) to gauge previous performance and aid in selection of future objectives.
 - Filter your todo list for climbs that are stout or soft for their grade.
 - Discover attributes about climbs and how they relate to your climbing ticks, such as an onsight of a notoriously tricky climb.
 - Look for hidden classics that the masses haven't yet caught onto, but a dedicated few seem to love.

**Underlying Details**:
- Giza removes all routes of type aid, ice and snow as analytics for those types of climbs are less meaningful and more difficult to weave into the more standard styles of sport, trad and boulder.
- The best data is gathered from a user who ticks every climb and every attempt.
- A single pitch fell/hung tick with multiple pitches is considered as many attempts as ticked pitches. Similarly a single pitch redpoint with multiple ticked pitches is considered N-1 failed attempts and a successful redpoint.
- An unavoidable side effect of the previous assumption is that single pitch climbs broken into multiple pitches is incorrectly assumed to be multiple attempts. This should happen rarely because you're a crusher and you should send the full pitch anyway.
- Multipitch climbs only "count" as a single climb of the overall grade of the climb. This ignores the grade and style of the other pitches. For example a multipitch with 2 pitches of 4th class climbing and a single 5.11+ pitch is given the same value as a 12 pitch climb with every pitch at 5.11+.  This is a limitation of the source data.
- Routes with missing lengths are set to 70ft, boulders to 12ft.

**Contact**:  
Brayden Levy  
Email: BraydenmLevy@gmail.com  
Github: https://github.com/Brayden-L

**Disclaimer**:  
Giza is for personal non-commercial use only. All Mountain Project data belongs to onX Maps Inc."""

pyr_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1643667996984-fcc69743449d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1548&q=80");
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
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
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
"""