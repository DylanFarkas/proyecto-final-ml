
import ray
import os
import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
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

ray.init()

# Ruta al archivo CSV 
data_path = 'datasets/sentiment_data.csv' 

# Paso 1: Cargar y preparar datos
print("🔍 Cargando datos de sentimiento...")
sentiment_df = load_sentiment_data(data_path)

# Paso 2: Rankear acciones mensualmente
print("📊 Calculando ranking mensual...")
filtered_df = filter_and_rank(sentiment_df)
fixed_dates = get_filtered_dates(filtered_df)

# Paso 3: Validar símbolos
symbols = sentiment_df.index.get_level_values('symbol').unique().tolist()
print(f"🧪 Validando {len(symbols)} símbolos...")
valid_symbols, failed_symbols = validate_symbols_parallel(symbols)
print("✅ Válidos:", valid_symbols)
print("❌ Fallidos:", failed_symbols)

# Paso 4: Descargar precios
print("💾 Descargando precios...")
prices_df = ray.get(download_prices.remote(valid_symbols))

# Paso 5: Calcular retornos logarítmicos
print("📈 Calculando retornos...")
returns_df = calculate_returns(prices_df)

# Paso 6: Construir portafolio con Ray
print("📦 Construyendo portafolio...")
portfolio_df = assemble_portfolio(returns_df, fixed_dates)

# Paso 7: Obtener benchmark del Nasdaq
print("📉 Obteniendo benchmark (QQQ)...")
benchmark_series = get_benchmark_returns()
portfolio_df['nasdaq_return'] = benchmark_series

# Paso 8: Calcular retorno acumulado
print("📊 Calculando retorno acumulado...")
cumulative_df = calculate_cumulative_returns(portfolio_df)

# Guardar resultados
cumulative_df.to_csv("cumulative_returns.csv")
print("✅ Resultados guardados en cumulative_returns.csv")


df = pd.read_csv("cumulative_returns.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)

plt.figure(figsize=(12, 6))
plt.plot(df["portfolio_returns"], label="Estrategia Twitter", linewidth=2)
plt.plot(df["nasdaq_return"], label="Benchmark (Nasdaq QQQ)", linestyle="--")
plt.title("Retornos Acumulados - Estrategia vs Benchmark")
plt.xlabel("Fecha")
plt.ylabel("Retorno acumulado")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
