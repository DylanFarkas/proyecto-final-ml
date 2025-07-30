import time
import pandas as pd
import numpy as np
import psutil
import yfinance as yf
import os
import ray
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from ray_task.sentiment import (
    load_sentiment_data,
    filter_and_rank,
    get_filtered_dates,
    validate_symbols_parallel,
    download_prices,
    calculate_returns,
    assemble_portfolio,
    get_benchmark_returns,
    calculate_cumulative_returns
)

# Función para medir uso de la CPU
def measure_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Función secuencial para validar un símbolo
def validate_symbol_sequential(symbol: str, start='2021-01-01', end='2023-03-01') -> Tuple[str, bool]:
    try:
        df = yf.download(symbol, start=start, end=end, progress=False)
        return (symbol, not df.empty)
    except Exception:
        return (symbol, False)

# Función secuencial para validar símbolos
def validate_symbols_sequential(symbols: List[str]) -> Tuple[List[str], List[str]]:
    valid = []
    failed = []
    for symbol in symbols:
        valid_symbol, is_valid = validate_symbol_sequential(symbol)
        if is_valid:
            valid.append(valid_symbol)
        else:
            failed.append(valid_symbol)
    return valid, failed

# Cargar los datos de sentimiento
def load_sentiment_data_sequential(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date', 'symbol'])
    df['engagement_ratio'] = df['twitterComments'] / df['twitterLikes']
    df = df[(df['twitterLikes'] > 20) & (df['twitterComments'] > 10)]
    return df

# Filtrar y rankear los datos
def filter_and_rank_sequential(sentiment_df: pd.DataFrame, criterio: str = 'engagement_ratio') -> pd.DataFrame:
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

# Obtener fechas de filtrado
def get_filtered_dates_sequential(filtered_df: pd.DataFrame) -> Dict[str, List[str]]:
    dates = filtered_df.index.get_level_values('date').unique().tolist()
    fixed_dates = {}
    for d in dates:
        fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
    return fixed_dates

# Descargar precios de forma secuencial
def download_prices_sequential(symbols: List[str], start: str = '2021-01-01', end: str = '2023-03-01') -> pd.DataFrame:
    return yf.download(tickers=symbols, start=start, end=end, progress=False)

# Calcular retornos
def calculate_returns_sequential(prices_df: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices_df['Close']).diff().dropna()

# Construir portafolio mensual
def build_monthly_portfolio_sequential(returns_df: pd.DataFrame, start_date: str, cols: List[str]) -> pd.DataFrame:
    end_date = (pd.to_datetime(start_date) + pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
    valid_cols = [c for c in cols if c in returns_df.columns]
    if not valid_cols:
        return pd.DataFrame()
    temp_df = returns_df[start_date:end_date][valid_cols].mean(axis=1).to_frame('portfolio_returns')
    return temp_df

# Ensamblar el portafolio
def assemble_portfolio_sequential(returns_df: pd.DataFrame, fixed_dates: Dict[str, List[str]]) -> pd.DataFrame:
    portfolio_df = pd.DataFrame()
    for d, cols in fixed_dates.items():
        portfolio_df = pd.concat([portfolio_df, build_monthly_portfolio_sequential(returns_df, d, cols)], axis=0)
    return portfolio_df

# Obtener los retornos del benchmark
def get_benchmark_returns_sequential(start: str = '2021-01-01', end: str = '2023-03-01') -> pd.Series:
    qqq_df = yf.download(tickers='QQQ', start=start, end=end, progress=False)
    return np.log(qqq_df['Close']).diff()

# Calcular los retornos acumulados
def calculate_cumulative_returns_sequential(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    return np.exp(np.log1p(portfolio_df).cumsum()).sub(1)

# Función para ejecutar todo el pipeline secuencialmente
def run_pipeline_sequential(criterio: str = "engagement_ratio", path: str = "datasets/sentiment_data.csv") -> pd.DataFrame:
    sentiment_df = load_sentiment_data_sequential(path)
    filtered_df = filter_and_rank_sequential(sentiment_df, criterio)
    fixed_dates = get_filtered_dates_sequential(filtered_df)

    symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
    valid_symbols, _ = validate_symbols_sequential(symbols)
    
    prices_df = download_prices_sequential(valid_symbols)
    returns_df = calculate_returns_sequential(prices_df)
    
    portfolio_df = assemble_portfolio_sequential(returns_df, fixed_dates)
    benchmark_series = get_benchmark_returns_sequential()
    portfolio_df['nasdaq_return'] = benchmark_series
    
    cumulative_df = calculate_cumulative_returns_sequential(portfolio_df)

    os.makedirs("results", exist_ok=True)
    cumulative_df.to_csv("results/cumulative_returns_sequential.csv")

    return cumulative_df

# Ray Parallelizado
def run_parallel_pipeline(criterio: str = "engagement_ratio", path: str = "datasets/sentiment_data.csv") -> pd.DataFrame:
    start_time = time.time()
    
    # Iniciar Ray
    ray.init(ignore_reinit_error=True)
    
    # Cargar y preparar datos
    sentiment_df = load_sentiment_data(path)
    
    # Filtrar y rankear
    filtered_df = filter_and_rank(sentiment_df, criterio)
    fixed_dates = get_filtered_dates(filtered_df)
    
    symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
    
    # Validar símbolos en paralelo
    valid_symbols, _ = validate_symbols_parallel(symbols)
    
    # Descargar precios en paralelo
    prices_df = ray.get(download_prices.remote(valid_symbols))
    
    # Calcular retornos
    returns_df = calculate_returns(prices_df)
    
    # Construir portafolio
    portfolio_df = assemble_portfolio(returns_df, fixed_dates)
    
    # Obtener benchmark
    benchmark_series = get_benchmark_returns()
    portfolio_df['nasdaq_return'] = benchmark_series
    
    # Calcular retorno acumulado
    cumulative_df = calculate_cumulative_returns(portfolio_df)
    
    # Medir tiempo de ejecución
    elapsed_time = time.time() - start_time
    print(f"Tiempo de ejecución paralelo: {elapsed_time:.2f} segundos")
    
    os.makedirs("results", exist_ok=True)
    cumulative_df.to_csv("results/cumulative_returns_parallel.csv")
    
    return cumulative_df

# Función para medir el uso de CPU antes y después de ejecutar
def measure_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Ejecutar y comparar tiempos
if __name__ == "__main__":
    # Benchmarking secuencial
    print("Ejecutando pipeline secuencial...")
    cpu_before_secuencial = measure_cpu_usage()
    start_time = time.time()
    result_secuencial = run_pipeline_sequential()
    secuencial_time = time.time() - start_time
    cpu_after_secuencial = measure_cpu_usage()
    print(f"Tiempo de ejecución secuencial: {secuencial_time:.2f} segundos")
    print(f"Uso de CPU secuencial: {cpu_after_secuencial}%")

    # Benchmarking paralelo
    print("\nEjecutando pipeline paralelo...")
    cpu_before_paralelo = measure_cpu_usage()
    start_time = time.time()
    result_paralelo = run_parallel_pipeline()
    paralelo_time = time.time() - start_time
    cpu_after_paralelo = measure_cpu_usage()
    print(f"Tiempo de ejecución paralelo: {paralelo_time:.2f} segundos")
    print(f"Uso de CPU paralelo: {cpu_after_paralelo}%")

    # Comparar resultados
    print("\nComparación de resultados:")
    print(f"Tiempo secuencial: {secuencial_time:.2f} segundos")
    print(f"Uso de CPU secuencial: {cpu_after_secuencial}%")
    print(f"Tiempo paralelo: {paralelo_time:.2f} segundos")
    print(f"Uso de CPU paralelo: {cpu_after_paralelo}%")

    # Graficar los resultados
    tiempos = {
        "Secuencial": secuencial_time,
        "Paralelo": paralelo_time
    }

    cpu_usage = {
        "Secuencial": cpu_after_secuencial,
        "Paralelo": cpu_after_paralelo
    }

    # Crear una figura y dos subgráficos para los tiempos y el uso de CPU
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Gráfica de tiempos
    ax1.bar(tiempos.keys(), tiempos.values(), color='b', alpha=0.6, label="Tiempo (segundos)", width=0.4, align='center')
    ax1.set_ylabel("Tiempo (segundos)", color='b')
    ax1.set_xlabel("Método")

    # Crear el eje secundario para el uso de CPU
    ax2 = ax1.twinx()
    ax2.plot(cpu_usage.keys(), cpu_usage.values(), color='r', marker='o', label="Uso de CPU (%)", linewidth=2)
    ax2.set_ylabel("Uso de CPU (%)", color='r')

    # Añadir títulos y leyenda
    plt.title("Comparación de Tiempos y Uso de CPU: Secuencial vs Paralelo")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    # Mostrar la gráfica
    plt.show()
