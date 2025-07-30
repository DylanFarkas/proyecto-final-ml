import ray
from ray import serve
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.sentiment.endpoints import router as sentiment_router
from api.intraday.endpoints import router as intradaily_router
import time

# 🌐 Crear FastAPI app
app = FastAPI(title="API de Análisis de Portafolio")

# CORS
app.add_middleware(
    CORSMiddleware,
 allow_origins=[
        "http://75.101.196.19:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Incluir routers
app.include_router(sentiment_router)
app.include_router(intradaily_router)

# 🔀 Envolver la app completa en un deployment Serve
@serve.deployment
@serve.ingress(app)
class UnifiedAPI:
    pass

# ✅ Ejecutar solo si se llama directamente el script
if __name__ == "__main__":
    ray.init(ignore_reinit_error=True)
    serve.start()
    serve.run(UnifiedAPI.bind())

    print("✅ Ray Serve está corriendo en http://localhost:8000")
    
    # 💤 Mantener proceso activo (lo puedes detener con Ctrl+C)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("🛑 Apagando Ray Serve...")
