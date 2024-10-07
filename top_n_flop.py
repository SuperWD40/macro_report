import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker
import ipywidgets as widgets
from IPython.display import display

class top_n_flop():
    def __init__(self, history):
        # Assigning input parameters to instance variables
        date = history.index[-1]
        self.date = date
        self.history = history
        self.range_dict = {
            '1D'    : date - pd.Timedelta(days=1),
            '1W'    : date - pd.Timedelta(days=7),
            '1M'    : date - pd.Timedelta(days=30),
            '3M'    : date - pd.Timedelta(days=30 * 3),
            '6M'    : date - pd.Timedelta(days=30 * 6),
            'YTD'   : pd.Timestamp(year=date.year, month=1, day=1),
            '1Y'    : date - pd.Timedelta(days=365),
            '2Y'    : date - pd.Timedelta(days=365*2),
            '5Y'    : date - pd.Timedelta(days=365*5),
            '10Y'   : date - pd.Timedelta(days=365*10),
        }
    
    def plot(self, range, n_stock): 
        df = self.history.resample('D').ffill()
        df = (df.loc[self.date] - df.loc[self.range_dict[range]]) / df.loc[self.range_dict[range]]
        df = df.dropna()

        df_first = (df.sort_values().tail(n_stock) * 100).round(2)
        df_last = (df.sort_values().head(n_stock) * 100).round(2)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        df_first.sort_values(ascending=True).plot(kind='barh', color='g', ax=ax2)
        df_last.sort_values(ascending=False).plot(kind='barh', color='r', ax=ax1)

        # Représenter à droite l'axe y du graphique 2
        ax2.yaxis.set_ticks_position('right')

        ax1.set_xlim([df_last.min()*1.2, 0])
        ax2.set_xlim([0, df_first.max()*1.2])

        # Afficher les variations directement sur le graphique
        for i, v in enumerate(df_last.sort_values(ascending=False)):
            ax1.text(df_last.min()*0.2+v, i, f"{v:.2f}%", color='r')
        for i, v in enumerate(df_first):
            ax2.text(df_first.min()*0.05+v, i, f"{v:.2f}%", color='g')

        # Afficher l'échelle x uniquement en entier
        ax1.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))

        # Insérer un titre
        fig.suptitle('Top and flop CAC 40', y=0.95)

        # Ajuster l'écart entre les deux graphiques
        fig.subplots_adjust(wspace=0.05)

        plt.show()
        
    def show(self):
        """Displaying interactive controls for selecting frequency and time range"""
        # Creating interactive controls for selecting frequency and time range
        controls = widgets.interactive(
            self.plot,
            range=widgets.Select(options=['1D', '1W', '1M', '3M', '6M', 'YTD', '1Y', '2Y', '5Y', '10Y'], value='1M'),
            n_stock=widgets.IntText(value=5, description='N stocks:', disabled=False)
        )

        # Displaying the interactive controls
        display(controls)