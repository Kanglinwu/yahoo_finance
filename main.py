from flask import Flask, render_template, request, redirect, url_for
from yahooquery import Ticker
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import re
import requests
import datetime

stocks = Ticker('aapl')

## Refer - https://github.com/dpguthrie/yahooquery

# stock_asset_profile = stocks.asset_profile
# stock_esg_scores = stocks.esg_scores
# stock_financial_data = stocks.financial_data
# stock_key_stats = stocks.key_stats

returndict = lambda a: a['aapl']
# print('Asset profile start')
# print(returndict(stock_asset_profile))
# print('#########')
# print('Esg Scores start')
# print(returndict(stock_esg_scores))
# print('#########')

# temp remark #
# print('Page1 - Free Cash Flow (unit: M) - (B9, C9, D9, E9):')
# print('Page1 - Revenue (unit: M) - (B12, C12, D12, E12):')
# print('Page1 - Net income (unit: M) - (B13, C13, D13, E13):')

dict_financial_data = stocks.financial_data
print('Current Price: ', returndict(dict_financial_data)['currentPrice'])

try:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    headers = {"User-Agent": user_agent}  #请求头,headers是一个字典类型
    html_wacc = requests.get(f'https://www.gurufocus.com/term/wacc/aapl/WACC-', headers=headers).text
    soup_for_wacc = BeautifulSoup(html_wacc, "lxml")
    target_h1 = soup_for_wacc.find("h1")
    target_wacc = target_h1.next_sibling.text
    get_number_only_array = re.findall(r'[0-9]+.',target_wacc)
    wacc_str = "".join(get_number_only_array)
    print(f'Page1 - Personal Required Rate of Return - wacc (B4): {wacc_str}')
except Exception as e:
    print(e)


dict_key_stats = stocks.key_stats
print('Page1 - Shares Outstanding: ', returndict(dict_key_stats)['sharesOutstanding'])

# temp remark #

df_cash_flow = stocks.cash_flow(frequency='a')
df_cash_flow_filter = df_cash_flow[['asOfDate','NetIncome','FreeCashFlow']]

df_income_statement = stocks.income_statement(frequency='a')
df_TotalRevenue = df_income_statement[['asOfDate', 'TotalRevenue']]

cur_df = pd.merge(df_cash_flow_filter, df_TotalRevenue).drop(index=4)
cur_df['Net_Profit_Margins'] = cur_df['NetIncome'] / cur_df['TotalRevenue']
cur_df['FCF_to_Profit_Margins'] = cur_df['FreeCashFlow'] / cur_df['NetIncome']
print('Current table:')
print(cur_df)
Net_Profit_Margins = cur_df['Net_Profit_Margins'].mean()
FCF_to_Profit_Margins = cur_df['FCF_to_Profit_Margins'].mean()
print('Page2 - Avg Profit Margin: ', Net_Profit_Margins)
print('Page2 - Avg FCF/ Profit Margin: ', FCF_to_Profit_Margins)


## Analysis ###
dict_earnings_trend = stocks.earnings_trend
list_earnings_trend = returndict(dict_earnings_trend)['trend']

list_endDate = []
list_period = []
list_revenueEstimate_low = []
list_revenueEstimate_growth_rate = []

for x in list_earnings_trend:
    temp_endDate = x['endDate'] if x['endDate'] else None
    list_endDate.append(temp_endDate)
    temp_period = x['period'] if x['period'] else None
    list_period.append(temp_period)
    temp_revenueEstimate_low = x['revenueEstimate']['low'] if x['revenueEstimate']['low'] else None
    list_revenueEstimate_low.append(temp_revenueEstimate_low)
    temp_revenueEstimate_growth_rate = x['revenueEstimate']['growth'] if x['revenueEstimate']['growth'] else None
    list_revenueEstimate_growth_rate.append(temp_revenueEstimate_growth_rate)

# print('list_endDate')
# print(pd.Categorical(list_endDate))
# print('list_revenueEstimate_low')
# print(pd.Series(list_revenueEstimate_low, dtype='float64'))
# print('list_revenueEstimate_growth_rate')
# print(pd.Series(list_revenueEstimate_growth_rate, dtype='float64'))

df_revenueEstimate_low = pd.DataFrame({
    'endDate': pd.to_datetime(list_endDate),
    'revenueEstimate_low': pd.Series(list_revenueEstimate_low, dtype='float64', index=list_period),
    'revenueEstimate_growth_rate': pd.Series(list_revenueEstimate_growth_rate, dtype='float64', index=list_period)
}, index=list_period)

cus_df = pd.DataFrame(df_revenueEstimate_low, index=['0y', '+1y', '+2y', '+3y'])

print('Analysis: ')
# print(cus_pd)
# print(cus_pd.index)
## Index(['0y', '+1y', '+2y', '+3y'], dtype='object')
# print(cus_pd.columns)
##Index(['endDate', 'revenueEstimate_low', 'revenueEstimate_growth_rate'], dtype='object')

## pd.loc[] -- get dataframe by row (index)
## pd.loc[][] -- the second one [] is get the first[] (dataframe) by columns
Page2_C5_Sales_Growth = (cus_df.loc['0y']['revenueEstimate_growth_rate'] + cus_df.loc['+1y']['revenueEstimate_growth_rate'])/2
print('Page 2 - C5 Sales Growth (year/est): ', Page2_C5_Sales_Growth)

## target ## 目前要把endDate改成我要的 2020-09-30, 2021-09-30 ... etc
# 產生pd.Series
# get the first datetime from dataframe-Analysis
tempkeydate = cus_df.iloc[0][0]
# dict for datetime - interval is 1 year
tempdict = {'endDate': pd.date_range(tempkeydate, periods=4, freq='12M')}
# new df for temp, it will replace the cur_pd
df_temp = pd.DataFrame(tempdict, index=['0y', '+1y', '+2y', '+3y'])
# replace it
cus_df = cus_df.assign(endDate=df_temp['endDate'])

### 加入F11 and G11 (revenue)
## F11 = E11*(1+ C5)
# call E11
Page2_E11 = cus_df.loc['+1y']['revenueEstimate_low']
# call F11
Page2_F11 = Page2_E11 * ( 1+ Page2_C5_Sales_Growth)
# call G11
Page2_G11 = Page2_F11 * ( 1+ Page2_C5_Sales_Growth)

# replace cus_df.iloc[3][3] and [4][4]
cus_df.loc['+2y', 'revenueEstimate_low'] = Page2_F11
cus_df.loc['+3y', 'revenueEstimate_low'] = Page2_G11

### Page2 _ D12, E12, F12, G12 - Net Income
## D12=D11*$C$3
temp_series = cus_df.loc[:,('revenueEstimate_low',)] * Net_Profit_Margins
cus_df.insert(3, 'Page2NetIncome', temp_series)
print(cus_df)
'''
       endDate  revenueEstimate_low  revenueEstimate_growth_rate  Page2NetIncome
0y  2020-09-30         2.546180e+11                        0.014    5.469928e+10
+1y 2021-09-30         2.616590e+11                        0.121    5.621189e+10
+2y 2022-09-30         2.793210e+11                          NaN    6.000619e+10
+3y 2023-09-30         2.981752e+11                          NaN    6.405661e+10
'''

### D10 = D12 * C4 (Page2FreeCashFlow = Net Income * FCF_to_Profit_Margins)



# ## Analysis ###

# # PV of Future Cash Flow ##
# print('Start - Fair Value of Equity =B17/B18')
# ## D14 __PV of Future Cash Flow__ = D10<D12<__revenueEstimate_low__*__Avg Profit Margin__>*__Avg FCF/ Profit Margin__> / D13 <ROUND((1+B15)^1,2)>
# # print('B17=SUM(D14:H14)')
# # print('D14=D10/D13')
# # print('D10=D12*$C$4')
# # print('D12=D11*$C$3, D12=Page2NetIncome')

## D12=D11*$C$3
# temp = period_year.loc[:,('revenueEstimate_low',)] * Net_Profit_Margins

# period_year.insert(4, 'Page2NetIncome', temp)

# # print(period_year)
# # print(period_year.dtypes)

# # newpd = pd.DataFrame(period_year,index=[2,3,4,5,6,7],columns=['endDate', 'period', 'revenueEstimate_low', 'revenueEstimate_growth_rate', 'Page2NetIncome'])
# # print(newpd)


# # newpd = pd.DataFrame({
# #     'endDate': pd.Categorical(list_endDate),
# #     'period': pd.Categorical(list_period),
# #     'revenueEstimate_low': pd.Series(list_revenueEstimate_low, dtype='float64'),
# #     'revenueEstimate_growth_rate': pd.Series(list_revenueEstimate_growth_rate, dtype='float64')
# # })

