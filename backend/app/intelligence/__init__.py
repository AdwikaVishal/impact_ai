"""
intelligence/ – LLM-powered insight generation layer.

Primary exports used by the API and enrich_processor:
  enrich_company_data  – full Groq-powered enrichment pipeline
  get_llm              – singleton LLM client (Groq → mock fallback)
"""

from .enricher import enrich_company_data
from .llm_client import get_llm

__all__ = ["enrich_company_data", "get_llm"]
