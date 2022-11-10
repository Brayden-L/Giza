import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

import pyinputplus as pyip

choices1 = ["csv", "link"]
resp1 = pyip.inputMenu(prompt='Select data source:\n', choices=choices1)
if resp1 == choices1[0]:
    while True:
        try:
            resp2 = pyip.inputFilepath(prompt='input csv file path', mustExist=True)
        except Exception:
            continue
        break
    df = pd.read_csv(resp2)
if resp1 == choices1[1]:
    resp2 = input('input link to profile of format "https://www.mountainproject.com/user/..."')