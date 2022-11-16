import os
import os.path as path
import glob 
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import seaborn as sns
sns.set(font_scale=1.5)
import numpy as np
import pandas as pd
from datetime import datetime
from scipy import stats

import tools as utils


wx_data_path  = './DataSciTest/wx_data/'
yld_data_path = './DataSciTest/yld_data/'

weather_tool = utils.weather_data_tool(wx_data_path, yld_data_path)

# Problem 1
MissingPrcpDataDF = weather_tool.MissingPrcpData() 

# Problem 2
YearlyAverageDf = weather_tool.YearlyAverages()  

# Problem 3
YearHistogramDf = weather_tool.YearHistogram()

# Problem 4
CorrelationsDf = weather_tool.Correlations() 