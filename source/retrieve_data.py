import datadotworld as dw
import sqlite3
import datetime
import requests
import pandas as pd

path_db = '../db/data_covid19.db'
conn_str = 'sqlite:///{}'.format(path_db)
dataSet_key = 'covid-19-data-resource-hub/covid-19-case-counts'

dt_missing = {
    'AI': 'AIA',
    'BQ': 'BES',
    'BL': 'BLM',
    'CZ': 'CZE',
    'FK': 'FLK',
}


def df2table(df, table, con=None):
    """
    Upersts into a table a dataframe.

    :param df:
    :param table:
    :param con:
    :return:
    """
    if con is None:
        con = sqlite3.connect(path_db)
        commit = True

    else:
        commit = False

    cur_sqlite = con.cursor()

    columns = ', '.join(df.columns)
    placeholders = ', '.join(['?'] * len(df.columns))
    sql_upsert = """
    INSERT OR REPLACE INTO {} ({}) VALUES ({})
    """.format(table, columns, placeholders)
    cur_sqlite.executemany(sql_upsert, df.values.tolist())

    if commit:
        con.commit()
        con.close()


def get_total_data_dw():
    # intro_dataset = dw.load_dataset('covid-19-data-resource-hub/covid-19-case-counts')
    # print(intro_dataset.describe())
    results = dw.query(dataSet_key, "SELECT * FROM covid_19_cases")
    df = results.dataframe
    df['prep_flow_runtime'] = df['prep_flow_runtime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df.to_sql(name='covid19_wd', con=conn_str, if_exists='replace', index=False)


def get_data_oecd_wd():
    df_oecd_pop = pd.read_csv('https://query.data.world/s/4vlxqub3dfjnd2o3wmafiupfywehgd')
    df_oecd_pop.to_sql(name='oecd_population', con=conn_str, if_exists='fail', index=False)

    df_oecd_eld = pd.read_csv('https://query.data.world/s/7iwddjynxxnpjnsha3555hx5an2zqh')
    df_oecd_eld.to_sql(name='oecd_elderly', con=conn_str, if_exists='fail', index=False)

    df_oecd_yng = pd.read_csv('https://query.data.world/s/b6hcfe3wdgslapzzgwroezdzq7frby')
    df_oecd_yng.to_sql(name='oecd_young', con=conn_str, if_exists='fail', index=False)

    df_oecd_wap = pd.read_csv('https://query.data.world/s/ej3cfdvz5nh23tvhyfohnmf5ixp6zb')
    df_oecd_wap.to_sql(name='oecd_working_age', con=conn_str, if_exists='fail', index=False)


def update_data_dw(date_update):
    query = """
    SELECT *
    FROM covid_19_cases
    WHERE date = '{}'
    """.format(date_update)

    results = dw.query(dataSet_key, query)
    df = results.dataframe
    df['prep_flow_runtime'] = df['prep_flow_runtime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df2table(df, table='total_cases')


def run_update_dw():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    update_data_dw(yesterday)


def get_data_ecdc(date_data=None):
    if date_data is None:
        date_data = datetime.date.today()

    if not isinstance(date_data, datetime.date):
        date_data = datetime.datetime.strptime(date_data, '%Y-%m-%d').date()

    filename = 'COVID-19-geographic-disbtribution-worldwide-{:%Y-%m-%d}.xlsx'.format(date_data)
    url = 'https://www.ecdc.europa.eu/sites/default/files/documents/{}'.format(filename)
    req = requests.get(url)

    with open('../data/{}'.format(filename), 'wb') as f:
        f.write(req.content)

    df = pd.read_excel('../data/{}'.format(filename), dtype={'GeoId': str}, keep_default_na=False)

    for alpha2Code in dt_missing:
        df.loc[df['geoId'] == alpha2Code, 'countryterritoryCode'] = dt_missing[alpha2Code]

    df.to_sql(name='covid19_ecdc', con=conn_str, index=False, if_exists='replace')


def get_total_data():
    get_total_data_dw()
    get_data_oecd_wd()
    get_data_ecdc()


if __name__ == '__main__':
    # get_total_data()
    # run_update()
    get_data_ecdc()
    pass
