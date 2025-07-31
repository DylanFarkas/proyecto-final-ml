import ray
from ray import serve
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.sentiment.endpoints import router as sentiment_router
from api.intraday.endpoints import router as intradaily_router
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API de Análisis de Portafolio")

# Middleware de manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado en {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

# CORS
app.add_middleware(
    CORSMiddleware,
 allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentiment_router)
app.include_router(intradaily_router)


@serve.deployment
@serve.ingress(app)
class UnifiedAPI:
    pass

if __name__ == "__main__":
    try:
        ray.init(ignore_reinit_error=True)
        serve.start()
        serve.run(UnifiedAPI.bind())
        
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print(" Apagando Ray Serve...")
    except Exception as e:
        logger.error(f"Error al inicializar Ray Serve: {e}")
        print(f"Error crítico: {e}")
