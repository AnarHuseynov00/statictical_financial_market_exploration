from datetime import timedelta, date
import yfinance as yf

MAJOR_CURRENY_PAIRS = [
        "EURUSD=X",  # Euro / US Dollar
        "GBPUSD=X",  # British Pound / US Dollar
        "USDJPY=X",  # US Dollar / Japanese Yen
        "USDCHF=X",  # US Dollar / Swiss Franc
        "AUDUSD=X",  # Australian Dollar / US Dollar
        "NZDUSD=X",  # New Zealand Dollar / US Dollar
        "USDCAD=X"   # US Dollar / Canadian Dollar
    ]



def get_major_forex_pairs():
    """
    Returns a list of major Forex pairs.
    """

    return MAJOR_CURRENY_PAIRS

def get_forex_data(period:int = 90):
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