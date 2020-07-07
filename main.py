from flask import Flask, render_template, request, redirect, url_for
from yahooquery import Ticker
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import re
import requests

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
print('Page1 - Free Cash Flow (unit: M) - (B9, C9, D9, E9):')
print('Page1 - Revenue (unit: M) - (B12, C12, D12, E12):')
print('Page1 - Net income (unit: M) - (B13, C13, D13, E13):')
print('Page1 - Shares Outstanding')

# try:
#     user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
#     headers = {"User-Agent": user_agent}  #请求头,headers是一个字典类型
#     html_wacc = requests.get(f'https://www.gurufocus.com/term/wacc/aapl/WACC-', headers=headers).text
#     soup_for_wacc = BeautifulSoup(html_wacc, "lxml")
#     target_h1 = soup_for_wacc.find("h1")
#     target_wacc = target_h1.next_sibling.text
#     get_number_only_array = re.findall(r'[0-9]+.',target_wacc)
#     wacc_str = "".join(get_number_only_array)
#     print(f'Page1 - Personal Required Rate of Return - wacc (B4): {wacc_str}')
# except Exception as e:
#     print(e)


dict_key_stats = stocks.key_stats
print('Shares Outstanding: ', returndict(dict_key_stats)['sharesOutstanding'])

dict_financial_data = stocks.financial_data
print('Current Price: ', returndict(dict_financial_data)['currentPrice'])
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
print('Net_Profit_Margins: ', Net_Profit_Margins)
print('FCF_to_Profit_Margins: ', FCF_to_Profit_Margins)


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
    temp_revenueEstimate_growth_rate = x['revenueEstimate']['growth'] if x['revenueEstimate']['low'] else None
    list_revenueEstimate_growth_rate.append(temp_revenueEstimate_growth_rate)

df_revenueEstimate_low = pd.DataFrame({
    'endDate': pd.Categorical(list_endDate),
    'period': pd.Categorical(list_period),
    'revenueEstimate_low': pd.Series(list_revenueEstimate_low, dtype='float64'),
    'revenueEstimate_growth_rate': pd.Series(list_revenueEstimate_growth_rate, dtype='float64')
})

period_year = df_revenueEstimate_low[df_revenueEstimate_low["period"].isin(['0y','+1y'])]

print('Analysis: ')
# print('Page2 - Analysis - Revenue Estimate - Low Estimate (unit: B) - (D11, E11):')
print(period_year)

print('Page 2 - C5 Sales Growth (year/est)')
print(period_year['revenueEstimate_growth_rate'].mean())

## Analysis ###

# PV of Future Cash Flow ##
print('Start - Fair Value of Equity =B17/B18')
## D14 __PV of Future Cash Flow__ = D10<D12<__revenueEstimate_low__*__Avg Profit Margin__>*__Avg FCF/ Profit Margin__> / D13 <ROUND((1+B15)^1,2)>
# print('B17=SUM(D14:H14)')
# print('D14=D10/D13')
# print('D10=D12*$C$4')
# print('D12=D11*$C$3, D12=Page2NetIncome')

# period_year['Page2NetIncome'] = period_year['revenueEstimate_low'] * Net_Profit_Margins

# print(period_year)

