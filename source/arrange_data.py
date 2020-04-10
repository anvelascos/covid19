import pandas as pd
from datetime import date
from retrieve_data import df2table, get_data_ecdc
import sqlite3

path_db = '../db/data_covid19.db'
conn_str = 'sqlite:///{}'.format(path_db)


def update_first_case():
    query = """
    SELECT countryterritoryCode as alpha3Code, min(dateRep) as dateFirstCase
    FROM covid19_ecdc
    WHERE cases > 0
    OR deaths > 0
    GROUP BY countryterritoryCode
    ORDER BY alpha3Code ASC
    """

    df_first_case = pd.read_sql(query, conn_str)
    df_first_case['dateFirstCase'] = pd.to_datetime(df_first_case['dateFirstCase'])
    df_first_case['dateFirstCase'] = df_first_case['dateFirstCase'].dt.strftime('%Y-%m-%d')

    df_first_case.to_sql('covid19_ecdc_first_case', conn_str, if_exists='replace', index=False)


def update_hundred_case():
    query = """
    SELECT alpha3Code, min(date) as dateHundredCase
    FROM covid19_ecdc_daily_cases
    WHERE totalCases >= 100
    GROUP BY alpha3Code
    ORDER BY alpha3Code ASC
    """

    df_hundred_case = pd.read_sql(query, conn_str)
    df_hundred_case['dateHundredCase'] = pd.to_datetime(df_hundred_case['dateHundredCase'])
    df_hundred_case['dateHundredCase'] = df_hundred_case['dateHundredCase'].dt.strftime('%Y-%m-%d')

    df_hundred_case.to_sql('covid19_ecdc_hundred_case', conn_str, if_exists='replace', index=False)


def arrange_data():
    df_date_first_case = pd.read_sql_table('covid19_ecdc_first_case', conn_str)
    df_date_first_case['dateFirstCase'] = pd.to_datetime(df_date_first_case['dateFirstCase'])

    df_total_cases = pd.read_sql_table('covid19_ecdc', conn_str)
    df_total_cases['dateRep'] = pd.to_datetime(df_total_cases['dateRep'])
    df_total_cases.drop(['year', 'month', 'day', 'countriesAndTerritories', 'popData2018'], inplace=True, axis=1)

    today = date.today()
    cols = ['alpha3Code', 'cases', 'deaths']

    for i, row in df_date_first_case.iterrows():
        alpha3Code = row['alpha3Code']
        date_first_case = row['dateFirstCase']
        print(alpha3Code)

        rng_dates = pd.date_range(date_first_case, today, freq='D', name='date')
        df_country_daily = pd.DataFrame(index=rng_dates, columns=cols)
        df_country_daily[['cases', 'deaths']] = 0

        idx_country = df_total_cases['countryterritoryCode'] == alpha3Code
        df_country = df_total_cases[idx_country].copy()
        df_country.set_index('dateRep', drop=True, inplace=True)
        idx_drop = df_country[(df_country['cases'] == 0) & (df_country['deaths'] == 0)].index
        df_country.drop(idx_drop, errors='ignore', inplace=True)

        df_country_daily.loc[df_country.index] += df_country
        df_country_daily['alpha3Code'] = alpha3Code
        df_country_daily['totalCases'] = df_country_daily['cases'].cumsum()
        df_country_daily['totalDeaths'] = df_country_daily['deaths'].cumsum()
        df_country_daily.reset_index(inplace=True)
        df_country_daily.index.name = 'days'
        df_country_daily.reset_index(inplace=True)
        df_country_daily['date'] = df_country_daily['date'].dt.strftime('%Y-%m-%d')

        try:
            df2table(df_country_daily, table='covid19_ecdc_daily_cases')

        except sqlite3.OperationalError:
            df_country_daily.to_sql('covid19_ecdc_daily_cases', conn_str, index=False, if_exists='replace')


def arrange_100_data():
    df_daily = pd.read_sql_table('covid19_ecdc_daily_cases', con=conn_str)
    df_daily.drop('days100', axis=1, inplace=True)
    cols = ['days', 'date', 'alpha3Code', 'totalCases', 'totalDeaths']
    df_daily_hundred = df_daily.loc[df_daily['totalCases'] >= 100, cols].copy()
    sr_start_100 = df_daily_hundred.groupby('alpha3Code')['days'].min()
    df_merge = df_daily_hundred.merge(sr_start_100, on=['alpha3Code'])
    df_merge['days100'] = (df_merge['days_x'] - df_merge['days_y'] + 1).astype(int)
    df_merge.drop(['totalCases', 'totalDeaths', 'days_x', 'days_y'], axis=1, inplace=True)
    df_output = df_daily.merge(df_merge, how='left', on=['date', 'alpha3Code'], copy=False)

    try:
        df2table(df_output, table='covid19_ecdc_daily_cases')

    except sqlite3.OperationalError as e:
        print(e)
        df_output.to_sql('covid19_ecdc_daily_cases', conn_str, index=False, if_exists='replace')


def update_data_ecdc():
    get_data_ecdc()
    update_first_case()
    arrange_data()
    arrange_100_data()


if __name__ == '__main__':
    update_data_ecdc()
    pass
