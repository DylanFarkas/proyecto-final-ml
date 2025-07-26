# main.py

import ray
from ray_task.intraday import (
    cargar_datos_diarios,
    cargar_datos_intradia,
    generar_senal_diaria,
    generar_senal_intradia,
    calcular_retorno_final
)

# Inicializar Ray
ray.init()

# Rutas a los archivos CSV
ruta_diaria = "datasets/simulated_daily_data.csv"
ruta_intradia = "datasets/simulated_5min_data.csv"

# 1. Cargar datos
print("Cargando datos...")
daily_df = cargar_datos_diarios(ruta_diaria)
intraday_df = cargar_datos_intradia(ruta_intradia)

# 2. Generar señales diarias con GARCH
print("Calculando señales diarias (GARCH)...")
daily_df = generar_senal_diaria(daily_df)

# 3. Generar señales intradía con RSI + Bollinger
print("Calculando señales intradía (RSI + Bollinger)...")
final_df = generar_senal_intradia(intraday_df, daily_df)

# 4. Calcular retorno de estrategia
print("Calculando retorno de la estrategia...")
final_df = calcular_retorno_final(final_df)

# 5. Guardar resultados
print("Guardando archivo final...")
final_df.to_csv("output/estrategia_intradia_resultado.csv")
print("✅ Listo. Archivo guardado en output/estrategia_intradia_resultado.csv")
