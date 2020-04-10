import pandas as pd
import plotly.express as px

path_db = '../db/data_covid19.db'
conn_str = 'sqlite:///{}'.format(path_db)

dt_names = {
    'totalCases': "Total Cases",
    'totalDeaths': "Total Deaths",
    'date': "Date",
    'days': "Days since first case reported",
    'days100': "Days since case number 100 reported",
    'alpha3Code': "Country Code"
}

df_continents_countries = pd.read_sql_table('countries', conn_str)

df_continents = df_continents_countries.groupby(['continent', 'continentCode']).size().reset_index()
dt_continents = [
    {
        'label': df_continents.loc[i, 'continent'],
        'value': df_continents.loc[i, 'continentCode']
    }
    for i in df_continents.index
]

df_countries = df_continents_countries.groupby(['country', 'alpha3Code']).size().reset_index()
dt_countries = [
    {
        'label': df_countries.loc[i, 'country'],
        'value': df_countries.loc[i, 'alpha3Code']
    }
    for i in df_countries.index
]


def get_countries_by_continent(continent=None):
    if continent:
        df_countries_by_continent = df_continents_countries[df_continents_countries['continentCode'] == continent]
        countries = df_countries_by_continent['alpha3Code'].values

    else:
        countries = []

    return countries


def get_data_plot(countries=None, cases='totalCases', units='people'):
    if countries:
        # print(countries)
        df_data = pd.read_sql_table('covid19_ecdc_daily_cases', conn_str)
        df_data_countries = df_data[df_data['alpha3Code'].isin(countries)].copy()

        df_data_countries.rename(columns=dt_names, inplace=True)

        fig_dates = px.line(
            data_frame=df_data_countries,
            x='Date',
            y=dt_names[cases],
            color='Country Code',
            title="Evolution of {} in time".format(dt_names[cases])
        )

        fig_days = px.line(
            data_frame=df_data_countries.dropna(),
            x='Days since case number 100 reported',
            y=dt_names[cases],
            color='Country Code',
            title="Number of {} since first case day".format(dt_names[cases])
        )

    else:
        fig_dates = None
        fig_days = None

    return [fig_dates, fig_days]


if __name__ == '__main__':
    # get_countries_by_continent('NA')
    get_data_plot(['COL', 'VEN'])
    pass
