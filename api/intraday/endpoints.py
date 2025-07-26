# intradaily_endpoints.py

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, FileResponse
from ray_task.intraday import (
    cargar_datos_diarios,
    cargar_datos_intradia,
    generar_senal_diaria,
    generar_senal_intradia,
    calcular_retorno_final
)
import ray
import os
from datetime import datetime
import pandas as pd
from api.intraday.plot import generate_plot


router = APIRouter(prefix="/intradaily")

# Inicializar Ray (si no está iniciado)
if not ray.is_initialized():
    ray.init()

# Rutas de los datos
RUTA_DIARIA = "datasets/simulated_daily_data.csv"
RUTA_INTRADIA = "datasets/simulated_5min_data.csv"
EXPORT_PATH = "output/estrategia_intradia_resultado.csv"

@router.get("/signals", summary="Señales intradía y diarias")
def get_signals():
    daily_df = cargar_datos_diarios(RUTA_DIARIA)
    intraday_df = cargar_datos_intradia(RUTA_INTRADIA)
    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df.reset_index(inplace=True)
    final_df['datetime'] = final_df['datetime'].astype(str)
    return JSONResponse(content=final_df[['datetime', 'signal_daily', 'signal_intraday']].dropna().to_dict(orient="records"))

@router.get("/returns", summary="Retornos acumulados de estrategia")
def get_returns(skip: int = 0, limit: int = 30):
    daily_df = cargar_datos_diarios(RUTA_DIARIA)
    intraday_df = cargar_datos_intradia(RUTA_INTRADIA)
    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df = calcular_retorno_final(final_df)
    final_df.reset_index(inplace=True)
    final_df['datetime'] = final_df['datetime'].astype(str)
    sliced = final_df[['datetime', 'strategy_return', 'cumulative_strategy_return']].dropna().iloc[skip:skip+limit]
    return JSONResponse(content=sliced.to_dict(orient="records"))

@router.get("/dates", summary="Fechas disponibles para consulta")
def get_available_dates():
    intraday_df = cargar_datos_intradia(RUTA_INTRADIA)
    fechas = sorted(pd.Series(intraday_df.index.date).astype(str).unique().tolist())

    return JSONResponse(content={"available_dates": fechas})

@router.get("/returns/filter", summary="Retornos filtrados por fecha")
def get_returns_by_date(
    start_date: str = Query(..., description="Fecha inicio en formato YYYY-MM-DD"),
    end_date: str = Query(..., description="Fecha fin en formato YYYY-MM-DD")
):
    daily_df = cargar_datos_diarios(RUTA_DIARIA)
    intraday_df = cargar_datos_intradia(RUTA_INTRADIA)
    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df = calcular_retorno_final(final_df)
    final_df.reset_index(inplace=True)
    final_df['datetime'] = pd.to_datetime(final_df['datetime'])
    mask = (final_df['datetime'] >= pd.to_datetime(start_date)) & (final_df['datetime'] <= pd.to_datetime(end_date))
    filtered = final_df.loc[mask, ['datetime', 'strategy_return', 'cumulative_strategy_return']].dropna()
    filtered['datetime'] = filtered['datetime'].astype(str)
    return JSONResponse(content=filtered.to_dict(orient="records"))

@router.get("/export", summary="Descargar CSV con estrategia")
def export_csv():
    daily_df = cargar_datos_diarios(RUTA_DIARIA)
    intraday_df = cargar_datos_intradia(RUTA_INTRADIA)
    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df = calcular_retorno_final(final_df)
    os.makedirs("output", exist_ok=True)
    final_df.to_csv(EXPORT_PATH)
    return FileResponse(EXPORT_PATH, media_type="text/csv", filename="estrategia_intradia_resultado.csv")

@router.get("/plot", summary="Gráfico del retorno acumulado de la estrategia")
def get_strategy_plot():
    daily_df = cargar_datos_diarios(RUTA_DIARIA)
    intraday_df = cargar_datos_intradia(RUTA_INTRADIA)
    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df = calcular_retorno_final(final_df)
    final_df.reset_index(inplace=True)

    final_df["datetime"] = final_df["datetime"].astype(str)
    plot_path = generate_plot(final_df)

    return FileResponse(plot_path, media_type="image/png", filename="estrategia_intradia_plot.png")

