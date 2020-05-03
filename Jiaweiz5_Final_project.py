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
# import data
forest_cov = pd.read_csv('Forest_land.csv')
agriculture_land = pd.read_csv('Agriculture_land.csv')
metadata_agriculture = pd.read_csv('Metadata_Agriculture.csv')
metadata_forest_cov = pd.read_csv('Metadata_forest.csv')
GDP = pd.read_csv('GDP.csv')
food_consumption = pd.read_csv('InternationalFoodConsumption.csv')

#Hypothesis 1: there would be a negative correlation between the agriculture land hold by a country and the forest coverage.


avg_ch_rate_agriculture = avgChRateOfCountries(agriculture_land , 263, 4)

print(avg_ch_rate_agriculture)
