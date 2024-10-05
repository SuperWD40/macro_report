import requests
import pandas as pd
import io
import numpy as np

import matplotlib.pyplot as plt

import ipywidgets as widgets
from IPython.display import display

class yield_curve:
    def __init__(self):
        """
        Initializes the yield_curve class.
        
        Attributes:
        - range_dict: Dictionary mapping time ranges to corresponding dates.
        - _oat_df: Placeholder for fetched French Treasury bond data.
        - _tbond_df: Placeholder for fetched US Treasury bond data.
        """
        # Initialization method
        today = pd.Timestamp.today().normalize()
        
        # Dictionary defining time ranges and corresponding dates
        self.range_dict = {
            '1D'    : today - pd.Timedelta(days=1),
            '1W'    : today - pd.Timedelta(days=7),
            '1M'    : today - pd.Timedelta(days=30),
            '3M'    : today - pd.Timedelta(days=30 * 3),
            '6M'    : today - pd.Timedelta(days=30 * 6),
            'YTD'   : pd.Timestamp(year=today.year, month=1, day=1),
            '1Y'    : today - pd.Timedelta(days=365),
            '2Y'    : today - pd.Timedelta(days=365*2),
            '5Y'    : today - pd.Timedelta(days=365*5),
            '10Y'   : today - pd.Timedelta(days=365*10),
        }
        
        # Placeholder for fetched US Treasury bond data
        self._tbond_df = None
        
        # Placeholder for fetched French Treasury bond data
        self._oat_df = None

    def tbond(self):
        """
        Fetches US Treasury bond data.
        
        Returns:
        - DataFrame: Pandas DataFrame containing US Treasury bond data.
        """
        # Method to fetch US Treasury bond data
        if self._tbond_df is None:
            # Generate a list of years to fetch data for the last 10 years
            year_dict = [(pd.Timestamp.now() - pd.Timedelta(days=365.25*n)).strftime('%Y') for n in range(0,11)]
            df = pd.DataFrame()
            for year in year_dict:
                # Construct the URL to fetch data for each year
                url = f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv'
                response = requests.get(url, headers={'User-Agent': 'Safari/537.36'}, timeout= 10)
                csv_file = io.StringIO(response.text)
                data = pd.read_csv(csv_file, index_col='Date')
                data.index = pd.to_datetime(data.index)
                df = pd.concat([df, data], axis=0)

            # Sort and fill missing values
            df = df.sort_index()
            df = df.resample('D').ffill()
            df = df.apply(lambda row: row.fillna((row.shift(1) + row.shift(-1)) / 2), axis=1)
            self._tbond_df = df
        return self._tbond_df
    
    def oat(self):
        """
        Fetches French Treasury bond data.
        
        Returns:
        - DataFrame: Pandas DataFrame containing French Treasury bond data.
        """
        # Method to fetch French Treasury bond data
        if self._oat_df is None:
            # Fetch data from the Banque de France website
            url = 'https://dataweb-laval.jouve-hdi.com/fr/downloadFile.do?id=5385693&exportType=csv'
            response = requests.get(url, headers={'User-Agent': 'Safari/537.36'}, timeout= 10)
            csv_file = io.StringIO(response.text)
            df = pd.read_csv(csv_file, header=5, sep = ';')

            # Clean and process the data
            columns = ['Date', '1 Yr', '10 Yr', '15 Yr', '2 Yr', '20 Yr', '25 Yr', '3 Yr', '30 Yr', '5 Yr', '7 Yr']
            df.columns = columns
            df = df.set_index('Date')
            df.index = pd.to_datetime(df.index, format="%d/%m/%Y")
            df = df.replace('-', np.nan)
            df = df.replace(',', '.', regex=True)
            df = pd.concat([pd.to_numeric(df[col], errors='coerce') for col in df.columns], axis=1)
            
            # Sort and fill missing values
            df = df.sort_index()
            df = df[['1 Yr', '2 Yr', '3 Yr', '5 Yr', '7 Yr', '10 Yr', '15 Yr', '20 Yr', '25 Yr', '30 Yr']]
            df = df.resample('D').ffill()
            self._oat_df = df
        return self._oat_df
    
    def plot(self, treasury, dates):
        """
        Plots the yield curve for the selected treasury and dates.
        
        Parameters:
        - treasury (str): Type of treasury, 'FR' for French or 'US' for US.
        - dates (list): List of selected date ranges.
        """
        # Method to plot the yield curve
        if treasury == 'FR':
            df = self.oat()
        elif treasury == 'US':
            df =  self.tbond()
        else:
            raise ValueError("Invalid treasury: must be 'FR' or 'US'")

        # Select data based on selected date ranges
        range = [self.range_dict[n] for n in dates]
        df = df.loc[range]
        df.index = dates
        df.T.plot(
            legend=True, 
            title=f'{treasury} Yield curve', 
            figsize=(10,5)
        )

        plt.show()

    def show(self):
        """
        Displays interactive controls for selecting treasury and dates.
        """
        # Method to display interactive controls for selecting treasury and dates
        controls = widgets.interactive(
        self.plot,
        treasury=widgets.Select(options=['FR', 'US'], value='US', description='Treasury:'),
        dates=widgets.SelectMultiple(options=['1D', '1W', '3M', '6M', 'YTD', '1Y', '2Y', '5Y', '10Y'], value=['1D', '1W', '1Y'], description='Dates')
        )
        
        # Displaying the interactive controls
        display(controls)
