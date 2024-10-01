import pandas as pd
import numpy as np
from datetime import datetime
from source_files.instruments.spy import get_spy_stock_data
from source_files.analysis_tools import calculate_percent_change
from typing import Union, Dict
import os
"""
In this script, we are going to implement the simple trading strategy called "buy oversold". The details are such:
1. Only S&P 500 stocks are taken into consideration for trading.
2. Next we define 3 parameters: hold_period, percentage and days_back.
3. If a stock loses at least the specified percentage (parameter above) of its value in days_back (parameter above) days, buy 1 share of that stock next day and sell it after hold_period (parameter above) days
4. As a benchmark, compare the results with the simple buy and hold strategy of spy.
    
"""

def backtest_strategy(hold_period:int = 5, percentage:Union[int, float] = 5, days_back:int = 1, period:int = 90, optional_data:Dict[str, pd.DataFrame] = None, result_text_file_loc:str = 'results/'):
    
    # Initial Data Structures for saving records
    
    target_data = None
    if optional_data == None:
        target_data = get_spy_stock_data(period=period)
    else:
        target_data = optional_data
    returns = []
    trade_volume_by_date = {}
    profit_by_date = {}
    total_val = []
    memo = {}
    
    # Creating txt file for results
    
    directory = result_text_file_loc + "oversold_SB/" + str(datetime.now().strftime("%m-%d-%Y%H:%M:%S"))
    os.makedirs(directory, exist_ok=True)
    
    final_results_txt_location = os.path.join(directory, "result.txt")
    final_results_csv_location = os.path.join(directory, "result.csv")
       
    with open(final_results_txt_location, 'w') as file:
        file.write(f"Results of backtest run.\n Hold Period: {hold_period}, Percentage: {percentage}, Days Back: {days_back}, Period: {period}\n")   
    
    trades_dict = {}
    trades_dict['ticker'] = []
    trades_dict['operation'] = []
    trades_dict['buy_date'] = []
    trades_dict['buy_price'] = []
    trades_dict['sell_date'] = []
    trades_dict['sell_price'] = []
    trades_dict['pct_drop'] = []
    trades_dict['profit'] = []
    trades_dict['return'] = []
    
    for ticker, df in target_data.items():
        df = calculate_percent_change(df, days_back)
        memo[ticker] = 0
        for i in range(len(df) - 1):
            
            if df['Percent Change'].iloc[i] < -1*percentage:
                
                # Simulate Buy Trade
                
                PCT_DROP = round(df['Percent Change'].iloc[i], 2)
                last_close_before_buy = round(df['Close'].iloc[i], 2)
                buy_price = round(df['Open'].iloc[i+1], 2)
                buy_date = df.index[i+1]
                if i+1+hold_period < len(df):
                    sell_price = round(df['Close'].iloc[i+1+hold_period], 2)
                    sell_date = df.index[i+1+hold_period]
                else:
                    sell_price = round(df['Close'].iloc[-1], 2)
                    sell_date = df.index[i+1]
                
                # Evaluate Results
                
                profit = round(sell_price - buy_price, 2)
                memo[ticker] = memo[ticker] + profit
                return_percent = (profit) / buy_price * 100
                
                # Update txt file
                with open(final_results_txt_location, 'a') as file:
                    file.write(f"B {ticker} at {buy_date} at {buy_price} ==> at {sell_date} at {sell_price}. PCT drop was: {PCT_DROP}, LCBB was: {last_close_before_buy}. Profit: {profit}. Return: {return_percent}.\n")
                
                # Update trades dictionary
                trades_dict['operation'].append("Buy")
                trades_dict['buy_date'].append(buy_date)
                trades_dict['buy_price'].append(buy_price)
                trades_dict['sell_date'].append(sell_date)
                trades_dict['sell_price'].append(sell_price)
                trades_dict['pct_drop'].append(PCT_DROP)
                trades_dict['ticker'].append(ticker)
                trades_dict['return'].append(return_percent)
                trades_dict['profit'].append(profit)
                
                returns.append(return_percent)
                total_val.append(profit)
                if buy_date in trade_volume_by_date:
                    trade_volume_by_date[buy_date] = trade_volume_by_date[buy_date] + buy_price
                else:
                    trade_volume_by_date[buy_date] = buy_price
                
                if sell_date in profit_by_date:
                    profit_by_date[sell_date] = profit_by_date[sell_date] + profit
                else:
                    profit_by_date[sell_date] = profit
        
        # Pop untraded stickers
        
        if memo[ticker] == 0:
            memo.pop(ticker)
        
    trades_dict_df = pd.DataFrame.from_dict(trades_dict)        
    trades_dict_df.to_csv(final_results_csv_location)
    avg_return = np.mean(returns) if returns else 0
    total_earning = np.sum(total_val) if total_val else 0
    return avg_return, returns, total_earning, total_val, memo, trade_volume_by_date, profit_by_date
