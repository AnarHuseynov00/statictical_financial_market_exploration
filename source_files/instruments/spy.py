import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta

def get_spy_stock_tickers():
    tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    spy_stock_tickers = tickers['Symbol'].apply(lambda x: (x.split(".")[0]) if len(x.split(".")) > 1 else x).tolist()
    return spy_stock_tickers

def calculate_spy_return(period:int = 90):
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
    
def get_spy_stock_data(period:int = 90):
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

