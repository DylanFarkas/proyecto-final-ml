from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.sentiment.endpoints import router as sentiment_router
from api.intraday.endpoints import router as intradaily_router

app = FastAPI(title="API de Análisis de Portafolio")

app.add_middleware(
    CORSMiddleware,
 allow_origins=[
        "http://75.101.196.19:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],    
)

app.include_router(sentiment_router)
app.include_router(intradaily_router)
