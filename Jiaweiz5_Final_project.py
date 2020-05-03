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
import numpy as np


def avgChRateOfCountries(df , num_of_country, start_point):
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
food_consumption = pd.read_csv('InternationalFoodConsumption.csv')

# Hypothesis 1
income = metadata_agriculture['IncomeGroup'].tolist()
income = pd.DataFrame(income, columns = ['Country Income'])

country_name = agriculture_land.T.iloc[0].tolist()
df_country_name = pd.DataFrame(country_name, columns = ['Country Name'])

avg_ch_rate_agriculture = avgChRateOfCountries(agriculture_land , 263, 4)
df_agr = pd.DataFrame(avg_ch_rate_agriculture, columns = ['slope_agr'])

country_agr = pd.concat([df_country_name, df_agr],axis=1, join='inner')
df = pd.concat([df_country_name, income, df_agr],axis=1, join='inner')


# Hypothesis 2 (GDP in 2010)

gdp_str = GDP.set_index('year').iloc[-3].tolist()
gdp = stringToFloat(gdp_str)
gdp_2008 = pd.DataFrame(gdp, columns = ['GDP_2008'])
gdp_list = list(GDP)[1:]
gdp_list = [x.rstrip(' ') for x in gdp_list]

df_gdp = pd.DataFrame(gdp_list, columns = ['Country Name'])

df_gdp = pd.concat([df_gdp, gdp_2008],axis=1).dropna()
df_gdp.columns = df_gdp.columns.str.rstrip()
df = pd.merge(df, df_gdp, how = 'inner', on = ['Country Name'])
avg_ch_rate_for = avgChRateOfCountries(forest_cov, 263,4)
df_for = pd.DataFrame(avg_ch_rate_for, columns = ['slope_forest'])
for_2008 = forest_cov['2008'].tolist()
forest_2008 = pd.DataFrame(for_2008, columns = ['Forest_2008_% of land area'])
df_merge = pd.concat([df_country_name, income,df_agr, df_for, forest_2008],axis=1, join='inner')

df_1 = pd.merge(df_merge, df_gdp, how = 'inner', on = ['Country Name'])
df_final = df_1.sort_values('GDP_2008')
print(df_final)
