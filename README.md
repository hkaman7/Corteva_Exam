### Notes:
- This is a class with four main function corresponding problems. 
- The name of main functions are exactly same as expected output names. 
- 

### Dependecies: 
Libraries: numpy, pandas, matplotlib, scipy , seaborn 


### Usage: 
- There are two main run files in python and notebook format
- First need to run the class object and then using the corresponding problem's function as in Notebook 

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
