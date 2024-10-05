import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

# Miner les données
x_history = yf.Ticker('^VIX').history('max')['Close']
x_history.name = 'VIX monthly average'
y_history = yf.Ticker('^TNX').history('max')['Close']
y_history.name = 'US 10y monthly average'

# Cacluler la moyenne des séries sur un 25 périodes
df = pd.concat([x_history, y_history], axis=1).dropna()
df = df.rolling(25).mean().dropna()
df = df.resample('M').last()

# Tracer le nuage de point et les droites
df.plot(
    kind='scatter',
    x=x_history.name, 
    y=y_history.name, 
    figsize=(10, 5), 
    color = 'grey', 
    marker='.',
    title = 'Risk and Reward climate indicator'
)
plt.axvline(x=25, color='black', linewidth=1)
plt.hlines(y=3, xmin=-1000000000, xmax=1000000000, color='black', linewidth=1)

# Définir les limites des axes x et y pour centrer le graphique
x_margin = np.percentile(df[x_history.name], 90) - np.percentile(df[x_history.name], 10)
y_margin = np.percentile(df[y_history.name], 90) - np.percentile(df[y_history.name], 10)
plt.xlim(25 - x_margin, 25 + x_margin)
plt.ylim(3 - y_margin, 3 + y_margin)

# Tracer le dernier point de la série en rouge
plt.scatter(x = df[x_history.name].iloc[-1], y = df[y_history.name].iloc[-1], color='red')

# Ajouter une légende à côté du point rouge
plt.annotate(
    'now', 
    xy=(df[x_history.name].iloc[-1], df[y_history.name].iloc[-1]),
    xytext=(5, -5),
    textcoords='offset points', 
    color='red', 
    fontsize=10
)

# Afficher le graphique et le sauvegarder dans le sous-dossier Figures
plt.show()