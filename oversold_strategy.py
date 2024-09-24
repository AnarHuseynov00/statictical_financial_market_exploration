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

def get_major_forex_pairs():
    """
    Returns a list of major Forex pairs.
    """
    major_forex_pairs = [
        "EURUSD=X",  # Euro / US Dollar
        "GBPUSD=X",  # British Pound / US Dollar
        "USDJPY=X",  # US Dollar / Japanese Yen
        "USDCHF=X",  # US Dollar / Swiss Franc
        "AUDUSD=X",  # Australian Dollar / US Dollar
        "NZDUSD=X",  # New Zealand Dollar / US Dollar
        "USDCAD=X"   # US Dollar / Canadian Dollar
    ]
    return major_forex_pairs

def get_forex_data(period = 90):
    tickers = get_major_forex_pairs()
    forex_data = {}
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period)
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if len(data) > 0:
                forex_data[ticker] = data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    return forex_data

def calculate_percent_change(df, days_back=1):
    df[f'Percent Change'] = (df['Close'].pct_change(periods=days_back) * 100)
    return df

def backtest_strategy(hold_period = 5, percentage = 5, days_back = 1, period = 90, optional_data = None):
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
    for ticker, df in target_data.items():
        df = calculate_percent_change(df, days_back)
        memo[ticker] = 0
        for i in range(len(df) - 1):
            if df['Percent Change'].iloc[i] < -1*percentage:
                PCT_DROP = round(df['Percent Change'].iloc[i], 2)
                last_close_before_buy = round(df['Close'].iloc[i], 2)
                buy_price = round(df['Open'].iloc[i+1], 2)
                buy_date = df.index[i+1]
                if i+1+hold_period < len(df):
                    sell_price = round(df['Close'].iloc[i+1+hold_period], 2)
                    sell_date = df.index[i+1+hold_period]
                else:
                    sell_price = round(df['Close'].iloc[i+1], 2)
                    sell_date = df.index[i+1]
                
                profit = round(sell_price - buy_price, 2)
                memo[ticker] = memo[ticker] + profit
                return_percent = (profit) / buy_price * 100
                print(f"B {ticker} at {buy_date} at {buy_price} ==> at {sell_date} at {sell_price}. PCT drop was: {PCT_DROP}, LCBB was: {last_close_before_buy}. Profit: {profit}. Return: {return_percent}")
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
        if memo[ticker] == 0:
            memo.pop(ticker)
                
    
    avg_return = np.mean(returns) if returns else 0
    total_earning = np.sum(total_val) if total_val else 0
    return avg_return, returns, total_earning, total_val, memo, trade_volume_by_date, profit_by_date

if __name__ == "__main__":
    common_period = 1800
    average_return, all_returns, total_earning, total_val, trading_memo, trade_volume_by_date, profit_by_date = backtest_strategy(hold_period=10, percentage=25, days_back=5, period=common_period)
    benchmark_return, benchmark_earning = calculate_spy_benchmark(period=common_period)
    print(f"SPY BENCHMARK IS {benchmark_return}, {benchmark_earning}")
    print(f"Average return of the strategy: {average_return:.2f}%")
    print(f"total earning of the strategy: {total_earning:.2f}")
    print(f"Number of winning trades: {np.sum(np.array(all_returns) > 0)}")
    print(f"Number of losing trades: {np.sum(np.array(all_returns) < 0)}")
    
    all_returns_np = np.array(all_returns)
    all_returns_np.sort()
    print(f"Top 5 losing trade losses: {all_returns_np[0:5]}")
    print(f"Top 5 winning trade profits: {all_returns_np[-6:-1]}")
    print(f"Number of winning tickers: {np.sum(np.array(list(trading_memo.values())) > 0)}")
    print(f"Number of losing tickers: {np.sum(np.array(list(trading_memo.values())) < 0)}")
    
    print(f"Number of winning days: {np.sum(np.array(list(profit_by_date.values())) > 0)}")
    print(f"Number of losing days: {np.sum(np.array(list(profit_by_date.values())) < 0)}")
    
    print(trade_volume_by_date)
    trade_volume_by_date_arr = np.array(list(trade_volume_by_date.values()))
    trade_volume_by_date_arr.sort()
    
    profit_by_date_arr = np.array(list(profit_by_date.values()))
    profit_by_date_arr.sort()
    
    print(f"highest trade volume (daily): {trade_volume_by_date_arr[-1]}")
    print(f"highest profit in a day: {profit_by_date_arr[-1]}")
    print(f"lowest profit in a day: {profit_by_date_arr[0]}")
    
    plt.hist(list(all_returns), bins=100)
    #plt.hist(list(trading_memo.values()), bins=50)
    plt.show()
# %%
