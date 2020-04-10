import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

path_db = '../db/data_covid19.db'
conn_str = 'sqlite:///{}'.format(path_db)

df_cases = pd.read_sql_table('covid19_ecdc_daily_cases', conn_str)
df_daily_cases = pd.pivot(df_cases, index='Days', columns='GeoId', values='Total_Cases')
df_daily_deaths = pd.pivot(df_cases, index='Days', columns='GeoId', values='Total_Deaths')

df_daily_cases.drop(['CN', 'IT', 'IR'], axis=1).head(30).plot()
df_daily_cases['CO'].head(30).plot(color='red')

# sns.catplot(x='Days', y='Total_Cases', hue='GeoId', data=df_cases)
plt.show()
