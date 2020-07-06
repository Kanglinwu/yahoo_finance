from flask import Flask, render_template, request, redirect, url_for
from yahooquery import Ticker

stocks = Ticker('aapl')

## Refer - https://github.com/dpguthrie/yahooquery

# stock_asset_profile = stocks.asset_profile
# stock_esg_scores = stocks.esg_scores
# stock_financial_data = stocks.financial_data
# stock_key_stats = stocks.key_stats

returndict = lambda a: a['aapl']

print('Page1 - Free Cash Flow (unit: M) - (B9, C9, D9, E9):')
print('NetIncome')
print(stocks.cash_flow(frequency='a'))

print('Page1 - Revenue (unit: M) - (B12, C12, D12, E12):')
print('TotalRevenue')
print(stocks.income_statement(frequency='a'))

# print('Asset profile start')
# print(returndict(stock_asset_profile))
# print('#########')

# print('Esg Scores start')
# print(returndict(stock_esg_scores))
# print('#########')

# print('Financial data start')
# print(returndict(stock_financial_data))
# print('#########')

# print('Key stats start')
# print(returndict(stock_key_stats))
# print('#########')