# Helper 
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import glob 
import os
from datetime import datetime
from scipy import stats



class weather_data_tool():
    """
    This tool will get the direcroty of input data and target data to calculate the answer for four questions: 

    input data: 
        - minimum temperature
        - maximum temperature
        - precipitation 
    
    target data: 
        - corn grain yield 

    Problems: 
        - Problem 1: [MissingPrcpData]  
            calculate for each weather data file the number of days in which the maximum temperature and 
            minimum temperature data are present but the precipitation data is missing 

        - Problem 2: [YearlyAverages] 
            calculating for each weather stateiotns within each year the average min and max temp and totall accumelation prcp

        - Problem 3: [YearHistogram]
            tabulates how often each year from 1985-2014 had the highest average maximum temperature, highest average minimum temperature, 
            and highest total accumulated precipitation from the set of weather stations

        - Problem 4: [Correlations]
            calculate the Pearson correlation between these variables and the grain yield data for each weather station 

    """
    def __init__(self, input_data_path = None, target_data_path = None): 

        self.input_data_path  = input_data_path
        self.target_data_path = target_data_path


        self.answer_path      = './DataSciTest/answers/' 

        # list all the weather station data in directory and sort them: 
        all_txt_file_in_wx_data             = os.listdir(self.input_data_path) 
        self.sorted_all_txt_file_in_wx_data = sorted(all_txt_file_in_wx_data)

        # Reading the target file as a gloabl variable: 
        target_full_name_path = os.path.join(self.target_data_path, 'US_corn_grain_yield.txt') 
        self.yield_target     = pd.read_csv(target_full_name_path, on_bad_lines='skip', delimiter = "\t", header = None)
        self.yield_target.columns = ['Year', 'Yield']

    def MissingPrcpData(self):
        """
            calculate for each weather data file the number of days in which the maximum temperature and 
            minimum temperature data are present but the precipitation data is missing
        """

        MissOutput = pd.DataFrame(columns = ['WStation', 'NumMissingPrcpDate'])
        for idx, weather_stateion in enumerate(self.sorted_all_txt_file_in_wx_data): 
            full_name_path         = os.path.join(self.input_data_path, weather_stateion) 
            this_station_dataframe = pd.read_csv(full_name_path, on_bad_lines='skip', delimiter = "\t", header = None)
            this_station_dataframe.columns = ['Date', 'MaxTemp', 'MinTemp', 'Prcp']
            #print(f"{weather_stateion} : {this_station_dataframe.shape}")

            count_days_miss_temp =  len(this_station_dataframe[(this_station_dataframe.Prcp == -9999) & 
                                                            (this_station_dataframe.MaxTemp !=-9999) & 
                                                            (this_station_dataframe.MinTemp !=-9999)])

            MissOutput.loc[idx,:] = [weather_stateion, count_days_miss_temp]
            
        # Write the output in '.out' file called 'MissingPrcpData.out'
        _ = self.WriteDfTo(MissOutput, 'MissingPrcpData.out')

        return MissOutput


    def YearlyAverages(self):
        """
        calculating for each weather stateiotns within each year the average min and max temp and totall accumelation prcp
        """

        output = pd.DataFrame(columns = ['WStation', 'Year', 'MaxTempAvg', 'MinTempAvg', 'TotalAccPrcp'])
        idx = 0
        for weather_stateion in self.sorted_all_txt_file_in_wx_data: 
            full_name_path         = os.path.join(self.input_data_path, weather_stateion) 
            this_station_dataframe = pd.read_csv(full_name_path, on_bad_lines='skip', delimiter = "\t", header = None)
            this_station_dataframe.columns = ['Date', 'MaxTemp', 'MinTemp', 'Prcp']

            add_year_col_to_df_ = self.AddYearColToDF(this_station_dataframe) 

            group_by_year_df    = add_year_col_to_df_.groupby(by = 'Year')

            for year, this_year_df in group_by_year_df: 
                avg_max_temp     = this_year_df.loc[this_year_df['MaxTemp'] != -9999, 'MaxTemp'].mean() # ignoring the nan value -9999 
                avg_min_temp     = this_year_df.loc[this_year_df['MinTemp'] != -9999, 'MinTemp'].mean()
                accumelated_prep = this_year_df.loc[this_year_df['Prcp'] != -9999, 'Prcp'].sum()
                output.loc[idx,:] = [weather_stateion, year, avg_max_temp, avg_min_temp, accumelated_prep]

                idx+=1

        output['MaxTempAvg'] = output['MaxTempAvg'].apply(lambda x: round(x, 2)) # just keep two decimals values 
        output['MinTempAvg'] = output['MinTempAvg'].apply(lambda x: round(x, 2))

        # check if there is any nan anc convert to -9999
        output_with_no_nan = self.ConvertNanToValue(output)

        # Write the output in '.out' file called 'YearlyAverages.out'
        _ = self.WriteDfTo(output_with_no_nan, 'YearlyAverages.out')

        return output_with_no_nan

    def YearHistogram(self):

        YearlyAverageDf = self.YearlyAverages()
        WStations_with_Years_HighValues = self.GetHighestValueYear(YearlyAverageDf)


        Years = YearlyAverageDf.Year.unique()

        YearFreq = pd.DataFrame(columns = ['Year', 'YearFreqHighMaxTempAvg', 'YearFreqHighMinTempAvg', 'YearFreqHighTotalAccPrcp'])

        for idx, Year in enumerate(Years):
            if Year in WStations_with_Years_HighValues['YearMaxTempAvg'].unique():
                YearFreqHighMaxTempAvg   = WStations_with_Years_HighValues['YearMaxTempAvg'].value_counts()[Year]
            else:
                YearFreqHighMaxTempAvg = 0

            if Year in WStations_with_Years_HighValues['YearMinTempAvg'].unique():
                YearFreqHighMinTempAvg   = WStations_with_Years_HighValues['YearMinTempAvg'].value_counts()[Year]
            else: 
                YearFreqHighMinTempAvg   = 0
            
            if Year in WStations_with_Years_HighValues['YearTotalAccPrcp'].unique():
                YearFreqHighTotalAccPrcp = WStations_with_Years_HighValues['YearTotalAccPrcp'].value_counts()[Year]
            else: 
                YearFreqHighTotalAccPrcp = 0

            YearFreq.loc[idx,:] = [Year, YearFreqHighMaxTempAvg, YearFreqHighMinTempAvg, YearFreqHighTotalAccPrcp]
        

        # Write the output in '.out' file called 'YearHistogram.out'
        _  = self.WriteDfTo(YearFreq, 'YearHistogram.out')

        # Plot the histogram and save as 'YearHistogram.png'
        _  = self.PlotYearHistogram(YearFreq, FigName = 'YearHistogram.png')

        return YearFreq


    def Correlations(self):
        """
        calculating for each weather stateiotns within each year the average min and max temp and totall accumelation prcp
        """

        YearlyAverageDf = self.YearlyAverages()

        WStationGroups = YearlyAverageDf.groupby(by = 'WStation')

        CorrOutput = pd.DataFrame(columns = ['WStation', 'PearsonMaxTempYield', 'PearsonMinTempYield', 'PearsonTtlPrcpYield'])

        for idx, (wstation, this_wstation_df) in enumerate(WStationGroups):
            
            # Check to consider only years in yield data which has input data: 

            this_wstation_df_years_mask = this_wstation_df['Year'].unique()
            Masked_Yield_data = self.yield_target[self.yield_target['Year'].isin(this_wstation_df_years_mask)]
            # Calculating the pearson correlation values: 
            PearsonMaxTempYield = stats.pearsonr(this_wstation_df['MaxTempAvg'], Masked_Yield_data['Yield'])[0]
            PearsonMinTempYield = stats.pearsonr(this_wstation_df['MinTempAvg'], Masked_Yield_data['Yield'])[0]
            PearsonTtlPrcpYield = stats.pearsonr(this_wstation_df['TotalAccPrcp'], Masked_Yield_data['Yield'])[0]

            CorrOutput.loc[idx,:] = [wstation, PearsonMaxTempYield, PearsonMinTempYield, PearsonTtlPrcpYield] 

        CorrOutput['PearsonMaxTempYield'] = CorrOutput['PearsonMaxTempYield'].apply(lambda x: round(x, 2))
        CorrOutput['PearsonMinTempYield'] = CorrOutput['PearsonMinTempYield'].apply(lambda x: round(x, 2))
        CorrOutput['PearsonTtlPrcpYield'] = CorrOutput['PearsonTtlPrcpYield'].apply(lambda x: round(x, 2))

        # Write the output in '.out' file called 'Correlations.out'
        _ = self.WriteDfTo(CorrOutput, 'Correlations.out')
        return CorrOutput

    
    def PlotYearHistogram(self, YearFreqDF, FigName = None): 

        fig, axs = plt.subplots(1, 1, figsize=(24,8))
        axs.set_facecolor('white')
        g = YearFreqDF.plot(x="Year", y=["YearFreqHighMaxTempAvg", "YearFreqHighMinTempAvg", "YearFreqHighTotalAccPrcp"], 
                                    ylabel  = 'Frequency', 
                                    kind="bar", 
                                    color= ['dimgray', 'goldenrod', 'tomato'], 
                                    width=0.7, rot=0, ax = axs)

        plt.setp(axs.xaxis.get_majorticklabels(), fontsize=16, rotation = 45)
        plt.yscale('log')
        plt.grid(False)
        plt.setp(axs.spines.values(), color='k')

        for bar in g.patches: 
            g.annotate(format(bar.get_height(), '.0f'),  
                        (bar.get_x() + bar.get_width() / 2,  
                            bar.get_height()), ha='center', va='center', 
                        size=12, xytext=(0, 6), 
                        textcoords='offset points') 
        x = 0.5
        for i in range(29):
            axs.axvline(x = x, linestyle = '--', color = '#C5C9C7', label = 'axvline - full height')
            x = x + 1


        YFHMaxT = Patch(color='dimgray', label='High Max Avg Temp')
        YFHMinT = Patch(color='goldenrod', label='High Min Avg Temp')
        YFHPcrp = Patch(color='tomato', label='High Total Acc Prcp')
        axs.legend(handles=[YFHMaxT, YFHMinT, YFHPcrp], loc='upper left')

        None
        plt.savefig(os.path.join(self.answer_path, FigName), dpi = 300) 


    def ConvertNanToValue(self, df):

        df = df.fillna(-9999.00)

        return df

    def GetHighestValueYear(self, WStationDfs):

        WStationGroups = WStationDfs.groupby(by = 'WStation')

        output = pd.DataFrame(columns = ['WStation', 'YearMaxTempAvg', 'YearMinTempAvg', 'YearTotalAccPrcp'])

        for idx, (wstation, this_wstation_df) in enumerate(WStationGroups):
            this_wstation_df = this_wstation_df.reset_index(drop=True)
            year_highest_max_temp  = this_wstation_df.loc[this_wstation_df['MaxTempAvg'].idxmax(), 'Year'] 
            year_highest_min_temp  = this_wstation_df.loc[this_wstation_df['MinTempAvg'].idxmax(), 'Year'] 
            year_highest_tacc_prep = this_wstation_df.loc[this_wstation_df['TotalAccPrcp'].idxmax(), 'Year'] 
            #print(f"{year_highest_max_temp} | {year_highest_min_temp} | {year_highest_tacc_prep}")
            output.loc[idx,:] = [wstation, year_highest_max_temp, year_highest_min_temp, year_highest_tacc_prep]


        return output 


    def WriteDfTo(self, df, outputfile_name = None): 

        full_output_name = os.path.join(self.answer_path, outputfile_name)

        isExist = os.path.exists(full_output_name)

        if isExist: 
            print("The file is already exist!")
        else: 
            df.to_csv(full_output_name, header = None, index = None, sep='\t', mode = 'a') 


    def AddYearColToDF(self, df):

        year_col = [datetime.strptime(str(row['Date']), '%Y%m%d').year for _,row in df.iterrows()]
        df.insert(loc = 1, column = 'Year', value = year_col) 

        return df 







