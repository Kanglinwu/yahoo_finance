from flask import Flask, render_template, request, redirect, url_for
from yahooquery import Ticker

stocks = Ticker('aapl')

## Refer - https://github.com/dpguthrie/yahooquery

# print(aapl.asset_profile) ## return company dict format
stock_asset_profile = stocks.asset_profile
stock_esg_scores = stocks.esg_scores
# print(temp_stock)
# print(type(temp_stock))

returndict = lambda a: a['aapl']

# for x in stocks[0]:
#     print(x, stocks[x])
#     print('#########')

print('Asset profile start')
print(returndict(stock_asset_profile))
print('#########')
# for x in stock_asset_profile:
#     print(x,stock_asset_profile[x])
#     print('#########')

print('Esg Scores start')
print(returndict(stock_esg_scores))
print('#########')
