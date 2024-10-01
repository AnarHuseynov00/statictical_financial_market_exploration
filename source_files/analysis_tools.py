import pandas as pd

def calculate_percent_change(df: pd.DataFrame, days_back: int=1, target_column:str = 'Close'):
    df['Percent Change'] = (df[target_column].pct_change(periods=days_back) * 100)
    return df