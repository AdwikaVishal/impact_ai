from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import analysis, market

app = FastAPI(title="MarketShield AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MarketShield Backend"}


