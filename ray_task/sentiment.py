
import ray
import pandas as pd
import numpy as np
import yfinance as yf
import os
from typing import List, Tuple, Dict

@ray.remote
def validate_symbol(symbol: str, start='2021-01-01', end='2023-03-01') -> Tuple[str, bool]:
    try:
        df = yf.download(symbol, start=start, end=end, progress=False)
        return (symbol, not df.empty)
    except Exception:
        return (symbol, False)

def load_sentiment_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date', 'symbol'])
    df['engagement_ratio'] = df['twitterComments'] / df['twitterLikes']
    df = df[(df['twitterLikes'] > 20) & (df['twitterComments'] > 10)]
    return df

def filter_and_rank(sentiment_df: pd.DataFrame, criterio: str = 'engagement_ratio') -> pd.DataFrame:
    if criterio not in sentiment_df.columns:
        raise ValueError(f"Columna '{criterio}' no encontrada en el DataFrame")

    aggragated_df = (
        sentiment_df.reset_index('symbol')
        .groupby([pd.Grouper(freq='ME'), 'symbol'])[[criterio]]
        .mean()
    )
    aggragated_df['rank'] = (
        aggragated_df.groupby(level=0)[criterio]
        .transform(lambda x: x.rank(ascending=False))
    )
    filtered_df = aggragated_df[aggragated_df['rank'] < 6].copy()
    filtered_df = filtered_df.reset_index(level=1)
    filtered_df.index = filtered_df.index + pd.DateOffset(1)
    return filtered_df.reset_index().set_index(['date', 'symbol'])


def get_filtered_dates(filtered_df: pd.DataFrame) -> Dict[str, List[str]]:
    dates = filtered_df.index.get_level_values('date').unique().tolist()
    fixed_dates = {}
    for d in dates:
        fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
    return fixed_dates

def validate_symbols_parallel(symbols: List[str]) -> Tuple[List[str], List[str]]:
    results = ray.get([validate_symbol.remote(s) for s in symbols])
    valid = [s for s, ok in results if ok]
    failed = [s for s, ok in results if not ok]
    return valid, failed

@ray.remote
def download_prices(symbols: List[str], start: str = '2021-01-01', end: str = '2023-03-01') -> pd.DataFrame:
    return yf.download(tickers=symbols, start=start, end=end, progress=False)

def calculate_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices_df['Close']).diff().dropna()

@ray.remote
def build_monthly_portfolio(returns_df: pd.DataFrame, start_date: str, cols: List[str]) -> pd.DataFrame:
    end_date = (pd.to_datetime(start_date) + pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
    valid_cols = [c for c in cols if c in returns_df.columns]
    if not valid_cols:
        return pd.DataFrame()
    temp_df = returns_df[start_date:end_date][valid_cols].mean(axis=1).to_frame('portfolio_returns')
    return temp_df

def assemble_portfolio(returns_df: pd.DataFrame, fixed_dates: Dict[str, List[str]]) -> pd.DataFrame:
    futures = [build_monthly_portfolio.remote(returns_df, d, cols) for d, cols in fixed_dates.items()]
    monthly_dfs = ray.get(futures)
    portfolio_df = pd.concat(monthly_dfs, axis=0)
    return portfolio_df

def get_benchmark_returns(start: str = '2021-01-01', end: str = '2023-03-01') -> pd.Series:
    qqq_df = yf.download(tickers='QQQ', start=start, end=end, progress=False)
    return np.log(qqq_df['Close']).diff()

def calculate_cumulative_returns(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    return np.exp(np.log1p(portfolio_df).cumsum()).sub(1)

def run_pipeline(criterio: str = "engagement_ratio", path: str = "datasets/sentiment_data.csv") -> pd.DataFrame:
    sentiment_df = load_sentiment_data(path)
    
    # Asegurar columna si no es engagement_ratio
    if criterio != "engagement_ratio":
        if criterio not in sentiment_df.columns:
            raise ValueError(f"'{criterio}' no es una columna válida en el dataset.")
    else:
        sentiment_df['engagement_ratio'] = sentiment_df['twitterComments'] / sentiment_df['twitterLikes']

    print(f"📊 Filtrando y rankeando por: {criterio}")
    filtered_df = filter_and_rank(sentiment_df, criterio)

    print("🗓️ Obteniendo fechas fijas")
    fixed_dates = get_filtered_dates(filtered_df)

    symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
    print("✅ Validando símbolos")
    valid_symbols, _ = validate_symbols_parallel(symbols)

    print("📥 Descargando precios")
    prices_df = ray.get(download_prices.remote(valid_symbols))

    print("📈 Calculando retornos")
    returns_df = calculate_returns(prices_df)

    print("📦 Construyendo portafolio mensual")
    portfolio_df = assemble_portfolio(returns_df, fixed_dates)

    print("📉 Agregando benchmark QQQ")
    benchmark_series = get_benchmark_returns()
    portfolio_df['nasdaq_return'] = benchmark_series

    print("📊 Calculando retorno acumulado")
    cumulative_df = calculate_cumulative_returns(portfolio_df)

    # Guarda resultado
    os.makedirs("output", exist_ok=True)
    cumulative_df.to_csv("output/cumulative_returns.csv")

    return cumulative_df
