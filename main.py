from flask import Flask, render_template, request, redirect, url_for
from yahooquery import Ticker

stocks = Ticker('aapl')

# print(aapl.asset_profile) ## return company dict format
temp_stock = stocks.asset_profile
# print(temp_stock)
# print(type(temp_stock))

def returnDict(target):


stock_asset_profile = lambda a: a['aapl']


# for x in stocks[0]:
#     print(x, stocks[x])
#     print('#########')

print(stock_asset_profile(temp_stock))
print(type(stock_asset_profile(temp_stock)))
# for x in stock_asset_profile:
#     print(x,stock_asset_profile[x])
#     print('#########')