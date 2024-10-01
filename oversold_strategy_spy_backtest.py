# %%
import numpy as np
import matplotlib.pyplot as plt
from source_files.strategies.oversold_strategy import backtest_strategy
from source_files.instruments.spy import calculate_spy_return

"""
In this script, we are going to implement the simple trading strategy called "buy oversold". The details are such:
1. Only S&P 500 stocks are taken into consideration for trading.
2. Next we define 3 parameters: hold_period, percentage and days_back.
3. If a stock loses at least the specified percentage (parameter above) of its value in days_back (parameter above) days, buy 1 share of that stock next day and sell it after hold_period (parameter above) days
4. As a benchmark, compare the results with the simple buy and hold strategy of spy.
    
"""


if __name__ == "__main__":
    common_period = 100
    average_return, all_returns, total_earning, total_val, trading_memo, trade_volume_by_date, profit_by_date = backtest_strategy(hold_period=10, percentage=20, days_back=5, period=common_period)
    benchmark_return, benchmark_earning = calculate_spy_return(period=common_period)
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
