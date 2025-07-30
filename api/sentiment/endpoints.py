import time
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
import numpy as np
import psutil
import ray
from api.sentiment.portfolio import get_cumulative_returns
from api.sentiment.plot import generate_plot
from fastapi import Query
from datetime import date
import pandas as pd
from fastapi.responses import StreamingResponse
import io
from pydantic import BaseModel
from ray_task.sentiment import run_pipeline
from ray_task.sentiment import ProgressTracker
from benchmarking.sentiment_compare import run_pipeline_sequential, run_parallel_pipeline

class RecalcInput(BaseModel):
    criterio: str
    
router = APIRouter(prefix="/sentiment")

def measure_cpu_usage(interval=1, duration=3):
    cpu_readings = [psutil.cpu_percent(interval=interval) for _ in range(duration)]
    return np.mean(cpu_readings)

download_progress = 0

def update_download_progress(progress: int):
    global download_progress
    download_progress = progress

@router.get("/returns", summary="Obtener retornos acumulados")
def get_returns():
    df = get_cumulative_returns()
    df["Date"] = df["Date"].astype(str) 
    return JSONResponse(content=df.to_dict(orient="records"))

@router.get("/plot", summary="Gráfico de retornos acumulados")
def get_plot():
    plot_path = generate_plot()
    return FileResponse(plot_path, media_type="image/png")


@router.get("/returns/filter", summary="Retornos por rango de fechas")
def get_filtered_returns(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    df = get_cumulative_returns()
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    df["Date"] = df["Date"].astype(str)
    return JSONResponse(content=df.to_dict(orient="records"))


@router.get("/returns/stats", summary="Estadísticas del portafolio y Nasdaq")
def get_return_stats():
    df = get_cumulative_returns()
    stats = {
        "portfolio_mean": df["portfolio_returns"].mean(),
        "portfolio_std": df["portfolio_returns"].std(),
        "nasdaq_mean": df["nasdaq_return"].mean(),
        "nasdaq_std": df["nasdaq_return"].std(),
    }
    return JSONResponse(content=stats)

@router.get("/returns/dates", summary="Fechas disponibles en los retornos")
def get_dates():
    df = get_cumulative_returns()
    dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()
    return JSONResponse(content={"dates": dates})

@router.get("/returns/filter/csv", summary="Descargar retornos filtrados por fecha en CSV")
def download_filtered_csv(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
    ):
    df = get_cumulative_returns()
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    df["Date"] = df["Date"].astype(str)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename=retornos_{start_date}a{end_date}.csv"
    })

progress_actor = ProgressTracker.remote() 
  
@router.post("/recalculate", summary="Recalcular portafolio con criterio dinámico")
def recalculate_portfolio(body: RecalcInput):
    df = run_pipeline(body.criterio, tracker=progress_actor)
    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)
    return JSONResponse(content=df.to_dict(orient="records"))
 

@router.get("/recalculate/status", summary="Consultar estado de cálculo en curso")
def get_recalculation_status():
    status = ray.get(progress_actor.get_status.remote())
    return JSONResponse(content=status)

@router.get("/download/progress", summary="Obtener el progreso de la descarga de datos")
def get_download_progress():
    return {"progress": download_progress}

@router.get("/compare", summary="Comparar rendimiento secuencial vs paralelo")
def compare_performance():
    print("Ejecutando pipeline secuencial...")
    update_download_progress(25)  
    cpu_before_secuencial = measure_cpu_usage()
    start_time = time.time()
    result_secuencial = run_pipeline_sequential()
    secuencial_time = time.time() - start_time
    cpu_after_secuencial = measure_cpu_usage()
    print(f"Tiempo de ejecución secuencial: {secuencial_time:.2f} segundos")
    print(f"Uso de CPU secuencial: {cpu_after_secuencial}%")
    
    update_download_progress(50) 

    print("\nEjecutando pipeline paralelo...")
    cpu_before_paralelo = measure_cpu_usage()
    start_time = time.time()
    result_paralelo = run_parallel_pipeline()
    paralelo_time = time.time() - start_time
    cpu_after_paralelo = measure_cpu_usage()
    print(f"Tiempo de ejecución paralelo: {paralelo_time:.2f} segundos")
    print(f"Uso de CPU paralelo: {cpu_after_paralelo}%")

    update_download_progress(100)  

   
    comparison_result = {
        "secuencial": {
            "tiempo": secuencial_time,
            "cpu": cpu_after_secuencial
        },
        "paralelo": {
            "tiempo": paralelo_time,
            "cpu": cpu_after_paralelo
        }
    }

    return JSONResponse(content=comparison_result)