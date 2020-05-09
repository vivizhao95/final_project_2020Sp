import pandas as pd
import matplotlib.pyplot as plt


def ConvertColToDF(df_input, trans: bool, index: int or str, column_name: str):
    """
    this function helps you convert a specific column in a dataframe to a new dataframe,
    in order to operate on it (ie. merge, concatenate etc.)
    :param df_input: input dataframe
    :param trans: whether the dataframe needs transpose
    :param index: column index, it can be either your index number or the column name
    :param column_name: new column name, its like rename the column for convenience
    :return: a dataframe
    >>> df_input = pd.read_csv('Doctest_ConvertColToDF.csv')
    >>> ConvertColToDF(df_input, True, 0, 'Country Name')
               Country Name
    0            Arab World
    1  United Arab Emirates
    2             Argentina
    3               Armenia
    4        American Samoa

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


def determineRelation(df, column1: int, column2: int):
    """
    this function is used to calculate the product of the values in column 1 and column 2, looping through the whole dataframe.
    if the product > 0, the 2 values are to the same direction (both positive or negative);
    if the product < 0, the 2 values are to the different direction (one is positive and another is negative);
    all else are Nans
    :param df: input dataframe
    :param column1: column index
    :param column2: column index
    :return:
    a list of results:
    if the product > 0, return 'Positive';
    if the product < 0, return 'Negative';
    all else return 'Nan'.
    >>> df = pd.read_csv('Doctest_determineRelation.csv')
    >>> determineRelation(df,0,1)
    ['Positive', 'Negative', 'Positive']
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
    this function is used to calculate the accumulative average change rate in same column in a dataframe.
    :param df: the dataframe needed to be processed
    :param num_of_country: number of rows in that column
    :param start_point: the starting row number in the dataframe
    :return:

    >>> df = pd.read_csv('Doctest_avgChRateOfCountries.csv')
    >>> avgChRateOfCountries(df, 8,4)
    [0.0, 0.0, -0.0021009663354085587, -0.0008981021680112534, 0.0, -0.001127876537652574, 0.01081939372755308, -0.009966727608890759]
    """
    avg_ch_rate = []
    for i in range(num_of_country):
        val = df.loc[i].iloc[start_point:].pct_change(fill_method='ffill').mean(skipna=True)
        avg_ch_rate.append(val)

    return avg_ch_rate


def stringToFloat(list):
    """
    this function converts a list of strings to float, the string should be formatted like: '2,012'.
    :param list: the list of string
    :return: a list of float
    >>> list = ['2,012','2,013','2,014']
    >>> stringToFloat(list)
    [2012.0, 2013.0, 2014.0]
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

# slice the columns needed, transpose them is needed
income = ConvertColToDF(metadata_agriculture, False, 'IncomeGroup', 'Country Income')

df_country_name = ConvertColToDF(agriculture_land, True, 0, 'Country Name')

df_country_code = ConvertColToDF(agriculture_land, True, 1, 'Country Code')

# calculate the avg change rate in this dataframe
avg_ch_rate_agriculture = avgChRateOfCountries(agriculture_land, 263, 4)

#convert it into a dataframe
df_agr = pd.DataFrame(avg_ch_rate_agriculture, columns=['slope_agr'])

# merge all the dataframes to a new one for analysis
country_agr = pd.concat([df_country_name, df_agr], axis=1, join='inner')
df = pd.concat([df_country_name, df_country_code, income, df_agr], axis=1, join='inner')

# select GDP for year 2008 and do some data formation
gdp_str = GDP.set_index('year').iloc[-3].tolist()
gdp = stringToFloat(gdp_str)
gdp_2008 = pd.DataFrame(gdp, columns=['GDP_2008'])
gdp_list = list(GDP)[1:]
gdp_list = [x.rstrip(' ') for x in gdp_list]

# organize is into a dataframe
df_gdp = pd.DataFrame(gdp_list, columns=['Country Name'])

df_gdp = pd.concat([df_gdp, gdp_2008], axis=1).dropna()
df_gdp.columns = df_gdp.columns.str.rstrip()

# calculate the avg change rate of forest for each country
avg_ch_rate_for = avgChRateOfCountries(forest_cov, 263, 4)
df_for = pd.DataFrame(avg_ch_rate_for, columns=['slope_forest'])

# for better analysis, we also select data for year 2008
forest_2008 = ConvertColToDF(forest_cov,False, '2008', 'Forest_2008_% of land area')
df_merge = pd.concat([df_country_name, df_country_code, income, df_agr, df_for, forest_2008], axis=1, join='inner')

# merge GDP dataframe with other dataframes
df_final = pd.merge(df_merge, df_gdp, how='inner', on=['Country Name'])

# sort the df by column GDP_2008 in order to plot
df_sort = df_final.sort_values('GDP_2008')

"""Hypothesis 2 (GDP in 2010)"""

df_sort.plot(y='Forest_2008_% of land area', x='GDP_2008', style='o')

df_2 = df_sort.groupby('Country Income').mean().sort_values('GDP_2008')
df_2.plot(x='Forest_2008_% of land area', y='GDP_2008')

# there is a moderate positive correlation between the GDP and the forest coverage of a country.
# to see it more clearly, groupby the data by 'Income level', and the graph shows a clear positive linear relationship.
# therefore, we may reject the second hypothesis.

"""Hypothesis 1"""
relation_agr_forest = determineRelation(df_final, 3, 4)
df_relation_agr_forest = pd.DataFrame(relation_agr_forest, columns=['linear relation agr forest'])

df_withrelation = pd.concat([df_final, df_relation_agr_forest], axis=1, join='inner')

counts = df_withrelation['linear relation agr forest'].value_counts()
counts_neg = counts['Negative']
counts_pos = counts['Positive']
total = counts_neg + counts_pos
# print(counts_neg/total)
# the result is roughly 70%, which means 70% of countries shows a negative correlation between the 2 variables.
# hence, we accept the hypothesis.

"""Hypothesis 3"""
#  also select data for year 2008 to analyse
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

# there seems no correlation between the 2 variables:
# even if we groupby the data by 'Income level', the result didnt change
# hence, we reject the hypothesis

plt.show()


