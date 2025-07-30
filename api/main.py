import ray
from ray import serve
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.sentiment.endpoints import router as sentiment_router
from api.intraday.endpoints import router as intradaily_router
import time

app = FastAPI(title="API de Análisis de Portafolio")

# CORS
app.add_middleware(
    CORSMiddleware,
 allow_origins=[
        "http://54.235.46.202:5173",
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
    ray.init(ignore_reinit_error=True)
    serve.start()
    serve.run(UnifiedAPI.bind())
    
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print(" Apagando Ray Serve...")
