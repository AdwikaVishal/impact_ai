from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import analysis, market, intelligence, comparison
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables from backend/.env file
env_file = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {env_file}")
print(f".env exists: {env_file.exists()}")
load_dotenv(dotenv_path=env_file)

# Debug: Print loaded API keys
print("="*80)
print("ENVIRONMENT VARIABLES LOADED:")
print(f"GROQ_API_KEY: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"ALPHA_VANTAGE_KEY: {bool(os.getenv('ALPHA_VANTAGE_KEY'))}")
print(f"NEWSAPI_KEY: {bool(os.getenv('NEWSAPI_KEY'))}")
print(f"GNEWS_API_KEY: {bool(os.getenv('GNEWS_API_KEY'))}")
if os.getenv('GNEWS_API_KEY'):
    print(f"GNEWS_API_KEY value: {os.getenv('GNEWS_API_KEY')[:10]}...")
print("="*80)

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
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["intelligence"])
app.include_router(comparison.router, prefix="/api/v1", tags=["comparison"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MarketShield Backend"}


