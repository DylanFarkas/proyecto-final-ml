# main.py

import ray
from ray_task.intraday import (
    load_daily_data,
    load_intraday_data,
    generate_daily_signal,
    generate_signal_intradia,
    calculate_final_return
)

# Inicializar Ray
ray.init()

# Rutas a los archivos CSV
ruta_diaria = "datasets/simulated_daily_data.csv"
ruta_intradia = "datasets/simulated_5min_data.csv"

# Cargar datos
print("Cargando datos...")
daily_df = load_daily_data(ruta_diaria)
intraday_df = load_intraday_data(ruta_intradia)

#Generar señales diarias con GARCH
print("Calculando señales diarias (GARCH)...")
daily_df = generate_daily_signal(daily_df)

# Generar señales intradía con RSI + Bollinger
print("Calculando señales intradía (RSI + Bollinger)...")
final_df = generate_signal_intradia(intraday_df, daily_df)

# Calcular retorno de estrategia
print("Calculando retorno de la estrategia...")
final_df = calculate_final_return(final_df)

# Guardar resultados
print("Guardando archivo final...")
final_df.to_csv("output/estrategia_intradia_resultado.csv")
print("✅ Listo. Archivo guardado en output/estrategia_intradia_resultado.csv")
