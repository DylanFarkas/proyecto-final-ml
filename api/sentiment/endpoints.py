from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from api.sentiment.portfolio import get_cumulative_returns
from api.sentiment.plot import generate_plot
from fastapi import Query
from datetime import date
import pandas as pd
from fastapi.responses import StreamingResponse
import io
from pydantic import BaseModel
from ray_task.sentiment import run_pipeline

class RecalcInput(BaseModel):
    criterio: str
    
router = APIRouter(prefix="/sentiment")

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
        "Content-Disposition": f"attachment; filename=retornos_{start_date}_a_{end_date}.csv"
    })
  
@router.post("/recalculate", summary="Recalcular portafolio con criterio dinámico")
def recalculate_portfolio(body: RecalcInput):
    df = run_pipeline(body.criterio)
    df = df.reset_index() 
    df["Date"] = df["Date"].astype(str)
    return JSONResponse(content=df.to_dict(orient="records"))
