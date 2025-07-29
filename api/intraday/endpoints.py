from fastapi import APIRouter, Query
from datetime import datetime
import numpy as np
import pandas as pd
from ray_task.intraday import cargar_datos_diarios, cargar_datos_intradia, generar_senal_diaria, generar_senal_intradia, calcular_retorno_final
from fastapi.responses import FileResponse
import tempfile


router = APIRouter(prefix="/intradaily")

@router.post("/run-strategy/")
def run_intraday_strategy():
    daily_df = cargar_datos_diarios("datasets/simulated_daily_data.csv")
    intraday_df = cargar_datos_intradia("datasets/simulated_5min_data.csv")

    daily_df = generar_senal_diaria(daily_df)
    final_df = generar_senal_intradia(intraday_df, daily_df)
    final_df = calcular_retorno_final(final_df)
    
    final_df.to_csv("output/estrategia_intradia_resultado.csv")
    return {"message": "✅ Estrategia ejecutada y guardada"}

@router.get("/dates")
def available_dates():
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=['datetime'])
    fechas = sorted(df['datetime'].dt.date.unique())
    fechas_str = [f.strftime("%Y-%m-%d") for f in fechas]
    return {"dates": fechas_str}

@router.get("/returns", summary="Retorno acumulado de la estrategia (como el notebook)")
def get_cumulative_returns(
    start_date: str = Query(None), 
    end_date: str = Query(None)
):
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    # Filtrar fechas si aplica
    if start_date:
        df = df[df["date"] >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        df = df[df["date"] <= datetime.strptime(end_date, "%Y-%m-%d").date()]

    # Asegurar que los retornos están completos
    df["strategy_return"] = df["strategy_return"].fillna(0)

    # Agrupar por día y calcular retorno acumulado exponencial
    daily_df = df.groupby("date")[["strategy_return"]].sum()
    daily_df["cumulative_strategy_return"] = np.exp(np.log1p(daily_df["strategy_return"]).cumsum()) - 1
    daily_df = daily_df.reset_index()
    daily_df["date"] = daily_df["date"].astype(str)
    daily_df["cumulative_strategy_return"] = daily_df["cumulative_strategy_return"] * 100  # % opcional

    return daily_df[["date", "cumulative_strategy_return"]].to_dict(orient="records")

@router.get("/returns/daily", summary="Retorno diario simple (sin acumulado)")
def get_daily_returns(
    start_date: str = Query(None),
    end_date: str = Query(None)):
    
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    # Filtrar fechas si aplica
    if start_date:
        df = df[df["date"] >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        df = df[df["date"] <= datetime.strptime(end_date, "%Y-%m-%d").date()]

    # Agrupar por día
    daily_return_df = df.groupby("date")[["strategy_return"]].sum().reset_index()

    # Convertir a porcentaje (opcional)
    daily_return_df["strategy_return"] = daily_return_df["strategy_return"] * 100
    daily_return_df["date"] = daily_return_df["date"].astype(str)

    return daily_return_df.to_dict(orient="records")


@router.get("/returns/download", summary="Descargar CSV del retorno actual")
def download_returns_csv(
    start_date: str = Query(None),
    end_date: str = Query(None),
    tipo: str = Query("acumulado")  # "acumulado" o "diario"
):
    df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.date

    if start_date:
        df = df[df["date"] >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        df = df[df["date"] <= datetime.strptime(end_date, "%Y-%m-%d").date()]

    df["strategy_return"] = df["strategy_return"].fillna(0)
    result_df = df.groupby("date")[["strategy_return"]].sum()

    if tipo == "acumulado":
        result_df["cumulative_strategy_return"] = np.exp(np.log1p(result_df["strategy_return"]).cumsum()) - 1
        result_df = result_df[["cumulative_strategy_return"]]
    else:
        result_df = result_df[["strategy_return"]]

    result_df = result_df.reset_index()
    result_df["date"] = result_df["date"].astype(str)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="") as tmp:
        result_df.to_csv(tmp.name, index=False)
        return FileResponse(tmp.name, filename=f"retornos_{tipo}.csv", media_type="text/csv")

