import pandas as pd

def get_cumulative_returns():
    df = pd.read_csv('output/cumulative_returns.csv', parse_dates=['Date'])
    return df