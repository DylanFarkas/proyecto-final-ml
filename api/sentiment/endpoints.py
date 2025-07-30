import time
from fastapi import APIRouter, HTTPException
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
from benchmarking.sentiment_compare import (
    run_pipeline_sequential, 
    run_parallel_pipeline,
    run_pipeline_sequential_for_api,
    run_parallel_pipeline_for_api
)
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        df = get_cumulative_returns()
        df["Date"] = df["Date"].astype(str) 
        return JSONResponse(content=df.to_dict(orient="records"))
    except FileNotFoundError as e:
        logger.error(f"Archivo de datos no encontrado: {e}")
        raise HTTPException(status_code=404, detail="Archivo de datos no encontrado")
    except Exception as e:
        logger.error(f"Error al obtener retornos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener retornos")

@router.get("/plot", summary="Gráfico de retornos acumulados")
def get_plot():
    try:
        plot_path = generate_plot()
        return FileResponse(plot_path, media_type="image/png")
    except FileNotFoundError as e:
        logger.error(f"Error al generar gráfico: {e}")
        raise HTTPException(status_code=404, detail="Error al generar el gráfico")
    except Exception as e:
        logger.error(f"Error interno al generar gráfico: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar gráfico")


@router.get("/returns/filter", summary="Retornos por rango de fechas")
def get_filtered_returns(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")
        
        df = get_cumulative_returns()
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el rango de fechas especificado")
        
        df["Date"] = df["Date"].astype(str)
        return JSONResponse(content=df.to_dict(orient="records"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al filtrar retornos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al filtrar retornos")


@router.get("/returns/stats", summary="Estadísticas del portafolio y Nasdaq")
def get_return_stats():
    try:
        df = get_cumulative_returns()
        if df.empty:
            raise HTTPException(status_code=404, detail="No hay datos disponibles para calcular estadísticas")
        
        stats = {
            "portfolio_mean": df["portfolio_returns"].mean(),
            "portfolio_std": df["portfolio_returns"].std(),
            "nasdaq_mean": df["nasdaq_return"].mean(),
            "nasdaq_std": df["nasdaq_return"].std(),
        }
        return JSONResponse(content=stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al calcular estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al calcular estadísticas")

@router.get("/returns/dates", summary="Fechas disponibles en los retornos")
def get_dates():
    try:
        df = get_cumulative_returns()
        if df.empty:
            raise HTTPException(status_code=404, detail="No hay datos disponibles")
        
        dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()
        return JSONResponse(content={"dates": dates})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener fechas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener fechas")

@router.get("/returns/filter/csv", summary="Descargar retornos filtrados por fecha en CSV")
def download_filtered_csv(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)")
    ):
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")
        
        df = get_cumulative_returns()
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el rango de fechas especificado")
        
        df["Date"] = df["Date"].astype(str)

        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=retornos_{start_date}a{end_date}.csv"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar CSV: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar CSV")

progress_actor = ProgressTracker.remote() 
  
@router.post("/recalculate", summary="Recalcular portafolio con criterio dinámico")
def recalculate_portfolio(body: RecalcInput):
    try:
        if not body.criterio or body.criterio.strip() == "":
            raise HTTPException(status_code=400, detail="El criterio no puede estar vacío")
        
        df = run_pipeline(body.criterio, tracker=progress_actor)
        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)
        return JSONResponse(content=df.to_dict(orient="records"))
    except ValueError as e:
        logger.error(f"Error de validación en recálculo: {e}")
        raise HTTPException(status_code=400, detail=f"Error en los datos: {str(e)}")
    except Exception as e:
        logger.error(f"Error al recalcular portafolio: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al recalcular portafolio")
 

@router.get("/recalculate/status", summary="Consultar estado de cálculo en curso")
def get_recalculation_status():
    try:
        status = ray.get(progress_actor.get_status.remote())
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error al obtener estado de recálculo: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener estado")

@router.get("/download/progress", summary="Obtener el progreso de la descarga de datos")
def get_download_progress():
    try:
        return {"progress": download_progress}
    except Exception as e:
        logger.error(f"Error al obtener progreso: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener progreso")

@router.get("/compare", summary="Comparar rendimiento secuencial vs paralelo")
def compare_performance():
    try:
        logger.info("Iniciando comparación de rendimiento...")
        
        # Ejecutar pipeline secuencial
        print("Ejecutando pipeline secuencial...")
        update_download_progress(10)
        cpu_before_secuencial = measure_cpu_usage()
        start_time = time.time()
        
        try:
            result_secuencial = run_pipeline_sequential_for_api()
            secuencial_time = time.time() - start_time
            cpu_after_secuencial = measure_cpu_usage()
            print(f"Tiempo de ejecución secuencial: {secuencial_time:.2f} segundos")
            print(f"Uso de CPU secuencial: {cpu_after_secuencial}%")
            update_download_progress(50)
        except TimeoutError as e:
            logger.error(f"Timeout en pipeline secuencial: {e}")
            raise HTTPException(
                status_code=408, 
                detail={
                    "error": "timeout",
                    "message": "El pipeline secuencial tardó demasiado en ejecutarse",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Error en pipeline secuencial: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "execution_error",
                    "message": "Error durante la ejecución del pipeline secuencial",
                    "details": str(e)
                }
            )

        # Ejecutar pipeline paralelo
        print("\nEjecutando pipeline paralelo...")
        cpu_before_paralelo = measure_cpu_usage()
        start_time = time.time()
        
        try:
            result_paralelo = run_parallel_pipeline_for_api()
            paralelo_time = time.time() - start_time
            cpu_after_paralelo = measure_cpu_usage()
            print(f"Tiempo de ejecución paralelo: {paralelo_time:.2f} segundos")
            print(f"Uso de CPU paralelo: {cpu_after_paralelo}%")
            update_download_progress(100)
        except TimeoutError as e:
            logger.error(f"Timeout en pipeline paralelo: {e}")
            raise HTTPException(
                status_code=408,
                detail={
                    "error": "timeout",
                    "message": "El pipeline paralelo tardó demasiado en ejecutarse",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Error en pipeline paralelo: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "execution_error", 
                    "message": "Error durante la ejecución del pipeline paralelo",
                    "details": str(e)
                }
            )

        # Preparar resultados
        comparison_result = {
            "secuencial": {
                "tiempo": round(secuencial_time, 2),
                "cpu": round(cpu_after_secuencial, 2)
            },
            "paralelo": {
                "tiempo": round(paralelo_time, 2),
                "cpu": round(cpu_after_paralelo, 2)
            },
            "mejora_velocidad": round(((secuencial_time - paralelo_time) / secuencial_time) * 100, 1) if secuencial_time > 0 else 0
        }

        logger.info("Comparación de rendimiento completada exitosamente")
        return JSONResponse(content=comparison_result)
        
    except HTTPException:
        # Re-lanzar las HTTPException para que mantengan su formato
        raise
    except Exception as e:
        logger.error(f"Error inesperado en comparación de rendimiento: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "unexpected_error",
                "message": "Error inesperado durante la comparación de rendimiento",
                "details": str(e)
            }
        )