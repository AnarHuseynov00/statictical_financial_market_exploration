# %%
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta
import matplotlib.pyplot as plt

"""
In this script, we are going to implement the simple trading strategy called "buy oversold". The details are such:
1. Only S&P 500 stocks are taken into consideration for trading.
2. Next we define 3 parameters: hold_period, percentage and days_back.
3. If a stock loses at least the specified percentage (parameter above) of its value in days_back (parameter above) days, buy 1 share of that stock next day and sell it after hold_period (parameter above) days
4. As a benchmark, compare the results with the simple buy and hold strategy of spy.
    
"""

def get_spy_stock_tickers():
    tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    spy_stock_tickers = tickers['Symbol'].apply(lambda x: (x.split(".")[0]) if len(x.split(".")) > 1 else x).tolist()
    return spy_stock_tickers

def calculate_spy_benchmark(period = 90):
    end_date = date.today()
    start_date = end_date - timedelta(days=period)
    spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)
    
    if len(spy_data) > 0:
        spy_start_price = spy_data['Close'].iloc[0]
        spy_end_price = spy_data['Close'].iloc[-1]
        
        spy_return = (spy_end_price - spy_start_price) / spy_start_price * 100
        return spy_return, spy_end_price - spy_start_price
    else:
        return None, None

def get_spy_stock_data(period = 90):
    tickers = get_spy_stock_tickers()
    stock_data = {}
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period)
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if len(data) > 0:
                stock_data[ticker] = data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    return stock_data

def calculate_percent_change(df, days_back=1):
    df[f'Percent Change'] = (df['Close'].pct_change(periods=days_back) * 100)
    return df

def backtest_strategy(hold_period = 5, percentage = 5, days_back = 1, period = 90):
    stock_data = get_spy_stock_data(period=period)
    returns = []
    total_val = []
    memo = {}
    for ticker, df in stock_data.items():
        df = calculate_percent_change(df, days_back)
        memo[ticker] = 0
        for i in range(len(df) - 1):
            if df['Percent Change'].iloc[i] < -1*percentage:
                PCT_DROP = round(df['Percent Change'].iloc[i], 2)
                last_close_before_buy = round(df['Close'].iloc[i], 2)
                buy_price = round(df['Open'].iloc[i+1], 2)
                if i+1+hold_period < len(df):
                    sell_price = round(df['Close'].iloc[i+1+hold_period], 2)
                    sell_date = df.index[i+1+hold_period]
                else:
                    sell_price = round(df['Close'].iloc[i+1], 2)
                    sell_date = df.index[i+1]
                
                profit = round(sell_price - buy_price, 2)
                memo[ticker] = memo[ticker] + profit
                return_percent = (profit) / buy_price * 100
                print(f"B {ticker} at {df.index[i+1]} at {buy_price} ==> at {sell_date} at {sell_price}. PCT drop was: {PCT_DROP}, LCBB was: {last_close_before_buy}. Profit: {profit}. Return: {return_percent}")
                returns.append(return_percent)
                total_val.append(profit)
        if memo[ticker] == 0:
            memo.pop(ticker)
                
    
    avg_return = np.mean(returns) if returns else 0
    total_earning = np.sum(total_val) if total_val else 0
    return avg_return, returns, total_earning, total_val, memo

if __name__ == "__main__":
    average_return, all_returns, total_earning, total_val, trading_memo = backtest_strategy(hold_period=10, percentage=10, days_back=5, period=720)
    benchmark_return, benchmark_earning = calculate_spy_benchmark(period=720)
    print(f"SPY BENCHMARK IS {benchmark_return}, {benchmark_earning}")
    print(f"Average return of the strategy: {average_return:.2f}%")
    print(f"total earning of the strategy: {total_earning:.2f}")
    print(f"Number of winning trades: {np.sum(np.array(all_returns) > 0)}")
    print(f"Number of losing trades: {np.sum(np.array(all_returns) < 0)}")
    plt.hist(list(trading_memo.values()), bins=50)
    plt.show()
# %%
