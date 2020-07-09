from flask import Flask, render_template, request, redirect, url_for, jsonify
from yahooquery import Ticker
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import re
import requests
import datetime
import json

app = Flask(__name__)

@app.route('/stock/<target>', methods=['GET', 'POST'])
def querystock(target):
    ## Refer - https://github.com/dpguthrie/yahooquery
    stocks = Ticker(target)
    returndict = lambda a: a[target]
    dict_financial_data = stocks.financial_data
    Current_Price = str(returndict(dict_financial_data)['currentPrice'])
    return_string = ""
    return_string = return_string + f'Current Price: {Current_Price}' + '<br>'
    print(f'Current Price: {Current_Price}')

    ## Get WACC
    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        headers = {"User-Agent": user_agent}  #请求头,headers是一个字典类型
        html_wacc = requests.get(f'https://www.gurufocus.com/term/wacc/aapl/WACC-', headers=headers).text
        soup_for_wacc = BeautifulSoup(html_wacc, "lxml")
        target_h1 = soup_for_wacc.find("h1")
        target_wacc = target_h1.next_sibling.text
        get_number_only_array = re.findall(r'[0-9]+.',target_wacc)
        wacc_str = "".join(get_number_only_array)
        return_string = return_string + f'Page1 - Personal Required Rate of Return - wacc (B4): {wacc_str}' + '<br>'
        print(f'Page1 - Personal Required Rate of Return - wacc (B4): {wacc_str}')
    except Exception as e:
        print(e)

    dict_key_stats = stocks.key_stats
    Page2_B18 = returndict(dict_key_stats)['sharesOutstanding']
    r_Page2_B18 = str(Page2_B18)
    return_string = return_string + f'Page1 - Shares Outstanding: {r_Page2_B18}' + '<br>'
    print(f'Page1 - Shares Outstanding: {r_Page2_B18}')
    
    df_cash_flow = stocks.cash_flow(frequency='a')
    df_cash_flow_filter = df_cash_flow[['asOfDate','NetIncome','FreeCashFlow']]
    
    df_income_statement = stocks.income_statement(frequency='a')
    df_TotalRevenue = df_income_statement[['asOfDate', 'TotalRevenue']]

    cur_df = pd.merge(df_cash_flow_filter, df_TotalRevenue).drop(index=4)
    cur_df['Net_Profit_Margins'] = cur_df['NetIncome'] / cur_df['TotalRevenue']
    cur_df['FCF_to_Profit_Margins'] = cur_df['FreeCashFlow'] / cur_df['NetIncome']
    Net_Profit_Margins = cur_df['Net_Profit_Margins'].mean()
    FCF_to_Profit_Margins = cur_df['FCF_to_Profit_Margins'].mean()
    r_Net_Profit_Margins = str(Net_Profit_Margins)
    r_FCF_to_Profit_Margins = str(FCF_to_Profit_Margins)
    return_string = return_string + f'Page2 - Avg Profit Margin: {r_Net_Profit_Margins}' + '<br>'
    print(f'Page2 - Avg Profit Margin: {r_Net_Profit_Margins}')
    return_string = return_string + f'Page2 - Avg FCF/ Profit Margin: {r_FCF_to_Profit_Margins}' + '<br>'
    print(f'Page2 - Avg FCF/ Profit Margin: {r_FCF_to_Profit_Margins}')

    ## Starting Page 2
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
    
    df_revenueEstimate_low = pd.DataFrame({
            'endDate': pd.to_datetime(list_endDate),
            'revenueEstimate_low': pd.Series(list_revenueEstimate_low, dtype='float64', index=list_period),
            'revenueEstimate_growth_rate': pd.Series(list_revenueEstimate_growth_rate, dtype='float64', index=list_period)
        }, index=list_period)

    cus_df = pd.DataFrame(df_revenueEstimate_low, index=['0y', '+1y', '+2y', '+3y'])

    ## pd.loc[] -- get dataframe by row (index)
    ## pd.loc[][] -- the second one [] is get the first[] (dataframe) by columns
    Page2_C5_Sales_Growth = (cus_df.loc['0y']['revenueEstimate_growth_rate'] + cus_df.loc['+1y']['revenueEstimate_growth_rate'])/2
    r_Page2_C5_Sales_Growth = str(Page2_C5_Sales_Growth)
    return_string = return_string + f'Page2 - C5 Sales Growth (year/est): {r_Page2_C5_Sales_Growth}' + '\n'
    print(f'Page2 - C5 Sales Growth (year/est): {r_Page2_C5_Sales_Growth}')

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
    
    '''
           endDate  revenueEstimate_low  revenueEstimate_growth_rate  Page2NetIncome
    0y  2020-09-30         2.546180e+11                        0.014    5.469928e+10
    +1y 2021-09-30         2.616590e+11                        0.121    5.621189e+10
    +2y 2022-09-30         2.793210e+11                          NaN    6.000619e+10
    +3y 2023-09-30         2.981752e+11                          NaN    6.405661e+10
    '''

    ## D10 = D12 * C4 (Page2FreeCashFlow = Net Income * FCF_to_Profit_Margins)
    Page2FreeCashFlow_pd_series = cus_df.loc[:,'Page2NetIncome'] * FCF_to_Profit_Margins
    cus_df.insert(4, 'Page2FreeCashFlow', Page2FreeCashFlow_pd_series)
    
    '''
           endDate  revenueEstimate_low  revenueEstimate_growth_rate  Page2NetIncome  Page2FreeCashFlow
    0y  2020-09-30         2.546180e+11                        0.014    5.469928e+10       5.932015e+10
    +1y 2021-09-30         2.616590e+11                        0.121    5.621189e+10       6.096054e+10
    +2y 2022-09-30         2.793210e+11                          NaN    6.000619e+10       6.507537e+10
    +3y 2023-09-30         2.981752e+11                          NaN    6.405661e+10       6.946796e+10
    '''
    
    ## D13 = ROUND((1+B15)^1,2) // B15 = wacc_str
    new_wacc_str = wacc_str.replace("%", "")
    wacc_float = float(new_wacc_str)/100
    x_list = list(range(1,5))
    temp_pd_series = pd.Series(x_list, index=['0y', '+1y', '+2y', '+3y'])
    Page2DiscountFactor = pd.DataFrame(round((wacc_float+1)**temp_pd_series,2))
    cus_df.insert(5, 'Page2DiscountFactor', Page2DiscountFactor)
    
    '''
           endDate  revenueEstimate_low  revenueEstimate_growth_rate  Page2NetIncome  Page2FreeCashFlow  Page2DiscountFactor
    0y  2020-09-30         2.546180e+11                        0.014    5.469928e+10       5.932015e+10                 1.07
    +1y 2021-09-30         2.616590e+11                        0.121    5.621189e+10       6.096054e+10                 1.14
    +2y 2022-09-30         2.793210e+11                          NaN    6.000619e+10       6.507537e+10                 1.22
    +3y 2023-09-30         2.981752e+11                          NaN    6.405661e+10       6.946796e+10                 1.30
    '''

    ## D14 = D10 / D13 ( Page2_PVofFutureCashFlow =  Page2FreeCashFlow / Page2DiscountFactor)
    cus_df['Page2_PVofFutureCashFlow'] = cus_df['Page2FreeCashFlow'] / cus_df['Page2DiscountFactor']

    '''
           endDate  revenueEstimate_low  revenueEstimate_growth_rate  Page2NetIncome  Page2FreeCashFlow  Page2DiscountFactor  Page2_PVofFutureCashFlow
    0y  2020-09-30         2.546180e+11                        0.014    5.469928e+10       5.932015e+10                 1.07              5.543939e+10
    +1y 2021-09-30         2.616590e+11                        0.121    5.621189e+10       6.096054e+10                 1.14              5.347416e+10
    +2y 2022-09-30         2.793210e+11                          NaN    6.000619e+10       6.507537e+10                 1.22              5.334047e+10
    +3y 2023-09-30         2.981752e+11                          NaN    6.405661e+10       6.946796e+10                 1.30              5.343689e+10
    '''

    ### H14 =H10/H13
    ## H10 =G10*(1+B16)/(B15-B16)
    # B15 = wacc_float
    Page2_B16 = 0.02
    Page2_G10 = cus_df.loc['+3y', 'Page2FreeCashFlow']
    Page2_H10 = Page2_G10*(1+Page2_B16)/(wacc_float - Page2_B16)
    Page2_H13 = cus_df.loc['+3y', 'Page2DiscountFactor']
    Page2_H14 = Page2_H10 / Page2_H13

    ### B17 =SUM(D14:H14)
    ## Today's Value = SUM(Page2_PVofFutureCashFlow)
    Page2_B17_front = cus_df['Page2_PVofFutureCashFlow'].sum()
    Page2_B17 = Page2_B17_front + Page2_H14
    
    
    ### B18 = Shares Outstanding
    ## Fair Value of Equity = B17/B18
    f = Page2_B17/Page2_B18
    Page2_FairValueofEquity = '%.2f' % f
    r_Page2_FairValueofEquity = str(Page2_FairValueofEquity)
    return_string = return_string + 'Excel_Page_1' + '\n'
    print('Excel_Page_1')
    return_string = return_string + str(cur_df) + '\n'
    print(cur_df)
    return_string = return_string + 'Excel_Page_2' + '\n'
    print('Excel_Page_2')
    return_string = return_string + str(cus_df) + '\n'
    print(cus_df)
    return_string = return_string + f'Fair Value of Equity: {r_Page2_FairValueofEquity}' + '\n'
    print(f'Fair Value of Equity: {r_Page2_FairValueofEquity}')
    
    html_page1 = (
        cur_df.style
        .set_table_attributes('width="100%"')
        .set_caption("Excel_Page_1")
        .hide_index() # hide the index columns
        .render() # to html format
        )
    
    html_page2 = (
        cus_df.style
        .set_table_attributes('width="100%"')
        .set_caption("Excel_Page_2")
        .hide_index() # hide the index columns
        .render() # to html format
        )
    
    total_page = html_page1 + html_page2
    
    if request.method == 'POST':
        return_dict = {'Stock_Name': target, 'Current_Price': Current_Price, 'Fair_Value_of_Equity': Page2_FairValueofEquity}
        # return_json = json.dumps(return_dict)
        return jsonify(return_dict)
    else:
        return f'<h2> Stock - {target} <br>' + f'Current Price: {Current_Price} <br>' + f'Fair Value of Equity: {r_Page2_FairValueofEquity} <br></h2>' + total_page

app.run(port=9876, debug=True)