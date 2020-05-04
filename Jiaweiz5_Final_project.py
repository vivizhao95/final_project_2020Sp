"""
Title: Analyse Potential Factors Affecting Forest Cover Rate of Different Countries

team member: Jiawei Zhao

Github ID: vivizhao95

Hypothesis 1: there would be a negative correlation between the  agriculture land hold by a country and the forest coverage.

Hypothesis 2: there would be a negative correlation between the GDP and the forest coverage of a country.

Hypothesis 3: if a country consumes more meat per capita, the country would have a lower forest coverage. (livestock requires agriculture lands)

source:

1. Agricultural land (% of land area)

https://data.worldbank.org/indicator/ag.lnd.frst.zs

2. Forest land (% of land area)

https://data.worldbank.org/indicator/AG.LND.AGRI.ZS

3. GDP by country

https://www.kaggle.com/jtennis/gdp-by-country-the-maddisonproject/data

4. Meat Consumption by country

https://data.world/oecd/meat-consumption

"""
import pandas as pd
import matplotlib.pyplot as plt


def ConvertColToDF(df_input, trans: bool, index: int or str, column_name: str):
    """

    :param df_input:
    :param trans:
    :param index:
    :param column_name:
    :return:
    """
    if trans is True:
        df_input = df_input.T

    if type(index) is int:
        list_output = df_input.iloc[index].tolist()
        df_output = pd.DataFrame(list_output, columns=[column_name])
    else:
        list_output = df_input[index].tolist()
        df_output = pd.DataFrame(list_output, columns=[column_name])

    return df_output


def determineRelation(df, column1, column2):
    """

    :param df:
    :param column1:
    :param column2:
    :return:
    """
    relation = []
    for i in range(len(df)):

        if df.iloc[i, column1] * df.iloc[i, column2] < 0:
            relation.append('Negative')
        elif df.iloc[i, column1] * df.iloc[i, column1] > 0:
            relation.append('Positive')
        else:
            relation.append('Nan')
    return relation


def avgChRateOfCountries(df, num_of_country, start_point):
    """

    :param df: the dataframe needed to be processed
    :param num_of_country:
    :param start_point:
    :return:
    """
    avg_ch_rate = []
    for i in range(num_of_country):
        val = df.loc[i].iloc[start_point:].pct_change(fill_method='ffill').mean(skipna=True)
        avg_ch_rate.append(val)

    return avg_ch_rate


def stringToFloat(list):
    """

    :param list:
    :return:
    """
    for i in range(0, len(list)):
        if type(list[i]) == str:
            list[i] = float(list[i].replace(',', ''))
    return list


# import data
forest_cov = pd.read_csv('Forest_land.csv')
agriculture_land = pd.read_csv('Agriculture_land.csv')
metadata_agriculture = pd.read_csv('Metadata_Agriculture.csv')
metadata_forest_cov = pd.read_csv('Metadata_forest.csv')
GDP = pd.read_csv('GDP.csv')
meat_consumption = pd.read_csv('meat_consumption.csv')

income = ConvertColToDF(metadata_agriculture, False, 'IncomeGroup', 'Country Income')

df_country_name = ConvertColToDF(agriculture_land, True, 0, 'Country Name')

df_country_code = ConvertColToDF(agriculture_land, True, 1, 'Country Code')

avg_ch_rate_agriculture = avgChRateOfCountries(agriculture_land, 263, 4)
df_agr = pd.DataFrame(avg_ch_rate_agriculture, columns=['slope_agr'])

country_agr = pd.concat([df_country_name, df_agr], axis=1, join='inner')
df = pd.concat([df_country_name, df_country_code, income, df_agr], axis=1, join='inner')

gdp_str = GDP.set_index('year').iloc[-3].tolist()
gdp = stringToFloat(gdp_str)
gdp_2008 = pd.DataFrame(gdp, columns=['GDP_2008'])
gdp_list = list(GDP)[1:]
gdp_list = [x.rstrip(' ') for x in gdp_list]

df_gdp = pd.DataFrame(gdp_list, columns=['Country Name'])

df_gdp = pd.concat([df_gdp, gdp_2008], axis=1).dropna()
df_gdp.columns = df_gdp.columns.str.rstrip()

avg_ch_rate_for = avgChRateOfCountries(forest_cov, 263, 4)
df_for = pd.DataFrame(avg_ch_rate_for, columns=['slope_forest'])

forest_2008 = ConvertColToDF(forest_cov,False, '2008', 'Forest_2008_% of land area')
df_merge = pd.concat([df_country_name, df_country_code, income, df_agr, df_for, forest_2008], axis=1, join='inner')

df_final = pd.merge(df_merge, df_gdp, how='inner', on=['Country Name'])
df_sort = df_final.sort_values('GDP_2008')

# Hypothesis 2 (GDP in 2010)
df_sort.plot(y='Forest_2008_% of land area', x='GDP_2008', style='o')

df_2 = df_sort.groupby('Country Income').mean().sort_values('GDP_2008')
df_2.plot(x='Forest_2008_% of land area', y='GDP_2008')

# Hypothesis 1
relation_agr_forest = determineRelation(df_final, 3, 4)
df_relation_agr_forest = pd.DataFrame(relation_agr_forest, columns=['linear relation agr forest'])

df_withrelation = pd.concat([df_final, df_relation_agr_forest], axis=1, join='inner')

counts = df_withrelation['linear relation agr forest'].value_counts()
counts_neg = counts['Negative']
counts_pos = counts['Positive']
total = counts_neg + counts_pos
# print(counts_neg/total)

# Hypothesis 3
df_meat_1 = meat_consumption.loc[meat_consumption['TIME'] == 2008]
df_meat = df_meat_1.loc[meat_consumption['MEASURE'] == 'KG_CAP']

df_meat_2008 = df_meat.groupby('LOCATION').mean().drop(columns='Flag Codes').drop(columns='TIME')
df_withmeat = pd.merge(df_final, df_meat_2008, how='left', left_on=['Country Code'], right_on=['LOCATION']).dropna()
df_sort_value = df_withmeat.sort_values('Value')
df_sort_value.rename(index=str, columns={'Value': 'Meat_consumption_KG_CAP'}, inplace=True)

df_sort_value.plot(y='Forest_2008_% of land area', x='Meat_consumption_KG_CAP')
df_sort_value.plot(y='GDP_2008', x='Meat_consumption_KG_CAP', style='o')
df_group_by_income = df_sort_value.groupby('Country Income').mean().sort_values('Meat_consumption_KG_CAP')
df_group_by_income.plot(y='Forest_2008_% of land area', x='Meat_consumption_KG_CAP')

plt.show()
