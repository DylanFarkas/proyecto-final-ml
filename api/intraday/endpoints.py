from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
import numpy as np
import pandas as pd
from benchmarking.intraday_compare import (
    benchmark_paralelo, 
    benchmark_secuencial,
    benchmark_secuencial_for_api,
    benchmark_paralelo_for_api
)
from ray_task.intraday import cargar_datos_diarios, cargar_datos_intradia, generar_senal_diaria, generar_senal_intradia, calcular_retorno_final
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/intradaily")

download_progress = 0 

def update_download_progress(progress: int):
    global download_progress
    download_progress = progress

@router.post("/run-strategy/")
def run_intraday_strategy():
    try:
        daily_df = cargar_datos_diarios("datasets/simulated_daily_data.csv")
        intraday_df = cargar_datos_intradia("datasets/simulated_5min_data.csv")

        daily_df = generar_senal_diaria(daily_df)
        final_df = generar_senal_intradia(intraday_df, daily_df)
        final_df = calcular_retorno_final(final_df)
        
        final_df.to_csv("output/estrategia_intradia_resultado.csv")
        return {"message": "Estrategia ejecutada y guardada"}
    except FileNotFoundError as e:
        logger.error(f"Archivo de datos no encontrado: {e}")
        raise HTTPException(status_code=404, detail="Archivo de datos no encontrado")
    except Exception as e:
        logger.error(f"Error al ejecutar estrategia: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al ejecutar estrategia")

@router.get("/dates")
def available_dates():
    try:
        df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=['datetime'])
        if df.empty:
            raise HTTPException(status_code=404, detail="No hay datos disponibles")
        
        fechas = sorted(df['datetime'].dt.date.unique())
        fechas_str = [f.strftime("%Y-%m-%d") for f in fechas]
        return {"dates": fechas_str}
    except FileNotFoundError as e:
        logger.error(f"Archivo de resultados no encontrado: {e}")
        raise HTTPException(status_code=404, detail="Archivo de resultados no encontrado. Ejecute la estrategia primero.")
    except Exception as e:
        logger.error(f"Error al obtener fechas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener fechas")

@router.get("/returns", summary="Retorno acumulado de la estrategia (como el notebook)")
def get_cumulative_returns(
    start_date: str = Query(None), 
    end_date: str = Query(None)
):
    try:
        df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
        df["date"] = df["datetime"].dt.date

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                df = df[df["date"] >= start_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de inicio inválido. Use YYYY-MM-DD")
                
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                df = df[df["date"] <= end_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de fin inválido. Use YYYY-MM-DD")

        if start_date and end_date and start_dt > end_dt:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el rango de fechas especificado")

        df["strategy_return"] = df["strategy_return"].fillna(0)

        daily_df = df.groupby("date")[["strategy_return"]].sum()
        daily_df["cumulative_strategy_return"] = np.exp(np.log1p(daily_df["strategy_return"]).cumsum()) - 1
        daily_df = daily_df.reset_index()
        daily_df["date"] = daily_df["date"].astype(str)
        daily_df["cumulative_strategy_return"] = daily_df["cumulative_strategy_return"] * 100  # % opcional

        return daily_df[["date", "cumulative_strategy_return"]].to_dict(orient="records")
    except FileNotFoundError as e:
        logger.error(f"Archivo de resultados no encontrado: {e}")
        raise HTTPException(status_code=404, detail="Archivo de resultados no encontrado. Ejecute la estrategia primero.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener retornos acumulados: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener retornos")

@router.get("/returns/daily", summary="Retorno diario simple (sin acumulado)")
def get_daily_returns(
    start_date: str = Query(None),
    end_date: str = Query(None)):
    
    try:
        df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
        df["date"] = df["datetime"].dt.date

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                df = df[df["date"] >= start_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de inicio inválido. Use YYYY-MM-DD")
                
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                df = df[df["date"] <= end_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de fin inválido. Use YYYY-MM-DD")

        if start_date and end_date and start_dt > end_dt:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el rango de fechas especificado")

        daily_return_df = df.groupby("date")[["strategy_return"]].sum().reset_index()
        daily_return_df["strategy_return"] = daily_return_df["strategy_return"] * 100
        daily_return_df["date"] = daily_return_df["date"].astype(str)

        return daily_return_df.to_dict(orient="records")
    except FileNotFoundError as e:
        logger.error(f"Archivo de resultados no encontrado: {e}")
        raise HTTPException(status_code=404, detail="Archivo de resultados no encontrado. Ejecute la estrategia primero.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener retornos diarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener retornos diarios")


@router.get("/returns/download", summary="Descargar CSV del retorno actual")
def download_returns_csv(
    start_date: str = Query(None),
    end_date: str = Query(None),
    tipo: str = Query("acumulado") 
):
    try:
        if tipo not in ["acumulado", "diario"]:
            raise HTTPException(status_code=400, detail="Tipo debe ser 'acumulado' o 'diario'")
        
        df = pd.read_csv("output/estrategia_intradia_resultado.csv", parse_dates=["datetime"])
        df["date"] = df["datetime"].dt.date

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                df = df[df["date"] >= start_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de inicio inválido. Use YYYY-MM-DD")
                
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                df = df[df["date"] <= end_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de fin inválido. Use YYYY-MM-DD")

        if start_date and end_date and start_dt > end_dt:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el rango de fechas especificado")

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
    except FileNotFoundError as e:
        logger.error(f"Archivo de resultados no encontrado: {e}")
        raise HTTPException(status_code=404, detail="Archivo de resultados no encontrado. Ejecute la estrategia primero.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar descarga CSV: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al generar descarga")


@router.get("/download/progress", summary="Obtener el progreso de la descarga de datos")
def get_download_progress():
    try:
        return {"progress": download_progress}
    except Exception as e:
        logger.error(f"Error al obtener progreso: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al obtener progreso")


@router.get("/compare", summary="Comparación de rendimiento: Secuencial vs Paralelo")
def benchmark():
    try:
        logger.info("Iniciando comparación de rendimiento intraday...")
        
        path_diarios = "datasets/simulated_daily_data.csv"
        path_intraday = "datasets/simulated_5min_data.csv"
        
        # Verificar que los archivos existen
        try:
            pd.read_csv(path_diarios, nrows=1)
            pd.read_csv(path_intraday, nrows=1)
        except FileNotFoundError as e:
            logger.error(f"Archivo de datos no encontrado: {e}")
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "file_not_found",
                    "message": "Archivos de datos no encontrados",
                    "details": str(e)
                }
            )
        
        # Ejecutar benchmark secuencial
        update_download_progress(10)
        print("Midiendo el rendimiento secuencial...")
        
        try:
            result_secuencial, secuencial_time, cpu_secuencial = benchmark_secuencial_for_api(
                path_diarios, path_intraday
            )
            update_download_progress(50)
        except TimeoutError as e:
            logger.error(f"Timeout en benchmark secuencial: {e}")
            raise HTTPException(
                status_code=408,
                detail={
                    "error": "timeout",
                    "message": "El benchmark secuencial tardó demasiado en ejecutarse",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Error en benchmark secuencial: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "execution_error",
                    "message": "Error durante la ejecución del benchmark secuencial",
                    "details": str(e)
                }
            )
       
        # Ejecutar benchmark paralelo
        update_download_progress(75)
        print("Midiendo el rendimiento paralelo...")
        
        try:
            result_paralelo, paralelo_time, cpu_paralelo = benchmark_paralelo_for_api(
                path_diarios, path_intraday
            )
            update_download_progress(100)
        except TimeoutError as e:
            logger.error(f"Timeout en benchmark paralelo: {e}")
            raise HTTPException(
                status_code=408,
                detail={
                    "error": "timeout",
                    "message": "El benchmark paralelo tardó demasiado en ejecutarse",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Error en benchmark paralelo: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "execution_error",
                    "message": "Error durante la ejecución del benchmark paralelo",
                    "details": str(e)
                }
            )
        
        print("Comparación de rendimiento completada.")
        
        # Preparar resultados
        comparison_data = {
            "secuencial": {
                "tiempo": round(secuencial_time, 2),
                "cpu": round(cpu_secuencial, 2)
            },
            "paralelo": {
                "tiempo": round(paralelo_time, 2),
                "cpu": round(cpu_paralelo, 2)
            },
            "mejora_velocidad": round(((secuencial_time - paralelo_time) / secuencial_time) * 100, 1) if secuencial_time > 0 else 0
        }

        logger.info("Comparación de rendimiento intraday completada exitosamente")
        return JSONResponse(content=comparison_data)
        
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