from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Financial/stock-specific routers disabled for data-collection phase ---
# from app.api.v1 import analysis, market

# New data-collection router
from app.api.v1.endpoints import research

app = FastAPI(title="Impact AI – Data Collection Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Disabled financial routes ---
# app.include_router(analysis.router, prefix="/api/v1")
# app.include_router(market.router, prefix="/api/v1")

# Data collection route
app.include_router(research.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Impact AI – Data Collection Engine"}
